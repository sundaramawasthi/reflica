"""Legacy app plans (app-plan@0) -> graph@1, without inventing provenance."""
from __future__ import annotations

import pytest

from reflica_service.graph.contract import GraphError
from reflica_service.graph.legacy import import_app_plan

# Exactly what PlanRepository._bootstrapNodes/_bootstrapEdges save for a new plan
SCAFFOLD_PLAN = {
    "id": "p1", "title": "Irrigation study",
    "nodes": [
        {"id": "goal", "label": "Irrigation study", "subLabel": "goal · Researchers",
         "type": "fact", "x": 0.5, "y": 0.14, "confidence": 1.0, "source": "user"},
        {"id": "situation", "label": "Situation", "subLabel": "observation",
         "type": "observation", "x": 0.22, "y": 0.45, "confidence": 0.85},
        {"id": "resources", "label": "Resources", "subLabel": "facts", "type": "fact",
         "x": 0.78, "y": 0.45, "confidence": 0.9},
        {"id": "constraints", "label": "Constraints", "subLabel": "facts", "type": "fact",
         "x": 0.5, "y": 0.62, "confidence": 0.9},
        {"id": "risks", "label": "Risks", "subLabel": "hypothesis", "type": "hypothesis",
         "x": 0.25, "y": 0.80, "confidence": 0.6},
        {"id": "plan", "label": "Proposed plan", "subLabel": "prediction", "type": "prediction",
         "x": 0.75, "y": 0.80, "confidence": 0.7},
    ],
    "edges": [
        {"fromId": "situation", "toId": "goal", "kind": "supports"},
        {"fromId": "resources", "toId": "goal", "kind": "enables"},
        {"fromId": "constraints", "toId": "plan", "kind": "requires"},
        {"fromId": "risks", "toId": "plan", "kind": "blocks"},
        {"fromId": "plan", "toId": "goal", "kind": "causes"},
        {"fromId": "situation", "toId": "plan", "kind": "supports"},
        {"fromId": "resources", "toId": "plan", "kind": "supports"},
    ],
}


def test_kind_mapping_preserves_the_original_type():
    imp = import_app_plan(SCAFFOLD_PLAN)
    n = {x.id: x for x in imp.graph.nodes}
    assert (n["goal"].kind, n["goal"].legacy.type) == ("claim", "fact")
    assert (n["situation"].kind, n["situation"].legacy.type) == ("evidence", "observation")
    assert (n["plan"].kind, n["plan"].legacy.type) == ("hypothesis", "prediction")
    assert n["risks"].kind == "hypothesis"
    assert "prediction_as_hypothesis" in {i.code for i in imp.issues}


def test_no_provenance_is_invented():
    imp = import_app_plan(SCAFFOLD_PLAN)
    for x in (*imp.graph.nodes, *imp.graph.edges):
        assert x.basis == "legacy_unverified" and x.spans == () and x.run_id is None
    assert all(n.confidence is None for n in imp.graph.nodes)      # legacy value kept aside
    goal = imp.graph.node("goal")
    assert (goal.legacy.source, goal.legacy.confidence, goal.legacy.sub_label) == (
        "user", 1.0, "goal · Researchers")
    assert all(e.certainty == "inferred" for e in imp.graph.edges)
    assert "provenance_unknown" in {i.code for i in imp.issues}


def test_scaffold_is_detected_and_layout_kept_separately():
    imp = import_app_plan(SCAFFOLD_PLAN)
    assert imp.template_scaffold and "template_scaffold" in {i.code for i in imp.issues}
    assert imp.layout["plan"] == (0.75, 0.8)
    real = {**SCAFFOLD_PLAN, "nodes": [{**SCAFFOLD_PLAN["nodes"][1], "label": "Dry spring"},
                                       *SCAFFOLD_PLAN["nodes"][2:], SCAFFOLD_PLAN["nodes"][0]]}
    assert not import_app_plan(real).template_scaffold


def test_depends_on_is_reversed_and_causes_stays_inferred():
    plan = {"nodes": [{"id": "a", "label": "Analysis", "type": "fact"},
                      {"id": "b", "label": "Dataset", "type": "observation"}],
            "edges": [{"fromId": "a", "toId": "b", "kind": "dependsOn"},
                      {"fromId": "b", "toId": "a", "kind": "causes"}]}
    imp = import_app_plan(plan)
    e0, e1 = imp.graph.edges
    assert (e0.source, e0.target, e0.type, e0.legacy.reversed) == ("b", "a", "requires", True)
    assert (e1.type, e1.certainty, e1.legacy.reversed) == ("causes", "inferred", False)
    assert "causal_link_unconfirmed" in {i.code for i in imp.issues}


def test_dangling_and_self_links_are_dropped_and_reported():
    plan = {"nodes": [{"id": "a", "label": "A", "type": "fact"}],
            "edges": [{"fromId": "a", "toId": "gone", "kind": "supports"},
                      {"fromId": "a", "toId": "a", "kind": "supports"}]}
    imp = import_app_plan(plan)
    assert imp.graph.edges == ()
    assert {"dangling_link_dropped", "self_link_dropped"} <= {i.code for i in imp.issues}


@pytest.mark.parametrize("plan, code", [
    ({"nodes": [{"id": "a", "label": "A", "type": "certainty"}]}, "unknown_legacy_type"),
    ({"nodes": [{"id": "has space", "label": "A", "type": "fact"}]}, "invalid_legacy_node"),
    ({"nodes": [{"id": "a", "label": "A", "type": "fact"}, {"id": "a", "label": "B",
                                                             "type": "fact"}]},
     "invalid_legacy_plan"),
])
def test_unrepresentable_plans_are_refused(plan, code):
    with pytest.raises(GraphError) as e:
        import_app_plan(plan)
    assert e.value.code == code


def test_editing_a_legacy_node_makes_it_user_stated():
    from reflica_service.graph import impact
    from reflica_service.graph.contract import Decision, EditNode
    g = import_app_plan(SCAFFOLD_PLAN).graph
    pv = impact.preview(g, EditNode(node_id="goal", label="Does irrigation raise yield?",
                                    kind="question"))
    g2, _ = impact.decide(g, pv, Decision(preview_sha256=pv.preview_sha256, decision="approve",
                                          decided_by="Dr A"))
    goal = g2.node("goal")
    assert (goal.kind, goal.basis, goal.legacy.type) == ("question", "user_stated", "fact")
