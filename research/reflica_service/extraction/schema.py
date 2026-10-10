"""What the model must return, and the proposal the researcher reviews.

The model never chooses ids, offsets, basis or certainty: it names items with
short refs and gives the exact supporting words (`quote`). The service
locates each quote in the input, assigns ids, and decides basis and
certainty deterministically (see extract.py).
"""
from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

from ..graph.contract import EdgeType, Graph, NodeKind, Sha256, Source

_IN = ConfigDict(extra="forbid")          # model output: strict, but not frozen
_OUT = ConfigDict(extra="forbid", frozen=True)
Ref = Annotated[str, Field(min_length=1, max_length=40)]


class ExtractedItem(BaseModel):
    model_config = _IN

    ref: Ref = Field(description="Short unique name for this item, e.g. 'h1'")
    kind: NodeKind = Field(description="What the item is. A hypothesis stays a hypothesis even "
                                       "if the text asserts it confidently.")
    label: str = Field(min_length=1, max_length=300, description="Short statement of the item")
    detail: str | None = Field(default=None, max_length=2000)
    quote: str | None = Field(default=None, max_length=2000,
                              description="Exact words from the text that state this item; "
                                          "null if the item is your own inference")


class ExtractedLink(BaseModel):
    model_config = _IN

    source: Ref = Field(description="ref of the influencing item")
    target: Ref = Field(description="ref of the influenced item")
    type: EdgeType = Field(description="requires: target requires source; derived_from: target "
                                       "is derived from source; otherwise 'source <type> target'")
    quote: str | None = Field(default=None, max_length=2000,
                              description="Exact words from the text that state this "
                                          "relationship; null if inferred")


class ExtractionOutput(BaseModel):
    model_config = _IN

    restatement: str = Field(min_length=1, max_length=2000,
                             description="One or two sentences restating the researcher's "
                                         "problem or goal, for them to confirm")
    items: list[ExtractedItem] = Field(max_length=200)
    links: list[ExtractedLink] = Field(default_factory=list, max_length=500)
    clarifying_questions: list[Annotated[str, Field(max_length=500)]] = Field(
        default_factory=list, max_length=10,
        description="Questions to ask where the text is ambiguous or incomplete")


Severity = Literal["info", "warning"]


class ExtractionIssue(BaseModel):
    """Something the service corrected or dropped. The researcher sees all of them."""

    model_config = _OUT

    code: Literal["quote_not_found", "quote_whitespace_normalized", "no_quote",
                  "link_quote_not_found", "duplicate_ref", "dangling_link", "self_link",
                  "duplicate_link", "output_in_code_fence", "nothing_linked"]
    severity: Severity
    message: str
    ref: str | None = None


class ModelInfo(BaseModel):
    model_config = _OUT

    provider: str
    model: str
    prompt_version: str
    request_sha256: Sha256
    response_sha256: Sha256


class ExtractionProposal(BaseModel):
    """A suggested graph. Not saved: the researcher reviews, edits and accepts it."""

    model_config = _OUT

    version: Literal["extraction@1"] = "extraction@1"
    source: Source
    restatement: str
    clarifying_questions: tuple[str, ...]
    graph: Graph                       # proposed nodes/edges with basis and certainty set
    refs: dict[str, str]               # model ref -> node id
    issues: tuple[ExtractionIssue, ...]
    model: ModelInfo
    proposal_sha256: Sha256


class ProposalReview(BaseModel):
    """The researcher's decision on a proposal: which items to keep, which links to confirm."""

    model_config = _OUT

    proposal_sha256: Sha256
    decided_by: Annotated[str, Field(min_length=1, max_length=200, pattern=r"\S")]
    remove_nodes: tuple[str, ...] = ()       # their links are removed too
    remove_edges: tuple[str, ...] = ()
    confirm_edges: tuple[str, ...] = ()      # researcher vouches: becomes user_stated, confirmed
