"""Category 6 — Capacity-Constrained Alternatives (C6-A aggregation, C6-B
combination selection). Metrics are per subfamily, never pooled."""

from __future__ import annotations

import pytest

from reflica_bench.adapters import StructuredAdapter_v1
from reflica_bench.baselines.b3_reachability import B3Reachability
from reflica_bench.baselines.b4a_atms import B4aClassicalATMS
from reflica_bench.baselines.b4b_weighted_csp import B4bWeightedCSP
from reflica_bench.evaluator import NA, evaluate_category_6a, evaluate_category_6b
from reflica_bench.groundtruth import CategoryMismatchError, generate_ground_truth, ground_truth_matches
from reflica_bench.linter import lint_scenario
from reflica_bench.loader import cat6_dir, iter_scenarios

ADAPTER = StructuredAdapter_v1()


def _scenarios(sub=None):
    return [s for s in iter_scenarios(cat6_dir()) if sub is None or s.subcategory == sub]


def _by_tid(tid: str, sub="C6-A"):
    return next(s for s in _scenarios(sub) if s.template_id == tid)


def _run(b, s):
    return b.revise(ADAPTER.adapt(s, run_id=f"{b.name}-{s.scenario_id}"))


def test_cat6_lint_round_trip_and_coverage():
    for s in _scenarios():
        lint_scenario(s)
        assert ground_truth_matches(s) == [], s.scenario_id
    a, b = _scenarios("C6-A"), _scenarios("C6-B")
    assert {s.template_id for s in a} == {"T6.1", "T6.2", "T6.3", "T6.4", "T6.5", "T6.8", "T6.9", "T6.10", "T6.11"}
    assert {s.template_id for s in b} == {"T6.6", "T6.7"}
    assert {s.operation.value for s in a} == {s.operation.value for s in b} == {
        "ADD", "EDIT", "DELETE", "RELATIONSHIP_CHANGE"}


def test_cat6a_rejects_single_source_sufficiency():
    """Correction 2: if any one source satisfies the full conjunction, not Cat 6."""
    s = _by_tid("T6.1").model_copy(deep=True)
    s.canonical_input.graph.node("S1").attributes["capacity"] = 100
    s.canonical_input.graph.node("demand_C").attributes.update(
        {"total": 170, "coverage": 1.7, "excess": 70})
    with pytest.raises(CategoryMismatchError, match="alone"):
        generate_ground_truth(s)


def test_cat6b_rejects_tied_optimum_as_cat7():
    s = _by_tid("T6.7", "C6-B").model_copy(deep=True)
    s.canonical_input.event.new_value = 8000  # {S1,S2} and {S1,S3} both cost 17000
    with pytest.raises(CategoryMismatchError, match="P10"):
        generate_ground_truth(s)


def test_cat6b_rejects_single_feasible_source():
    s = _by_tid("T6.6", "C6-B").model_copy(deep=True)
    s.canonical_input.graph.node("S1").attributes["capacity"] = 120
    s.canonical_input.graph.node("demand_C").attributes["feasible_count"] = 3  # {S1},{S1,S2},{S1,S3}
    with pytest.raises(CategoryMismatchError, match="single source"):
        generate_ground_truth(s)


def test_cat6_requires_subcategory():
    s = _by_tid("T6.2").model_copy(deep=True)
    s.subcategory = None
    with pytest.raises(CategoryMismatchError):
        generate_ground_truth(s)


def test_compensation_ground_truth():
    assert generate_ground_truth(_by_tid("T6.5")).scenario.compensation_viable is True
    assert generate_ground_truth(_by_tid("T6.1")).scenario.compensation_viable is False
    assert generate_ground_truth(_by_tid("T6.3")).scenario.compensation_viable is None


def test_b4b_cpsat_perfect_on_c6a():
    for s in _scenarios("C6-A"):
        m = evaluate_category_6a(_run(B4bWeightedCSP(), s), generate_ground_truth(s), s)
        assert m.feasibility_classification_accuracy == 1.0, s.scenario_id
        for block in (m.aggregate_value_accuracy, m.shortfall_excess_accuracy):
            for d in block.values():
                assert d.get("within_tolerance", d.get("sign_match")) == 1.0, (s.scenario_id, d)
        assert m.compensation_reasoning_accuracy in (1.0, NA)
        assert m.affected_node_recall == 1.0


def test_b4b_cpsat_perfect_on_c6b():
    for s in _scenarios("C6-B"):
        m = evaluate_category_6b(_run(B4bWeightedCSP(), s), generate_ground_truth(s), s)
        assert m.feasible_combination_recall == m.feasible_combination_precision == 1.0, s.scenario_id
        assert m.optimal_combination_accuracy in (1.0, NA)
        assert m.compensation_reasoning_accuracy in (1.0, NA)
        assert isinstance(m.combinatorial_search_cost, int)


def test_c6b_optimum_shift():
    s = _by_tid("T6.7", "C6-B")
    r = _run(B4bWeightedCSP(), s)
    assert r.attribute_values["demand_C"]["selected"] == ["S1", "S2"]


@pytest.mark.parametrize("baseline", [B3Reachability(), B4aClassicalATMS()], ids=lambda b: b.name)
def test_b3_b4a_unsupported_on_aggregation(baseline):
    for s in _scenarios():
        r, gt = _run(baseline, s), generate_ground_truth(s)
        if s.subcategory == "C6-A":
            m = evaluate_category_6a(r, gt, s)
            assert m.aggregate_value_accuracy == NA and m.feasibility_classification_accuracy == NA
        else:
            m = evaluate_category_6b(r, gt, s)
            assert m.feasible_combination_recall == NA and m.combinatorial_search_cost == NA
        assert m.affected_node_precision != NA


def test_b4a_scope_follows_nested_and_shared_aggregates():
    for tid in ("T6.10", "T6.11", "T6.8"):
        s = _by_tid(tid)
        m = evaluate_category_6a(_run(B4aClassicalATMS(), s), generate_ground_truth(s), s)
        assert m.affected_node_recall == 1.0, tid
