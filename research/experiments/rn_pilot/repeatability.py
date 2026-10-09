"""Temperature-0 repeatability check (OpenAI-compatible endpoint; provider from REFLICA_LLM_PROVIDER).

Refuses to run without config.frozen.json. Sends the extractor prompt for 2
fixed pilot scenarios `repeats_per_call` times each and reports whether the
outputs are byte-identical. Every response's served model version must equal
the frozen model id, otherwise the run aborts (providers can silently redirect
ids (seen on Gemini: 3.7-flash -> 3.8-flash)). Key read from the provider env var only.
"""
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parents[1]))
from _api import PROVIDER, chat  # noqa: E402
from reflica_bench import rn  # noqa: E402

CASES = ("cat5_threshold_partial_partial_001", "cat7_ambiguous_referent_001")
if "--only" in sys.argv:  # restrict to named cases (v1.4 three-call check)
    CASES = tuple(sys.argv[sys.argv.index("--only") + 1:])


SCHEMA_FOR = {  # prompt -> the output schema it must be sent with (v1.1 fix; v1.2 typed extractor schema)
    "extractor": "extractor_output.schema.v1.4.json",
    "b1_full_regeneration": "revision_output.schema.v1.json",
    "b2_delta": "revision_output.schema.v1.json",
}


def render_prompt(name: str, r) -> tuple[str, str]:
    text = (HERE / "prompts" / name).read_text()
    schema = (HERE / SCHEMA_FOR[name.split(".v")[0]]).read_text().strip()
    text = text.replace("{output_schema}", schema)
    reasons = (HERE / "prompts" / "common_reasons.txt").read_text()
    text = (text.replace("{plan_text}", r.method_input.plan_text)
                .replace("{change_text}", r.method_input.change_text)
                .replace("{common_reasons}", reasons))
    system, _, user = text.partition("\nUSER:\n")
    return system.removeprefix("SYSTEM: ").strip(), user.strip()


def _is_json(t: str) -> bool:
    try:
        json.loads(t)
        return True
    except ValueError:
        return False


def _schema_errors(t: str) -> int:
    """Validation against the typed extractor schema (v1.2)."""
    from pydantic import ValidationError

    from reflica_bench.extraction_schema import ExtractionOutput

    try:
        ExtractionOutput.model_validate_json(t)
        return 0
    except ValidationError as e:
        return e.error_count()


def _downstream(t: str) -> dict:
    """Operational check with the frozen downstream code, no repair layer:
    parse -> MethodInputStructured -> formula lint -> B4b.revise()."""
    from reflica_bench.adapters import AdapterOutput
    from reflica_bench.baselines.b4b_weighted_csp import B4bWeightedCSP
    from reflica_bench.extraction_schema import ExtractionOutput
    from reflica_bench.linter import LintError, _lint_expr

    out = {"parse_ok": False, "lint_ok": False, "b4b_ok": False}
    try:
        mi = ExtractionOutput.model_validate_json(t).to_method_input()
        out["parse_ok"] = True
    except Exception as e:
        out["error"] = f"parse: {str(e)[:120]}"
        return out
    sat = (mi.rules.get("satisfaction_functions") or {}).get("entries", {}) or {}
    comps, sfs = sat.get("computations", []) or [], sat.get("status_functions", {}) or {}
    out.update(n_computations=len(comps), n_status_functions=len(sfs))
    known = {n.id for n in mi.graph.nodes}
    try:
        for c in comps:
            _lint_expr(c["machine"], c["node"], known)
        for n, sf in sfs.items():
            for m in sf["mapping"]:
                if m["when"] != "otherwise":
                    _lint_expr(m["when"], n, known)
        out["lint_ok"] = True
    except (LintError, KeyError, TypeError) as e:
        out["error"] = f"lint: {str(e)[:120]}"
    try:
        r = B4bWeightedCSP().revise(AdapterOutput(mi, None, {}))
        flags = r.pathology_flags or {}
        out["b4b_ok"] = not any("UNSAT" in v for v in flags.values())
        out["b4b_flags"] = flags
        out["b4b_status"] = r.feasibility_status
    except Exception as e:
        out["error"] = f"b4b: {type(e).__name__}: {str(e)[:120]}"
    return out


def _log(record: dict) -> None:
    """Append every raw response as it arrives so a crash never loses calls."""
    with open(HERE / "repeatability_raw.jsonl", "a") as f:
        f.write(json.dumps(record) + "\n")


def call(cfg, model: str, system: str, user: str):
    """Transient 429/503 are retried with backoff (recorded); other errors abort.
    The served model must equal the requested id, else abort."""
    import time

    for attempt in range(6):
        t0 = time.perf_counter()
        try:
            r = chat(model, system, user, cfg["temperature"], cfg["seed"], cfg["max_output_tokens"],
                     cfg["model_params"].get(model))
            break
        except SystemExit as e:
            if not any(c in str(e) for c in ("HTTP 429", "HTTP 503")) or attempt == 5:
                raise
            time.sleep(15 * 2 ** attempt)
    if r.get("model") != model:
        raise SystemExit(f"ABORT: served model {r.get('model')!r} != frozen {model!r}")
    msg = r["choices"][0]["message"]
    u = r.get("usage", {})
    return msg.get("content") or "", {"served": r.get("model"), "finish": r["choices"][0].get("finish_reason"),
                                      "out_tokens": u.get("completion_tokens"), "retries": attempt,
                                      "latency_s": round(time.perf_counter() - t0, 1)}


if __name__ == "__main__":
    cfg_path = HERE / "config.frozen.json"
    if not cfg_path.exists():
        raise SystemExit("No config.frozen.json — freeze and get approval first.")
    cfg = json.loads(cfg_path.read_text())
    assert PROVIDER == cfg["provider_key"], "set REFLICA_LLM_PROVIDER to the frozen provider"
    report = {"provider": PROVIDER, "temperature": cfg["temperature"], "seed": cfg["seed"],
              "run_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "cases": []}
    for model in [m for m in [cfg["model_id"], cfg.get("secondary_model_id")] if m]:
        for sid in CASES:
            system, user = render_prompt(cfg["extractor_prompt"], rn.load_rn(sid))
            runs = []
            for i in range(cfg["repeats_per_call"]):
                text, meta = call(cfg, model, system, user)
                _log({"model": model, "scenario": sid, "repeat": i, "meta": meta, "content": text})
                runs.append((text, meta))
            texts = [t for t, _ in runs]
            report["cases"].append({
                "model": model, "scenario": sid,
                "output_sha256": [hashlib.sha256(t.encode()).hexdigest()[:16] for t in texts],
                "identical": len(set(texts)) == 1,
                "valid_json": all(_is_json(t) for t in texts),
                "schema_valid": [_schema_errors(t) == 0 for t in texts],
                "schema_error_counts": [_schema_errors(t) for t in texts],
                "downstream": [_downstream(t) for t in texts],
                "calls": [m for _, m in runs],
            })
    report["all_identical"] = all(c["identical"] for c in report["cases"])
    (HERE / "repeatability_report.json").write_text(json.dumps(report, indent=1) + "\n")
    print(json.dumps(report, indent=1))
