"""B5 — Reflica dependency-aware revision engine (v0.1.0).

Pipeline (each stage recorded in the trace):
  1. change detection    apply the update to a copy of the state; resolve
                         referents; nothing is guessed (open choices kept)
  2. dependency analysis build a rule-dependency graph over (node, attribute)
                         keys and compute the downstream closure of the change
  3. revision            recompute only keys in that closure, in dependency
                         order (cycles: finite-domain fixed-point search)
  4. verification/repair re-check EVERY rule on the revised state; violations
                         inside the closure are repaired by recomputation;
                         violations outside it are reported, never "fixed"
  5. determinability     run 1–4 once per consistent completion of the open
                         choices (shared name, unstated link kind, unresolved
                         conflicting reports, duplicate rules); a value is
                         committed only if it is known and identical in every
                         completion, else the node abstains with reason codes

Written from the declared rule semantics only. It must not import the
ground-truth engine, the generators, B4b or the evaluator (tested).
A source-preference rule naming a source that no claim carries is treated as
invalid (P2 stays open) — B5 never invents or repairs a preference.
"""
from __future__ import annotations

import itertools
from dataclasses import dataclass, field
from fractions import Fraction
from typing import Any

INFLUENCING = {"requires", "supports", "causes", "blocks", "enables", "derived_from"}
CMP = {"ge": lambda a, b: a >= b, "gt": lambda a, b: a > b, "le": lambda a, b: a <= b,
       "lt": lambda a, b: a < b, "eq": lambda a, b: a == b}
VERSION = "0.1.0"


class Missing:
    """An undeterminable value and why (reason codes)."""
    __slots__ = ("why",)

    def __init__(self, *why: str):
        self.why = frozenset(why)

    def __eq__(self, o):
        return isinstance(o, Missing) and o.why == self.why

    def __hash__(self):
        return hash(self.why)

    def __repr__(self):
        return f"Missing{sorted(self.why)}"


def _t(v):  # edge type as plain string
    return getattr(v, "value", v)


def _num(v):
    if isinstance(v, bool) or not isinstance(v, (int, float, Fraction)):
        return None
    return Fraction(str(v)) if isinstance(v, float) else Fraction(v)


def _plain(v):
    if isinstance(v, Fraction):
        return int(v) if v.denominator == 1 else round(float(v), 6)
    return v


@dataclass
class World:
    nodes: dict[str, dict[str, Any]]
    edges: list[dict[str, Any]]
    states: dict[str, Any] = field(default_factory=dict)

    def copy(self) -> "World":
        return World({k: dict(v) for k, v in self.nodes.items()}, [dict(e) for e in self.edges], dict(self.states))

    def link(self, a: str, b: str) -> bool:
        return a in self.nodes and any(e["source"] == a and e["target"] == b and _t(e["type"]) in INFLUENCING
                                       for e in self.edges)

    def feeders(self, b: str) -> list[str]:
        return sorted({e["source"] for e in self.edges if e["target"] == b and _t(e["type"]) in INFLUENCING
                       and e["source"] in self.nodes})


# ---------------------------------------------------------------------------
# Rules (lowered into one list of "key <- formula" definitions)
# ---------------------------------------------------------------------------

@dataclass
class Rule:
    node: str
    attr: str
    kind: str          # formula | copy | map | justify | combo
    body: Any
    idx: int
    when_linked: tuple = ()


def lower(rules: dict) -> tuple[list[Rule], dict]:
    def entries(name):
        return ((rules.get(name) or {}).get("entries") or {})
    out: list[Rule] = []
    for p in entries("propagation_rules").get("rules", []) or []:
        m = p.get("machine") or {}
        out.append(Rule(p["to_node"], p["to_attribute"], "map" if m.get("operator") == "map" else "copy", p, len(out)))
    for c, cfg in (entries("justifications").get("conclusions", {}) or {}).items():
        out.append(Rule(c, cfg.get("status_attribute", "status"), "justify", cfg, len(out)))
    sat = entries("satisfaction_functions")
    for c in sat.get("computations", []) or []:
        out.append(Rule(c["node"], c["attribute"], "formula", c["machine"], len(out), tuple(c.get("when_linked") or ())))
    for n, sf in (sat.get("status_functions", {}) or {}).items():
        out.append(Rule(n, sf.get("status_attribute", "status"), "formula",
                        {"case": [{"when": m["when"], "then": m["label"]} for m in sf["mapping"]]}, len(out)))
    for n, p in (entries("combination_selection").get("problems", {}) or {}).items():
        out.append(Rule(n, "__combo__", "combo", p, len(out)))
    aux = {"claims": entries("evidence").get("claims", {}) or {}, "resolution": entries("evidence").get("resolution", {}) or {},
           "factors": entries("units").get("factors", {}) or {}, "domains": entries("fixed_point_semantics").get("domains", {}) or {}}
    return out, aux


def _split(k: str):
    n, _, a = k.partition(".")
    return n, a


# ---------------------------------------------------------------------------
# Evaluation of one rule against a world
# ---------------------------------------------------------------------------

class Eval:
    def __init__(self, w: World, aux: dict):
        self.w, self.aux = w, aux

    def read(self, n, a, dflt, owner):
        attrs = self.w.nodes.get(n)
        if attrs is None or a not in attrs:
            return self.expr(dflt, owner) if dflt is not None else Missing("P1")
        v = attrs[a]
        if isinstance(v, Missing):
            return v
        if isinstance(v, dict) and "$unknown" in v:
            return Missing("P1")
        unit = attrs.get(f"{a}_unit")
        q = _num(v)
        if isinstance(unit, str) and q is not None:
            f = self.aux["factors"].get(unit)
            return (q * _num(f), "*base*") if f is not None else (q, unit)
        return (q, None) if q is not None else (v, None)

    def expr(self, e, owner):
        if not isinstance(e, dict):
            q = _num(e)
            return (q, None) if q is not None else (e, None)
        if "ref" in e:
            return self.read(*_split(e["ref"]), e.get("default"), owner)
        if "src" in e:
            n, a = _split(e["src"])
            if not self.w.link(n, owner):
                return self.expr(e["default"], owner) if e.get("default") is not None else Missing("P1")
            return self.read(n, a, e.get("default"), owner)
        if "agg" in e:
            vals = [self.read(s, e["attribute"], None, owner) for s in self.w.feeders(owner)]
            bad = [v for v in vals if isinstance(v, Missing)]
            if bad:
                return Missing(*set().union(*(b.why for b in bad)))
            if e["agg"] == "count":
                return Fraction(len(vals)), None
            if not vals:
                return _num(e.get("empty", 0)), None
            if any(not isinstance(v[0], Fraction) for v in vals):
                return Missing("P6")
            units = {u for _, u in vals if u}
            if len(units) > 1:
                return Missing("P7")
            agg = {"sum": sum, "max": max, "min": min}[e["agg"]]
            return agg(v[0] for v in vals), next(iter(units), None)
        if "case" in e:
            for b in e["case"]:
                if b["when"] == "otherwise":
                    return b["then"], None
                c = self.expr(b["when"], owner)
                if isinstance(c, Missing):
                    return c
                if c[0] is True:
                    return b["then"], None
            return Missing("P1")
        args = [self.expr(x, owner) for x in e["args"]]
        bad = [a for a in args if isinstance(a, Missing)]
        if bad:
            return Missing(*set().union(*(b.why for b in bad)))
        op = e["op"]
        vs = [a[0] for a in args]
        if op in ("and", "or", "not"):
            if any(not isinstance(v, bool) for v in vs):
                return Missing("P6")
            return (all(vs) if op == "and" else any(vs) if op == "or" else not vs[0]), None
        if any(not isinstance(v, Fraction) for v in vs):
            return Missing("P6")
        units = [a[1] for a in args]
        declared = {u for u in units if u}
        if op != "mul" and len(declared) > 1:
            return Missing("P7")
        u = next(iter(declared), None)
        if op in CMP:
            return CMP[op](vs[0], vs[1]), None
        if op == "add":
            return sum(vs), u
        if op == "sub":
            return vs[0] - vs[1], u
        if op == "mul":
            r = Fraction(1)
            for v in vs:
                r *= v
            return r, u
        if op == "div":
            if vs[1] == 0:
                return Missing("P1")
            return vs[0] / vs[1], (None if units[0] and units[1] else u)
        return (min(vs) if op == "min" else max(vs)), u

    def rule(self, r: Rule):
        if r.kind == "formula":
            v = self.expr(r.body, r.node)
            return v if isinstance(v, Missing) else _plain(v[0])
        if r.kind in ("copy", "map"):
            p = r.body
            if not self.w.link(p["from_node"], p["to_node"]):
                return None
            v = self.w.nodes[p["from_node"]].get(p["from_attribute"])
            if r.kind == "copy":
                return v
            m = p.get("machine") or {}
            return (m.get("mapping") or {}).get(v, m.get("default")) if not isinstance(v, (dict, list)) else m.get("default")
        if r.kind == "justify":
            cfg = r.body
            ok = any(all(p in self.w.nodes and self.w.link(p, r.node) for p in j) for j in cfg["justifications"])
            return cfg.get("true_value", True) if ok else cfg.get("false_value", False)
        return self.combo(r)

    def combo(self, r: Rule):
        p = r.body
        cands = self.w.feeders(r.node)
        attrs = {c["attribute"] for c in p["constraints"]} | ({p["objective"]["attribute"]} if p.get("objective") else set())
        val = {}
        for s in cands:
            for a in attrs:
                q = _num(self.w.nodes[s].get(a))
                if q is None:
                    return {"status": Missing("P1"), "feasible_count": Missing("P1")}
                val[s, a] = q
        agg = {"sum": sum, "max": max, "min": min}
        feas = []
        for k in range(1, len(cands) + 1):
            for sub in itertools.combinations(cands, k):
                if all(CMP[c["op"]](agg[c["agg"]](val[s, c["attribute"]] for s in sub), _num(c["value"]))
                       for c in p["constraints"]):
                    feas.append(list(sub))
        out = {p.get("status_attribute", "status"): p.get("feasible_label", "FEASIBLE") if feas else p.get("infeasible_label", "INFEASIBLE"),
               "feasible_count": len(feas), "__feasible__": sorted(feas)}
        o = p.get("objective")
        if o:
            if not feas:
                out.update(selected=None, selected_value=None)
            else:
                score = {tuple(f): agg[o["agg"]](val[s, o["attribute"]] for s in f) for f in feas}
                best = (min if o.get("sense", "min") == "min" else max)(score.values())
                tops = sorted(list(f) for f, v in score.items() if v == best)
                out["selected_value"] = _plain(best)
                out["selected"] = tops[0] if len(tops) == 1 else Missing("P10")
                if len(tops) > 1:
                    out["__ties__"] = tops
        return out


# ---------------------------------------------------------------------------
# Dependency analysis + revision of one completion
# ---------------------------------------------------------------------------

def _reads(r: Rule, w: World) -> set:
    """Keys (node, attr) this rule reads in world w; ('*link*', node) marks
    dependence on which links enter `node`."""
    out: set = {("*link*", r.node)}
    if r.kind in ("copy", "map"):
        out.add((r.body["from_node"], r.body["from_attribute"]))
    elif r.kind == "justify":
        out |= {(p, "*exists*") for j in r.body["justifications"] for p in j}
    elif r.kind == "combo":
        attrs = {c["attribute"] for c in r.body["constraints"]} | ({r.body["objective"]["attribute"]} if r.body.get("objective") else set())
        out |= {(s, a) for s in w.feeders(r.node) for a in attrs}
    else:
        def walk(e):
            if isinstance(e, dict):
                for k in ("ref", "src"):
                    if k in e:
                        out.add(_split(e[k]))
                if "agg" in e:
                    out.update((s, e["attribute"]) for s in w.feeders(r.node))
                for v in e.values():
                    walk(v)
            elif isinstance(e, list):
                for v in e:
                    walk(v)
        walk(r.body)
    # A numeric attribute's unit is part of its value (`<attr>_unit`), so a
    # unit change must reach every rule that reads the attribute.
    out |= {(n, f"{a}_unit") for n, a in list(out) if not a.startswith("*")}
    return out


def _seeds(before: World, after: World) -> set:
    seeds = set()
    for n in set(before.nodes) | set(after.nodes):
        b, a = before.nodes.get(n), after.nodes.get(n)
        if b is None or a is None:
            seeds.add((n, "*exists*"))
            seeds |= {(n, k) for k in (b or a)}
            continue
        seeds |= {(n, k) for k in set(b) | set(a) if b.get(k) != a.get(k)}
    bl = {(e["source"], e["target"], _t(e["type"])) for e in before.edges}
    al = {(e["source"], e["target"], _t(e["type"])) for e in after.edges}
    seeds |= {("*link*", t) for s, t, _ in bl ^ al}
    return seeds


def revise_world(pre: World, post: World, rules: list[Rule], aux: dict, choice: dict) -> dict:
    """Stages 2–4 for one completion. Mutates `post`; returns a trace."""
    active = [r for r in rules if r.node in post.nodes and all(post.link(x, r.node) for x in r.when_linked)]
    by_key: dict[tuple, list[Rule]] = {}
    for r in active:
        by_key.setdefault((r.node, r.attr), []).append(r)
    chosen = {k: (v[0] if len(v) == 1 else next(x for x in v if x.idx == choice.get(f"P5:{k[0]}.{k[1]}", v[0].idx)))
              for k, v in by_key.items()}
    reads = {k: _reads(r, post) | _reads(r, pre) for k, r in chosen.items()}
    seeds = _seeds(pre, post)
    affected, frontier = set(), set(seeds)
    while frontier:  # downstream closure
        nxt = {k for k, rd in reads.items() if k not in affected and rd & frontier}
        affected |= nxt
        frontier = nxt
    ev = Eval(post, aux)
    order, cycles = _order(affected, reads)
    for comp in order:
        if len(comp) == 1 and comp[0] not in reads[comp[0]]:
            _set(post, chosen[comp[0]], ev.rule(chosen[comp[0]]))
        else:
            cycles.append(_fixed_point(comp, chosen, ev, post, aux))
    verified, repaired, outside = _verify(post, chosen, ev, affected)
    return {"choice": choice, "seeds": sorted(map(str, seeds)), "affected": sorted(f"{n}.{a}" for n, a in affected),
            "cycles": cycles, "verified": verified, "repaired": repaired, "violations_outside_scope": outside}


def _set(w: World, r: Rule, v):
    if r.kind == "combo":
        for k, x in v.items():
            if not k.startswith("__"):
                w.nodes[r.node][k] = x
        w.nodes[r.node]["__combo__"] = v
    else:
        w.nodes[r.node][r.attr] = v


def _order(keys: set, reads: dict):
    """Tarjan SCCs over the affected keys, dependencies first."""
    graph = {k: {d for d in reads[k] if d in keys} for k in keys}
    idx, low, stack, on, out, n = {}, {}, [], set(), [], [0]

    def go(v):
        idx[v] = low[v] = n[0]; n[0] += 1; stack.append(v); on.add(v)
        for w_ in sorted(graph[v]):
            if w_ not in idx:
                go(w_); low[v] = min(low[v], low[w_])
            elif w_ in on:
                low[v] = min(low[v], idx[w_])
        if low[v] == idx[v]:
            comp = []
            while True:
                x = stack.pop(); on.discard(x); comp.append(x)
                if x == v:
                    break
            out.append(sorted(comp))
    for k in sorted(keys):
        if k not in idx:
            go(k)
    return out, []


def _fixed_point(comp, chosen, ev: Eval, w: World, aux):
    names = [f"{n}.{a}" for n, a in comp]
    doms = [aux["domains"].get(x) for x in names]
    if any(d is None for d in doms):
        for n, a in comp:
            w.nodes[n][a] = Missing("P4")
        return {"keys": names, "fixed_points": None}
    sols = []
    for combo in itertools.product(*doms):
        for (n, a), v in zip(comp, combo):
            w.nodes[n][a] = v
        if all(ev.rule(chosen[k]) == v for k, v in zip(comp, combo)):
            sols.append(dict(zip(names, combo)))
    for i, (n, a) in enumerate(comp):
        w.nodes[n][a] = sols[0][names[i]] if len(sols) == 1 else Missing("P4")
    return {"keys": names, "fixed_points": sols}


def _verify(w: World, chosen, ev: Eval, affected):
    repaired, outside = [], []
    for _ in range(3):
        bad = []
        for k, r in chosen.items():
            cur = w.nodes[r.node].get("__combo__") if r.kind == "combo" else w.nodes[r.node].get(r.attr)
            if isinstance(cur, Missing):
                continue
            new = ev.rule(r)
            if r.kind == "combo":
                same = {x: y for x, y in (cur or {}).items()} == new
            else:
                same = new == cur
            if not same and not isinstance(new, Missing):
                bad.append((k, r, new))
        fix = [(k, r, v) for k, r, v in bad if k in affected]
        outside = sorted({f"{k[0]}.{k[1]}" for k, _, _ in bad if k not in affected})
        if not fix:
            return not bad, repaired, outside
        for k, r, v in fix:
            _set(w, r, v)
            repaired.append(f"{k[0]}.{k[1]}")
    return False, repaired, outside
