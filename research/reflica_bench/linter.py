"""Schema linter and canonical-input sanitiser.

Enforces the locked information-flow invariants:

    A.1  `declared_input` is canonical/evaluation metadata only. It is stripped
         from method_input during sanitisation. The baseline sees rule content,
         not visibility flags.

    A.2  category, subcategory, template_id, scenario_id, ground_truth.*,
         evaluation_annotations.* are NEVER method-visible.
         scenario_metadata passed to a baseline contains only `operation`,
         `regime`, and an opaque `run_id`.

    Edge IDs globally unique within a scenario. Event target_kind disambiguates
    node-vs-edge targets. Natural-language description is required when
    regime == R-N.
"""

from __future__ import annotations

from typing import Any

from .schema import (
    EdgeType,
    Operation,
    Regime,
    Scenario,
    TargetKind,
)


class LintError(ValueError):
    """Raised when a scenario violates a locked schema invariant."""


# ---------------------------------------------------------------------------
# Lint
# ---------------------------------------------------------------------------

def lint_scenario(scenario: Scenario) -> None:
    """Raise LintError on any violation of the locked invariants.

    Order matters: fail on the first violation so the message is specific.
    """
    _lint_identity(scenario)
    _lint_edge_uniqueness(scenario)
    _lint_event_target_kind(scenario)
    _lint_regime_consistency(scenario)
    _lint_propagation_rules(scenario)
    _lint_justifications(scenario)
    _lint_satisfaction_functions(scenario)
    _lint_combination_selection(scenario)
    _lint_ground_truth_coverage(scenario)


_OPS = {"add", "sub", "mul", "div", "min", "max", "ge", "gt", "le", "lt", "eq", "and", "or", "not"}
_AGGS = {"sum", "max", "min", "count"}


def _lint_expr(e: Any, where: str, known: set[str]) -> None:
    if not isinstance(e, dict):
        if isinstance(e, (list, tuple)):
            raise LintError(f"{where}: bare list is not an expression")
        return
    if "ref" in e or "src" in e:
        key = e.get("ref", e.get("src"))
        if not isinstance(key, str) or "." not in key:
            raise LintError(f"{where}: reference must be 'node.attribute', got {key!r}")
        if key.split(".", 1)[0] not in known:
            raise LintError(f"{where}: unknown node in reference {key!r}")
        if "default" in e:
            _lint_expr(e["default"], where, known)
    elif "agg" in e:
        if e["agg"] not in _AGGS or not isinstance(e.get("attribute"), str):
            raise LintError(f"{where}: agg needs one of {sorted(_AGGS)} and an attribute")
    elif "case" in e:
        branches = e["case"]
        if not branches or branches[-1].get("when") != "otherwise":
            raise LintError(f"{where}: case must end with an 'otherwise' branch")
        for b in branches:
            if b["when"] != "otherwise":
                _lint_expr(b["when"], where, known)
    elif "op" in e:
        if e["op"] not in _OPS or not isinstance(e.get("args"), list):
            raise LintError(f"{where}: unknown op {e.get('op')!r}")
        for a in e["args"]:
            _lint_expr(a, where, known)
    else:
        raise LintError(f"{where}: unrecognised expression {e}")


def _known_nodes(scenario: Scenario) -> set[str]:
    known = set(scenario.canonical_input.graph.node_ids())
    if scenario.canonical_input.event.new_node is not None:
        known.add(scenario.canonical_input.event.new_node.id)
    return known


def _lint_satisfaction_functions(scenario: Scenario) -> None:
    entries = scenario.canonical_input.rules.satisfaction_functions.entries or {}
    known = _known_nodes(scenario)
    for i, c in enumerate(entries.get("computations", []) or []):
        for key in ("node", "attribute", "machine", "human"):
            if key not in c:
                raise LintError(f"computation #{i} missing '{key}'")
        if c["node"] not in known:
            raise LintError(f"computation #{i}: node '{c['node']}' not in graph")
        _lint_expr(c["machine"], f"computation #{i}", known)
    for node, sf in (entries.get("status_functions", {}) or {}).items():
        if node not in known:
            raise LintError(f"status_function: node '{node}' not in graph")
        mapping = sf.get("mapping") or []
        if not mapping or mapping[-1].get("when") != "otherwise":
            raise LintError(f"status_function[{node}]: mapping must end with 'otherwise'")
        for m in mapping:
            if "label" not in m:
                raise LintError(f"status_function[{node}]: every entry needs a label")
            if m["when"] != "otherwise":
                _lint_expr(m["when"], f"status_function[{node}]", known)


def _lint_combination_selection(scenario: Scenario) -> None:
    problems = (scenario.canonical_input.rules.combination_selection.entries or {}).get("problems", {}) or {}
    if len(problems) > 1:
        raise LintError("at most one combination_selection problem per scenario")
    known = _known_nodes(scenario)
    for node, p in problems.items():
        if node not in known:
            raise LintError(f"combination problem: node '{node}' not in graph")
        if not p.get("constraints"):
            raise LintError(f"combination problem[{node}] needs constraints")
        for c in p["constraints"]:
            if c.get("agg") not in {"sum", "max", "min"} or c.get("op") not in {"ge", "gt", "le", "lt", "eq"}:
                raise LintError(f"combination problem[{node}]: bad constraint {c}")


def _lint_justifications(scenario: Scenario) -> None:
    """Validate that the Cat 4 justifications block references real
    conclusions and that each justification is a non-empty list of premise
    ids known to the graph (or newly added by the event)."""
    entries = scenario.canonical_input.rules.justifications.entries
    if not isinstance(entries, dict):
        return
    conclusions = entries.get("conclusions", {})
    if not isinstance(conclusions, dict):
        raise LintError("rules.justifications.entries.conclusions must be a dict")

    graph = scenario.canonical_input.graph
    known_nodes = set(graph.node_ids())
    ev = scenario.canonical_input.event
    if ev.new_node is not None:
        known_nodes.add(ev.new_node.id)

    for conclusion_id, config in conclusions.items():
        if not isinstance(config, dict):
            raise LintError(f"justifications[{conclusion_id}] must be a dict")
        if conclusion_id not in known_nodes:
            raise LintError(
                f"justifications: conclusion '{conclusion_id}' not in graph"
            )
        justs = config.get("justifications", [])
        if not isinstance(justs, list) or len(justs) < 2:
            raise LintError(
                f"justifications[{conclusion_id}].justifications must be a list "
                f"with ≥ 2 alternatives for Category 4"
            )
        for i, just in enumerate(justs):
            if not isinstance(just, list) or len(just) == 0:
                raise LintError(
                    f"justifications[{conclusion_id}].justifications[{i}] must "
                    f"be a non-empty list of premise ids"
                )
            for p in just:
                if p not in known_nodes:
                    raise LintError(
                        f"justifications[{conclusion_id}].justifications[{i}]: "
                        f"premise '{p}' not in graph"
                    )


def _lint_propagation_rules(scenario: Scenario) -> None:
    """Validate propagation rule entries reference known nodes.

    The rules are allowed to reference nodes that will be created by an ADD
    event, so we check against the union of pre-event + event-added nodes.
    """
    rules = scenario.canonical_input.rules.propagation_rules.entries
    if not isinstance(rules, dict):
        return
    rule_list = rules.get("rules", [])
    if not isinstance(rule_list, list):
        raise LintError("rules.propagation_rules.entries.rules must be a list")

    graph = scenario.canonical_input.graph
    known_nodes = set(graph.node_ids())
    ev = scenario.canonical_input.event
    if ev.new_node is not None:
        known_nodes.add(ev.new_node.id)

    for i, r in enumerate(rule_list):
        if not isinstance(r, dict):
            raise LintError(f"propagation rule #{i} must be a dict")
        for key in ("from_node", "from_attribute", "to_node", "to_attribute"):
            if key not in r:
                raise LintError(f"propagation rule #{i} missing '{key}'")
        if r["from_node"] not in known_nodes:
            raise LintError(
                f"propagation rule #{i}: from_node '{r['from_node']}' not in graph"
            )
        if r["to_node"] not in known_nodes:
            raise LintError(
                f"propagation rule #{i}: to_node '{r['to_node']}' not in graph"
            )


def _lint_identity(scenario: Scenario) -> None:
    if scenario.category not in {1, 2, 3, 4, 5, 6, 7}:
        raise LintError(f"category must be 1..7, got {scenario.category}")
    if not scenario.scenario_id:
        raise LintError("scenario_id is required")
    if not scenario.template_id:
        raise LintError("template_id is required")


def _lint_edge_uniqueness(scenario: Scenario) -> None:
    edge_ids = [e.edge_id for e in scenario.canonical_input.graph.edges]
    if len(edge_ids) != len(set(edge_ids)):
        dupes = {eid for eid in edge_ids if edge_ids.count(eid) > 1}
        raise LintError(f"duplicate edge_id(s): {sorted(dupes)}")

    node_ids = scenario.canonical_input.graph.node_ids()
    for e in scenario.canonical_input.graph.edges:
        if e.source not in node_ids:
            raise LintError(f"edge {e.edge_id} source {e.source} not in graph")
        if e.target not in node_ids:
            raise LintError(f"edge {e.edge_id} target {e.target} not in graph")


def _lint_event_target_kind(scenario: Scenario) -> None:
    ev = scenario.canonical_input.event
    graph = scenario.canonical_input.graph

    if ev.operation == Operation.ADD:
        if ev.target_kind == TargetKind.NODE:
            if ev.new_node is None:
                raise LintError("ADD on a node requires new_node")
            if ev.new_node.id in graph.node_ids():
                raise LintError(f"ADD node id {ev.new_node.id} already exists")
        elif ev.target_kind == TargetKind.EDGE:
            if ev.edge_change is None:
                raise LintError("ADD on an edge requires edge_change")
            ec = ev.edge_change
            if ec.source is None or ec.target is None:
                raise LintError("ADD edge_change requires source and target")
            if ec.new_type is None and len(ec.candidate_types or []) < 2:
                raise LintError("ADD edge_change requires new_type or ≥ 2 candidate_types")
            if ec.source not in graph.node_ids():
                raise LintError(f"ADD edge source {ec.source} not in graph")
            if ec.target not in graph.node_ids():
                raise LintError(f"ADD edge target {ec.target} not in graph")

    elif ev.operation == Operation.EDIT:
        if ev.target_kind != TargetKind.NODE:
            raise LintError("EDIT currently targets nodes only (attribute edit)")
        if ev.target_id is None and ev.target_ref is None:
            raise LintError("EDIT requires target_id or target_ref")
        if ev.target_id is not None and ev.target_id not in graph.node_ids():
            raise LintError(f"EDIT target node {ev.target_id} not in graph")
        if ev.attribute is None:
            raise LintError("EDIT requires an attribute name")

    elif ev.operation == Operation.DELETE:
        if ev.target_kind == TargetKind.NODE:
            if ev.target_id is None or ev.target_id not in graph.node_ids():
                raise LintError(f"DELETE target node {ev.target_id} not in graph")
        elif ev.target_kind == TargetKind.EDGE:
            if ev.target_id is None or ev.target_id not in graph.edge_ids():
                raise LintError(f"DELETE target edge {ev.target_id} not in graph")

    elif ev.operation == Operation.RELATIONSHIP_CHANGE:
        if ev.target_kind != TargetKind.EDGE:
            raise LintError("RELATIONSHIP_CHANGE targets edges")
        if ev.edge_change is None:
            raise LintError("RELATIONSHIP_CHANGE requires edge_change")
        if ev.edge_change.edge_id is None:
            raise LintError("RELATIONSHIP_CHANGE edge_change requires an existing edge_id")
        if ev.edge_change.edge_id not in graph.edge_ids():
            raise LintError(
                f"RELATIONSHIP_CHANGE target edge {ev.edge_change.edge_id} not in graph"
            )


def _lint_regime_consistency(scenario: Scenario) -> None:
    if scenario.regime == Regime.R_N and not scenario.natural_language_description:
        raise LintError("regime=R-N requires natural_language_description")


def _lint_ground_truth_coverage(scenario: Scenario) -> None:
    gt_nodes = set(scenario.ground_truth.nodes.keys())
    graph_nodes = scenario.canonical_input.graph.node_ids()
    # Ground truth may list only nodes that exist post-event; the generator
    # is responsible for including nodes added by the event. For pre-event
    # nodes, we require full coverage.
    missing = graph_nodes - gt_nodes
    if missing:
        raise LintError(f"ground_truth.nodes missing entries for: {sorted(missing)}")


# ---------------------------------------------------------------------------
# Sanitise canonical_input -> method_input.structured
# ---------------------------------------------------------------------------

# Fields that are canonical/evaluation metadata and MUST NOT be visible to the method.
_FORBIDDEN_TOP_LEVEL = frozenset(
    {
        "category",
        "subcategory",
        "template_id",
        "scenario_id",
        "ground_truth",
        "evaluation_annotations",
    }
)


def sanitise_rules_for_method(rules_dict: dict[str, Any]) -> dict[str, Any]:
    """Strip rule blocks with declared_input=False; strip the flag itself.

    Enforces invariant A.1.
    """
    out: dict[str, Any] = {}
    for block_name, block in rules_dict.items():
        if not isinstance(block, dict):
            # Unknown shape: pass through untouched (will be caught by schema).
            out[block_name] = block
            continue
        declared_input = block.get("declared_input")
        if declared_input is False:
            continue  # strip the whole block from method input
        # Copy without declared_input flag.
        sanitised = {k: v for k, v in block.items() if k != "declared_input"}
        out[block_name] = sanitised
    return out


def method_metadata(scenario: Scenario, run_id: str) -> dict[str, Any]:
    """Build the ONLY metadata that may be passed to a baseline.

    Enforces invariant A.2: no category/template/subcategory/ground-truth leak.
    """
    return {
        "operation": scenario.operation.value,
        "regime": scenario.regime.value,
        "run_id": run_id,
    }


def assert_no_forbidden_fields(obj: Any, path: str = "") -> None:
    """Hard assert that invariant A.2's forbidden fields never appear in a
    structure that will reach a baseline. Called by the adapter after
    sanitisation."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in _FORBIDDEN_TOP_LEVEL:
                raise LintError(f"forbidden method-visible field '{k}' at {path or '<root>'}")
            assert_no_forbidden_fields(v, f"{path}.{k}" if path else k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            assert_no_forbidden_fields(v, f"{path}[{i}]")
    # scalars are fine
