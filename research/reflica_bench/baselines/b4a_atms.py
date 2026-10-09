"""B4a — Classical ATMS-style baseline (Cats 1 / 2 / 3 / 4).

Cat 1: no justifications touched → only the direct event target changes.

Cat 2 and Cat 3: propagation_rules are treated as justifications; the
baseline walks them transitively, respecting edge-type semantics (and
over-flipping at rule-insensitivity termination, as the design expects).

Cat 4: alternative justifications. When a conclusion declares multiple
justifications, B4a correctly preserves it as long as ANY justification is
intact in the post-event graph. This is the classical ATMS property. B4a
does NOT compute attribute values; attribute_values stays None (N/A).

Cats 5/6: each declared computation / combination problem is read as a
justification link (source → owner); B4a walks them for scope only.

Cat 7 (partial abstention): ATMS can see structural trouble in its
justification network — a cycle among propagating edges (P4) and two active
rules justifying the same output (P5) — and flags those nodes plus their
dependents as AMBIGUOUS. It has no notion of missing values, units, claims,
referents or ties, so it commits on every other pathology.
"""

from __future__ import annotations

from ._event import resolve_target
from ..adapters import AdapterOutput
from ..baseline import Baseline, RevisionResult, Timer
from ..schema import (
    PROPAGATING_EDGE_TYPES,
    Operation,
    OutcomeLabel,
    TargetKind,
)


def _build_post_event_graph_sketch(graph, ev) -> tuple[set[str], list[dict]]:
    """Minimal post-event graph (node ids + edges) sketched inline so B4a
    can evaluate alternative justifications without duplicating the full
    ground-truth generator. Keeps B4a's dependency surface small — only
    graph existence + propagating-edge membership matters for ATMS."""
    nodes = set(graph.node_ids())
    edges: list[dict] = [
        {"edge_id": e.edge_id, "source": e.source, "target": e.target, "type": e.type}
        for e in graph.edges
    ]
    if ev.operation == Operation.ADD and ev.target_kind == TargetKind.NODE:
        if ev.new_node is not None:
            nodes.add(ev.new_node.id)
    elif ev.operation == Operation.ADD and ev.target_kind == TargetKind.EDGE:
        if ev.edge_change is not None:
            edges.append(
                {
                    "edge_id": f"__added__{ev.edge_change.source}_{ev.edge_change.target}",
                    "source": ev.edge_change.source,
                    "target": ev.edge_change.target,
                    "type": ev.edge_change.new_type,
                }
            )
    elif ev.operation == Operation.DELETE and ev.target_kind == TargetKind.NODE:
        if ev.target_id is not None:
            nodes.discard(ev.target_id)
            edges = [e for e in edges if e["source"] != ev.target_id and e["target"] != ev.target_id]
    elif ev.operation == Operation.DELETE and ev.target_kind == TargetKind.EDGE:
        if ev.target_id is not None:
            edges = [e for e in edges if e["edge_id"] != ev.target_id]
    elif ev.operation == Operation.RELATIONSHIP_CHANGE:
        if ev.edge_change is not None and ev.edge_change.edge_id is not None:
            for e in edges:
                if e["edge_id"] == ev.edge_change.edge_id and ev.edge_change.new_type is not None:
                    e["type"] = ev.edge_change.new_type
    return nodes, edges


def _justification_intact_sketch(
    premises: list, conclusion_id: str, nodes: set[str], edges: list[dict]
) -> bool:
    for p in premises:
        if not isinstance(p, str) or p not in nodes:
            return False
        if not any(
            e["source"] == p and e["target"] == conclusion_id and e["type"] in PROPAGATING_EDGE_TYPES
            for e in edges
        ):
            return False
    return True


def _refs(e, owner: str, out: set[str]) -> None:
    if isinstance(e, dict):
        for k in ("ref", "src"):
            if k in e:
                node = e[k].split(".", 1)[0]
                if node != owner:
                    out.add(node)
        if "agg" in e:
            out.add("*")
        for v in e.values():
            _refs(v, owner, out)
    elif isinstance(e, list):
        for v in e:
            _refs(v, owner, out)


def _quantitative_links(rules: dict) -> list[tuple[str, str]]:
    sat = (rules.get("satisfaction_functions") or {}).get("entries", {}) or {}
    links: set[tuple[str, str]] = set()
    for c in sat.get("computations", []) or []:
        srcs: set[str] = set()
        _refs(c.get("machine"), c["node"], srcs)
        links |= {(s, c["node"]) for s in srcs}
    for n, sf in (sat.get("status_functions", {}) or {}).items():
        srcs = set()
        _refs(sf.get("mapping"), n, srcs)
        links |= {(s, n) for s in srcs}
    problems = ((rules.get("combination_selection") or {}).get("entries") or {}).get("problems", {}) or {}
    links |= {("*", n) for n in problems}
    return sorted(links)


def _structural_pathologies(rules: dict, nodes: set[str], edges: list[dict], links) -> dict[str, list[str]]:
    """P4: nodes on a propagating-edge cycle; P5: two active computations for
    one output. Both spread to dependents along propagating edges."""
    adj: dict[str, set[str]] = {}
    for e in edges:
        if e["type"] in PROPAGATING_EDGE_TYPES and e["source"] in nodes and e["target"] in nodes:
            adj.setdefault(e["source"], set()).add(e["target"])

    def reach(a: str) -> set[str]:
        seen, stack = set(), list(adj.get(a, ()))
        while stack:
            n = stack.pop()
            if n not in seen:
                seen.add(n)
                stack.extend(adj.get(n, ()))
        return seen

    flags: dict[str, set[str]] = {}
    for n in nodes:
        if n in reach(n):
            flags.setdefault(n, set()).add("P4")
    sat = (rules.get("satisfaction_functions") or {}).get("entries", {}) or {}
    count: dict[tuple[str, str], int] = {}
    for c in sat.get("computations", []) or []:
        if c["node"] in nodes and all(w in adj and c["node"] in adj[w] for w in c.get("when_linked", [])):
            k = (c["node"], c["attribute"])
            count[k] = count.get(k, 0) + 1
    for (n, _a), k in count.items():
        if k > 1:
            flags.setdefault(n, set()).add("P5")
    for n in list(flags):
        for d in reach(n):
            flags.setdefault(d, set()).update(flags[n])
    return {n: sorted(c) for n, c in flags.items()}


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

            # The direct event target is always a candidate for change.
            if ev.operation == Operation.ADD and ev.target_kind == TargetKind.NODE:
                assert ev.new_node is not None
                affected.add(ev.new_node.id)
            elif ev.operation == Operation.EDIT:
                target = resolve_target(graph, ev)
                if target is not None:
                    affected.add(target)
            elif ev.operation == Operation.DELETE and ev.target_kind == TargetKind.NODE:
                assert ev.target_id is not None
                affected.add(ev.target_id)
            # Edge-only ADD / DELETE / RELATIONSHIP_CHANGE touch no node
            # attribute directly, but may touch justifications (handled below).

            # Walk declared propagation rules as justifications. From Cat 2
            # onward, these let ATMS reach the depth-1 dependents without
            # computing their new attribute values.
            rules_block = mi.rules.get("propagation_rules")
            rule_list: list[dict] = []
            if isinstance(rules_block, dict):
                entries = rules_block.get("entries", {})
                if isinstance(entries, dict):
                    cand = entries.get("rules", [])
                    if isinstance(cand, list):
                        rule_list = list(cand)
            # Cats 5/6/7: declared computations / combination problems become
            # justification links. "*" = any node with a propagating edge in.
            quant_links = _quantitative_links(mi.rules)
            rule_list += [{"from_node": f, "to_node": t} for f, t in quant_links]

            # Collect sources whose "support" is affected by the event.
            affected_sources: set[str] = set()
            if ev.operation == Operation.EDIT and resolve_target(graph, ev) is not None:
                affected_sources.add(resolve_target(graph, ev))
            if (
                ev.operation == Operation.DELETE
                and ev.target_kind == TargetKind.NODE
                and ev.target_id is not None
            ):
                affected_sources.add(ev.target_id)

            # Edge events touch justifications when the edge type is (or
            # becomes) propagating between a known from_node and to_node.
            if ev.operation == Operation.ADD and ev.target_kind == TargetKind.EDGE:
                assert ev.edge_change is not None
                if (
                    ev.edge_change.new_type is not None
                    and ev.edge_change.new_type in PROPAGATING_EDGE_TYPES
                ):
                    for r in rule_list:
                        if (
                            r.get("from_node") in (ev.edge_change.source, "*")
                            and r.get("to_node") == ev.edge_change.target
                        ):
                            affected.add(r["to_node"])

            if ev.operation == Operation.DELETE and ev.target_kind == TargetKind.EDGE:
                e = graph.edge(ev.target_id)  # type: ignore[arg-type]
                if e is not None and e.type in PROPAGATING_EDGE_TYPES:
                    for r in rule_list:
                        if r.get("from_node") in (e.source, "*") and r.get("to_node") == e.target:
                            affected.add(r["to_node"])

            if ev.operation == Operation.RELATIONSHIP_CHANGE:
                assert ev.edge_change is not None and ev.edge_change.edge_id is not None
                e = graph.edge(ev.edge_change.edge_id)
                old_prop = e is not None and e.type in PROPAGATING_EDGE_TYPES
                new_prop = (
                    ev.edge_change.new_type is not None
                    and ev.edge_change.new_type in PROPAGATING_EDGE_TYPES
                )
                if e is not None and (old_prop or new_prop):
                    for r in rule_list:
                        if r.get("from_node") in (e.source, "*") and r.get("to_node") == e.target:
                            affected.add(r["to_node"])

            # Transitive justification invalidation: a dependent whose
            # justification is touched becomes a new "affected source" that
            # may touch further justifications. We iterate to a fixed point
            # by alternately walking rules and absorbing newly-affected
            # dependents into affected_sources. This mirrors ATMS cascading
            # invalidation and — critically — does NOT check whether the
            # rule's output actually changes, so B4a will over-flip at
            # rule-insensitivity termination points on Cat 3 (expected).
            while True:
                before = len(affected)
                for r in rule_list:
                    to_n = r["to_node"]
                    froms = (
                        [r["from_node"]] if r["from_node"] != "*"
                        else [e.source for e in graph.edges if e.target == to_n]
                    )
                    for from_n in froms:
                        if from_n not in affected_sources:
                            continue
                        has_prop_edge = any(
                            e.source == from_n
                            and e.target == to_n
                            and e.type in PROPAGATING_EDGE_TYPES
                            for e in graph.edges
                        )
                        if has_prop_edge:
                            affected.add(to_n)
                            affected_sources.add(to_n)
                if len(affected) == before:
                    break

            # Cat 4: alternative-justification preservation. If a conclusion
            # declares multiple justifications and at least one remains
            # intact in the post-event graph, ATMS preserves it. We
            # therefore REMOVE such conclusions from the affected set even
            # if a transitive walk previously flagged them.
            justif_block = mi.rules.get("justifications")
            conclusions_cfg: dict = {}
            if isinstance(justif_block, dict):
                conclusions_cfg = justif_block.get("entries", {}).get("conclusions", {}) or {}

            if conclusions_cfg:
                post_nodes_set, post_edges_list = _build_post_event_graph_sketch(graph, ev)
                for conclusion_id, config in conclusions_cfg.items():
                    if conclusion_id not in post_nodes_set:
                        continue
                    justs = config.get("justifications", [])
                    any_intact = False
                    for just in justs:
                        if _justification_intact_sketch(
                            just, conclusion_id, post_nodes_set, post_edges_list
                        ):
                            any_intact = True
                            break
                    if any_intact:
                        affected.discard(conclusion_id)
                    else:
                        affected.add(conclusion_id)

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

            determinability = None
            flags = None
            if quant_links:
                post_nodes_set, post_edges_list = _build_post_event_graph_sketch(graph, ev)
                flags = _structural_pathologies(mi.rules, post_nodes_set, post_edges_list, quant_links)
                for nid in flags:
                    affected.add(nid)
                    outcome[nid] = OutcomeLabel.UNCERTAIN
                determinability = {
                    n: ("AMBIGUOUS" if n in flags else "DETERMINABLE") for n in outcome
                }

            return RevisionResult(
                affected_set=sorted(affected),
                outcome_labels=outcome,
                attribute_values=None,
                feasibility_status=None,
                determinability=determinability,
                pathology_flags=flags,
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
