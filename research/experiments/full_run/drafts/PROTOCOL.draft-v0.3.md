# Full experiment — protocol

**Status: DRAFT v0.3 (2026-10-10) — NOT FROZEN. No full-run LLM call may be made until the owner approves a final version and it is frozen (§10).**
Benchmark v0.2.0 (manifest `27b6ea09…6915`) · B5 v0.1.0 (id `fc9524a4ea38cca5`) · LLM config v1.7 (`../rn_pilot/config.frozen.json`)

Earlier drafts are kept unchanged in `drafts/`. Hypothesis changes, with date, rationale, evidence inspected and
implications, are in `HYPOTHESIS_CHANGES.md`. Checks are in Appendix A, changes from v0.2 in Appendix B.

---

## 0. Decisions

### Closed by the owner (2026-10-10)

| # | Decision |
|---|---|
| D1 | τ_FA = 0.15 is the maximum acceptable **false-abstention rate on determinable gold nodes**. H5b is Supported only if the upper bound of its 95% CI is **strictly below** 0.15. |
| D2 | δ = 0.05 is the **non-inferiority margin** for B-B5 vs B-B4b on the primary endpoint. H4 is Supported only if the lower bound of the 95% CI of the paired difference is **strictly above** −0.05. |
| D3 | A held-out set (~2 per category) is added only if it can be built rigorously before the run (§8). Otherwise the main run proceeds and the limitation is disclosed. |
| D4 | **3 repeats** per scenario and LLM call type, under the frozen budget and failure rules (§7). |
| D5 | On a model outage: pause and retry under the **same frozen configuration** for up to 7 days. If the same served model and configuration cannot be restored, **stop**. Never mix models. A restart with another model or setting needs a documented amendment, a new configuration hash and a separate run folder. |
| N1 | **H3 removed from the confirmatory family.** RQ2 is descriptive, with attribute-value metrics; unsupported metrics are N/A (§4.3). |
| N2 | The **owner authors** the held-out scenarios. A **supervisor or qualified second reviewer independently reviews** the scenarios and gold labels (§8). No approval is assumed until it is recorded. |
| N3 | Held-out deadline **2026-10-24 (provisional)**. If the set is not ready, proceed without it and disclose. |
| N4 | The original draft is preserved (`drafts/PROTOCOL.draft-v0.1.md`) and the change is documented (`HYPOTHESIS_CHANGES.md`, change 1). |

### Proposed in v0.3, awaiting the owner

| # | Proposal | Why |
|---|---|---|
| P1 | Confirmatory test = **paired sign-flip test on Σ d** (§5); Wilcoxon becomes a sensitivity analysis. | Makes each test's statistic the numerator of the estimand its CI describes (review point 1). `HYPOTHESIS_CHANGES.md`, change 2. |
| P2 | **Freeze only after the full-run runner is written and dry-tested without API calls**, so its code is in the lock. | The gate fingerprints every `.py` under `full_run/`; a runner written after freezing blocks the gate until an amendment (§9). |
| P3 | **Pin the run environment**: exact Python and package versions (at least pydantic, pydantic-core, ortools, networkx, protobuf, numpy) in a lock file, and take the freeze fingerprints on the machine that will run the experiment. | `ortools` (used by B4b) is unpinned (`>=9.9`), and the pilot did not record package versions (§11). The gate checks these versions exactly. |

---

## 1. Research questions

- **RQ1 (architecture).** Under natural-language input, does *extract → symbolic revision → determinability check* (B5) revise a plan more correctly than direct LLM reasoning (B1 regeneration, B2 delta)?
- **RQ2 (attribute awareness), descriptive.** Which methods can represent partial satisfaction and capacity constraints (Cat 5–6), and how accurately do those that can compute attribute values after LLM extraction?
- **RQ3 (knowing when not to answer).** Does B5's determinability stage reduce false confidence on ambiguous nodes compared with B4b, B1 and B2, without excessive abstention?
- **RQ4 (failure attribution), exploratory.** When the pipeline is wrong, is the error caused by extraction or by revision?

## 2. Hypotheses (confirmatory)

"B-X" = method X on the shared LLM extraction (Condition B). Unit: scenario. Estimands and tests: §5.

| ID | Hypothesis | Endpoint (§4) | Estimand | Rule |
|---|---|---|---|---|
| H1 | B-B5 is more correct than B1 | Primary, analysis set | mean paired difference B-B5 − B1 | Superiority, predicted > 0 |
| H2 | B-B5 is more correct than B2 | Primary, analysis set | mean paired difference B-B5 − B2 | Superiority, predicted > 0 |
| H3 | *Removed (N1). ID reserved; see `HYPOTHESIS_CHANGES.md` and RQ2.* | — | — | — |
| H4 | B-B5 is not meaningfully worse than B-B4b | Primary, analysis set | mean paired difference B-B5 − B-B4b | Non-inferiority, δ = 0.05 |
| H5a | B-B5 is less often falsely confident than each of B-B4b, B1, B2 (three comparisons) | False confidence, ambiguous-node subset | pooled-rate difference B-B5 − X | Superiority, predicted < 0 |
| H5b | B-B5 does not over-abstain | False abstention, analysis set | pooled rate of B-B5 | Below τ_FA = 0.15 |

Against B4b, B5's distinctive claim is H5a; on gold input B4b already matches gold on Cat 5–6.

## 3. Conditions and methods

| Condition | Input | Methods | Role |
|---|---|---|---|
| **B (main)** | plan_text + change_text → shared extractor (one call per scenario per repeat) → identical structured input to every symbolic method | B3, B4a, B4b, **B5** | Confirmatory for B4b and B5; B3 and B4a descriptive |
| **Direct LLM** | plan_text + change_text | B1 full regeneration, B2 delta | Confirmatory comparators (H1, H2, H5a) |
| **A (sanity)** | gold structured input, no LLM | B3, B4a, B4b, B5 | Descriptive only; never evidence of extraction accuracy |
| **B6 oracle scope** | canonical input | evaluator-side | Diagnostic upper bound only |

Fixed for every call (config v1.7): model `nvidia/nemotron-3-ultra-550b-a55b`, temperature 0, seed 20261008, thinking
on, max 16,384 output tokens, prompts `b1_full_regeneration.v1.1`, `b2_delta.v1.1`, `extractor.v1.1`,
`common_reasons`, schemas `extractor_output.schema.v1.4`, `revision_output.schema.v1`. The served-model id must equal
the config id or the call aborts. Output parsing and label mapping follow the pilot's approved rules (`from_direct`,
`_remap` in `../rn_pilot/pilot.py`, fingerprinted): exact match, then case/space-insensitive; unmapped labels are
counted, never guessed.

Budget: 63 × 3 × {B1, B2, EXTRACT} = **567 calls**, + 126 if the 14-scenario held-out set exists (**693**). Retries
under §7 are logged and are not extra budget.

## 4. Metrics

Node-level quantities come from `reflica_bench/endpoints.py::node_counts`, built only from the evaluator's primitives
`_abstained` and `_node_correct`. It reproduces the evaluator's Cat 7 rates exactly (Appendix A, check 1).

### 4.1 Node classification (per scenario-repeat)

For each gold node in `ground_truth.nodes`:
- **abstained** = determinability AMBIGUOUS, or label UNCERTAIN or REQUIRES_REEVALUATION;
- **AMBIGUOUS gold node** → *correct* if abstained, else *falsely confident*;
- **determinable gold node** → *falsely abstained* if abstained; else *correct* if `_node_correct` (label equals gold and, if the method outputs attribute values, every gold attribute matches: numbers within absolute 1e-3, other values exactly; extra attributes not penalised), else *committed-wrong*.

Each node is in exactly one class. Applied identically to every method:
- **Failed output** (unparseable, schema-invalid, truncated, extraction failure, solver failure): no node correct; ambiguous nodes falsely confident, determinable nodes committed-wrong.
- **Missing node**: committed and wrong (evaluator semantics); also counted as a *missing prediction*.
- **No attribute output** (B3, B4a): labels only; these methods are in no confirmatory hypothesis.
- **No determinability output** (B3 always; B4a and B4b on 22 scenarios under gold input): abstention only via an abstention label.

### 4.2 Confirmatory endpoints

- **Primary** (per scenario-repeat) = correct nodes / gold nodes; per scenario = mean over its common repeats (§7).
- **False confidence**: count per scenario = falsely confident nodes (mean over common repeats); pooled rate = Σ count / Σ ambiguous gold nodes. Reported first in every Cat 7 table, never averaged with anything.
- **False abstention**: count per scenario = falsely abstained nodes (mean over common repeats); pooled rate = Σ count / Σ determinable gold nodes.

### 4.3 RQ2 — descriptive Cat 5–6 attribute metrics

Computed with the evaluator's own functions on Condition B (and Condition A for reference) for B1, B2, B3, B4a, B4b, B5:

| Sub-category | Metrics |
|---|---|
| Cat 5 (12) | attribute accuracy by type, partial-satisfaction preservation, binarisation error, state-change precision/recall, direction correctness, depth-stratified attribute accuracy |
| Cat 6-A (9) | aggregate value accuracy, shortfall/excess accuracy, per-dimension accuracy, feasibility classification, compensation reasoning, direction correctness |
| Cat 6-B (4) | feasible-combination precision/recall, optimal-combination accuracy, compensation reasoning, combinatorial search cost |
| All | affected-node precision/recall, over-flip, inertia (label-level; every method) |

**N/A rules.** (a) A method that does not output the needed dimension gets **N/A**, never zero: B3 and B4a for every
attribute metric; B5 for combinatorial search cost. (b) A metric that does not apply to a scenario is skipped for that
scenario. Each cell reports the number of scenarios it is computed on. Aggregation: mean over those scenarios, with a
95% bootstrap CI (§5). The B-B5 − B-B4b difference is shown with its CI and **no p-value**; nothing in §4.3 produces a verdict.
A capability table (which method outputs which dimension) is reported as a design property, not a statistical result.

### 4.4 Other secondary metrics

All other evaluator metrics, missing-prediction counts, cost (tokens, latency, calls) and extraction quality (as in the
pilot), descriptive only.

## 5. Statistical analysis plan

Code: `reflica_bench/stats.py` (standard library only). Tests: `tests/test_stats.py`.

- **Unit and aggregation.** The scenario; a scenario's value is the mean over its common repeats (§7). Counts are averaged over common repeats, then summed over scenarios for pooled rates.
- **Pairing.** All methods use the same analysis set and repeats; in Condition B every symbolic method gets the identical extraction of a repeat.
- **Estimands.**
  - H1, H2, H4: mean over scenarios of d_s = primary(B-B5, s) − primary(X, s) = Σ d_s / n.
  - H5a: pooled-rate difference = Σ_s d_s / Σ_s amb_s, with d_s = fc(B-B5, s) − fc(X, s) over the **ambiguous-node subset** (analysis-set scenarios with ≥ 1 AMBIGUOUS gold node; 11 Cat 7 scenarios if none is excluded). The subset is fixed by gold labels, not by results.
  - H5b: pooled false-abstention rate of B-B5 over the analysis set.
- **Confidence intervals.** 95% percentile bootstrap; scenarios resampled with replacement **within category** (Cat 6-A and 6-B together), keeping category sizes; 10,000 resamples; type-7 quantiles; a fresh generator seeded 20261010 for every CI. Ratio estimands are recomputed as ratio of sums in each resample. Not multiplicity-adjusted.
- **Tests (P1).** Two-sided paired **sign-flip test** with statistic Σ d_s over the same d_s that define the estimand. H0: each d_s is symmetric about 0. Because n (H1, H2) and Σ amb_s (H5a) do not change under sign flips, the test is about exactly the estimand's numerator. Zero differences are dropped; differences are rounded to 12 decimals. p = P(|S*| ≥ |S_obs|), **exact** by enumeration when ≤ 20 differences are non-zero (always the case for H5a), otherwise Monte Carlo with 200,000 sign vectors from seed 20261010 and p = (1 + hits)/(1 + 200,000).
- **Multiplicity.** Holm–Bonferroni over exactly **5 tests**: H1, H2, H5a-vs-B4b, H5a-vs-B1, H5a-vs-B2; familywise α = 0.05. H4 and H5b are CI rules, outside the family. Everything else is descriptive.
- **Power note (fixed before data).** H5a rests on ≤ 11 scenarios. With 5 Holm tests the smallest p must be < 0.01; with equal-size differences that needs **≥ 8 non-zero differences all in one direction** (7 give p = 0.0156). An Inconclusive H5a is reported as such, not as evidence of no difference.
- **Per-category results.** Descriptive only (n = 4–16).
- **Repeatability.** Agreement of outputs across the 3 repeats, per call type.
- **Sensitivity analyses (reported, never change a verdict).** (i) Wilcoxon signed-rank (exact, `stats.wilcoxon_signed_rank`) on the same d_s; (ii) equal weight per category; (iii) available-case repeats instead of common repeats.

## 6. Verdict rules (applied automatically; all inequalities strict)

| Verdict | Superiority (H1, H2, each H5a comparison) | Non-inferiority (H4) | Threshold (H5b) |
|---|---|---|---|
| **Supported** | Holm-adjusted p < 0.05, **and** CI entirely on the predicted side of 0, **and** Σ d_s on the predicted side | CI lower bound > −0.05 | CI upper bound < 0.15 |
| **Contradicted** | Holm-adjusted p < 0.05, **and** CI entirely on the opposite side, **and** Σ d_s on the opposite side | CI upper bound < −0.05 | CI lower bound > 0.15 |
| **Inconclusive** | anything else (including all-zero differences, p = 1) | anything else | anything else |

**Test–CI consistency.** Test and CI now concern the same estimand, and the CI's point estimate has the same sign as
Σ d_s by construction. They remain different procedures (randomisation test vs bootstrap), so near the boundary one can
exclude 0 while the other does not. That yields Inconclusive, flagged *discordant*; it can never yield Supported.

**Composites.** H5a overall: Supported iff all three comparisons are Supported; Contradicted iff any is Contradicted;
else Inconclusive. H5 overall: same rule over {H5a overall, H5b}.

Each verdict is reported with estimate, 95% CI, raw and Holm-adjusted p, Σ d_s, number of non-zero differences, and the
Wilcoxon sensitivity result.

## 7. Eligibility, failures and missing data

Code: `stats.analysis_set`. Each call has one status: **ok**, **model failure** (scored per §4.1) or **infrastructure missing** (a call never made counts as infrastructure missing).

1. **Status inheritance.** B1 and B2 have their own calls. All four Condition B methods take the status of the EXTRACT call of the same scenario and repeat. Condition A and B6 have no calls and no missingness.
2. **Common repeat.** Repeat r is common to scenario s iff none of B1 r, B2 r, EXTRACT r is infrastructure missing.
3. **Analysis set.** Scenarios with ≥ 1 common repeat. Every method and every confirmatory comparison uses **this one set and these repeats**; no comparison-specific eligibility. H5a uses the analysis-set scenarios with ≥ 1 AMBIGUOUS gold node.
4. **Model failures are never missing.** They are scored, so they never remove a scenario or a repeat.
5. **Excluded scenarios** (0 common repeats) are excluded for every method and listed by id with their category.
6. **Stop rule.** If more than 5% of planned calls are infrastructure missing after the retry policy, stop and report before any analysis. The held-out set has its own analysis set and stop rule.
7. **Missingness report** (always published): per call type × category, and per method × condition (by inheritance): ok, model failures, infrastructure missing, repeats used, excluded scenario ids; plus missing-prediction node counts per method.

| Event | Handling |
|---|---|
| API / infrastructure failure (HTTP 5xx, 429 after retries, timeout) | Retry with backoff as in the pilot; then one re-run later. Originals kept in a failures log. Still failing → infrastructure missing. |
| Model unavailable | D5. Never switch model or settings mid-run. |
| Genuine model failure (non-JSON, schema-invalid, truncated, unmapped labels, invented content) | Scored per §4.1; never excluded. |
| Extraction failure | Failed output for every Condition B method in that repeat; classified for RQ4. |
| Solver failure on a valid extraction | Failed output for that method only; reported. |

## 8. Held-out set

**Status: NOT CREATED. No held-out scenario, gold label or review exists. The set must not be described as ready until §8.3–8.4 are complete and recorded.**

**8.1 People.** Author: the owner. Reviewer: a supervisor or qualified second reviewer who did not write B5. They review
the scenarios and gold labels independently and record their sign-off (name, date, scenarios reviewed, issues found and
how they were resolved) in `heldout/REVIEW.md`. The agent sessions that built B5 do not write, review or see held-out
scenarios before they are frozen.

**8.2 Construction.** Cat 1–5: two each; Cat 6: one C6-A and one C6-B; Cat 7: two, each with ≥ 1 AMBIGUOUS gold node
(14 total). Written from the category definitions and scenario schema only, not from B5's code or report. New domains
and names; no edited copies of the 63. Structural near-duplicate check (scripted): no held-out scenario may match a
canonical one on node count, edge-type multiset and rule formulas together.

**8.3 Gold validation.** Hand-written gold labels must agree with the independent exact generator `gt_engine.py` on
every node's label, values and determinability, and pass the linter and the R-N leakage checker. The author resolves
disagreements with a written note; a scenario `gt_engine` cannot express is dropped, not hand-patched. Before freezing,
only evaluator-side tools (`gt_engine`, linter, renderer, leakage checker) may run on held-out scenarios; no compared
method (B1–B5) and no LLM.

**8.4 Freezing and leakage.** The held-out files get their own SHA-256 manifest (benchmark v0.2.0 is not changed). Its
hash goes into the protocol lock (`heldout_manifest_sha256`) before any call. B5 stays at v0.1.0; any B5 change after
held-out results are seen invalidates the held-out evaluation.

**8.5 Timing.** The held-out manifest and review must be complete before the main run starts and by **2026-10-24
(provisional)**. Otherwise the protocol is frozen without a held-out set and the limitation is disclosed. A set built
after main results exist is post-hoc and exploratory.

**8.6 Analysis and claims.** Same calls, settings, repeats, endpoints and statistics, analysed **separately** (never
pooled with the 63). A pre-registered **replication**, outside the confirmatory family: estimates and 95% CIs, p-values
unadjusted and descriptive, no verdicts. Per hypothesis: *consistent* (estimate on the same side as the main result and
CI not entirely on the opposite side) or *not consistent*. Supported claim: "the direction of the main result holds on
14 unseen scenarios", nothing stronger.

## 9. Fingerprints, the pre-call gate and entry points

Code: `reflica_bench/protocol_lock.py`. Tests: `tests/test_protocol_lock.py`.

**Fingerprinted** (`fingerprints()`), all compared exactly by the gate unless marked:

| Group | Contents |
|---|---|
| Protocol | sha256 of the frozen protocol file |
| Benchmark | manifest sha256; every scenario file via `rn.verify_manifest` |
| Rendered inputs | sha256 of the deterministic renders of all 63 (texts + alias maps), render version |
| B5 | file hashes and version id (recomputed: first 16 hex of sha256 of the sorted file→hash JSON) |
| LLM configuration | config v1.7 sha256; every prompt and schema; client `_api.py` |
| Code | analysis (evaluator, endpoints, stats, schema, loader, adapters, baseline, extraction schema, protocol_lock); runtime (rn, linter, gt_engine, groundtruth, groundtruth_quant); all baselines; pilot code reused by the runner (`_api.py`, `repeatability.py`, `pilot.py`); **every `.py` under `full_run/`** |
| Environment | Python version and implementation; exact versions of pydantic, pydantic-core, ortools, networkx, protobuf, numpy |
| Record only | sha256 of the full installed-package list (recorded, not compared) |
| Held-out | manifest sha256, if the set exists |

`record_problems()` checks the existing records against disk (benchmark manifest, `b5/FROZEN.json`, config v1.7
prompts, schemas, client, extraction schema, render leakage).

**Gate.** `write_gate_record(run_dir)` runs `assert_ready_for_llm_calls()`. That raises unless a frozen lock exists, the
lock is valid, there are no record problems and every compared fingerprint equals the **active** (latest) lock entry.
It then writes `run_dir/gate.json`, once per run folder.

**Entry points.**
- The full-run runner (task 2, not yet written) must call `write_gate_record` before any network use. A test fails for any `.py` under `full_run/` that can reach a model without calling the gate first.
- The analysis must call `check_gate_record(run_dir)` and refuse a run folder without a valid gate record. So data from an ungated run cannot be analysed even if someone bypasses the runner.
- The existing pilot scripts (`pilot.py run`, `repeatability.py`, `list_models.py`, `gemini_models.py`) make API calls without this gate. They predate the protocol and are fingerprinted as they are, so they are not modified. A test keeps them unable to address the full run (no reference to `full_run`, no iteration over the 63 canonical files), and any edit to them changes `pilot_code` and blocks the gate.

## 10. Freezing and amendments

- **Draft (now):** no `protocol_lock.json`; `PROTOCOL.md` says DRAFT and NOT FROZEN (test-enforced); the gate refuses every call.
- **Freeze** (only after the owner's explicit written approval, and after P2/P3 if accepted): copy the approved text to `PROTOCOL.v1.0.md` with status FROZEN; mark `PROTOCOL.md` SUPERSEDED; write `protocol_lock.json` with version, file, sha256, date, approver and the full `fingerprints()` output taken on the run machine.
- **After freezing**, a test fails if a listed file is edited or deleted, if its status is not FROZEN, or if `PROTOCOL.md` is not marked SUPERSEDED.
- **Amendment** (still possible after freezing): new file `PROTOCOL.v1.N.md`; new lock entry whose `supersedes` is the previous hash, with fresh fingerprints; an `AMENDMENTS.md` entry with both hashes, the date, reason and expected effect. Earlier files are never edited. The gate then checks against the new version. Each run folder's gate record names the version it ran under, so amendments made after a run started apply only to a new, separate run.
- During the run: no change to protocol, prompts, schemas, metrics or verdict rules; no look at aggregated results before the completeness check passes; deviations go to `DEVIATIONS.md` before analysis. All hypotheses are reported whatever the verdict.

## 11. Known limitations (reported in the thesis)

- B5 was designed with the 63 scenarios visible; gold-input agreement is expected. The held-out set (§8) partly addresses this only if it is built.
- H3 was withdrawn after Condition A sanity results (`HYPOTHESIS_CHANGES.md`); no confirmatory data existed.
- H5a rests on 11 scenarios and 19 ambiguous nodes; limited power (§5).
- B3 and B4a cannot output attribute values; their correctness is label-only and they are in no confirmatory test.
- The pilot did not record package versions, and `ortools` is unpinned (`>=9.9`). The pilot ran on Python 3.14.3; this review ran on Python 3.13.16 (pydantic 2.14.0, ortools 9.15.6755), where all 247 tests pass, but pilot results are not guaranteed to reproduce bit-for-bit under other versions (P3).
- The pilot scripts can make API calls without the gate. They are limited to the pilot by test and by fingerprint, but not by the gate itself.
- One primary LLM, one provider (free tier); replication model not available. Temperature 0 is not guaranteed deterministic on this endpoint.
- Synthetic, template-rendered language; real user text may be harder.

---

## Appendix A — checks performed (2026-10-10, no model or API calls)

| # | Check | Result |
|---|---|---|
| 1 | `node_counts` vs `evaluate_category_7`, 63 scenarios × B3/B4a/B4b/B5 on gold input | 145 cross-checks, **0 mismatches**; four-way node partition holds on all 252 runs |
| 2 | Condition A summary (230 nodes, 19 ambiguous) | primary B3 0.885, B4a 0.904, B4b 0.952, B5 1.000; falsely confident 19/15/11/0; falsely abstained 0/2/0/0; Cat 5–6 labels 107/107 for all |
| 3 | Cat 5–6 metric support on gold input | attribute metrics computed for B4b and B5, N/A for B3 and B4a; search cost B4b only; some metrics N/A on individual scenarios for every method (not applicable) |
| 4 | Ambiguous-node scenarios | 11, all Cat 7; nodes per scenario 1,1,1,1,1,1,2,2,2,3,4 |
| 5 | Pilot scorer on failed outputs | status only, no metrics → rule in §4.1, implemented as `node_counts(None, …)` |
| 6 | Sign-flip test | equals brute-force enumeration on 200 random cases incl. ties, zeros and thirds; Monte Carlo within 0.01 of exact and reproducible; statistic equals the H5a numerator; p invariant to scaling. A rounding bug (1/3 + 1/3 + 1/3 ≠ 1 after scaling) was found by this check and fixed |
| 7 | Wilcoxon (sensitivity) | equals brute force (200 cases) and scipy exact (50 cases) |
| 8 | Bootstrap, quantiles, Holm, verdict boundaries, common-repeat rule, per-category missingness | unit-tested, incl. strict boundaries (−0.05, 0.15, α) |
| 9 | Existing records vs disk | benchmark manifest, B5 files and id, config v1.7 prompts, schemas, client, extraction schema: **all match** |
| 10 | Renders of all 63 | leakage checker: 0 problems |
| 11 | Freeze, amendment and gate | edit / deletion / wrong status / draft not SUPERSEDED / undocumented amendment / broken chain / file reuse all fail; documented amendment passes and becomes the gated version; gate refuses in draft and on any tampered compared fingerprint (10 groups tested); record-only fields ignored; a runner added after freezing blocks the gate; gate record written once, refused if missing, unknown or tampered |
| 12 | Entry points | an ungated script placed under `full_run/` makes the entry-point test fail; pilot scripts do not reference the full run |
| 13 | Mutation checks | 14 deliberate bugs across endpoints, stats and protocol_lock; every one makes a test fail (one gap found and closed: gate-record fingerprint tampering) |
| 14 | Full test suite | **247 passed** (203 existing + 44 new) |

## Appendix B — changes from v0.2

N1–N4 closed and recorded · H3 removed (ID reserved), Holm family 5 tests · RQ2 descriptive metrics and N/A rules (§4.3) ·
P1 sign-flip test as the confirmatory test, Wilcoxon as sensitivity · test–CI consistency restated (§6) · eligibility
rules numbered, status inheritance, per-category and per-method missingness (§7) · held-out status NOT CREATED, reviewer
sign-off record, provisional deadline (§8) · fingerprints extended to baselines, runtime and pilot code, any `full_run`
runner, environment; record-only field (§9) · gate record per run folder, analysis-side check, entry-point test (§9) ·
draft must be SUPERSEDED after freezing (§10) · P2 freeze-after-runner and P3 environment pinning proposed · limitations
updated (§11) · drafts v0.1 and v0.2 archived in `drafts/`; `HYPOTHESIS_CHANGES.md` added.
