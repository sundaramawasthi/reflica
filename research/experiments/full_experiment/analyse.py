"""Hypothesis analysis for the confirmatory experiment (PROTOCOL.md §5–§8).

    python analyse.py --scores runs/ID/scores.jsonl --out runs/ID

Reads only scores.jsonl. Repeats are first aggregated within each scenario;
every test then resamples scenarios (never repeats). Writes analysis.json and
report.md. Verdict wording is fixed here, before any confirmatory data exist.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import stats

DELTA = 0.05     # H2 non-inferiority margin
TAU_FA = 0.15    # H3 false-abstention ceiling
H1_COMPARATORS = ("B1", "B2")
H2_COMPARATOR = "LLM_B4b"
H3_COMPARATORS = ("B1", "B2", "LLM_B4b")
METHOD = "LLM_B5"
H2_GROUPS = {"Cat 5": lambda r: r["category"] == 5,
             "Cat 6-A": lambda r: r["subcategory"] == "C6-A",
             "Cat 6-B": lambda r: r["subcategory"] == "C6-B"}
INFRA = ("missing", "api_error")

# Failure handling rules (PROTOCOL.md §8).
RULES = {
    "primary": "infrastructure failures excluded pairwise; every other failure scored at its worst value",
    "S1_complete_case": "only scenario-repeats where both compared conditions succeeded",
    "S2_all_worst_case": "every failure, including infrastructure, scored at its worst value",
    "S3_repeat0": "primary rule, first repeat only",
}


def _value(row: dict, rule: str) -> dict | None:
    """Primary-metric dict for one row under a failure-handling rule, or None (excluded)."""
    if rule == "S3_repeat0" and row["repeat"] != 0:
        return None
    if row["status"] == "ok":
        return row["primary"]
    if rule in ("primary", "S3_repeat0"):
        return None if row["status"] in INFRA else row["primary_worst_case"]
    if rule == "S2_all_worst_case":
        return row["primary_worst_case"]
    return None  # S1: failures excluded (pairing handled below)


def scenario_values(rows: list[dict], cond_a: str, cond_b: str, metric: str, rule: str,
                    where=lambda r: True) -> dict[str, tuple[float, float]]:
    """Paired per-scenario means over repeats of `metric` for two conditions.
    Repeats are paired by index; a repeat is used only if both values exist."""
    by: dict[tuple, dict] = {}
    for r in rows:
        if r["condition"] in (cond_a, cond_b) and r["repeat"] is not None and where(r):
            by.setdefault((r["scenario"], r["repeat"]), {})[r["condition"]] = r
    acc: dict[str, list[tuple[float, float]]] = {}
    for (sid, _), pair in by.items():
        if cond_a not in pair or cond_b not in pair:
            continue
        if rule == "S1_complete_case" and not (pair[cond_a]["status"] == pair[cond_b]["status"] == "ok"):
            continue
        va, vb = _value(pair[cond_a], rule), _value(pair[cond_b], rule)
        if va is None or vb is None or va.get(metric) is None or vb.get(metric) is None:
            continue
        acc.setdefault(sid, []).append((va[metric], vb[metric]))
    return {sid: (sum(a for a, _ in v) / len(v), sum(b for _, b in v) / len(v)) for sid, v in sorted(acc.items())}


def pooled_inputs(rows, cond_a, cond_b, num, den, rule):
    """Per-scenario mean numerators/denominators for pooled Cat 7 rates, paired."""
    by: dict[tuple, dict] = {}
    for r in rows:
        if r["category"] == 7 and r["condition"] in (cond_a, cond_b) and r["repeat"] is not None:
            by.setdefault((r["scenario"], r["repeat"]), {})[r["condition"]] = r
    acc: dict[str, list] = {}
    for (sid, _), pair in by.items():
        if cond_a not in pair or (cond_b and cond_b not in pair):
            continue
        conds = [cond_a] + ([cond_b] if cond_b else [])
        if rule == "S1_complete_case" and any(pair[c]["status"] != "ok" for c in conds):
            continue
        vals = [_value(pair[c], rule) for c in conds]
        if any(v is None or v.get(num) is None for v in vals):
            continue
        acc.setdefault(sid, []).append([(v[num], v[den]) for v in vals])
    out = {}
    for sid, reps in sorted(acc.items()):
        k = len(reps)
        out[sid] = [(sum(rp[j][0] for rp in reps) / k, sum(rp[j][1] for rp in reps) / k) for j in range(len(reps[0]))]
    return out


def h1(rows, rule) -> dict:
    tests, p = {}, {}
    for metric in ("over_flip", "missed_change"):
        for comp in H1_COMPARATORS:
            v = scenario_values(rows, METHOD, comp, metric, rule, lambda r: r["category"] <= 4)
            res = stats.paired_mean_difference([a - b for a, b in v.values()])
            res.update(method_mean=_mean([a for a, _ in v.values()]), comparator_mean=_mean([b for _, b in v.values()]))
            name = f"{metric} vs {comp}"
            tests[name] = res
            p[name] = res["p"]
    adj = stats.holm(p)
    favourable = 0
    for name, t in tests.items():
        t.update(adj[name])
        t["favourable"] = bool(t["reject"] and t["estimate"] is not None and t["estimate"] < 0)
        favourable += t["favourable"]
    verdict = ("SUPPORTED" if favourable == len(tests) else
               "PARTIALLY SUPPORTED" if favourable else "NOT SUPPORTED")
    return {"tests": tests, "verdict": verdict,
            "rule": "all 4 Holm-adjusted comparisons significant with B5 lower (over-flip and missed change, vs B1 and B2)"}


def h2(rows, rule) -> dict:
    groups = {"Aggregate (Cat 5–6)": lambda r: r["category"] in (5, 6)} | H2_GROUPS
    res = {}
    for g, where in groups.items():
        v = scenario_values(rows, METHOD, H2_COMPARATOR, "value_accuracy", rule, where)
        t = stats.paired_mean_difference([a - b for a, b in v.values()])
        t.update(method_mean=_mean([a for a, _ in v.values()]), comparator_mean=_mean([b for _, b in v.values()]))
        lb = None if t["ci"] is None else t["ci"][0]
        t["non_inferior"] = lb is not None and lb > -DELTA
        t["point_above_margin"] = t["estimate"] is not None and t["estimate"] > -DELTA
        res[g] = t
    agg = res["Aggregate (Cat 5–6)"]
    subs = [res[g] for g in H2_GROUPS]
    if agg["non_inferior"] and all(s["non_inferior"] for s in subs):
        verdict = "SUPPORTED"
    elif agg["non_inferior"] and all(s["point_above_margin"] for s in subs):
        verdict = "SUPPORTED IN AGGREGATE ONLY (non-inferiority not established in every category)"
    else:
        verdict = "NOT SUPPORTED"
    return {"tests": res, "verdict": verdict, "margin": DELTA,
            "rule": "B5 − B4b value accuracy; lower 95% CI bound > −0.05 in the aggregate and in Cat 5, 6-A and 6-B"}


def h3(rows, rule) -> dict:
    tests, p = {}, {}
    for comp in H3_COMPARATORS:
        v = list(pooled_inputs(rows, METHOD, comp, "false_confident", "n_ambiguous", rule).values())
        t = stats.pooled_rate_difference([x[0][0] for x in v], [x[0][1] for x in v],
                                         [x[1][0] for x in v], [x[1][1] for x in v])
        tests[f"false_confidence vs {comp}"] = t
        p[f"false_confidence vs {comp}"] = t["p"]
    adj = stats.holm(p)
    for name, t in tests.items():
        t.update(adj[name])
        t["favourable"] = bool(t["reject"] and t["estimate"] is not None and t["estimate"] < 0)
    fa = pooled_inputs(rows, METHOD, None, "false_abstained", "n_determinable", rule)
    far = stats.pooled_rate([x[0][0] for x in fa.values()], [x[0][1] for x in fa.values()])
    if far["ci"] is None:
        far["threshold"] = "INCONCLUSIVE (insufficient data)"
    elif far["ci"][1] <= TAU_FA:
        far["threshold"] = "PASS (upper 95% bound ≤ 0.15)"
    elif far["ci"][0] > TAU_FA:
        far["threshold"] = "FAIL (lower 95% bound > 0.15)"
    else:
        far["threshold"] = "INCONCLUSIVE (95% CI contains 0.15)"
    all_fav = all(t["favourable"] for t in tests.values())
    if far["threshold"].startswith("FAIL") or not all_fav:
        verdict = "NOT SUPPORTED"
    elif far["threshold"].startswith("PASS"):
        verdict = "SUPPORTED"
    else:
        verdict = "INCONCLUSIVE (false-confidence advantage shown, false-abstention ceiling not established)"
    return {"tests": tests, "false_abstention_B5": far, "verdict": verdict, "tau_FA": TAU_FA,
            "rule": "B5 pooled false-confidence lower than B1, B2 and LLM→B4b (Holm, 3 tests) "
                    "AND upper 95% bound of B5 false-abstention ≤ 0.15"}


def operational(rows) -> dict:
    out: dict[str, dict] = {}
    for r in rows:
        if r["repeat"] is None:
            continue
        s = out.setdefault(r["condition"], {"n": 0})
        s["n"] += 1
        s[r["status"]] = s.get(r["status"], 0) + 1
    for s in out.values():
        s["operational_failure_rate"] = 1 - s.get("ok", 0) / s["n"]
    return out


def _mean(xs):
    return sum(xs) / len(xs) if xs else None


def analyse(rows: list[dict]) -> dict:
    gate = {c: sum(r["status"] != "ok" for r in rows if r["condition"] == c) for c in ("gold_B4b", "gold_B5")}
    eval_fail = sum(r["status"] == "evaluation_failure" for r in rows)
    out = {"operational": operational(rows), "gold_gate_failures": gate, "evaluation_failures": eval_fail,
           "valid": eval_fail == 0, "rules": RULES, "analyses": {}}
    if eval_fail:
        out["note"] = "evaluation failures are harness defects: fix and re-score before reading any verdict"
    for rule in RULES:
        out["analyses"][rule] = {"H1": h1(rows, rule), "H2": h2(rows, rule), "H3": h3(rows, rule)}
    out["verdicts_primary"] = {h: out["analyses"]["primary"][h]["verdict"] for h in ("H1", "H2", "H3")}
    return out


def _fmt(x):
    return "N/A" if x is None else f"{x:+.3f}" if isinstance(x, float) else str(x)


def report(a: dict) -> str:
    lines = ["# Confirmatory analysis report", "",
             f"Valid run: **{a['valid']}** (evaluation failures: {a['evaluation_failures']})", "",
             "## Operational failure rates (reported separately from accuracy)", "",
             "| Condition | n | ok | failure rate | statuses |", "|---|---|---|---|---|"]
    for c, s in sorted(a["operational"].items()):
        st = {k: v for k, v in s.items() if k not in ("n", "ok", "operational_failure_rate")}
        lines.append(f"| {c} | {s['n']} | {s.get('ok', 0)} | {s['operational_failure_rate']:.3f} | {st or '—'} |")
    for rule, res in a["analyses"].items():
        lines += ["", f"## Analysis: {rule} — {RULES[rule]}", ""]
        for h in ("H1", "H2", "H3"):
            lines += [f"### {h}: **{res[h]['verdict']}**", f"Rule: {res[h]['rule']}", "",
                      "| Test | n | estimate | 95% CI | p | p (Holm) |", "|---|---|---|---|---|---|"]
            for name, t in res[h]["tests"].items():
                ci = "N/A" if t.get("ci") is None else f"[{t['ci'][0]:+.3f}, {t['ci'][1]:+.3f}]"
                lines.append(f"| {name} | {t['n']} | {_fmt(t['estimate'])} | {ci} | {_fmt(t.get('p'))} | "
                             f"{_fmt(t.get('p_holm'))} |")
            if h == "H3":
                f = res[h]["false_abstention_B5"]
                ci = "N/A" if f.get("ci") is None else f"[{f['ci'][0]:.3f}, {f['ci'][1]:.3f}]"
                lines += ["", f"B5 false-abstention: {_fmt(f['estimate'])} {ci} → {f['threshold']}"]
            lines.append("")
    return "\n".join(lines) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--scores", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    rows = [json.loads(x) for x in a.scores.read_text().splitlines()]
    res = analyse(rows)
    a.out.mkdir(parents=True, exist_ok=True)
    (a.out / "analysis.json").write_text(json.dumps(res, indent=1, sort_keys=True) + "\n")
    (a.out / "report.md").write_text(report(res))
    print(json.dumps({"valid": res["valid"], "verdicts_primary": res["verdicts_primary"]}, indent=1))


if __name__ == "__main__":
    main()
