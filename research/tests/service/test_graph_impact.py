"""Impact analysis: preview -> fingerprint -> decision -> apply, and B3 equivalence."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

from reflica_service.graph.contract import (AddEdge, AddNode, ChangeEdgeType, Decision,
                                            DeleteEdge, DeleteNode, Edge, EditNode, Graph,
                                            GraphError, ImpactPreview, Node, ResolveReview)
from reflica_service.graph.impact import LinkFollowing, Reach, preview, decide

DATA = Path(__file__).parent / "data" / "graph"
_spec = importlib.util.spec_from_file_location("make_examples", DATA / "make_examples.py")
make_examples = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(make_examples)


def example() -> Graph:
    return make_examples.research_example()


def chain(*links, certainty="confirmed", extra_nodes=()) -> Graph:
    """Graph from ("a", "supports", "b") triples; all user-stated."""
    ids = list(dict.fromkeys([x for s, _, t in links for x in (s, t)] + list(extra_nodes)))
    nodes = tuple(Node(id=i, kind="claim", label=f"claim {i}", basis="user_stated") for i in ids)
    edges = tuple(Edge(id=f"e{k}", source=s, target=t, type=ty, certainty=certainty,
                       basis="user_stated" if certainty == "confirmed" else "llm_inferred")
                  for k, (s, ty, t) in enumerate(links))
    return Graph(nodes=nodes, edges=edges)


def by_id(p: ImpactPreview) -> dict:
    return {i.node_id: i for i in p.items}


def approve(p, who="researcher"):
    return Decision(preview_sha256=p.preview_sha256, decision="approve", decided_by=who)


# ---------------------------------------------------------------------------
# what is affected
# ---------------------------------------------------------------------------

def test_chain_direct_downstream_and_unaffected():
    g = chain(("a", "supports", "b"), ("b", "supports", "c"), extra_nodes=("d",))
    p = preview(g, DeleteNode(node_id="a"))
    items = by_id(p)
    assert {k: v.relation for k, v in items.items()} == {"a": "changed", "b": "direct",
                                                         "c": "downstream"}
    assert all(i.certainty == "confirmed" for i in p.items)
    assert items["c"].path == ("e0", "e1")
    assert p.unaffected == ("d",)


def test_non_propagating_links_do_not_carry_a_change():
    g = chain(("a", "informs", "b"), ("a", "references", "c"), ("b", "supports", "d"))
    p = preview(g, EditNode(node_id="a", label="new wording"))
    assert set(by_id(p)) == {"a"}
    assert set(p.unaffected) == {"b", "c", "d"}
    assert set(p.related_unaffected) == {"b", "c"}


def test_cycles_terminate_and_report_each_node_once():
    g = chain(("a", "supports", "b"), ("b", "supports", "c"), ("c", "supports", "a"))
    p = preview(g, EditNode(node_id="b", label="x"))
    assert [i.node_id for i in p.items] == ["a", "b", "c"]
    assert by_id(p)["c"].relation == "direct" and by_id(p)["a"].relation == "downstream"


def test_inferred_links_make_dependencies_uncertain():
    g = example()
    p = preview(g, DeleteNode(node_id="a1"))       # a1 --requires(inferred)--> r1 ...
    items = by_id(p)
    assert {k: v.certainty for k, v in items.items() if k != "a1"} == {
        "r1": "uncertain", "h1": "uncertain", "t1": "uncertain"}
    assert "inferred and unconfirmed" in items["r1"].explanation


def test_confirmed_path_is_preferred_when_one_exists():
    g = Graph(nodes=tuple(Node(id=i, kind="claim", label=i, basis="user_stated") for i in "abc"),
              edges=(Edge(id="e1", source="a", target="c", type="supports", certainty="inferred",
                          basis="llm_inferred"),
                     Edge(id="e2", source="a", target="b", type="supports", certainty="confirmed",
                          basis="user_stated"),
                     Edge(id="e3", source="b", target="c", type="supports", certainty="confirmed",
                          basis="user_stated")))
    c = by_id(preview(g, EditNode(node_id="a", label="x")))["c"]
    assert (c.certainty, c.path, c.relation) == ("confirmed", ("e2", "e3"), "downstream")


def test_example_research_graph_explanations():
    g = example()
    p = preview(g, DeleteNode(node_id="m1"))
    items = by_id(p)
    assert items["r1"].certainty == "confirmed" and items["r1"].relation == "direct"
    assert "'Weekly irrigated plots yielded 18% more grain than rain-fed plots' is derived from " \
           "'2024 field trial measuring grain yield in 40 plots' (confirmed, source quoted)" \
           in items["r1"].explanation
    assert items["h1"].certainty == "uncertain" and items["t1"].relation == "downstream"
    assert p.related_unaffected == ("l1",)
    assert p.unaffected == ("a1", "l1")


def test_requires_reads_in_the_right_direction():
    g = chain(("supplier", "requires", "task"))
    item = by_id(preview(g, DeleteNode(node_id="supplier")))["task"]
    assert "'claim task' requires 'claim supplier'" in item.explanation


@pytest.mark.parametrize("change, expected", [
    (DeleteEdge(edge_id="e0"), {"b": "direct", "c": "downstream"}),
    (ChangeEdgeType(edge_id="e0", new_type="informs"), {"b": "direct", "c": "downstream"}),
    (AddEdge(edge=Edge(id="new", source="d", target="c", type="enables",
                       certainty="confirmed", basis="user_stated")), {"c": "direct"}),
    (AddEdge(edge=Edge(id="new", source="d", target="c", type="informs",
                       certainty="inferred", basis="llm_inferred")), {}),
    (AddNode(node=Node(id="z", kind="question", label="new", basis="user_stated")),
     {"z": "changed"}),
])
def test_edge_and_add_operations(change, expected):
    g = chain(("a", "supports", "b"), ("b", "supports", "c"), extra_nodes=("d",))
    assert {k: v.relation for k, v in by_id(preview(g, change)).items()} == expected


def test_retyping_an_inferred_link_counts_as_confirmed_by_the_researcher():
    g = chain(("a", "supports", "b"), certainty="inferred")
    assert by_id(preview(g, DeleteEdge(edge_id="e0")))["b"].certainty == "uncertain"
    assert by_id(preview(g, ChangeEdgeType(edge_id="e0", new_type="causes")))["b"].certainty \
        == "confirmed"


@pytest.mark.parametrize("change, code", [
    (DeleteNode(node_id="nope"), "unknown_node"),
    (DeleteEdge(edge_id="nope"), "unknown_edge"),
    (EditNode(node_id="a"), "empty_edit"),
    (ChangeEdgeType(edge_id="e0", new_type="supports"), "empty_edit"),
    (AddNode(node=Node(id="a", kind="claim", label="dup", basis="user_stated")), "duplicate_id"),
    (AddEdge(edge=Edge(id="e9", source="a", target="zz", type="supports", certainty="confirmed",
                       basis="user_stated")), "unknown_node"),
    (ResolveReview(node_id="a"), "nothing_to_resolve"),
])
def test_invalid_changes_are_refused(change, code):
    with pytest.raises(GraphError) as e:
        preview(chain(("a", "supports", "b")), change)
    assert e.value.code == code


# ---------------------------------------------------------------------------
# preview is read-only; decision is required; dependents are only flagged
# ---------------------------------------------------------------------------

def test_preview_does_not_modify_the_graph_and_is_deterministic():
    g = example()
    before = g.model_dump_json()
    p1 = preview(g, DeleteNode(node_id="m1"))
    p2 = preview(g, DeleteNode(node_id="m1"))
    assert g.model_dump_json() == before
    assert p1 == p2 and p1.preview_sha256 == p1.fingerprint()
    assert p1.graph_sha256 == g.sha256()


def test_delete_proposes_link_removal_and_review_flags_never_deleting_dependents():
    g = example()
    p = preview(g, DeleteNode(node_id="m1"))
    actions = [(u.action, u.target) for u in p.proposed_updates]
    assert actions == [("delete_node", "m1"), ("delete_edge", "e1"),
                       ("flag_for_review", "h1"), ("flag_for_review", "r1"),
                       ("flag_for_review", "t1")]  # graph order, deterministic
    after, record = decide(g, p, approve(p))
    assert {n.id for n in after.nodes} == {"h1", "r1", "a1", "t1", "l1"}   # only m1 removed
    assert after.edge("e1") is None and after.edge("e2") is not None
    flagged = {n.id for n in after.nodes if n.needs_review}
    assert flagged == {"r1", "h1", "t1"}
    note = after.node("h1").reviews[0]
    assert note.change_sha256 == p.preview_sha256 and "'m1' was deleted." in note.reason
    assert after.node("r1").label == g.node("r1").label  # content untouched
    assert record.graph_before_sha256 == g.sha256() and record.graph_after_sha256 == after.sha256()


def test_reject_changes_nothing_and_is_recorded():
    g = example()
    p = preview(g, DeleteNode(node_id="m1"))
    after, record = decide(g, p, Decision(preview_sha256=p.preview_sha256, decision="reject",
                                          decided_by="researcher", note="keep the trial"))
    assert after == g
    assert record.graph_after_sha256 == record.graph_before_sha256 == g.sha256()
    assert record.decision.note == "keep the trial"


def test_decision_must_name_this_preview():
    g = example()
    p = preview(g, DeleteNode(node_id="m1"))
    other = preview(g, DeleteNode(node_id="a1"))
    with pytest.raises(GraphError) as e:
        decide(g, p, approve(other))
    assert e.value.code == "decision_mismatch"


def test_edited_preview_is_refused():
    g = example()
    p = preview(g, DeleteNode(node_id="m1"))
    tampered = p.model_copy(update={"items": p.items[:1]})  # hide the dependents
    with pytest.raises(GraphError) as e:
        decide(g, tampered, approve(tampered))
    assert e.value.code == "preview_modified"


def test_stale_preview_is_refused_after_the_graph_changes():
    g = example()
    p = preview(g, DeleteNode(node_id="m1"))
    q = preview(g, EditNode(node_id="l1", label="Two seasons would be better"))
    g2, _ = decide(g, q, approve(q))
    with pytest.raises(GraphError) as e:
        decide(g2, p, approve(p))
    assert e.value.code == "graph_changed"


def test_a_different_analyzer_cannot_reuse_a_preview():
    class Nothing:
        name = "nothing@0"

        def analyze(self, graph, change):
            return Reach(items=(), unaffected=tuple(n.id for n in graph.nodes),
                         related_unaffected=())

    g = example()
    p = preview(g, DeleteNode(node_id="m1"))
    with pytest.raises(GraphError) as e:
        decide(g, p, approve(p), analyzer=Nothing())
    assert e.value.code == "preview_mismatch"
    q = preview(g, DeleteNode(node_id="m1"), analyzer=Nothing())
    assert q.analyzer == "nothing@0" and q.limitations == ()


def test_editing_wording_makes_it_the_researchers_but_keeps_provenance():
    g = example()
    p = preview(g, EditNode(node_id="h1", label="Moisture is associated with yield"))
    assert "basis source_quoted → user_stated" in p.proposed_updates[0].description
    after, _ = decide(g, p, approve(p))
    h1 = after.node("h1")
    assert (h1.basis, h1.kind, h1.spans) == ("user_stated", "hypothesis", g.node("h1").spans)
    assert after.node("t1").needs_review and not after.node("a1").needs_review
    assert not h1.needs_review  # the edited node is the change itself, not flagged by it


def test_changing_only_the_kind_keeps_the_basis():
    g = example()
    p = preview(g, EditNode(node_id="h1", kind="claim"))
    after, _ = decide(g, p, approve(p))
    assert (after.node("h1").kind, after.node("h1").basis) == ("claim", "source_quoted")


def test_retype_becomes_confirmed_user_statement_and_review_can_be_resolved():
    g = example()
    p = preview(g, ChangeEdgeType(edge_id="e2", new_type="causes"))
    g2, _ = decide(g, p, approve(p))
    e2 = g2.edge("e2")
    assert (e2.type, e2.certainty, e2.basis) == ("causes", "confirmed", "user_stated")
    assert g2.node("h1").needs_review
    r = preview(g2, ResolveReview(node_id="h1"))
    assert r.items == ()
    g3, _ = decide(g2, r, approve(r))
    assert not g3.node("h1").needs_review and g3.node("t1").needs_review


def test_reviews_accumulate_across_changes():
    g = chain(("a", "supports", "c"), ("b", "supports", "c"))
    p = preview(g, EditNode(node_id="a", label="x"))
    g, _ = decide(g, p, approve(p))
    q = preview(g, EditNode(node_id="b", label="y"))
    g, _ = decide(g, q, approve(q))
    assert len(g.node("c").reviews) == 2


def test_records_serialize():
    g = example()
    p = preview(g, DeleteNode(node_id="m1"))
    _, record = decide(g, p, approve(p))
    again = type(record).model_validate_json(record.model_dump_json())
    assert again == record
    json.loads(p.model_dump_json())


# ---------------------------------------------------------------------------
# equivalence with the benchmark's B3 reachability baseline
# ---------------------------------------------------------------------------

def _benchmark_cases():
    from reflica_bench.adapters import StructuredAdapter_v1
    from reflica_bench.loader import iter_scenarios, scenarios_dir
    out = []
    for s in iter_scenarios(scenarios_dir()):
        out.append((s.scenario_id, StructuredAdapter_v1().adapt(s, "equivalence")))
    return out


CASES = _benchmark_cases()


def _to_graph1(mi):
    """Benchmark structured input -> graph@1 (user-stated, confirmed) + change."""
    nodes = tuple(Node(id=n.id, kind="claim", label=n.id, basis="user_stated")
                  for n in mi.graph.nodes)
    edges = tuple(Edge(id=e.edge_id, source=e.source, target=e.target, type=e.type.value,
                       certainty="confirmed", basis="user_stated") for e in mi.graph.edges)
    g = Graph(nodes=nodes, edges=edges)
    ev = mi.event
    op, kind = ev.operation.value, ev.target_kind.value
    if ev.target_ref is not None:
        return g, None  # target named ambiguously (Cat 7): graph@1 changes name an exact id
    if (op, kind) == ("EDIT", "node"):
        return g, EditNode(node_id=ev.target_id, detail=f"{ev.attribute} = {ev.new_value!r}")
    if (op, kind) == ("DELETE", "node"):
        return g, DeleteNode(node_id=ev.target_id)
    if (op, kind) == ("ADD", "node"):
        return g, AddNode(node=Node(id=ev.new_node.id, kind="claim", label=ev.new_node.id,
                                    basis="user_stated"))
    ec = ev.edge_change
    if ec is not None and ec.new_type is None:
        return g, None  # link kind deliberately unstated (Cat 7): graph@1 links have a type
    if (op, kind) == ("ADD", "edge"):
        return g, AddEdge(edge=Edge(id=ec.edge_id or "added_edge", source=ec.source,
                                    target=ec.target, type=ec.new_type.value,
                                    certainty="confirmed", basis="user_stated"))
    if op == "RELATIONSHIP_CHANGE":
        return g, ChangeEdgeType(edge_id=ec.edge_id, new_type=ec.new_type.value)
    if (op, kind) == ("DELETE", "edge"):
        return g, DeleteEdge(edge_id=ev.target_id)
    raise AssertionError(f"unmapped event {op} {kind}")


@pytest.mark.parametrize("sid, out", CASES, ids=[c[0] for c in CASES])
def test_affected_set_equals_b3(sid, out):
    from reflica_bench.baselines.b3_reachability import B3Reachability
    g, change = _to_graph1(out.structured)
    if change is None:
        pytest.skip("ambiguous target or unstated link type: not expressible as a graph@1 change")
    p = preview(g, change)
    b3 = B3Reachability().revise(out)
    assert sorted(i.node_id for i in p.items) == b3.affected_set
    stable = {n for n, lab in b3.outcome_labels.items() if lab.value == "MUST_STAY_STABLE"}
    assert set(p.unaffected) == stable


def test_equivalence_covers_the_benchmark():
    mapped = sum(_to_graph1(out.structured)[1] is not None for _, out in CASES)
    assert (len(CASES), mapped) == (63, 60)  # 3 Cat 7 ambiguity cases are not expressible
