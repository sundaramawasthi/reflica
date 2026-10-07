"""Ground-truth generator tests."""

from __future__ import annotations

import pytest

from reflica_bench.groundtruth import (
    CategoryMismatchError,
    generate_ground_truth,
    ground_truth_matches,
)
from reflica_bench.loader import cat1_dir, iter_scenarios
from reflica_bench.schema import EdgeType, Operation


def test_mechanical_ground_truth_matches_stored():
    scenarios = iter_scenarios(cat1_dir())
    assert len(scenarios) >= 4
    for s in scenarios:
        mismatches = ground_truth_matches(s)
        assert mismatches == [], f"{s.scenario_id} mismatches: {mismatches}"


def test_ground_truth_contains_only_determinable_nodes():
    for s in iter_scenarios(cat1_dir()):
        gt = generate_ground_truth(s)
        for nid, g in gt.nodes.items():
            assert g.determinability.value == "DETERMINABLE"
            assert g.outcome_label.value in {"MUST_CHANGE", "MUST_STAY_STABLE"}


def test_cat1_rejects_rule_touching_edit():
    """If the EDIT target touches an attribute that any rule reads, the
    scenario does NOT belong in Cat 1 and must be rejected."""
    s = iter_scenarios(cat1_dir())[0].model_copy(deep=True)
    # Force an EDIT on an attribute the rule system reads.
    s.canonical_input.event.operation = Operation.EDIT
    s.canonical_input.event.target_kind = s.canonical_input.event.target_kind.NODE
    s.canonical_input.event.target_id = s.canonical_input.graph.nodes[0].id
    s.canonical_input.event.attribute = "capacity"
    s.canonical_input.event.new_value = 42
    s.canonical_input.event.new_node = None
    # Add a read_attributes entry so "capacity" is now a rule-read attribute.
    s.canonical_input.rules.read_attributes.entries["supplier_A"] = ["capacity"]
    with pytest.raises(CategoryMismatchError):
        generate_ground_truth(s)


def test_cat1_rejects_propagating_edge_change():
    """A RELATIONSHIP_CHANGE that introduces a propagating edge type is Cat 2+,
    not Cat 1."""
    s = iter_scenarios(cat1_dir())[-1].model_copy(deep=True)
    assert s.canonical_input.event.operation == Operation.RELATIONSHIP_CHANGE
    assert s.canonical_input.event.edge_change is not None
    s.canonical_input.event.edge_change.new_type = EdgeType.REQUIRES
    with pytest.raises(CategoryMismatchError):
        generate_ground_truth(s)
