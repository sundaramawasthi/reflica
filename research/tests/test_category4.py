"""Category 4 — Alternative-Justification Preservation.

Covers all five required distinctions from the Cat 4 brief:
  1. one justification becoming invalid while another remains valid
  2. all justifications becoming invalid (negative control)
  3. unrelated justifications remaining stable
  4. over-flipping caused by naive reachability (B3 structural failure)
  5. correct propagation through the remaining valid justification
"""

from __future__ import annotations

import pytest

from reflica_bench.adapters import StructuredAdapter_v1
from reflica_bench.baselines.b3_reachability import B3Reachability
from reflica_bench.baselines.b4a_atms import B4aClassicalATMS
from reflica_bench.baselines.b4b_weighted_csp import B4bWeightedCSP
from reflica_bench.evaluator import NA, evaluate_category_4
from reflica_bench.groundtruth import (
    CategoryMismatchError,
    generate_ground_truth,
    ground_truth_matches,
)
from reflica_bench.linter import lint_scenario
from reflica_bench.loader import cat4_dir, iter_scenarios


def _scenarios():
    return iter_scenarios(cat4_dir())


def _by_id(sid: str):
    return next(s for s in _scenarios() if s.scenario_id == sid)


def _conclusion_ids_of(sc) -> set[str]:
    """Pull declared conclusion IDs from the scenario's rules.justifications."""
    cfg = sc.canonical_input.rules.justifications.entries.get("conclusions", {})
    return set(cfg.keys())


BASELINES = [B3Reachability(), B4aClassicalATMS(), B4bWeightedCSP()]


# --- schema + lint ----------------------------------------------------------

def test_all_cat4_scenarios_lint_clean():
    sc = _scenarios()
    assert len(sc) == 5
    for s in sc:
        lint_scenario(s)


def test_cat4_covers_all_four_operations():
    ops = {s.operation.value for s in _scenarios()}
    assert ops == {"ADD", "EDIT", "DELETE", "RELATIONSHIP_CHANGE"}, ops


def test_cat4_contains_preservation_and_negative_control():
    subs = {s.subcategory for s in _scenarios()}
    assert "preservation" in subs
    assert "negative_control" in subs


# --- ground truth round-trip ------------------------------------------------

def test_cat4_mechanical_ground_truth_matches_stored():
    for s in _scenarios():
        mismatches = ground_truth_matches(s)
        assert mismatches == [], f"{s.scenario_id} mismatches: {mismatches}"


def test_cat4_rejects_single_justification_scenario():
    """Cat 4 requires ≥ 2 justifications per conclusion; linter enforces."""
    sc = _by_id("cat4_diamond_delete_preservation_001").model_copy(deep=True)
    sc.canonical_input.rules.justifications.entries["conclusions"]["conclusion_C"][
        "justifications"
    ] = [["premise_A"]]
    from reflica_bench.linter import LintError
    with pytest.raises(LintError, match="≥ 2"):
        lint_scenario(sc)


def test_cat4_rejects_scenario_whose_conclusion_never_true():
    """Verifier flags Cat 4 scenarios where no conclusion starts in the
    'true' state because the rule system cannot support it (every
    justification is unintact pre-event)."""
    sc = _by_id("cat4_diamond_delete_preservation_001").model_copy(deep=True)
    # Strip BOTH supports edges so neither justification can be intact pre-event.
    sc.canonical_input.graph.edges = []
    with pytest.raises(CategoryMismatchError):
        generate_ground_truth(sc)


# --- the headline distinction: B3 over-flips, B4a / B4b preserve -----------

def test_b3_over_flips_conclusion_on_diamond_delete_preservation():
    """Required distinction (4) + (5): naive reachability flags the
    conclusion as changed even though the alternative justification holds."""
    sc = _by_id("cat4_diamond_delete_preservation_001")
    adapter = StructuredAdapter_v1()
    r = B3Reachability().revise(adapter.adapt(sc, run_id="b3-pres"))
    gt = generate_ground_truth(sc)
    assert r.affected_set is not None
    assert "conclusion_C" in r.affected_set, (
        "B3 reachability must over-flip the conclusion on Cat 4 preservation"
    )
    m = evaluate_category_4(r, gt, _conclusion_ids_of(sc))
    assert m.false_invalidation_rate == 1.0, m.false_invalidation_rate
    assert m.discrimination_accuracy == 0.0, m.discrimination_accuracy


def test_b4a_preserves_conclusion_on_diamond_delete():
    """Required distinction (1) + (5): ATMS keeps the conclusion stable
    because the alternative justification remains intact."""
    sc = _by_id("cat4_diamond_delete_preservation_001")
    adapter = StructuredAdapter_v1()
    r = B4aClassicalATMS().revise(adapter.adapt(sc, run_id="b4a-pres"))
    gt = generate_ground_truth(sc)
    assert r.affected_set is not None
    assert "conclusion_C" not in r.affected_set
    m = evaluate_category_4(r, gt, _conclusion_ids_of(sc))
    assert m.false_invalidation_rate == 0.0
    assert m.discrimination_accuracy == 1.0
    assert m.preservation_precision == 1.0


def test_b4b_computes_status_true_on_preservation():
    """B4b must COMPUTE the status attribute and leave it at true when the
    alternative is intact — not just preserve scope."""
    sc = _by_id("cat4_diamond_delete_preservation_001")
    adapter = StructuredAdapter_v1()
    r = B4bWeightedCSP().revise(adapter.adapt(sc, run_id="b4b-pres"))
    assert r.attribute_values is not None
    assert r.attribute_values["conclusion_C"]["status"] is True


def test_b4a_correctly_flips_on_negative_control():
    """Required distinction (2): when all justifications are invalidated
    (shared-premise DELETE), B4a MUST mark the conclusion as changed."""
    sc = _by_id("cat4_shared_premise_delete_negative_001")
    adapter = StructuredAdapter_v1()
    r = B4aClassicalATMS().revise(adapter.adapt(sc, run_id="b4a-neg"))
    gt = generate_ground_truth(sc)
    assert r.affected_set is not None
    assert "conclusion_C" in r.affected_set
    m = evaluate_category_4(r, gt, _conclusion_ids_of(sc))
    assert m.discrimination_accuracy == 1.0


def test_b4b_flips_status_false_on_negative_control():
    sc = _by_id("cat4_shared_premise_delete_negative_001")
    adapter = StructuredAdapter_v1()
    r = B4bWeightedCSP().revise(adapter.adapt(sc, run_id="b4b-neg"))
    assert r.attribute_values is not None
    assert r.attribute_values["conclusion_C"]["status"] is False


def test_b4a_and_b4b_discrimination_accuracy_perfect_across_cat4():
    """Required distinction (2) + (1) across the full set: both baselines
    must correctly discriminate preservation from negative control."""
    adapter = StructuredAdapter_v1()
    for baseline in (B4aClassicalATMS(), B4bWeightedCSP()):
        for sc in _scenarios():
            r = baseline.revise(adapter.adapt(sc, run_id=f"{baseline.name}-{sc.scenario_id}"))
            gt = generate_ground_truth(sc)
            m = evaluate_category_4(r, gt, _conclusion_ids_of(sc))
            assert m.discrimination_accuracy == 1.0, (baseline.name, sc.scenario_id)


# --- (3) unrelated justifications stability --------------------------------

def test_b4a_leaves_unrelated_premises_stable():
    """Required distinction (3): on preservation scenarios the untouched
    premise and all unrelated nodes must stay out of the affected set."""
    sc = _by_id("cat4_diamond_delete_preservation_001")
    adapter = StructuredAdapter_v1()
    r = B4aClassicalATMS().revise(adapter.adapt(sc, run_id="b4a-stable"))
    assert r.affected_set is not None
    assert "premise_B" not in r.affected_set


# --- RELATIONSHIP_CHANGE path specifically ---------------------------------

def test_b4a_preserves_on_relchange_breaking_one_justification():
    sc = _by_id("cat4_relchange_breaks_one_001")
    adapter = StructuredAdapter_v1()
    r = B4aClassicalATMS().revise(adapter.adapt(sc, run_id="b4a-rc"))
    gt = generate_ground_truth(sc)
    assert "conclusion_C" not in (r.affected_set or [])
    m = evaluate_category_4(r, gt, _conclusion_ids_of(sc))
    assert m.false_invalidation_rate == 0.0


# --- B3 N/A attribute values -------------------------------------------------

def test_b3_cat4_attribute_values_na():
    adapter = StructuredAdapter_v1()
    for sc in _scenarios():
        r = B3Reachability().revise(adapter.adapt(sc, run_id=f"b3-{sc.scenario_id}"))
        assert r.attribute_values is None
