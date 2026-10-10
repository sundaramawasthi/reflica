"""Write real API responses (offline, scripted model) as fixtures for the Flutter tests.

    python tests/service/make_dart_fixtures.py        (run from research/)

`test_dart_fixtures_are_current` fails if the fixtures drift from what the
service actually returns, so the Dart tests always parse genuine responses.
"""
from __future__ import annotations

import json
import sys
import warnings
from pathlib import Path

RESEARCH = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RESEARCH))
OUT = RESEARCH.parent / "test" / "fixtures"
DATA = RESEARCH / "tests" / "service" / "data" / "extraction"


def responses() -> dict[str, object]:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        from fastapi.testclient import TestClient
    from reflica_service.app import create_app
    from reflica_service.extraction.llm import ScriptedLLM

    text = (DATA / "input.txt").read_text()
    c = TestClient(create_app(llm=ScriptedLLM((DATA / "good_response.json").read_text())))
    out: dict[str, object] = {}
    proposal = c.post("/v1/extract", json={"text": text, "title": "Irrigation"}).json()
    out["proposal.json"] = proposal
    review = {"proposal_sha256": proposal["proposal_sha256"], "decided_by": "uid-demo",
              "remove_nodes": ["n7"], "remove_edges": [], "confirm_edges": ["x2"]}
    out["accept_request.json"] = {"proposal": proposal, "review": review}
    accepted = c.post("/v1/extract/accept", json={"proposal": proposal, "review": review}).json()
    out["accept_response.json"] = accepted
    graph = accepted["graph"]
    change = {"op": "delete_node", "node_id": "n3"}
    preview = c.post("/v1/impact/preview", json={"graph": graph, "change": change}).json()
    out["preview_delete_n3.json"] = preview
    decision = {"preview_sha256": preview["preview_sha256"], "decision": "approve",
                "decided_by": "uid-demo", "note": None}
    out["decide_approve.json"] = c.post("/v1/impact/decide", json={
        "graph": graph, "preview": preview, "decision": decision}).json()
    out["decide_reject.json"] = c.post("/v1/impact/decide", json={
        "graph": graph, "preview": preview, "decision": {**decision, "decision": "reject"}}).json()
    out["error_graph_changed.json"] = c.post("/v1/impact/decide", json={
        "graph": out["decide_approve.json"]["graph"], "preview": preview,
        "decision": decision}).json()
    return out


def render(obj) -> str:
    return json.dumps(obj, indent=1, ensure_ascii=False) + "\n"


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for name, obj in responses().items():
        (OUT / name).write_text(render(obj))
        print("wrote", OUT / name)
