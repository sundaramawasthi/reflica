"""Translate a plan saved by the current Flutter app (app-plan@0) into graph@1.

The app's JSON (lib/models/plan.dart) has nodes typed
fact / observation / prediction / hypothesis / assumption and edges typed
dependsOn / blocks / enables / causes / requires / supports, with no record
of where any item came from. Translation rules:

- Every imported node and edge gets basis `legacy_unverified`; nothing is
  presented as quoted, user-stated or computed. All imported links are
  therefore `inferred` until the researcher confirms them.
- Kinds: fact -> claim, observation -> evidence, prediction -> hypothesis,
  hypothesis -> hypothesis, assumption -> assumption. The original type,
  sub-label, free-text source and confidence are kept in `legacy`.
- Edges: `A dependsOn B` (A depends on B) becomes `B --requires--> A` because
  graph@1 edges point from the influencing item to the influenced one
  (`legacy.reversed` records the flip). Other types keep their direction;
  `causes` is kept but, like every legacy link, stays inferred.
- Node positions are display data, returned separately as `layout`.
- Plans that still contain the app's fixed starter scaffold are reported, so
  the app can offer to rebuild them from the researcher's own text instead of
  treating template nodes as knowledge.
"""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, ValidationError

from .contract import Edge, Graph, GraphError, LegacyOrigin, Node

KIND = {"fact": "claim", "observation": "evidence", "prediction": "hypothesis",
        "hypothesis": "hypothesis", "assumption": "assumption"}
EDGE = {"dependsOn": ("requires", True), "blocks": ("blocks", False),
        "enables": ("enables", False), "causes": ("causes", False),
        "requires": ("requires", False), "supports": ("supports", False)}
# the fixed starter nodes PlanRepository._bootstrapNodes creates for every plan
SCAFFOLD = {"situation": "Situation", "resources": "Resources", "constraints": "Constraints",
            "risks": "Risks", "plan": "Proposed plan"}


class LegacyIssue(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    code: str
    message: str
    item: str | None = None


class LegacyImport(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    graph: Graph
    layout: dict[str, tuple[float, float]]
    issues: tuple[LegacyIssue, ...]
    template_scaffold: bool  # plan still holds the fixed starter nodes


def import_app_plan(plan: dict[str, Any]) -> LegacyImport:
    """Translate the app's Plan JSON. Raises GraphError if it cannot be represented."""
    issues: list[LegacyIssue] = []
    nodes, layout = [], {}
    for raw in plan.get("nodes") or []:
        t = raw.get("type")
        if t not in KIND:
            raise GraphError("unknown_legacy_type", f"Unknown node type '{t}'.", {"node": raw.get("id")})
        label = (raw.get("label") or "").strip() or str(raw.get("id"))
        if len(label) > 300:
            issues.append(LegacyIssue(code="label_truncated", item=raw.get("id"),
                                      message="Label longer than 300 characters was truncated."))
            label = label[:300]
        origin = LegacyOrigin(type=t, sub_label=raw.get("subLabel"), source=raw.get("source"),
                              confidence=raw.get("confidence"))
        try:
            nodes.append(Node(id=raw["id"], kind=KIND[t], label=label, basis="legacy_unverified",
                              legacy=origin))
        except ValidationError as e:
            raise GraphError("invalid_legacy_node", f"Node '{raw.get('id')}' cannot be imported: "
                             f"{e.errors()[0]['msg']}", {"node": raw.get("id")}) from None
        if t == "prediction":
            issues.append(LegacyIssue(code="prediction_as_hypothesis", item=raw["id"], message=(
                "Imported as kind 'hypothesis'; its original type 'prediction' is kept in "
                "legacy.type.")))
        if "x" in raw and "y" in raw:
            layout[raw["id"]] = (float(raw["x"]), float(raw["y"]))
    edges = []
    for k, raw in enumerate(plan.get("edges") or []):
        kind = raw.get("kind")
        if kind not in EDGE:
            raise GraphError("unknown_legacy_type", f"Unknown edge kind '{kind}'.", {"edge": k})
        etype, flip = EDGE[kind]
        src, dst = (raw["toId"], raw["fromId"]) if flip else (raw["fromId"], raw["toId"])
        if src == dst:
            issues.append(LegacyIssue(code="self_link_dropped", item=f"edge {k}",
                                      message="A link from a node to itself was dropped."))
            continue
        edges.append(Edge(id=f"legacy_e{k}", source=src, target=dst, type=etype,
                          certainty="inferred", basis="legacy_unverified",
                          legacy=LegacyOrigin(type=kind, reversed=flip)))
        if kind == "causes":
            issues.append(LegacyIssue(code="causal_link_unconfirmed", item=f"legacy_e{k}", message=(
                "A 'causes' link was imported as inferred; confirm it only if the evidence "
                "supports a causal claim.")))
    known = {n.id for n in nodes}
    kept = [e for e in edges if e.source in known and e.target in known]
    for e in edges:
        if e not in kept:
            issues.append(LegacyIssue(code="dangling_link_dropped", item=e.id,
                                      message="A link to a missing node was dropped."))
    try:
        graph = Graph(nodes=tuple(nodes), edges=tuple(kept))
    except ValidationError as e:
        raise GraphError("invalid_legacy_plan", f"The plan cannot be imported: {e.errors()[0]['msg']}") from None
    scaffold = all(any(n.id == i and n.label == lab for n in nodes) for i, lab in SCAFFOLD.items())
    if scaffold:
        issues.append(LegacyIssue(code="template_scaffold", message=(
            "This plan contains the app's fixed starter nodes (Situation, Resources, "
            "Constraints, Risks, Proposed plan). They were not derived from your input; "
            "consider rebuilding the graph from your text.")))
    issues.append(LegacyIssue(code="provenance_unknown", message=(
        "Imported items have basis 'legacy_unverified': where they came from was never recorded, "
        "and all links are inferred until you confirm them.")))
    return LegacyImport(graph=graph, layout=layout, issues=tuple(issues), template_scaffold=scaffold)
