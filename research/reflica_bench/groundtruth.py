"""Mechanical ground-truth generator for Category 1 floor cases.

For Category 1 (Irrelevant Change / No Propagation), ground truth is fully
determined by the structural / rule-level irrelevance of the change event:

    - Changed element: MUST_CHANGE.
    - Every other node: MUST_STAY_STABLE.
    - No node: REQUIRES_REEVALUATION.
    - No node: UNCERTAIN.
    - affected_set is the singleton containing the changed element (if it's a
      node) or empty (if it's an edge-only operation).

The generator ALSO verifies that the scenario genuinely qualifies as Cat 1 by
checking the five irrelevance criteria from the locked design:

    a. changed node has no outgoing propagating edges, OR
    b. changed node has only non-propagating outgoing edges, OR
    c. changed attribute is not in any rule's read_attributes, OR
    d. node is outside the dependency closure of every current conclusion
       (treated as: not referenced by any rule), OR
    e. relationship-change touches an edge type that carries no causal weight.

If none of these hold, the scenario does NOT belong in Cat 1 and the
generator raises CategoryMismatchError.

Later categories will plug in richer post-event rule evaluation here.
"""

from __future__ import annotations

from .schema import (
    PROPAGATING_EDGE_TYPES,
    Determinability,
    EdgeType,
    GroundTruth,
    NodeGroundTruth,
    Operation,
    OutcomeLabel,
    Scenario,
    ScenarioGroundTruth,
    TargetKind,
)


class CategoryMismatchError(ValueError):
    """Raised when a scenario claimed to be in a category does not satisfy
    the category's definitional criteria."""


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_ground_truth(scenario: Scenario) -> GroundTruth:
    """Compute ground truth mechanically for a Category 1 scenario.

    Does NOT consult the scenario's `ground_truth` field. The caller is
    responsible for comparing the result against the stored ground truth
    (round-trip test) or for using this result as the authoritative source.
    """
    if scenario.category != 1:
        raise NotImplementedError(
            f"ground-truth generator only supports Category 1 in this version "
            f"(got category {scenario.category})"
        )

    _verify_category_1(scenario)

    gt_nodes: dict[str, NodeGroundTruth] = {}

    # Pre-event nodes: all stable by default.
    pre_event_node_ids = scenario.canonical_input.graph.node_ids()
    for node_id in pre_event_node_ids:
        gt_nodes[node_id] = NodeGroundTruth(
            outcome_label=OutcomeLabel.MUST_STAY_STABLE,
            state_change=False,
            attribute_values=dict(scenario.canonical_input.graph.node(node_id).attributes),  # type: ignore[union-attr]
            in_affected_set=False,
            determinability=Determinability.DETERMINABLE,
            pathology_codes=[],
        )

    ev = scenario.canonical_input.event

    if ev.operation == Operation.ADD and ev.target_kind == TargetKind.NODE:
        new = ev.new_node
        assert new is not None, "lint should have caught this"
        gt_nodes[new.id] = NodeGroundTruth(
            outcome_label=OutcomeLabel.MUST_CHANGE,
            state_change=True,
            attribute_values=dict(new.attributes),
            in_affected_set=True,
            determinability=Determinability.DETERMINABLE,
        )

    elif ev.operation == Operation.ADD and ev.target_kind == TargetKind.EDGE:
        # No node changes. Edge-only ADD in Cat 1 means a non-propagating edge
        # between irrelevant endpoints; no node transitions.
        pass

    elif ev.operation == Operation.EDIT:
        assert ev.target_id is not None and ev.attribute is not None
        current = gt_nodes[ev.target_id]
        new_attrs = dict(current.attribute_values)
        new_attrs[ev.attribute] = ev.new_value
        gt_nodes[ev.target_id] = NodeGroundTruth(
            outcome_label=OutcomeLabel.MUST_CHANGE,
            state_change=True,
            attribute_values=new_attrs,
            in_affected_set=True,
            determinability=Determinability.DETERMINABLE,
        )

    elif ev.operation == Operation.DELETE and ev.target_kind == TargetKind.NODE:
        assert ev.target_id is not None
        # Per Cat 1 design: changed element = MUST_CHANGE and in affected_set.
        # The deleted node keeps a ground-truth entry so the "affected set is
        # singleton {changed element}" invariant is directly checkable.
        current = gt_nodes.get(ev.target_id)
        gt_nodes[ev.target_id] = NodeGroundTruth(
            outcome_label=OutcomeLabel.MUST_CHANGE,
            state_change=True,
            attribute_values=dict(current.attribute_values) if current else {},
            in_affected_set=True,
            determinability=Determinability.DETERMINABLE,
        )

    elif ev.operation == Operation.DELETE and ev.target_kind == TargetKind.EDGE:
        # Edge-only delete in Cat 1 touches a non-propagating edge. No node changes.
        pass

    elif ev.operation == Operation.RELATIONSHIP_CHANGE:
        # Non-propagating edge retyped (or similar). No node changes expected
        # under Cat 1 construction.
        pass

    else:
        raise CategoryMismatchError(
            f"unsupported Cat 1 operation combo: {ev.operation} / {ev.target_kind}"
        )

    return GroundTruth(scenario=ScenarioGroundTruth(), nodes=gt_nodes)


# ---------------------------------------------------------------------------
# Category 1 verification
# ---------------------------------------------------------------------------

def _verify_category_1(scenario: Scenario) -> None:
    """Confirm the scenario really belongs in Cat 1.

    Checks irrelevance criteria (a)-(e). At least one must hold for the
    changed element.
    """
    ev = scenario.canonical_input.event
    graph = scenario.canonical_input.graph
    read_attrs: dict[str, list[str]] = (
        scenario.canonical_input.rules.read_attributes.entries  # type: ignore[assignment]
        if isinstance(scenario.canonical_input.rules.read_attributes.entries, dict)
        else {}
    )

    def node_has_propagating_outgoing(node_id: str) -> bool:
        return any(
            e.source == node_id and e.type in PROPAGATING_EDGE_TYPES
            for e in graph.edges
        )

    def attribute_is_read_anywhere(attr: str) -> bool:
        for _node, attrs in read_attrs.items():
            if attr in attrs:
                return True
        return False

    def node_referenced_by_any_rule(node_id: str) -> bool:
        return node_id in read_attrs and len(read_attrs[node_id]) > 0

    if ev.operation == Operation.ADD and ev.target_kind == TargetKind.NODE:
        # (a) new node has no outgoing propagating edges, trivially true (no edges yet).
        # (d) new node not yet referenced by any rule, trivially true.
        return

    if ev.operation == Operation.ADD and ev.target_kind == TargetKind.EDGE:
        # (b or e): the new edge must be non-propagating.
        new_type = ev.edge_change.new_type if ev.edge_change else None
        if new_type in PROPAGATING_EDGE_TYPES:
            raise CategoryMismatchError(
                f"Cat 1 edge ADD must be a non-propagating edge type, got {new_type}"
            )
        return

    if ev.operation == Operation.EDIT:
        assert ev.target_id is not None and ev.attribute is not None
        # (c) attribute edited is not referenced by any rule
        if attribute_is_read_anywhere(ev.attribute):
            # Still allowed if the specific node's attributes are not read by any rule
            # using this node — but that's a stricter check. For the floor we require
            # that no rule reads this attribute anywhere; otherwise it belongs in a
            # later category.
            raise CategoryMismatchError(
                f"Cat 1 EDIT must edit an attribute not read by any rule; "
                f"'{ev.attribute}' appears in rules.read_attributes"
            )
        # Also (a or b): node has no outgoing propagating edges relevant to any rule.
        if node_has_propagating_outgoing(ev.target_id) and node_referenced_by_any_rule(
            ev.target_id
        ):
            raise CategoryMismatchError(
                f"Cat 1 EDIT target '{ev.target_id}' has propagating outgoing edges "
                f"AND is referenced by rules; this is Cat 2, not Cat 1"
            )
        return

    if ev.operation == Operation.DELETE and ev.target_kind == TargetKind.NODE:
        assert ev.target_id is not None
        # (d) node is not referenced by any rule's premise set, i.e. not a
        # justification for any conclusion. In this minimal rule system that
        # means not in read_attrs.
        if node_referenced_by_any_rule(ev.target_id):
            raise CategoryMismatchError(
                f"Cat 1 DELETE target '{ev.target_id}' is referenced by a rule; "
                f"deletion would propagate — this is Cat 2+ or Cat 7, not Cat 1"
            )
        # (a) node must not have propagating outgoing edges to referenced nodes.
        for e in graph.edges:
            if (
                e.source == ev.target_id
                and e.type in PROPAGATING_EDGE_TYPES
                and node_referenced_by_any_rule(e.target)
            ):
                raise CategoryMismatchError(
                    f"Cat 1 DELETE target '{ev.target_id}' has a propagating edge "
                    f"to a rule-referenced node '{e.target}'"
                )
        return

    if ev.operation == Operation.DELETE and ev.target_kind == TargetKind.EDGE:
        assert ev.target_id is not None
        edge = graph.edge(ev.target_id)
        assert edge is not None
        # (e) the edge must be non-propagating.
        if edge.is_propagating:
            raise CategoryMismatchError(
                f"Cat 1 edge DELETE must be a non-propagating edge; "
                f"edge {ev.target_id} is of type {edge.type}"
            )
        return

    if ev.operation == Operation.RELATIONSHIP_CHANGE:
        assert ev.edge_change is not None and ev.edge_change.edge_id is not None
        edge = graph.edge(ev.edge_change.edge_id)
        assert edge is not None
        old_type = edge.type
        new_type = ev.edge_change.new_type
        # (e) neither old nor new type is propagating-with-rule-effect in Cat 1.
        if old_type in PROPAGATING_EDGE_TYPES or (
            new_type is not None and new_type in PROPAGATING_EDGE_TYPES
        ):
            # Edge touches a propagating relationship — this belongs in Cat 2+
            # or Cat 7, not Cat 1.
            raise CategoryMismatchError(
                f"Cat 1 RELATIONSHIP_CHANGE must stay within non-propagating edge "
                f"types; got old={old_type}, new={new_type}"
            )
        return

    raise CategoryMismatchError(
        f"unsupported Cat 1 operation combination: {ev.operation}/{ev.target_kind}"
    )


# ---------------------------------------------------------------------------
# Round-trip verification
# ---------------------------------------------------------------------------

def ground_truth_matches(scenario: Scenario) -> list[str]:
    """Return a list of mismatch messages between the scenario's stored
    ground_truth and the mechanically generated one. Empty list == match.

    This is the round-trip check: a scenario file must never contain a hand-
    typed ground truth that disagrees with the generator.
    """
    computed = generate_ground_truth(scenario)
    stored = scenario.ground_truth
    mismatches: list[str] = []

    if set(stored.nodes.keys()) != set(computed.nodes.keys()):
        mismatches.append(
            f"node-id set mismatch: stored={sorted(stored.nodes)}, "
            f"computed={sorted(computed.nodes)}"
        )
        return mismatches

    for node_id, cgt in computed.nodes.items():
        sgt = stored.nodes[node_id]
        if sgt.outcome_label != cgt.outcome_label:
            mismatches.append(
                f"{node_id}: outcome_label stored={sgt.outcome_label} vs "
                f"computed={cgt.outcome_label}"
            )
        if sgt.in_affected_set != cgt.in_affected_set:
            mismatches.append(
                f"{node_id}: in_affected_set stored={sgt.in_affected_set} vs "
                f"computed={cgt.in_affected_set}"
            )
        if sgt.state_change != cgt.state_change:
            mismatches.append(
                f"{node_id}: state_change stored={sgt.state_change} vs "
                f"computed={cgt.state_change}"
            )
        if sgt.attribute_values != cgt.attribute_values:
            mismatches.append(
                f"{node_id}: attribute_values stored={sgt.attribute_values} vs "
                f"computed={cgt.attribute_values}"
            )

    return mismatches
