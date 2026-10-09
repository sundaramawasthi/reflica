"""Direct-Python reference evaluator for Categories 5, 6 and 7.

Used ONLY by the ground-truth generator. B4b computes the same quantities
through an OR-Tools CP-SAT model (baselines/b4b_cpsat.py); the two never
share code, which breaks the ground-truth / B4b circularity flagged in the
Cat 4 audit.

Arithmetic is exact (fractions.Fraction) and rounded to 6 decimals only on
output. A value that cannot be determined is represented by `Unknown`,
carrying the pathology codes (P1..P10) that caused it.

Expression grammar (the `machine` form of every computation):

    literal                      number / bool / string / null
    {"ref": "N.a", "default": e} attribute a of node N (default if missing)
    {"src": "N.a", "default": e} as ref, but only while N has a propagating
                                 edge into the computation's own node
    {"agg": "sum|max|min|count", "attribute": "a", "empty": v}
                                 combine attribute a over every node with a
                                 propagating edge into the computation's node
    {"op": "add|sub|mul|div|min|max|ge|gt|le|lt|eq|and|or|not", "args": [..]}
    {"case": [{"when": e | "otherwise", "then": label}, ...]}
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass, field
from fractions import Fraction
from typing import Any

from .schema import PROPAGATING_EDGE_TYPES, Rules


class Unknown:
    __slots__ = ("codes",)

    def __init__(self, codes: set[str] | frozenset[str]):
        self.codes = frozenset(codes)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Unknown) and other.codes == self.codes

    def __hash__(self) -> int:
        return hash(self.codes)

    def __repr__(self) -> str:
        return f"Unknown({sorted(self.codes)})"


@dataclass
class _V:
    """A value plus its unit (None = dimensionless / undeclared)."""

    v: Any
    unit: str | None = None


@dataclass
class EvalResult:
    nodes: dict[str, dict[str, Any]]
    fixed_point_analysis: dict[str, Any] = field(default_factory=dict)
    combination: dict[str, Any] | None = None
    no_fixed_point: set[tuple[str, str]] = field(default_factory=set)


# ---------------------------------------------------------------------------
# Rule extraction
# ---------------------------------------------------------------------------

def computations_of(rules: Rules) -> list[dict]:
    """Computations + status functions (lowered to `case` computations)."""
    entries = rules.satisfaction_functions.entries or {}
    out = [dict(c) for c in entries.get("computations", [])]
    for node, sf in (entries.get("status_functions", {}) or {}).items():
        out.append(
            {
                "node": node,
                "attribute": sf.get("status_attribute", "status"),
                "machine": {
                    "case": [{"when": m["when"], "then": m["label"]} for m in sf["mapping"]]
                },
                "human": sf.get("human", ""),
                "role": "status",
            }
        )
    return out


def status_attributes_of(rules: Rules) -> dict[str, str]:
    entries = rules.satisfaction_functions.entries or {}
    out = {
        n: sf.get("status_attribute", "status")
        for n, sf in (entries.get("status_functions", {}) or {}).items()
    }
    for n, p in (rules.combination_selection.entries.get("problems", {}) or {}).items():
        out[n] = p.get("status_attribute", "status")
    return out


def top_label_of(rules: Rules, node: str) -> str | None:
    entries = rules.satisfaction_functions.entries or {}
    sf = (entries.get("status_functions", {}) or {}).get(node)
    if sf:
        return sf["mapping"][0]["label"]
    p = (rules.combination_selection.entries.get("problems", {}) or {}).get(node)
    if p:
        return p.get("feasible_label", "FEASIBLE")
    return None


def split_key(key: str) -> tuple[str, str]:
    node, _, attr = key.partition(".")
    return node, attr


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------

def linked(nodes: dict, edges: list[dict], source: str, target: str) -> bool:
    if source not in nodes:
        return False
    return any(
        e["source"] == source and e["target"] == target and e["type"] in PROPAGATING_EDGE_TYPES
        for e in edges
    )


def _num(x: Any) -> Fraction | None:
    if isinstance(x, bool) or not isinstance(x, (int, float, Fraction)):
        return None
    return Fraction(str(x)) if isinstance(x, float) else Fraction(x)


def out_value(x: Any) -> Any:
    if isinstance(x, Fraction):
        if x.denominator == 1:
            return int(x)
        return round(float(x), 6)
    return x


class _Evaluator:
    def __init__(self, nodes, edges, rules: Rules, choices: dict[str, Any]):
        self.nodes = nodes
        self.edges = edges
        self.rules = rules
        self.choices = choices
        self.factors = (rules.units.entries or {}).get("factors", {}) or {}
        ev = rules.evidence.entries or {}
        self.claims = ev.get("claims", {}) or {}
        self.resolution = ev.get("resolution", {}) or {}

    # -- reading ------------------------------------------------------------
    def read(self, node: str, attr: str, default: Any, owner: str) -> Any:
        if node not in self.nodes or attr not in self.nodes[node]:
            if default is not None:
                return self.eval(default, owner)
            return Unknown({"P1"})
        raw = self.nodes[node][attr]
        if isinstance(raw, Unknown):
            return raw
        unit = self.nodes[node].get(f"{attr}_unit")
        unit = unit if isinstance(unit, str) else None
        if unit is not None and unit in self.factors:
            n = _num(raw)
            if n is not None:
                return _V(n * _num(self.factors[unit]), "__base__")
        return _V(raw, unit)

    # -- expressions --------------------------------------------------------
    def eval(self, e: Any, owner: str) -> Any:
        if not isinstance(e, dict):
            return _V(e)
        if "ref" in e:
            n, a = split_key(e["ref"])
            return self.read(n, a, e.get("default"), owner)
        if "src" in e:
            n, a = split_key(e["src"])
            if not linked(self.nodes, self.edges, n, owner):
                if "default" in e and e["default"] is not None:
                    return self.eval(e["default"], owner)
                return Unknown({"P1"})
            return self.read(n, a, e.get("default"), owner)
        if "agg" in e:
            srcs = sorted(s for s in self.nodes if linked(self.nodes, self.edges, s, owner))
            vals = [self.read(s, e["attribute"], None, owner) for s in srcs]
            unk = [v for v in vals if isinstance(v, Unknown)]
            if unk:
                return Unknown(frozenset().union(*(u.codes for u in unk)))
            if e["agg"] == "count":
                return _V(Fraction(len(vals)))
            if not vals:
                return _V(e.get("empty", 0))
            nums = [_num(v.v) for v in vals]
            if any(n is None for n in nums):
                return Unknown({"P6"})
            units = {v.unit for v in vals if v.unit is not None}
            if len(units) > 1:
                return Unknown({"P7"})
            unit = next(iter(units)) if units else None
            fn = {"sum": sum, "max": max, "min": min}[e["agg"]]
            return _V(fn(nums), unit)
        if "case" in e:
            for branch in e["case"]:
                if branch["when"] == "otherwise":
                    return _V(branch["then"])
                c = self.eval(branch["when"], owner)
                if isinstance(c, Unknown):
                    return c
                if c.v is True:
                    return _V(branch["then"])
            return Unknown({"P1"})
        if "op" in e:
            return self._op(e["op"], [self.eval(a, owner) for a in e["args"]])
        raise ValueError(f"unknown expression form: {e}")

    def _op(self, op: str, args: list[Any]) -> Any:
        unk = [a for a in args if isinstance(a, Unknown)]
        if unk:
            return Unknown(frozenset().union(*(u.codes for u in unk)))
        if op in ("and", "or", "not"):
            bs = [a.v for a in args]
            if any(not isinstance(b, bool) for b in bs):
                return Unknown({"P6"})
            if op == "and":
                return _V(all(bs))
            if op == "or":
                return _V(any(bs))
            return _V(not bs[0])
        nums = [_num(a.v) for a in args]
        if any(n is None for n in nums):
            return Unknown({"P6"})
        units = [a.unit for a in args]
        declared = {u for u in units if u is not None}
        if op in ("add", "sub", "min", "max", "ge", "gt", "le", "lt", "eq", "div") and len(declared) > 1:
            return Unknown({"P7"})
        unit = next(iter(declared)) if declared else None
        a = nums
        if op == "add":
            return _V(sum(a), unit)
        if op == "sub":
            return _V(a[0] - a[1], unit)
        if op == "mul":
            r = Fraction(1)
            for x in a:
                r *= x
            return _V(r, unit)
        if op == "div":
            if a[1] == 0:
                return Unknown({"P1"})
            both = units[0] is not None and units[1] is not None
            return _V(a[0] / a[1], None if both else unit)
        if op == "min":
            return _V(min(a), unit)
        if op == "max":
            return _V(max(a), unit)
        cmp = {
            "ge": a[0] >= a[1] if len(a) == 2 else None,
            "gt": a[0] > a[1] if len(a) == 2 else None,
            "le": a[0] <= a[1] if len(a) == 2 else None,
            "lt": a[0] < a[1] if len(a) == 2 else None,
            "eq": a[0] == a[1] if len(a) == 2 else None,
        }
        if op in cmp:
            return _V(cmp[op])
        raise ValueError(f"unknown op {op}")

    # -- dependency collection ---------------------------------------------
    def deps(self, e: Any, owner: str, out: set[tuple[str, str]]) -> None:
        if not isinstance(e, dict):
            return
        if "ref" in e:
            out.add(split_key(e["ref"]))
            self.deps(e.get("default"), owner, out)
        elif "src" in e:
            n, a = split_key(e["src"])
            if linked(self.nodes, self.edges, n, owner):
                out.add((n, a))
            self.deps(e.get("default"), owner, out)
        elif "agg" in e:
            for s in self.nodes:
                if linked(self.nodes, self.edges, s, owner):
                    out.add((s, e["attribute"]))
        elif "case" in e:
            for b in e["case"]:
                if b["when"] != "otherwise":
                    self.deps(b["when"], owner, out)
        elif "op" in e:
            for x in e["args"]:
                self.deps(x, owner, out)


def active_computations(nodes, edges, rules: Rules) -> list[tuple[int, dict]]:
    out = []
    for i, c in enumerate(computations_of(rules)):
        if c["node"] not in nodes:
            continue
        if all(linked(nodes, edges, w, c["node"]) for w in c.get("when_linked", [])):
            out.append((i, c))
    return out


def duplicate_targets(nodes, edges, rules: Rules) -> dict[tuple[str, str], list[int]]:
    by_key: dict[tuple[str, str], list[int]] = {}
    for i, c in active_computations(nodes, edges, rules):
        by_key.setdefault((c["node"], c["attribute"]), []).append(i)
    return {k: v for k, v in by_key.items() if len(v) > 1}


def _sccs(graph: dict[Any, set[Any]]) -> list[list[Any]]:
    """Tarjan; returns SCCs in dependency-first (topological) order."""
    index: dict[Any, int] = {}
    low: dict[Any, int] = {}
    stack: list[Any] = []
    on: set[Any] = set()
    out: list[list[Any]] = []
    counter = [0]

    def visit(v: Any) -> None:
        index[v] = low[v] = counter[0]
        counter[0] += 1
        stack.append(v)
        on.add(v)
        for w in sorted(graph.get(v, ())):
            if w not in index:
                visit(w)
                low[v] = min(low[v], low[w])
            elif w in on:
                low[v] = min(low[v], index[w])
        if low[v] == index[v]:
            comp = []
            while True:
                w = stack.pop()
                on.discard(w)
                comp.append(w)
                if w == v:
                    break
            out.append(sorted(comp))

    for v in sorted(graph):
        if v not in index:
            visit(v)
    return out


def evaluate_state(
    nodes: dict[str, dict[str, Any]],
    edges: list[dict],
    rules: Rules,
    choices: dict[str, Any] | None = None,
) -> EvalResult:
    """Evaluate every computation, status function and combination problem
    on the given state. `nodes` is copied, never mutated."""
    choices = choices or {}
    vals = {n: dict(a) for n, a in nodes.items()}
    ev = _Evaluator(vals, edges, rules, choices)

    # Evidence: conflicting claims are resolved by declared rule or by the
    # completion's choice; otherwise left to the caller (choice points).
    for key, claims in ev.claims.items():
        n, a = split_key(key)
        if n not in vals:
            continue
        res = ev.resolution.get(key)
        chosen = choices.get(f"P2:{key}")
        if res and res.get("policy") == "prefer_source":
            if res["source"] != "graph":
                for c in claims:
                    if c["source"] == res["source"]:
                        vals[n][a] = c["value"]
        elif chosen is not None:
            vals[n][a] = chosen

    active = active_computations(vals, edges, rules)
    by_key: dict[tuple[str, str], list[dict]] = {}
    for i, c in active:
        by_key.setdefault((c["node"], c["attribute"]), []).append((i, c))
    chosen_comp: dict[tuple[str, str], dict] = {}
    for key, lst in by_key.items():
        if len(lst) == 1:
            chosen_comp[key] = lst[0][1]
        else:
            pick = choices.get(f"P5:{key[0]}.{key[1]}", lst[0][0])
            chosen_comp[key] = next(c for i, c in lst if i == pick)

    graph: dict[tuple[str, str], set[tuple[str, str]]] = {}
    for key, c in chosen_comp.items():
        d: set[tuple[str, str]] = set()
        ev.deps(c["machine"], c["node"], d)
        graph[key] = {x for x in d if x in chosen_comp}

    result = EvalResult(nodes=vals)
    fp_domains = (rules.fixed_point_semantics.entries or {}).get("domains", {}) or {}

    def assign(key: tuple[str, str], value: Any) -> None:
        if isinstance(value, _V):
            value = out_value(value.v)
        vals[key[0]][key[1]] = value

    for comp in _sccs(graph):
        cyclic = len(comp) > 1 or comp[0] in graph.get(comp[0], set())
        if not cyclic:
            key = comp[0]
            c = chosen_comp[key]
            assign(key, ev.eval(c["machine"], c["node"]))
            continue
        names = [f"{k[0]}.{k[1]}" for k in comp]
        if not all(n in fp_domains for n in names):
            for k in comp:
                vals[k[0]][k[1]] = Unknown({"P4"})
            result.fixed_point_analysis["|".join(names)] = {"fixed_points": None}
            continue
        fixed: list[dict[str, Any]] = []
        for combo in itertools.product(*(fp_domains[n] for n in names)):
            for k, v in zip(comp, combo):
                vals[k[0]][k[1]] = v
            ok = True
            for k, v in zip(comp, combo):
                c = chosen_comp[k]
                r = ev.eval(c["machine"], c["node"])
                if isinstance(r, Unknown) or out_value(r.v) != v:
                    ok = False
                    break
            if ok:
                fixed.append(dict(zip(names, combo)))
        result.fixed_point_analysis["|".join(names)] = {"fixed_points": fixed}
        if len(fixed) == 1:
            for k, n in zip(comp, names):
                vals[k[0]][k[1]] = fixed[0][n]
        else:
            for k in comp:
                vals[k[0]][k[1]] = Unknown({"P4"})
            if not fixed:
                result.no_fixed_point.update(comp)

    result.combination = _evaluate_combinations(vals, edges, rules)
    return result


# ---------------------------------------------------------------------------
# Combination selection (Cat 6-B, Cat 7 P10) — exhaustive enumeration
# ---------------------------------------------------------------------------

def _cmp(op: str, a: Fraction, b: Fraction) -> bool:
    return {"ge": a >= b, "gt": a > b, "le": a <= b, "lt": a < b, "eq": a == b}[op]


def _evaluate_combinations(vals, edges, rules: Rules) -> dict[str, Any] | None:
    problems = (rules.combination_selection.entries or {}).get("problems", {}) or {}
    if not problems:
        return None
    (conclusion, p), = problems.items()
    if conclusion not in vals:
        return None
    cands = sorted(s for s in vals if linked(vals, edges, s, conclusion))
    attrs = {c["attribute"] for c in p["constraints"]}
    if p.get("objective"):
        attrs.add(p["objective"]["attribute"])
    data: dict[str, dict[str, Fraction]] = {}
    for s in cands:
        data[s] = {}
        for a in attrs:
            n = _num(vals[s].get(a))
            if n is None:
                for k in ("status", "feasible_count", "selected", "selected_value"):
                    vals[conclusion][k] = Unknown({"P1"})
                return {"conclusion": conclusion, "candidates": cands, "feasible": None}
            data[s][a] = n

    def agg(kind: str, members: tuple[str, ...], a: str) -> Fraction:
        xs = [data[m][a] for m in members]
        return {"sum": sum, "max": max, "min": min}[kind](xs)

    feasible: list[list[str]] = []
    for k in range(1, len(cands) + 1):
        for members in itertools.combinations(cands, k):
            if all(
                _cmp(c["op"], agg(c["agg"], members, c["attribute"]), _num(c["value"]))
                for c in p["constraints"]
            ):
                feasible.append(list(members))
    feasible.sort()
    status_attr = p.get("status_attribute", "status")
    vals[conclusion][status_attr] = (
        p.get("feasible_label", "FEASIBLE") if feasible else p.get("infeasible_label", "INFEASIBLE")
    )
    vals[conclusion]["feasible_count"] = len(feasible)
    info: dict[str, Any] = {"conclusion": conclusion, "candidates": cands, "feasible": feasible}
    obj = p.get("objective")
    if obj:
        if not feasible:
            vals[conclusion]["selected"] = None
            vals[conclusion]["selected_value"] = None
            info["optima"] = []
        else:
            scored = [(agg(obj["agg"], tuple(m), obj["attribute"]), m) for m in feasible]
            best = (min if obj.get("sense", "min") == "min" else max)(s for s, _ in scored)
            optima = sorted(m for s, m in scored if s == best)
            info["optima"] = optima
            info["objective_value"] = out_value(best)
            vals[conclusion]["selected_value"] = out_value(best)
            vals[conclusion]["selected"] = optima[0] if len(optima) == 1 else Unknown({"P10"})
    return info
