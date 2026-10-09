"""Category 5 — Partial Satisfaction + Attribute Change.

Covers: lint + round-trip, mechanical Cat 5 boundary tests (Cat 6 / Cat 7
leakage, missing PARTIAL level), ground-truth / B4b independence (direct
Python arithmetic vs CP-SAT agree), N/A (not zero) attribute metrics for
B3/B4a, binarisation, threshold-crossing vs non-crossing.
"""

from __future__ import annotations

import pytest

from reflica_bench.adapters import StructuredAdapter_v1
from reflica_bench.baselines.b3_reachability import B3Reachability
from reflica_bench.baselines.b4a_atms import B4aClassicalATMS
from reflica_bench.baselines.b4b_weighted_csp import B4bWeightedCSP
from reflica_bench.baseline import RevisionResult
from reflica_bench.evaluator import NA, evaluate_category_5, monotonicity_rate
from reflica_bench.groundtruth import CategoryMismatchError, generate_ground_truth, ground_truth_matches
from reflica_bench.linter import lint_scenario
from reflica_bench.loader import cat5_dir, iter_scenarios

ADAPTER = StructuredAdapter_v1()


def _scenarios():
    return iter_scenarios(cat5_dir())


def _by_tid(tid: str):
    return next(s for s in _scenarios() if s.template_id == tid)


def _run(baseline, sc):
    return baseline.revise(ADAPTER.adapt(sc, run_id=f"{baseline.name}-{sc.scenario_id}"))


def test_cat5_lint_and_template_coverage():
    sc = _scenarios()
    for s in sc:
        lint_scenario(s)
    assert {s.template_id for s in sc} == {
        "T5.1", "T5.2", "T5.3", "T5.4", "T5.5", "T5.6", "T5.7", "T5.8", "T5.9a", "T5.9b", "T5.9c", "T5.10"
    }
    assert {s.operation.value for s in sc} == {"ADD", "EDIT", "DELETE", "RELATIONSHIP_CHANGE"}


def test_cat5_round_trip():
    for s in _scenarios():
        assert ground_truth_matches(s) == [], s.scenario_id


def test_cat5_round_trip_detects_tampering():
    s = _by_tid("T5.1").model_copy(deep=True)
    s.ground_truth.nodes["demand_C"].attribute_values["coverage"] = 0.7
    assert ground_truth_matches(s)


def test_cat5_rejects_two_quantitative_sources():
    """Boundary test: a conclusion reading two sources is Cat 6."""
    s = _by_tid("T5.6").model_copy(deep=True)
    comps = s.canonical_input.rules.satisfaction_functions.entries["computations"]
    comps[0]["machine"] = {"op": "add", "args": [{"ref": "demand_C.own_stock"}, {"src": "supplier_A.capacity", "default": 0},
                                                  {"ref": "unrelated_U.spare"}]}
    s.canonical_input.graph.node("unrelated_U").attributes["spare"] = 0
    with pytest.raises(CategoryMismatchError, match="Cat 6"):
        generate_ground_truth(s)


def test_cat5_rejects_aggregation():
    s = _by_tid("T5.1").model_copy(deep=True)
    s.canonical_input.rules.satisfaction_functions.entries["computations"][0]["machine"] = {
        "agg": "sum", "attribute": "capacity", "empty": 0}
    with pytest.raises(CategoryMismatchError, match="Cat 6"):
        generate_ground_truth(s)


def test_cat5_rejects_unknowable_input():
    """Boundary test: a non-numeric value makes the scenario Cat 7."""
    s = _by_tid("T5.1").model_copy(deep=True)
    s.canonical_input.event.new_value = "a lot"
    with pytest.raises(CategoryMismatchError, match="Cat 7"):
        generate_ground_truth(s)


def test_cat5_rejects_binary_only_status():
    s = _by_tid("T5.1").model_copy(deep=True)
    sf = s.canonical_input.rules.satisfaction_functions.entries["status_functions"]["demand_C"]
    sf["mapping"] = [m for m in sf["mapping"] if m["label"] != "PARTIAL"]
    sf["mapping"][-1]["when"] = "otherwise"
    with pytest.raises(CategoryMismatchError, match="PARTIAL"):
        generate_ground_truth(s)


def test_cat5_rejects_inconsistent_pre_state():
    s = _by_tid("T5.1").model_copy(deep=True)
    s.canonical_input.graph.node("demand_C").attributes["coverage"] = 0.9
    with pytest.raises(CategoryMismatchError, match="disagree"):
        generate_ground_truth(s)


def test_state_change_vs_attribute_change_are_separate():
    gt_a = generate_ground_truth(_by_tid("T5.9a")).nodes["demand_C"]
    assert gt_a.outcome_label.value == "MUST_CHANGE" and gt_a.state_change is False
    gt_b = generate_ground_truth(_by_tid("T5.9b")).nodes["demand_C"]
    assert gt_b.state_change is True and gt_b.attribute_values["status"] == "INVALID"
    gt_10 = generate_ground_truth(_by_tid("T5.10")).nodes["demand_C"]
    assert gt_10.state_change is False and gt_10.attribute_values["status"] == "FULL"


def test_b4b_cpsat_matches_independent_ground_truth_on_all_cat5():
    for s in _scenarios():
        m = evaluate_category_5(_run(B4bWeightedCSP(), s), generate_ground_truth(s), s)
        for t, d in m.attribute_accuracy_by_type.items():
            score = d.get("exact_match", d.get("within_tolerance", d.get("sign_match")))
            assert score == 1.0, (s.scenario_id, t, d)
        assert m.binarisation_error_rate in (0.0, NA)
        assert m.state_change_precision == 1.0 and m.state_change_recall == 1.0, s.scenario_id
        assert m.direction_correctness in (1.0, NA)


@pytest.mark.parametrize("baseline", [B3Reachability(), B4aClassicalATMS()], ids=lambda b: b.name)
def test_b3_b4a_attribute_metrics_are_na_not_zero(baseline):
    for s in _scenarios():
        m = evaluate_category_5(_run(baseline, s), generate_ground_truth(s), s)
        assert m.attribute_accuracy_by_type == NA
        assert m.partial_satisfaction_preservation_rate == NA
        assert m.binarisation_error_rate == NA
        assert m.affected_node_recall != NA  # scope is still evaluated


def test_binarising_method_is_penalised():
    s = _by_tid("T5.9a")
    gt = generate_ground_truth(s)
    good = _run(B4bWeightedCSP(), s)
    bad = RevisionResult(
        affected_set=good.affected_set, outcome_labels=good.outcome_labels,
        attribute_values={**good.attribute_values, "demand_C": {**good.attribute_values["demand_C"], "status": "INVALID"}},
        feasibility_status={"demand_C": "INVALID"},
    )
    m = evaluate_category_5(bad, gt, s)
    assert m.binarisation_error_rate == 1.0
    assert m.partial_satisfaction_preservation_rate == 0.0


def test_scope_baselines_on_two_hop_chain():
    s = _by_tid("T5.5")
    gt = generate_ground_truth(s)
    for b in (B3Reachability(), B4aClassicalATMS(), B4bWeightedCSP()):
        m = evaluate_category_5(_run(b, s), gt, s)
        assert m.affected_node_recall == 1.0, b.name
    depth = evaluate_category_5(_run(B4bWeightedCSP(), s), gt, s).depth_stratified_attribute_accuracy
    assert set(depth) == {0, 1, 2} and all(v == 1.0 for v in depth.values())


def test_attribute_metric_types():
    s = _by_tid("T5.1")
    m = evaluate_category_5(_run(B4bWeightedCSP(), s), generate_ground_truth(s), s)
    assert {"discrete", "continuous_bounded", "continuous_unbounded_positive", "signed_continuous"} <= set(
        m.attribute_accuracy_by_type
    )


def test_monotonicity_rate():
    assert monotonicity_rate([100, 60, 40, 0], [1.0, 0.6, 0.4, 0.0]) == 1.0
    assert monotonicity_rate([0, 1, 2], [0.0, 0.5, 0.2]) == 0.5
    assert monotonicity_rate([0, 1], [0.1, None]) == NA
