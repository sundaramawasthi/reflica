"""B4a — Classical ATMS-style baseline (Cat 1 floor).

For Cat 1 scenarios no node has justifications touched by the event, so this
baseline flags only the event-target node (if it's a node) as changed and
leaves everything else stable. Attribute computation is unsupported.

This stub is correct for Cat 1 and will be expanded for Cat 4 (justification
preservation) when scenarios actually carry justifications.
"""

from __future__ import annotations

from ..adapters import AdapterOutput
from ..baseline import Baseline, RevisionResult, Timer
from ..schema import (
    Operation,
    OutcomeLabel,
    TargetKind,
)


class B4aClassicalATMS:
    name: str = "B4a_classical_atms"
    version: str = "1.0.0"
    supports_scope_detection: bool = True
    supports_attribute_computation: bool = False
    supports_feasibility_classification: bool = False
    supports_abstention: bool = False  # consistency/cycle detection added later

    def revise(self, adapter_output: AdapterOutput) -> RevisionResult:
        with Timer() as t:
            if adapter_output.structured is None:
                return RevisionResult(
                    unsupported_dimensions=["all"], wall_time_ms=t.elapsed_ms
                )
            mi = adapter_output.structured
            graph = mi.graph
            ev = mi.event

            affected: set[str] = set()
            outcome: dict[str, OutcomeLabel] = {}

            # In Cat 1 no justifications are touched; the only node whose state
            # legitimately changes is the direct event target.
            if ev.operation == Operation.ADD and ev.target_kind == TargetKind.NODE:
                assert ev.new_node is not None
                affected.add(ev.new_node.id)
            elif ev.operation == Operation.EDIT:
                assert ev.target_id is not None
                affected.add(ev.target_id)
            elif ev.operation == Operation.DELETE and ev.target_kind == TargetKind.NODE:
                assert ev.target_id is not None
                # Deleted node is "changed" in the sense of being removed; we
                # include it in the affected set for comparison with ground truth
                # (though ground truth drops it after the event).
                affected.add(ev.target_id)
            # Edge-only operations touch no justifications → affected set empty.

            # The changed element (including a deleted node) stays in the
            # universe of reported nodes so the "affected set = singleton
            # {changed element}" invariant is directly comparable against
            # ground truth.
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
                attribute_values=None,
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
