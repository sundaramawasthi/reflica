"""Request and response bodies of the HTTP API (v1). No FastAPI import here."""
from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from .extraction.extract import AcceptanceRecord
from .extraction.schema import ExtractionProposal, ProposalReview
from .graph.contract import Change, ChangeRecord, Decision, Graph, ImpactPreview

_REQ = ConfigDict(extra="forbid", frozen=True)


class ExtractRequest(BaseModel):
    model_config = _REQ
    text: str = Field(max_length=200_000)   # the extractor applies its own, smaller limit
    title: str = Field(default="Research problem", min_length=1, max_length=300)


class AcceptRequest(BaseModel):
    model_config = _REQ
    proposal: ExtractionProposal
    review: ProposalReview


class AcceptResponse(BaseModel):
    model_config = _REQ
    graph: Graph
    record: AcceptanceRecord


class PreviewRequest(BaseModel):
    model_config = _REQ
    graph: Graph
    change: Change


class DecideRequest(BaseModel):
    model_config = _REQ
    graph: Graph
    preview: ImpactPreview
    decision: Decision


class DecideResponse(BaseModel):
    model_config = _REQ
    graph: Graph
    record: ChangeRecord


class LegacyImportRequest(BaseModel):
    model_config = _REQ
    plan: dict[str, Any]   # the app's Plan JSON (app-plan@0)


class ErrorBody(BaseModel):
    model_config = _REQ
    code: str
    message: str
    detail: dict[str, Any] = {}


class ErrorResponse(BaseModel):
    model_config = _REQ
    error: ErrorBody


class Health(BaseModel):
    model_config = _REQ
    status: Literal["ok"] = "ok"
    service_version: str
    graph_version: str
    llm: str | None   # "provider/model", or None when extraction is not configured
