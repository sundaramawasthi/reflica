"""Extraction: provider-neutral, offline. All model responses are hand-written fixtures."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from reflica_service.extraction.extract import (MAX_INPUT_CHARS, PROMPT_VERSION, ExtractionError,
                                                accept, extract, locate, request_for)
from reflica_service.extraction.llm import LLMError, LLMResponse, ScriptedLLM
from reflica_service.extraction.schema import ProposalReview
from reflica_service.graph import impact
from reflica_service.graph.contract import Decision, DeleteNode, Graph

DATA = Path(__file__).parent / "data" / "extraction"
TEXT = (DATA / "input.txt").read_text()
GOOD = (DATA / "good_response.json").read_text()
FLAWED = (DATA / "flawed_response.json").read_text()


def proposal(response=GOOD, text=TEXT):
    return extract(text, ScriptedLLM(response))


def nodes_by_label(p):
    return {n.label: n for n in p.graph.nodes}


def review(p, **kw):
    return ProposalReview(proposal_sha256=p.proposal_sha256, decided_by="Dr A", **kw)


# ---------------------------------------------------------------------------
# a good response
# ---------------------------------------------------------------------------

def test_good_response_becomes_a_checked_proposal():
    p = proposal()
    assert len(p.graph.nodes) == 7 and len(p.graph.edges) == 6
    assert p.refs == {"q": "n1", "h": "n2", "m": "n3", "r": "n4", "a": "n5", "t": "n6", "l": "n7"}
    kinds = [n.kind for n in p.graph.nodes]
    assert kinds == ["question", "hypothesis", "method", "result", "assumption", "task", "limitation"]
    assert p.source.text == TEXT and p.graph.sources == (p.source,)
    assert p.clarifying_questions[0].startswith("Were plots assigned")
    assert p.model.provider == "scripted" and p.model.prompt_version == PROMPT_VERSION


def test_basis_follows_quote_verification():
    p = proposal()
    by = {n.id: n for n in p.graph.nodes}
    assert all(by[i].basis == "source_quoted" for i in ("n1", "n2", "n3", "n4", "n5", "n6"))
    assert by["n7"].basis == "llm_inferred" and by["n7"].spans == ()
    for n in p.graph.nodes:
        for sp in n.spans:
            assert TEXT[sp.start:sp.end] == sp.quote
    assert [i.code for i in p.issues] == ["no_quote"]


def test_links_are_confirmed_only_when_their_quote_is_found():
    edges = {(e.source, e.target): e for e in proposal().graph.edges}
    assert edges[("n4", "n2")].certainty == "confirmed"           # "which supports the hypothesis"
    assert edges[("n2", "n6")].certainty == "confirmed"
    for key in (("n2", "n1"), ("n3", "n4"), ("n5", "n4"), ("n7", "n4")):
        e = edges[key]
        assert (e.certainty, e.basis) == ("inferred", "llm_inferred")


def test_extraction_is_deterministic_and_records_the_request():
    llm = ScriptedLLM(GOOD, GOOD)
    a, b = extract(TEXT, llm), extract(TEXT, llm)
    assert a == b
    assert llm.requests[0] == request_for(TEXT) and TEXT in llm.requests[0].user
    assert a.model.request_sha256 == request_for(TEXT).sha256()


# ---------------------------------------------------------------------------
# a flawed response: corrected or dropped, always reported
# ---------------------------------------------------------------------------

def test_flawed_response_is_repaired_conservatively():
    p = proposal(FLAWED)
    codes = sorted(i.code for i in p.issues)
    assert codes == sorted(["quote_whitespace_normalized", "quote_not_found", "duplicate_ref",
                            "link_quote_not_found", "duplicate_link", "dangling_link",
                            "self_link"])
    by = nodes_by_label(p)
    h = by["Weekly irrigation raises yield"]
    assert h.basis == "source_quoted" and h.spans[0].quote == "weekly irrigation raises yield"
    r = by["Irrigated plots yielded 25% more grain"]   # misquoted number: not in the text
    assert (r.basis, r.spans) == ("llm_inferred", ())
    assert "A second item reusing the name r" not in by
    assert len(p.graph.nodes) == 3
    edges = [(e.source, e.target, e.type, e.certainty) for e in p.graph.edges]
    assert edges == [("n2", "n1", "supports", "inferred"), ("n1", "n3", "causes", "inferred")]


def test_quote_location():
    assert locate("a  b\nc", "a b c") == (0, 6, True)
    assert locate("xx abc", "abc") == (3, 6, False)
    assert locate("abc", "abd") is None and locate("abc", "   ") is None
    # only whitespace may differ: case and missing spaces mean the words were changed
    assert locate("weekly irrigation raises yield", "Weekly Irrigation raises yield") is None
    assert locate("weekly irrigation raises yield", "weeklyirrigation raises yield") is None


@pytest.mark.parametrize("raw, code", [
    ("not json at all", "malformed_output"),
    ('{"restatement": "x", "items": [', "malformed_output"),
    ('{"restatement": "x", "items": [{"ref": "a", "kind": "fact", "label": "x"}]}',
     "schema_violation"),
    ('{"restatement": "x", "items": [], "extra": 1}', "schema_violation"),
    ('{"restatement": "x", "items": []}', "empty_extraction"),
])
def test_unusable_output_is_refused_as_a_whole(raw, code):
    with pytest.raises(ExtractionError) as e:
        proposal(raw)
    assert e.value.code == code


def test_schema_violation_reports_where():
    bad = json.loads(GOOD)
    bad["items"][1]["kind"] = "fact"
    with pytest.raises(ExtractionError) as e:
        proposal(json.dumps(bad))
    assert e.value.detail["errors"][0]["loc"].startswith("items.1.kind")


def test_code_fence_is_tolerated_and_reported():
    p = proposal("```json\n" + GOOD + "\n```")
    assert "output_in_code_fence" in {i.code for i in p.issues}


def test_truncated_and_unavailable_model():
    with pytest.raises(ExtractionError) as e:
        extract(TEXT, ScriptedLLM(LLMResponse(text=GOOD, provider="p", model="m",
                                              finish_reason="length")))
    assert e.value.code == "truncated_output"
    for exc in (LLMError("rate limited"), TimeoutError("slow"), RuntimeError("boom")):
        with pytest.raises(ExtractionError) as e:
            extract(TEXT, ScriptedLLM(exc))
        assert e.value.code == "llm_unavailable"


def test_input_limits():
    for text, code in (("", "empty_input"), ("   \n", "empty_input"),
                       ("x" * (MAX_INPUT_CHARS + 1), "input_too_long")):
        with pytest.raises(ExtractionError) as e:
            extract(text, ScriptedLLM(GOOD))
        assert e.value.code == code


def test_single_unlinked_items_are_flagged():
    out = {"restatement": "r", "items": [
        {"ref": "a", "kind": "claim", "label": "x", "quote": "We want"},
        {"ref": "b", "kind": "claim", "label": "y", "quote": None}], "links": []}
    assert "nothing_linked" in {i.code for i in proposal(json.dumps(out)).issues}


# ---------------------------------------------------------------------------
# review and acceptance
# ---------------------------------------------------------------------------

def test_accept_applies_the_review():
    p = proposal()
    g, rec = accept(p, review(p, remove_nodes=("n7",), remove_edges=("x1",),
                              confirm_edges=("x2",)))
    assert "n7" not in {n.id for n in g.nodes}
    assert {e.id for e in g.edges} == {"x2", "x3", "x4", "x5"}   # x6 left with n7
    x2 = g.edge("x2")
    assert (x2.basis, x2.certainty) == ("user_stated", "confirmed")
    assert rec.removed_edges == ("x1", "x6") and rec.confirmed_edges == ("x2",)
    assert rec.graph_sha256 == g.sha256()
    Graph.model_validate_json(g.model_dump_json())


def test_accept_refuses_mismatched_or_modified_proposals():
    p = proposal()
    other = proposal(FLAWED)
    with pytest.raises(ExtractionError) as e:
        accept(p, review(other))
    assert e.value.code == "review_mismatch"
    tampered = p.model_copy(update={"restatement": "something else"})
    with pytest.raises(ExtractionError) as e:
        accept(tampered, review(tampered))
    assert e.value.code == "proposal_modified"


@pytest.mark.parametrize("kw, code", [
    ({"remove_nodes": ("n99",)}, "unknown_item"),
    ({"confirm_edges": ("x99",)}, "unknown_item"),
    ({"remove_nodes": ("n7",), "confirm_edges": ("x6",)}, "conflicting_review"),
])
def test_accept_refuses_inconsistent_reviews(kw, code):
    p = proposal()
    with pytest.raises(ExtractionError) as e:
        accept(p, review(p, **kw))
    assert e.value.code == code


def test_extracted_graph_feeds_impact_analysis():
    """End to end without HTTP: extract -> accept -> preview -> approve."""
    p = proposal()
    g, _ = accept(p, review(p))
    pv = impact.preview(g, DeleteNode(node_id="n3"))         # delete the field trial
    items = {i.node_id: (i.relation, i.certainty) for i in pv.items}
    assert items == {"n2": ("downstream", "uncertain"), "n3": ("changed", "confirmed"),
                     "n4": ("direct", "uncertain"), "n6": ("downstream", "uncertain")}
    g2, rec = impact.decide(g, pv, Decision(preview_sha256=pv.preview_sha256,
                                            decision="approve", decided_by="Dr A"))
    assert {n.id for n in g2.nodes if n.needs_review} == {"n2", "n4", "n6"}
    assert rec.graph_after_sha256 == g2.sha256()
