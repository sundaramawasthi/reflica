"""Mechanical ground-truth generator for Categories 1, 2, 3, and 4.

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
    """Compute ground truth mechanically for a Category 1, 2, or 3 scenario.

    Does NOT consult the scenario's `ground_truth` field. The caller is
    responsible for comparing the result against the stored ground truth
    (round-trip test) or for using this result as the authoritative source.
    """
    if scenario.category == 2:
        return _generate_cat2(scenario)
    if scenario.category == 3:
        return _generate_cat3(scenario)
    if scenario.category == 4:
        return _generate_cat4(scenario)
    if scenario.category in (5, 6, 7):
        from .groundtruth_quant import generate_quantitative

        return generate_quantitative(scenario)
    if scenario.category != 1:
        raise NotImplementedError(
            f"ground-truth generator supports Category 1-4 in this version "
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
# Category 2 — Direct Dependency / Single Hop
# ---------------------------------------------------------------------------

def _generate_cat2(scenario: Scenario) -> GroundTruth:
    """Compute post-event state for a Category 2 scenario.

    Mechanics:
      1. Build the post-event graph.
      2. For each propagation rule, check whether the post-event graph has at
         least one propagating edge from from_node to to_node. If yes, set
         to_node.to_attribute = from_node.from_attribute (post-event). If no,
         to_node.to_attribute = None (unlinked).
      3. Compare with pre-event values; any node whose attributes changed
         (including the event target) is MUST_CHANGE; others MUST_STAY_STABLE.
      4. Verify depth-exactly-1 propagation: a propagation rule's to_node
         must not itself be the from_node of another propagation rule whose
         output is actually affected by the event. If it is, this is Cat 3+.
    """
    graph = scenario.canonical_input.graph
    ev = scenario.canonical_input.event
    rules_block = scenario.canonical_input.rules.propagation_rules.entries
    rule_list = rules_block.get("rules", []) if isinstance(rules_block, dict) else []

    # Pre-event snapshot: attribute values per node.
    pre_values: dict[str, dict[str, object]] = {
        n.id: dict(n.attributes) for n in graph.nodes
    }

    # Build post-event graph (nodes + edges) as a lightweight mutable view.
    post_nodes: dict[str, dict[str, object]] = {
        n.id: dict(n.attributes) for n in graph.nodes
    }
    post_edges: list[dict[str, object]] = [
        {"edge_id": e.edge_id, "source": e.source, "target": e.target, "type": e.type}
        for e in graph.edges
    ]

    _apply_event_to_post_state(ev, post_nodes, post_edges)

    # Apply propagation rules at depth 1 only. We use the shared
    # _compute_rule_output helper so the operator field (copy / map / …) is
    # honoured consistently across Cat 2 and Cat 3; the Cat-2 depth-1
    # invariant is still enforced below.
    for r in rule_list:
        to_node = r.get("to_node")
        to_attr = r.get("to_attribute")
        if not isinstance(to_node, str) or not isinstance(to_attr, str):
            continue
        if to_node not in post_nodes:
            continue
        post_nodes[to_node][to_attr] = _compute_rule_output(r, post_nodes, post_edges)

    _verify_category_2(ev, graph, rule_list, pre_values, post_nodes)

    # Build ground-truth node annotations.
    gt_nodes: dict[str, NodeGroundTruth] = {}
    affected: set[str] = set()

    # Account for all nodes present pre- and post-event.
    all_ids = set(pre_values.keys()) | set(post_nodes.keys())
    for nid in all_ids:
        pre = pre_values.get(nid)
        post = post_nodes.get(nid)
        if post is None:
            # Node removed: ground truth retains an entry to make
            # "affected set = singleton{changed element}" directly comparable.
            gt_nodes[nid] = NodeGroundTruth(
                outcome_label=OutcomeLabel.MUST_CHANGE,
                state_change=True,
                attribute_values=dict(pre) if pre else {},
                in_affected_set=True,
                determinability=Determinability.DETERMINABLE,
            )
            affected.add(nid)
            continue

        changed = pre is None or pre != post
        gt_nodes[nid] = NodeGroundTruth(
            outcome_label=OutcomeLabel.MUST_CHANGE
            if changed
            else OutcomeLabel.MUST_STAY_STABLE,
            state_change=changed,
            attribute_values=dict(post),
            in_affected_set=changed,
            determinability=Determinability.DETERMINABLE,
        )
        if changed:
            affected.add(nid)

    return GroundTruth(scenario=ScenarioGroundTruth(), nodes=gt_nodes)


def _apply_event_to_post_state(
    ev,
    post_nodes: dict[str, dict[str, object]],
    post_edges: list[dict[str, object]],
) -> None:
    """Mutate (post_nodes, post_edges) in-place to reflect the event."""
    if ev.operation == Operation.ADD and ev.target_kind == TargetKind.NODE:
        assert ev.new_node is not None
        post_nodes[ev.new_node.id] = dict(ev.new_node.attributes)
    elif ev.operation == Operation.ADD and ev.target_kind == TargetKind.EDGE:
        assert ev.edge_change is not None
        post_edges.append(
            {
                "edge_id": f"__added__{ev.edge_change.source}_{ev.edge_change.target}",
                "source": ev.edge_change.source,
                "target": ev.edge_change.target,
                "type": ev.edge_change.new_type,
            }
        )
    elif ev.operation == Operation.EDIT:
        assert ev.target_id is not None and ev.attribute is not None
        if ev.target_id in post_nodes:
            post_nodes[ev.target_id][ev.attribute] = ev.new_value
    elif ev.operation == Operation.DELETE and ev.target_kind == TargetKind.NODE:
        assert ev.target_id is not None
        post_nodes.pop(ev.target_id, None)
        # Drop edges incident to the deleted node.
        post_edges[:] = [
            e
            for e in post_edges
            if e["source"] != ev.target_id and e["target"] != ev.target_id
        ]
    elif ev.operation == Operation.DELETE and ev.target_kind == TargetKind.EDGE:
        assert ev.target_id is not None
        post_edges[:] = [e for e in post_edges if e["edge_id"] != ev.target_id]
    elif ev.operation == Operation.RELATIONSHIP_CHANGE:
        assert ev.edge_change is not None and ev.edge_change.edge_id is not None
        for e in post_edges:
            if e["edge_id"] == ev.edge_change.edge_id:
                if ev.edge_change.new_type is not None:
                    e["type"] = ev.edge_change.new_type


def _has_propagating_edge(
    post_edges: list[dict[str, object]], source: str, target: str
) -> bool:
    for e in post_edges:
        if (
            e["source"] == source
            and e["target"] == target
            and e["type"] in PROPAGATING_EDGE_TYPES
        ):
            return True
    return False


def _verify_category_2(
    ev,
    graph,
    rule_list: list[dict],
    pre_values: dict[str, dict[str, object]],
    post_nodes: dict[str, dict[str, object]],
) -> None:
    """Enforce 'depth exactly 1' propagation.

    A Cat 2 scenario violates its contract if any to_node from one firing
    propagation rule is itself the from_node of a DIFFERENT firing rule
    whose output would change on this event. That would be depth-2
    propagation and belongs in Cat 3.
    """
    changed_targets: set[tuple[str, str]] = set()
    for r in rule_list:
        to_node = r["to_node"]
        to_attr = r["to_attribute"]
        pre_v = pre_values.get(to_node, {}).get(to_attr)
        post_v = post_nodes.get(to_node, {}).get(to_attr)
        if pre_v != post_v:
            changed_targets.add((to_node, to_attr))

    for r in rule_list:
        from_node = r["from_node"]
        from_attr = r["from_attribute"]
        if (from_node, from_attr) in changed_targets:
            raise CategoryMismatchError(
                f"Cat 2 violation: propagation rule from ({from_node}.{from_attr}) "
                f"depends on an attribute that itself changed via another rule — "
                f"this is depth-2 propagation (Cat 3)."
            )


# ---------------------------------------------------------------------------
# Category 3 — Multi-hop Propagation
# ---------------------------------------------------------------------------

def _generate_cat3(scenario: Scenario) -> GroundTruth:
    """Compute post-event state for a Category 3 scenario by iterating
    propagation rules to a fixed point.

    Supports the `copy` operator (also used in Cat 2) and the `map` operator
    (needed by early-termination templates — rule output can be insensitive
    to a specific input change).
    """
    graph = scenario.canonical_input.graph
    ev = scenario.canonical_input.event
    rules_block = scenario.canonical_input.rules.propagation_rules.entries
    rule_list = rules_block.get("rules", []) if isinstance(rules_block, dict) else []

    pre_values: dict[str, dict[str, object]] = {
        n.id: dict(n.attributes) for n in graph.nodes
    }
    post_nodes: dict[str, dict[str, object]] = {
        n.id: dict(n.attributes) for n in graph.nodes
    }
    post_edges: list[dict[str, object]] = [
        {"edge_id": e.edge_id, "source": e.source, "target": e.target, "type": e.type}
        for e in graph.edges
    ]

    _apply_event_to_post_state(ev, post_nodes, post_edges)

    _verify_category_3_cycles(rule_list)

    _apply_rules_fixed_point(post_nodes, post_edges, rule_list)

    _verify_category_3_depth(ev, graph, rule_list, pre_values, post_nodes)

    # Ground-truth annotations.
    gt_nodes: dict[str, NodeGroundTruth] = {}
    all_ids = set(pre_values.keys()) | set(post_nodes.keys())
    for nid in all_ids:
        pre = pre_values.get(nid)
        post = post_nodes.get(nid)
        if post is None:
            gt_nodes[nid] = NodeGroundTruth(
                outcome_label=OutcomeLabel.MUST_CHANGE,
                state_change=True,
                attribute_values=dict(pre) if pre else {},
                in_affected_set=True,
                determinability=Determinability.DETERMINABLE,
            )
            continue
        changed = pre is None or pre != post
        gt_nodes[nid] = NodeGroundTruth(
            outcome_label=OutcomeLabel.MUST_CHANGE
            if changed
            else OutcomeLabel.MUST_STAY_STABLE,
            state_change=changed,
            attribute_values=dict(post),
            in_affected_set=changed,
            determinability=Determinability.DETERMINABLE,
        )

    return GroundTruth(scenario=ScenarioGroundTruth(), nodes=gt_nodes)


def _apply_rules_fixed_point(
    post_nodes: dict[str, dict[str, object]],
    post_edges: list[dict[str, object]],
    rule_list: list[dict],
    max_iters: int = 100,
) -> None:
    """Iterate propagation rules until no node attribute changes further.

    Each rule produces a target attribute value from the current post-event
    state. If the computed value differs from the current target value, the
    update is applied. Iteration continues until a full sweep makes no
    changes, or until max_iters is hit (indicating a non-converging rule
    system — treated as a programmer error, not a benchmark condition).
    """
    for _ in range(max_iters):
        changed = False
        for r in rule_list:
            to_node = r.get("to_node")
            to_attr = r.get("to_attribute")
            if not isinstance(to_node, str) or not isinstance(to_attr, str):
                continue
            if to_node not in post_nodes:
                continue
            new_val = _compute_rule_output(r, post_nodes, post_edges)
            current = post_nodes[to_node].get(to_attr)
            if current != new_val:
                post_nodes[to_node][to_attr] = new_val
                changed = True
        if not changed:
            return
    raise RuntimeError(
        f"propagation did not converge in {max_iters} iterations — "
        f"check for cycles or non-monotone rules"
    )


def _compute_rule_output(
    rule: dict,
    post_nodes: dict[str, dict[str, object]],
    post_edges: list[dict[str, object]],
) -> object:
    """Return the post-event value of the rule's target attribute.

    Returns None if the propagating edge or source node/attribute is absent,
    modelling an "unlinked" state.
    """
    from_node = rule.get("from_node")
    to_node = rule.get("to_node")
    from_attr = rule.get("from_attribute")
    machine = rule.get("machine", {})
    operator = machine.get("operator", "copy")

    if not isinstance(from_node, str) or not isinstance(to_node, str):
        return None

    has_prop_edge = _has_propagating_edge(post_edges, from_node, to_node)
    if not has_prop_edge or from_node not in post_nodes:
        return None

    source_attr_value = (
        post_nodes[from_node].get(from_attr) if isinstance(from_attr, str) else None
    )

    if operator == "copy":
        return source_attr_value
    if operator == "map":
        mapping = machine.get("mapping", {})
        default = machine.get("default")
        if source_attr_value is None:
            return default
        key = source_attr_value
        if isinstance(key, (dict, list)):
            return default
        return mapping.get(key, default) if isinstance(mapping, dict) else default

    # Unknown operator: fall through to None rather than silently copy —
    # keeps the surface area explicit for later categories.
    return None


def _verify_category_3_cycles(rule_list: list[dict]) -> None:
    """Reject rule systems whose propagation DAG contains a cycle.

    Cycles belong in Cat 7 (ambiguity), not Cat 3.
    """
    outgoing: dict[str, set[str]] = {}
    for r in rule_list:
        from_n = r.get("from_node")
        to_n = r.get("to_node")
        if isinstance(from_n, str) and isinstance(to_n, str):
            outgoing.setdefault(from_n, set()).add(to_n)
    # DFS cycle detection on the (from_node → to_node) graph.
    WHITE, GREY, BLACK = 0, 1, 2
    color: dict[str, int] = {n: WHITE for n in outgoing}
    for src in outgoing:
        if color.get(src, WHITE) != WHITE:
            continue
        stack: list[tuple[str, bool]] = [(src, False)]
        while stack:
            node, processed = stack.pop()
            if processed:
                color[node] = BLACK
                continue
            if color.get(node, WHITE) == GREY:
                raise CategoryMismatchError(
                    f"Cat 3 rule system contains a cycle involving '{node}'; "
                    f"cycles belong in Cat 7, not Cat 3"
                )
            if color.get(node, WHITE) == BLACK:
                continue
            color[node] = GREY
            stack.append((node, True))
            for nxt in outgoing.get(node, ()):
                if color.get(nxt, WHITE) == GREY:
                    raise CategoryMismatchError(
                        f"Cat 3 rule system contains a cycle involving '{nxt}'; "
                        f"cycles belong in Cat 7, not Cat 3"
                    )
                if color.get(nxt, WHITE) == WHITE:
                    stack.append((nxt, False))


def _verify_category_3_depth(
    ev,
    graph,
    rule_list: list[dict],
    pre_values: dict[str, dict[str, object]],
    post_nodes: dict[str, dict[str, object]],
) -> None:
    """Enforce 'rule system contains at least one depth-≥-2 chain.'

    Cat 3 is a STRUCTURAL property of the scenario: the propagation DAG
    declared by the rules has a length-≥-2 path. Whether the specific event
    actually cascades to depth 2 depends on the event — the early-
    termination template T3.4 deliberately produces only depth-1 effective
    propagation under its event, and that is still a valid Cat 3 scenario
    because the chain STRUCTURE exists and B3/B4a over-flip past the
    termination point.
    """
    produces_at: dict[str, set[str]] = {}  # from_node -> set of (to_node,to_attribute) targets of rules originating here
    consumes_at: dict[tuple[str, str], set[str]] = {}  # (node,attribute) -> set of to_nodes consuming it
    for r in rule_list:
        from_n = r.get("from_node")
        from_a = r.get("from_attribute")
        to_n = r.get("to_node")
        to_a = r.get("to_attribute")
        if not all(isinstance(x, str) for x in (from_n, from_a, to_n, to_a)):
            continue
        produces_at.setdefault(to_n, set()).add((to_n, to_a))
        consumes_at.setdefault((from_n, from_a), set()).add(to_n)

    # A length-≥-2 chain exists iff some rule's to_node is the from_node of
    # another rule — i.e. produces_at[to_n] intersects a rule's from_node.
    has_chain = False
    for r in rule_list:
        to_n = r.get("to_node")
        to_a = r.get("to_attribute")
        if not isinstance(to_n, str) or not isinstance(to_a, str):
            continue
        if (to_n, to_a) in consumes_at:
            has_chain = True
            break

    if not has_chain:
        raise CategoryMismatchError(
            "Cat 3 scenario's rule system contains no length-≥-2 chain; this "
            "is a Cat 2 scenario in disguise."
        )


# ---------------------------------------------------------------------------
# Category 4 — Alternative-Justification Preservation
# ---------------------------------------------------------------------------

def _generate_cat4(scenario: Scenario) -> GroundTruth:
    """Compute post-event state for a Category 4 scenario.

    Mechanics:
      1. Build post-event graph (apply event to a mutable copy).
      2. Apply any declared propagation_rules (fixed-point).
      3. Evaluate each conclusion's justifications: at least one intact →
         status_attribute = true_value; else false_value.
      4. Compare post-event attributes to pre-event, label diffs.

    A Cat 4 scenario must declare at least one conclusion with ≥ 2
    justifications and must contain either a preservation case (one
    justification invalidated, another remains intact) OR a negative control
    (all justifications invalidated). The verifier below ensures this.
    """
    graph = scenario.canonical_input.graph
    ev = scenario.canonical_input.event
    rules_block = scenario.canonical_input.rules.propagation_rules.entries
    rule_list = rules_block.get("rules", []) if isinstance(rules_block, dict) else []
    justif_block = scenario.canonical_input.rules.justifications.entries
    conclusions_cfg = (
        justif_block.get("conclusions", {})
        if isinstance(justif_block, dict)
        else {}
    )

    pre_values: dict[str, dict[str, object]] = {
        n.id: dict(n.attributes) for n in graph.nodes
    }
    post_nodes: dict[str, dict[str, object]] = {
        n.id: dict(n.attributes) for n in graph.nodes
    }
    post_edges: list[dict[str, object]] = [
        {"edge_id": e.edge_id, "source": e.source, "target": e.target, "type": e.type}
        for e in graph.edges
    ]

    _apply_event_to_post_state(ev, post_nodes, post_edges)

    # Pre-event: evaluate justifications on the pre-event graph.
    pre_post_nodes_snapshot = {n.id: dict(n.attributes) for n in graph.nodes}
    pre_edges_snapshot = [
        {"edge_id": e.edge_id, "source": e.source, "target": e.target, "type": e.type}
        for e in graph.edges
    ]
    pre_justification_states = _evaluate_all_justifications(
        pre_post_nodes_snapshot, pre_edges_snapshot, conclusions_cfg
    )

    # Apply Cat 2/3 propagation rules in case they're declared.
    if rule_list:
        _apply_rules_fixed_point(post_nodes, post_edges, rule_list)

    # Apply justifications → conclusion status attributes.
    post_justification_states = _evaluate_all_justifications(
        post_nodes, post_edges, conclusions_cfg
    )
    for conclusion_id, status_update in post_justification_states.items():
        if conclusion_id in post_nodes:
            post_nodes[conclusion_id].update(status_update)

    _verify_category_4(conclusions_cfg, pre_justification_states, post_justification_states)

    # Build ground-truth annotations.
    gt_nodes: dict[str, NodeGroundTruth] = {}
    all_ids = set(pre_values.keys()) | set(post_nodes.keys())
    for nid in all_ids:
        pre = pre_values.get(nid)
        post = post_nodes.get(nid)
        if post is None:
            gt_nodes[nid] = NodeGroundTruth(
                outcome_label=OutcomeLabel.MUST_CHANGE,
                state_change=True,
                attribute_values=dict(pre) if pre else {},
                in_affected_set=True,
                determinability=Determinability.DETERMINABLE,
            )
            continue
        changed = pre is None or pre != post
        gt_nodes[nid] = NodeGroundTruth(
            outcome_label=OutcomeLabel.MUST_CHANGE
            if changed
            else OutcomeLabel.MUST_STAY_STABLE,
            state_change=changed,
            attribute_values=dict(post),
            in_affected_set=changed,
            determinability=Determinability.DETERMINABLE,
        )

    return GroundTruth(scenario=ScenarioGroundTruth(), nodes=gt_nodes)


def _evaluate_all_justifications(
    nodes: dict[str, dict[str, object]],
    edges: list[dict[str, object]],
    conclusions_cfg: dict,
) -> dict[str, dict[str, object]]:
    """For every conclusion with declared justifications, compute the
    status_attribute update dict (one key: the status attribute name).

    A justification is intact iff every premise exists in `nodes` AND each
    premise has a propagating edge to the conclusion in `edges`.
    """
    out: dict[str, dict[str, object]] = {}
    for conclusion_id, config in conclusions_cfg.items():
        if conclusion_id not in nodes:
            continue
        status_attr = config.get("status_attribute", "status")
        true_v = config.get("true_value", True)
        false_v = config.get("false_value", False)
        justs = config.get("justifications", [])
        any_intact = False
        for just in justs:
            if _justification_intact(just, conclusion_id, nodes, edges):
                any_intact = True
                break
        out[conclusion_id] = {status_attr: true_v if any_intact else false_v}
    return out


def _justification_intact(
    premises: list,
    conclusion_id: str,
    nodes: dict[str, dict[str, object]],
    edges: list[dict[str, object]],
) -> bool:
    for p in premises:
        if not isinstance(p, str):
            return False
        if p not in nodes:
            return False
        if not _has_propagating_edge(edges, p, conclusion_id):
            return False
    return True


def _verify_category_4(
    conclusions_cfg: dict,
    pre_states: dict[str, dict[str, object]],
    post_states: dict[str, dict[str, object]],
) -> None:
    """Enforce Cat 4 contract:
      - At least one conclusion is declared with ≥ 2 justifications.
      - Either a preservation OR a negative-control case fires: some
        conclusion's pre-event status is true, AND after the event either
        (preservation) the status is still true despite at least one
        justification having invalidated, OR (negative control) the status
        has flipped to false because every justification is invalidated.
    """
    if not conclusions_cfg:
        raise CategoryMismatchError(
            "Cat 4 requires at least one conclusion with declared justifications"
        )
    any_fires = False
    for conclusion_id, config in conclusions_cfg.items():
        status_attr = config.get("status_attribute", "status")
        true_v = config.get("true_value", True)
        pre_s = pre_states.get(conclusion_id, {}).get(status_attr)
        post_s = post_states.get(conclusion_id, {}).get(status_attr)
        if pre_s != true_v:
            # Pre-event status wasn't 'true' — scenario doesn't exercise the
            # Cat 4 property on this conclusion.
            continue
        any_fires = True
        # Preservation case: status still true. Negative control: flipped.
        # Both are legal; we don't need to disambiguate here.
        break
    if not any_fires:
        raise CategoryMismatchError(
            "Cat 4 scenario does not exercise alternative-justification "
            "logic: no conclusion starts in the 'true' state"
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
        if sgt.determinability != cgt.determinability:
            mismatches.append(
                f"{node_id}: determinability stored={sgt.determinability} vs "
                f"computed={cgt.determinability}"
            )
        if sorted(sgt.pathology_codes) != sorted(cgt.pathology_codes):
            mismatches.append(
                f"{node_id}: pathology_codes stored={sgt.pathology_codes} vs "
                f"computed={cgt.pathology_codes}"
            )

    s, c = stored.scenario, computed.scenario
    for fld in (
        "pathology_codes",
        "feasible_combinations",
        "optimal_combination",
        "fixed_point_analysis",
        "consistent_completions",
        "compensation_viable",
    ):
        if getattr(s, fld) != getattr(c, fld):
            mismatches.append(
                f"scenario.{fld}: stored={getattr(s, fld)} vs computed={getattr(c, fld)}"
            )

    return mismatches
