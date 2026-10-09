"""B5 — Reflica baseline wrapper: change detection, consistent completions,
determinability, output. See engine.py for stages 2–4."""
from __future__ import annotations

import itertools
from typing import Any

from ..adapters import AdapterOutput
from ..baseline import RevisionResult, Timer
from ..schema import OutcomeLabel
from .engine import INFLUENCING, VERSION, Missing, World, _t, lower, revise_world


def _world(mi) -> World:
    return World({n.id: dict(n.attributes) for n in mi.graph.nodes},
                 [{"edge_id": e.edge_id, "source": e.source, "target": e.target, "type": _t(e.type)} for e in mi.graph.edges],
                 {n.id: n.state for n in mi.graph.nodes})


def _referents(w: World, ev) -> list[str]:
    if ev.target_ref is None:
        return [ev.target_id] if ev.target_id else []
    named = sorted(n for n, a in w.nodes.items() if a.get("name") == ev.target_ref)
    if not ev.target_scope:
        return named

    def reaches(s):
        seen, todo = set(), [s]
        while todo:
            x = todo.pop()
            if x == ev.target_scope:
                return True
            if x not in seen:
                seen.add(x)
                todo += [e["target"] for e in w.edges if e["source"] == x and e["type"] in INFLUENCING]
        return False
    return [n for n in named if reaches(n)]


def _event_choices(w: World, ev) -> list[tuple[str, list]]:
    pts = []
    if ev.target_ref is not None:
        pts.append((f"P9:{ev.target_ref}", _referents(w, ev) or [None]))
    ec = ev.edge_change
    if ec is not None and ec.new_type is None and ec.candidate_types:
        pts.append((f"P3:{ec.source}->{ec.target}", [_t(t) for t in ec.candidate_types]))
    return pts


def _apply(w: World, ev, choice: dict, notes: list) -> None:
    op, kind = _t(ev.operation), _t(ev.target_kind)
    if op == "EDIT":
        tgt = choice.get(f"P9:{ev.target_ref}") if ev.target_ref is not None else ev.target_id
        if tgt not in w.nodes:
            notes.append(f"update target {tgt!r} not found")
            return
        attrs = w.nodes[tgt]
        if w.states.get(tgt) == "unavailable":
            attrs[ev.attribute] = Missing("P8a")
            notes.append(f"{tgt} is unavailable; update contradicts its state")
        elif ev.attribute not in attrs:
            for k in attrs:
                if k != "name":
                    attrs[k] = Missing("P8b")
            notes.append(f"{tgt} has no attribute {ev.attribute!r}; intended effect unknown")
        else:
            attrs[ev.attribute] = ev.new_value
    elif op == "DELETE" and kind == "node":
        w.nodes.pop(ev.target_id, None)
        w.edges[:] = [e for e in w.edges if ev.target_id not in (e["source"], e["target"])]
    elif op == "DELETE":
        w.edges[:] = [e for e in w.edges if e["edge_id"] != ev.target_id]
    elif op == "ADD" and kind == "node":
        w.nodes[ev.new_node.id] = dict(ev.new_node.attributes)
        w.states[ev.new_node.id] = ev.new_node.state
    elif op == "ADD":
        ec = ev.edge_change
        t = _t(ec.new_type) if ec.new_type is not None else choice[f"P3:{ec.source}->{ec.target}"]
        w.edges.append({"edge_id": f"+{ec.source}->{ec.target}", "source": ec.source, "target": ec.target, "type": t})
    else:
        for e in w.edges:
            if e["edge_id"] == ev.edge_change.edge_id and ev.edge_change.new_type is not None:
                e["type"] = _t(ev.edge_change.new_type)


def _evidence(w: World, aux: dict, notes: list) -> list[tuple[str, list]]:
    """Valid preference rules are applied; a rule naming a source no claim
    carries is rejected (never invented or repaired). Unresolved disagreement
    becomes an open choice (P2)."""
    pts = []
    for key, claims in aux["claims"].items():
        n, _, a = key.partition(".")
        if n not in w.nodes or a not in w.nodes[n]:
            continue
        res = aux["resolution"].get(key)
        sources = {c["source"] for c in claims}
        if res and res.get("policy") == "prefer_source" and (res["source"] == "graph" or res["source"] in sources):
            if res["source"] != "graph":
                w.nodes[n][a] = next(c["value"] for c in claims if c["source"] == res["source"])
            continue
        if res:
            notes.append(f"rejected preference rule for {key}: source {res.get('source')!r} has no claim")
        vals = []
        for v in [w.nodes[n][a]] + [c["value"] for c in claims]:
            if v not in vals:
                vals.append(v)
        if len(vals) > 1:
            pts.append((f"P2:{key}", vals))
    return pts


def _dup_choices(w: World, rules) -> list[tuple[str, list]]:
    seen: dict = {}
    for r in rules:
        if r.node in w.nodes and all(w.link(x, r.node) for x in r.when_linked):
            seen.setdefault((r.node, r.attr), []).append(r.idx)
    return [(f"P5:{n}.{a}", ids) for (n, a), ids in sorted(seen.items()) if len(ids) > 1]


class B5Reflica:
    name = "B5_reflica"
    version = VERSION
    supports_scope_detection = True
    supports_attribute_computation = True
    supports_feasibility_classification = True
    supports_abstention = True

    def revise(self, adapter_output: AdapterOutput) -> RevisionResult:
        with Timer() as t:
            mi = adapter_output.structured
            if mi is None:
                return RevisionResult(unsupported_dimensions=["all"])
            rules, aux = lower(mi.rules)
            pre = _world(mi)
            runs = []
            for c1 in _product(_event_choices(pre, mi.event)):
                notes: list = []
                w1 = pre.copy()
                _apply(w1, mi.event, c1, notes)
                for c2 in _product(_evidence(w1.copy(), aux, []) + _dup_choices(w1, rules)):
                    w = w1.copy()
                    _evidence(w, aux, notes)
                    for k, v in c2.items():
                        if k.startswith("P2:"):
                            n, _, a = k[3:].partition(".")
                            w.nodes[n][a] = v
                    trace = revise_world(pre, w, rules, aux, {**c1, **c2})
                    trace["notes"] = sorted(set(notes))
                    runs.append((w, trace))
            return self._merge(pre, runs, t)

    def _merge(self, pre: World, runs, t) -> RevisionResult:
        ids = set(pre.nodes) | set().union(*(set(w.nodes) for w, _ in runs))
        labels, values, det, flags, conf, status = {}, {}, {}, {}, {}, {}
        choice_codes = lambda a, b: {k.split(":")[0] for k in a["choice"] if a["choice"][k] != b["choice"].get(k)}  # noqa: E731
        for nid in sorted(ids):
            posts = [w.nodes.get(nid) for w, _ in runs]
            if all(p is None for p in posts):
                labels[nid], values[nid], det[nid], flags[nid], conf[nid] = OutcomeLabel.MUST_CHANGE, dict(pre.nodes[nid]), "DETERMINABLE", [], 1.0
                continue
            keys = set().union(*(set(p or {}) for p in posts)) - {"__combo__"}
            merged, why, provisional = {}, set(), False
            for k in sorted(keys):
                vs = [(p or {}).get(k) for p in posts]
                miss = [v for v in vs if isinstance(v, Missing)]
                if miss:
                    why |= set().union(*(m.why for m in miss))
                    merged[k] = None
                elif any(v != vs[0] for v in vs):
                    provisional = True
                    for (_, ta), (_, tb) in itertools.combinations(runs, 2):
                        why |= choice_codes(ta, tb)
                    merged[k] = None
                else:
                    merged[k] = vs[0]
            values[nid] = merged
            if why:
                labels[nid] = OutcomeLabel.REQUIRES_REEVALUATION if provisional and not any(
                    isinstance(v, Missing) for p in posts for v in (p or {}).values()) else OutcomeLabel.UNCERTAIN
                det[nid], flags[nid], conf[nid] = "AMBIGUOUS", sorted(why), 0.0
            else:
                changed = nid not in pre.nodes or merged != pre.nodes[nid]
                labels[nid] = OutcomeLabel.MUST_CHANGE if changed else OutcomeLabel.MUST_STAY_STABLE
                det[nid], flags[nid], conf[nid] = "DETERMINABLE", [], 1.0
            if "status" in merged and nid in _status_nodes(runs):
                status[nid] = merged["status"]
        combos = [w.nodes.get(n, {}).get("__combo__", {}).get("__feasible__") for w, _ in runs for n in w.nodes
                  if "__combo__" in w.nodes.get(n, {})]
        return RevisionResult(
            affected_set=sorted(n for n, l in labels.items() if l != OutcomeLabel.MUST_STAY_STABLE),
            outcome_labels=labels, attribute_values=values, feasibility_status=status,
            determinability=det, pathology_flags=flags, confidence_scores=conf,
            feasible_combinations=combos[0] if combos and all(c == combos[0] for c in combos) else ([] if not combos else None),
            explanation={"version": VERSION, "completions": [tr for _, tr in runs]},
            wall_time_ms=t.elapsed_ms)


def _product(points: list[tuple[str, list]]):
    for combo in itertools.product(*(v for _, v in points)) if points else [()]:
        yield dict(zip((k for k, _ in points), combo))


def _status_nodes(runs) -> set:
    out = set()
    for _, tr in runs:
        out |= {a.split(".")[0] for a in tr["affected"] if a.endswith(".status")}
    return out | {n for w, _ in runs for n, attrs in w.nodes.items() if "status" in attrs}
