"""Offline tests for the confirmatory runner, scoring and statistics.

No model calls: inputs are stored pilot responses, synthetic records and
injected failures.
"""
from __future__ import annotations

import importlib.util
import json
import random
import statistics
import sys
from pathlib import Path

import pytest

FULL = Path(__file__).resolve().parents[1] / "experiments" / "full_experiment"
PILOT_RAW = FULL.parent / "rn_pilot" / "pilot_raw.jsonl"
sys.path.insert(0, str(FULL))


def _load(name: str, file: str):
    spec = importlib.util.spec_from_file_location(name, FULL / file)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


R = _load("full_run", "run.py")
import stats as S  # noqa: E402  (experiments/full_experiment/stats.py)

A = _load("full_analyse", "analyse.py")

from reflica_bench import rn  # noqa: E402
from reflica_bench.baseline import RevisionResult  # noqa: E402
from reflica_bench.loader import load_scenario  # noqa: E402

T72 = "cat7_conflicting_evidence_edit_001"  # pilot case with the invented preference rule
CAT5 = "cat5_threshold_partial_partial_001"
CODES = R.cfg()["reason_to_code"]


def _pilot_raw() -> dict:
    return R.read_raw(PILOT_RAW)


def _sc(sid):
    return load_scenario(rn.source_path(sid))


def _rows(sid, raw, revisers=None, repeats=3):
    return R.score_scenario(_sc(sid), R.load_rn_full(sid).alias_map, CODES, repeats, raw, revisers)


def _get(rows, cond, rep):
    return next(r for r in rows if r["condition"] == cond and r["repeat"] == rep)


# ---------------------------------------------------------------------------
# Natural-language files and pre-run gates
# ---------------------------------------------------------------------------

def test_all_63_rn_files_present_leak_free_and_equal_to_fresh_render():
    assert len(R.all_ids()) == 63
    assert R.check_rn_full() == []


def test_pre_run_gates_pass():
    rep = R.check()
    assert rep["passed"], rep


def test_plan_counts_calls():
    p = R.plan()
    assert p["calls"] == 63 * 3 * 3 and p["scenarios"] == 63


# ---------------------------------------------------------------------------
# Remapping and confidence propagation
# ---------------------------------------------------------------------------

def test_remap_keeps_confidence_and_cost_fields():
    m = {"Alpha": "a", "Beta": "b"}.get
    r = RevisionResult(affected_set=["Alpha", "Ghost"], outcome_labels={"Alpha": "X", "Ghost": "Y"},
                       confidence_scores={"Alpha": 1.0, "Beta": 0.0}, determinability={"Beta": "AMBIGUOUS"},
                       token_cost=7, wall_time_ms=9)
    r2 = R.remap(r, m)
    assert r2.confidence_scores == {"a": 1.0, "b": 0.0}
    assert r2.affected_set == ["a"] and r2.outcome_labels == {"a": "X"}
    assert (r2.token_cost, r2.wall_time_ms) == (7, 9)
    assert R.unmapped(r, m) == 1


def test_confidence_reaches_scored_b5_rows_on_real_pilot_extraction():
    rows = _rows(T72, _pilot_raw())
    b5 = [r for r in rows if r["condition"] == "LLM_B5"]
    assert all(r["status"] == "ok" and r["confidence_available"] for r in b5)


# ---------------------------------------------------------------------------
# Failure attribution (PROTOCOL.md §8)
# ---------------------------------------------------------------------------

def test_invented_rule_is_a_solver_failure_for_b4b_only_not_a_shared_extraction_failure():
    rows = _rows(T72, _pilot_raw())
    b4b, b5 = _get(rows, "LLM_B4b", 1), _get(rows, "LLM_B5", 1)
    assert b4b["status"] == "solver_failure" and b4b["shared"] is False
    assert b5["status"] == "ok"
    assert b5["primary"]["n_ambiguous"] >= 1  # abstention is scored, not treated as failure


def test_missing_and_api_errors_are_infrastructure_and_shared():
    raw = {(CAT5, "B1", 0): [{"ok": False, "error": "HTTP 500"}]}
    rows = _rows(CAT5, raw, repeats=1)
    assert _get(rows, "B1", 0)["status"] == "api_error"
    assert _get(rows, "B2", 0)["status"] == "missing"
    for c in ("LLM_B4b", "LLM_B5"):
        r = _get(rows, c, 0)
        assert r["status"] == "missing" and r["shared"] is True


@pytest.mark.parametrize("content,finish", [("not json", "stop"), ("{}", "stop"), ('{"graph": 1}', "stop"),
                                            ("{}", "length")])
def test_invalid_extraction_is_shared_identically_by_both_methods(content, finish):
    raw = {(CAT5, "EXTRACT", 0): [{"ok": True, "content": content, "meta": {"finish": finish}}]}
    rows = _rows(CAT5, raw, repeats=1)
    a, b = _get(rows, "LLM_B4b", 0), _get(rows, "LLM_B5", 0)
    assert a["status"] == b["status"] == "invalid_extraction"
    assert a["shared"] is b["shared"] is True
    assert a["primary_worst_case"] == b["primary_worst_case"]


def test_truncated_or_unparseable_direct_output_is_invalid_llm_output():
    raw = {(CAT5, "B1", 0): [{"ok": True, "content": '{"entities": []}', "meta": {"finish": "length"}}],
           (CAT5, "B2", 0): [{"ok": True, "content": "Sure! here you go", "meta": {"finish": "stop"}}]}
    rows = _rows(CAT5, raw, repeats=1)
    assert _get(rows, "B1", 0)["status"] == "invalid_llm_output"
    assert _get(rows, "B2", 0)["status"] == "invalid_llm_output"


class _Crash:
    def revise(self, _):
        raise RuntimeError("boom")


class _Garbage:
    def revise(self, _):
        return object()  # not a RevisionResult → remap/metrics fail


def test_solver_crash_and_b5_crash_are_attributed_to_their_method_only():
    raw = _pilot_raw()
    rows = _rows(CAT5, raw, revisers={"B4b": _Crash, "B5": R.REVISERS["B5"]})
    assert {r["status"] for r in rows if r["condition"] == "LLM_B4b"} == {"solver_failure"}
    assert {r["status"] for r in rows if r["condition"] == "LLM_B5"} == {"ok"}
    assert _get(rows, "gold_B4b", None)["status"] == "solver_failure"
    rows = _rows(CAT5, raw, revisers={"B4b": R.REVISERS["B4b"], "B5": _Crash})
    assert {r["status"] for r in rows if r["condition"] == "LLM_B5"} == {"b5_failure"}
    assert {r["status"] for r in rows if r["condition"] == "LLM_B4b"} == {"ok"}


def test_harness_defects_are_evaluation_failures():
    rows = _rows(CAT5, _pilot_raw(), revisers={"B4b": R.REVISERS["B4b"], "B5": _Garbage})
    assert {r["status"] for r in rows if r["condition"] == "LLM_B5"} == {"evaluation_failure"}
    a = A.analyse(rows)
    assert a["valid"] is False and a["evaluation_failures"] == 3


def test_identical_repeat_share():
    ok = lambda t: [{"ok": True, "content": t}]  # noqa: E731
    raw = {("a", "B1", 0): ok("x"), ("a", "B1", 1): ok("x"), ("b", "B1", 0): ok("x"), ("b", "B1", 1): ok("y"),
           ("c", "B1", 0): ok("x")}
    res = R.identical_repeats(raw, ["a", "b", "c"], 2)["B1"]
    assert res == {"scenarios_complete": 2, "all_repeats_identical": 1, "share": 0.5}


def test_completion_pass_selects_first_success_and_retries_at_most_once():
    fail, ok = {"ok": False, "error": "HTTP 503"}, {"ok": True, "content": "x"}
    assert R.select([fail, ok]) is ok and R.select([fail]) is fail and R.select(None) is None
    raw = {("s", "B1", 0): [fail], ("s", "B2", 0): [fail, fail], ("s", "EXTRACT", 0): [ok]}
    assert R.todo(raw, ["s"], 1, completion=True) == [("s", "B1", 0)]
    assert R.todo(raw, ["s"], 1, completion=False) == []


# ---------------------------------------------------------------------------
# Runner with an injected (fake) model — no network
# ---------------------------------------------------------------------------

def test_run_logs_every_call_and_aborts_on_served_model_mismatch(tmp_path, monkeypatch):
    monkeypatch.setattr(R, "RUNS", tmp_path)
    monkeypatch.setattr(R, "check", lambda: {"passed": True})
    monkeypatch.setattr(R, "environment", lambda d: {"python": "test"})
    ids = [CAT5, T72]
    out = R.run("t1", workers=2, call_fn=lambda s, u: ("{}", {"finish": "stop"}), ids=ids)
    lines = (tmp_path / "t1" / "raw.jsonl").read_text().splitlines()
    assert out["calls_made"] == len(lines) == 2 * 3 * 3
    assert R.run("t1", call_fn=lambda s, u: 1 / 0, ids=ids)["calls_made"] == 0  # resumable: nothing left

    def mismatch(s, u):
        raise SystemExit("ABORT: served model 'x' != frozen 'y'")
    with pytest.raises(SystemExit, match="ABORTED"):
        R.run("t2", workers=1, call_fn=mismatch, ids=ids)


def test_run_refuses_when_gates_fail(tmp_path, monkeypatch):
    monkeypatch.setattr(R, "RUNS", tmp_path)
    monkeypatch.setattr(R, "check", lambda: {"passed": False})
    with pytest.raises(SystemExit, match="gates failed"):
        R.run("t3", call_fn=lambda s, u: ("{}", {}), ids=[CAT5])


def test_cli_run_requires_explicit_paid_run_approval():
    with pytest.raises(SystemExit, match="approve"):
        R.main(["run", "--run-id", "x"])


# ---------------------------------------------------------------------------
# Primary metric definitions
# ---------------------------------------------------------------------------

def test_missed_change_undefined_when_gold_affected_set_is_empty():
    sc = _sc("cat1_relchange_nonprop_001")
    assert not any(g.in_affected_set for g in sc.ground_truth.nodes.values())
    assert R.primary(sc, {"over_flip_rate": 0.0, "affected_node_recall": 1.0})["missed_change"] is None
    assert R.worst_case(sc)["missed_change"] is None
    sc2 = _sc("cat1_edit_attribute_irrelevance_001")
    assert R.primary(sc2, {"over_flip_rate": 0.5, "affected_node_recall": 0.25}) == \
        {"over_flip": 0.5, "missed_change": 0.75}


def test_pooled_value_accuracy_weights_types_by_n():
    by_type = {"discrete": {"n": 2, "exact_match": 0.5},
               "continuous_bounded": {"n": 6, "within_tolerance": 1.0},
               "signed_continuous": {"n": 2, "sign_match": 0.0}}
    assert R.pooled_hits(by_type) == pytest.approx((1 + 6 + 0) / 10)
    assert R.pooled_hits("N/A") is None


# ---------------------------------------------------------------------------
# Statistics
# ---------------------------------------------------------------------------

def test_bootstrap_constant_differences():
    zero = S.paired_mean_difference([0.0] * 10)
    assert zero["ci"] == (0.0, 0.0) and zero["p"] == 1.0 and zero["degenerate"]
    neg = S.paired_mean_difference([-1.0] * 10)
    assert neg["ci"] == (-1.0, -1.0) and neg["p"] == 0.0
    assert S.paired_mean_difference([0.3])["ci"] is None


def test_bootstrap_is_seeded_and_close_to_normal_theory():
    rng = random.Random(1)
    x = [rng.gauss(0.2, 1.0) for _ in range(400)]
    a, b = S.paired_mean_difference(x), S.paired_mean_difference(x)
    assert a == b
    se = statistics.stdev(x) / len(x) ** 0.5
    m = statistics.mean(x)
    assert a["ci"][0] == pytest.approx(m - 1.96 * se, abs=0.02)
    assert a["ci"][1] == pytest.approx(m + 1.96 * se, abs=0.02)


def test_holm_matches_hand_computation():
    out = S.holm({"a": 0.01, "b": 0.04, "c": 0.03})
    assert out["a"]["p_holm"] == pytest.approx(0.03)
    assert out["c"]["p_holm"] == pytest.approx(0.06)
    assert out["b"]["p_holm"] == pytest.approx(0.06)
    assert [out[k]["reject"] for k in "acb"] == [True, False, False]
    assert S.holm({"x": None})["x"]["reject"] is False


def test_pooled_rate_skips_zero_denominator_resamples():
    res = S.pooled_rate([1, 0], [1, 0])
    assert res["estimate"] == 1.0 and res["skipped_resamples"] > 0
    assert S.pooled_rate([0, 0], [0, 0])["ci"] is None


# ---------------------------------------------------------------------------
# Decision rules on synthetic score rows
# ---------------------------------------------------------------------------

def _row(sid, cat, sub, cond, rep, primary, status="ok"):
    return {"scenario": sid, "category": cat, "subcategory": sub, "condition": cond, "repeat": rep,
            "status": status, "primary": primary if status == "ok" else None,
            "primary_worst_case": None if status == "ok" else primary}


def _h1_rows(b5, other):
    rows = []
    for i in range(22):
        for rep in range(3):
            rows.append(_row(f"s{i}", 1 + i % 4, None, "LLM_B5", rep, {"over_flip": b5, "missed_change": b5}))
            for c in ("B1", "B2"):
                rows.append(_row(f"s{i}", 1 + i % 4, None, c, rep, {"over_flip": other, "missed_change": other}))
    return rows


def test_h1_supported_only_when_all_four_comparisons_favour_b5():
    assert A.h1(_h1_rows(0.0, 1.0), "primary")["verdict"] == "SUPPORTED"
    assert A.h1(_h1_rows(0.0, 0.0), "primary")["verdict"] == "NOT SUPPORTED"  # floor: not testable
    assert A.h1(_h1_rows(1.0, 0.0), "primary")["verdict"] == "NOT SUPPORTED"


def _h2_rows(diff_6b):
    rows = []
    groups = [(5, None, 12), (6, "C6-A", 9), (6, "C6-B", 4)]
    k = 0
    for cat, sub, n in groups:
        for _ in range(n):
            for rep in range(3):
                b5 = 0.8 + (diff_6b if sub == "C6-B" else 0.0)
                rows.append(_row(f"t{k}", cat, sub, "LLM_B5", rep, {"value_accuracy": b5}))
                rows.append(_row(f"t{k}", cat, sub, "LLM_B4b", rep, {"value_accuracy": 0.8}))
            k += 1
    return rows


def test_h2_weak_category_cannot_be_concealed_by_the_aggregate():
    assert A.h2(_h2_rows(0.0), "primary")["verdict"] == "SUPPORTED"
    res = A.h2(_h2_rows(-0.1), "primary")
    assert res["tests"]["Aggregate (Cat 5–6)"]["non_inferior"]  # aggregate alone would pass
    assert res["verdict"] == "NOT SUPPORTED"


def _h3_rows(b5_fc, b5_fa, other_fc=1.0):
    rows = []
    for i in range(16):
        amb, det = (2, 2) if i < 11 else (0, 3)
        for rep in range(3):
            rows.append(_row(f"u{i}", 7, None, "LLM_B5", rep, {"n_ambiguous": amb, "n_determinable": det,
                             "false_confident": b5_fc * amb, "false_abstained": b5_fa[i] * det}))
            for c in ("B1", "B2", "LLM_B4b"):
                rows.append(_row(f"u{i}", 7, None, c, rep, {"n_ambiguous": amb, "n_determinable": det,
                                 "false_confident": other_fc * amb, "false_abstained": 0.0}))
    return rows


def test_h3_false_abstention_threshold_pass_fail_inconclusive():
    assert A.h3(_h3_rows(0.0, [0.0] * 16), "primary")["verdict"] == "SUPPORTED"
    assert A.h3(_h3_rows(0.0, [1.0] * 16), "primary")["verdict"] == "NOT SUPPORTED"
    mixed = [1.0 if i in (0, 5, 12) else 0.0 for i in range(16)]  # point ≈ 0.2, wide CI
    res = A.h3(_h3_rows(0.0, mixed), "primary")
    assert res["false_abstention_B5"]["threshold"].startswith("INCONCLUSIVE")
    assert res["verdict"].startswith("INCONCLUSIVE")
    assert A.h3(_h3_rows(0.0, [0.0] * 16, other_fc=0.0), "primary")["verdict"] == "NOT SUPPORTED"


def test_failure_rules_infrastructure_excluded_shared_failures_identical():
    rows = _h2_rows(0.0)
    for r in rows:
        if r["scenario"] == "t0" and r["condition"] in ("LLM_B5", "LLM_B4b"):
            r.update(status="invalid_extraction", primary=None, primary_worst_case={"value_accuracy": 0.0})
        if r["scenario"] == "t1" and r["condition"] == "LLM_B5":
            r.update(status="api_error", primary=None, primary_worst_case={"value_accuracy": 0.0})
    prim = A.scenario_values(rows, "LLM_B5", "LLM_B4b", "value_accuracy", "primary")
    assert prim["t0"] == (0.0, 0.0)  # shared failure: worst case for both, never one method only
    assert "t1" not in prim  # infrastructure failure excluded pairwise
    assert "t0" not in A.scenario_values(rows, "LLM_B5", "LLM_B4b", "value_accuracy", "S1_complete_case")
    assert A.scenario_values(rows, "LLM_B5", "LLM_B4b", "value_accuracy", "S2_all_worst_case")["t1"] == \
        pytest.approx((0.0, 0.8))


def test_repeats_are_averaged_within_scenario_before_resampling():
    rows = [_row("only", 5, None, "LLM_B5", rep, {"value_accuracy": v}) for rep, v in enumerate([0.0, 0.5, 1.0])]
    rows += [_row("only", 5, None, "LLM_B4b", rep, {"value_accuracy": 0.5}) for rep in range(3)]
    v = A.scenario_values(rows, "LLM_B5", "LLM_B4b", "value_accuracy", "primary")
    assert v == {"only": (0.5, 0.5)}  # one scenario = one unit, not three
