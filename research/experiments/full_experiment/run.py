"""Confirmatory full experiment: 63 scenarios × R repeats (PROTOCOL.md).

Reuses the frozen pilot pieces unchanged (prompt rendering, API call with
served-model check, B1/B2 output mapping, extraction quality, per-category
metrics). Differences from the pilot harness, all in this file:

  * all 63 scenarios, natural-language files in reflica_bench/rn/full/;
  * LLM→B5 and gold→B5 conditions next to LLM→B4b and gold→B4b;
  * label remapping keeps confidence_scores, token_cost and wall_time_ms
    (the pilot's _remap dropped them);
  * failures are classified by stage, and a shared extraction is judged valid
    or invalid once, before either revision method sees it.

    python run.py write-rn                 # write the 63 R-N files (no API)
    python run.py check                    # pre-run gates (no API)
    python run.py plan                     # call count + prompt-size estimate (no API)
    python run.py run --run-id ID --i-approve-paid-run [--workers 4] [--completion]
    python run.py score --run-id ID        # or: --raw PATH --out DIR [--scenarios pilot]

The API key is read from the provider environment variable by the frozen
client only; nothing in this file reads, prints or stores it.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parents[1]
PILOT_DIR = HERE.parent / "rn_pilot"
sys.path[:0] = [str(RESEARCH), str(PILOT_DIR)]

import pilot  # noqa: E402  (frozen pilot harness; imported, never modified)
from reflica_bench import rn  # noqa: E402
from reflica_bench.adapters import AdapterOutput, StructuredAdapter_v1  # noqa: E402
from reflica_bench.b5.reflica import B5Reflica  # noqa: E402
from reflica_bench.baseline import RevisionResult  # noqa: E402
from reflica_bench.baselines.b4b_weighted_csp import B4bWeightedCSP  # noqa: E402
from reflica_bench.evaluator import NA  # noqa: E402
from reflica_bench.extraction_schema import ExtractionOutput  # noqa: E402
from reflica_bench.linter import _lint_expr  # noqa: E402
from reflica_bench.loader import load_scenario  # noqa: E402

RN_FULL = Path(rn.__file__).parent / "rn" / "full"
RUNS = HERE / "runs"
CALLS = pilot.CALLS  # {"B1": prompt, "B2": prompt, "EXTRACT": prompt}
LLM_CONDITIONS = ("B1", "B2", "LLM_B4b", "LLM_B5")
GATE_CONDITIONS = ("gold_B4b", "gold_B5")
REVISERS: dict[str, Callable[[], Any]] = {"B4b": B4bWeightedCSP, "B5": B5Reflica}

# Failure stages (PROTOCOL.md §8). "ok" is the only success status.
INFRA = ("missing", "api_error")
STAGES = {
    "missing": "API/infrastructure — call never logged",
    "api_error": "API/infrastructure — call failed after retries",
    "invalid_llm_output": "B1/B2 output truncated, not JSON or wrong shape",
    "invalid_extraction": "extraction truncated, not JSON or fails the typed schema (shared)",
    "extraction_failure": "schema-valid extraction cannot become a method input or fails formula lint (shared)",
    "solver_failure": "B4b raised on a valid extraction",
    "b5_failure": "B5 raised on a valid extraction",
    "evaluation_failure": "label mapping or metric computation raised (harness defect)",
}
METHOD_FAILURE = {"B4b": "solver_failure", "B5": "b5_failure"}


def cfg() -> dict:
    return json.loads((PILOT_DIR / "config.frozen.json").read_text())


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


# ---------------------------------------------------------------------------
# Scenario ids and natural-language files
# ---------------------------------------------------------------------------

def all_ids() -> list[str]:
    return sorted(load_scenario(p).scenario_id for p in rn.canonical_files())


def rn_full_path(sid: str) -> Path:
    return RN_FULL / f"{sid}.rn.json"


def load_rn_full(sid: str) -> rn.RNScenario:
    return rn.RNScenario.model_validate_json(rn_full_path(sid).read_text())


def _fresh(sid: str) -> tuple[rn.RNScenario, Any]:
    src = rn.source_path(sid)
    sc = load_scenario(src)
    return rn.render(sc, rn._sha(src)), sc


def write_rn_full() -> list[str]:
    """Render all 63 with the frozen renderer; refuse leaks; never overwrite a
    file whose content differs from a fresh render."""
    RN_FULL.mkdir(parents=True, exist_ok=True)
    written = []
    for sid in all_ids():
        r, sc = _fresh(sid)
        problems = rn.check_leakage(r, sc)
        if problems:
            raise ValueError(f"{sid}: leakage {problems}")
        text = r.model_dump_json(indent=2) + "\n"
        path = rn_full_path(sid)
        if path.exists() and path.read_text() != text:
            raise ValueError(f"{sid}: existing R-N file differs from a fresh render; not overwritten")
        if not path.exists():
            path.write_text(text)
            written.append(sid)
    return written


def check_rn_full() -> list[str]:
    problems = []
    for sid in all_ids():
        path = rn_full_path(sid)
        if not path.exists():
            problems.append(f"{sid}: R-N file missing")
            continue
        fresh, sc = _fresh(sid)
        on_disk = load_rn_full(sid)
        if on_disk.model_dump() != fresh.model_dump():
            problems.append(f"{sid}: R-N file differs from a fresh render")
        problems += [f"{sid}: leakage {p}" for p in rn.check_leakage(on_disk, sc)]
        if sid in rn.PILOT_IDS and on_disk.model_dump() != rn.load_rn(sid).model_dump():
            problems.append(f"{sid}: differs from the pilot R-N file")
    return problems


# ---------------------------------------------------------------------------
# Pre-run gates (PROTOCOL.md §7)
# ---------------------------------------------------------------------------

def fingerprint_problems() -> list[str]:
    c = cfg()
    p = PILOT_DIR
    expected = {p / "prompts" / k: v for k, v in c["prompts"].items()}
    expected |= {p / k: v for k, v in c["schemas"].items()}
    expected |= {p / "_api.py": c["client_fingerprint"], p / "repeatability.py": c["runner_fingerprint"],
                 p / "pilot.py": c["pilot_runner_fingerprint"],
                 RESEARCH / "reflica_bench" / "frozen_manifest.json": c["benchmark_manifest_sha256"],
                 RESEARCH / "reflica_bench" / "extraction_schema.py": c["extraction_schema_module_fingerprint"]}
    b5 = json.loads((RESEARCH / "reflica_bench" / "b5" / "FROZEN.json").read_text())
    expected |= {RESEARCH / "reflica_bench" / "b5" / f: h for f, h in b5["files"].items()}
    return [f"fingerprint mismatch: {f.relative_to(RESEARCH)}" for f, h in expected.items() if sha256(f) != h]


def gold_gate() -> list[str]:
    """gold→B4b and gold→B5 must run and score on every scenario."""
    problems = []
    for sid in all_ids():
        sc = load_scenario(rn.source_path(sid))
        for name, cls in REVISERS.items():
            try:
                pilot.metrics(cls().revise(StructuredAdapter_v1().adapt(sc, "gold")), sc)
            except Exception as e:  # noqa: BLE001
                problems.append(f"gold_{name} {sid}: {type(e).__name__}: {e}")
    return problems


def check() -> dict:
    report = {
        "manifest": rn.verify_manifest(),
        "fingerprints": fingerprint_problems(),
        "rn_full": check_rn_full(),
        "gold_gate": gold_gate(),
        "reminder": "also run `pytest -q` (gate 1); test_b5.py asserts 0 gold disagreements for B5",
    }
    report["passed"] = not any(report[k] for k in ("manifest", "fingerprints", "rn_full", "gold_gate"))
    return report


def plan(repeats: int | None = None) -> dict:
    """Expected calls and prompt sizes. No API."""
    from repeatability import render_prompt

    r = repeats or cfg()["repeats_per_call"]
    ids = all_ids()
    chars: dict[str, list[int]] = {k: [] for k in CALLS}
    for sid in ids:
        rnsc = load_rn_full(sid)
        for k, name in CALLS.items():
            s, u = render_prompt(name, rnsc)
            chars[k].append(len(s) + len(u))
    total_chars = sum(sum(v) for v in chars.values()) * r
    return {"scenarios": len(ids), "repeats": r, "calls": len(ids) * len(CALLS) * r,
            "prompt_chars_per_call_median": {k: sorted(v)[len(v) // 2] for k, v in chars.items()},
            "input_tokens_estimate_chars_div_4": total_chars // 4}


# ---------------------------------------------------------------------------
# Data collection
# ---------------------------------------------------------------------------

def read_raw(path: Path) -> dict[tuple, list[dict]]:
    out: dict[tuple, list[dict]] = {}
    if path.exists():
        for line in path.read_text().splitlines():
            d = json.loads(line)
            out.setdefault((d["scenario"], d["call"], d["repeat"]), []).append(d)
    return out


def select(records: list[dict] | None) -> dict | None:
    """First successful record if any, else the last attempt."""
    if not records:
        return None
    return next((r for r in records if r.get("ok")), records[-1])


def todo(raw: dict[tuple, list[dict]], ids: list[str], repeats: int, completion: bool) -> list[tuple]:
    jobs = []
    for sid in ids:
        for i in range(repeats):
            for k in CALLS:
                recs = raw.get((sid, k, i), [])
                if not completion and not recs:
                    jobs.append((sid, k, i))
                elif completion and recs and not any(r.get("ok") for r in recs) and len(recs) < 2:
                    jobs.append((sid, k, i))  # at most one logged data-completion attempt
    return jobs


def environment(run_dir: Path) -> dict:
    def sh(*a):
        try:
            return subprocess.run(a, capture_output=True, text=True, check=False).stdout.strip()
        except OSError:
            return None
    c = cfg()
    return {
        "started_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "python": sys.version, "platform": platform.platform(),
        "pip_freeze": sh(sys.executable, "-m", "pip", "freeze"),
        "git_commit": sh("git", "-C", str(RESEARCH), "rev-parse", "HEAD"),
        "git_dirty": bool(sh("git", "-C", str(RESEARCH), "status", "--porcelain")),
        "config_version": c["config_version"], "model_id": c["model_id"], "provider": c["provider_key"],
        "protocol_sha256": sha256(HERE / "PROTOCOL.md"), "runner_sha256": sha256(Path(__file__)),
        "analyse_sha256": sha256(HERE / "analyse.py"), "stats_sha256": sha256(HERE / "stats.py"),
    }


def run(run_id: str, workers: int = 4, completion: bool = False,
        call_fn: Callable | None = None, ids: list[str] | None = None) -> dict:
    """Make the API calls. `call_fn(system, user) -> (text, meta)` is injectable for tests."""
    c = cfg()
    if call_fn is None:
        import _api
        from repeatability import call
        if _api.PROVIDER != c["provider_key"]:
            raise SystemExit(f"set REFLICA_LLM_PROVIDER={c['provider_key']} (frozen provider)")

        def call_fn(system, user):
            return call(c, c["model_id"], system, user)
    from repeatability import render_prompt

    gate = check()
    if not gate["passed"]:
        raise SystemExit(f"pre-run gates failed: {json.dumps(gate, indent=1)}")
    run_dir = RUNS / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    raw_path = run_dir / "raw.jsonl"
    if not (run_dir / "env.json").exists():
        (run_dir / "env.json").write_text(json.dumps(environment(run_dir), indent=1) + "\n")
    ids = ids or all_ids()
    jobs = todo(read_raw(raw_path), ids, c["repeats_per_call"], completion)
    lock, abort = threading.Lock(), threading.Event()
    print(f"{len(jobs)} calls to make", flush=True)

    def one(job):
        if abort.is_set():
            return
        sid, k, i = job
        system, user = render_prompt(CALLS[k], load_rn_full(sid))
        rec = {"scenario": sid, "call": k, "repeat": i, "attempt": "completion" if completion else "first",
               "logged_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}
        try:
            text, meta = call_fn(system, user)
            rec.update(ok=True, meta=meta, content=text)
        except (Exception, SystemExit) as e:  # recorded, never retried silently
            rec.update(ok=False, error=str(e)[:300])
            if "ABORT" in str(e):  # served model differs from the frozen id
                abort.set()
        with lock, open(raw_path, "a") as f:
            f.write(json.dumps(rec) + "\n")
        print(f"{sid} {k} r{i} ok={rec['ok']}", flush=True)

    with ThreadPoolExecutor(workers) as ex:
        list(ex.map(one, jobs))
    if abort.is_set():
        raise SystemExit("ABORTED: served model differs from the frozen model id; see raw.jsonl")
    return {"run_dir": str(run_dir), "calls_made": len(jobs)}


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def remap(r: RevisionResult, m) -> RevisionResult:
    """Extracted labels → canonical ids. Unlike pilot._remap, keeps every
    per-node dimension including confidence_scores, plus cost fields."""
    def d(x):
        return None if x is None else {m(k): v for k, v in x.items() if m(k)}
    return RevisionResult(
        affected_set=None if r.affected_set is None else sorted({m(x) for x in r.affected_set if m(x)}),
        outcome_labels=d(r.outcome_labels), attribute_values=d(r.attribute_values),
        feasibility_status=d(r.feasibility_status), determinability=d(r.determinability),
        pathology_flags=d(r.pathology_flags), confidence_scores=d(r.confidence_scores),
        feasible_combinations=None if r.feasible_combinations is None
        else [sorted(filter(None, map(m, c))) for c in r.feasible_combinations],
        search_cost=r.search_cost, unsupported_dimensions=list(r.unsupported_dimensions),
        token_cost=r.token_cost, wall_time_ms=r.wall_time_ms)


def unmapped(r: RevisionResult, m) -> int:
    keys = set()
    for x in (r.outcome_labels, r.attribute_values, r.determinability):
        keys |= set(x or {})
    return sum(m(k) is None for k in keys)


def lint_extraction(mi) -> None:
    """Shared structural check, identical for both revision methods (same
    checks as the pilot's operational downstream check, without B4b)."""
    sat = (mi.rules.get("satisfaction_functions") or {}).get("entries", {}) or {}
    known = {n.id for n in mi.graph.nodes}
    for c in sat.get("computations", []) or []:
        _lint_expr(c["machine"], c["node"], known)
    for n, sf in (sat.get("status_functions", {}) or {}).items():
        for mp in sf["mapping"]:
            if mp["when"] != "otherwise":
                _lint_expr(mp["when"], n, known)


def _num(v):
    return None if v == NA or v is None else float(v)


def pooled_hits(by_type) -> float | None:
    """Pooled hit rate over attribute types: discrete exact_match, bounded and
    unbounded within_tolerance, signed sign_match, weighted by n."""
    if not isinstance(by_type, dict):
        return None
    hits = n = 0.0
    for d in by_type.values():
        rate = next((d[k] for k in ("exact_match", "within_tolerance", "sign_match") if k in d), NA)
        if d.get("n") and rate != NA:
            hits += rate * d["n"]
            n += d["n"]
    return hits / n if n else None


def primary(sc, m: dict) -> dict:
    """Primary-metric values for one scenario-repeat (PROTOCOL.md §5)."""
    gt = sc.ground_truth.nodes
    if sc.category <= 4:
        recall = _num(m.get("affected_node_recall"))
        has_affected = any(g.in_affected_set for g in gt.values())
        return {"over_flip": _num(m.get("over_flip_rate")),
                "missed_change": (1 - recall) if (has_affected and recall is not None) else None}
    if sc.category == 5:
        return {"value_accuracy": pooled_hits(m.get("attribute_accuracy_by_type"))}
    if sc.category == 6:
        if sc.subcategory == "C6-A":
            return {"value_accuracy": pooled_hits(m.get("aggregate_value_accuracy"))}
        return {"value_accuracy": _num(m.get("optimal_combination_accuracy"))}
    n_amb = sum(g.determinability.value == "AMBIGUOUS" for g in gt.values())
    n_det = len(gt) - n_amb
    fcr, far = _num(m.get("false_confidence_rate")), _num(m.get("false_abstention_rate"))
    return {"n_ambiguous": n_amb, "n_determinable": n_det,
            "false_confident": None if (n_amb and fcr is None) else (fcr or 0.0) * n_amb,
            "false_abstained": None if (n_det and far is None) else (far or 0.0) * n_det}


def worst_case(sc) -> dict:
    """Worst value of every primary metric (PROTOCOL.md §8, primary rule)."""
    gt = sc.ground_truth.nodes
    if sc.category <= 4:
        return {"over_flip": 1.0, "missed_change": 1.0 if any(g.in_affected_set for g in gt.values()) else None}
    if sc.category in (5, 6):
        return {"value_accuracy": 0.0}
    n_amb = sum(g.determinability.value == "AMBIGUOUS" for g in gt.values())
    return {"n_ambiguous": n_amb, "n_determinable": len(gt) - n_amb,
            "false_confident": float(n_amb), "false_abstained": float(len(gt) - n_amb)}


def _row(sc, condition, repeat, status, **kw) -> dict:
    row = {"scenario": sc.scenario_id, "category": sc.category, "subcategory": sc.subcategory,
           "condition": condition, "repeat": repeat, "status": status}
    row.update(kw)
    if status != "ok":
        row["primary"] = None
        row["primary_worst_case"] = worst_case(sc)
    return row


def _meta(rec: dict | None) -> dict | None:
    return None if rec is None else rec.get("meta")


def score_scenario(sc, alias: dict, codes: dict, repeats: int, raw: dict[tuple, list[dict]],
                   revisers: dict[str, Callable[[], Any]] | None = None) -> list[dict]:
    revisers = revisers or REVISERS
    m = pilot._mapper(alias)
    rows = []
    for name, cls in revisers.items():  # pre-run gate conditions (no LLM)
        try:
            met = pilot.metrics(cls().revise(StructuredAdapter_v1().adapt(sc, "gold")), sc)
            rows.append(_row(sc, f"gold_{name}", None, "ok", metrics=met, primary=primary(sc, met)))
        except Exception as e:  # noqa: BLE001
            rows.append(_row(sc, f"gold_{name}", None, METHOD_FAILURE[name], error=str(e)[:200]))
    b6 = RevisionResult(affected_set=sorted(n for n, g in sc.ground_truth.nodes.items() if g.in_affected_set))
    rows.append(_row(sc, "B6", None, "ok", metrics=pilot.metrics(b6, sc)))

    for i in range(repeats):
        for kind in ("B1", "B2"):
            rec = select(raw.get((sc.scenario_id, kind, i)))
            attempts = len(raw.get((sc.scenario_id, kind, i), []))
            if rec is None or not rec.get("ok"):
                rows.append(_row(sc, kind, i, "missing" if rec is None else "api_error", attempts=attempts))
                continue
            if (rec.get("meta") or {}).get("finish") == "length":
                rows.append(_row(sc, kind, i, "invalid_llm_output", error="truncated", call_meta=_meta(rec)))
                continue
            try:
                r, info = pilot.from_direct(kind, rec["content"], sc, alias, codes)
            except (ValueError, KeyError, TypeError, AttributeError) as e:
                rows.append(_row(sc, kind, i, "invalid_llm_output", error=str(e)[:200], call_meta=_meta(rec)))
                continue
            try:
                met = pilot.metrics(r, sc)
                rows.append(_row(sc, kind, i, "ok", metrics=met, primary=primary(sc, met),
                                 call_meta=_meta(rec), attempts=attempts, **info))
            except Exception as e:  # noqa: BLE001
                rows.append(_row(sc, kind, i, "evaluation_failure", error=str(e)[:200]))

        # One shared extraction, judged once, then given to both methods.
        rec = select(raw.get((sc.scenario_id, "EXTRACT", i)))
        attempts = len(raw.get((sc.scenario_id, "EXTRACT", i), []))
        shared_status, shared_err, mi, quality = None, None, None, None
        if rec is None or not rec.get("ok"):
            shared_status = "missing" if rec is None else "api_error"
        elif (rec.get("meta") or {}).get("finish") == "length":
            shared_status, shared_err = "invalid_extraction", "truncated"
        else:
            try:
                x = ExtractionOutput.model_validate_json(rec["content"])
            except ValueError as e:  # pydantic ValidationError and JSON errors
                shared_status, shared_err = "invalid_extraction", str(e)[:200]
            else:
                try:
                    mi = x.to_method_input()
                    lint_extraction(mi)
                except Exception as e:  # noqa: BLE001  (LintError, conversion errors)
                    shared_status, shared_err = "extraction_failure", f"{type(e).__name__}: {str(e)[:200]}"
                try:  # secondary metric; its failure never changes the shared status
                    quality = pilot.extraction_quality(x, sc, alias)
                except Exception as e:  # noqa: BLE001
                    quality = {"evaluation_error": str(e)[:200]}
        for name, cls in revisers.items():
            cond = f"LLM_{name}"
            if shared_status:
                rows.append(_row(sc, cond, i, shared_status, shared=True, error=shared_err,
                                 call_meta=_meta(rec), attempts=attempts))
                continue
            try:
                r = cls().revise(AdapterOutput(mi, None, {}))
            except Exception as e:  # noqa: BLE001
                rows.append(_row(sc, cond, i, METHOD_FAILURE[name], shared=False,
                                 error=f"{type(e).__name__}: {str(e)[:200]}", extraction=quality,
                                 call_meta=_meta(rec), attempts=attempts))
                continue
            try:
                r2 = remap(r, m)
                met = pilot.metrics(r2, sc)
                rows.append(_row(sc, cond, i, "ok", metrics=met, primary=primary(sc, met), extraction=quality,
                                 unmapped_labels=unmapped(r, m), call_meta=_meta(rec), attempts=attempts,
                                 confidence_available=r2.confidence_scores is not None))
            except Exception as e:  # noqa: BLE001
                rows.append(_row(sc, cond, i, "evaluation_failure", error=str(e)[:200]))
    return rows


def score(raw_path: Path, out_dir: Path, ids: list[str] | None = None, repeats: int | None = None,
          rn_loader: Callable[[str], Any] | None = None) -> dict:
    c = cfg()
    repeats = repeats or c["repeats_per_call"]
    ids = ids or all_ids()
    rn_loader = rn_loader or load_rn_full
    raw = read_raw(raw_path)
    rows = []
    for sid in ids:
        sc = load_scenario(rn.source_path(sid))
        rows += score_scenario(sc, rn_loader(sid).alias_map, c["reason_to_code"], repeats, raw)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "scores.jsonl").write_text("".join(json.dumps(r, sort_keys=True, default=str) + "\n" for r in rows))
    summary = operational_summary(rows)
    summary["identical_repeats"] = identical_repeats(raw, ids, repeats)
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=1, sort_keys=True) + "\n")
    return summary


def identical_repeats(raw: dict[tuple, list[dict]], ids: list[str], repeats: int) -> dict:
    """Per call type: share of scenarios whose successful repeats are all byte-identical."""
    out = {}
    for k in CALLS:
        same = total = 0
        for sid in ids:
            texts = [r["content"] for i in range(repeats) if (r := select(raw.get((sid, k, i)))) and r.get("ok")]
            if len(texts) == repeats:
                total += 1
                same += len(set(texts)) == 1
        out[k] = {"scenarios_complete": total, "all_repeats_identical": same,
                  "share": same / total if total else None}
    return out


def operational_summary(rows: list[dict]) -> dict:
    """Status counts per condition — operational failure rates, reported
    separately from accuracy."""
    out: dict[str, dict] = {}
    for r in rows:
        s = out.setdefault(r["condition"], {"n": 0, "status": {}})
        s["n"] += 1
        s["status"][r["status"]] = s["status"].get(r["status"], 0) + 1
    for s in out.values():
        s["failure_rate"] = 1 - s["status"].get("ok", 0) / s["n"]
    return out


def main(argv: list[str]) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["write-rn", "check", "plan", "run", "score"])
    ap.add_argument("--run-id")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--completion", action="store_true", help="one logged rerun of failed calls")
    ap.add_argument("--i-approve-paid-run", action="store_true")
    ap.add_argument("--raw", type=Path)
    ap.add_argument("--out", type=Path)
    ap.add_argument("--scenarios", choices=["all", "pilot"], default="all")
    a = ap.parse_args(argv)
    ids = list(rn.PILOT_IDS) if a.scenarios == "pilot" else None
    if a.command == "write-rn":
        print(json.dumps({"written": write_rn_full()}, indent=1))
    elif a.command == "check":
        rep = check()
        print(json.dumps(rep, indent=1))
        sys.exit(0 if rep["passed"] else 1)
    elif a.command == "plan":
        print(json.dumps(plan(), indent=1))
    elif a.command == "run":
        if not (a.run_id and a.i_approve_paid_run):
            raise SystemExit("run needs --run-id and --i-approve-paid-run (owner approval required)")
        t0 = time.time()
        print(json.dumps(run(a.run_id, a.workers, a.completion, ids=ids), indent=1))
        print(f"elapsed {time.time() - t0:.0f}s")
    else:
        raw = a.raw or (RUNS / a.run_id / "raw.jsonl")
        out = a.out or (RUNS / a.run_id)
        print(json.dumps(score(raw, out, ids), indent=1))


if __name__ == "__main__":
    main(sys.argv[1:])
