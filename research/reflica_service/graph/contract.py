"""graph@1 — the shared, versioned knowledge-graph contract.

One representation for the app, the service and the research code. The
JSON Schema exported from these models (`graph@1.schema.json`, checked by
tests) is what other clients validate against.

Two questions are kept apart on purpose:

- `kind`  — what an item IS (a hypothesis, a claim, a result, ...).
- `basis` — where the item CAME FROM (stated by the user, quoted from a
  source, inferred by a language model, computed by an analysis).

Neither says the item is true. A hypothesis quoted from a paper is still a
hypothesis; only the researcher changes its kind. An item whose basis is
`llm_inferred` is a suggestion until the researcher confirms it.

Edges point from the influencing item to the influenced item: a change to
`source` may affect `target`. Read each type as
    supports, causes, blocks, enables, informs, references: "source <type> target"
    requires:      "target requires source"
    derived_from:  "target is derived from source"
This is the benchmark's convention (e.g. supplier --requires--> task).
`informs` and `references` record a relationship that does not carry a
change forward; the other six do (PROPAGATING).

`certainty` says whether a link is established (`confirmed`: stated by the
user or quoted from a source) or only suggested (`inferred`).
"""
from __future__ import annotations

import hashlib
import json
from typing import Annotated, Literal, Union

from pydantic import BaseModel, ConfigDict, Field, model_validator

VERSION = "graph@1"

_STRICT = ConfigDict(extra="forbid", frozen=True)
Id = Annotated[str, Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,63}$")]
Sha256 = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]

MAX_SOURCE_CHARS = 200_000
MAX_NODES = 2_000
MAX_EDGES = 10_000

NodeKind = Literal["goal", "question", "hypothesis", "assumption", "claim", "method",
                   "evidence", "result", "limitation", "task"]
Basis = Literal["user_stated", "source_quoted", "llm_inferred", "computed"]
EdgeType = Literal["requires", "supports", "causes", "blocks", "enables", "derived_from",
                   "informs", "references"]
PROPAGATING: frozenset[str] = frozenset(
    {"requires", "supports", "causes", "blocks", "enables", "derived_from"})
Certainty = Literal["confirmed", "inferred"]
ESTABLISHED_BASES: frozenset[str] = frozenset({"user_stated", "source_quoted"})


class GraphError(ValueError):
    """A graph or change violates the contract. `code` is stable; `message` is plain language."""

    def __init__(self, code: str, message: str, detail: dict | None = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.detail = detail or {}


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonical_sha256(model: BaseModel, exclude: set[str] | None = None) -> str:
    """SHA-256 of a model's canonical JSON (sorted keys, no whitespace)."""
    blob = json.dumps(model.model_dump(mode="json", exclude=exclude), sort_keys=True,
                      separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# sources and provenance
# ---------------------------------------------------------------------------

class Source(BaseModel):
    """Text the graph was built from. Quotes are checked against it."""

    model_config = _STRICT

    id: Id
    title: str = Field(min_length=1, max_length=300)
    media_type: Literal["text/plain"] = "text/plain"
    text: str = Field(max_length=MAX_SOURCE_CHARS)
    sha256: Sha256

    @model_validator(mode="after")
    def _hash_matches(self):
        if sha256_text(self.text) != self.sha256:
            raise ValueError("sha256 does not match text")
        return self

    @classmethod
    def from_text(cls, id: str, title: str, text: str) -> "Source":
        return cls(id=id, title=title, text=text, sha256=sha256_text(text))


class SourceSpan(BaseModel):
    """A verbatim passage: source.text[start:end] == quote (checked by Graph)."""

    model_config = _STRICT

    source_id: Id
    start: int = Field(ge=0)
    end: int = Field(gt=0)
    quote: str = Field(min_length=1, max_length=4000)

    @model_validator(mode="after")
    def _length(self):
        if self.end - self.start != len(self.quote):
            raise ValueError("end - start must equal len(quote)")
        return self


class ReviewNote(BaseModel):
    """Why a node needs the researcher's review after an approved change."""

    model_config = _STRICT

    change_sha256: Sha256  # the approved impact preview that raised it
    reason: str = Field(min_length=1, max_length=2000)


class Confidence(BaseModel):
    model_config = _STRICT

    value: float = Field(ge=0.0, le=1.0)
    stated_by: Literal["user", "llm_estimate", "analysis"]


# ---------------------------------------------------------------------------
# nodes and edges
# ---------------------------------------------------------------------------

def _check_basis(basis: str, spans: tuple, run_id: str | None, what: str) -> None:
    if basis == "source_quoted" and not spans:
        raise ValueError(f"{what} with basis 'source_quoted' needs at least one source span")
    if basis == "computed" and not run_id:
        raise ValueError(f"{what} with basis 'computed' needs the run_id of the analysis")


class Node(BaseModel):
    model_config = _STRICT

    id: Id
    kind: NodeKind
    label: str = Field(min_length=1, max_length=300)
    detail: str | None = Field(default=None, max_length=4000)
    basis: Basis
    spans: tuple[SourceSpan, ...] = ()       # provenance; required for source_quoted
    run_id: str | None = Field(default=None, max_length=200)  # required for computed
    confidence: Confidence | None = None
    reviews: tuple[ReviewNote, ...] = ()     # non-empty = needs review

    @model_validator(mode="after")
    def _basis(self):
        _check_basis(self.basis, self.spans, self.run_id, "node")
        return self

    @property
    def needs_review(self) -> bool:
        return bool(self.reviews)


class Edge(BaseModel):
    model_config = _STRICT

    id: Id
    source: Id
    target: Id
    type: EdgeType
    certainty: Certainty
    basis: Basis
    spans: tuple[SourceSpan, ...] = ()
    run_id: str | None = Field(default=None, max_length=200)
    note: str | None = Field(default=None, max_length=2000)

    @model_validator(mode="after")
    def _rules(self):
        if self.source == self.target:
            raise ValueError("an edge cannot link a node to itself")
        _check_basis(self.basis, self.spans, self.run_id, "edge")
        if self.certainty == "confirmed" and self.basis not in ESTABLISHED_BASES:
            raise ValueError("only user-stated or source-quoted links can be 'confirmed'; "
                             f"a link with basis '{self.basis}' must be 'inferred'")
        return self

    @property
    def propagates(self) -> bool:
        return self.type in PROPAGATING


class Graph(BaseModel):
    model_config = _STRICT

    version: Literal["graph@1"] = VERSION
    sources: tuple[Source, ...] = ()
    nodes: tuple[Node, ...] = Field(default=(), max_length=MAX_NODES)
    edges: tuple[Edge, ...] = Field(default=(), max_length=MAX_EDGES)

    @model_validator(mode="after")
    def _integrity(self):
        problems: list[str] = []
        ids = [s.id for s in self.sources]
        if len(set(ids)) != len(ids):
            problems.append("duplicate source ids")
        node_ids = [n.id for n in self.nodes]
        edge_ids = [e.id for e in self.edges]
        if len(set(node_ids)) != len(node_ids):
            problems.append("duplicate node ids")
        if len(set(edge_ids)) != len(edge_ids):
            problems.append("duplicate edge ids")
        if set(node_ids) & set(edge_ids):
            problems.append("a node and an edge share an id")
        known = set(node_ids)
        for e in self.edges:
            if e.source not in known or e.target not in known:
                problems.append(f"edge {e.id} links a node that does not exist")
        sources = {s.id: s for s in self.sources}
        for owner in (*self.nodes, *self.edges):
            for sp in owner.spans:
                src = sources.get(sp.source_id)
                if src is None:
                    problems.append(f"{owner.id}: span cites unknown source {sp.source_id}")
                elif src.text[sp.start:sp.end] != sp.quote:
                    problems.append(f"{owner.id}: quote is not verbatim at {sp.start}:{sp.end} "
                                    f"of {sp.source_id}")
        if problems:
            raise ValueError("; ".join(problems))
        return self

    def node(self, node_id: str) -> Node | None:
        return next((n for n in self.nodes if n.id == node_id), None)

    def edge(self, edge_id: str) -> Edge | None:
        return next((e for e in self.edges if e.id == edge_id), None)

    def sha256(self) -> str:
        return canonical_sha256(self)


# ---------------------------------------------------------------------------
# changes the researcher can propose
# ---------------------------------------------------------------------------

class AddNode(BaseModel):
    model_config = _STRICT
    op: Literal["add_node"] = "add_node"
    node: Node


class EditNode(BaseModel):
    """Change a node's wording or kind. Fields left None stay as they are.

    Editing the label or detail makes the content the researcher's own: the
    node's basis becomes `user_stated` (its source spans are kept as references).
    """

    model_config = _STRICT
    op: Literal["edit_node"] = "edit_node"
    node_id: Id
    label: str | None = Field(default=None, min_length=1, max_length=300)
    detail: str | None = Field(default=None, max_length=4000)
    kind: NodeKind | None = None


class DeleteNode(BaseModel):
    model_config = _STRICT
    op: Literal["delete_node"] = "delete_node"
    node_id: Id


class AddEdge(BaseModel):
    model_config = _STRICT
    op: Literal["add_edge"] = "add_edge"
    edge: Edge


class DeleteEdge(BaseModel):
    model_config = _STRICT
    op: Literal["delete_edge"] = "delete_edge"
    edge_id: Id


class ChangeEdgeType(BaseModel):
    """Re-type a link. The researcher asserts it, so it becomes user-stated and confirmed."""

    model_config = _STRICT
    op: Literal["change_edge_type"] = "change_edge_type"
    edge_id: Id
    new_type: EdgeType


class ResolveReview(BaseModel):
    """The researcher has reviewed a flagged node; clears its review notes."""

    model_config = _STRICT
    op: Literal["resolve_review"] = "resolve_review"
    node_id: Id


Change = Annotated[Union[AddNode, EditNode, DeleteNode, AddEdge, DeleteEdge, ChangeEdgeType,
                         ResolveReview], Field(discriminator="op")]


# ---------------------------------------------------------------------------
# impact preview, decision and record
# ---------------------------------------------------------------------------

class ImpactItem(BaseModel):
    """A node that may be affected by the change, and why."""

    model_config = _STRICT

    node_id: Id
    relation: Literal["changed", "direct", "downstream"]
    # confirmed: reachable through confirmed links only; uncertain: every path
    # from the change passes through at least one inferred link
    certainty: Literal["confirmed", "uncertain"]
    path: tuple[Id, ...]  # edge ids from the change to this node (empty for the changed node)
    explanation: str


class ProposedUpdate(BaseModel):
    model_config = _STRICT

    action: Literal["add_node", "edit_node", "delete_node", "add_edge", "delete_edge",
                    "change_edge_type", "flag_for_review", "resolve_review"]
    target: Id
    description: str


class ImpactPreview(BaseModel):
    """What a change would do. Nothing is applied until this exact preview is approved."""

    model_config = _STRICT

    version: Literal["impact@1"] = "impact@1"
    analyzer: str            # e.g. "link_following@1"
    graph_sha256: Sha256     # the graph the preview was computed on
    change: Change
    items: tuple[ImpactItem, ...]
    unaffected: tuple[Id, ...]           # nodes no propagating link reaches
    related_unaffected: tuple[Id, ...]   # linked to an affected node only by informs/references
    proposed_updates: tuple[ProposedUpdate, ...]
    limitations: tuple[str, ...]
    preview_sha256: Sha256

    def fingerprint(self) -> str:
        return canonical_sha256(self, exclude={"preview_sha256"})


class Decision(BaseModel):
    """The researcher's decision on one specific preview."""

    model_config = _STRICT

    preview_sha256: Sha256
    decision: Literal["approve", "reject"]
    decided_by: Annotated[str, Field(min_length=1, max_length=200, pattern=r"\S")]
    note: str | None = Field(default=None, max_length=2000)


class ChangeRecord(BaseModel):
    """Reproducible record of a decided change (approved or rejected)."""

    model_config = _STRICT

    preview: ImpactPreview
    decision: Decision
    graph_before_sha256: Sha256
    graph_after_sha256: Sha256  # equal to before when rejected


def json_schema() -> dict:
    """JSON Schemas for every graph@1 message, for non-Python clients."""
    from pydantic import TypeAdapter
    return {"version": VERSION,
            "Graph": Graph.model_json_schema(),
            "Change": TypeAdapter(Change).json_schema(),
            "ImpactPreview": ImpactPreview.model_json_schema(),
            "Decision": Decision.model_json_schema(),
            "ChangeRecord": ChangeRecord.model_json_schema()}
