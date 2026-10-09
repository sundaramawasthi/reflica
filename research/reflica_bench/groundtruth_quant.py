"""Ground-truth generation for Categories 5, 6 (6-A, 6-B) and 7.

All values come from `gt_engine` (direct Python arithmetic + exhaustive
enumeration). Never from B4b.

Per-node conventions (Cats 5–7):
  - outcome_label MUST_CHANGE iff any attribute differs from pre-event (or
    the node was added / deleted).
  - state_change is the SEMANTIC transition only: the node's declared status
    attribute changed, or the node was added / deleted. A pure attribute
    shift (coverage 0.8 → 0.6, status PARTIAL → PARTIAL) is not a state change.
  - Cat 7 AMBIGUOUS nodes: outcome UNCERTAIN or REQUIRES_REEVALUATION (from
    evaluation_annotations.escalation_policy), in_affected_set True,
    state_change False, undeterminable attributes stored as null.

Determinability: a node is AMBIGUOUS iff some value is Unknown in a
completion, or its values differ across the consistent completions of the
finite choice points (P2 conflicting claims, P3 ambiguous edge type, P5 rule
conflict, P9 ambiguous referent).
"""

from __future__ import annotations

import itertools
from typing import Any

from .groundtruth import CategoryMismatchError
from .gt_engine import (
    EvalResult,
    Unknown,
    computations_of,
    duplicate_targets,
    evaluate_state,
    split_key,
    status_attributes_of,
    top_label_of,
)
from .schema import (
    PROPAGATING_EDGE_TYPES,
    Determinability,
    EdgeType,
    GroundTruth,
    NodeGroundTruth,
    Operation,
    OutcomeLabel,
    Scenario,
    ScenarioGroundTruth,
    TargetKind,
)


# ---------------------------------------------------------------------------
# State construction
# ---------------------------------------------------------------------------

def _pre_state(sc: Scenario):
    g = sc.canonical_input.graph
    nodes = {n.id: dict(n.attributes) for n in g.nodes}
    states = {n.id: n.state for n in g.nodes}
    edges = [
        {"edge_id": e.edge_id, "source": e.source, "target": e.target, "type": e.type}
        for e in g.edges
    ]
    return nodes, states, edges


def _reaches(edges: list[dict], start: str, goal: str) -> bool:
    seen, stack = set(), [start]
    while stack:
        n = stack.pop()
        if n == goal:
            return True
        if n in seen:
            continue
        seen.add(n)
        stack.extend(
            e["target"] for e in edges if e["source"] == n and e["type"] in PROPAGATING_EDGE_TYPES
        )
    return False


def referent_candidates(sc: Scenario) -> list[str]:
    ev = sc.canonical_input.event
    nodes, _, edges = _pre_state(sc)
    if ev.target_ref is None:
        return [ev.target_id] if ev.target_id else []
    cands = sorted(n for n, a in nodes.items() if a.get("name") == ev.target_ref)
    if ev.target_scope:
        cands = [c for c in cands if _reaches(edges, c, ev.target_scope)]
    return cands


def _apply_event(sc: Scenario, nodes, states, edges, choice: dict[str, Any]) -> None:
    ev = sc.canonical_input.event
    if ev.operation == Operation.ADD and ev.target_kind == TargetKind.NODE:
        nodes[ev.new_node.id] = dict(ev.new_node.attributes)
    elif ev.operation == Operation.ADD and ev.target_kind == TargetKind.EDGE:
        ec = ev.edge_change
        etype = ec.new_type or EdgeType(choice[f"P3:{ec.source}->{ec.target}"])
        edges.append(
            {"edge_id": f"__added__{ec.source}_{ec.target}", "source": ec.source,
             "target": ec.target, "type": etype}
        )
    elif ev.operation == Operation.EDIT:
        target = ev.target_id if ev.target_ref is None else choice.get(f"P9:{ev.target_ref}")
        if target is None or target not in nodes:
            return
        attrs = nodes[target]
        if states.get(target) == "unavailable":
            attrs[ev.attribute] = Unknown({"P8a"})
        elif ev.attribute not in attrs and sc.category == 7:
            for k in attrs:
                if k != "name":
                    attrs[k] = Unknown({"P8b"})
        else:
            attrs[ev.attribute] = ev.new_value
    elif ev.operation == Operation.DELETE and ev.target_kind == TargetKind.NODE:
        nodes.pop(ev.target_id, None)
        edges[:] = [e for e in edges if ev.target_id not in (e["source"], e["target"])]
    elif ev.operation == Operation.DELETE and ev.target_kind == TargetKind.EDGE:
        edges[:] = [e for e in edges if e["edge_id"] != ev.target_id]
    elif ev.operation == Operation.RELATIONSHIP_CHANGE:
        for e in edges:
            if e["edge_id"] == ev.edge_change.edge_id and ev.edge_change.new_type is not None:
                e["type"] = ev.edge_change.new_type


def _event_choice_points(sc: Scenario) -> list[tuple[str, list[Any]]]:
    ev = sc.canonical_input.event
    pts: list[tuple[str, list[Any]]] = []
    if ev.target_ref is not None:
        cands = referent_candidates(sc)
        if len(cands) > 1:
            pts.append((f"P9:{ev.target_ref}", cands))
        elif len(cands) == 1:
            pts.append((f"P9:{ev.target_ref}", cands))  # resolved, single value
    ec = ev.edge_change
    if ec is not None and ec.new_type is None and ec.candidate_types:
        pts.append((f"P3:{ec.source}->{ec.target}", [t.value for t in ec.candidate_types]))
    return pts


def _state_choice_points(sc: Scenario, nodes, edges) -> list[tuple[str, list[Any]]]:
    rules = sc.canonical_input.rules
    pts: list[tuple[str, list[Any]]] = []
    ev = rules.evidence.entries or {}
    for key, claims in (ev.get("claims", {}) or {}).items():
        if key in (ev.get("resolution", {}) or {}):
            continue
        n, a = split_key(key)
        if n not in nodes or a not in nodes[n]:
            continue
        vals: list[Any] = []
        for v in [nodes[n][a]] + [c["value"] for c in claims]:
            if v not in vals:
                vals.append(v)
        if len(vals) > 1:
            pts.append((f"P2:{key}", vals))
    for (n, a), idxs in sorted(duplicate_targets(nodes, edges, rules).items()):
        pts.append((f"P5:{n}.{a}", idxs))
    return pts


def _completions(sc: Scenario) -> list[tuple[dict[str, Any], EvalResult]]:
    rules = sc.canonical_input.rules
    out = []
    ev_pts = _event_choice_points(sc)
    for combo in itertools.product(*(v for _, v in ev_pts)):
        choice = dict(zip((k for k, _ in ev_pts), combo))
        nodes, states, edges = _pre_state(sc)
        _apply_event(sc, nodes, states, edges, choice)
        st_pts = _state_choice_points(sc, nodes, edges)
        for combo2 in itertools.product(*(v for _, v in st_pts)):
            full = dict(choice)
            full.update(zip((k for k, _ in st_pts), combo2))
            out.append((full, evaluate_state(nodes, edges, rules, full)))
    return out


# ---------------------------------------------------------------------------
# Generator
# ---------------------------------------------------------------------------

def _norm(v: Any) -> Any:
    return None if isinstance(v, Unknown) else v


def _unknown_codes(attrs: dict) -> set[str]:
    out: set[str] = set()
    for v in attrs.values():
        if isinstance(v, Unknown):
            out |= v.codes
    return out


def generate_quantitative(sc: Scenario) -> GroundTruth:
    rules = sc.canonical_input.rules
    nodes0, _, edges0 = _pre_state(sc)
    pre = evaluate_state(nodes0, edges0, rules)
    for nid, attrs in pre.nodes.items():
        if _unknown_codes(attrs):
            raise CategoryMismatchError(f"pre-event state of '{nid}' is not determinable")
        if attrs != nodes0[nid]:
            raise CategoryMismatchError(
                f"stored pre-event attributes of '{nid}' {nodes0[nid]} disagree with "
                f"the declared rules {attrs}"
            )

    comps = _completions(sc)
    status_attrs = status_attributes_of(rules)
    policy = sc.evaluation_annotations.escalation_policy
    first = comps[0][1]

    gt_nodes: dict[str, NodeGroundTruth] = {}
    for nid in sorted(set(nodes0) | set().union(*(set(r.nodes) for _, r in comps))):
        pre_attrs = nodes0.get(nid)
        posts = [r.nodes.get(nid) for _, r in comps]
        if any(p is None for p in posts):
            if all(p is None for p in posts):  # deleted
                gt_nodes[nid] = NodeGroundTruth(
                    outcome_label=OutcomeLabel.MUST_CHANGE, state_change=True,
                    attribute_values=dict(pre_attrs or {}), in_affected_set=True,
                )
                continue
        codes: set[str] = set()
        for p in posts:
            codes |= _unknown_codes(p or {})
        for (ci, ri), (cj, rj) in itertools.combinations(comps, 2):
            pi, pj = ri.nodes.get(nid) or {}, rj.nodes.get(nid) or {}
            if {k: _norm(v) for k, v in pi.items()} != {k: _norm(v) for k, v in pj.items()}:
                codes |= {k.split(":")[0] for k in ci if ci[k] != cj.get(k)}
        if codes:
            keys = set().union(*(set(p or {}) for p in posts))
            merged = {}
            for k in sorted(keys):
                vs = [(p or {}).get(k) for p in posts]
                merged[k] = None if any(isinstance(v, Unknown) for v in vs) or any(
                    v != vs[0] for v in vs
                ) else vs[0]
            label = OutcomeLabel.UNCERTAIN
            if any(policy.get(c) == "REQUIRES_REEVALUATION" for c in codes) or (
                any(n == nid for r in (x for _, x in comps) for n, _ in r.no_fixed_point)
                and policy.get("P4_no_fixed_point") == "REQUIRES_REEVALUATION"
            ):
                label = OutcomeLabel.REQUIRES_REEVALUATION
            gt_nodes[nid] = NodeGroundTruth(
                outcome_label=label, state_change=False, attribute_values=merged,
                in_affected_set=True, determinability=Determinability.AMBIGUOUS,
                pathology_codes=sorted(codes),
            )
            continue
        post = posts[0]
        changed = pre_attrs is None or pre_attrs != post
        sa = status_attrs.get(nid)
        state_change = pre_attrs is None or (
            sa is not None and pre_attrs.get(sa) != post.get(sa)
        )
        gt_nodes[nid] = NodeGroundTruth(
            outcome_label=OutcomeLabel.MUST_CHANGE if changed else OutcomeLabel.MUST_STAY_STABLE,
            state_change=state_change, attribute_values=dict(post),
            in_affected_set=changed,
        )

    # ---- scenario-level annotations ----
    scen = ScenarioGroundTruth()
    scen.pathology_codes = sorted(set().union(*(set(g.pathology_codes) for g in gt_nodes.values())))
    for _, r in comps:
        for k, v in r.fixed_point_analysis.items():
            scen.fixed_point_analysis.setdefault(k, v)
    if len(comps) > 1 and any(g.determinability == Determinability.AMBIGUOUS for g in gt_nodes.values()):
        flat = [
            {f"{n}.{a}": _norm(v) for n, attrs in r.nodes.items() for a, v in attrs.items()}
            for _, r in comps
        ]
        keys = sorted(k for k in set().union(*flat) if len({repr(f.get(k)) for f in flat}) > 1)
        if keys:
            scen.consistent_completions = [
                {"choice": c, "differs": {k: f.get(k) for k in keys}}
                for (c, _), f in zip(comps, flat)
            ]
    combo = first.combination
    if combo is not None and combo.get("feasible") is not None:
        scen.feasible_combinations = combo["feasible"]
        if "optima" in combo:
            optima = combo["optima"]
            entry: dict[str, Any] = {
                "members": optima[0] if len(optima) == 1 else None,
                "objective_value": combo.get("objective_value"),
            }
            if len(optima) > 1:
                entry["ties"] = optima
                scen.consistent_completions = [
                    {"choice": {f"P10:{combo['conclusion']}": m},
                     "differs": {f"{combo['conclusion']}.selected": m}}
                    for m in optima
                ]
            scen.optimal_combination = {combo["conclusion"]: entry}

    if sc.category == 6:
        scen.compensation_viable = _compensation(sc, pre, first)

    gt = GroundTruth(scenario=scen, nodes=gt_nodes)
    _VERIFY[sc.category](sc, pre, comps, gt)
    return gt


def _compensation(sc: Scenario, pre: EvalResult, post: EvalResult) -> bool | None:
    if sc.operation == Operation.ADD:
        return None
    rules = sc.canonical_input.rules
    satisfied = [
        n for n, a in status_attributes_of(rules).items()
        if pre.nodes.get(n, {}).get(a) == top_label_of(rules, n)
    ]
    if not satisfied:
        return None
    return all(
        post.nodes.get(n, {}).get(status_attributes_of(rules)[n]) == top_label_of(rules, n)
        for n in satisfied
    )


# ---------------------------------------------------------------------------
# Category verifiers (mechanical boundary tests)
# ---------------------------------------------------------------------------

def _walk(e: Any, fn) -> None:
    if isinstance(e, dict):
        fn(e)
        for v in e.values():
            _walk(v, fn)
    elif isinstance(e, list):
        for v in e:
            _walk(v, fn)


def _no_ambiguity(sc: Scenario, comps, gt: GroundTruth, cat: str) -> None:
    if len(comps) > 1 or any(g.determinability == Determinability.AMBIGUOUS for g in gt.nodes.values()):
        codes = sorted(set(gt.scenario.pathology_codes) | {k.split(":")[0] for c, _ in comps for k in c})
        raise CategoryMismatchError(f"{cat} scenario contains ambiguity {codes} — belongs in Cat 7")


def _verify_cat5(sc: Scenario, pre, comps, gt) -> None:
    rules = sc.canonical_input.rules
    sfs = (rules.satisfaction_functions.entries or {}).get("status_functions", {}) or {}
    if not any(any(m["label"] == "PARTIAL" for m in sf["mapping"]) for sf in sfs.values()):
        raise CategoryMismatchError("Cat 5 requires a status function with a PARTIAL level")
    if (rules.combination_selection.entries or {}).get("problems"):
        raise CategoryMismatchError("combination selection belongs in Cat 6-B")
    for c in computations_of(rules):
        srcs: set[str] = set()

        def visit(e: dict) -> None:
            if "agg" in e:
                raise CategoryMismatchError(
                    f"Cat 5 computation {c['node']}.{c['attribute']} aggregates sources — Cat 6"
                )
            for k in ("ref", "src"):
                if k in e and split_key(e[k])[0] != c["node"]:
                    srcs.add(split_key(e[k])[0])

        _walk(c["machine"], visit)
        if len(srcs) > 1:
            raise CategoryMismatchError(
                f"Cat 5 computation {c['node']}.{c['attribute']} reads {sorted(srcs)} — "
                f"more than one quantitative source is Cat 6"
            )
    _no_ambiguity(sc, comps, gt, "Cat 5")
    if not any(g.outcome_label == OutcomeLabel.MUST_CHANGE for n, g in gt.nodes.items() if n in sfs):
        raise CategoryMismatchError("Cat 5 event must revise a conclusion's attributes")


def _verify_cat6(sc: Scenario, pre, comps, gt) -> None:
    rules = sc.canonical_input.rules
    _no_ambiguity(sc, comps, gt, "Cat 6")
    if sc.subcategory == "C6-B":
        for r in (pre, comps[0][1]):
            info = r.combination
            if not info or len(info["candidates"]) < 2:
                raise CategoryMismatchError("Cat 6-B needs ≥ 2 candidate sources")
            if any(len(m) == 1 for m in info["feasible"]):
                raise CategoryMismatchError("a single source satisfies all constraints — not Cat 6")
            if len(info.get("optima", [])) > 1:
                raise CategoryMismatchError("tied optimum — Cat 7 P10, not Cat 6-B")
        return
    if sc.subcategory != "C6-A":
        raise CategoryMismatchError("Cat 6 subcategory must be C6-A or C6-B")
    sfs = (rules.satisfaction_functions.entries or {}).get("status_functions", {}) or {}
    owners = set()
    for c in computations_of(rules):
        _walk(c["machine"], lambda e, c=c: owners.add(c["node"]) if "agg" in e else None)
    tested = owners & set(sfs)
    if not tested:
        raise CategoryMismatchError("Cat 6-A needs a status-bearing aggregate conclusion")
    nodes0, _, edges0 = _pre_state(sc)
    for concl in tested:
        srcs = [e["source"] for e in edges0 if e["target"] == concl and e["type"] in PROPAGATING_EDGE_TYPES]
        for s in srcs:
            only = [e for e in edges0 if e["target"] != concl or e["source"] == s]
            r = evaluate_state(nodes0, only, rules)
            if r.nodes[concl].get(sfs[concl].get("status_attribute", "status")) == top_label_of(rules, concl):
                raise CategoryMismatchError(
                    f"source '{s}' alone satisfies '{concl}' — Cat 4/5, not Cat 6"
                )


def _surface_pathology(sc: Scenario) -> bool:
    rules = sc.canonical_input.rules
    nodes, _, edges = _pre_state(sc)
    if any(_reaches(edges, e["target"], e["source"]) for e in edges if e["type"] in PROPAGATING_EDGE_TYPES):
        return True
    if (rules.evidence.entries or {}).get("claims") or (rules.units.entries or {}).get("factors"):
        return True
    if sc.canonical_input.event.target_ref is not None:
        return True
    found = []
    for c in computations_of(rules):
        _walk(c["machine"], lambda e: found.append(1) if "default" in e else None)
    return bool(found)


def _verify_cat7(sc: Scenario, pre, comps, gt) -> None:
    amb = any(g.determinability == Determinability.AMBIGUOUS for g in gt.nodes.values())
    if sc.subcategory == "ambiguous" and not amb:
        raise CategoryMismatchError("Cat 7 ambiguous scenario has no AMBIGUOUS node")
    if sc.subcategory == "false_ambiguous":
        if amb:
            raise CategoryMismatchError("Cat 7 negative control must be fully determinable")
        if not _surface_pathology(sc):
            raise CategoryMismatchError("Cat 7 negative control needs a surface pathology")
    if sc.subcategory not in ("ambiguous", "false_ambiguous"):
        raise CategoryMismatchError("Cat 7 subcategory must be ambiguous or false_ambiguous")


_VERIFY = {5: _verify_cat5, 6: _verify_cat6, 7: _verify_cat7}
