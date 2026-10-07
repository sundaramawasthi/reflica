"""Baselines B3, B4a, B4b + evaluator smoke tests on Cat 1 floor scenarios."""

from __future__ import annotations

import pytest

from reflica_bench.adapters import StructuredAdapter_v1
from reflica_bench.baselines.b3_reachability import B3Reachability
from reflica_bench.baselines.b4a_atms import B4aClassicalATMS
from reflica_bench.baselines.b4b_weighted_csp import B4bWeightedCSP
from reflica_bench.evaluator import NA, evaluate_category_1
from reflica_bench.groundtruth import generate_ground_truth
from reflica_bench.loader import cat1_dir, iter_scenarios


BASELINES = [B3Reachability(), B4aClassicalATMS(), B4bWeightedCSP()]


@pytest.mark.parametrize("baseline", BASELINES, ids=lambda b: b.name)
def test_baseline_perfect_on_cat1_floor(baseline):
    adapter = StructuredAdapter_v1()
    for s in iter_scenarios(cat1_dir()):
        out = adapter.adapt(s, run_id=f"{baseline.name}-{s.scenario_id}")
        result = baseline.revise(out)
        gt = generate_ground_truth(s)
        metrics = evaluate_category_1(result, gt)

        # Floor correctness: no over-flipping, no unnecessary revisions.
        assert metrics.over_flip_rate in (0.0,), (
            f"{baseline.name} over-flipped on {s.scenario_id}: {metrics.over_flip_rate}"
        )
        assert metrics.unnecessary_revision_rate in (0.0,), (
            f"{baseline.name} had unnecessary revisions on {s.scenario_id}: "
            f"{metrics.unnecessary_revision_rate}"
        )
        # Scope precision must be perfect on these clean cases.
        assert metrics.affected_node_precision in (1.0,), (
            f"{baseline.name} scope precision != 1.0 on {s.scenario_id}: "
            f"{metrics.affected_node_precision}"
        )
        # Recall is 1.0 unless the ground-truth affected set is empty (edge-only ops).
        assert metrics.affected_node_recall in (1.0,), (
            f"{baseline.name} scope recall != 1.0 on {s.scenario_id}: "
            f"{metrics.affected_node_recall}"
        )
        # Final-state accuracy perfect (methods that produce outcome labels).
        assert metrics.final_state_accuracy in (1.0,), (
            f"{baseline.name} final-state accuracy != 1.0 on {s.scenario_id}: "
            f"{metrics.final_state_accuracy}"
        )


def test_b3_reports_attribute_values_as_na():
    """B3 does not compute attribute values; evaluator must honour N/A, not zero."""
    adapter = StructuredAdapter_v1()
    b3 = B3Reachability()
    s = iter_scenarios(cat1_dir())[1]  # EDIT scenario
    out = adapter.adapt(s, run_id="t")
    r = b3.revise(out)
    assert r.attribute_values is None
    assert "attribute_computation" in r.unsupported_dimensions


def test_b4b_reports_feasibility_as_empty_dict_not_none():
    """B4b supports feasibility but Cat 1 has no feasibility constraints — the
    legitimate result is {}, not None (null-vs-empty rule)."""
    adapter = StructuredAdapter_v1()
    b4b = B4bWeightedCSP()
    s = iter_scenarios(cat1_dir())[0]
    out = adapter.adapt(s, run_id="t")
    r = b4b.revise(out)
    assert r.feasibility_status == {}
    assert "abstention" in r.unsupported_dimensions


def test_evaluator_reports_na_for_unsupported():
    """When a baseline returns affected_set=None, metrics must report N/A."""
    from reflica_bench.baseline import RevisionResult
    gt = generate_ground_truth(iter_scenarios(cat1_dir())[0])
    stub = RevisionResult(affected_set=None, outcome_labels=None)
    metrics = evaluate_category_1(stub, gt)
    assert metrics.affected_node_precision == NA
    assert metrics.affected_node_recall == NA
    assert metrics.unnecessary_revision_rate == NA
    assert metrics.over_flip_rate == NA
    assert metrics.final_state_accuracy == NA
