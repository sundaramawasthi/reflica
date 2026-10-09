"""R-N (natural-language) layer.

  * Freeze: SHA-256 manifest of the 63 canonical scenarios. R-N files live in
    a separate tree (reflica_bench/rn/) and never modify canonical files.
  * Renderer: deterministic template prose from canonical_input ONLY (graph,
    rules, event). It never reads ground_truth, category, subcategory,
    template_id or evaluation_annotations.
  * Leakage checker: rejects outcome / ambiguity vocabulary, P-codes,
    template ids, and any number that exists only in the post-event answer.

The alias map (display label → node id) is evaluator-only; it is stored in
the R-N file but never passed to a method (see NaturalLanguageAdapter_v1).
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict

from .schema import PROPAGATING_EDGE_TYPES, MethodInputNaturalLanguage, Operation, Scenario, TargetKind

RENDER_VERSION = "rn-template-1.0.0"
PKG = Path(__file__).parent
MANIFEST = PKG / "frozen_manifest.json"
RN_DIR = PKG / "rn"

PILOT_IDS = [
    "cat1_edit_attribute_irrelevance_001", "cat1_relchange_nonprop_001",
    "cat2_pair_edit_001", "cat2_delete_premise_001",
    "cat3_linear_chain_edit_001", "cat3_early_termination_edit_001",
    "cat4_diamond_delete_preservation_001", "cat4_shared_premise_delete_negative_001",
    "cat5_threshold_partial_partial_001", "cat5_no_crossing_control_001",
    "cat6a_compensation_edit_001", "cat6b_optimal_selection_edit_001",
    "cat7_conflicting_evidence_edit_001", "cat7_conflict_with_resolution_001",
    "cat7_ambiguous_referent_001", "cat7_referent_resolved_001",
]


class RNScenario(BaseModel):
    model_config = ConfigDict(extra="forbid")
    source_scenario_id: str
    source_sha256: str
    render_version: str
    method_input: MethodInputNaturalLanguage
    alias_map: dict[str, str]  # evaluator-only: display label -> node id


# ---------------------------------------------------------------------------
# Freeze
# ---------------------------------------------------------------------------

def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_files() -> list[Path]:
    return sorted((PKG / "scenarios").glob("cat*/*.json"))


def compute_manifest() -> dict[str, Any]:
    files = {str(p.relative_to(PKG)): _sha(p) for p in canonical_files()}
    return {"count": len(files), "files": files}


def write_manifest() -> None:
    MANIFEST.write_text(json.dumps(compute_manifest(), indent=2) + "\n")


def verify_manifest() -> list[str]:
    frozen = json.loads(MANIFEST.read_text())
    now = compute_manifest()
    diffs = [f"count {frozen['count']} -> {now['count']}"] if frozen["count"] != now["count"] else []
    for k in sorted(set(frozen["files"]) | set(now["files"])):
        if frozen["files"].get(k) != now["files"].get(k):
            diffs.append(f"changed/added/removed: {k}")
    return diffs


def source_path(scenario_id: str) -> Path:
    for p in canonical_files():
        if json.loads(p.read_text())["scenario_id"] == scenario_id:
            return p
    raise KeyError(scenario_id)


# ---------------------------------------------------------------------------
# Renderer
# ---------------------------------------------------------------------------

GLOSSARY = (
    "Link kinds: 'requires', 'supports', 'causes', 'blocks', 'enables' and 'derived_from' "
    "carry influence from the first entity to the second; 'informs' and 'references' "
    "do not carry influence. An 'influencing link into X' means one of the first kind ending at X."
)


_ROLE_TYPES = {"conclusion", "generic", "premise"}  # role words, not domain types


def _fmt(v: Any) -> str:
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, str):
        return f'"{v}"'
    if isinstance(v, list):
        return "[" + ", ".join(_fmt(x) for x in v) + "]"
    if v is None:
        return "unset"
    return repr(v) if isinstance(v, float) else str(v)


class _Renderer:
    def __init__(self, sc: Scenario):
        self.sc = sc
        # Labels never reuse node ids (ids such as `unrelated_U` or `loop_P`
        # would hint at the answer). A node's own `name` is used when unique;
        # otherwise a neutral E1, E2, … in graph order.
        nodes = list(sc.canonical_input.graph.nodes)
        if sc.canonical_input.event.new_node is not None:
            nodes.append(sc.canonical_input.event.new_node)
        names = [n.attributes.get("name") for n in nodes]
        self.L = {}
        for k, n in enumerate(nodes, 1):
            nm = n.attributes.get("name")
            unique = isinstance(nm, str) and names.count(nm) == 1 and nm.strip()
            self.L[n.id] = nm if unique else f"E{k}"
        if len(set(self.L.values())) != len(self.L):
            self.L = {n.id: f"E{k}" for k, n in enumerate(nodes, 1)}

    def ref(self, key: str) -> str:
        n, _, a = key.partition(".")
        return f"{a} of {self.L.get(n, n)}"

    def expr(self, e: Any, owner: str) -> str:
        if not isinstance(e, dict):
            return _fmt(e)
        if "ref" in e:
            s = self.ref(e["ref"])
            return s if e.get("default") is None else f"({s}, or {self.expr(e['default'], owner)} if missing)"
        if "src" in e:
            n = e["src"].split(".")[0]
            alt = self.expr(e["default"], owner) if e.get("default") is not None else "undefined"
            return (f"[{self.ref(e['src'])}, counted only while {self.L.get(n, n)} has an influencing "
                    f"link into {self.L[owner]}; otherwise {alt}]")
        if "agg" in e:
            what = "number" if e["agg"] == "count" else f"{e['agg']} of {e['attribute']}"
            return (f"the {what} over all entities with an influencing link into {self.L[owner]} "
                    f"({_fmt(e.get('empty', 0))} if there are none)")
        if "case" in e:
            parts = [f"{_fmt(b['then'])} if {self.expr(b['when'], owner)}" for b in e["case"][:-1]]
            return "; ".join(parts) + f"; otherwise {_fmt(e['case'][-1]['then'])}"
        a = [self.expr(x, owner) for x in e["args"]]
        sym = {"add": " + ", "sub": " − ", "mul": " × ", "div": " ÷ ", "ge": " ≥ ", "gt": " > ",
               "le": " ≤ ", "lt": " < ", "eq": " = ", "and": " and ", "or": " or "}
        op = e["op"]
        if op in sym:
            return "(" + sym[op].join(a) + ")"
        if op == "not":
            return f"not {a[0]}"
        return f"the {'smaller' if op == 'min' else 'larger'} of ({', '.join(a)})"

    def plan(self) -> str:
        ci = self.sc.canonical_input
        out = ["Entities:"]
        for n in ci.graph.nodes:
            attrs = "; ".join(f"{k} = {_fmt(v)}" for k, v in n.attributes.items()) or "no attributes"
            kind = [] if n.type in _ROLE_TYPES else [n.type]
            if n.state:
                kind.append(f"state: {n.state}")
            out.append(f"- {self.L[n.id]}{' (' + ', '.join(kind) + ')' if kind else ''}: {attrs}.")
        out.append("Links:")
        out += [f"- {self.L[e.source]} → {self.L[e.target]} ({e.type.value})." for e in ci.graph.edges] or ["- none."]
        out.append(GLOSSARY)
        out.append("Rules:")
        out += self._rules()
        return "\n".join(out)

    def _rules(self) -> list[str]:
        r = self.sc.canonical_input.rules
        lines: list[str] = []
        for node, attrs in (r.read_attributes.entries or {}).items():
            if attrs:
                lines.append(f"- Rules depend on these attributes of {self.L.get(node, node)}: {', '.join(attrs)}.")
        for p in (r.propagation_rules.entries or {}).get("rules", []):
            src, dst = self.L[p["from_node"]], self.L[p["to_node"]]
            m = p.get("machine", {})
            if m.get("operator", "copy") == "map":
                table = ", ".join(f"{_fmt(k)} → {_fmt(v)}" for k, v in m.get("mapping", {}).items())
                how = f"is looked up from {p['from_attribute']} of {src} ({table}; anything else → {_fmt(m.get('default'))})"
            else:
                how = f"equals {p['from_attribute']} of {src}"
            lines.append(f"- {p['to_attribute']} of {dst} {how} while {src} has an influencing link into {dst}; otherwise it is unset.")
        for c, cfg in ((r.justifications.entries or {}).get("conclusions", {}) or {}).items():
            alts = " OR ".join(
                "(" + " and ".join(f"{self.L[p]} exists with an influencing link into {self.L[c]}" for p in j) + ")"
                for j in cfg["justifications"])
            lines.append(f"- {cfg.get('status_attribute', 'status')} of {self.L[c]} is {_fmt(cfg.get('true_value', True))} "
                         f"when at least one holds: {alts}; otherwise {_fmt(cfg.get('false_value', False))}.")
        sat = r.satisfaction_functions.entries or {}
        for c in sat.get("computations", []):
            cond = ""
            if c.get("when_linked"):
                cond = " (applies only while " + ", ".join(self.L[w] for w in c["when_linked"]) + f" has an influencing link into {self.L[c['node']]})"
            lines.append(f"- {c['attribute']} of {self.L[c['node']]} = {self.expr(c['machine'], c['node'])}{cond}.")
        for n, sf in (sat.get("status_functions", {}) or {}).items():
            case = {"case": [{"when": m["when"], "then": m["label"]} for m in sf["mapping"]]}
            lines.append(f"- {sf.get('status_attribute', 'status')} of {self.L[n]} is {self.expr(case, n)}.")
        for n, p in ((r.combination_selection.entries or {}).get("problems", {}) or {}).items():
            word = {"sum": "total", "max": "largest", "min": "smallest"}
            opw = {"ge": "≥", "gt": ">", "le": "≤", "lt": "<", "eq": "="}
            cons = ", ".join(f"{word[c['agg']]} {c['attribute']} {opw[c['op']]} {_fmt(c['value'])}" for c in p["constraints"])
            line = (f"- For {self.L[n]}, a valid combination is any non-empty set of entities with an influencing link "
                    f"into {self.L[n]} such that {cons}. {p.get('status_attribute', 'status')} of {self.L[n]} is "
                    f"{_fmt(p.get('feasible_label', 'FEASIBLE'))} if at least one valid combination exists, otherwise "
                    f"{_fmt(p.get('infeasible_label', 'INFEASIBLE'))}; feasible_count is the number of valid combinations.")
            if p.get("objective"):
                o = p["objective"]
                line += (f" selected is the valid combination with the {'lowest' if o.get('sense', 'min') == 'min' else 'highest'} "
                         f"{word[o['agg']]} {o['attribute']} (unset if none), and selected_value is that {o['attribute']}.")
            lines.append(line)
        ev = r.evidence.entries or {}
        for key, claims in (ev.get("claims", {}) or {}).items():
            for c in claims:
                lines.append(f"- A separate report ({c['source']}) states that {self.ref(key)} is {_fmt(c['value'])}.")
        for key, res in (ev.get("resolution", {}) or {}).items():
            who = "the value recorded in the plan" if res["source"] == "graph" else f"the {res['source']} value"
            lines.append(f"- If reports disagree about {self.ref(key)}, use {who}.")
        factors = (r.units.entries or {}).get("factors")
        if factors:
            lines.append("- Unit conversion to a common base: " + ", ".join(f"1 {u} = {_fmt(f)}" for u, f in factors.items()) + ".")
        for key, dom in ((r.fixed_point_semantics.entries or {}).get("domains", {}) or {}).items():
            lines.append(f"- {self.ref(key)} can only be one of {_fmt(dom)}.")
        return lines or ["- none."]

    def change(self) -> str:
        ci = self.sc.canonical_input
        ev, g = ci.event, ci.graph
        if ev.operation == Operation.EDIT:
            if ev.target_ref is not None:
                who = f'the entity named "{ev.target_ref}"'
                if ev.target_scope:
                    who += f" (the one that feeds {self.L[ev.target_scope]})"
            else:
                who = self.L[ev.target_id]
            return f"Update: {ev.attribute} of {who} is now {_fmt(ev.new_value)}."
        if ev.operation == Operation.DELETE and ev.target_kind == TargetKind.NODE:
            return f"Update: {self.L[ev.target_id]} has been removed."
        if ev.operation == Operation.DELETE:
            e = g.edge(ev.target_id)
            return f"Update: the link {self.L[e.source]} → {self.L[e.target]} ({e.type.value}) has been removed."
        if ev.operation == Operation.ADD and ev.target_kind == TargetKind.NODE:
            n = ev.new_node
            attrs = "; ".join(f"{k} = {_fmt(v)}" for k, v in n.attributes.items()) or "no attributes"
            return f"Update: new entity {self.L[n.id]}: {attrs}."
        ec = ev.edge_change
        if ev.operation == Operation.ADD:
            if ec.new_type is not None:
                return f"Update: new link {self.L[ec.source]} → {self.L[ec.target]} ({ec.new_type.value})."
            kinds = " or ".join(t.value for t in ec.candidate_types)
            return f"Update: new link {self.L[ec.source]} → {self.L[ec.target]}; the report gives its kind only as {kinds}."
        e = g.edge(ec.edge_id)
        return f"Update: the link {self.L[e.source]} → {self.L[e.target]} is now {ec.new_type.value} (was {e.type.value})."


def render(sc: Scenario, sha: str) -> RNScenario:
    r = _Renderer(sc)
    return RNScenario(
        source_scenario_id=sc.scenario_id, source_sha256=sha, render_version=RENDER_VERSION,
        method_input=MethodInputNaturalLanguage(plan_text=r.plan(), change_text=r.change()),
        alias_map={label: nid for nid, label in r.L.items()},
    )


# ---------------------------------------------------------------------------
# Leakage checker
# ---------------------------------------------------------------------------

_FORBIDDEN = [
    r"MUST_CHANGE", r"MUST_STAY_STABLE", r"REQUIRES_REEVALUATION", r"\bUNCERTAIN\b",
    r"\bDETERMINABLE\b", r"\bambigu\w*", r"\baffected\b", r"\bunchanged\b", r"\bstays? (the )?same\b",
    r"\bcategory\b", r"\btemplate\b", r"\bpatholog\w*", r"\bground[ _-]?truth\b", r"\bexpected\b",
    r"\bunrelated\b", r"\birrelevant\b", r"\bdistractor\b", r"\bloop\b", r"\bcycle\b",
    r"\bP(?:10|[1-9]|8a|8b)\b", r"\bT\d+\.\d+[a-c]?\b", r"\bcat\d", r"\bnegative control\b",
]
_NUM = re.compile(r"(?<![\w.])-?\d+(?:\.\d+)?(?![\w.]*\w)")


def _numbers(obj: Any, out: set[float]) -> None:
    if isinstance(obj, bool) or obj is None:
        return
    if isinstance(obj, (int, float)):
        out.add(round(float(obj), 6))
    elif isinstance(obj, dict):
        for v in obj.values():
            _numbers(v, out)
    elif isinstance(obj, list):
        for v in obj:
            _numbers(v, out)
    elif isinstance(obj, str):
        for m in _NUM.findall(obj):
            out.add(round(float(m), 6))


def check_leakage(rn: RNScenario, sc: Scenario) -> list[str]:
    text = rn.method_input.plan_text + "\n" + rn.method_input.change_text
    problems = [f"forbidden term /{p}/" for p in _FORBIDDEN if re.search(p, text, re.IGNORECASE)]
    if sc.scenario_id in text:
        problems.append("scenario id in text")
    given: set[float] = set()
    _numbers(sc.canonical_input.model_dump(mode="json"), given)
    answer: set[float] = set()
    _numbers(sc.ground_truth.model_dump(mode="json"), answer)
    in_text: set[float] = set()
    _numbers(text, in_text)
    leaked = sorted((answer - given) & in_text)
    if leaked:
        problems.append(f"post-event-only numbers in text: {leaked}")
    ids = sc.canonical_input.graph.node_ids()
    for nid in ids:
        if len(nid) > 2 and re.search(rf"\b{re.escape(nid)}\b", text):
            problems.append(f"node id '{nid}' in text")
    missing = set(ids) - set(rn.alias_map.values())
    if missing:
        problems.append(f"alias map misses nodes {sorted(missing)}")
    return problems


# ---------------------------------------------------------------------------
# Pilot files
# ---------------------------------------------------------------------------

def pilot_path(scenario_id: str) -> Path:
    return RN_DIR / "pilot" / f"{scenario_id}.rn.json"


def load_rn(scenario_id: str) -> RNScenario:
    return RNScenario.model_validate_json(pilot_path(scenario_id).read_text())


def write_pilot() -> None:
    from .loader import load_scenario

    (RN_DIR / "pilot").mkdir(parents=True, exist_ok=True)
    for sid in PILOT_IDS:
        src = source_path(sid)
        sc = load_scenario(src)
        rn = render(sc, _sha(src))
        problems = check_leakage(rn, sc)
        if problems:
            raise ValueError(f"{sid}: {problems}")
        pilot_path(sid).write_text(rn.model_dump_json(indent=2) + "\n")
