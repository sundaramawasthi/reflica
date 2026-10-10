"""HTTP API v1, in-process (FastAPI TestClient). Offline: the model is a scripted fake."""
from __future__ import annotations

import json
import warnings
from pathlib import Path

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx")
with warnings.catch_warnings():  # starlette suggests httpx2; httpx works
    warnings.simplefilter("ignore")
    from fastapi.testclient import TestClient

from reflica_service.app import create_app, status_for  # noqa: E402
from reflica_service.extraction.llm import ScriptedLLM  # noqa: E402
from reflica_service.models import ServiceConfig  # noqa: E402

DATA = Path(__file__).parent / "data" / "extraction"
TEXT = (DATA / "input.txt").read_text()
GOOD = (DATA / "good_response.json").read_text()
pytestmark = pytest.mark.filterwarnings("ignore::DeprecationWarning")


def client(*responses, **kw):
    return TestClient(create_app(llm=ScriptedLLM(*responses) if responses else None, **kw))


def err(r, status, code):
    assert r.status_code == status, r.text
    assert r.json()["error"]["code"] == code
    return r.json()["error"]


def test_health():
    assert client(GOOD).get("/v1/health").json() == {
        "status": "ok", "service_version": "0.0.1", "graph_version": "graph@1",
        "llm": "scripted/scripted-v1"}
    assert client().get("/v1/health").json()["llm"] is None


def test_full_workflow_over_http():
    """Enter text -> proposal -> review -> edit preview -> approve -> flagged dependents."""
    c = client(GOOD)
    prop = c.post("/v1/extract", json={"text": TEXT, "title": "Irrigation"}).json()
    assert prop["version"] == "extraction@1" and len(prop["graph"]["nodes"]) == 7
    acc = c.post("/v1/extract/accept", json={"proposal": prop, "review": {
        "proposal_sha256": prop["proposal_sha256"], "decided_by": "Dr A",
        "remove_nodes": ["n7"]}})
    assert acc.status_code == 200
    graph = acc.json()["graph"]
    pv = c.post("/v1/impact/preview", json={"graph": graph, "change": {
        "op": "edit_node", "node_id": "n2", "label": "Weekly irrigation is associated with yield"}})
    assert pv.status_code == 200
    preview = pv.json()
    assert {i["node_id"]: i["certainty"] for i in preview["items"]} == {
        "n2": "confirmed", "n6": "confirmed"}
    assert preview["related_unaffected"] == ["n1"]                  # linked only by "informs"
    dec = c.post("/v1/impact/decide", json={"graph": graph, "preview": preview, "decision": {
        "preview_sha256": preview["preview_sha256"], "decision": "approve",
        "decided_by": "Dr A"}})
    assert dec.status_code == 200
    out = dec.json()
    flagged = [n["id"] for n in out["graph"]["nodes"] if n["reviews"]]
    assert flagged == ["n6"]
    assert out["record"]["graph_after_sha256"] != out["record"]["graph_before_sha256"]
    # the same preview cannot be applied twice: the graph has moved on
    again = c.post("/v1/impact/decide", json={"graph": out["graph"], "preview": preview,
                                              "decision": {"preview_sha256": preview["preview_sha256"],
                                                           "decision": "approve",
                                                           "decided_by": "Dr A"}})
    err(again, 409, "graph_changed")


def test_reject_over_http_returns_the_same_graph():
    c = client(GOOD)
    prop = c.post("/v1/extract", json={"text": TEXT}).json()
    graph = c.post("/v1/extract/accept", json={"proposal": prop, "review": {
        "proposal_sha256": prop["proposal_sha256"], "decided_by": "Dr A"}}).json()["graph"]
    preview = c.post("/v1/impact/preview", json={"graph": graph, "change": {
        "op": "delete_node", "node_id": "n3"}}).json()
    out = c.post("/v1/impact/decide", json={"graph": graph, "preview": preview, "decision": {
        "preview_sha256": preview["preview_sha256"], "decision": "reject",
        "decided_by": "Dr A"}}).json()
    assert out["graph"] == graph and out["record"]["decision"]["decision"] == "reject"


def test_extraction_errors_map_to_stable_codes():
    err(client().post("/v1/extract", json={"text": TEXT}), 503, "llm_not_configured")
    err(client("not json").post("/v1/extract", json={"text": TEXT}), 502, "malformed_output")
    err(client(GOOD).post("/v1/extract", json={"text": "  "}), 422, "empty_input")


def test_request_validation_uses_the_error_envelope():
    e = err(client(GOOD).post("/v1/impact/preview", json={"graph": {}, "change": {
        "op": "explode"}}), 422, "invalid_request")
    assert e["detail"]["error_count"] >= 1
    err(client(GOOD).post("/v1/extract", json={"text": TEXT, "surprise": 1}), 422,
        "invalid_request")


def test_contract_violations_in_a_graph_are_refused():
    graph = {"nodes": [{"id": "a", "kind": "claim", "label": "A", "basis": "user_stated"}],
             "edges": [{"id": "e", "source": "a", "target": "b", "type": "supports",
                        "certainty": "confirmed", "basis": "llm_inferred"}]}
    e = err(client().post("/v1/impact/preview", json={"graph": graph, "change": {
        "op": "delete_node", "node_id": "a"}}), 422, "invalid_request")
    assert "must be 'inferred'" in json.dumps(e)


def test_graph_errors_map_to_stable_codes():
    graph = {"nodes": [{"id": "a", "kind": "claim", "label": "A", "basis": "user_stated"}]}
    err(client().post("/v1/impact/preview", json={"graph": graph, "change": {
        "op": "delete_node", "node_id": "zz"}}), 422, "unknown_node")
    assert status_for("decision_mismatch") == 409 and status_for("llm_unavailable") == 502


def test_legacy_import_endpoint():
    from tests.service.test_legacy import SCAFFOLD_PLAN
    r = client().post("/v1/legacy/import", json={"plan": SCAFFOLD_PLAN})
    assert r.status_code == 200
    body = r.json()
    assert body["template_scaffold"] is True
    assert {n["basis"] for n in body["graph"]["nodes"]} == {"legacy_unverified"}


def test_body_size_limit():
    c = client(GOOD, config=ServiceConfig(max_upload_bytes=1000))
    err(c.post("/v1/extract", json={"text": "x" * 2000}), 413, "too_large")


def test_cors_allows_only_local_origins():
    c = client()
    ok = c.options("/v1/health", headers={"Origin": "http://localhost:5000",
                                          "Access-Control-Request-Method": "GET"})
    assert ok.headers.get("access-control-allow-origin") == "http://localhost:5000"
    bad = c.options("/v1/health", headers={"Origin": "https://example.com",
                                           "Access-Control-Request-Method": "GET"})
    assert "access-control-allow-origin" not in bad.headers


def test_dart_fixtures_are_current():
    """The Flutter tests parse these files; they must equal real API output."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "make_dart_fixtures", Path(__file__).parent / "make_dart_fixtures.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    for name, obj in mod.responses().items():
        assert (mod.OUT / name).read_text() == mod.render(obj), name
    err = json.loads((mod.OUT / "error_graph_changed.json").read_text())
    assert err["error"]["code"] == "graph_changed"
