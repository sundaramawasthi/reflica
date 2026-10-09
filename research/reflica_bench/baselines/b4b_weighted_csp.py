"""B4b — Weighted CSP + rule engine (Cat 1 floor + Cat 2 single hop).

Cat 1: no declared aggregation or satisfaction functions, so the "solve" is
a no-op; the baseline simply mirrors the pre-event attribute values.

Cat 2: the rule system declares propagation_rules — single-hop declarative
mappings `(from_node, from_attribute) -> (to_node, to_attribute)` mediated
by a propagating edge. For each rule the baseline checks whether the
post-event graph has at least one propagating edge between from_node and
to_node, and if so copies the source's post-event attribute into the
target's attribute slot. If the propagating edge no longer exists (DELETE
of edge, DELETE of source node, or RELATIONSHIP_CHANGE propagating →
non-propagating), the target's attribute becomes None, modelling an
"unlinked" state.

Cats 5/6/7: satisfaction functions and combination problems are solved by
an OR-Tools CP-SAT model (b4b_cpsat.py), independent of the ground-truth
engine. Abstention is partial: B4b flags outputs it cannot model (missing /
non-numeric input), UNSAT conflicts and multi-solution cycles, and commits
everywhere else.
"""

from __future__ import annotations

try:  # pragma: no cover - import test only
    from ortools.sat.python import cp_model  # noqa: F401
    _ORTOOLS_AVAILABLE = True
except ImportError:  # pragma: no cover
    _ORTOOLS_AVAILABLE = False

from ..adapters import AdapterOutput
from ..baseline import Baseline, RevisionResult, Timer
from ._event import resolve_target
from .b4b_cpsat import solve_combination, solve_computations
from ..schema import (
    PROPAGATING_EDGE_TYPES,
    Operation,
    OutcomeLabel,
    TargetKind,
)


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


def _compute_rule_output(
    rule: dict,
    post_nodes: dict[str, dict[str, object]],
    post_edges: list[dict[str, object]],
) -> object:
    """Mirror of groundtruth._compute_rule_output; kept independent so a
    future divergence (B4b → CP-SAT, ground truth → direct Python arithmetic)
    is a one-sided change."""
    from_node = rule.get("from_node")
    to_node = rule.get("to_node")
    from_attr = rule.get("from_attribute")
    machine = rule.get("machine", {})
    operator = machine.get("operator", "copy")
    if not isinstance(from_node, str) or not isinstance(to_node, str):
        return None
    if not _has_propagating_edge(post_edges, from_node, to_node):
        return None
    if from_node not in post_nodes:
        return None
    src_val = (
        post_nodes[from_node].get(from_attr) if isinstance(from_attr, str) else None
    )
    if operator == "copy":
        return src_val
    if operator == "map":
        mapping = machine.get("mapping", {})
        default = machine.get("default")
        if src_val is None:
            return default
        if isinstance(src_val, (dict, list)):
            return default
        return mapping.get(src_val, default) if isinstance(mapping, dict) else default
    return None


def _apply_rules_fixed_point(
    post_nodes: dict[str, dict[str, object]],
    post_edges: list[dict[str, object]],
    rule_list: list[dict],
    max_iters: int = 100,
) -> None:
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
        f"B4b propagation did not converge in {max_iters} iterations"
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

            outcome: dict[str, OutcomeLabel] = {}

            # Start from the pre-event attribute snapshot.
            post_nodes: dict[str, dict[str, object]] = {
                n.id: dict(n.attributes) for n in graph.nodes
            }
            # Mutable edge list in post-event form.
            post_edges: list[dict[str, object]] = [
                {
                    "edge_id": e.edge_id,
                    "source": e.source,
                    "target": e.target,
                    "type": e.type,
                }
                for e in graph.edges
            ]

            # Apply the event to post state.
            if ev.operation == Operation.ADD and ev.target_kind == TargetKind.NODE:
                assert ev.new_node is not None
                post_nodes[ev.new_node.id] = dict(ev.new_node.attributes)
            elif ev.operation == Operation.ADD and ev.target_kind == TargetKind.EDGE:
                assert ev.edge_change is not None
                if ev.edge_change.new_type is not None:
                    post_edges.append(
                        {
                            "edge_id": f"__added__{ev.edge_change.source}_{ev.edge_change.target}",
                            "source": ev.edge_change.source,
                            "target": ev.edge_change.target,
                            "type": ev.edge_change.new_type,
                        }
                    )
            elif ev.operation == Operation.EDIT:
                target = resolve_target(graph, ev)
                if target in post_nodes and ev.attribute is not None:
                    post_nodes[target][ev.attribute] = ev.new_value
            elif ev.operation == Operation.DELETE and ev.target_kind == TargetKind.NODE:
                assert ev.target_id is not None
                post_nodes.pop(ev.target_id, None)
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
                    if e["edge_id"] == ev.edge_change.edge_id and ev.edge_change.new_type is not None:
                        e["type"] = ev.edge_change.new_type

            # Apply declared propagation rules (Cat 2 and later). Cat 1
            # scenarios declare an empty rule list, so this is a no-op.
            # From Cat 3 on this is a FIXED-POINT iteration so multi-hop
            # cascades converge.
            rules_block = mi.rules.get("propagation_rules")
            rule_list: list[dict] = []
            if isinstance(rules_block, dict):
                entries = rules_block.get("entries", {})
                if isinstance(entries, dict):
                    cand = entries.get("rules", [])
                    if isinstance(cand, list):
                        rule_list = cand

            _apply_rules_fixed_point(post_nodes, post_edges, rule_list)

            # Cat 4: evaluate alternative justifications and update each
            # declared conclusion's status attribute. OR across
            # justifications, AND within each (every premise must exist
            # and have a propagating edge to the conclusion). Independent
            # from ATMS: this path computes the status value whereas B4a
            # only flags scope.
            justif_block = mi.rules.get("justifications")
            if isinstance(justif_block, dict):
                conclusions_cfg = justif_block.get("entries", {}).get("conclusions", {}) or {}
                for conclusion_id, config in conclusions_cfg.items():
                    if conclusion_id not in post_nodes:
                        continue
                    status_attr = config.get("status_attribute", "status")
                    true_v = config.get("true_value", True)
                    false_v = config.get("false_value", False)
                    justs = config.get("justifications", [])
                    any_intact = False
                    for just in justs:
                        all_present = all(
                            isinstance(p, str)
                            and p in post_nodes
                            and _has_propagating_edge(post_edges, p, conclusion_id)
                            for p in just
                        )
                        if all_present:
                            any_intact = True
                            break
                    post_nodes[conclusion_id][status_attr] = (
                        true_v if any_intact else false_v
                    )

            # Cats 5/6/7: CP-SAT over declared computations + combinations.
            values, unknown = solve_computations(post_nodes, post_edges, mi.rules)
            for (n, a), v in values.items():
                post_nodes[n][a] = v
            ambiguous: dict[str, set[str]] = {}
            for (n, a), codes in unknown.items():
                if n in post_nodes:
                    post_nodes[n][a] = None
                    ambiguous.setdefault(n, set()).update(codes)
            combo = solve_combination(post_nodes, post_edges, mi.rules)
            if combo is not None:
                post_nodes[combo["conclusion"]].update(combo["attrs"])
                if combo["unknown"]:
                    ambiguous.setdefault(combo["conclusion"], set()).update(combo["unknown"])
            sat = (mi.rules.get("satisfaction_functions") or {}).get("entries", {}) or {}
            status_nodes = {
                n: sf.get("status_attribute", "status")
                for n, sf in (sat.get("status_functions", {}) or {}).items()
            }
            if combo is not None:
                status_nodes[combo["conclusion"]] = "status"
            quantitative = bool(sat.get("computations") or status_nodes)

            # Compute affected set by comparing with pre-event snapshot.
            pre_attrs: dict[str, dict[str, object]] = {
                n.id: dict(n.attributes) for n in graph.nodes
            }
            all_ids = set(pre_attrs.keys()) | set(post_nodes.keys())
            affected: set[str] = set()
            attribute_values: dict[str, dict[str, object]] = {}

            for nid in all_ids:
                pre = pre_attrs.get(nid)
                post = post_nodes.get(nid)
                if post is None:
                    # Deleted node: changed; keep pre-event attrs so the
                    # affected-set invariant stays comparable.
                    affected.add(nid)
                    attribute_values[nid] = dict(pre) if pre else {}
                    outcome[nid] = OutcomeLabel.MUST_CHANGE
                    continue
                attribute_values[nid] = dict(post)
                if nid in ambiguous:
                    affected.add(nid)
                    outcome[nid] = OutcomeLabel.UNCERTAIN
                elif pre is None or pre != post:
                    affected.add(nid)
                    outcome[nid] = OutcomeLabel.MUST_CHANGE
                else:
                    outcome[nid] = OutcomeLabel.MUST_STAY_STABLE

            return RevisionResult(
                affected_set=sorted(affected),
                outcome_labels=outcome,
                attribute_values=attribute_values,
                feasibility_status={
                    n: post_nodes[n].get(a) for n, a in status_nodes.items() if n in post_nodes
                },
                determinability=(
                    {n: ("AMBIGUOUS" if n in ambiguous else "DETERMINABLE") for n in all_ids}
                    if quantitative else None
                ),
                pathology_flags=(
                    {n: sorted(c) for n, c in ambiguous.items()} if quantitative else None
                ),
                confidence_scores=None,
                feasible_combinations=combo["feasible"] if combo is not None else None,
                search_cost=combo["search_cost"] if combo is not None else None,
                explanation=None,
                unsupported_dimensions=[] if quantitative else ["abstention"],
                token_cost=0,
                wall_time_ms=t.elapsed_ms,
            )
