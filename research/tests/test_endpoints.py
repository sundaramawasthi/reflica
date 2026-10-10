"""Protocol endpoints must equal the evaluator's own node-level quantities."""

from __future__ import annotations

import pytest

from reflica_bench import rn
from reflica_bench.adapters import StructuredAdapter_v1
from reflica_bench.b5.reflica import B5Reflica
from reflica_bench.baseline import RevisionResult
from reflica_bench.baselines.b3_reachability import B3Reachability
from reflica_bench.baselines.b4a_atms import B4aClassicalATMS
from reflica_bench.endpoints import node_counts
from reflica_bench.evaluator import NA, evaluate_category_7
from reflica_bench.loader import load_scenario

pytest.importorskip("ortools")
from reflica_bench.baselines.b4b_weighted_csp import B4bWeightedCSP  # noqa: E402

METHODS = (B3Reachability, B4aClassicalATMS, B4bWeightedCSP, B5Reflica)
SCENARIOS = [load_scenario(p) for p in rn.canonical_files()]


def _gold(sc, cls):
    return cls().revise(StructuredAdapter_v1().adapt(sc, "gold"))


@pytest.mark.parametrize("cls", METHODS, ids=lambda c: c.__name__)
def test_counts_partition_nodes_and_match_evaluator_category_7(cls):
    for sc in SCENARIOS:
        gt = sc.ground_truth
        r = _gold(sc, cls)
        c = node_counts(r, gt)
        assert c.correct + c.false_confident + c.false_abstained + c.committed_wrong == c.nodes
        assert c.nodes == c.ambiguous + c.determinable == len(gt.nodes)
        m = evaluate_category_7([(r, gt)])
        if m.false_confidence_rate == NA:
            continue  # method reports no determinability; evaluator gives N/A
        n = c.nodes
        assert m.determinability_accuracy * n == pytest.approx(n - c.false_confident - c.false_abstained)
        if c.ambiguous:
            assert m.false_confidence_rate * c.ambiguous == pytest.approx(c.false_confident)
        if c.determinable:
            assert m.false_abstention_rate * c.determinable == pytest.approx(c.false_abstained)
        committed_det = c.determinable - c.false_abstained
        if committed_det and m.selective_risk != NA:
            assert m.selective_risk * committed_det == pytest.approx(c.committed_wrong)


def test_b5_on_gold_input_is_fully_correct():
    """Regression: B5 v0.1.0 agrees with gold on all 63 (B5_REPORT §5)."""
    for sc in SCENARIOS:
        assert node_counts(_gold(sc, B5Reflica), sc.ground_truth).primary == 1.0, sc.scenario_id


def test_failed_output_handles_no_node_correctly():
    sc = next(s for s in SCENARIOS if s.category == 7 and any(
        g.determinability.value == "AMBIGUOUS" for g in s.ground_truth.nodes.values()))
    c = node_counts(None, sc.ground_truth)
    assert c.failed_output and c.correct == 0 and c.primary == 0.0
    assert c.false_confident == c.ambiguous and c.committed_wrong == c.determinable
    assert c.missing_prediction == c.nodes


def test_missing_node_prediction_is_committed_and_wrong():
    sc = SCENARIOS[0]
    full = _gold(sc, B5Reflica)
    drop = next(iter(sc.ground_truth.nodes))
    partial = RevisionResult(
        outcome_labels={k: v for k, v in full.outcome_labels.items() if k != drop},
        attribute_values={k: v for k, v in (full.attribute_values or {}).items() if k != drop},
        determinability={k: v for k, v in full.determinability.items() if k != drop},
    )
    c = node_counts(partial, sc.ground_truth)
    assert c.missing_prediction == 1 and c.correct == c.nodes - 1
