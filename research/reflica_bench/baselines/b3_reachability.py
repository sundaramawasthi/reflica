"""B3 — Reachability-only invalidation.

Scope-only baseline. From the changed element, walks the graph through
PROPAGATING edges and flags every reachable node as affected. Does not
compute attribute values or feasibility; attribute_values is None (N/A).

This is deliberately the simplest "graph-aware" baseline. In Cat 1 the
changed element has no propagating outgoing edges that reach any
rule-relevant node, so B3 should produce the correct affected set
(singleton {changed_element} for node-targeted operations, empty for
edge-only operations).
"""

from __future__ import annotations

from ..adapters import AdapterOutput
from ..baseline import Baseline, RevisionResult, Timer
from ..schema import (
    PROPAGATING_EDGE_TYPES,
    Operation,
    OutcomeLabel,
    TargetKind,
)


class B3Reachability:
    name: str = "B3_reachability"
    version: str = "1.0.0"
    supports_scope_detection: bool = True
    supports_attribute_computation: bool = False
    supports_feasibility_classification: bool = False
    supports_abstention: bool = False

    def revise(self, adapter_output: AdapterOutput) -> RevisionResult:
        with Timer() as t:
            if adapter_output.structured is None:
                return RevisionResult(
                    unsupported_dimensions=["all"],
                    wall_time_ms=t.elapsed_ms,
                )
            mi = adapter_output.structured
            graph = mi.graph
            ev = mi.event

            affected: set[str] = set()
            outcome: dict[str, OutcomeLabel] = {}

            # Seed the propagation from the changed element.
            seeds: list[str] = []
            if ev.operation == Operation.ADD and ev.target_kind == TargetKind.NODE:
                assert ev.new_node is not None
                seeds.append(ev.new_node.id)
            elif ev.operation == Operation.EDIT:
                assert ev.target_id is not None
                seeds.append(ev.target_id)
            elif ev.operation == Operation.DELETE and ev.target_kind == TargetKind.NODE:
                assert ev.target_id is not None
                seeds.append(ev.target_id)
            # Edge-only operations: B3 is edge-type filtered — it only seeds
            # from the edge's target if the touched edge is a propagating type
            # (old or new type for RELATIONSHIP_CHANGE). This is the "edge-
            # type-filtered reachability" behaviour required by the Cat 1
            # locked design. Non-propagating edges produce no seeds.
            elif (
                ev.operation == Operation.DELETE
                and ev.target_kind == TargetKind.EDGE
            ):
                e = graph.edge(ev.target_id)  # type: ignore[arg-type]
                if e is not None and e.type in PROPAGATING_EDGE_TYPES:
                    seeds.append(e.target)
            elif ev.operation == Operation.RELATIONSHIP_CHANGE:
                assert ev.edge_change is not None and ev.edge_change.edge_id is not None
                e = graph.edge(ev.edge_change.edge_id)
                new_type = ev.edge_change.new_type
                old_prop = e is not None and e.type in PROPAGATING_EDGE_TYPES
                new_prop = new_type is not None and new_type in PROPAGATING_EDGE_TYPES
                if (old_prop or new_prop) and e is not None:
                    seeds.append(e.target)
            elif ev.operation == Operation.ADD and ev.target_kind == TargetKind.EDGE:
                assert ev.edge_change is not None
                new_type = ev.edge_change.new_type
                if (
                    new_type is not None
                    and new_type in PROPAGATING_EDGE_TYPES
                    and ev.edge_change.target is not None
                ):
                    seeds.append(ev.edge_change.target)

            # BFS through propagating edges only.
            frontier = list(dict.fromkeys(seeds))
            while frontier:
                node_id = frontier.pop(0)
                if node_id in affected:
                    continue
                if node_id in graph.node_ids() or (
                    ev.operation == Operation.ADD
                    and ev.target_kind == TargetKind.NODE
                    and ev.new_node is not None
                    and ev.new_node.id == node_id
                ):
                    affected.add(node_id)
                for e in graph.edges:
                    if e.source == node_id and e.type in PROPAGATING_EDGE_TYPES:
                        if e.target not in affected:
                            frontier.append(e.target)

            # Outcome labels: affected -> MUST_CHANGE, others -> MUST_STAY_STABLE.
            # B3 doesn't actually know *what* changed; this is intentionally
            # coarse. The deleted node stays in the reported universe so the
            # "affected set = singleton {changed element}" invariant is
            # directly comparable against ground truth.
            all_nodes_in_graph = set(graph.node_ids())
            if (
                ev.operation == Operation.ADD
                and ev.target_kind == TargetKind.NODE
                and ev.new_node is not None
            ):
                all_nodes_in_graph.add(ev.new_node.id)

            for nid in all_nodes_in_graph:
                outcome[nid] = (
                    OutcomeLabel.MUST_CHANGE if nid in affected else OutcomeLabel.MUST_STAY_STABLE
                )

            return RevisionResult(
                affected_set=sorted(affected),
                outcome_labels=outcome,
                attribute_values=None,          # unsupported — N/A
                feasibility_status=None,
                determinability=None,
                pathology_flags=None,
                confidence_scores=None,
                feasible_combinations=None,
                explanation=None,
                unsupported_dimensions=[
                    "attribute_computation",
                    "feasibility_classification",
                    "abstention",
                ],
                token_cost=0,
                wall_time_ms=t.elapsed_ms,
            )
