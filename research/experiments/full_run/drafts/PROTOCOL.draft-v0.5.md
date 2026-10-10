# Full experiment — protocol

**Status: DRAFT v0.5 (2026-10-10) — NOT FROZEN. No full-run LLM call may be made until the owner approves a final version and it is frozen (§10).**
Benchmark v0.2.0 (manifest `27b6ea09…6915`) · B5 v0.1.0 (id `fc9524a4ea38cca5`) · LLM config v1.7 (`../rn_pilot/config.frozen.json`)

Earlier drafts are kept unchanged in `drafts/` (v0.1 `e112437b…`, v0.2 `fefe80e5…`, v0.3 `7bf5dc51…`, v0.4 `697b4380…`).

> **v0.5 note.** The owner did **not** approve S1 (binary endpoints) and asked for an expanded study. Sections 2, 4.2, 5 and 6 below still describe the **unapproved v0.4 proposal** and must not be read as decided. The study, options, original-vs-proposed estimands and freeze blockers are in `DECISION_REPORT_S1_S4.md`. Newcombe's interval was corrected after external verification (S3); H4 would use Tango if option B or C is chosen. Every
hypothesis or test change, with date, rationale, evidence inspected and implications, is in `HYPOTHESIS_CHANGES.md`.
Checks: Appendix A. Changes from v0.3: Appendix B. Statistical assumption analysis: Appendix C.

---

## 0. Decisions

### Closed by the owner (2026-10-10)

| # | Decision |
|---|---|
| D1 | τ_FA = 0.15, maximum acceptable false abstention; H5b Supported only if the 95% upper bound is strictly below 0.15. *(Its unit — node or scenario — depends on S1.)* |
| D2 | δ = 0.05, non-inferiority margin for B-B5 vs B-B4b; Supported only if the 95% lower bound of the paired difference is strictly above −0.05. *(Its endpoint depends on S1.)* |
| D3 | Held-out set (~2 per category) only if built rigorously before the run (§8); otherwise proceed and disclose. |
| D4 | 3 repeats per scenario and LLM call type. |
| D5 | Outage: pause and retry under the same frozen configuration for up to 7 days; otherwise stop. Never mix models; any restart with a changed model or configuration needs an amendment, a new configuration hash and a separate run folder. |
| N1 | H3 removed from the confirmatory family; RQ2 descriptive with N/A for unsupported metrics. |
| N2 | Owner authors the held-out scenarios; a supervisor or qualified second reviewer reviews them independently. No approval assumed until recorded. |
| N3 | Held-out deadline 2026-10-24 (provisional); if not ready, proceed and disclose. |
| N4 | Original draft preserved; changes documented in `HYPOTHESIS_CHANGES.md`. |
| P1 | Sign-flip test approved **on condition** that its assumptions are checked. They were checked and are **not defensible** (Appendix C); see S1. |
| P2 | Freeze only after the runner exists and passes offline tests. Runner built and tested (§9, Appendix A). |
| P3 | Pin exact dependencies; record the real execution environment on the run machine; document the unrecorded pilot environment (§9.4, §11). |

### Awaiting the owner before freezing

| # | Question | Proposal |
|---|---|---|
| **S1** | Replace the withdrawn sign-flip/Wilcoxon/bootstrap verdict machinery with **binary per-scenario endpoints and exact/score methods** (§4.2, §5)? This re-reads D1 as "proportion of scenarios with any false abstention" and D2 as a margin on the "proportion of fully-correct scenarios". | **Yes** (`HYPOTHESIS_CHANGES.md`, change 3). The analysis code already implements it. |
| **S2** | Keep sign-flip and Wilcoxon on node-level means as **descriptive** numbers in the report? | Yes, labelled "not valid for verdicts" (Wilcoxon gave 82% false "B5 better" in simulation). |
| **S3** | Who checks the Newcombe interval against an external reference? This container cannot reach the reference sites. | Owner, on the run machine: R `Epi::ci.pd(20, 12, 2, 16)` should give 0.0618 to 0.3242 (our output); record the result before freezing. |
| **S4** | Environment pins (§9.4): keep the provisional lock generated here (Python 3.13.16) or regenerate on the run machine? | Install the lock on the run machine; if that is impossible, regenerate there, re-run the full test suite and record the change. Fingerprints are taken on the run machine either way. |

---

## 1. Research questions

- **RQ1 (architecture).** Under natural-language input, does *extract → symbolic revision → determinability check* (B5) handle scenarios correctly more often than direct LLM reasoning (B1 regeneration, B2 delta)?
- **RQ2 (attribute awareness), descriptive.** Which methods can represent partial satisfaction and capacity (Cat 5–6), and how accurately do those that can compute attribute values after LLM extraction?
- **RQ3 (knowing when not to answer).** Does B5 fall into false confidence on ambiguous cases less often than B4b, B1 and B2, without over-abstaining?
- **RQ4 (failure attribution), exploratory.** When the pipeline is wrong, is the error caused by extraction or by revision?

## 2. Hypotheses (confirmatory; as proposed under S1)

"B-X" = method X on the shared LLM extraction (Condition B). Unit: scenario.

| ID | Hypothesis | Endpoint (§4.2) | Estimand | Rule |
|---|---|---|---|---|
| H1 | B-B5 handles more scenarios fully correctly than B1 | fully correct, analysis set | difference in proportions B-B5 − B1 | Superiority, predicted > 0 |
| H2 | … than B2 | fully correct, analysis set | B-B5 − B2 | Superiority, predicted > 0 |
| H3 | *Removed (N1); ID reserved.* | — | — | — |
| H4 | B-B5 is not meaningfully worse than B-B4b | fully correct, analysis set | B-B5 − B-B4b | Non-inferiority, δ = 0.05 |
| H5a | B-B5 is falsely confident in fewer ambiguous scenarios than each of B-B4b, B1, B2 | any false confidence, ambiguous subset | B-B5 − X | Superiority, predicted < 0 (three comparisons) |
| H5b | B-B5 does not over-abstain | any false abstention, analysis set | proportion for B-B5 | Upper bound < τ_FA = 0.15 |

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

### 4.2 Confirmatory endpoints (binary per scenario; S1)

Per scenario-repeat:
- **fully correct** = every gold node correct;
- **any false confidence** = at least one ambiguous gold node falsely confident;
- **any false abstention** = at least one determinable gold node falsely abstained.

Per scenario, an indicator is **1 if it holds in at least half of the scenario's common repeats** (2 or 3 of 3, 1 or 2
of 2, the single repeat if only one). The same rule applies to every method.

### 4.3 Descriptive endpoints

Node-level: mean node correctness per method (95% stratified bootstrap CI), pooled false-confidence rate, pooled
false-abstention rate; sign-flip and Wilcoxon on per-scenario mean differences (S2; *not valid for verdicts*,
Appendix C); fully-correct counts per category; missing predictions; cost; extraction quality.
**RQ2:** Cat 5 / 6-A / 6-B evaluator metrics (attribute accuracy by type, partial-satisfaction preservation,
binarisation error, state-change precision/recall, direction correctness, aggregate/shortfall/per-dimension accuracy,
feasibility classification, compensation reasoning, feasible/optimal combination, search cost; label-level affected
precision/recall, over-flip, inertia). Mean over the scenarios where computed, with the number of scenarios.
**N/A**, never zero, for a method that does not output the dimension (B3 and B4a for every attribute metric; B5 for
search cost). No p-values, no verdicts.

## 5. Statistical analysis plan (S1)

Code: `reflica_bench/stats.py` (standard library only), `experiments/full_run/analysis.py`. Tests: `tests/test_stats.py`, `tests/test_analysis_units.py`, `tests/test_full_run.py`.

- **Pairing.** Every method is scored on the same analysis set and the same common repeats (§7). For each comparison: a = both 1, b = B-B5 only, c = comparator only, d = neither; estimate = (b − c) / n.
- **Tests (H1, H2, H5a ×3).** Two-sided **exact McNemar** test: conditional on the k = b + c discordant scenarios, b ~ Binomial(k, ½) under H0. Implemented as the exact sign-flip enumeration on d_s ∈ {−1, 0, 1} (identical to the binomial test). Concordant scenarios carry no information about the difference and are not used by the test.
- **Null hypothesis and its assumption.** H0: in every scenario, both methods have the same probability of the indicator being 1. Then P(d_s = 1) = P(d_s = −1), so d_s is exactly symmetric, with no further assumption about error structure, correlation between methods or variation between scenarios. Scenarios must be independent (separate calls; separate extractions). If probabilities differ between scenarios but are equal within each, the test is exact or conservative.
- **Numerics.** Differences are rounded to 12 decimals before use and scaled to integers at 1e-9; sums equal within k units of rounding count as ties. For binary d_s the distribution has k + 1 points, so the computation is always exact (no Monte Carlo).
- **Confidence intervals.** Paired differences (H1, H2, H4, H5a): **Newcombe (1998) method 10** hybrid score interval, no continuity correction; φ = (ad − bc)/√((a+b)(c+d)(a+c)(b+d)), set to 0 when the denominator is 0; Wilson score limits at z = 1.959964 (found by bisection on erf). H5b: exact **Clopper–Pearson** interval by bisection on the exact binomial CDF (200 iterations). CIs are not multiplicity-adjusted.
- **Multiplicity.** Holm–Bonferroni over exactly **5 tests**: H1, H2, H5a-vs-B4b, H5a-vs-B1, H5a-vs-B2; familywise α = 0.05. H4 and H5b are CI rules outside the family.
- **Power notes (fixed before data).** The smallest attainable two-sided p with k discordant scenarios is 2/2^k; with 5 Holm tests the first must be < 0.01, which needs k ≥ 8 all in one direction. H5a has at most 11 scenarios. H5b can be Supported only if at most **3 of 63** scenarios show a false abstention. In simulation, power for H5a was 0.87 (α 0.05) / 0.43 (α 0.01) for a large effect and 0.33 / 0.08 for a moderate one (Appendix C).
- **Per-category results.** Descriptive only.

## 6. Verdict rules (all inequalities strict)

| Verdict | Superiority (H1, H2, each H5a comparison) | Non-inferiority (H4) | Threshold (H5b) |
|---|---|---|---|
| **Supported** | Holm-adjusted p < 0.05, **and** Newcombe CI entirely on the predicted side of 0, **and** b − c on the predicted side | CI lower bound > −0.05 | Clopper–Pearson upper bound < 0.15 |
| **Contradicted** | Holm-adjusted p < 0.05, **and** CI entirely on the opposite side, **and** b − c on the opposite side | CI upper bound < −0.05 | lower bound > 0.15 |
| **Inconclusive** | anything else | anything else | anything else |

The exact test and the score interval are different procedures; at the margin one can exclude 0 while the other does
not. That gives Inconclusive, flagged *discordant*, never Supported. **Composites:** H5a overall = Supported iff all
three comparisons are Supported, Contradicted iff any is Contradicted, else Inconclusive; H5 overall = the same over
{H5a overall, H5b}. Each verdict is reported with the 2×2 table, estimate, CI, exact and Holm p.

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
rule did not trigger. `analysis.py` runs only on a folder that passes complete validation, and writes `results.json`.

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

**Freeze checklist** (in order; none done yet): (1) owner closes S1–S4; (2) held-out set complete and reviewed, or
deadline passed and omitted; (3) on the run machine: install the lock, `env-check` passes, full test suite passes;
(4) owner's explicit written approval of the final text; (5) copy it to `PROTOCOL.v1.0.md` with status FROZEN, mark
`PROTOCOL.md` SUPERSEDED, write `protocol_lock.json` with `fingerprints()` taken on the run machine.

After freezing, tests fail if a listed file is edited or deleted, its status is not FROZEN, or `PROTOCOL.md` is not
SUPERSEDED. **Amendments stay possible:** a new `PROTOCOL.v1.N.md`, a new lock entry chained by `supersedes` with fresh
fingerprints, and an `AMENDMENTS.md` entry with both hashes, date, reason and expected effect; the gate then checks the
new version. Each run folder's gate record names the version it ran under; an amendment made after a run started
applies only to a new run folder. During the run: no protocol change, no look at aggregated results before validation
passes, deviations to `DEVIATIONS.md` before analysis, every hypothesis reported whatever the verdict.

## 11. Known limitations (reported in the thesis)

- B5 was designed with the 63 scenarios visible; the held-out set addresses this only if built.
- H3 withdrawn after Condition A sanity results; the confirmatory test changed after simulation (`HYPOTHESIS_CHANGES.md`). No experimental data existed at any change.
- Binary endpoints ignore partial credit and lose power; H5a rests on ≤ 11 scenarios and needs ≥ 8 one-directional discordant scenarios.
- Newcombe method 10 is verified here by formula properties and simulated coverage, not yet against an external reference (S3).
- Pilot environment not recorded; pilot not claimed fully reproducible (§9.4). The experiment environment is provisional until confirmed on the run machine.
- Pilot scripts are ungated (§9.5).
- One model, one provider (free tier); temperature 0 not guaranteed deterministic; synthetic template-rendered language.

---

## Appendix A — checks performed (2026-10-10, no model or API calls)

| # | Check | Result |
|---|---|---|
| 1 | `node_counts` vs `evaluate_category_7`, 63 scenarios × 4 methods, gold input | 145 cross-checks, 0 mismatches |
| 2 | Condition A | primary B3 0.885 · B4a 0.904 · B4b 0.952 · B5 1.000; Cat 5–6 labels 107/107 for all |
| 3 | Statistical assumptions | Appendix C |
| 4 | McNemar / sign-flip, Clopper–Pearson, Wilson, Newcombe | exact against brute force and closed forms; CP defining equations; Newcombe property (correlation narrows/widens) and coverage; Armitage & Berry (20, 12, 2, 16): difference 0.200, Newcombe-10 (0.0618, 0.3242), exact McNemar p = 0.0129 |
| 5 | Existing records vs disk; renders | all match; 0 leakage problems |
| 6 | Freeze, amendment, gate | as v0.3, plus environment lock, record-only fields, runner-after-freeze, gate record |
| 7 | Runner, offline (network blocked in tests; replay of the 144 real pilot responses + gold-based answers) | full gate before every request; draft blocks everything; mid-run gate failure stops before the request; wrong provider / missing key / served-model mismatch / ABORT fatal; pause after 5 infrastructure failures, D5 stop after 7 days; seeded plan order; one re-run max; private, chained, redacted log; validation catches edits, a missing gate record and incomplete runs; analysis refuses invalid folders; scoring and analysis end to end, deterministic |
| 8 | Mutation checks | 17 deliberate bugs in runner, analysis, gate and statistics; all caught (4 gaps found and closed) |
| 9 | Environment | this container matches `requirements-experiment.lock` |
| 10 | Full test suite | **275 passed** |

## Appendix B — changes from v0.3

P1–P3 recorded · sign-flip withdrawn after assumption check · S1 binary endpoints, exact McNemar, Newcombe, Clopper–Pearson
proposed and implemented · S2–S4 opened · runner, validation, scoring and analysis implemented and tested offline ·
environment lock and gate check · pilot-environment limitation documented · freeze checklist · v0.3 archived.

## Appendix C — statistical assumption analysis (offline simulation, seeds fixed; scripts in `simulations/`)

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
