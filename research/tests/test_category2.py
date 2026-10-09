"""Category 2 — Direct Dependency / Single Hop.

Covers: ground-truth round-trip, scope-level behaviour of all three
deterministic baselines, Cat-2-specific metrics (inertia, attribute-value
accuracy, N/A honoured for B3/B4a), and distinction from Cat 3.
"""

from __future__ import annotations

import pytest

from reflica_bench.adapters import StructuredAdapter_v1
from reflica_bench.baselines.b3_reachability import B3Reachability
from reflica_bench.baselines.b4a_atms import B4aClassicalATMS
from reflica_bench.baselines.b4b_weighted_csp import B4bWeightedCSP
from reflica_bench.evaluator import NA, evaluate_category_2
from reflica_bench.groundtruth import (
    CategoryMismatchError,
    generate_ground_truth,
    ground_truth_matches,
)
from reflica_bench.linter import lint_scenario
from reflica_bench.loader import cat2_dir, iter_scenarios


BASELINES = [B3Reachability(), B4aClassicalATMS(), B4bWeightedCSP()]


def _scenarios():
    return iter_scenarios(cat2_dir())


# --- schema + linter --------------------------------------------------------


def test_all_cat2_scenarios_lint_clean():
    s = _scenarios()
    assert len(s) == 6
    for sc in s:
        lint_scenario(sc)


# --- ground truth round-trip ------------------------------------------------


def test_cat2_mechanical_ground_truth_matches_stored():
    for sc in _scenarios():
        mismatches = ground_truth_matches(sc)
        assert mismatches == [], f"{sc.scenario_id} mismatches: {mismatches}"


def test_cat2_rejects_depth_2_scenario():
    """A rule whose from_node is itself the to_node of another firing rule
    is Cat 3, not Cat 2 — generator must raise."""
    pair_edit = next(s for s in _scenarios() if s.scenario_id == "cat2_pair_edit_001")
    sc = pair_edit.model_copy(deep=True)
    # The pair-edit scenario has one edge supplier_A --supports--> task_T.
    # Fabricate a second rule turning task_T into a source for a new target
    # that would ALSO change under this event — pure depth-2 cascade.
    sc.canonical_input.graph.nodes.append(
        sc.canonical_input.graph.nodes[0].model_copy(
            update={"id": "task_D", "attributes": {"available_capacity": 100}}
        )
    )
    sc.canonical_input.graph.edges.append(
        sc.canonical_input.graph.edges[0].model_copy(
            update={"edge_id": "E2", "source": "task_T", "target": "task_D"}
        )
    )
    rules_entries = sc.canonical_input.rules.propagation_rules.entries
    rules_entries["rules"].append(
        {
            "from_node": "task_T",
            "from_attribute": "available_capacity",
            "to_node": "task_D",
            "to_attribute": "available_capacity",
            "machine": {"operator": "copy",
                        "inputs": [{"node": "task_T", "attribute": "available_capacity"}],
                        "output_name": "available_capacity"},
            "human": "depth-2",
        }
    )
    with pytest.raises(CategoryMismatchError):
        generate_ground_truth(sc)


# --- baseline behaviour -----------------------------------------------------


@pytest.mark.parametrize("baseline", BASELINES, ids=lambda b: b.name)
def test_baseline_scope_perfect_on_cat2(baseline):
    adapter = StructuredAdapter_v1()
    for sc in _scenarios():
        out = adapter.adapt(sc, run_id=f"{baseline.name}-{sc.scenario_id}")
        result = baseline.revise(out)
        gt = generate_ground_truth(sc)
        metrics = evaluate_category_2(result, gt)

        assert metrics.affected_node_precision in (1.0,), (
            f"{baseline.name} scope precision != 1.0 on {sc.scenario_id}: "
            f"{metrics.affected_node_precision}"
        )
        assert metrics.affected_node_recall in (1.0,), (
            f"{baseline.name} scope recall != 1.0 on {sc.scenario_id}: "
            f"{metrics.affected_node_recall}"
        )
        assert metrics.over_flip_rate in (0.0,), (
            f"{baseline.name} over-flipped on {sc.scenario_id}: {metrics.over_flip_rate}"
        )
        assert metrics.inertia_rate in (0.0,), (
            f"{baseline.name} inertia on {sc.scenario_id}: {metrics.inertia_rate}"
        )


def test_b4b_attribute_values_match_ground_truth():
    """B4b is the reference attribute-computing baseline. Must achieve
    1.0 attribute-value accuracy on every Cat 2 floor scenario."""
    adapter = StructuredAdapter_v1()
    b4b = B4bWeightedCSP()
    for sc in _scenarios():
        out = adapter.adapt(sc, run_id=f"b4b-{sc.scenario_id}")
        result = b4b.revise(out)
        gt = generate_ground_truth(sc)
        metrics = evaluate_category_2(result, gt)
        assert metrics.attribute_value_accuracy == 1.0, (
            f"B4b attribute-value accuracy {metrics.attribute_value_accuracy} "
            f"!= 1.0 on {sc.scenario_id}"
        )


def test_b3_and_b4a_report_attribute_accuracy_as_na():
    """B3 and B4a do not compute attribute values; the metric must be N/A,
    never 0 (null-vs-empty rule)."""
    adapter = StructuredAdapter_v1()
    for baseline in (B3Reachability(), B4aClassicalATMS()):
        for sc in _scenarios():
            out = adapter.adapt(sc, run_id=f"{baseline.name}-{sc.scenario_id}")
            r = baseline.revise(out)
            assert r.attribute_values is None
            metrics = evaluate_category_2(r, generate_ground_truth(sc))
            assert metrics.attribute_value_accuracy == NA, (
                f"{baseline.name} attribute_value_accuracy must be N/A on {sc.scenario_id}"
            )


def test_cat2_has_at_least_one_scenario_per_operation():
    ops = {sc.operation.value for sc in _scenarios()}
    assert ops == {"ADD", "EDIT", "DELETE", "RELATIONSHIP_CHANGE"}, ops
