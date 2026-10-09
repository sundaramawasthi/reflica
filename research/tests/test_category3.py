"""Category 3 — Multi-hop Propagation.

Covers: ground-truth round-trip, baseline scope behaviour including the
expected B3/B4a over-flip on early-termination, B4b correctness,
depth-stratified metrics, Cat 3 rejection of depth-1-only and cyclic
scenarios.
"""

from __future__ import annotations

import pytest

from reflica_bench.adapters import StructuredAdapter_v1
from reflica_bench.baselines.b3_reachability import B3Reachability
from reflica_bench.baselines.b4a_atms import B4aClassicalATMS
from reflica_bench.baselines.b4b_weighted_csp import B4bWeightedCSP
from reflica_bench.evaluator import NA, evaluate_category_3
from reflica_bench.groundtruth import (
    CategoryMismatchError,
    generate_ground_truth,
    ground_truth_matches,
)
from reflica_bench.linter import lint_scenario
from reflica_bench.loader import cat3_dir, iter_scenarios


BASELINES = [B3Reachability(), B4aClassicalATMS(), B4bWeightedCSP()]


def _scenarios():
    return iter_scenarios(cat3_dir())


def _by_id(sid: str):
    return next(s for s in _scenarios() if s.scenario_id == sid)


# --- schema + lint ----------------------------------------------------------


def test_all_cat3_scenarios_lint_clean():
    s = _scenarios()
    assert len(s) >= 6
    for sc in s:
        lint_scenario(sc)


def test_cat3_covers_all_four_operations():
    ops = {sc.operation.value for sc in _scenarios()}
    assert ops == {"ADD", "EDIT", "DELETE", "RELATIONSHIP_CHANGE"}, ops


# --- ground truth round-trip ------------------------------------------------


def test_cat3_mechanical_ground_truth_matches_stored():
    for sc in _scenarios():
        mismatches = ground_truth_matches(sc)
        assert mismatches == [], f"{sc.scenario_id} mismatches: {mismatches}"


def test_cat3_rejects_depth_1_only_scenario():
    """A scenario whose rules do not produce any depth-≥-2 cascade must be
    rejected as Cat 2 in disguise."""
    sc = _by_id("cat3_linear_chain_edit_001").model_copy(deep=True)
    # Drop N2→N3 and N1→N2 rules to collapse to depth-1 only.
    rules_entries = sc.canonical_input.rules.propagation_rules.entries
    rules_entries["rules"] = [rules_entries["rules"][0]]
    with pytest.raises(CategoryMismatchError):
        generate_ground_truth(sc)


def test_cat3_rejects_cyclic_rule_system():
    """Cycles belong in Cat 7, not Cat 3."""
    sc = _by_id("cat3_linear_chain_edit_001").model_copy(deep=True)
    rules_entries = sc.canonical_input.rules.propagation_rules.entries
    # Add a back-edge from N3 to N1 to create a cycle.
    rules_entries["rules"].append(
        {
            "from_node": "node_N3",
            "from_attribute": "mirror",
            "to_node": "node_N1",
            "to_attribute": "mirror",
            "machine": {"operator": "copy",
                        "inputs": [{"node": "node_N3", "attribute": "mirror"}],
                        "output_name": "mirror"},
            "human": "cycle",
        }
    )
    sc.canonical_input.graph.edges.append(
        sc.canonical_input.graph.edges[0].model_copy(
            update={"edge_id": "E_cycle", "source": "node_N3", "target": "node_N1", "type": "supports"}
        )
    )
    with pytest.raises(CategoryMismatchError):
        generate_ground_truth(sc)


# --- baseline behaviour -----------------------------------------------------


def test_b4b_perfect_on_all_cat3_scenarios():
    """B4b iterates the rule network to a fixed point; it must match ground
    truth on scope, termination, inertia, over-flip, and attribute values."""
    adapter = StructuredAdapter_v1()
    b4b = B4bWeightedCSP()
    for sc in _scenarios():
        out = adapter.adapt(sc, run_id=f"b4b-{sc.scenario_id}")
        result = b4b.revise(out)
        gt = generate_ground_truth(sc)
        m = evaluate_category_3(result, gt, sc.canonical_input.graph, sc.canonical_input.event)
        assert m.affected_node_precision == 1.0, (sc.scenario_id, m.affected_node_precision)
        assert m.affected_node_recall == 1.0, (sc.scenario_id, m.affected_node_recall)
        assert m.over_flip_rate == 0.0, (sc.scenario_id, m.over_flip_rate)
        assert m.inertia_rate == 0.0, (sc.scenario_id, m.inertia_rate)
        assert m.attribute_value_accuracy == 1.0, (sc.scenario_id, m.attribute_value_accuracy)
        assert m.termination_accuracy == 1.0, (sc.scenario_id, m.termination_accuracy)


def test_b3_over_flips_on_early_termination():
    """The design predicts B3 over-flips past the termination point of the
    T3.4 early-termination scenario because reachability doesn't check
    whether the propagated rule output actually changes."""
    adapter = StructuredAdapter_v1()
    b3 = B3Reachability()
    sc = _by_id("cat3_early_termination_edit_001")
    out = adapter.adapt(sc, run_id="b3-term")
    result = b3.revise(out)
    gt = generate_ground_truth(sc)
    m = evaluate_category_3(result, gt, sc.canonical_input.graph, sc.canonical_input.event)
    # B3 flags N2 and N3 as affected despite ground truth saying stable.
    assert m.over_flip_rate > 0.0, m.over_flip_rate
    # Termination accuracy should drop below 1.0 — B3 crosses the boundary.
    assert m.termination_accuracy != 1.0 and m.termination_accuracy != NA, m.termination_accuracy


def test_b4a_over_flips_on_early_termination():
    """ATMS cascading justification invalidation also crosses the
    termination boundary (treats 'touched' as 'invalid' without checking
    whether rule output actually changed)."""
    adapter = StructuredAdapter_v1()
    b4a = B4aClassicalATMS()
    sc = _by_id("cat3_early_termination_edit_001")
    out = adapter.adapt(sc, run_id="b4a-term")
    result = b4a.revise(out)
    gt = generate_ground_truth(sc)
    m = evaluate_category_3(result, gt, sc.canonical_input.graph, sc.canonical_input.event)
    assert m.over_flip_rate > 0.0, m.over_flip_rate
    assert m.termination_accuracy != 1.0 and m.termination_accuracy != NA, m.termination_accuracy


def test_b4b_stops_at_early_termination():
    """B4b iterates rule outputs and discovers rule-insensitivity, so it
    should stop at the correct depth on T3.4."""
    adapter = StructuredAdapter_v1()
    b4b = B4bWeightedCSP()
    sc = _by_id("cat3_early_termination_edit_001")
    out = adapter.adapt(sc, run_id="b4b-term")
    result = b4b.revise(out)
    gt = generate_ground_truth(sc)
    m = evaluate_category_3(result, gt, sc.canonical_input.graph, sc.canonical_input.event)
    assert m.termination_accuracy == 1.0, m.termination_accuracy
    assert m.over_flip_rate == 0.0, m.over_flip_rate


def test_b3_does_not_propagate_through_informs():
    """Chain + irrelevant side-branches scenario: informs edges must not
    pull side_Y / side_Z into the affected set, even for the reachability
    baseline (B3 is edge-type-filtered)."""
    adapter = StructuredAdapter_v1()
    b3 = B3Reachability()
    sc = _by_id("cat3_chain_plus_side_edit_001")
    out = adapter.adapt(sc, run_id="b3-side")
    result = b3.revise(out)
    assert result.affected_set is not None
    assert "side_Y" not in result.affected_set
    assert "side_Z" not in result.affected_set


def test_b3_and_b4a_report_attribute_accuracy_as_na_on_cat3():
    adapter = StructuredAdapter_v1()
    for baseline in (B3Reachability(), B4aClassicalATMS()):
        for sc in _scenarios():
            out = adapter.adapt(sc, run_id=f"{baseline.name}-{sc.scenario_id}")
            r = baseline.revise(out)
            assert r.attribute_values is None
            m = evaluate_category_3(r, generate_ground_truth(sc), sc.canonical_input.graph, sc.canonical_input.event)
            assert m.attribute_value_accuracy == NA
