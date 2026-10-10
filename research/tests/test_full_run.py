"""Offline tests of the full-run runner, validation, scoring and analysis.

No model or network: every socket connection raises, and the transport is a
fake that replays the 144 real pilot responses (16 pilot scenarios) and
answers the other scenarios from gold labels (B1/B2) or with invalid JSON
(EXTRACT). The freeze gate runs for real against a temporary frozen protocol.
"""

from __future__ import annotations

import ast
import json
import os
import socket
import sys
from pathlib import Path

import pytest

from reflica_bench import protocol_lock as pl

pytest.importorskip("ortools")
FULL_RUN = pl.FULL_RUN
sys.path.insert(0, str(FULL_RUN))
import runner as R  # noqa: E402
import analysis as A  # noqa: E402
import _api  # noqa: E402  (imported via runner's sys.path)

MODEL = R._cfg()["model_id"]
SECRET = "nvapi-" + "k" * 40
FROZEN = "# Protocol\n\n**Status: FROZEN v1.0 (test).**\n"
SUPERSEDED = "# Protocol\n\n**Status: SUPERSEDED — test.**\n"
DECISION = {"MUST_CHANGE": "changed", "MUST_STAY_STABLE": "not_changed",
            "UNCERTAIN": "cannot_answer", "REQUIRES_REEVALUATION": "needs_human_review"}


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    def refuse(*a, **k):
        raise AssertionError("network access attempted in an offline test")
    monkeypatch.setattr(socket.socket, "connect", refuse)
    monkeypatch.setattr(socket, "create_connection", refuse)


@pytest.fixture
def env(monkeypatch):
    monkeypatch.setenv("REFLICA_LLM_PROVIDER", "nvidia")
    monkeypatch.setenv("NVIDIA_API_KEY", SECRET)
    monkeypatch.setattr(_api, "PROVIDER", "nvidia")
    monkeypatch.setattr(_api, "KEY_ENV", "NVIDIA_API_KEY")


@pytest.fixture
def protocol(tmp_path):
    d = tmp_path / "protocol"
    d.mkdir()
    (d / "PROTOCOL.md").write_text(SUPERSEDED)
    (d / "PROTOCOL.v1.0.md").write_text(FROZEN)
    sha = pl.sha256(d / "PROTOCOL.v1.0.md")
    fps = pl.fingerprints(d / "PROTOCOL.v1.0.md", full_run_dir=d)
    (d / pl.LOCK_NAME).write_text(json.dumps({"versions": [
        {"version": "1.0", "file": "PROTOCOL.v1.0.md", "sha256": sha, "frozen_at": "2026-10-10",
         "approved_by": "test", "supersedes": None, "fingerprints": fps}]}))
    return d


SCEN = R.rendered_scenarios()
PILOT = {(d["scenario"], d["call"], d["repeat"]): d["content"]
         for d in map(json.loads, (R.PILOT_DIR / "pilot_raw.jsonl").read_text().splitlines()) if d.get("ok")}


def gold_answer(sid: str, kind: str) -> str:
    sc, r = SCEN[sid]
    label = {}
    for lab, nid in r.alias_map.items():
        label.setdefault(nid, lab)
    ents = [{"label": label[nid], "decision": DECISION[g.outcome_label.value], "reason": None,
             "attributes": g.attribute_values, "confidence": 1.0}
            for nid, g in sc.ground_truth.nodes.items() if nid in label]
    return json.dumps({"entities": ents, "valid_combinations": None})


class Fake:
    """Replay transport. `fail` maps job -> list of exceptions to raise, in order."""

    def __init__(self, fail=None, served=MODEL, content_hook=None):
        self.calls: list[tuple] = []
        self.events: list[str] | None = None
        self.fail = {k: list(v) for k, v in (fail or {}).items()}
        self.served = served
        self.hook = content_hook
        self._job = None

    def __call__(self, cfg, model, system, user):
        job = self._job
        self.calls.append(job)
        if self.events is not None:
            self.events.append("call")
        if self.fail.get(job):
            raise self.fail[job].pop(0)
        sid, call, rep = job
        text = PILOT.get(job) or (gold_answer(sid, call) if call != "EXTRACT" else "not json")
        if self.hook:
            text = self.hook(job, text)
        return text, {"served": self.served, "finish": "stop", "out_tokens": 1, "retries": 0, "latency_s": 0.0}


def make_runner(run_dir, protocol, fake, gate=None, clock=None):
    r = R.Runner(run_dir, protocol_dir=protocol, transport=fake, gate=gate,
                 **({"clock": clock} if clock else {}))
    orig = r._attempt

    def attempt(idx, job, scen, n):  # tell the fake which job it is answering
        fake._job = tuple(job)
        return orig(idx, job, scen, n)
    r._attempt = attempt
    return r


def spy_gate(events):
    def g():
        events.append("gate")
    return g


# --- the gate ----------------------------------------------------------------

def test_draft_protocol_blocks_everything(tmp_path, env):
    d = tmp_path / "draft"
    d.mkdir()
    (d / "PROTOCOL.md").write_text("# P\n\n**Status: DRAFT — NOT FROZEN.**\n")
    fake = Fake()
    with pytest.raises(R.Fatal, match="gate"):
        make_runner(tmp_path / "run", d, fake).run()
    assert fake.calls == [] and not (tmp_path / "run" / "raw.jsonl").exists()
    assert not (tmp_path / "run" / "gate.json").exists()


def test_real_gate_runs_before_each_request(tmp_path, env, protocol, monkeypatch):
    seen = []
    real = pl.assert_ready_for_llm_calls
    monkeypatch.setattr(pl, "assert_ready_for_llm_calls", lambda d=pl.FULL_RUN: (seen.append("gate"), real(d))[1])
    fake = Fake()
    fake.events = seen
    make_runner(tmp_path / "run", protocol, fake).run(max_calls=3)
    # setup: full gate + write_gate_record (which re-runs it); then one full gate before every request
    assert seen == ["gate", "gate"] + ["gate", "call"] * 3
    assert json.loads((tmp_path / "run" / "gate.json").read_text())["protocol_sha256"] == pl.sha256(protocol / "PROTOCOL.v1.0.md")


def test_gate_failure_mid_run_stops_before_the_request(tmp_path, env, protocol):
    run = tmp_path / "run"
    make_runner(run, protocol, Fake()).run(max_calls=0)
    n = {"k": 0}

    def gate():
        n["k"] += 1
        if n["k"] == 3:
            raise RuntimeError("fingerprint mismatch: b5_version_id")
    fake = Fake()
    with pytest.raises(R.Fatal, match="b5_version_id"):
        make_runner(run, protocol, fake, gate=gate).run()
    assert len(fake.calls) == 2
    recs = R.read_raw(run)
    assert recs[-1]["error_class"] == "fatal" and "content" not in recs[-1]
    with pytest.raises(R.Fatal, match="stopped"):
        make_runner(run, protocol, Fake(), gate=lambda: None).run()


def test_wrong_provider_or_missing_key_blocks_requests(tmp_path, env, protocol, monkeypatch):
    monkeypatch.setattr(_api, "PROVIDER", "openai")
    fake = Fake()
    with pytest.raises(R.Fatal, match="provider"):
        make_runner(tmp_path / "run", protocol, fake).run(max_calls=1)
    assert fake.calls == []


def test_runner_code_only_calls_the_transport_behind_the_gate():
    tree = ast.parse((FULL_RUN / "runner.py").read_text())
    callers = []
    for fn in ast.walk(tree):
        if isinstance(fn, ast.FunctionDef):
            for node in ast.walk(fn):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "transport":
                    callers.append(fn.name)
    assert callers == ["_request"]
    src = ast.get_source_segment((FULL_RUN / "runner.py").read_text(),
                                 next(f for f in ast.walk(tree) if isinstance(f, ast.FunctionDef) and f.name == "_request"))
    assert src.index("self.gate()") < src.index("self.transport(")


# --- run order, failures, logging --------------------------------------------

def test_served_model_mismatch_is_fatal(tmp_path, env, protocol):
    fake = Fake(served="some/other-model")
    with pytest.raises(R.Fatal, match="served model"):
        make_runner(tmp_path / "run", protocol, fake).run()
    assert len(fake.calls) == 1


def test_abort_from_client_is_fatal(tmp_path, env, protocol):
    run = tmp_path / "run"
    make_runner(run, protocol, Fake()).run(max_calls=0)
    first = tuple(json.loads((run / "plan.json").read_text())["jobs"][0])
    fake = Fake(fail={first: [SystemExit("ABORT: served model 'x' != frozen")]})
    with pytest.raises(R.Fatal):
        make_runner(run, protocol, fake, gate=lambda: None).run()


def test_pause_after_consecutive_infrastructure_failures_and_d5(tmp_path, env, protocol):
    run = tmp_path / "run"
    t = {"now": 1_000_000.0}
    make_runner(run, protocol, Fake()).run(max_calls=0)
    jobs = [tuple(j) for j in json.loads((run / "plan.json").read_text())["jobs"]]
    fake = Fake(fail={j: [SystemExit("HTTP 503: busy")] for j in jobs})
    out = make_runner(run, protocol, fake, gate=lambda: None, clock=lambda: t["now"]).run()
    assert out == {"status": "paused", "calls": R.PAUSE_AFTER}
    t["now"] += 24 * 3600
    assert make_runner(run, protocol, fake, gate=lambda: None, clock=lambda: t["now"]).run()["status"] == "paused"
    t["now"] += 7 * 24 * 3600
    with pytest.raises(R.Fatal, match="D5"):
        make_runner(run, protocol, fake, gate=lambda: None, clock=lambda: t["now"]).run()


def test_raw_log_is_private_chained_and_redacted(tmp_path, env, protocol):
    run = tmp_path / "run"
    fake = Fake(content_hook=lambda job, text: text + " " + SECRET)
    make_runner(run, protocol, fake).run(max_calls=2)
    raw = run / "raw.jsonl"
    assert oct(os.stat(raw).st_mode & 0o777) == "0o600" and oct(os.stat(run).st_mode & 0o777) == "0o700"
    text = raw.read_text()
    assert SECRET not in text and "[REDACTED]" in text
    assert all(r.get("redacted") for r in R.read_raw(run))


# --- end to end ---------------------------------------------------------------

@pytest.fixture(scope="module")
def full_run(tmp_path_factory):
    """One complete offline run: real gate at setup, spy gate per request,
    two infrastructure failures (one recovered by the re-run, one not)."""
    mp = pytest.MonkeyPatch()
    mp.setenv("REFLICA_LLM_PROVIDER", "nvidia")
    mp.setenv("NVIDIA_API_KEY", SECRET)
    mp.setattr(_api, "PROVIDER", "nvidia")
    mp.setattr(_api, "KEY_ENV", "NVIDIA_API_KEY")
    mp.setattr(socket.socket, "connect", lambda *a, **k: (_ for _ in ()).throw(AssertionError("network")))
    base = tmp_path_factory.mktemp("e2e")
    proto = base / "protocol"
    proto.mkdir()
    (proto / "PROTOCOL.md").write_text(SUPERSEDED)
    (proto / "PROTOCOL.v1.0.md").write_text(FROZEN)
    fps = pl.fingerprints(proto / "PROTOCOL.v1.0.md", full_run_dir=proto)
    (proto / pl.LOCK_NAME).write_text(json.dumps({"versions": [
        {"version": "1.0", "file": "PROTOCOL.v1.0.md", "sha256": pl.sha256(proto / "PROTOCOL.v1.0.md"),
         "frozen_at": "2026-10-10", "approved_by": "test", "supersedes": None, "fingerprints": fps}]}))
    run = base / "run"
    make_runner(run, proto, Fake()).run(max_calls=0)
    jobs = [tuple(j) for j in json.loads((run / "plan.json").read_text())["jobs"]]
    flaky, dead = jobs[10], jobs[20]
    events: list[str] = []
    fake = Fake(fail={flaky: [SystemExit("HTTP 500: x")], dead: [SystemExit("HTTP 503: x"), SystemExit("HTTP 503: x")]})
    fake.events = events
    out = make_runner(run, proto, fake, gate=spy_gate(events)).run()
    retry = make_runner(run, proto, fake, gate=spy_gate(events)).retry()
    yield {"run": run, "proto": proto, "jobs": jobs, "fake": fake, "events": events, "out": out,
           "retry": retry, "flaky": flaky, "dead": dead}
    mp.undo()


def test_full_run_order_gate_and_retry(full_run):
    f = full_run
    assert f["out"] == {"status": "done", "calls": len(f["jobs"])} and f["retry"] == {"status": "done", "calls": 2}
    ev = f["events"]
    assert ev.count("gate") == ev.count("call") == len(f["jobs"]) + 2
    assert all(ev[i] == "gate" and ev[i + 1] == "call" for i in range(0, len(ev), 2))
    first = [c for i, c in enumerate(f["fake"].calls) if c not in f["fake"].calls[:i]]
    assert first == f["jobs"]  # executed in the saved, seeded plan order
    expected = sorted((s, c, r) for s in SCEN for c in R.CALL_TYPES for r in range(3))
    import random
    random.Random(R.SEED).shuffle(expected)
    assert f["jobs"] == expected


def test_full_run_validates_and_reports_missingness(full_run):
    v = R.validate(full_run["run"], protocol_dir=full_run["proto"])
    assert v["problems"] == []
    a = v["summary"]["analysis_set"]
    assert a["calls_planned"] == 567 and a["calls_infra_missing"] == 1
    sid, call, rep = full_run["dead"]
    assert rep not in a["common_repeats"][sid]


def test_validation_detects_tampering(full_run, tmp_path):
    import shutil
    run = tmp_path / "copy"
    shutil.copytree(full_run["run"], run)
    proto = full_run["proto"]
    lines = (run / "raw.jsonl").read_text().splitlines()
    rec = json.loads(lines[5])
    rec["content"] = "edited"
    lines[5] = json.dumps(rec, sort_keys=True)
    (run / "raw.jsonl").write_text("\n".join(lines) + "\n")
    os.chmod(run / "raw.jsonl", 0o600)
    assert any("hash chain" in p for p in R.validate(run, protocol_dir=proto)["problems"])
    shutil.rmtree(run)
    shutil.copytree(full_run["run"], run)
    (run / "gate.json").unlink()
    assert any("gate" in p for p in R.validate(run, protocol_dir=proto)["problems"])
    with pytest.raises(RuntimeError, match="failed validation"):
        A.analyze(run, protocol_dir=proto, write=False)


def test_incomplete_run_cannot_be_analysed(tmp_path, env, protocol):
    run = tmp_path / "run"
    make_runner(run, protocol, Fake()).run(max_calls=4)
    assert any("never attempted" in p for p in R.validate(run, protocol_dir=protocol)["problems"])
    with pytest.raises(RuntimeError, match="failed validation"):
        A.analyze(run, protocol_dir=protocol, write=False)


def test_scoring_and_analysis_end_to_end(full_run):
    rows = R.score(full_run["run"])
    assert {r["status"] for r in rows} == {"ok", "model_failure", "infra_missing"}
    b5 = [r for r in rows if r["condition"] == "B" and r["method"] == "B5"]
    pilot_ids = {k[0] for k in PILOT}
    assert all(r["status"] == "model_failure" for r in b5 if r["scenario"] not in pilot_ids and r["status"] != "infra_missing")
    gold_b1 = [r for r in rows if r["method"] == "B1" and r["status"] == "ok" and r["scenario"] not in pilot_ids]
    assert gold_b1 and all(r["counts"]["primary"] == 1.0 for r in gold_b1)  # gold answers score perfectly
    res = A.analyze(full_run["run"], protocol_dir=full_run["proto"], write=False)
    def walk(o):  # S1 = D: no verdicts, no p-values anywhere in the results
        if isinstance(o, dict):
            for k, v in o.items():
                assert "verdict" not in k and not k.startswith("p_") and "holm" not in k, k
                walk(v)
        elif isinstance(o, (list, tuple)):
            for v in o:
                walk(v)
        else:
            assert o not in ("Supported", "Contradicted", "Inconclusive"), o
    walk(res)
    q = res["questions"]
    for key in ("Q1_B5_minus_B1", "Q2_B5_minus_B2", "Q4_B5_minus_B4b"):
        lo, hi = q[key]["ci95"]
        assert lo <= q[key]["estimate"] <= hi and q[key]["n_scenarios"] == res["missingness"]["analysis_set_size"]
    # node-level estimate equals a hand computation from scores.jsonl over the common repeats
    common = R.validate(full_run["run"], protocol_dir=full_run["proto"])["summary"]["analysis_set"]["common_repeats"]
    per = {}
    for r in rows:
        if r["condition"] == "B" and r["method"] == "B5" and r["scenario"] in common and r["repeat"] in common[r["scenario"]]:
            per.setdefault(r["scenario"], []).append(r["counts"]["primary"])
    hand = sum(sum(v) / len(v) for v in per.values()) / len(per)
    assert q["node_correctness_by_method"]["B|B5"]["estimate"] == pytest.approx(hand)
    b1 = {}
    for r in rows:
        if r["method"] == "B1" and r["scenario"] in common and r["repeat"] in common[r["scenario"]]:
            b1.setdefault(r["scenario"], []).append(r["counts"]["primary"])
    hand_d = sum(sum(per[s]) / len(per[s]) - sum(b1[s]) / len(b1[s]) for s in per) / len(per)
    assert q["Q1_B5_minus_B1"]["estimate"] == pytest.approx(hand_d)   # sign: B5 − B1
    assert q["Q5a_false_confidence"]["ambiguous_nodes"] == 19 and q["Q5a_false_confidence"]["ambiguous_scenarios"] == 11
    assert "reference_line_D1" in q["Q5b_false_abstention_B5"] and q["Q4_B5_minus_B4b"]["reference_line_D2"]["margin"] == -0.05
    assert res["missingness"]["calls_infra_missing"] == 1
    assert set(q["false_abstention_by_method"]) == {"direct|B1", "direct|B2", "B|B3", "B|B4a", "B|B4b", "B|B5"}
    assert q["false_abstention_by_method"]["B|B5"]["pooled_rate"] == q["Q5b_false_abstention_B5"]["pooled_rate"]
    assert res["secondary_scenario_level"]["fully_correct_by_category"]["B|B5"]
    ca = res["condition_A_gold_input_sanity"]
    assert ca["B5"]["mean_node_correctness"] == 1.0 and ca["B5"]["scenarios"] == 63   # B5 v0.1.0 matches gold
    assert ca["B4b"]["falsely_confident"] == 11 and ca["B3"]["falsely_confident"] == 19  # Appendix A, check 2
    for v in q.values():
        if isinstance(v, dict) and "ci95" in v:
            assert v["interval"].startswith("APPROXIMATE") and "DESCRIPTIVE" in v["interval"]
    for v in q["node_correctness_by_method"].values():
        assert v["interval"].startswith("APPROXIMATE")
    assert "cluster" in q["Q5b_false_abstention_B5"]["interval"] and "11 scenarios" in q["Q5a_false_confidence"]["interval"]
    assert "cluster" in res["secondary_scenario_level"]["caution"]
    att = res["error_patterns"]["rq4_attribution_B5"]
    assert sum(att[k] for k in ("correct", "wrong_with_extraction_error", "wrong_with_correct_extraction",
                                "failed_output")) == sum(len(v) for v in common.values())
    rq2 = res["descriptive_rq2_cat5_6"]
    attr = [k for k in rq2["direct|B1"] if "binarisation" in k or "aggregate_value" in k]
    assert attr and all(rq2["B|B3"][k] == "N/A" for k in attr)  # B3 outputs no attribute values
    assert A.analyze(full_run["run"], protocol_dir=full_run["proto"], write=False) == res  # deterministic


def test_exact_secret_is_redacted_even_if_it_does_not_look_like_a_key(tmp_path, env, protocol, monkeypatch):
    plain = "plain-secret-value-0123456789"
    monkeypatch.setenv("NVIDIA_API_KEY", plain)
    run = tmp_path / "run"
    make_runner(run, protocol, Fake(content_hook=lambda job, text: text + plain)).run(max_calls=1)
    assert plain not in (run / "raw.jsonl").read_text()


def test_second_retry_never_makes_a_third_attempt(full_run):
    fake = Fake(fail={full_run["dead"]: [SystemExit("HTTP 503: x")]})
    events: list[str] = []
    fake.events = events
    out = make_runner(full_run["run"], full_run["proto"], fake, gate=spy_gate(events)).retry()
    assert out == {"status": "done", "calls": 0} and fake.calls == []
