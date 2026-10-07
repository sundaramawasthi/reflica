"""B4b — Weighted CSP + rule engine (Cat 1 floor).

Cat 1 scenarios declare no aggregation functions, no satisfaction functions,
and no numeric constraints. For these scenarios a weighted-CSP solve is a
no-op: the rule system has no constraints that mention the changed element,
so the solver produces exactly the same assignment as pre-event.

This baseline is scaffolded here with ortools imported but not actually
invoked on Cat 1 inputs. From Cat 5/6 onward it will build and solve a
CP-SAT model from the declared constraints.
"""

from __future__ import annotations

try:  # pragma: no cover - import test only
    from ortools.sat.python import cp_model  # noqa: F401
    _ORTOOLS_AVAILABLE = True
except ImportError:  # pragma: no cover
    _ORTOOLS_AVAILABLE = False

from ..adapters import AdapterOutput
from ..baseline import Baseline, RevisionResult, Timer
from ..schema import (
    Operation,
    OutcomeLabel,
    TargetKind,
)


class B4bWeightedCSP:
    name: str = "B4b_weighted_csp_ortools"
    version: str = "1.0.0"
    supports_scope_detection: bool = True
    supports_attribute_computation: bool = True   # declared capability; Cat 5/6 exercises it
    supports_feasibility_classification: bool = True
    supports_abstention: bool = False             # UNSAT-only abstention added later

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
            attribute_values: dict[str, dict[str, object]] = {}

            # Cat 1 has no declared aggregation or satisfaction functions, so
            # the "solve" is: only the event target's own attributes change;
            # all other node attribute values are preserved exactly.
            if ev.operation == Operation.ADD and ev.target_kind == TargetKind.NODE:
                assert ev.new_node is not None
                affected.add(ev.new_node.id)
                attribute_values[ev.new_node.id] = dict(ev.new_node.attributes)
            elif ev.operation == Operation.EDIT:
                assert ev.target_id is not None and ev.attribute is not None
                affected.add(ev.target_id)
                src_attrs = dict(graph.node(ev.target_id).attributes)  # type: ignore[union-attr]
                src_attrs[ev.attribute] = ev.new_value
                attribute_values[ev.target_id] = src_attrs
            elif ev.operation == Operation.DELETE and ev.target_kind == TargetKind.NODE:
                assert ev.target_id is not None
                affected.add(ev.target_id)
            # Edge-only ops change no node attributes.

            # Carry pre-event attribute values through for all unchanged nodes.
            # The deleted node stays in the reported universe so the affected-
            # set invariant is comparable; its attribute_values preserve the
            # pre-event snapshot (no new values are computed for a deleted node).
            all_nodes_in_graph = set(graph.node_ids())
            if (
                ev.operation == Operation.ADD
                and ev.target_kind == TargetKind.NODE
                and ev.new_node is not None
            ):
                all_nodes_in_graph.add(ev.new_node.id)

            for nid in all_nodes_in_graph:
                if nid not in attribute_values:
                    node = graph.node(nid)
                    if node is not None:
                        attribute_values[nid] = dict(node.attributes)
                outcome[nid] = (
                    OutcomeLabel.MUST_CHANGE if nid in affected else OutcomeLabel.MUST_STAY_STABLE
                )

            return RevisionResult(
                affected_set=sorted(affected),
                outcome_labels=outcome,
                attribute_values=attribute_values,
                feasibility_status={},               # supported, legitimately empty on Cat 1
                determinability=None,                # abstention not supported here
                pathology_flags=None,
                confidence_scores=None,
                feasible_combinations=None,
                explanation=None,
                unsupported_dimensions=["abstention"],
                token_cost=0,
                wall_time_ms=t.elapsed_ms,
            )
