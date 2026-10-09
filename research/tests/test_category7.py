"""Category 7 — Ambiguity / Structural Edge Cases (abstention).

Ground truth is a determinability label per node, generated mechanically by
enumerating the consistent completions of finite choice points and by
tracking undeterminable values. B6 stays a scope-only oracle and is not
tested for determinability here.
"""

from __future__ import annotations

import pytest

from reflica_bench.adapters import StructuredAdapter_v1
from reflica_bench.baselines.b3_reachability import B3Reachability
from reflica_bench.baselines.b4a_atms import B4aClassicalATMS
from reflica_bench.baselines.b4b_weighted_csp import B4bWeightedCSP
from reflica_bench.evaluator import NA, evaluate_category_7, selective_accuracy_coverage_area
from reflica_bench.groundtruth import CategoryMismatchError, generate_ground_truth, ground_truth_matches
from reflica_bench.linter import lint_scenario
from reflica_bench.loader import cat7_dir, iter_scenarios

ADAPTER = StructuredAdapter_v1()
CODES = {"P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8a", "P8b", "P9", "P10"}


def _scenarios(sub=None):
    return [s for s in iter_scenarios(cat7_dir()) if sub is None or s.subcategory == sub]


def _by_tid(tid):
    return next(s for s in _scenarios() if s.template_id == tid)


def _pairs(b, scs):
    return [(b.revise(ADAPTER.adapt(s, run_id=f"{b.name}-{s.scenario_id}")), generate_ground_truth(s)) for s in scs]


def test_cat7_lint_round_trip_and_coverage():
    for s in _scenarios():
        lint_scenario(s)
        assert ground_truth_matches(s) == [], s.scenario_id
    amb, neg = _scenarios("ambiguous"), _scenarios("false_ambiguous")
    assert len(amb) == 11 and len(neg) == 5
    assert {c for s in amb for c in s.ground_truth.scenario.pathology_codes} == CODES
    assert {s.operation.value for s in _scenarios()} == {"ADD", "EDIT", "DELETE", "RELATIONSHIP_CHANGE"}


def test_negative_controls_are_fully_determinable():
    for s in _scenarios("false_ambiguous"):
        gt = generate_ground_truth(s)
        assert all(g.determinability.value == "DETERMINABLE" for g in gt.nodes.values()), s.scenario_id


def test_completion_insensitive_status_stays_determinable():
    """P3: coverage differs across completions, but status is PARTIAL in both."""
    g = generate_ground_truth(_by_tid("T7.3")).nodes["demand_C"]
    assert g.determinability.value == "AMBIGUOUS"
    assert g.attribute_values["status"] == "PARTIAL" and g.attribute_values["coverage"] is None


def test_p4_fixed_point_semantics():
    """Correction 1: multiple fixed points → AMBIGUOUS; unique → DETERMINABLE."""
    s = _by_tid("T7.4")
    fps = generate_ground_truth(s).scenario.fixed_point_analysis
    assert len(next(iter(fps.values()))["fixed_points"]) == 2
    # Ground the cycle: X commits only if Y does AND its own plan says so; with
    # solo_commit false the unique fixed point is (false, false).
    s2 = s.model_copy(deep=True)
    comps = s2.canonical_input.rules.satisfaction_functions.entries["computations"]
    comps[0]["machine"] = {"op": "and", "args": [{"src": "team_Y.committed", "default": False},
                                                 {"ref": "team_X.solo_commit"}]}
    s2.canonical_input.graph.node("team_X").attributes["solo_commit"] = False
    for n, v in (("team_X", False), ("team_Y", False)):
        s2.canonical_input.graph.node(n).attributes["committed"] = v
    s2.canonical_input.graph.node("launch_C").attributes.update({"ready": False, "status": "INVALID"})
    s2.subcategory = "false_ambiguous"
    gt = generate_ground_truth(s2)
    assert all(g.determinability.value == "DETERMINABLE" for g in gt.nodes.values())


def test_escalation_policy_applied():
    assert generate_ground_truth(_by_tid("T7.2")).nodes["demand_C"].outcome_label.value == "REQUIRES_REEVALUATION"
    assert generate_ground_truth(_by_tid("T7.1")).nodes["demand_C"].outcome_label.value == "UNCERTAIN"


def test_cat7_verifier_rejects_mislabelled_scenarios():
    s = _by_tid("T7.13").model_copy(deep=True)
    s.subcategory = "ambiguous"
    with pytest.raises(CategoryMismatchError):
        generate_ground_truth(s)
    s = _by_tid("T7.1").model_copy(deep=True)
    s.subcategory = "false_ambiguous"
    with pytest.raises(CategoryMismatchError):
        generate_ground_truth(s)


def test_b3_abstention_metrics_are_na():
    m = evaluate_category_7(_pairs(B3Reachability(), _scenarios()))
    assert m.false_confidence_rate == NA and m.coverage == NA


def test_b4b_detects_exactly_its_modelled_pathologies():
    m = evaluate_category_7(_pairs(B4bWeightedCSP(), _scenarios()))
    pr = m.pathology_precision_recall
    for c in ("P1", "P2", "P4", "P5", "P6"):
        assert pr[c]["recall"] == 1.0 and pr[c]["precision"] == 1.0, c
    for c in ("P3", "P7", "P8a", "P8b", "P9", "P10"):
        assert pr[c]["recall"] == 0.0, c
    assert m.false_abstention_rate == 0.0
    assert 0 < m.false_confidence_rate < 1


def test_b4a_detects_structural_pathologies_and_false_abstains_on_dormant_cycle():
    m = evaluate_category_7(_pairs(B4aClassicalATMS(), _scenarios()))
    assert m.pathology_precision_recall["P4"]["recall"] == 1.0
    assert m.pathology_precision_recall["P5"]["recall"] == 1.0
    dormant = evaluate_category_7(_pairs(B4aClassicalATMS(), [_by_tid("T7.11")]))
    assert dormant.false_abstention_rate > 0


def test_no_native_confidence_means_no_primary_risk_coverage():
    m = evaluate_category_7(_pairs(B4bWeightedCSP(), _scenarios()))
    assert m.selective_accuracy_coverage_area == NA
    assert m.selective_risk == 0.0 and 0 < m.coverage < 1


def test_selective_accuracy_coverage_area():
    perfect = [(1.0, True, True)] * 4
    area, op = selective_accuracy_coverage_area(perfect)
    assert area == NA and op == {"coverage": 1.0, "selective_risk": 0.0}  # single point
    items = [(0.9, True, True), (0.6, True, True), (0.3, False, True), (0.1, False, True)]
    area, op = selective_accuracy_coverage_area(items)
    assert op == {"coverage": 0.5, "selective_risk": 0.0}
    assert 0 < area < 1
    # Full abstention: zero coverage excluded, risk N/A.
    area, op = selective_accuracy_coverage_area([(0.0, False, True)])
    assert op["selective_risk"] == NA
