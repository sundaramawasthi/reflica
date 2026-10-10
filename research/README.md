# reflica-bench — M.Tech research benchmark

Attribute-aware revision of LLM-extracted state graphs under partial-satisfaction and capacity constraints.

The benchmark (`reflica_bench`) is intentionally separate from the Flutter Reflica product and will remain so. See `../PROGRESS.md` for the frozen design contract and current status.

This workspace also holds `reflica_service`, the product's local scientific-analysis service. It is isolated from `reflica_bench` (no imports in either direction, enforced by tests) and does not affect the frozen benchmark. See `reflica_service/NOTES.md`.

## Scope of this version

- **Benchmark v0.2.0:** 63 scenarios across all 7 categories (`reflica_bench/scenarios/`), fingerprinted in `reflica_bench/frozen_manifest.json`.
- **Ground truth:** hand-written labels, cross-checked by the independent exact generator `gt_engine.py`.
- **Deterministic baselines:** B3 (reachability), B4a (ATMS), B4b (weighted CSP / OR-Tools CP-SAT).
- **B5 (Reflica engine) v0.1.0:** `reflica_bench/b5/`, see `B5_REPORT.md`.
- **Natural-language layer:** renderer + leakage checker (`rn.py`) and the LLM pilot harness in `experiments/rn_pilot/` (B1, B2, extractor).
- The full 63-scenario LLM experiment has not been run yet.
- **Scientific-analysis service:** `reflica_service/` — CSV ingestion and `describe@1`, run with a time limit in a separate process.

## Install

```
cd research
python3 -m venv .venv
. .venv/bin/activate
pip install -e ".[dev,csp]"            # benchmark
pip install -e ".[dev,csp,service]"    # also the analysis service
```

`ortools` (the `csp` extra) is required for B4b and the Cat 5–7 tests.

## Run

```
pytest                          # everything: 203 benchmark + 296 service tests
pytest --ignore=tests/service   # benchmark only
```
