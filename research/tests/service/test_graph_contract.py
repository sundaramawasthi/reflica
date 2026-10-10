"""graph@1 contract: structure, provenance, epistemic rules and the exported schema."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest
from pydantic import TypeAdapter, ValidationError

from reflica_service.graph import export_schema
from reflica_service.graph.contract import (Change, Decision, Edge, Graph, Node, Source,
                                            SourceSpan, sha256_text)

DATA = Path(__file__).parent / "data" / "graph"
_spec = importlib.util.spec_from_file_location("make_examples", DATA / "make_examples.py")
make_examples = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(make_examples)


def example() -> Graph:
    return make_examples.research_example()


def test_fixture_file_is_current_and_round_trips():
    on_disk = json.loads((DATA / "research_example.json").read_text())
    g = example()
    assert g.model_dump(mode="json") == on_disk
    assert Graph.model_validate(on_disk) == g
    assert Graph.model_validate_json(g.model_dump_json()).sha256() == g.sha256()


def test_exported_schema_is_current():
    assert export_schema.PATH.read_text() == export_schema.render()
    schema = json.loads(export_schema.PATH.read_text())
    assert schema["version"] == "graph@1"
    assert set(schema) == {"version", "Graph", "Change", "ImpactPreview", "Decision", "ChangeRecord"}


def test_kind_and_basis_are_separate_fields():
    node = example().node("h1")
    assert (node.kind, node.basis) == ("hypothesis", "source_quoted")  # quoted, still a hypothesis


def test_every_quote_is_verbatim_in_its_source():
    g = example()
    text = g.sources[0].text
    for owner in (*g.nodes, *g.edges):
        for sp in owner.spans:
            assert text[sp.start:sp.end] == sp.quote


def _dump(g: Graph) -> dict:
    return g.model_dump(mode="json")


def test_quote_that_is_not_in_the_source_is_rejected():
    d = _dump(example())
    sp = d["nodes"][0]["spans"][0]
    sp["quote"] = "X" + sp["quote"][1:]
    with pytest.raises(ValidationError, match="not verbatim"):
        Graph.model_validate(d)


def test_span_must_cite_a_known_source_and_consistent_offsets():
    d = _dump(example())
    d["nodes"][0]["spans"][0]["source_id"] = "s9"
    with pytest.raises(ValidationError, match="unknown source"):
        Graph.model_validate(d)
    with pytest.raises(ValidationError, match="len"):
        SourceSpan(source_id="s1", start=0, end=5, quote="abc")


def test_source_hash_must_match_text():
    with pytest.raises(ValidationError, match="sha256"):
        Source(id="s1", title="t", text="abc", sha256=sha256_text("abd"))


def test_basis_requirements():
    with pytest.raises(ValidationError, match="source span"):
        Node(id="n", kind="claim", label="x", basis="source_quoted")
    with pytest.raises(ValidationError, match="run_id"):
        Node(id="n", kind="result", label="x", basis="computed")
    Node(id="n", kind="result", label="x", basis="computed", run_id="regress:abc")


def test_inferred_links_cannot_be_marked_confirmed():
    with pytest.raises(ValidationError, match="must be 'inferred'"):
        Edge(id="e", source="a", target="b", type="supports", certainty="confirmed",
             basis="llm_inferred")
    with pytest.raises(ValidationError, match="itself"):
        Edge(id="e", source="a", target="a", type="supports", certainty="inferred",
             basis="llm_inferred")


@pytest.mark.parametrize("mutate, message", [
    (lambda d: d["nodes"].append(dict(d["nodes"][0])), "duplicate node ids"),
    (lambda d: d["edges"].append(dict(d["edges"][0])), "duplicate edge ids"),
    (lambda d: d["edges"][0].update(target="zz"), "does not exist"),
    (lambda d: d["edges"][0].update(id="h1"), "share an id"),
])
def test_graph_integrity(mutate, message):
    d = _dump(example())
    mutate(d)
    with pytest.raises(ValidationError, match=message):
        Graph.model_validate(d)


def test_unknown_fields_kinds_and_versions_are_rejected():
    d = _dump(example())
    for bad in ({"version": "graph@2"}, {"extra": 1}):
        with pytest.raises(ValidationError):
            Graph.model_validate({**d, **bad})
    d["nodes"][0]["kind"] = "fact"  # not a kind: truth is never a kind
    with pytest.raises(ValidationError):
        Graph.model_validate(d)


def test_ids_are_restricted():
    for bad in ("", "has space", "-lead", "x" * 65):
        with pytest.raises(ValidationError):
            Node(id=bad, kind="claim", label="x", basis="user_stated")


def test_change_union_parses_by_op():
    ch = TypeAdapter(Change).validate_python({"op": "delete_node", "node_id": "h1"})
    assert ch.op == "delete_node"
    with pytest.raises(ValidationError):
        TypeAdapter(Change).validate_python({"op": "merge_nodes", "node_id": "h1"})


def test_decision_needs_a_named_person():
    for who in ("", "   "):
        with pytest.raises(ValidationError):
            Decision(preview_sha256="0" * 64, decision="approve", decided_by=who)


def test_graph_hash_is_canonical():
    g = example()
    again = Graph.model_validate(json.loads(json.dumps(g.model_dump(mode="json"), sort_keys=True)))
    assert again.sha256() == g.sha256()
    other = Graph.model_validate({**g.model_dump(mode="json"),
                                  "nodes": [n.model_dump(mode="json") for n in g.nodes[:-1]],
                                  "edges": [e.model_dump(mode="json") for e in g.edges
                                            if "l1" not in (e.source, e.target)]})
    assert other.sha256() != g.sha256()
