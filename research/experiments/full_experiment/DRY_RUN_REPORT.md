# Dry-run report — confirmatory experiment preparation (2026-10-09)

**Verdict: technically ready; waiting for owner approval.** Every pre-run
gate passes and the whole pipeline (runner → scoring → statistics → report)
has been exercised offline. No model call was made. The paid run must not
start until the owner (1) approves `PROTOCOL.md` v2, (2) rotates the NVIDIA
key, and (3) explicitly approves the run.

## 1. What was built

| File | Purpose |
|---|---|
| `run.py` | Runner for all 63 scenarios: LLM→B4b **and LLM→B5**, gold gates, B6, staged failure attribution, confidence-preserving label remapping, append-only logging, resumable runs, one data-completion pass, served-model abort, explicit paid-run flag |
| `analyse.py` | H1–H3 decision rules, four failure-handling analyses, operational failure table, Markdown report |
| `stats.py` | Paired scenario-level bootstrap (10,000 resamples, seed 20261009), cluster bootstrap for pooled rates, Holm |
| `PROTOCOL.md` | Revised protocol v2 (D1–D7) |
| `reflica_bench/rn/full/*.rn.json` | 63 natural-language scenario files (frozen renderer, 0 leakage) |
| `tests/test_full_experiment.py` | 30 offline tests |

Not modified: the benchmark, gold answers, manifest, `config.frozen.json`,
prompts, schemas, `pilot.py`, `repeatability.py`, `_api.py`, B5, the pilot
records. `git diff` on tracked files is empty.

## 2. Offline validation

| Check | Result |
|---|---|
| Full test suite | **233 / 233 pass** (203 existing + 30 new) |
| Pre-run gates (`run.py check`) | **pass**: manifest, all fingerprints, 63 R-N files (equal to fresh render, leak-free, pilot files identical), gold→B4b and gold→B5 on all 63 |
| Pilot raw data re-scored by the new runner (operational view only) | B1 48/48 ok · B2 48/48 · LLM→B5 48/48 · LLM→B4b 47/48 (1 `solver_failure`) · gold gates 16/16 each · 0 evaluation failures |
| Failure attribution on real data | T7.2 r1 (invented preference rule): extraction schema- and lint-valid; **B4b raised → `solver_failure`**, B5 abstained → `ok`. The pilot harness had counted this as an extraction failure |
| Confidence propagation | B5 confidence present on 48/48 scored rows (the pilot `_remap` dropped it) |
| Scoring determinism | Re-scoring twice gives byte-identical `scores.jsonl` |
| Repeat identity (pilot, operational) | All 3 repeats byte-identical: B1 9/16, B2 9/16, EXTRACT **1/16** scenarios → temperature 0 is not deterministic; repeats are needed |
| Analysis pipeline | Runs end to end on the dry-run scores (all four handling rules, H1–H3) |

Per protocol §2, no accuracy, effect size or verdict computed from pilot data
was inspected; the dry-run outputs were written outside the repository.

### Controlled failure tests (synthetic or injected, no network)

Missing call · API error · truncated B1 · unparseable B2 · four kinds of
invalid extraction (all shared identically by both methods) · B4b crash ·
B5 crash · harness defect (`evaluation_failure` invalidates the run) ·
completion pass retries at most once · served-model mismatch aborts the run ·
the run refuses to start if gates fail · the CLI refuses a paid run without
`--i-approve-paid-run` · resumed runs make no duplicate calls.

### Statistics tests

Constant differences (CI collapses, p = 1 or 0) · seeded determinism ·
agreement with normal theory on n = 400 (±0.02) · Holm vs hand computation ·
zero-denominator resamples skipped · H1 floor effect is not supported · a
weak Cat 6-B **cannot be concealed** by a passing aggregate (H2 → not
supported) · H3 false-abstention PASS / FAIL / INCONCLUSIVE · shared
failures scored identically for both methods · infrastructure failures
excluded pairwise · repeats averaged within a scenario (one unit, not three).

## 3. Expected calls, cost and runtime

| Item | Estimate | Method |
|---|---|---|
| Calls | **567** = 63 × 3 call types × 3 repeats | `run.py plan` |
| Input tokens | **≈ 1.59 M** | rendered prompt characters ÷ 4 (`run.py plan`); replace with exact `usage.prompt_tokens` from the first calls |
| Output tokens | ≈ 0.87 M (pilot median 1,536/call) up to 3.2 M (pilot max 5,708/call) | pilot completion tokens, which include reasoning |
| Cost | trial credits consumed per request on the NVIDIA free tier; on a paid endpoint, tokens × the provider's price | check the remaining credit balance before starting |
| Wall time | ≈ 2.4 h at the pilot median (60 s/call, 4 workers); budget **4–6 h** with retry back-off | pilot latency and retry counts |

## 4. How to run (after approval)

```bash
cd research
python3 -m venv .venv && . .venv/bin/activate
pip install -e ".[dev,csp]"
pytest -q                                               # gate 1: 233 passed

cd experiments/full_experiment
python run.py check                                     # gates 2–5, no API
python run.py plan                                      # 567 calls, no API

export REFLICA_LLM_PROVIDER=nvidia                      # NVIDIA_API_KEY already in your shell profile
python run.py run --run-id confirmatory_v1 --i-approve-paid-run --workers 4
python run.py run --run-id confirmatory_v1 --i-approve-paid-run --completion   # only if calls failed
python run.py score --run-id confirmatory_v1
python analyse.py --scores runs/confirmatory_v1/scores.jsonl --out runs/confirmatory_v1
```

The run is resumable: re-running `run` makes only the calls not yet logged.

## 5. Reproducibility

- Outputs: `runs/confirmatory_v1/{raw.jsonl, env.json, scores.jsonl,
  summary.json, analysis.json, report.md}`. `raw.jsonl` is append-only.
- `env.json` records Python version, `pip freeze`, git commit, and SHA-256 of
  `PROTOCOL.md`, `run.py`, `analyse.py`, `stats.py`. It never records
  environment variables or keys.
- To reproduce the analysis: run `score` and `analyse.py` on the same
  `raw.jsonl`; results are deterministic (fixed seed, sorted output).
- Commit the code and protocol **before** the run so `env.json` points at a
  clean commit (`git_dirty: false`).

## 6. Go / no-go checklist

- [x] Runner with LLM→B5, gold gates and staged failure attribution
- [x] Confidence remapping bug fixed (in the new runner; pilot code untouched)
- [x] 63 R-N files written; leakage checker clean on all 63
- [x] Statistics and reporting code, with tests
- [x] Offline dry run on pilot data, synthetic fixtures and injected failures
- [x] 233/233 tests pass; all gates pass
- [ ] Owner approves `PROTOCOL.md` v2 (including the open decisions below)
- [ ] Code and protocol committed (owner approval needed) so the run starts from a clean commit
- [ ] NVIDIA key rotated and set in the shell only
- [ ] Trial credit / budget checked
- [ ] Owner gives explicit approval to start the paid run

## 7. Open methodological decisions for the owner

1. **H2 Cat 6-B (n = 4).** The rule requires non-inferiority in every
   category, so "supported in aggregate only" is the likely ceiling for H2.
   Accept this, or prespecify Cat 6-B as descriptive-only?
2. **H3 power.** With 37 determinable nodes, PASS needs an observed
   false-abstention rate near 0; INCONCLUSIVE is likely. Accept as stated?
3. **Shared lint check.** A schema-valid extraction that fails formula lint
   is a shared `extraction_failure` (the same check the pilot already used).
   Confirm that lint belongs to "extraction validity" rather than to each
   method.
4. **Worst-case for Cat 7 failures** counts both false confidence (all
   ambiguous nodes) and false abstention (all determinable nodes) at once —
   the worst value for each metric separately. Confirm.
5. **Repeats.** R = 3 as in the frozen config. More repeats would narrow
   within-scenario noise but do not add scenarios (power is limited by
   n = 16–25). Keep 3?
