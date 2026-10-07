# reflica-bench — M.Tech research benchmark

Attribute-aware revision of LLM-extracted state graphs under partial-satisfaction and capacity constraints.

This workspace is intentionally separate from the Flutter Reflica product and will remain so. See `../PROGRESS.md` and the memory file `benchmark_cross_category_synthesis.md` for the frozen design contract.

## Scope of this version

- Category 1 floor only: Irrelevant Change / No Propagation.
- Deterministic baselines only: B3 (reachability), B4a (ATMS), B4b (weighted CSP + rule engine).
- No LLM code. No B1, B2, B5. No natural-language regime yet.

## Install

```
cd research
python3 -m venv .venv
. .venv/bin/activate
pip install -e ".[dev,csp]"
```

If `ortools` has no wheel for your Python version, install without the `csp` extra; the Cat 1 floor cases do not exercise the CSP solver. Later categories will.

## Run

```
pytest
```
