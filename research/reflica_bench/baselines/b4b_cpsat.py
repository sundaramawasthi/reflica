"""CP-SAT model building for B4b (Cats 5, 6, 7).

Deliberately independent of gt_engine.py: B4b encodes every declared
computation as a constraint in an OR-Tools CP-SAT model over fixed-point
integers (scale S = 10 000) and reads the solution back; the ground truth
evaluates the same rules with exact Python fractions. Agreement between
the two is therefore evidence, not tautology. Values that are not exact at
4 decimals (e.g. 2/3) come back truncated — the evaluator's tolerance bands
absorb this.

What B4b can and cannot notice (Cat 7, "partial abstention"):
  - missing input with no default (P1), non-numeric input (P6): the model
    cannot be built for that output → flagged.
  - contradictory constraints (conflicting claims P2, duplicate rules P5):
    UNSAT → the suspect outputs are flagged and the rest is re-solved.
  - more than one solution (cycles with several fixed points, P4): flagged.
  - unit mismatch (P7), ambiguous edge type (P3), ambiguous referent (P9),
    contradictory / invalid event (P8a/b), tied optimum (P10): not modelled,
    so B4b commits to an answer.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Any

from ortools.sat.python import cp_model

from ..schema import PROPAGATING_EDGE_TYPES

SCALE = 10_000
BIG = 10**9  # scaled bound: |value| <= 100 000; keeps products within int64
_CMP = {"ge", "gt", "le", "lt", "eq"}
_BOOL = {"and", "or", "not"} | _CMP


class _Missing(Exception):
    def __init__(self, codes: set[str]):
        super().__init__(codes)
        self.codes = set(codes)


def _linked(nodes: dict, edges: list[dict], s: str, t: str) -> bool:
    return s in nodes and any(
        e["source"] == s and e["target"] == t and e["type"] in PROPAGATING_EDGE_TYPES for e in edges
    )


def _scaled(x: Any) -> int:
    return int(Fraction(str(x)) * SCALE)


def _key(k: str) -> tuple[str, str]:
    n, _, a = k.partition(".")
    return n, a


def lower_rules(rules: dict) -> list[dict]:
    sat = (rules.get("satisfaction_functions") or {}).get("entries", {}) or {}
    out = [dict(c) for c in sat.get("computations", []) or []]
    for node, sf in (sat.get("status_functions", {}) or {}).items():
        out.append({"node": node, "attribute": sf.get("status_attribute", "status"),
                    "machine": {"case": [{"when": m["when"], "then": m["label"]} for m in sf["mapping"]]}})
    return out


class _Build:
    def __init__(self, nodes, edges, rules, comps, unknown, bad_inputs):
        self.m = cp_model.CpModel()
        self.nodes, self.edges, self.rules = nodes, edges, rules
        self.factors = ((rules.get("units") or {}).get("entries") or {}).get("factors", {}) or {}
        ev = (rules.get("evidence") or {}).get("entries") or {}
        self.claims = ev.get("claims", {}) or {}
        self.resolution = ev.get("resolution", {}) or {}
        self.domains = ((rules.get("fixed_point_semantics") or {}).get("entries") or {}).get("domains", {}) or {}
        self.comps = comps
        self.unknown = unknown
        self.bad_inputs = bad_inputs
        self.claim_vars: dict[tuple[str, str], Any] = {}
        self.out: dict[tuple[str, str], tuple[str, Any, list[str] | None]] = {}
        for c in comps:
            k = (c["node"], c["attribute"])
            if k in unknown or k in self.out:
                continue
            kind = self._kind(c["machine"], c["node"], {k})
            if kind == "label":
                labels = [b["then"] for b in c["machine"]["case"]]
                self.out[k] = ("label", self.m.NewIntVar(0, len(labels) - 1, f"{k}"), labels)
            elif kind == "bool":
                self.out[k] = ("bool", self.m.NewBoolVar(f"{k}"), None)
            else:
                self.out[k] = ("num", self.m.NewIntVar(-BIG, BIG, f"{k}"), None)

    # -- kinds -------------------------------------------------------------
    def _kind(self, e, owner, seen) -> str:
        if isinstance(e, bool):
            return "bool"
        if not isinstance(e, dict):
            return "num"
        if "case" in e:
            return "label"
        if "op" in e:
            return "bool" if e["op"] in _BOOL else "num"
        if "ref" in e or "src" in e:
            k = _key(e.get("ref") or e.get("src"))
            name = f"{k[0]}.{k[1]}"
            if name in self.domains and self.domains[name]:
                return "bool" if isinstance(self.domains[name][0], bool) else "num"
            comp = next((c for c in self.comps if (c["node"], c["attribute"]) == k), None)
            if comp is not None and k not in seen:
                return self._kind(comp["machine"], comp["node"], seen | {k})
            v = self.nodes.get(k[0], {}).get(k[1])
            if isinstance(v, bool):
                return "bool"
            if v is None and "default" in e:
                return self._kind(e["default"], owner, seen)
        return "num"

    # -- helpers -----------------------------------------------------------
    def lit(self, v: bool):
        b = self.m.NewBoolVar("c")
        self.m.Add(b == int(v))
        return b

    def var(self, expr):
        v = self.m.NewIntVar(-BIG, BIG, "t")
        self.m.Add(v == expr)
        return v

    def read(self, node, attr, default, owner):
        k = (node, attr)
        if k in self.unknown:
            raise _Missing(self.unknown[k])
        if k in self.out:
            kind, v, _ = self.out[k]
            return kind, v
        if k in self.bad_inputs:
            raise _Missing(self.bad_inputs[k])
        if node not in self.nodes or attr not in self.nodes[node]:
            if default is not None:
                return self.expr(default, owner)
            raise _Missing({"P1"})
        raw = self.nodes[node][attr]
        name = f"{node}.{attr}"
        if name in self.claims:
            res = self.resolution.get(name)
            if res and res.get("policy") == "prefer_source" and res["source"] != "graph":
                raw = next(c["value"] for c in self.claims[name] if c["source"] == res["source"])
            elif not res:
                if k not in self.claim_vars:
                    v = self.m.NewIntVar(-BIG, BIG, name)
                    for val in [raw] + [c["value"] for c in self.claims[name]]:
                        self.m.Add(v == _scaled(val))
                    self.claim_vars[k] = v
                return "num", self.claim_vars[k]
        if isinstance(raw, bool):
            return "bool", self.lit(raw)
        if not isinstance(raw, (int, float)):
            raise _Missing({"P6"})
        unit = self.nodes[node].get(f"{attr}_unit")
        factor = self.factors.get(unit, 1) if isinstance(unit, str) else 1
        return "num", _scaled(raw) * int(factor)

    # -- expressions -------------------------------------------------------
    def expr(self, e, owner):
        m = self.m
        if isinstance(e, bool):
            return "bool", self.lit(e)
        if isinstance(e, (int, float)):
            return "num", _scaled(e)
        if not isinstance(e, dict):
            raise _Missing({"P6"})
        if "ref" in e:
            n, a = _key(e["ref"])
            return self.read(n, a, e.get("default"), owner)
        if "src" in e:
            n, a = _key(e["src"])
            if not _linked(self.nodes, self.edges, n, owner):
                if e.get("default") is not None:
                    return self.expr(e["default"], owner)
                raise _Missing({"P1"})
            return self.read(n, a, e.get("default"), owner)
        if "agg" in e:
            srcs = sorted(s for s in self.nodes if _linked(self.nodes, self.edges, s, owner))
            xs = [self.read(s, e["attribute"], None, owner)[1] for s in srcs]
            if e["agg"] == "count":
                return "num", len(xs) * SCALE
            if not xs:
                return "num", _scaled(e.get("empty", 0))
            if e["agg"] == "sum":
                return "num", sum(xs)
            t = m.NewIntVar(-BIG, BIG, "agg")
            (m.AddMaxEquality if e["agg"] == "max" else m.AddMinEquality)(t, xs)
            return "num", t
        if "case" in e:
            labels = [b["then"] for b in e["case"]]
            idx = m.NewIntVar(0, len(labels) - 1, "case")
            prev = []
            for i, b in enumerate(e["case"]):
                c = self.lit(True) if b["when"] == "otherwise" else self.expr(b["when"], owner)[1]
                s = m.NewBoolVar("sel")
                m.AddBoolAnd([c] + [p.Not() for p in prev]).OnlyEnforceIf(s)
                m.AddBoolOr([c.Not()] + prev).OnlyEnforceIf(s.Not())
                m.Add(idx == i).OnlyEnforceIf(s)
                prev.append(c)
            return "label", idx
        op = e["op"]
        args = [self.expr(a, owner) for a in e["args"]]
        vals = [a[1] for a in args]
        if op in ("and", "or"):
            b = m.NewBoolVar(op)
            if op == "and":
                m.AddBoolAnd(vals).OnlyEnforceIf(b)
                m.AddBoolOr([v.Not() for v in vals]).OnlyEnforceIf(b.Not())
            else:
                m.AddBoolOr(vals).OnlyEnforceIf(b)
                m.AddBoolAnd([v.Not() for v in vals]).OnlyEnforceIf(b.Not())
            return "bool", b
        if op == "not":
            return "bool", vals[0].Not()
        if any(a[0] != "num" for a in args):
            raise _Missing({"P6"})
        if op in _CMP:
            b = m.NewBoolVar(op)
            l, r = vals
            pos = {"ge": l >= r, "gt": l > r, "le": l <= r, "lt": l < r, "eq": l == r}[op]
            neg = {"ge": l < r, "gt": l <= r, "le": l > r, "lt": l >= r, "eq": l != r}[op]
            m.Add(pos).OnlyEnforceIf(b)
            m.Add(neg).OnlyEnforceIf(b.Not())
            return "bool", b
        if op == "add":
            return "num", sum(vals)
        if op == "sub":
            return "num", vals[0] - vals[1]
        if op in ("min", "max"):
            t = m.NewIntVar(-BIG, BIG, op)
            (m.AddMinEquality if op == "min" else m.AddMaxEquality)(t, [self.var(v) if not isinstance(v, int) else v for v in vals])
            return "num", t
        if op == "mul":
            acc = vals[0]
            for v in vals[1:]:
                t = m.NewIntVar(-BIG, BIG, "mul")
                if isinstance(v, int):
                    m.AddDivisionEquality(t, acc * v, SCALE)
                elif isinstance(acc, int):
                    m.AddDivisionEquality(t, v * acc, SCALE)
                else:
                    p = m.NewIntVar(-BIG * BIG, BIG * BIG, "prod")
                    m.AddMultiplicationEquality(p, [self.var(acc), self.var(v)])
                    m.AddDivisionEquality(t, p, SCALE)
                acc = t
            return "num", acc
        if op == "div":
            d = m.NewIntVarFromDomain(cp_model.Domain.FromIntervals([[-BIG, -1], [1, BIG]]), "den")
            m.Add(d == vals[1])
            t = m.NewIntVar(-BIG, BIG, "div")
            m.AddDivisionEquality(t, vals[0] * SCALE, d)
            return "num", t
        raise _Missing({"P6"})


class _Collector(cp_model.CpSolverSolutionCallback):
    def __init__(self, out, limit=8):
        super().__init__()
        self.out, self.limit, self.solutions = out, limit, []

    def on_solution_callback(self) -> None:
        self.solutions.append({k: self.Value(v) for k, (_, v, _) in self.out.items()})
        if len(self.solutions) >= self.limit:
            self.StopSearch()


def _active(nodes, edges, comps):
    return [c for c in comps if c["node"] in nodes
            and all(_linked(nodes, edges, w, c["node"]) for w in c.get("when_linked", []))]


def solve_computations(nodes: dict, edges: list[dict], rules: dict):
    """Returns (values {(node, attr): value}, unknown {(node, attr): codes})."""
    comps = _active(nodes, edges, lower_rules(rules))
    if not comps:
        return {}, {}
    unknown: dict[tuple[str, str], set[str]] = {}
    bad_inputs: dict[tuple[str, str], set[str]] = {}
    for _round in range(6):
        b = _Build(nodes, edges, rules, comps, unknown, bad_inputs)
        restart = False
        for c in comps:
            k = (c["node"], c["attribute"])
            if k in unknown:
                continue
            try:
                kind, e = b.expr(c["machine"], c["node"])
            except _Missing as miss:
                unknown[k] = miss.codes
                restart = True
                break
            b.m.Add(b.out[k][1] == e)
        if restart:
            continue
        solver = cp_model.CpSolver()
        solver.parameters.num_workers = 1
        solver.parameters.enumerate_all_solutions = True
        col = _Collector(b.out)
        status = solver.Solve(b.m, col)
        if status == cp_model.INFEASIBLE:
            dup = {}
            for c in comps:
                k = (c["node"], c["attribute"])
                dup[k] = dup.get(k, 0) + 1
            new = {k: {"P5"} for k, n in dup.items() if n > 1 and k not in unknown}
            for name in b.claims:
                if name not in b.resolution:
                    bad_inputs[_key(name)] = {"P2"}
            if not new and not bad_inputs:
                return {}, {k: {"UNSAT"} for k in b.out}
            unknown.update(new)
            continue
        sols = col.solutions
        varying = {k for k in b.out if len({s[k] for s in sols}) > 1}
        if varying:
            unknown.update({k: {"P4"} for k in varying})
            continue
        values = {}
        for k, (kind, _, labels) in b.out.items():
            raw = sols[0][k]
            if kind == "bool":
                values[k] = bool(raw)
            elif kind == "label":
                values[k] = labels[raw]
            else:
                x = Fraction(raw, SCALE)
                values[k] = int(x) if x.denominator == 1 else round(float(x), 4)
        return values, {**unknown, **bad_inputs}
    return {}, {**unknown, **bad_inputs}


def solve_combination(nodes: dict, edges: list[dict], rules: dict):
    """C6-B via CP-SAT: enumerate feasible subsets, then optimise.

    Returns None when no problem is declared, else a dict with
    `conclusion`, `attrs` (conclusion attribute updates), `feasible`,
    `search_cost`, `unknown` (codes or None).
    """
    problems = ((rules.get("combination_selection") or {}).get("entries") or {}).get("problems", {}) or {}
    if not problems:
        return None
    (concl, p), = problems.items()
    if concl not in nodes:
        return None
    cands = sorted(s for s in nodes if _linked(nodes, edges, s, concl))
    attrs = {c["attribute"] for c in p["constraints"]} | ({p["objective"]["attribute"]} if p.get("objective") else set())
    data = {}
    for s in cands:
        for a in attrs:
            v = nodes[s].get(a)
            if isinstance(v, bool) or not isinstance(v, (int, float)):
                return {"conclusion": concl, "attrs": {}, "feasible": None, "search_cost": 0, "unknown": {"P1"}}
            data[(s, a)] = _scaled(v)

    def build():
        m = cp_model.CpModel()
        x = {s: m.NewBoolVar(s) for s in cands}
        m.AddBoolOr(list(x.values()))
        for c in p["constraints"]:
            a, opn, rhs = c["attribute"], c["op"], _scaled(c["value"])
            if c["agg"] == "sum":
                tot = sum(x[s] * data[(s, a)] for s in cands)
                m.Add({"ge": tot >= rhs, "gt": tot > rhs, "le": tot <= rhs, "lt": tot < rhs, "eq": tot == rhs}[opn])
                continue
            ok = {s: {"ge": data[(s, a)] >= rhs, "gt": data[(s, a)] > rhs, "le": data[(s, a)] <= rhs,
                      "lt": data[(s, a)] < rhs, "eq": data[(s, a)] == rhs}[opn] for s in cands}
            every = (c["agg"] == "max" and opn in ("le", "lt")) or (c["agg"] == "min" and opn in ("ge", "gt"))
            if every:  # every chosen member must satisfy
                for s in cands:
                    if not ok[s]:
                        m.Add(x[s] == 0)
            else:  # at least one chosen member must satisfy
                m.AddBoolOr([x[s] for s in cands if ok[s]])
        return m, x

    m, x = build()
    solver = cp_model.CpSolver()
    solver.parameters.num_workers = 1
    solver.parameters.enumerate_all_solutions = True
    found: list[list[str]] = []

    class CB(cp_model.CpSolverSolutionCallback):
        def on_solution_callback(self_inner):
            found.append(sorted(s for s in cands if self_inner.Value(x[s])))

    solver.Solve(m, CB())
    feasible = sorted(found)
    cost = int(solver.NumBranches()) + len(found)
    out = {p.get("status_attribute", "status"): p.get("feasible_label", "FEASIBLE") if feasible else p.get("infeasible_label", "INFEASIBLE"),
           "feasible_count": len(feasible)}
    obj = p.get("objective")
    if obj:
        if not feasible:
            out["selected"], out["selected_value"] = None, None
        else:
            m2, x2 = build()
            term = sum(x2[s] * data[(s, obj["attribute"])] for s in cands)
            (m2.Minimize if obj.get("sense", "min") == "min" else m2.Maximize)(term)
            s2 = cp_model.CpSolver()
            s2.parameters.num_workers = 1
            s2.Solve(m2)
            cost += int(s2.NumBranches())
            out["selected"] = sorted(s for s in cands if s2.Value(x2[s]))
            val = Fraction(int(s2.ObjectiveValue()), SCALE)
            out["selected_value"] = int(val) if val.denominator == 1 else float(val)
    return {"conclusion": concl, "attrs": out, "feasible": feasible, "search_cost": cost, "unknown": None}
