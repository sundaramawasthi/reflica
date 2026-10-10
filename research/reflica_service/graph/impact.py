"""Impact analysis for graph@1: preview -> fingerprint -> decision -> apply.

`preview(graph, change)` reports which nodes a change may affect, how sure
that is, and the path that explains it, and lists the updates that would be
made. It never modifies the graph. `decide(graph, preview, decision)` applies
the change only if the decision approves that exact preview and the graph is
unchanged since; a rejection is recorded and changes nothing.

Dependent conclusions are never deleted or rewritten automatically: an
approved change only flags them for the researcher's review.

Analyzers sit behind the `ImpactAnalyzer` protocol. `LinkFollowing` (this
module) follows propagating links from the change, with the same scope as the
benchmark's B3 reachability baseline (checked by tests). The attribute-aware
revision engine studied in the thesis can be added later as another analyzer
without changing the contract.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Protocol

from .contract import (AddEdge, AddNode, Change, ChangeEdgeType, ChangeRecord, DeleteEdge,
                       DeleteNode, Decision, Edge, EditNode, Graph, GraphError, ImpactItem,
                       ImpactPreview, PROPAGATING, ProposedUpdate, ResolveReview, ReviewNote)

LINK_FOLLOWING_LIMITATIONS = (
    "Link-following treats every propagating link (requires, supports, causes, blocks, "
    "enables, derived_from) as a possible dependency. It shows what may need review; it does "
    "not decide whether a dependent conclusion actually changes.",
    "Links of type informs or references do not carry a change forward; items connected only "
    "that way are listed as related but unaffected.",
    "Uncertain means every path from the change runs through at least one inferred link that "
    "the researcher has not confirmed.",
    "Only links recorded in the graph are followed; dependencies missing from the graph cannot "
    "be found.",
)


@dataclass(frozen=True)
class Reach:
    """Analyzer output: affected nodes with relation, certainty and explaining path."""

    items: tuple[ImpactItem, ...]
    unaffected: tuple[str, ...]
    related_unaffected: tuple[str, ...]


class ImpactAnalyzer(Protocol):
    name: str

    def analyze(self, graph: Graph, change: Change) -> Reach: ...


# ---------------------------------------------------------------------------
# validation of a change against the graph
# ---------------------------------------------------------------------------

def _require_node(graph: Graph, node_id: str) -> None:
    if graph.node(node_id) is None:
        raise GraphError("unknown_node", f"No node with id '{node_id}'.", {"node_id": node_id})


def _require_edge(graph: Graph, edge_id: str) -> Edge:
    e = graph.edge(edge_id)
    if e is None:
        raise GraphError("unknown_edge", f"No link with id '{edge_id}'.", {"edge_id": edge_id})
    return e


def check_change(graph: Graph, change: Change) -> None:
    """Raise GraphError if `change` cannot be applied to `graph`."""
    taken = {n.id for n in graph.nodes} | {e.id for e in graph.edges}
    if isinstance(change, AddNode):
        if change.node.id in taken:
            raise GraphError("duplicate_id", f"The id '{change.node.id}' is already used.",
                             {"id": change.node.id})
    elif isinstance(change, (EditNode, DeleteNode, ResolveReview)):
        _require_node(graph, change.node_id)
        if isinstance(change, EditNode) and change.label is None and change.detail is None \
                and change.kind is None:
            raise GraphError("empty_edit", "The edit changes nothing.", {"node_id": change.node_id})
        if isinstance(change, ResolveReview) and not graph.node(change.node_id).reviews:
            raise GraphError("nothing_to_resolve", "This node has no open review.",
                             {"node_id": change.node_id})
    elif isinstance(change, AddEdge):
        if change.edge.id in taken:
            raise GraphError("duplicate_id", f"The id '{change.edge.id}' is already used.",
                             {"id": change.edge.id})
        _require_node(graph, change.edge.source)
        _require_node(graph, change.edge.target)
    elif isinstance(change, (DeleteEdge, ChangeEdgeType)):
        e = _require_edge(graph, change.edge_id)
        if isinstance(change, ChangeEdgeType) and e.type == change.new_type:
            raise GraphError("empty_edit", "The link already has this type.",
                             {"edge_id": change.edge_id})


# ---------------------------------------------------------------------------
# link-following analyzer
# ---------------------------------------------------------------------------

def _seeds(graph: Graph, change: Change) -> tuple[str | None, list[tuple[str, bool, tuple]]]:
    """(changed node id or None, [(seed node, seed confirmed?, path to it)])."""
    if isinstance(change, AddNode):
        return change.node.id, []  # a new node has no links yet: nothing downstream
    if isinstance(change, (EditNode, DeleteNode)):
        return change.node_id, [(change.node_id, True, ())]
    if isinstance(change, ResolveReview):
        return None, []  # reviewing does not change content
    if isinstance(change, AddEdge):
        e = change.edge
        return None, ([(e.target, e.certainty == "confirmed", (e.id,))] if e.propagates else [])
    e = graph.edge(change.edge_id)
    new_prop = isinstance(change, ChangeEdgeType) and change.new_type in PROPAGATING
    if e.propagates or new_prop:
        # a re-typed link is asserted by the researcher, so it counts as confirmed
        confirmed = e.certainty == "confirmed" or isinstance(change, ChangeEdgeType)
        return None, [(e.target, confirmed, (e.id,))]
    return None, []


def _bfs(graph: Graph, seeds, confirmed_only: bool) -> dict[str, tuple[int, tuple]]:
    """Shortest (depth, path) to each reachable node. Deterministic: graph order."""
    out_edges: dict[str, list[Edge]] = {}
    for e in graph.edges:
        if e.propagates and (not confirmed_only or e.certainty == "confirmed"):
            out_edges.setdefault(e.source, []).append(e)
    best: dict[str, tuple[int, tuple]] = {}
    queue: deque = deque()
    for node, ok, path in seeds:
        if (ok or not confirmed_only) and node not in best:
            best[node] = (0, path)
            queue.append(node)
    while queue:
        n = queue.popleft()
        depth, path = best[n]
        for e in out_edges.get(n, ()):
            if e.target not in best:
                best[e.target] = (depth + 1, path + (e.id,))
                queue.append(e.target)
    return best


class LinkFollowing:
    """Follow propagating links from the change (scope as the benchmark's B3)."""

    name = "link_following@1"

    def analyze(self, graph: Graph, change: Change) -> Reach:
        changed, seeds = _seeds(graph, change)
        reach_all = _bfs(graph, seeds, confirmed_only=False)
        reach_ok = _bfs(graph, seeds, confirmed_only=True)
        edges = {e.id: e for e in graph.edges}
        if isinstance(change, AddEdge):
            edges[change.edge.id] = change.edge
        items = []
        order = [n.id for n in graph.nodes]
        if changed is not None and changed not in order:
            order.append(changed)  # an added node
        for nid in order:
            if nid == changed:
                items.append(ImpactItem(node_id=nid, relation="changed", certainty="confirmed",
                                        path=(), explanation=_changed_text(change)))
                continue
            if nid not in reach_all:
                continue
            certain = nid in reach_ok
            depth, path = reach_ok[nid] if certain else reach_all[nid]
            # node changes seed the node itself (depth 0); link changes seed the
            # link's target, which is therefore directly affected at depth 0
            direct_depth = 1 if changed is not None else 0
            relation = "direct" if depth == direct_depth else "downstream"
            items.append(ImpactItem(node_id=nid, relation=relation,
                                    certainty="confirmed" if certain else "uncertain", path=path,
                                    explanation=_path_text(graph, edges, path, certain)))
        hit = {i.node_id for i in items}
        unaffected = tuple(n.id for n in graph.nodes if n.id not in hit)
        related = tuple(sorted({e.target if e.source in hit else e.source for e in graph.edges
                                if not e.propagates and ((e.source in hit) != (e.target in hit))}
                               - hit, key=order.index))
        return Reach(items=tuple(items), unaffected=unaffected, related_unaffected=related)


def _changed_text(change: Change) -> str:
    return {"add_node": "This node is being added.",
            "edit_node": "This node is being edited.",
            "delete_node": "This node is being deleted."}[change.op]


_READ = {"requires": "{t} requires {s}", "derived_from": "{t} is derived from {s}"}


def _path_text(graph: Graph, edges: dict[str, Edge], path: tuple, certain: bool) -> str:
    def label(nid):
        n = graph.node(nid)
        return f"'{n.label}'" if n is not None else f"'{nid}'"
    steps = []
    for eid in path:
        e = edges[eid]
        tmpl = _READ.get(e.type, "{s} " + e.type.replace("_", " ") + " {t}")
        steps.append(tmpl.format(s=label(e.source), t=label(e.target))
                     + f" ({e.certainty}, {e.basis.replace('_', ' ')})")
    text = "Affected through: " + "; ".join(steps) + "."
    if not certain:
        text += (" At least one link on every path is inferred and unconfirmed, so this "
                 "dependency is uncertain.")
    return text


# ---------------------------------------------------------------------------
# preview, decision, apply
# ---------------------------------------------------------------------------

def _proposed(graph: Graph, change: Change, reach: Reach) -> list[ProposedUpdate]:
    ups: list[ProposedUpdate] = []
    if isinstance(change, AddNode):
        ups.append(ProposedUpdate(action="add_node", target=change.node.id,
                                  description=f"Add {change.node.kind} '{change.node.label}'."))
    elif isinstance(change, EditNode):
        n = graph.node(change.node_id)
        parts = []
        if change.label is not None and change.label != n.label:
            parts.append(f"label '{n.label}' → '{change.label}'")
        if change.detail is not None and change.detail != n.detail:
            parts.append("detail")
        if change.kind is not None and change.kind != n.kind:
            parts.append(f"kind {n.kind} → {change.kind}")
        if (change.label is not None or change.detail is not None) and n.basis != "user_stated":
            parts.append(f"basis {n.basis} → user_stated (the wording is now the researcher's)")
        ups.append(ProposedUpdate(action="edit_node", target=n.id,
                                  description="Edit: " + ("; ".join(parts) or "no visible change") + "."))
    elif isinstance(change, DeleteNode):
        n = graph.node(change.node_id)
        ups.append(ProposedUpdate(action="delete_node", target=n.id,
                                  description=f"Delete {n.kind} '{n.label}'."))
        for e in graph.edges:
            if change.node_id in (e.source, e.target):
                ups.append(ProposedUpdate(action="delete_edge", target=e.id, description=(
                    f"Remove link {e.source} --{e.type}--> {e.target}, which cannot exist "
                    "without the deleted node.")))
    elif isinstance(change, AddEdge):
        e = change.edge
        ups.append(ProposedUpdate(action="add_edge", target=e.id, description=(
            f"Add link {e.source} --{e.type}--> {e.target} ({e.certainty}).")))
    elif isinstance(change, DeleteEdge):
        e = graph.edge(change.edge_id)
        ups.append(ProposedUpdate(action="delete_edge", target=e.id,
                                  description=f"Remove link {e.source} --{e.type}--> {e.target}."))
    elif isinstance(change, ChangeEdgeType):
        e = graph.edge(change.edge_id)
        ups.append(ProposedUpdate(action="change_edge_type", target=e.id, description=(
            f"Change link {e.source} --{e.type}--> {e.target} to '{change.new_type}' "
            "(now user-stated and confirmed).")))
    elif isinstance(change, ResolveReview):
        ups.append(ProposedUpdate(action="resolve_review", target=change.node_id,
                                  description="Mark this node's open reviews as resolved."))
    for i in reach.items:
        if i.relation != "changed":
            ups.append(ProposedUpdate(action="flag_for_review", target=i.node_id, description=(
                f"Flag for review ({i.certainty}); it is not changed or deleted.")))
    return ups


def preview(graph: Graph, change: Change, analyzer: ImpactAnalyzer | None = None) -> ImpactPreview:
    """Describe what `change` would do to `graph`. Does not modify anything."""
    analyzer = analyzer or LinkFollowing()
    check_change(graph, change)
    reach = analyzer.analyze(graph, change)
    draft = ImpactPreview(analyzer=analyzer.name, graph_sha256=graph.sha256(), change=change,
                          items=reach.items, unaffected=reach.unaffected,
                          related_unaffected=reach.related_unaffected,
                          proposed_updates=tuple(_proposed(graph, change, reach)),
                          limitations=LINK_FOLLOWING_LIMITATIONS
                          if analyzer.name == LinkFollowing.name else (),
                          preview_sha256="0" * 64)
    return draft.model_copy(update={"preview_sha256": draft.fingerprint()})


def decide(graph: Graph, impact: ImpactPreview, decision: Decision,
           analyzer: ImpactAnalyzer | None = None) -> tuple[Graph, ChangeRecord]:
    """Apply an approved preview, or record a rejection. Returns (graph, record)."""
    if impact.fingerprint() != impact.preview_sha256:
        raise GraphError("preview_modified", "The preview's contents do not match its "
                         "fingerprint; it was changed after it was produced.")
    if decision.preview_sha256 != impact.preview_sha256:
        raise GraphError("decision_mismatch", "The decision is for a different preview.",
                         {"decided": decision.preview_sha256, "preview": impact.preview_sha256})
    before = graph.sha256()
    if before != impact.graph_sha256:
        raise GraphError("graph_changed", "The graph has changed since the preview; preview "
                         "the change again.", {"preview_graph": impact.graph_sha256,
                                               "current_graph": before})
    fresh = preview(graph, impact.change, analyzer)
    if fresh.preview_sha256 != impact.preview_sha256:
        raise GraphError("preview_mismatch", "Recomputing the preview gives a different result "
                         "(analyzer or service version differs); preview the change again.")
    if decision.decision == "reject":
        return graph, ChangeRecord(preview=impact, decision=decision, graph_before_sha256=before,
                                   graph_after_sha256=before)
    after = _apply(graph, impact)
    return after, ChangeRecord(preview=impact, decision=decision, graph_before_sha256=before,
                               graph_after_sha256=after.sha256())


def _apply(graph: Graph, impact: ImpactPreview) -> Graph:
    change = impact.change
    nodes = list(graph.nodes)
    edges = list(graph.edges)
    if isinstance(change, AddNode):
        nodes.append(change.node)
    elif isinstance(change, EditNode):
        i = next(k for k, n in enumerate(nodes) if n.id == change.node_id)
        n = nodes[i]
        upd = {k: v for k, v in (("label", change.label), ("detail", change.detail),
                                 ("kind", change.kind)) if v is not None}
        if "label" in upd or "detail" in upd:
            upd["basis"] = "user_stated"
        nodes[i] = _revalidate(n, upd)
    elif isinstance(change, DeleteNode):
        nodes = [n for n in nodes if n.id != change.node_id]
        edges = [e for e in edges if change.node_id not in (e.source, e.target)]
    elif isinstance(change, AddEdge):
        edges.append(change.edge)
    elif isinstance(change, DeleteEdge):
        edges = [e for e in edges if e.id != change.edge_id]
    elif isinstance(change, ChangeEdgeType):
        i = next(k for k, e in enumerate(edges) if e.id == change.edge_id)
        edges[i] = _revalidate(edges[i], {"type": change.new_type, "basis": "user_stated",
                                            "certainty": "confirmed"})
    elif isinstance(change, ResolveReview):
        i = next(k for k, n in enumerate(nodes) if n.id == change.node_id)
        nodes[i] = _revalidate(nodes[i], {"reviews": ()})
    flags = {i.node_id: i for i in impact.items if i.relation != "changed"}
    for k, n in enumerate(nodes):
        item = flags.get(n.id)
        if item is not None:
            note = ReviewNote(change_sha256=impact.preview_sha256,
                              reason=f"{_summary(change)} {item.explanation}")
            nodes[k] = _revalidate(n, {"reviews": n.reviews + (note,)})
    try:
        return Graph(sources=graph.sources, nodes=tuple(nodes), edges=tuple(edges))
    except ValueError as e:  # pragma: no cover - previews are checked first
        raise GraphError("invalid_result", f"The change would produce an invalid graph: {e}")


def _summary(change: Change) -> str:
    return {"add_node": "A node was added.", "edit_node": f"'{getattr(change, 'node_id', '')}' was edited.",
            "delete_node": f"'{getattr(change, 'node_id', '')}' was deleted.",
            "add_edge": "A link was added.", "delete_edge": "A link was removed.",
            "change_edge_type": "A link's type was changed.",
            "resolve_review": "A review was resolved."}[change.op]


def _revalidate(model, update: dict):
    """Copy with changes, re-running validation (model_copy alone does not validate)."""
    return type(model).model_validate({**model.model_dump(), **update})
