# reflica_service — implementation notes

Local scientific-analysis service for the first vertical slice described in `../PLATFORM_AUDIT.md`. Product work; it does not change the locked M.Tech thesis scope.

**Status (Step 2, after review fixes):** CSV ingestion (`csv_adapter.py`), `describe@1` and timeout-bounded execution (`execution.py`) are implemented and tested. `regress`, `sweep`, storage, the router and API routes are not implemented. `describe@1` is not yet frozen: its output may still change before the first commit of this package; after that, any output change requires a new version.

## Scientific-correctness requirements

1. A dataset labelled `controlled` must not automatically justify a causal claim.
2. Causal interpretation requires an appropriate experimental design and defensible, stated assumptions.
3. Prediction intervals must have documented statistical assumptions and validated calculations.
4. Extrapolation beyond the observed data range must be refused by `sweep`.
5. No arbitrary user-supplied code may be executed. Only the registered operations (`describe`, `regress`, `sweep`) may run, and every run requires explicit approval and a reproducible run record.

"Regression" in this package means statistical regression, not software regression testing.

## Boundaries

- Isolated from `reflica_bench`: no imports in either direction (enforced by `tests/service/test_scaffold.py`).
- Service dependencies (FastAPI, Uvicorn, pandas, NumPy) live in the optional `service` extra. They must only be imported inside functions, so the package imports without them.
- The existing tests and `reflica_bench/frozen_manifest.json` are regression guards and must stay unchanged.

## CSV ingestion rules (Step 2)

Standard library only; uploaded content is never evaluated.

- **Limits:** size (`max_upload_bytes`, checked on raw bytes before decoding), rows (`max_rows`), columns (`max_columns`, checked as soon as the header is read).
- **Encoding:** UTF-8 only; a BOM is removed; NUL bytes are rejected.
- **Header:** the first non-blank row. Names are trimmed; blank names (`empty_column_name`) and case-insensitive duplicates (`duplicate_columns`) are rejected. Numeric-looking names such as `2020,2021` are accepted; `describe` flags them with `numeric_header`.
- **Rows:** a line is blank only if it has no fields, or one whitespace-only field when the header has more than one column; blank lines are skipped. A row of empty fields such as `,` is a data row with missing cells. Every data row must have the header's field count (`malformed_row`, with line number); bad quoting is `malformed_csv`. A header with no rows is `no_data_rows`.
- **Missing values:** after trimming, empty or `NA`, `N/A`, `NaN`, `null`, `None` (case-insensitive). A single-column file must write a missing value as `""` or a token, because an empty line is blank.
- **Numeric inference:** numeric only if *every* non-missing value is a finite plain or scientific-notation number (no `inf`, thousands separators, underscores or hex). Integer-like values with a leading zero (`007`) make the column text, flagged `leading_zeros`. Otherwise at least half numeric → `mixed`; less → `text`; no values → `empty`.
- **Formula-like cells** (non-numeric values starting with `=`, `+`, `-`, `@`) stay plain text; any future export must escape them.
- **Memory:** cells are stored once, column by column; floats are computed on demand; duplicate rows are detected with a 16-byte hash per row (cells joined with NUL, which cannot occur in a cell).
- Errors are `CSVValidationError(code, message, detail)` with stable codes.

## describe@1 (Step 2)

- Per column: type, count, missing, missing fraction, exact distinct count; for numeric columns min, max, mean, median and sample SD (n − 1).
- **Numerical method:** values are rescaled by an exact power of two (lossless) before centring, which prevents overflow near the float limit and precision loss among subnormal values; constant columns get exactly zero deviations; SD uses the corrected two-pass formula; the mean is kept within [min, max]. A statistic that cannot be represented is `None` with a reason in `numeric.unavailable` (e.g. `"sd": "true value is outside the floating-point range"`). Verified against an exact rational-arithmetic reference on 20,000 randomised datasets (120 run in the suite).
- **Integers:** distinct counts for integer columns use exact Python ints. Integers above 2^53 are flagged `precision_loss`, because mean, median and SD are computed in floating point.
- **Correlations:** Pearson, between numeric columns, on pairwise-complete rows, labelled `association`. `r` is `None` with a `reason` when n < 3 or a side is constant on the paired rows. Columns are centred on their median (robust to outliers; since |mean − median| ≤ SD, complete columns cannot suffer cancellation) and every per-pair sum is one C-level `math.sumprod` call. A pair that is still ill-conditioned (centred sum of squares below 10⁻⁶ of the raw sum, e.g. the paired rows form a far-away minority cluster) is recomputed exactly on its own rows from the original values. A non-finite result is never clamped into a plausible r; it is reported as unavailable.
- **Bounded correlation work (hardware-independent):** the first numeric columns, in column order, are correlated up to `max_correlation_columns` (default 50) and up to `max_correlation_work` pairs × rows (default 5×10⁷; e.g. 32 columns at 100,000 rows). Others are listed in `correlations_skipped` with `reason` `column_limit` or `work_limit`. Exact recomputation may process at most `correlation_refine_budget_rows` rows (default 5×10⁶); a pair beyond that budget gets `r = None` with an explicit reason and the dataset-level issue `correlations_unrefined`.
- **Warnings vs invalid results:** `issues` and correlation `warnings` mark valid results that need care; `unavailable` and `reason` mark results that could not be computed.
- **Issue codes:** `constant_column`, `all_missing`, `high_missing` (> 20%), `possible_id_column`, `non_numeric_in_numeric`, `duplicate_rows`, `precision_loss`, `leading_zeros`, `small_sample` (< 10 values), `numeric_header`, `correlations_unrefined`.
- Output records operation, version, service version and the dataset SHA-256, so a result can later be attached as traceable evidence. Same input and configuration → identical output. Determinism is per Python version: Python 3.12+ uses `math.sumprod`, 3.11 a slower fallback whose last-digit rounding can differ, so future run records must store the Python version.

## Bounded execution (Step 2)

- `execution.run_describe(data, config)` parses and describes in a separate process (`spawn`) and stops it when `analysis_timeout_s` passes, raising `AnalysisTimeout`. A check inside the same process cannot stop a long pure-Python loop, so the limit is enforced from outside: SIGTERM, then SIGKILL after 2 s if the worker does not exit.
- Validation errors are passed back as `CSVValidationError`; unexpected worker errors as `AnalysisFailed`. Oversized input is rejected before a process starts. If the caller is interrupted while waiting, the worker is still stopped.
- Calling `describe()` directly has no time limit. A test enforces that no service module other than `execution.py` imports the analyses.
- Python's `multiprocessing.resource_tracker` process starts once per parent and exits with it; it is not a leak.
- Worker start-up costs about 0.1–0.2 s. The caller must run from an importable module (not code piped through stdin).
- **Tested on Linux only.** `spawn` is the default on macOS and Windows and `terminate()` maps to TerminateProcess on Windows, so the design is portable, but it has not been run there.

## Measured workloads (this machine, Linux, Python 3.13, 2026-10-10)

Observations, not guarantees: timings depend on hardware. All through `run_describe` (30 s limit) unless noted.

| Input (at or near the limits) | Total time | Correlations | Peak RSS (in-process) |
|---|---|---|---|
| 5 cols × 100,000 rows (3.8 MB) | 1.1 s | 10/10 | 107 MB |
| 50 cols × 26,579 rows (10 MB) | 3.0 s | 1,225 | 225 MB |
| 50 cols × 29,114 rows, 10% missing (10 MB) | 5.1 s | 1,225 | 298 MB |
| 200 cols × 6,644 rows (10 MB) | 2.7 s | 1,225 (18,675 skipped: column limit) | 185 MB |
| 50 cols × 100,000 rows, 1-digit cells, 5% missing (9.3 MB) — hardest found | 12.5 s | 496 (work limit) | — |
| Adversarial: unpaired outliers, 50 cols × 100,000 rows (9.5 MB) | 12.0 s | 496/496 computed | — |
| Adversarial: minority clusters forcing exact recomputation, 32 cols × 100,000 rows | 9.1 s | 496/496 computed | — |

Before the Step 2 review the 200-column file ran for over 10 minutes; before the timeout-risk fix the outlier pattern hit the 30 s limit and returned nothing.

**Guaranteed by tests:** limits on size, rows and columns; correlation work bounded by `max_correlation_work` and `correlation_refine_budget_rows`, with every skipped or unrefined correlation reported; a running analysis is stopped at the time limit and its process cleaned up. **Not guaranteed:** any particular wall-clock time on other hardware (the time limit remains the backstop), or any bound on memory beyond the size limit (about 20–30× the file size was observed).

## Optional test-only reference: statsmodels (not added)
Using `statsmodels` as a reference for `regress@1` tests would give an independent, widely used implementation to compare against. Trade-offs: it pulls in SciPy, pandas and patsy (large installs, slower CI), its versions change numerical details over time, and agreement with it is evidence of consistency, not of correctness. If added, it belongs in a separate optional `reference` extra used only by tests that skip when it is absent, so neither the runtime nor the benchmark depends on it. Textbook datasets with published coefficients are a complementary reference that needs no dependency.
