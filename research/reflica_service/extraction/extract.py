"""Extract a graph@1 proposal from a researcher's text, then accept it after review.

    proposal = extract(text, llm)                 # model suggests; service checks
    graph, record = accept(proposal, review)      # researcher decides what to keep

The model only names items, their kinds, links and the exact supporting words.
Everything that matters for trust is decided here, deterministically:

- A quote counts only if it is found in the input text (exactly, or with only
  whitespace differences; the stored quote is then the input's own words).
  Found -> basis `source_quoted` with its location. Not found or absent ->
  basis `llm_inferred`, and the researcher is told.
- A link is `confirmed` only if its supporting quote is found in the text;
  otherwise it is `inferred`. The model cannot mark anything confirmed.
- Links to unknown items, self-links and duplicates are dropped and reported.
- Malformed, truncated or schema-violating output is refused as a whole; no
  partial graph is produced from it.

Nothing is saved by `extract`. `accept` applies the researcher's review
(remove items or links, confirm links they vouch for) and returns the graph.
"""
from __future__ import annotations

import hashlib
import json
import re

from pydantic import BaseModel, ConfigDict, ValidationError

from ..graph.contract import (Edge, Graph, GraphError, Node, Source, SourceSpan,
                              canonical_sha256)
from .llm import LLMClient, LLMError, LLMRequest
from .schema import (ExtractionIssue, ExtractionOutput, ExtractionProposal, ModelInfo,
                     ProposalReview)

PROMPT_VERSION = "extract-text@1"
MAX_INPUT_CHARS = 20_000

SYSTEM = """You help a researcher turn their own description of a research problem into a
structured knowledge graph. You propose; the researcher decides.

Identify the items the text contains: goals, questions, hypotheses, assumptions, claims,
methods, evidence, results, limitations and tasks. Use the kind that says what the item IS.
Do not judge whether anything is true: a hypothesis stays a hypothesis, a planned task stays
a task, even if the text sounds confident.

For every item and link, give `quote`: the exact words from the text that state it, copied
character for character. If the text does not state it and you are inferring it, set quote to
null. Never invent a quote.

Links point from the influencing item to the influenced item: a change to the source may
affect the target. Read them as: "source supports target", "source causes target",
"source blocks target", "source enables target", "source informs target",
"source references target", "target requires source", "target is derived from source".
Use informs or references when one item is relevant to another but a change to it should not
change the other. Use causes only if the text explicitly states a causal relationship.

Restate the researcher's problem in one or two sentences, and list clarifying questions where
the text is ambiguous or missing something important. Return only JSON matching the schema."""

USER = "RESEARCHER'S TEXT:\n<<<\n{text}\n>>>"


class ExtractionError(GraphError):
    """Extraction could not produce a proposal. `code` is stable."""


class AcceptanceRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    proposal_sha256: str
    review: ProposalReview
    graph_sha256: str
    removed_nodes: tuple[str, ...]
    removed_edges: tuple[str, ...]   # including links of removed nodes
    confirmed_edges: tuple[str, ...]


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def request_for(text: str) -> LLMRequest:
    return LLMRequest(system=SYSTEM, user=USER.format(text=text),
                      json_schema=ExtractionOutput.model_json_schema())


def _parse(raw: str, issues: list) -> ExtractionOutput:
    s = raw.strip()
    fence = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", s, flags=re.S)
    if fence:
        s = fence.group(1)
        issues.append(ExtractionIssue(code="output_in_code_fence", severity="info",
                                      message="The model wrapped its JSON in a code fence; "
                                              "the fence was removed."))
    try:
        data = json.loads(s)
    except json.JSONDecodeError as e:
        raise ExtractionError("malformed_output", "The model's output is not valid JSON, so "
                              "nothing was extracted.", {"error": str(e)}) from None
    try:
        return ExtractionOutput.model_validate(data)
    except ValidationError as e:
        errs = [{"loc": ".".join(map(str, x["loc"])), "msg": x["msg"]} for x in e.errors()[:5]]
        raise ExtractionError("schema_violation", "The model's output does not match the "
                              "extraction schema, so nothing was extracted.",
                              {"errors": errs, "error_count": e.error_count()}) from None


def locate(text: str, quote: str) -> tuple[int, int, bool] | None:
    """(start, end, whitespace_normalized) of `quote` in `text`, or None."""
    i = text.find(quote)
    if i >= 0:
        return i, i + len(quote), False
    words = quote.split()
    if not words:
        return None
    m = re.search(r"\s+".join(map(re.escape, words)), text)
    return (m.start(), m.end(), True) if m else None


def _span(source: Source, quote: str | None, ref: str, issues: list, link: bool):
    if quote is None or not quote.strip():
        if not link:
            issues.append(ExtractionIssue(code="no_quote", severity="info", ref=ref, message=(
                "No supporting words were given; marked as inferred by the model.")))
        return None
    found = locate(source.text, quote)
    if found is None:
        issues.append(ExtractionIssue(
            code="link_quote_not_found" if link else "quote_not_found", severity="warning",
            ref=ref, message=("The quoted words do not appear in your text; marked as inferred "
                              "by the model.")))
        return None
    start, end, normalized = found
    if normalized:
        issues.append(ExtractionIssue(code="quote_whitespace_normalized", severity="info", ref=ref,
                                      message="The quote matched your text after ignoring "
                                              "whitespace differences; your exact words are kept."))
    return SourceSpan(source_id=source.id, start=start, end=end, quote=source.text[start:end])


def extract(text: str, llm: LLMClient, title: str = "Research problem") -> ExtractionProposal:
    """Ask the model for a proposal and check it. Raises ExtractionError."""
    if not text or not text.strip():
        raise ExtractionError("empty_input", "There is no text to extract from.")
    if len(text) > MAX_INPUT_CHARS:
        raise ExtractionError("input_too_long", f"The text is longer than {MAX_INPUT_CHARS} "
                              "characters; shorten it or split it.",
                              {"chars": len(text), "limit": MAX_INPUT_CHARS})
    source = Source.from_text("s1", title[:300] or "Research problem", text)
    req = request_for(text)
    try:
        resp = llm.complete(req)
    except LLMError as e:
        raise ExtractionError("llm_unavailable", f"The language model could not be used: {e}") from None
    except Exception as e:  # provider adapters may raise anything; never leak a traceback
        raise ExtractionError("llm_unavailable", "The language model could not be used "
                              f"({type(e).__name__}).") from None
    if resp.finish_reason == "length":
        raise ExtractionError("truncated_output", "The model's output was cut off before it "
                              "finished, so nothing was extracted. Try a shorter text.")
    issues: list[ExtractionIssue] = []
    out = _parse(resp.text, issues)
    if not out.items:
        raise ExtractionError("empty_extraction", "The model found nothing to extract.",
                              {"restatement": out.restatement})

    refs: dict[str, str] = {}
    nodes = []
    for item in out.items:
        if item.ref in refs:
            issues.append(ExtractionIssue(code="duplicate_ref", severity="warning", ref=item.ref,
                                          message="Two items share this name; the second was "
                                                  "dropped."))
            continue
        nid = f"n{len(nodes) + 1}"
        refs[item.ref] = nid
        span = _span(source, item.quote, item.ref, issues, link=False)
        nodes.append(Node(id=nid, kind=item.kind, label=item.label, detail=item.detail,
                          basis="source_quoted" if span else "llm_inferred",
                          spans=(span,) if span else ()))
    edges, seen = [], set()
    for k, link in enumerate(out.links):
        name = f"{link.source}->{link.target}"
        if link.source not in refs or link.target not in refs:
            issues.append(ExtractionIssue(code="dangling_link", severity="warning", ref=name,
                                          message="The link names an item that does not exist; "
                                                  "it was dropped."))
            continue
        s, t = refs[link.source], refs[link.target]
        if s == t:
            issues.append(ExtractionIssue(code="self_link", severity="warning", ref=name,
                                          message="A link from an item to itself was dropped."))
            continue
        if (s, t, link.type) in seen:
            issues.append(ExtractionIssue(code="duplicate_link", severity="info", ref=name,
                                          message="A repeated link was dropped."))
            continue
        seen.add((s, t, link.type))
        span = _span(source, link.quote, name, issues, link=True)
        edges.append(Edge(id=f"x{len(edges) + 1}", source=s, target=t, type=link.type,
                          certainty="confirmed" if span else "inferred",
                          basis="source_quoted" if span else "llm_inferred",
                          spans=(span,) if span else ()))
    if len(nodes) > 1 and not edges:
        issues.append(ExtractionIssue(code="nothing_linked", severity="info", message=(
            "No relationships were found between the items; impact analysis will have nothing "
            "to follow until you add links.")))
    graph = Graph(sources=(source,), nodes=tuple(nodes), edges=tuple(edges))
    draft = ExtractionProposal(
        source=source, restatement=out.restatement,
        clarifying_questions=tuple(out.clarifying_questions), graph=graph, refs=refs,
        issues=tuple(issues),
        model=ModelInfo(provider=resp.provider, model=resp.model, prompt_version=PROMPT_VERSION,
                        request_sha256=req.sha256(), response_sha256=_sha(resp.text)),
        proposal_sha256="0" * 64)
    return draft.model_copy(update={"proposal_sha256": proposal_hash(draft)})


def proposal_hash(p: ExtractionProposal) -> str:
    return canonical_sha256(p, exclude={"proposal_sha256"})


def accept(proposal: ExtractionProposal, review: ProposalReview) -> tuple[Graph, AcceptanceRecord]:
    """Apply the researcher's review to an unmodified proposal and return the graph."""
    if proposal_hash(proposal) != proposal.proposal_sha256:
        raise ExtractionError("proposal_modified", "The proposal's contents do not match its "
                              "fingerprint; it was changed after extraction.")
    if review.proposal_sha256 != proposal.proposal_sha256:
        raise ExtractionError("review_mismatch", "The review is for a different proposal.")
    g = proposal.graph
    node_ids, edge_ids = {n.id for n in g.nodes}, {e.id for e in g.edges}
    unknown = sorted((set(review.remove_nodes) - node_ids)
                     | ((set(review.remove_edges) | set(review.confirm_edges)) - edge_ids))
    if unknown:
        raise ExtractionError("unknown_item", "The review names items that are not in the "
                              "proposal.", {"ids": unknown})
    drop_n = set(review.remove_nodes)
    drop_e = set(review.remove_edges) | {e.id for e in g.edges
                                         if e.source in drop_n or e.target in drop_n}
    conflict = sorted(set(review.confirm_edges) & drop_e)
    if conflict:
        raise ExtractionError("conflicting_review", "A link cannot be both confirmed and "
                              "removed (removing an item removes its links).", {"ids": conflict})
    edges = []
    for e in g.edges:
        if e.id in drop_e:
            continue
        if e.id in review.confirm_edges:
            e = Edge.model_validate({**e.model_dump(), "basis": "user_stated",
                                     "certainty": "confirmed"})
        edges.append(e)
    graph = Graph(sources=g.sources, nodes=tuple(n for n in g.nodes if n.id not in drop_n),
                  edges=tuple(edges))
    record = AcceptanceRecord(proposal_sha256=proposal.proposal_sha256, review=review,
                              graph_sha256=graph.sha256(),
                              removed_nodes=tuple(sorted(drop_n)),
                              removed_edges=tuple(sorted(drop_e)),
                              confirmed_edges=tuple(sorted(review.confirm_edges)))
    return graph, record
