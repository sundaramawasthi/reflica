"""HTTP API (v1) for the Reflica app: extraction proposals, impact preview, decisions.

FastAPI is an optional dependency (the `service` extra), so it must only be
imported inside functions, never at module import time.

    app = create_app(llm=some_client)     # llm=None: extraction answers 503

The API is stateless: the client sends the graph it holds and receives the
new graph and a record; nothing is stored here. Every endpoint returns either
its documented body or {"error": {"code", "message", "detail"}} with a stable
code. It binds to 127.0.0.1 by default and allows browser calls only from
localhost origins (the Flutter web app during development).
"""
# No `from __future__ import annotations`: FastAPI must evaluate the endpoint
# annotations, whose models are imported inside create_app.
from . import __version__
from .extraction.llm import LLMClient
from .graph.contract import VERSION as GRAPH_VERSION
from .graph.contract import GraphError
from .models import ServiceConfig

CONFLICT = {"graph_changed", "decision_mismatch", "preview_mismatch", "preview_modified",
            "proposal_modified", "review_mismatch"}
UPSTREAM = {"llm_unavailable", "truncated_output", "malformed_output", "schema_violation",
            "empty_extraction"}
LOCAL_ORIGINS = r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$"


def status_for(code: str) -> int:
    if code == "llm_not_configured":
        return 503
    if code in UPSTREAM:
        return 502
    if code in CONFLICT:
        return 409
    return 422


def create_app(llm: LLMClient | None = None, config: ServiceConfig | None = None):
    from fastapi import FastAPI, Request
    from fastapi.exceptions import RequestValidationError
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse

    from .api_models import (AcceptRequest, AcceptResponse, DecideRequest, DecideResponse,
                             ErrorResponse, ExtractRequest, Health, LegacyImportRequest,
                             PreviewRequest)
    from .extraction.extract import ExtractionError, accept, extract
    from .extraction.schema import ExtractionProposal
    from .graph import impact
    from .graph.contract import ImpactPreview
    from .graph.legacy import LegacyImport, import_app_plan

    config = config or ServiceConfig()
    app = FastAPI(title="Reflica service", version=__version__,
                  responses={409: {"model": ErrorResponse}, 422: {"model": ErrorResponse},
                             502: {"model": ErrorResponse}, 503: {"model": ErrorResponse}})
    app.add_middleware(CORSMiddleware, allow_origin_regex=LOCAL_ORIGINS,
                       allow_methods=["GET", "POST"], allow_headers=["Content-Type"])

    def error(status: int, code: str, message: str, detail: dict | None = None):
        return JSONResponse(status_code=status, content={
            "error": {"code": code, "message": message, "detail": detail or {}}})

    @app.middleware("http")
    async def limit_size(request: Request, call_next):
        size = request.headers.get("content-length")
        if size is not None and size.isdigit() and int(size) > config.max_upload_bytes:
            return error(413, "too_large", "Request body exceeds the size limit.",
                         {"bytes": int(size), "limit": config.max_upload_bytes})
        return await call_next(request)

    @app.exception_handler(GraphError)
    async def graph_error(_request, exc: GraphError):
        return error(status_for(exc.code), exc.code, exc.message, exc.detail)

    @app.exception_handler(RequestValidationError)
    async def invalid_request(_request, exc: RequestValidationError):
        errs = [{"loc": ".".join(map(str, e["loc"])), "msg": e["msg"]} for e in exc.errors()[:10]]
        return error(422, "invalid_request", "The request does not match the API contract.",
                     {"errors": errs, "error_count": len(exc.errors())})

    @app.get("/v1/health", response_model=Health)
    def health():
        return Health(service_version=__version__, graph_version=GRAPH_VERSION,
                      llm=f"{llm.provider}/{llm.model}" if llm is not None else None)

    @app.post("/v1/extract", response_model=ExtractionProposal)
    def extract_endpoint(body: ExtractRequest):
        if llm is None:
            raise ExtractionError("llm_not_configured", "No language model is configured, so "
                                  "text cannot be extracted. Graphs can still be edited.")
        return extract(body.text, llm, body.title)

    @app.post("/v1/extract/accept", response_model=AcceptResponse)
    def accept_endpoint(body: AcceptRequest):
        graph, record = accept(body.proposal, body.review)
        return AcceptResponse(graph=graph, record=record)

    @app.post("/v1/impact/preview", response_model=ImpactPreview)
    def preview_endpoint(body: PreviewRequest):
        return impact.preview(body.graph, body.change)

    @app.post("/v1/impact/decide", response_model=DecideResponse)
    def decide_endpoint(body: DecideRequest):
        graph, record = impact.decide(body.graph, body.preview, body.decision)
        return DecideResponse(graph=graph, record=record)

    @app.post("/v1/legacy/import", response_model=LegacyImport)
    def legacy_endpoint(body: LegacyImportRequest):
        return import_app_plan(body.plan)

    return app


def main() -> None:  # pragma: no cover - manual use: python -m reflica_service.app
    import uvicorn
    config = ServiceConfig()
    uvicorn.run(create_app(config=config), host=config.host, port=config.port)


if __name__ == "__main__":  # pragma: no cover
    main()
