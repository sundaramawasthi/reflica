# Full experiment — protocol

**Status: DRAFT v0.6 (2026-10-10) — NOT FROZEN. No full-run LLM call may be made until the owner approves a final version and it is frozen (§10).**
Benchmark v0.2.0 (manifest `27b6ea09…6915`) · B5 v0.1.0 (id `fc9524a4ea38cca5`) · LLM config v1.7 (`../rn_pilot/config.frozen.json`)

Earlier drafts are kept unchanged in `drafts/` (v0.1 `e112437b…`, v0.2 `fefe80e5…`, v0.3 `7bf5dc51…`, v0.4 `697b4380…`,
v0.5 `efd02192…`). Every change to hypotheses, tests or analysis type, with date, rationale, evidence inspected and
implications, is in `HYPOTHESIS_CHANGES.md` (change 5 = this version). The evidence behind the v0.6 decisions is in
`DECISION_REPORT_S1_S4.md`.

**v0.6 in one paragraph.** The analysis is **descriptive**. The full experiment will report estimates, uncertainty
where it is adequately calibrated, scenario-level results as secondary information, and error patterns. It issues **no
confirmatory Supported/Contradicted verdicts and no p-values**, because no procedure examined was both well calibrated
and able to answer the approved node-level questions at n = 63 (or 11). D1 and D2 keep their approved node-level
meaning and appear only as reference lines. This is provisional for this run: a larger or better-designed
confirmatory study can be planned after the results are seen, and would be a separate, newly pre-registered study.

---

## 0. Decisions

### Closed by the owner (2026-10-10)

| # | Decision |
|---|---|
| D1 | τ_FA = 0.15 = maximum acceptable **false-abstention rate on determinable gold nodes** (node level). Unchanged. Under S1 = D it is a reference line, not a test. |
| D2 | δ = 0.05 = margin for B-B5 vs B-B4b on **mean node correctness** (node level). Unchanged. Under S1 = D it is a reference line, not a test. |
| D3 | Held-out set (~2 per category) only if built rigorously before the run (§8); otherwise proceed and disclose. |
| D4 | 3 repeats per scenario and LLM call type. |
| D5 | Outage: pause and retry under the same frozen configuration up to 7 days; otherwise stop. Never mix models; restarts with a changed model or configuration need an amendment, a new configuration hash and a separate run folder. |
| N1 | H3 removed from the confirmatory family; RQ2 descriptive with N/A for unsupported metrics. |
| N2 | Owner authors the held-out scenarios; a supervisor or qualified second reviewer reviews them independently. No approval assumed until recorded. |
| N3 | Held-out deadline 2026-10-24 (provisional); if not ready, proceed and disclose. |
| N4 | All drafts preserved; changes documented in `HYPOTHESIS_CHANGES.md`. |
| P1 | Sign-flip test approved conditionally; assumptions checked and found not defensible; withdrawn. |
| P2 | Freeze only after the runner exists and passes offline tests: done in the review container. |
| P3 | Exact pins; real environment recorded on the run machine; pilot environment documented as unrecorded. |

### Provisional decisions by the owner (2026-10-10) — to be confirmed before freezing

| # | Decision |
|---|---|
| **S1 = D** | **Descriptive estimates only.** No confirmatory verdicts for H1, H2, H4, H5a, H5b with the current procedures. Report node-level outcomes, effect estimates, uncertainty where appropriate, scenario-level results as secondary descriptive information, and error patterns; keep descriptive evidence clearly separate from confirmatory inference. Provisional for this run, not permanent. |
| **S2** | **D1 and D2 keep their approved node-level definitions.** Nothing is redefined at scenario level. §2 states which questions can be answered descriptively and which need a better-powered confirmatory design. |
| **S3** | **External verification accepted provisionally.** The corrected Newcombe implementation and the independent reference tests are kept. Verification method, versions, cases and limitations: Appendix D. Agreement between implementations does **not** establish statistical calibration. |
| **S4** | **DRAFT / NOT FROZEN.** No model/API calls, no full run, no freeze, no commit or push. The owner reviews the decision report and runs `preflight.py` on the intended machine before deciding on freezing. |

---

## 1. Research questions

- **RQ1 (architecture).** Under natural-language input, how does *extract → symbolic revision → determinability check* (B5) compare with direct LLM reasoning (B1, B2) in node-level correctness?
- **RQ2 (attribute awareness), descriptive.** Which methods can represent partial satisfaction and capacity (Cat 5–6), and how accurately do those that can compute attribute values after LLM extraction?
- **RQ3 (knowing when not to answer).** How often is each method falsely confident on ambiguous nodes, and how often does B5 abstain on nodes it could have answered?
- **RQ4 (failure attribution), exploratory.** When B5 is wrong, is the shared extraction already wrong, or is the extraction right and the revision wrong?

## 2. Questions, estimands and what this run can and cannot establish

The hypotheses H1–H5 are kept as **directional expectations stated before the run**, so the report can say whether
the estimates point the expected way. They are **not tested**. Each is answered by the estimand below.

| ID | Original expectation | Node-level estimand (approved) | Reported | Can this run answer it? |
|---|---|---|---|---|
| H1 | B-B5 more correct than B1 | mean over scenarios of B-B5 − B1 node correctness | estimate, 95% t-interval, counts of scenarios higher/equal/lower | **Descriptively.** Direction and size with approximate uncertainty (simulated coverage 0.934–0.959). A confirmatory claim needs a design whose test is calibrated under clustered errors (see "Future confirmatory design"). |
| H2 | B-B5 more correct than B2 | same, vs B2 | same | same as H1 |
| H3 | *Removed (N1).* | — | RQ2 descriptive table | — |
| H4 | B-B5 not worse than B-B4b by more than δ = 0.05 (D2) | mean difference B-B5 − B-B4b | estimate, 95% t-interval, and whether the interval's lower end lies above −0.05 **as a description** | **Descriptively.** The simulated chance that the lower end lies above −0.05 when the true difference is exactly −0.05 was up to 4.0% (nominal for a test would be 2.5%), so this is orientation, not non-inferiority. |
| H5a | B-B5 less often falsely confident than B-B4b, B1, B2 | pooled false-confidence rate on the 19 ambiguous nodes (11 scenarios) | counts and rates per method, per-scenario table; **no interval** | **Descriptively only, and weakly.** 11 scenarios: no interval was adequately calibrated; any difference is reported as counts. A confirmatory answer needs many more ambiguous scenarios. |
| H5b | B-B5 false abstention below τ_FA = 0.15 (D1) | pooled false-abstention rate on 211 determinable nodes | rate, counts, number of scenarios affected, position relative to 0.15 **as a description**; **no interval** | **Descriptively.** Rare, clustered abstentions made the simulated bootstrap interval cover only 0.70, so no interval is reported. |

**Future confirmatory design (not part of this run).** A confirmatory test of H1/H2/H4 at node level needs either a
much larger scenario set (so that tests of the mean are calibrated despite clustered, all-or-nothing errors), or a
pre-specified estimand whose test is exact and whose meaning is accepted (e.g. a binary scenario endpoint, accepting
that it rewards clustered errors). H5a needs many more ambiguous scenarios. Any such study is planned after this run,
pre-registered separately, and run on new scenarios.

## 3. Conditions and methods

| Condition | Input | Methods | Role |
|---|---|---|---|
| **B (main)** | plan_text + change_text → shared extractor (one call per scenario per repeat) → identical structured input to every symbolic method | B3, B4a, B4b, **B5** | Confirmatory for B4b and B5; B3, B4a descriptive |
| **Direct LLM** | plan_text + change_text | B1, B2 | Confirmatory comparators (H1, H2, H5a) |
| **A (sanity)** | gold structured input, no LLM | B3, B4a, B4b, B5 | Descriptive only |

Fixed for every call (config v1.7): model `nvidia/nemotron-3-ultra-550b-a55b`, provider `nvidia`, temperature 0, seed
20261008, thinking on, max 16,384 output tokens, prompts `b1_full_regeneration.v1.1`, `b2_delta.v1.1`,
`extractor.v1.1`, `common_reasons`, schemas `extractor_output.schema.v1.4`, `revision_output.schema.v1`. Parsing and
label mapping use the pilot's approved rules (`from_direct`, `_remap`, fingerprinted). Budget: 63 × 3 × {B1, B2,
EXTRACT} = **567 calls** (+126 with a held-out set). A re-run of a failed call (§7) is logged and is not extra budget.

## 4. Metrics

### 4.1 Node classification (unchanged from v0.3)

`reflica_bench/endpoints.py::node_counts`, built only from the evaluator's `_abstained` and `_node_correct`, puts every
gold node in exactly one class per scenario-repeat: correct, falsely confident (ambiguous, committed), falsely abstained
(determinable, abstained) or committed-wrong. A failed output (unparseable, schema-invalid, truncated, extraction or
solver failure) handles no node correctly; a missing node counts as committed and wrong and as a missing prediction.
B3 and B4a output no attribute values (labels only). Verified against the evaluator: Appendix A, check 1.

### 4.2 Primary descriptive quantities (node level)

- **Node correctness** per scenario-repeat = correct nodes / gold nodes; per scenario = mean over common repeats (§7); per method = mean over the analysis set (every scenario equal weight).
- **Paired differences** B-B5 − X per scenario, for X ∈ {B1, B2, B-B4b}; summarised by their mean, a 95% t-interval and the numbers of scenarios where B5 is higher, equal and lower.
- **False confidence**: falsely confident nodes on ambiguous gold nodes (mean over common repeats), pooled over the ambiguous scenarios; per scenario as a table.
- **False abstention (B5)**: falsely abstained nodes on determinable gold nodes, pooled; plus the number of scenarios with any.

### 4.3 Secondary descriptive quantities

- **Scenario level** (secondary, with a stated caution): per comparison, the 2×2 table of "fully correct" (all gold nodes correct, in ≥ half of common repeats) and, on the ambiguous subset, of "any false confidence"; B5's number of scenarios with any false abstention. *Caution printed with every table:* a binary scenario endpoint favours a method whose errors cluster within scenarios, even at equal node accuracy.
- **False abstention for every method** (context for H5b), pooled rate and number of scenarios affected.
- **Fully-correct scenarios by category and method** (secondary, same caution).
- **Condition A (gold input, no LLM):** node correctness, fully-correct scenarios, false confidence and false abstention per symbolic method over all 63 scenarios; a sanity check, never evidence of extraction accuracy.
- **Error patterns:** node correctness by category and method; failure statuses and missing predictions by method; RQ4 attribution of each wrong B5 scenario-repeat to "extraction deviates from gold" or "extraction correct, revision wrong" (exploratory).
- **RQ2:** Cat 5 / 6-A / 6-B evaluator metrics, mean over scenarios where computed with the number of scenarios; N/A (never zero) where a method does not output the dimension.
- **Cost:** tokens, latency, calls; extraction quality as in the pilot.

## 5. Statistical analysis plan (descriptive)

Code: `experiments/full_run/analysis.py`, `reflica_bench/stats.py`. Tests: `tests/test_full_run.py`, `tests/test_stats.py`, `tests/test_reference_r.py`.

- **Unit:** the scenario; repeats averaged within a scenario over its common repeats; all methods on the same analysis set (§7).
- **Intervals:** 95% one-sample **t-interval** over scenarios for node-correctness means and paired differences (Student-t quantile computed exactly and checked against R `qt`). Chosen because it had the best simulated coverage among the procedures examined (0.934–0.959; percentile bootstrap 0.907–0.933; bootstrap-t 0.896–0.948). It is approximate; its calibration is stated next to every interval in `results.json`.
- **No interval** for false-confidence (≤ 11 scenarios) or false-abstention rates (rare, clustered) — counts only.
- **No hypothesis tests, no p-values, no multiplicity adjustment, no verdicts.** Reference lines for D1 and D2 are reported as positions ("lower end above −0.05", "estimate below 0.15"), labelled "orientation only".
- **Not used:** the sign-flip and Wilcoxon tests and the bootstrap percentile intervals from earlier drafts (simulation showed miscalibration in the plausible error structure); the exact McNemar, Newcombe, Tango and Clopper–Pearson implementations stay in the code, verified, for a possible future confirmatory study.
- **Interpretation rule:** an interval excluding 0 is described as "the estimate and its approximate interval lie above (below) zero", never as "significant" or "supported".

## 6. Reporting rules

- Every question in §2 is reported, whatever the direction of the estimate.
- Descriptive results are never called confirmatory; the words "significant", "supported", "proved" are not used for them.
- Node-level results are reported first; scenario-level results follow, with the clustering caution.
- The thesis states that this run was descriptive by design and why (DECISION_REPORT_S1_S4).

## 7. Eligibility, failures and missing data (unchanged rules; now implemented in the runner)

Statuses per call: **ok**, **model failure** (scored, §4.1), **infrastructure missing** (failed twice, or never made).
1. B1 and B2 have their own calls; all four Condition B methods inherit the status of the EXTRACT call of the same scenario and repeat.
2. A repeat is **common** if none of B1 r, B2 r, EXTRACT r is infrastructure missing.
3. **Analysis set** = scenarios with ≥ 1 common repeat; every method and every confirmatory comparison uses this one set and these repeats. H5a uses its scenarios with ≥ 1 ambiguous gold node.
4. Model failures are never missing. 5. Excluded scenarios are excluded for every method and listed. 6. **Stop rule:** > 5% of planned calls infrastructure missing → stop before analysis.
7. **Missingness report** per call type × category and per condition × method (ok / model failure / infrastructure missing / missing predictions), plus excluded scenario ids.

Failure handling in the runner: transient 429/503 retried with backoff inside the pilot client; any other failure of a
call is recorded and the call is re-run **once** later (`runner.py retry`); 5 consecutive infrastructure failures pause
the run (D5); a resume more than 7 days after the pause began stops it permanently; a served-model mismatch, an
`ABORT`, a missing key, a wrong provider or a gate failure stops it immediately.

## 8. Held-out set (unchanged from v0.3)

**Status: NOT CREATED. No held-out scenario, gold label or review exists.** Owner authors; a supervisor or qualified
second reviewer independently reviews scenarios and gold labels and signs `heldout/REVIEW.md`. 14 scenarios (Cat 1–5 ×2,
Cat 6 = one 6-A + one 6-B, Cat 7 ×2 with ambiguous nodes), written from category definitions and schema only, new
domains, scripted near-duplicate check. Gold labels must agree with `gt_engine`, linter and leakage checker; only
evaluator-side tools touch them before freezing. Own SHA-256 manifest, hash in the lock before any call; benchmark
v0.2.0 unchanged; B5 stays v0.1.0. Must be complete before the main run and by 2026-10-24 (provisional), else omitted
and disclosed. Analysed separately as a pre-registered replication with the same endpoints: estimates and CIs, no
verdicts, *consistent / not consistent* per hypothesis. The runner does not yet load held-out scenarios; adding that is
an amendment-before-freeze item if the set is built.

## 9. Runner, gate, fingerprints and environment

### 9.1 Runner (`experiments/full_run/runner.py`)

| Command | API | Does |
|---|---|---|
| `env-check` | no | compares this interpreter and packages with `requirements-experiment.lock` |
| `run RUN_DIR` | yes | full gate → `gate.json` → `environment.json` → `plan.json` → calls in plan order |
| `retry RUN_DIR` | yes | one re-run of calls whose every attempt failed for infrastructure reasons |
| `score RUN_DIR` | no | final outputs → node counts and evaluator metrics (`scores.jsonl`) |
| `validate RUN_DIR` | no | integrity and completeness (below) |

- **Plan:** all 63 scenarios rendered in memory (leakage-checked), jobs = scenario × call type × repeat, sorted then shuffled once with seed 20261010; saved before the first call and recomputed and compared on every start.
- **Order:** one call at a time, in plan order (≈ 9–10 h at the pilot's median 60 s per call).
- **Gate before every request:** `Runner._request` runs the full gate — `assert_ready_for_llm_calls` (lock valid, every fingerprint equal to the active lock entry, existing records consistent, environment equal to the lock) plus the provider and key check — immediately before each transport call. It is the only place the transport is called (AST-tested).
- **Logging:** every attempt (ok or failed) is appended to `raw.jsonl` with scenario, call, repeat, plan index, attempt, timestamps, raw content and response metadata (served model, finish reason, tokens, latency). Owner-only permissions (file 0600, folder 0700), fsync per record, each line chained to the previous one by SHA-256. The API key is never written: the exact key value and key-like strings are redacted and the record is flagged.

### 9.2 Validation and analysis

`validate` refuses a run folder unless: the gate record matches a frozen lock version; the plan equals the
pre-specified plan; the recorded environment equals the gated one; the hash chain is intact; every record belongs to
the plan with the right index; first attempts are in plan order; ≤ 2 attempts per job and none after a success; every
served model equals the frozen id; no key-like string is present; the log is not readable by others; and (complete
mode) every job was attempted, every infrastructure failure was re-run once, the run was not stopped, and the stop
rule did not trigger. `analysis.py` runs only on a folder that passes complete validation, and writes `results.json` (descriptive only: no verdicts, no p-values; test-enforced).

### 9.3 Fingerprints (gate-checked unless marked)

Protocol file · benchmark manifest and scenario files · deterministic renders of all 63 · B5 files and version id ·
LLM config, prompts, schemas, client · analysis code (evaluator, endpoints, stats, schema, loader, adapters, baseline,
extraction schema, protocol_lock) · runtime code (rn, linter, gt_engine, groundtruth, groundtruth_quant) · all baselines ·
pilot code reused by the runner (`_api.py`, `repeatability.py`, `pilot.py`) · **every `.py` under `full_run/`**
(runner, analysis) · Python version and exact versions of pydantic, pydantic-core, ortools, networkx, protobuf, numpy ·
sha256 of `requirements-experiment.lock` · *record only:* hash of the full installed-package list · held-out manifest if any.

### 9.4 Environment (P3)

`research/requirements-experiment.lock` pins every installed package exactly and Python 3.13.16. It is
**provisional**: generated in this review container (Linux x86_64), where all tests pass. Before freezing, on the
machine that will run the experiment: install it (`pip install -r requirements-experiment.lock && pip install --no-deps
-e .`), run `python experiments/full_run/runner.py env-check` and the full test suite, and take the freeze fingerprints
there (S4). The gate refuses any request if the interpreter or a pinned version differs. Each run folder records the
actual environment (`environment.json`: Python, platform, full package list).

**Pilot environment (not recorded).** The pilot (config v1.7) recorded only "python 3.14.3" and its client and runner
fingerprints. It did **not** record package versions, the OR-Tools version used by B4b, the operating system or the
machine. `ortools` was and is unpinned in `pyproject.toml` (`>=9.9`). Pilot results are therefore **not claimed to be
fully reproducible**: re-scoring the pilot's saved raw outputs under the pinned environment is possible (no API), but
whether that reproduces the pilot's original B4b numbers exactly is unknown, and calls to the model cannot be replayed.

### 9.5 Entry points

Only `runner.py` under `full_run/` may import anything that can reach a model (test-enforced). The pilot scripts
(`pilot.py run`, `repeatability.py`, `list_models.py`, `gemini_models.py`) can still call the API without this gate;
they are fingerprinted unchanged, cannot address the full run (test), and the analysis refuses any run folder without
a valid gate record.

## 10. Freezing and amendments

**Freeze checklist** (in order; none done yet): (1) owner confirms the provisional S1–S4 decisions (§0); (2) held-out set complete and reviewed, or
deadline passed and omitted; (3) on the run machine: install the lock, `env-check` passes, full test suite passes;
(4) owner's explicit written approval of the final text; (5) copy it to `PROTOCOL.v1.0.md` with status FROZEN, mark
`PROTOCOL.md` SUPERSEDED, write `protocol_lock.json` with `fingerprints()` taken on the run machine.

After freezing, tests fail if a listed file is edited or deleted, its status is not FROZEN, or `PROTOCOL.md` is not
SUPERSEDED. **Amendments stay possible:** a new `PROTOCOL.v1.N.md`, a new lock entry chained by `supersedes` with fresh
fingerprints, and an `AMENDMENTS.md` entry with both hashes, date, reason and expected effect; the gate then checks the
new version. Each run folder's gate record names the version it ran under; an amendment made after a run started
applies only to a new run folder. During the run: no protocol change, no look at aggregated results before validation
passes, deviations to `DEVIATIONS.md` before analysis, every question in §2 reported whatever the direction of the estimate.

## 11. Known limitations (reported in the thesis)

- **Descriptive only (S1 = D):** this run cannot establish B5's superiority, non-inferiority or threshold compliance with controlled error rates; it can show direction, size and approximate uncertainty.
- The t-intervals are approximate (simulated coverage 0.934–0.959; at the D2 reference line the lower end exceeded −0.05 in up to 4.0% of simulations where the true difference was exactly −0.05).
- No interval for false confidence (11 scenarios) or false abstention (rare, clustered).
- Scenario-level results reward clustered errors; they are secondary and printed with a caution.
- Simulated error structures are assumptions; the real ones are unknown until data exist.
- B5 was designed with the 63 scenarios visible; the held-out set addresses this only if built.
- H3 removed after Condition A sanity results; the statistical approach changed twice after simulation and once after external verification (`HYPOTHESIS_CHANGES.md`). No experimental data existed at any change.
- External verification shows that our implementations agree with an independent R implementation; it does not show that any method is calibrated for this experiment (Appendix D).
- Pilot environment not recorded; pilot not claimed fully reproducible. Experiment environment provisional until confirmed on the run machine.
- Pilot scripts are ungated; one model and provider (free tier); temperature 0 not guaranteed deterministic; synthetic template-rendered language; the 63 scenarios are a fixed benchmark, not a random sample.

---

## Appendix A — checks performed (2026-10-10, no model or API calls)

| # | Check | Result |
|---|---|---|
| 1 | `node_counts` vs `evaluate_category_7`, 63 scenarios × 4 methods, gold input | 145 cross-checks, 0 mismatches |
| 2 | Condition A | primary B3 0.885 · B4a 0.904 · B4b 0.952 · B5 1.000; Cat 5–6 labels 107/107 for all |
| 3 | Statistical procedures (simulation) | Appendix C and `DECISION_REPORT_S1_S4.md` §2 |
| 4 | Implementations vs R | Appendix D |
| 5 | Records vs disk; renders | all match; 0 leakage problems |
| 6 | Freeze, amendment, gate, environment lock | tested (temporary directories) |
| 7 | Runner offline (network blocked; pilot replay) | full gate before every request; ordering; failures; logging; validation; scoring; descriptive analysis; deterministic |
| 8 | Descriptive analysis | no verdict/p-value keys or values anywhere in `results.json` (structural test); every interval labelled APPROXIMATE and DESCRIPTIVE; H5a/H5b no-interval reasons and clustering cautions present (tested); Condition A summary reproduces Appendix A check 2; node-level estimate and B5 − B1 sign equal hand computations; RQ4 attribution counts sum to all B5 scenario-repeats |
| 9 | Mutation checks | 17 earlier + 3 on the descriptive analysis (sign of differences, validation bypass, majority rule): all caught |
| 10 | Preflight | passes in the review container (not the intended machine) |
| 11 | Full test suite | **284 passed** |

## Appendix B — changes from v0.5

S1 = D, S2, S3, S4 recorded as provisional owner decisions · §2 rewritten: hypotheses kept as stated expectations,
answered descriptively, with what each can and cannot establish · §4.2/4.3, §5, §6 replaced by the descriptive plan
and reporting rules · `analysis.py` rewritten to descriptive output · t-interval with exact t quantile (checked against
R `qt`) · §11 updated · Appendix D added · v0.5 archived.

## Appendix C — statistical assumption analysis (offline simulation, seeds fixed; scripts in `simulations/`)

*Under S1 = D none of the tests below is used for this run; the tables record why. The expanded study is `simulations/s1_study.py` (output `simulations/s1_study_output.txt`), summarised in `DECISION_REPORT_S1_S4.md` §2.*

Structure: H5a 11 scenarios with 1,1,1,1,1,1,2,2,2,3,4 ambiguous nodes; H1/H2 63 scenarios with their real node
counts (2–7); 3 repeats. Key realistic feature: B5 is deterministic given the extraction, so its errors tend to be
all-or-nothing per scenario, while B1/B2 vary node by node.

| Procedure (v0.3) | Null scenario (equal expected values) | False "B5 better" | Nominal (one direction) |
|---|---|---|---|
| Sign-flip, H5a counts | B5 all-or-nothing vs X node-wise, p = 0.3 | 1.95% at α 0.01 · 4.7–6.4% at α 0.05 (full verdict rule, p = 0.1–0.3) | 0.5% · 2.5% |
| Sign-flip, H1 means (n = 63) | accuracy 0.95 | 6.3% at α 0.01 · 10.9% at α 0.05 | 0.5% · 2.5% |
| Wilcoxon, H1 | accuracy 0.95 | **82%** at α 0.05 | 2.5% |
| Bootstrap CI, H4 | accuracy 0.95 | coverage 0.90–0.92 | 0.95 |
| Bootstrap CI, H5b | rare clustered abstention | coverage 0.70 (upper bound below truth 30%) | 0.95 (2.5%) |

| Procedure (S1) | Check | Result |
|---|---|---|
| Exact McNemar, H5a | B5 deterministic vs X stochastic; heterogeneous scenarios; correlated methods | false rejections ≤ 0.5% per direction at α 0.05 (conservative) |
| Newcombe CI (n = 63) | six structures incl. correlation | coverage 0.943–0.986 |
| H4 rule at the margin | true difference −0.05 | false support 1.9–2.6% (nominal 2.5%) |
| H5b rule | true scenario rate 0.15 | false support 1.1% |

## Appendix D — external verification of the statistical implementations (S3)

- **Method.** Each implementation compared with an independent implementation in R on a fixed grid: every 2×2 table with N = 1, 2, 3, 5, 12; 400 random tables with N = 63 (seed 20261010); 13 edge cases (all concordant, all discordant, zero cells, ties, extremes); every k = 0…63 of 63 for single proportions; t quantiles for df 1…100. Script `reference/refgrid.R`; values `reference/*.csv`; regression test `tests/test_reference_r.py` (no R needed).
- **Versions.** R 4.3.3 (2024-02-29, Ubuntu 24.04 `r-base-core`); contingencytables 3.1.0 (Fagerland, Lydersen & Laake; installed from the GitHub CRAN mirror because CRAN is blocked in the review container); Epi 2.47.1 (Ubuntu `r-cran-epi`); MASS 7.3-60.0.1; boot 1.3-30; PropCIs 0.3.0 installed but not used.
- **Results.** Newcombe paired (corrected), Agresti–Min, Bonett–Price, McNemar exact and mid-p, Clopper–Pearson, Wilson: max difference ≤ 2e-15; Tango 2.4e-8 (R root tolerance); t quantile ≤ 1e-10.
- **Findings.** (i) `Epi::ci.pd(aa, bb, cc, dd)` treats its arguments as **two independent groups** (p1 = aa/(aa+cc), p2 = bb/(bb+dd)) and implements Newcombe's unpaired method 10; it is **not** a valid reference for the paired interval. (ii) Our earlier Newcombe implementation used an uncorrected correlation term; fixed to the published form.
- **Limitations.** Verification is against one independent implementation, not against the original papers' printed tables (the paper hosts were unreachable). Agreement shows the formulas are implemented as published; it says nothing about calibration in this experiment. The reference packages were installed from a mirror, not CRAN; repeating `refgrid.R` on the intended machine with CRAN packages is optional.
