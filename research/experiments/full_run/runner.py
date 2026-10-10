"""Full-experiment runner (protocol §3, §7, §9).

    python runner.py env-check         # this machine vs requirements-experiment.lock   (no API)
    python runner.py run RUN_DIR       # gate -> plan -> calls in plan order            (API)
    python runner.py retry RUN_DIR     # one re-run of infrastructure-failed calls      (API)
    python runner.py score RUN_DIR     # outputs -> node counts and metrics             (no API)
    python runner.py validate RUN_DIR  # integrity and completeness checks              (no API)

Every model request goes through `Runner._request`, which runs the full
freeze gate (`protocol_lock.assert_ready_for_llm_calls` plus the provider
check) immediately before calling the transport. The first `run` also writes
`gate.json`, which the analysis requires. Jobs run one at a time in the saved
plan order. Every attempt, ok or failed, is appended to `raw.jsonl` (owner-only
permissions, hash-chained, API key never written). The transport is injected,
so all of this is tested offline.
"""

from __future__ import annotations

import hashlib
import json
import os
import random
import re
import sys
import time
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parents[1]
PILOT_DIR = RESEARCH / "experiments" / "rn_pilot"
for p in (str(RESEARCH), str(PILOT_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

from reflica_bench import protocol_lock as pl  # noqa: E402
from reflica_bench import rn  # noqa: E402
from reflica_bench import stats as S  # noqa: E402
from reflica_bench.loader import load_scenario  # noqa: E402

SEED = 20261010
REPEATS = 3
CALL_TYPES = ("B1", "B2", "EXTRACT")
PROMPTS = {"B1": "b1_full_regeneration.v1.1.txt", "B2": "b2_delta.v1.1.txt", "EXTRACT": "extractor.v1.1.txt"}
MAX_ATTEMPTS = 2               # original + one re-run (protocol §7)
PAUSE_AFTER = 5                # consecutive infrastructure failures -> pause (D5)
MAX_PAUSE_S = 7 * 24 * 3600    # D5: seven days
KEY_PATTERN = re.compile(r"(sk-[A-Za-z0-9_-]{20,}|AQ\.[A-Za-z0-9_-]{20,}|AIza[A-Za-z0-9_-]{20,}|nvapi-[A-Za-z0-9_-]{20,})")
FILES = {"gate": "gate.json", "plan": "plan.json", "raw": "raw.jsonl", "state": "state.json",
         "env": "environment.json", "scores": "scores.jsonl"}


class Fatal(RuntimeError):
    """Stop the run: gate failure, wrong provider/model, missing key, D5 expiry."""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def _cfg() -> dict:
    return json.loads((PILOT_DIR / "config.frozen.json").read_text())


def _write_private(path: Path, text: str) -> None:
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        f.write(text)


# ---------------------------------------------------------------------------
# Plan
# ---------------------------------------------------------------------------

def rendered_scenarios() -> dict[str, Any]:
    """Deterministic R-N renders of all canonical scenarios (leakage-checked)."""
    out = {}
    for p in rn.canonical_files():
        sc = load_scenario(p)
        r = rn.render(sc, rn._sha(p))
        leaks = rn.check_leakage(r, sc)
        if leaks:
            raise Fatal(f"render leakage in {sc.scenario_id}: {leaks}")
        out[sc.scenario_id] = (sc, r)
    return out


def make_plan(protocol_sha256: str, scenarios: dict[str, Any]) -> dict:
    jobs = sorted((sid, c, r) for sid in scenarios for c in CALL_TYPES for r in range(REPEATS))
    random.Random(SEED).shuffle(jobs)
    return {
        "protocol_sha256": protocol_sha256,
        "seed": SEED, "repeats": REPEATS, "call_types": list(CALL_TYPES), "prompts": PROMPTS,
        "scenarios": {sid: {"category": sc.category, "subcategory": sc.subcategory,
                            "render_sha256": _sha(r.model_dump_json())}
                      for sid, (sc, r) in sorted(scenarios.items())},
        "jobs": [list(j) for j in jobs],
    }


# ---------------------------------------------------------------------------
# Raw log
# ---------------------------------------------------------------------------

def read_raw(run_dir: Path) -> list[dict]:
    path = Path(run_dir) / FILES["raw"]
    return [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []


def _last_line_sha(run_dir: Path) -> str:
    path = Path(run_dir) / FILES["raw"]
    if not path.exists() or not path.read_text():
        return "0" * 64
    return _sha(path.read_text().splitlines()[-1])


def _redact(text: str, secret: str | None) -> tuple[str, bool]:
    hit = False
    if secret and secret in text:
        text, hit = text.replace(secret, "[REDACTED]"), True
    if KEY_PATTERN.search(text):
        text, hit = KEY_PATTERN.sub("[REDACTED]", text), True
    return text, hit


def append_raw(run_dir: Path, record: dict, secret: str | None) -> dict:
    record = dict(record, prev_sha256=_last_line_sha(run_dir))
    line, redacted = _redact(json.dumps(record, sort_keys=True), secret)
    if redacted:
        record = json.loads(line) | {"redacted": True}
        line = json.dumps(record, sort_keys=True)
    path = Path(run_dir) / FILES["raw"]
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
    with os.fdopen(fd, "a") as f:
        f.write(line + "\n")
        f.flush()
        os.fsync(f.fileno())
    return record


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def default_transport(cfg: dict, model: str, system: str, user: str):
    from repeatability import call  # pilot client: retries 429/503, aborts on served-model mismatch

    return call(cfg, model, system, user)


def provider_problems(cfg: dict) -> list[str]:
    import _api

    out = []
    if _api.PROVIDER != cfg["provider_key"]:
        out.append(f"provider {_api.PROVIDER!r} != frozen {cfg['provider_key']!r} (set REFLICA_LLM_PROVIDER)")
    if not os.environ.get(_api.KEY_ENV):
        out.append(f"{_api.KEY_ENV} is not set")
    return out


def _secret() -> str | None:
    import _api

    return os.environ.get(_api.KEY_ENV)


class Runner:
    def __init__(self, run_dir: Path, *, protocol_dir: Path = HERE,
                 transport: Callable | None = None, gate: Callable[[], None] | None = None,
                 clock: Callable[[], float] = time.time, secret: Callable[[], str | None] = _secret):
        self.run_dir = Path(run_dir)
        self.protocol_dir = Path(protocol_dir)
        self.cfg = _cfg()
        self.transport = transport or default_transport
        self.gate = gate or self._full_gate
        self.clock = clock
        self.secret = secret

    # -- gate ---------------------------------------------------------------
    def _full_gate(self) -> None:
        pl.assert_ready_for_llm_calls(self.protocol_dir)  # lock, fingerprints, records, environment lock
        problems = provider_problems(self.cfg)
        if problems:
            raise RuntimeError("; ".join(problems))

    def _request(self, system: str, user: str):
        try:
            self.gate()  # full gate before EVERY request
        except Exception as e:
            raise Fatal(f"freeze gate failed: {e}") from None
        return self.transport(self.cfg, self.cfg["model_id"], system, user)

    # -- state ----------------------------------------------------------------
    def _state(self) -> dict:
        p = self.run_dir / FILES["state"]
        return json.loads(p.read_text()) if p.exists() else {}

    def _set_state(self, **kw) -> None:
        _write_private(self.run_dir / FILES["state"], json.dumps(self._state() | kw, indent=1, sort_keys=True) + "\n")

    def _check_state(self) -> None:
        st = self._state()
        if st.get("stopped"):
            raise Fatal(f"run stopped: {st['stopped']}; a restart needs an amendment and a new run folder")
        if st.get("paused_at") is not None and self.clock() - st["paused_at"] > MAX_PAUSE_S:
            self._set_state(stopped="D5: paused for more than 7 days")
            raise Fatal("D5: paused for more than 7 days; stop")

    # -- setup ----------------------------------------------------------------
    def _setup(self) -> tuple[dict, dict]:
        self.run_dir.mkdir(parents=True, exist_ok=True)
        os.chmod(self.run_dir, 0o700)
        self._check_state()
        gate_path = self.run_dir / FILES["gate"]
        if not gate_path.exists():
            # The gate record is always written by the full gate, never by an injected one.
            try:
                self._full_gate()
                pl.write_gate_record(self.run_dir, self.protocol_dir)
            except Exception as e:
                raise Fatal(f"freeze gate failed: {e}") from None
        gate = json.loads(gate_path.read_text())
        if not (self.run_dir / FILES["env"]).exists():
            _write_private(self.run_dir / FILES["env"],
                           json.dumps(pl.environment() | {"platform": pl.platform_info(),
                                                           "all_packages": pl.all_packages()},
                                      indent=1, sort_keys=True) + "\n")
        scen = rendered_scenarios()
        plan = make_plan(gate["protocol_sha256"], scen)
        plan_path = self.run_dir / FILES["plan"]
        if plan_path.exists():
            if json.loads(plan_path.read_text()) != plan:
                raise Fatal("saved plan differs from the plan recomputed now (inputs changed?)")
        else:
            _write_private(plan_path, json.dumps(plan, indent=1, sort_keys=True) + "\n")
        return plan, scen

    # -- execution ----------------------------------------------------------
    def _attempt(self, idx: int, job: list, scen: dict, attempt: int) -> str:
        """Make one attempt; return 'ok', 'infra' or raise Fatal."""
        from repeatability import render_prompt

        sid, call, rep = job
        system, user = render_prompt(PROMPTS[call], scen[sid][1])
        rec = {"plan_index": idx, "scenario": sid, "call": call, "repeat": rep, "attempt": attempt,
               "started_at": _now()}
        try:
            text, meta = self._request(system, user)
        except Fatal as e:
            append_raw(self.run_dir, rec | {"finished_at": _now(), "ok": False, "error_class": "fatal",
                                            "error": str(e)[:500]}, self.secret())
            self._set_state(stopped=str(e)[:300])
            raise
        except BaseException as e:  # noqa: BLE001 — every failure is recorded, nothing retried silently
            msg = str(e)
            fatal = "ABORT" in msg or "is not set in the environment" in msg
            append_raw(self.run_dir, rec | {"finished_at": _now(), "ok": False,
                                            "error_class": "fatal" if fatal else "infra",
                                            "error": f"{type(e).__name__}: {msg[:500]}"}, self.secret())
            if fatal:
                self._set_state(stopped=msg[:300])
                raise Fatal(msg[:300]) from None
            if isinstance(e, KeyboardInterrupt):
                raise
            return "infra"
        if meta.get("served") != self.cfg["model_id"]:
            append_raw(self.run_dir, rec | {"finished_at": _now(), "ok": False, "error_class": "fatal",
                                            "error": f"served model {meta.get('served')!r}"}, self.secret())
            self._set_state(stopped="served model mismatch")
            raise Fatal("served model mismatch")
        append_raw(self.run_dir, rec | {"finished_at": _now(), "ok": True, "content": text, "meta": meta},
                   self.secret())
        return "ok"

    def _loop(self, todo: list[tuple[int, list, int]], scen: dict, max_calls: int | None) -> dict:
        streak = made = 0
        for idx, job, attempt in todo:
            if max_calls is not None and made >= max_calls:
                break
            status = self._attempt(idx, job, scen, attempt)
            made += 1
            if status == "ok":
                streak = 0
                if self._state().get("paused_at") is not None:
                    self._set_state(paused_at=None)
            else:
                streak += 1
                if streak >= PAUSE_AFTER:
                    if self._state().get("paused_at") is None:
                        self._set_state(paused_at=self.clock())
                    return {"status": "paused", "calls": made}
        return {"status": "done", "calls": made}

    def run(self, max_calls: int | None = None) -> dict:
        plan, scen = self._setup()
        attempted = {(r["scenario"], r["call"], r["repeat"]) for r in read_raw(self.run_dir)}
        todo = [(i, j, 1) for i, j in enumerate(plan["jobs"]) if tuple(j) not in attempted]
        return self._loop(todo, scen, max_calls)

    def retry(self, max_calls: int | None = None) -> dict:
        """One more attempt for jobs whose every attempt failed for infrastructure reasons."""
        plan, scen = self._setup()
        by_job: dict[tuple, list[dict]] = {}
        for r in read_raw(self.run_dir):
            by_job.setdefault((r["scenario"], r["call"], r["repeat"]), []).append(r)
        todo = []
        for i, j in enumerate(plan["jobs"]):
            recs = by_job.get(tuple(j), [])
            if recs and not any(r["ok"] for r in recs) and len(recs) < MAX_ATTEMPTS \
                    and all(r.get("error_class") == "infra" for r in recs):
                todo.append((i, j, len(recs) + 1))
        return self._loop(todo, scen, max_calls)


# ---------------------------------------------------------------------------
# Job status (shared by validate and score)
# ---------------------------------------------------------------------------

def job_status(run_dir: Path) -> tuple[dict[tuple, str], dict[tuple, dict]]:
    """status[(sid, call, r)] ∈ {ok, infra_missing}; final ok record per job.
    Model failures are decided at scoring time (the call itself succeeded)."""
    status: dict[tuple, str] = {}
    final: dict[tuple, dict] = {}
    for r in read_raw(run_dir):
        k = (r["scenario"], r["call"], r["repeat"])
        if r["ok"]:
            status[k], final[k] = S.OK, r
        else:
            status.setdefault(k, S.INFRA_MISSING)
    return status, final


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate(run_dir: Path, *, protocol_dir: Path = HERE, complete: bool = True) -> dict:
    run_dir = Path(run_dir)
    problems: list[str] = list(pl.check_gate_record(run_dir, protocol_dir))
    gate_path = run_dir / FILES["gate"]
    gate = json.loads(gate_path.read_text()) if gate_path.exists() else {}
    plan_path = run_dir / FILES["plan"]
    if not plan_path.exists():
        return {"problems": problems + ["plan.json missing"], "summary": {}}
    plan = json.loads(plan_path.read_text())
    if plan.get("protocol_sha256") != gate.get("protocol_sha256"):
        problems.append("plan protocol differs from gate record")
    expected = make_plan(plan.get("protocol_sha256", ""), rendered_scenarios())
    if plan != expected:
        problems.append("plan differs from the pre-specified plan (scenarios, renders, seed or order)")
    env_path = run_dir / FILES["env"]
    if not env_path.exists():
        problems.append("environment.json missing")
    elif gate.get("fingerprints") and json.loads(env_path.read_text()).get("packages") != gate["fingerprints"]["environment"]["packages"]:
        problems.append("recorded environment differs from the gated environment")

    lines = (run_dir / FILES["raw"]).read_text().splitlines() if (run_dir / FILES["raw"]).exists() else []
    prev = "0" * 64
    index = {tuple(j): i for i, j in enumerate(plan["jobs"])}
    attempts: dict[tuple, list[dict]] = {}
    first_order: list[int] = []
    fatal_seen = False
    model = _cfg()["model_id"]
    for n, line in enumerate(lines):
        rec = json.loads(line)
        if rec.get("prev_sha256") != prev:
            problems.append(f"raw.jsonl line {n + 1}: hash chain broken")
        prev = _sha(line)
        k = (rec["scenario"], rec["call"], rec["repeat"])
        if k not in index or rec.get("plan_index") != index.get(k):
            problems.append(f"raw.jsonl line {n + 1}: job not in plan or wrong plan index")
            continue
        if fatal_seen:
            problems.append(f"raw.jsonl line {n + 1}: record after a fatal stop")
        fatal_seen |= rec.get("error_class") == "fatal"
        attempts.setdefault(k, []).append(rec)
        if len(attempts[k]) == 1:
            first_order.append(index[k])
        if rec["ok"] and rec.get("meta", {}).get("served") != model:
            problems.append(f"raw.jsonl line {n + 1}: served model differs")
        if KEY_PATTERN.search(line):
            problems.append(f"raw.jsonl line {n + 1}: key-like string present")
    if first_order != sorted(first_order):
        problems.append("first attempts are not in plan order")
    for k, recs in attempts.items():
        if len(recs) > MAX_ATTEMPTS:
            problems.append(f"{k}: more than {MAX_ATTEMPTS} attempts")
        if any(r["ok"] for r in recs[:-1]):
            problems.append(f"{k}: attempt after a successful one")
    if (run_dir / FILES["raw"]).exists() and (os.stat(run_dir / FILES["raw"]).st_mode & 0o077):
        problems.append("raw.jsonl is readable by other users")

    status, _ = job_status(run_dir)
    jobs = [tuple(j) for j in plan["jobs"]]
    not_attempted = [k for k in jobs if k not in attempts]
    retry_possible = [k for k in jobs if status.get(k) == S.INFRA_MISSING and len(attempts[k]) < MAX_ATTEMPTS
                      and all(r.get("error_class") == "infra" for r in attempts[k])]
    if complete and not_attempted:
        problems.append(f"{len(not_attempted)} planned jobs never attempted")
    if complete and retry_possible:
        problems.append(f"{len(retry_possible)} infrastructure failures not yet re-run once")
    st = json.loads((run_dir / FILES["state"]).read_text()) if (run_dir / FILES["state"]).exists() else {}
    if complete and st.get("stopped"):
        problems.append(f"run stopped: {st['stopped']}")
    sids = sorted(plan["scenarios"])
    aset = S.analysis_set({k: v for k, v in status.items()}, sids, CALL_TYPES, REPEATS,
                          categories={s: plan["scenarios"][s]["category"] for s in sids})
    if complete and aset["stop_rule_triggered"]:
        problems.append(f"stop rule: {aset['infra_missing_fraction']:.1%} of calls infrastructure-missing (> 5%)")
    return {"problems": problems, "summary": {"records": len(lines), "jobs": len(jobs),
                                              "not_attempted": len(not_attempted), "analysis_set": aset}}


# ---------------------------------------------------------------------------
# Scoring (no API)
# ---------------------------------------------------------------------------

def score(run_dir: Path) -> list[dict]:
    """Turn the final ok output of every job into per-method node counts and
    evaluator metrics. Writes scores.jsonl (sorted, deterministic)."""
    import pilot  # approved pilot scoring rules: from_direct, _remap, _mapper, metrics, extraction_quality

    from reflica_bench.adapters import AdapterOutput, StructuredAdapter_v1
    from reflica_bench.b5.reflica import B5Reflica
    from reflica_bench.baselines.b3_reachability import B3Reachability
    from reflica_bench.baselines.b4a_atms import B4aClassicalATMS
    from reflica_bench.baselines.b4b_weighted_csp import B4bWeightedCSP
    from reflica_bench.endpoints import node_counts
    from reflica_bench.extraction_schema import ExtractionOutput

    symbolic = {"B3": B3Reachability, "B4a": B4aClassicalATMS, "B4b": B4bWeightedCSP, "B5": B5Reflica}
    codes = _cfg()["reason_to_code"]
    plan = json.loads((Path(run_dir) / FILES["plan"]).read_text())
    status, final = job_status(run_dir)
    scen = rendered_scenarios()
    rows: list[dict] = []

    def row(sid, cond, method, rep, st, result=None, **extra):
        sc = scen[sid][0]
        base = {"scenario": sid, "category": sc.category, "condition": cond, "method": method, "repeat": rep,
                "status": st}
        if st == S.INFRA_MISSING:
            return base | extra
        counts = node_counts(result, sc.ground_truth)
        base["counts"] = counts.to_dict()
        if result is not None:
            base["metrics"] = pilot.metrics(result, sc)
        return base | extra

    for sid in sorted(plan["scenarios"]):
        sc, r_n = scen[sid]
        alias = r_n.alias_map
        m = pilot._mapper(alias)
        for name, cls in symbolic.items():
            res = cls().revise(StructuredAdapter_v1().adapt(sc, "gold"))
            rows.append(row(sid, "A", name, 0, S.OK, res))
        for rep in range(REPEATS):
            for kind in ("B1", "B2"):
                k = (sid, kind, rep)
                if status.get(k) != S.OK:
                    rows.append(row(sid, "direct", kind, rep, S.INFRA_MISSING))
                    continue
                try:
                    res, info = pilot.from_direct(kind, final[k]["content"], sc, alias, codes)
                    rows.append(row(sid, "direct", kind, rep, S.OK, res, **info))
                except Exception as e:  # noqa: BLE001 — invalid output is a model failure, scored
                    rows.append(row(sid, "direct", kind, rep, S.MODEL_FAILURE, None, error=f"{type(e).__name__}: {str(e)[:200]}"))
            k = (sid, "EXTRACT", rep)
            if status.get(k) != S.OK:
                for name in symbolic:
                    rows.append(row(sid, "B", name, rep, S.INFRA_MISSING))
                continue
            try:
                x = ExtractionOutput.model_validate_json(final[k]["content"])
                mi = x.to_method_input()
                quality = pilot.extraction_quality(x, sc, alias)
            except Exception as e:  # noqa: BLE001 — extraction failure: every Condition B method fails
                for name in symbolic:
                    rows.append(row(sid, "B", name, rep, S.MODEL_FAILURE, None,
                                    error=f"extraction: {type(e).__name__}: {str(e)[:200]}"))
                continue
            for name, cls in symbolic.items():
                try:
                    res, bad = pilot._remap(cls().revise(AdapterOutput(mi, None, {})), m)
                    rows.append(row(sid, "B", name, rep, S.OK, res, unmapped_labels=bad, extraction=quality))
                except Exception as e:  # noqa: BLE001 — solver failure for this method only
                    rows.append(row(sid, "B", name, rep, S.MODEL_FAILURE, None,
                                    error=f"solver: {type(e).__name__}: {str(e)[:200]}"))
    rows.sort(key=lambda r: (r["scenario"], r["condition"], r["method"], r["repeat"]))
    _write_private(Path(run_dir) / FILES["scores"], "".join(json.dumps(r, sort_keys=True, default=str) + "\n" for r in rows))
    return rows


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str]) -> int:
    if argv[:1] == ["env-check"]:
        problems = pl.environment_lock_problems()
        print(json.dumps(pl.environment() | {"platform": pl.platform_info()}, indent=1))
        print("\n".join(problems) if problems else "environment matches requirements-experiment.lock")
        return 1 if problems else 0
    if len(argv) != 2 or argv[0] not in {"run", "retry", "score", "validate"}:
        print(__doc__)
        return 2
    cmd, run_dir = argv[0], Path(argv[1])
    if cmd == "run":
        print(json.dumps(Runner(run_dir).run()))
    elif cmd == "retry":
        print(json.dumps(Runner(run_dir).retry()))
    elif cmd == "score":
        print(f"{len(score(run_dir))} rows")
    else:
        v = validate(run_dir)
        print(json.dumps(v, indent=1, default=str))
        return 1 if v["problems"] else 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
