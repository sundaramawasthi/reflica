# reflica-bench — M.Tech research benchmark

Attribute-aware revision of LLM-extracted state graphs under partial-satisfaction and capacity constraints.

This workspace is intentionally separate from the Flutter Reflica product and will remain so. See `../PROGRESS.md` for the frozen design contract and current status.

## Scope of this version

- **Benchmark v0.2.0:** 63 scenarios across all 7 categories (`reflica_bench/scenarios/`), fingerprinted in `reflica_bench/frozen_manifest.json`.
- **Ground truth:** hand-written labels, cross-checked by the independent exact generator `gt_engine.py`.
- **Deterministic baselines:** B3 (reachability), B4a (ATMS), B4b (weighted CSP / OR-Tools CP-SAT).
- **B5 (Reflica engine) v0.1.0:** `reflica_bench/b5/`, see `B5_REPORT.md`.
- **Natural-language layer:** renderer + leakage checker (`rn.py`) and the LLM pilot harness in `experiments/rn_pilot/` (B1, B2, extractor).
- The full 63-scenario LLM experiment has not been run yet.

## Install

```
cd research
python3 -m venv .venv
. .venv/bin/activate
pip install -e ".[dev,csp]"
```

`ortools` (the `csp` extra) is required for B4b and the Cat 5–7 tests.

## Run

```
pytest
```
