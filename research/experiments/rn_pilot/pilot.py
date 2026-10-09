"""16-scenario R-N pilot (config v1.4). Data collection + scoring.

Conditions (see CONDITIONS.md):
  B1           direct LLM, full post-update state
  B2           direct LLM, delta only
  LLM_B4b      shared LLM extraction -> frozen B4b           (experiment B)
  gold_B4b     canonical structured input -> B4b, no LLM     (A: downstream sanity only)
  B6           ground-truth affected set (scope oracle, diagnostic)

Pre-specified output-mapping rules (method-agnostic, fixed before data):
  * Entity labels map to node ids through the evaluator-only alias map
    (exact, then case/space-insensitive). Unmapped labels are counted.
  * B1 returns the complete state: a plan entity it omits is read as removed
    (MUST_CHANGE). B2 returns a delta: an omitted entity is not_changed with
    its pre-update values.
  * decision -> label: changed MUST_CHANGE, not_changed MUST_STAY_STABLE,
    cannot_answer UNCERTAIN, needs_human_review REQUIRES_REEVALUATION;
    abstentions are AMBIGUOUS with reason -> P-code from config.
Every raw response is appended to pilot_raw.jsonl; reruns skip calls already
logged (resumable). Metrics come only from reflica_bench.evaluator.

    python pilot.py run       # API calls (needs approved frozen config)
    python pilot.py score     # scoring only, no API
"""
from __future__ import annotations

import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parents[1]))

from reflica_bench import rn  # noqa: E402
from reflica_bench.adapters import AdapterOutput, StructuredAdapter_v1  # noqa: E402
from reflica_bench.baseline import RevisionResult  # noqa: E402
from reflica_bench.baselines.b4b_weighted_csp import B4bWeightedCSP  # noqa: E402
from reflica_bench.evaluator import (  # noqa: E402
    NA, evaluate_category_1, evaluate_category_2, evaluate_category_3, evaluate_category_4,
    evaluate_category_5, evaluate_category_6a, evaluate_category_6b, evaluate_category_7)
from reflica_bench.extraction_schema import ExtractionOutput  # noqa: E402
from reflica_bench.gt_engine import evaluate_state  # noqa: E402
from reflica_bench.loader import load_scenario  # noqa: E402
from reflica_bench.schema import OutcomeLabel, Rules  # noqa: E402

RAW = HERE / "pilot_raw.jsonl"
CALLS = {"B1": "b1_full_regeneration.v1.1.txt", "B2": "b2_delta.v1.1.txt", "EXTRACT": "extractor.v1.1.txt"}
DECISION = {"changed": OutcomeLabel.MUST_CHANGE, "not_changed": OutcomeLabel.MUST_STAY_STABLE,
            "cannot_answer": OutcomeLabel.UNCERTAIN, "needs_human_review": OutcomeLabel.REQUIRES_REEVALUATION}


def cfg() -> dict:
    return json.loads((HERE / "config.frozen.json").read_text())


# ---------------------------------------------------------------------------
# Data collection
# ---------------------------------------------------------------------------

def _done() -> set[tuple]:
    if not RAW.exists():
        return set()
    return {(d["scenario"], d["call"], d["repeat"]) for d in map(json.loads, RAW.read_text().splitlines())}


def run(workers: int = 4) -> None:
    import threading

    from repeatability import call, render_prompt

    c = cfg()
    lock = threading.Lock()
    todo = [(sid, k, i) for sid in rn.PILOT_IDS for i in range(c["repeats_per_call"]) for k in CALLS
            if (sid, k, i) not in _done()]
    print(f"{len(todo)} calls to make", flush=True)

    def one(job):
        sid, k, i = job
        system, user = render_prompt(CALLS[k], rn.load_rn(sid))
        try:
            text, meta = call(c, c["model_id"], system, user)
            rec = {"scenario": sid, "call": k, "repeat": i, "ok": True, "meta": meta, "content": text}
        except BaseException as e:  # recorded, never retried silently
            rec = {"scenario": sid, "call": k, "repeat": i, "ok": False, "error": str(e)[:300]}
        with lock, open(RAW, "a") as f:
            f.write(json.dumps(rec) + "\n")
        print(f"{sid} {k} r{i} ok={rec['ok']}", flush=True)

    with ThreadPoolExecutor(workers) as ex:
        list(ex.map(one, todo))


# ---------------------------------------------------------------------------
# Mapping method outputs to RevisionResult (canonical ids)
# ---------------------------------------------------------------------------

def _mapper(alias: dict[str, str]):
    loose = {" ".join(k.lower().split()): v for k, v in alias.items()}

    def m(label: Any) -> str | None:
        if not isinstance(label, str):
            return None
        return alias.get(label) or loose.get(" ".join(label.lower().split()))
    return m


def from_direct(kind: str, text: str, sc, alias, codes) -> tuple[RevisionResult, dict]:
    data = json.loads(text)
    m = _mapper(alias)
    pre = {n.id: dict(n.attributes) for n in sc.canonical_input.graph.nodes}
    labels, attrs, det, flags, conf, unmapped = {}, {}, {}, {}, {}, 0
    for e in data.get("entities", []):
        nid = m(e.get("label"))
        if nid is None:
            unmapped += 1
            continue
        lbl = DECISION.get(e.get("decision"))
        labels[nid] = lbl
        base = {} if kind == "B1" else dict(pre.get(nid, {}))
        base.update(e.get("attributes") or {})
        attrs[nid] = base
        if lbl in (OutcomeLabel.UNCERTAIN, OutcomeLabel.REQUIRES_REEVALUATION):
            det[nid] = "AMBIGUOUS"
            if e.get("reason") in codes:
                flags[nid] = [codes[e["reason"]]]
        conf[nid] = float(e.get("confidence", 1.0))
    for nid in set(alias.values()):
        if nid in labels:
            continue
        if kind == "B1" and nid in pre:
            labels[nid], attrs[nid] = OutcomeLabel.MUST_CHANGE, {}   # omitted from full state = removed
        else:
            labels[nid], attrs[nid] = OutcomeLabel.MUST_STAY_STABLE, dict(pre.get(nid, {}))
    for nid in labels:
        det.setdefault(nid, "DETERMINABLE")
        flags.setdefault(nid, [])
    combos = data.get("valid_combinations")
    r = RevisionResult(
        affected_set=sorted(n for n, l in labels.items() if l != OutcomeLabel.MUST_STAY_STABLE),
        outcome_labels=labels, attribute_values=attrs, determinability=det, pathology_flags=flags,
        confidence_scores=conf,
        feasible_combinations=None if combos is None else [sorted(filter(None, map(m, c))) for c in combos])
    return r, {"unmapped_labels": unmapped}


def _remap(r: RevisionResult, m) -> tuple[RevisionResult, int]:
    """Rename B4b output keys (extracted labels) to canonical ids."""
    bad = 0

    def key(k):
        nonlocal bad
        v = m(k)
        if v is None:
            bad += 1
        return v

    def d(x):
        return None if x is None else {key(k): v for k, v in x.items() if m(k)}
    r2 = RevisionResult(
        affected_set=None if r.affected_set is None else sorted(m(x) for x in r.affected_set if m(x)),
        outcome_labels=d(r.outcome_labels), attribute_values=d(r.attribute_values),
        feasibility_status=d(r.feasibility_status), determinability=d(r.determinability),
        pathology_flags=d(r.pathology_flags),
        feasible_combinations=None if r.feasible_combinations is None
        else [sorted(filter(None, map(m, c))) for c in r.feasible_combinations],
        search_cost=r.search_cost)
    for k in (r.outcome_labels or {}):
        key(k)
    return r2, bad


def extraction_quality(x: ExtractionOutput, sc, alias) -> dict:
    m = _mapper(alias)
    g = sc.canonical_input.graph
    got = {m(n.id) for n in x.graph.nodes} - {None}
    truth = g.node_ids()
    t_edges = {(e.source, e.target, e.type.value) for e in g.edges}
    p_edges = {(m(e.source), m(e.target), e.type.value) for e in x.graph.edges}
    pairs = [(n.id, a, v) for n in g.nodes for a, v in n.attributes.items()]
    xa = {m(n.id): n.attributes for n in x.graph.nodes}
    vals = sum(xa.get(nid, {}).get(a) == v for nid, a, v in pairs)
    mi = x.to_method_input()
    try:
        rules = Rules.model_validate({k: {"declared_input": True, **v} for k, v in mi.rules.items()})
        nodes = {n.id: dict(n.attributes) for n in mi.graph.nodes}
        edges = [{"edge_id": e.edge_id, "source": e.source, "target": e.target, "type": e.type} for e in mi.graph.edges]
        ev = evaluate_state(nodes, edges, rules).nodes
        rep = {m(k): v for k, v in ev.items()}
        reproduced = sum(rep.get(nid, {}).get(a) == v for nid, a, v in pairs) / len(pairs) if pairs else NA
    except Exception:
        reproduced = 0.0
    ce, xe = sc.canonical_input.event, mi.event
    return {
        "node_recall": len(got & truth) / len(truth) if truth else NA,
        "node_precision": len(got & truth) / len(got) if got else NA,
        "edge_recall": len(p_edges & t_edges) / len(t_edges) if t_edges else NA,
        "edge_precision": len(p_edges & t_edges) / len(p_edges) if p_edges else NA,
        "pre_value_accuracy": vals / len(pairs) if pairs else NA,
        "pre_state_reproduction": reproduced,
        "event_correct": (ce.operation == xe.operation and ce.attribute == xe.attribute
                          and ce.new_value == xe.new_value
                          and (ce.target_id == m(xe.target_id) or ce.target_ref == xe.target_ref)),
    }


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def metrics(r: RevisionResult, sc) -> dict:
    gt = sc.ground_truth
    cat = sc.category
    if cat == 1:
        return evaluate_category_1(r, gt).to_dict()
    if cat == 2:
        return evaluate_category_2(r, gt).to_dict()
    if cat == 3:
        return evaluate_category_3(r, gt, sc.canonical_input.graph, sc.canonical_input.event).to_dict()
    if cat == 4:
        return evaluate_category_4(r, gt, set(sc.canonical_input.rules.justifications.entries.get("conclusions", {}))).to_dict()
    if cat == 5:
        return evaluate_category_5(r, gt, sc).to_dict()
    if cat == 6:
        f = evaluate_category_6a if sc.subcategory == "C6-A" else evaluate_category_6b
        return f(r, gt, sc).to_dict()
    return evaluate_category_7([(r, gt)]).to_dict()


def score() -> None:
    c = cfg()
    codes = c["reason_to_code"]
    raw: dict[tuple, dict] = {}
    if RAW.exists():
        for d in map(json.loads, RAW.read_text().splitlines()):
            raw[(d["scenario"], d["call"], d["repeat"])] = d
    rows = []
    for sid in rn.PILOT_IDS:
        sc = load_scenario(rn.source_path(sid))
        alias = rn.load_rn(sid).alias_map
        m = _mapper(alias)
        gold = B4bWeightedCSP().revise(StructuredAdapter_v1().adapt(sc, "gold"))
        rows.append({"scenario": sid, "category": sc.category, "condition": "gold_B4b", "repeat": 0,
                     "status": "ok", "metrics": metrics(gold, sc)})
        b6 = RevisionResult(affected_set=sorted(n for n, g in sc.ground_truth.nodes.items() if g.in_affected_set))
        rows.append({"scenario": sid, "category": sc.category, "condition": "B6", "repeat": 0,
                     "status": "ok", "metrics": metrics(b6, sc)})
        for i in range(c["repeats_per_call"]):
            for kind in ("B1", "B2"):
                d = raw.get((sid, kind, i))
                row = {"scenario": sid, "category": sc.category, "condition": kind, "repeat": i}
                if d is None or not d.get("ok"):
                    row["status"] = "missing" if d is None else "api_error"
                else:
                    try:
                        r, info = from_direct(kind, d["content"], sc, alias, codes)
                        row.update(status="ok", metrics=metrics(r, sc), **info)
                    except (ValueError, KeyError, TypeError, AttributeError) as e:
                        row.update(status="invalid_output", error=str(e)[:200])
                rows.append(row)
            d = raw.get((sid, "EXTRACT", i))
            row = {"scenario": sid, "category": sc.category, "condition": "LLM_B4b", "repeat": i}
            if d is None or not d.get("ok"):
                row["status"] = "missing" if d is None else "api_error"
            else:
                try:
                    x = ExtractionOutput.model_validate_json(d["content"])
                    row["extraction"] = extraction_quality(x, sc, alias)
                    r = B4bWeightedCSP().revise(AdapterOutput(x.to_method_input(), None, {}))
                    r2, bad = _remap(r, m)
                    row.update(status="ok", metrics=metrics(r2, sc), unmapped_labels=bad)
                except Exception as e:  # schema-invalid or downstream failure = extraction failure
                    row.update(status="extraction_failure", error=f"{type(e).__name__}: {str(e)[:200]}")
            rows.append(row)
    (HERE / "pilot_scores.jsonl").write_text("".join(json.dumps(r, default=str) + "\n" for r in rows))
    summary: dict[str, dict] = {}
    for r in rows:
        s = summary.setdefault(r["condition"], {}).setdefault(f"cat{r['category']}", {"n": 0, "ok": 0, "status": {}})
        s["n"] += 1
        s["ok"] += r["status"] == "ok"
        s["status"][r["status"]] = s["status"].get(r["status"], 0) + 1
    (HERE / "pilot_summary.json").write_text(json.dumps(summary, indent=1) + "\n")
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    if sys.argv[1:] == ["run"]:
        run()
    elif sys.argv[1:] == ["score"]:
        score()
    else:
        raise SystemExit(__doc__)
