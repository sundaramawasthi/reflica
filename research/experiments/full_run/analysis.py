"""Pre-specified DESCRIPTIVE analysis of a full-experiment run folder (protocol v0.6, S1 = D).

    python analysis.py RUN_DIR     # writes RUN_DIR/results.json (no API)

Refuses to run unless `runner.validate(RUN_DIR, complete=True)` reports no
problems, so data from a run that did not pass the freeze gate, was edited,
or is incomplete cannot be analysed.

There are no confirmatory verdicts, no p-values and no multiplicity
adjustment. Every quantity is an estimate with, where the protocol judges it
appropriate, a 95% interval whose simulated calibration is stated next to it.
The thresholds D1 (τ_FA = 0.15) and D2 (δ = 0.05) keep their approved
node-level meaning and are shown only as reference lines for orientation.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import runner  # noqa: E402
from runner import S  # noqa: E402  (reflica_bench.stats)

DELTA = 0.05     # D2, node-level, reference line only
TAU_FA = 0.15    # D1, node-level, reference line only
B5 = ("B", "B5")
COMPARATORS = {"B1": ("direct", "B1"), "B2": ("direct", "B2"), "B4b": ("B", "B4b"),
               "B3": ("B", "B3"), "B4a": ("B", "B4a")}
METHODS = [("direct", "B1"), ("direct", "B2"), ("B", "B3"), ("B", "B4a"), ("B", "B4b"), ("B", "B5")]
T_NOTE = ("APPROXIMATE 95% one-sample t-interval over scenarios; DESCRIPTIVE, not confirmatory. Simulated "
          "coverage 0.934–0.959 at n = 63; not a test, not multiplicity-adjusted (DECISION_REPORT_S1_S4 §2)")
INDICATORS = {
    "fully_correct": lambda c: c["correct"] == c["nodes"],
    "any_false_confidence": lambda c: c["false_confident"] > 0,
    "any_false_abstention": lambda c: c["false_abstained"] > 0,
}


def _load(run_dir: Path) -> list[dict]:
    p = Path(run_dir) / runner.FILES["scores"]
    if not p.exists():
        return runner.score(run_dir)
    return [json.loads(x) for x in p.read_text().splitlines()]


def _cells(rows, common) -> dict[tuple, list[dict]]:
    """(condition, method, scenario) -> node counts over the scenario's common repeats."""
    out: dict[tuple, list[dict]] = {}
    for r in rows:
        if r["condition"] == "A" or r["scenario"] not in common or r["repeat"] not in common[r["scenario"]]:
            continue
        if "counts" not in r:
            raise RuntimeError(f"no counts for {r['scenario']} {r['method']} r{r['repeat']} inside common repeats")
        out.setdefault((r["condition"], r["method"], r["scenario"]), []).append(r["counts"])
    return out


def _mean(cells, m, s, key):
    reps = cells[(*m, s)]
    return sum(c[key] for c in reps) / len(reps)


def indicator(cells, method, sid, name) -> int:
    reps = cells[(*method, sid)]
    return int(2 * sum(INDICATORS[name](c) for c in reps) >= len(reps))


def _paired(cells, sids, name, second):
    return S.paired_binary([indicator(cells, B5, s, name) for s in sids],
                           [indicator(cells, second, s, name) for s in sids])


def _interval(values):
    m, lo, hi = S.mean_t_interval(values)
    return {"estimate": m, "ci95": (lo, hi), "n_scenarios": len(values), "interval": T_NOTE}


def analyze(run_dir: Path, *, protocol_dir: Path = HERE, write: bool = True) -> dict:
    run_dir = Path(run_dir)
    v = runner.validate(run_dir, protocol_dir=protocol_dir, complete=True)
    if v["problems"]:
        raise RuntimeError("run folder failed validation; nothing analysed:\n" + "\n".join(v["problems"]))
    aset = v["summary"]["analysis_set"]
    common = aset["common_repeats"]
    sids = sorted(common)
    rows = _load(run_dir)
    cells = _cells(rows, common)
    cat = {r["scenario"]: r["category"] for r in rows}
    amb_sids = [s for s in sids if cells[(*B5, s)][0]["ambiguous"] > 0]
    res: dict = {"analysis_type": "descriptive (S1 = D): no confirmatory verdicts, no p-values",
                 "questions": {}, "secondary_scenario_level": {}, "error_patterns": {}}
    q = res["questions"]

    # Q1/Q2 (were H1/H2) and Q4 (was H4): node-level mean correctness, as approved.
    q["node_correctness_by_method"] = {"|".join(m): _interval([_mean(cells, m, s, "primary") for s in sids])
                                       for m in METHODS}
    for key, comp in (("Q1_B5_minus_B1", "B1"), ("Q2_B5_minus_B2", "B2"), ("Q4_B5_minus_B4b", "B4b")):
        d = [_mean(cells, B5, s, "primary") - _mean(cells, COMPARATORS[comp], s, "primary") for s in sids]
        q[key] = _interval(d) | {"scenarios_B5_higher": sum(x > 0 for x in d),
                                 "scenarios_equal": sum(x == 0 for x in d),
                                 "scenarios_B5_lower": sum(x < 0 for x in d)}
    q4 = q["Q4_B5_minus_B4b"]
    q4["reference_line_D2"] = {"margin": -DELTA, "interval_lower_above_margin": q4["ci95"][0] > -DELTA,
                               "note": "orientation only; not a non-inferiority test (S1 = D)"}

    # Q5a (was H5a): false confidence on the 19 ambiguous nodes — counts, no interval (≤ 11 clusters).
    amb_total = sum(cells[(*B5, s)][0]["ambiguous"] for s in amb_sids)
    q["Q5a_false_confidence"] = {
        "ambiguous_nodes": amb_total, "ambiguous_scenarios": len(amb_sids),
        "by_method": {"|".join(m): {
            "falsely_confident_nodes_mean_over_repeats": sum(_mean(cells, m, s, "false_confident") for s in amb_sids),
            "pooled_rate": (sum(_mean(cells, m, s, "false_confident") for s in amb_sids) / amb_total) if amb_total else "N/A",
            "per_scenario": {s: _mean(cells, m, s, "false_confident") for s in amb_sids}} for m in METHODS},
        "interval": "none: ≤ 11 scenarios; no interval was adequately calibrated in simulation"}

    # Q5b (was H5b): B5 false abstention on determinable nodes — counts and clustering, D1 as reference line.
    det_total = sum(cells[(*B5, s)][0]["determinable"] for s in sids)
    fa = {s: _mean(cells, B5, s, "false_abstained") for s in sids}
    rate = sum(fa.values()) / det_total if det_total else "N/A"
    q["false_abstention_by_method"] = {"|".join(m): {
        "falsely_abstained_nodes_mean_over_repeats": sum(_mean(cells, m, s, "false_abstained") for s in sids),
        "pooled_rate": (sum(_mean(cells, m, s, "false_abstained") for s in sids) / det_total) if det_total else "N/A",
        "scenarios_with_any": sum(_mean(cells, m, s, "false_abstained") > 0 for s in sids)} for m in METHODS}
    q["Q5b_false_abstention_B5"] = {
        "determinable_nodes": det_total, "falsely_abstained_nodes_mean_over_repeats": sum(fa.values()),
        "pooled_rate": rate, "scenarios_with_any_false_abstention": sum(v > 0 for v in fa.values()),
        "reference_line_D1": {"tau_FA": TAU_FA, "estimate_below": rate < TAU_FA if rate != "N/A" else "N/A",
                              "note": "orientation only; not a threshold test (S1 = D)"},
        "interval": "none: abstentions may cluster by scenario; percentile bootstrap covered 0.70 in simulation"}

    # Secondary: scenario-level 2×2 tables, descriptive only.
    for key, name, comp, subset in (("fully_correct_vs_B1", "fully_correct", "B1", sids),
                                    ("fully_correct_vs_B2", "fully_correct", "B2", sids),
                                    ("fully_correct_vs_B4b", "fully_correct", "B4b", sids),
                                    ("any_false_confidence_vs_B4b", "any_false_confidence", "B4b", amb_sids),
                                    ("any_false_confidence_vs_B1", "any_false_confidence", "B1", amb_sids),
                                    ("any_false_confidence_vs_B2", "any_false_confidence", "B2", amb_sids)):
        t = _paired(cells, subset, name, COMPARATORS[comp])
        res["secondary_scenario_level"][key] = {
            "both": t.both, "B5_only": t.only_first, "comparator_only": t.only_second, "neither": t.neither,
            "n": t.n, "difference_in_proportions": t.difference}
    res["secondary_scenario_level"]["caution"] = (
        "a binary scenario endpoint favours a method whose errors cluster within scenarios even at equal "
        "node-level accuracy (DECISION_REPORT_S1_S4 §2 E); read with Q1/Q2/Q4")
    k = sum(indicator(cells, B5, s, "any_false_abstention") for s in sids)
    res["secondary_scenario_level"]["B5_scenarios_with_any_false_abstention"] = {"k": k, "n": len(sids)}

    res["secondary_scenario_level"]["fully_correct_by_category"] = {
        "|".join(m): {f"cat{c}": f"{sum(indicator(cells, m, s, 'fully_correct') for s in sids if cat[s] == c)}"
                                 f"/{sum(1 for s in sids if cat[s] == c)}" for c in sorted({cat[s] for s in sids})}
        for m in METHODS}
    res["error_patterns"] = _error_patterns(cells, sids, cat, rows, common)
    res["condition_A_gold_input_sanity"] = _condition_a(rows)
    res["descriptive_rq2_cat5_6"] = _rq2(rows, common)
    res["missingness"] = {"analysis_set_size": len(sids), "excluded_scenarios": aset["excluded_scenarios"],
                          "calls_planned": aset["calls_planned"], "calls_infra_missing": aset["calls_infra_missing"],
                          "by_call_type": aset["by_call_type"],
                          "by_call_type_and_category": aset["by_call_type_and_category"],
                          "by_method": _status_by_method(rows)}
    res["validation"] = {"records": v["summary"]["records"], "problems": []}
    if write:
        (run_dir / "results.json").write_text(json.dumps(res, indent=1, sort_keys=True, default=str) + "\n")
    return res


def _condition_a(rows) -> dict:
    """Gold structured input, no LLM (protocol §3): descriptive sanity check only, never
    evidence of extraction accuracy. All 63 scenarios (no calls, so no missingness)."""
    out: dict = {}
    for r in rows:
        if r["condition"] != "A":
            continue
        cell = out.setdefault(r["method"], {"scenarios": 0, "primary_sum": 0.0, "fully_correct": 0,
                                            "falsely_confident": 0, "falsely_abstained": 0})
        c = r["counts"]
        cell["scenarios"] += 1
        cell["primary_sum"] += c["primary"]
        cell["fully_correct"] += c["correct"] == c["nodes"]
        cell["falsely_confident"] += c["false_confident"]
        cell["falsely_abstained"] += c["false_abstained"]
    for cell in out.values():
        cell["mean_node_correctness"] = cell.pop("primary_sum") / cell["scenarios"]
    return out | {"note": "descriptive sanity check; B5 agreement with gold is expected by construction"}


def _status_by_method(rows) -> dict:
    out: dict[str, dict] = {}
    for r in rows:
        cell = out.setdefault(f"{r['condition']}|{r['method']}", {"ok": 0, "model_failure": 0, "infra_missing": 0,
                                                                     "missing_predictions": 0})
        cell[r["status"]] += 1
        cell["missing_predictions"] += (r.get("counts") or {}).get("missing_prediction", 0) if r["status"] == "ok" else 0
    return out


def _error_patterns(cells, sids, cat, rows, common) -> dict:
    out: dict = {"node_correctness_by_category": {}, "rq4_attribution_B5": {}}
    for m in METHODS:
        by: dict = {}
        for s in sids:
            by.setdefault(cat[s], []).append(_mean(cells, m, s, "primary"))
        out["node_correctness_by_category"]["|".join(m)] = {
            f"cat{c}": {"mean": sum(v) / len(v), "n_scenarios": len(v)} for c, v in sorted(by.items())}
    # RQ4 (exploratory): a wrong B5 output is attributed to extraction if the shared extraction
    # deviates from gold on nodes, links, pre-state values or the event; otherwise to revision.
    att = {"correct": 0, "wrong_with_extraction_error": 0, "wrong_with_correct_extraction": 0, "failed_output": 0}
    for r in rows:
        if r["condition"] != "B" or r["method"] != "B5" or r["scenario"] not in common \
                or r["repeat"] not in common[r["scenario"]]:
            continue
        if r["status"] == "model_failure":
            att["failed_output"] += 1
            continue
        if r["counts"]["primary"] == 1.0:
            att["correct"] += 1
            continue
        x = r.get("extraction") or {}
        clean = all(x.get(k) == 1.0 for k in ("node_recall", "node_precision", "edge_recall", "edge_precision",
                                               "pre_value_accuracy")) and x.get("event_correct") is True
        att["wrong_with_correct_extraction" if clean else "wrong_with_extraction_error"] += 1
    out["rq4_attribution_B5"] = att | {"unit": "scenario-repeat", "status": "exploratory"}
    return out


def _rq2(rows, common) -> dict:
    out: dict = {}
    for r in rows:
        if r["category"] not in (5, 6) or r["condition"] == "A" or r["scenario"] not in common \
                or r["repeat"] not in common[r["scenario"]] or "metrics" not in r:
            continue
        for metric, val in r["metrics"].items():
            if isinstance(val, (int, float)) and not isinstance(val, bool) and metric not in ("token_cost", "wall_time_ms"):
                out.setdefault(f"{r['condition']}|{r['method']}", {}).setdefault(metric, {}) \
                    .setdefault(r["scenario"], []).append(val)
    for m, metrics in out.items():
        for metric, per in metrics.items():
            vals = [sum(v) / len(v) for v in per.values()]
            metrics[metric] = {"mean": sum(vals) / len(vals), "n_scenarios": len(vals)}
    every = sorted({k for metrics in out.values() for k in metrics})
    for m in ["B|B3", "B|B4a", "B|B4b", "B|B5", "direct|B1", "direct|B2"]:
        metrics = out.setdefault(m, {})
        for k in every:
            metrics.setdefault(k, "N/A")  # method does not output this dimension (or no valid output)
    return out


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    res = analyze(Path(sys.argv[1]))
    print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk in ("estimate", "ci95", "pooled_rate")}
                      for k, v in res["questions"].items() if isinstance(v, dict)}, indent=1, default=str))
