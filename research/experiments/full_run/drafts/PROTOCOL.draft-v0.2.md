# Full experiment — protocol

**Status: DRAFT v0.2 (2026-10-10) — NOT FROZEN. No full-run LLM call may be made until the owner approves a final version and it is frozen (§10).**
Benchmark v0.2.0 (manifest `27b6ea09…6915`) · B5 v0.1.0 (id `fc9524a4ea38cca5`) · LLM config v1.7 (`../rn_pilot/config.frozen.json`)

Changes from v0.1 are listed in Appendix B. The checks behind them are in Appendix A.

---

## 0. Decisions

### Closed by the owner (2026-10-10)

| # | Decision |
|---|---|
| D1 | τ_FA = 0.15 is the maximum acceptable **false-abstention rate on determinable gold nodes**. H5b is Supported only if the upper bound of its 95% CI is **strictly below** 0.15. |
| D2 | δ = 0.05 is the **non-inferiority margin** for B-B5 vs B-B4b on the primary endpoint. H4 is Supported only if the lower bound of the 95% CI of the paired difference is **strictly above** −0.05. |
| D3 | A held-out set (~2 scenarios per category) is added **if it can be built rigorously before the run** (§8). If not, the main run goes ahead and the limitation is reported. |
| D4 | **3 repeats** per scenario and LLM call type, under the frozen budget and failure rules (§7). |
| D5 | On a model outage: pause and retry under the **same frozen configuration** for up to 7 days. If the same served model and configuration cannot be restored, **stop**. Models are never mixed. Any restart with another model or setting needs a documented amendment, a new configuration hash and a separate run folder. |

### Still open (owner must close before freezing)

| # | Question | Proposal |
|---|---|---|
| N1 | **H3 cannot test what it claims** (Appendix A, check 2): on gold input B3 and B4a already get **107/107** Cat 5–6 outcome labels right, the same as B5. Their Cat 5–6 weakness is in attribute values and partial status, which they do not output at all (`attribute_values` is None on all 63), so the evaluator scores those metrics N/A for them. | **Withdraw H3 from the confirmatory family.** Answer RQ2 descriptively: a capability table (which methods can represent partial satisfaction and capacity) plus Cat 5–6 attribute metrics for B4b and B5 with CIs. H3's ID stays reserved so the numbering shows the change. |
| N2 | Who writes and who validates the held-out scenarios (§8.1)? | The owner writes them; a second person (e.g. the guide or a lab peer) reviews them. The agent sessions that built B5 do not write them. |
| N3 | Held-out deadline (§8.5). | Held-out manifest frozen by **2026-10-24**, otherwise proceed without it. |
| N4 | Disclosure: the v0.2 hypothesis changes (N1) were made after seeing **Condition A (gold-input) sanity results** for B3, B4a, B4b and B5. No Condition B or LLM full-run data exist. | Keep this sentence in the frozen protocol and the thesis. |

---

## 1. Research questions

- **RQ1 (architecture).** Under natural-language input, does *extract → symbolic revision → determinability check* (B5) revise a plan more correctly than direct LLM reasoning (B1 regeneration, B2 delta)?
- **RQ2 (attribute awareness), descriptive.** Which methods can represent partial satisfaction and capacity constraints (Cat 5–6), and how accurately do those that can (B4b, B5) compute attribute values after LLM extraction?
- **RQ3 (knowing when not to answer).** Does B5's determinability stage reduce false confidence on ambiguous nodes compared with B4b, B1 and B2, without excessive abstention?
- **RQ4 (failure attribution), exploratory.** When the pipeline is wrong, is the error caused by extraction or by revision?

## 2. Hypotheses

"B-X" = method X run on the shared LLM extraction (Condition B). The unit is the scenario. Estimands and tests are in §5.

| ID | Hypothesis | Endpoint (§4) | Estimand | Rule |
|---|---|---|---|---|
| H1 | B-B5 is more correct than B1 | Primary, analysis set | mean paired difference B-B5 − B1 | Superiority, predicted > 0 |
| H2 | B-B5 is more correct than B2 | Primary, analysis set | mean paired difference B-B5 − B2 | Superiority, predicted > 0 |
| H3 | *Withdrawn in v0.2 pending N1; see RQ2* | — | — | — |
| H4 | B-B5 is not meaningfully worse than B-B4b | Primary, analysis set | mean paired difference B-B5 − B-B4b | Non-inferiority, margin δ = 0.05 |
| H5a | B-B5 is less often falsely confident than each of B-B4b, B1, B2 (three comparisons) | False-confidence rate, ambiguous-node scenarios | pooled-rate difference B-B5 − X | Superiority, predicted < 0 |
| H5b | B-B5 does not over-abstain | False-abstention rate, analysis set | pooled rate of B-B5 | Below threshold τ_FA = 0.15 |

Against B4b, B5's distinctive claim is H5a; on gold input B4b already matches gold on Cat 5–6.

## 3. Conditions and methods

| Condition | Input | Methods | Role |
|---|---|---|---|
| **B (main)** | plan_text + change_text → shared extractor (one call per scenario per repeat) → identical structured input to every symbolic method | B3, B4a, B4b, **B5** | Confirmatory for B4b and B5 (H1, H2, H4, H5); B3 and B4a descriptive |
| **Direct LLM** | plan_text + change_text | B1 full regeneration, B2 delta | Confirmatory comparators (H1, H2, H5a) |
| **A (sanity)** | gold structured input, no LLM | B3, B4a, B4b, B5 | Descriptive only. Never evidence of extraction accuracy; B5 agreement here is expected by construction |
| **B6 oracle scope** | canonical input | evaluator-side | Diagnostic upper bound only |

Fixed for every call (config v1.7): model `nvidia/nemotron-3-ultra-550b-a55b`, temperature 0, seed 20261008, thinking
on, max 16,384 output tokens, prompts `b1_full_regeneration.v1.1`, `b2_delta.v1.1`, `extractor.v1.1`,
`common_reasons`, schemas `extractor_output.schema.v1.4`, `revision_output.schema.v1`. Served-model id must equal the
config id or the call aborts. All three LLM call types get the same abstention-reason list. Output parsing and label
mapping follow the pilot's approved scoring rules (`from_direct`, `_remap` in `../rn_pilot/pilot.py`): labels map
exactly, then case/space-insensitively; unmapped labels are counted, never guessed.

Budget: 63 scenarios × 3 repeats × {B1, B2, EXTRACT} = **567 calls** (+ 126 if the 14-scenario held-out set exists:
**693**). Retries of failed calls (§7) are not extra budget items; they are logged.

## 4. Metrics

All node-level quantities come from `reflica_bench/endpoints.py::node_counts`, which is built only from the evaluator's
own primitives `_abstained` and `_node_correct` (`reflica_bench/evaluator.py`). Appendix A, check 1 shows it reproduces
the evaluator's Cat 7 rates exactly.

### 4.1 Node classification (per scenario-repeat)

For each gold node (all nodes in `ground_truth.nodes`):

- **abstained** = determinability reported AMBIGUOUS, or outcome label UNCERTAIN or REQUIRES_REEVALUATION (`_abstained`);
- **AMBIGUOUS gold node** → *correct* if abstained, otherwise *falsely confident*;
- **determinable gold node** → *falsely abstained* if abstained; otherwise *correct* if `_node_correct`, else *committed-wrong*.
  `_node_correct`: outcome label equals gold, and, if the method outputs attribute values, every gold attribute value
  matches (numbers within absolute 1e-3, other values exactly). Extra predicted attributes are not penalised.

Every node lands in exactly one of: correct, falsely confident, falsely abstained, committed-wrong.

Special cases, applied identically to every method:
- **Failed output** (unparseable, schema-invalid, truncated, extraction failure, solver failure): no node is handled
  correctly; every ambiguous node counts as falsely confident and every determinable node as committed-wrong.
- **Missing node** (gold node absent from the output): counted as committed and wrong (evaluator semantics), and
  reported separately as *missing predictions* per method.
- **No attribute output** (B3, B4a): `_node_correct` checks labels only. These methods appear in no confirmatory hypothesis.
- **No determinability output** (B3 on all 63; B4a and B4b on 22 under gold input): the method can abstain only through an abstention label.

### 4.2 Endpoints

- **Primary endpoint** (per scenario-repeat) = correct nodes / gold nodes. Per scenario = mean over its common repeats (§7).
- **False-confidence count / rate** = falsely confident nodes; rate = Σ falsely confident / Σ ambiguous gold nodes (pooled over scenarios, evaluator definition). Reported first in every Cat 7 table and never averaged with anything.
- **False-abstention count / rate** = falsely abstained nodes; rate = Σ falsely abstained / Σ determinable gold nodes (pooled).
- Secondary, descriptive: every metric already in `evaluator.py` (over-flip, inertia, affected-node precision/recall, attribute-value accuracy, termination accuracy, false invalidation, partial-satisfaction preservation, binarisation error, feasibility and optimal-combination accuracy, pathology precision/recall, coverage, selective risk); missing-prediction count; cost (tokens, latency, calls); extraction quality as in the pilot. Unsupported metrics are N/A, never zero.

## 5. Statistical analysis plan

Code: `reflica_bench/stats.py` (standard library only). Tests: `tests/test_stats.py`.

- **Unit and aggregation.** The scenario. A scenario's value is the mean over its common repeats (§7). Count-based quantities (false confidence, false abstention) are also averaged over common repeats, then summed over scenarios for pooled rates.
- **Pairing.** All methods are scored on the same analysis set and the same repeats; in Condition B every symbolic method receives the identical extraction of a repeat.
- **Estimands.**
  - H1, H2, H4: mean over scenarios of the per-scenario difference in primary endpoint (every scenario equal weight).
  - H5a: pooled-rate difference = Σ_s (fc_B5,s − fc_X,s) / Σ_s amb_s over the scenarios with ≥ 1 AMBIGUOUS gold node (currently 11, all Cat 7). This set is fixed by gold labels, not by results.
  - H5b: pooled false-abstention rate of B-B5 over the analysis set.
- **Confidence intervals.** 95% percentile bootstrap: scenarios resampled with replacement **within category** (Cat 6-A and 6-B together as Cat 6), keeping each category's size; 10,000 resamples; quantiles by linear interpolation (type 7); a fresh generator seeded 20261010 for every CI, so each CI is reproducible on its own. CIs are not multiplicity-adjusted.
- **Tests.** Two-sided Wilcoxon signed-rank test on the same per-scenario differences that define the estimand (H5a: per-scenario count differences fc_B5,s − fc_X,s, whose sum over scenarios is the numerator of the pooled difference). Zero differences are dropped; tied |differences| get average ranks; differences are rounded to 12 decimals before ranking. The p-value is **exact**: the null distribution is enumerated over all sign assignments of the observed ranks, so it stays exact with ties. Effect size: matched-pairs rank-biserial correlation.
- **Multiplicity.** Holm–Bonferroni over exactly **5 tests**: H1, H2, H5a-vs-B4b, H5a-vs-B1, H5a-vs-B2; familywise α = 0.05. H4 and H5b are CI rules and are not in the family. Secondary and per-category results are descriptive: CIs shown, no p-value used for a claim.
- **Power note (fixed before data).** H5a uses 11 scenarios. With 5 Holm tests the smallest p-value must be < 0.01; the exact test reaches that only with **≥ 8 non-zero differences all in one direction** (7 give p = 0.0156). H5a can therefore be Inconclusive even if B5 is better; that outcome is reported as such, not as evidence of no difference.
- **Per-category results.** Descriptive only (n = 4–16 per category).
- **Repeatability.** Per call type, agreement of outputs across the 3 repeats is reported (temperature 0 is not guaranteed deterministic on this endpoint; the pilot recorded seed behaviour as unverified).
- **Pre-specified sensitivity analyses (reported, never change a verdict).** (i) equal weight per category instead of per scenario; (ii) available-case repeats instead of common repeats.

## 6. Verdict rules (applied automatically; all inequalities strict)

| Verdict | Superiority (H1, H2, each H5a comparison) | Non-inferiority (H4) | Threshold (H5b) |
|---|---|---|---|
| **Supported** | Holm-adjusted p < 0.05, **and** CI entirely on the predicted side of 0, **and** rank-biserial points the predicted way | CI lower bound > −0.05 | CI upper bound < 0.15 |
| **Contradicted** | Holm-adjusted p < 0.05, **and** CI entirely on the opposite side, **and** rank-biserial points the opposite way | CI upper bound < −0.05 | CI lower bound > 0.15 |
| **Inconclusive** | anything else (including all-zero differences, p = 1) | anything else | anything else |

**Consistency of test and CI.** The CI describes the mean difference; the Wilcoxon test describes the location of the
same per-scenario differences. They can disagree (e.g. p < 0.05 while the CI touches 0). A verdict needs both, so a
disagreement can only produce Inconclusive, never Supported. Every such case is flagged *discordant* in the report.

**Composites.** H5a overall = Supported iff all three comparisons are Supported; Contradicted iff any is Contradicted;
otherwise Inconclusive. H5 overall = the same rule over {H5a overall, H5b}.

Every verdict is reported with its estimate, 95% CI, raw and Holm-adjusted p, rank-biserial and the number of non-zero differences.

## 7. Eligibility, failures and missing data

Code: `stats.analysis_set`. Statuses per call: **ok**, **model failure** (scored, §4.1), **infrastructure missing**.

- **Common repeats.** A repeat r is *common* to a scenario if none of its three calls (B1 r, B2 r, EXTRACT r) is
  infrastructure-missing. Every method (B1, B2 and the four Condition B methods) is scored on exactly the common repeats.
- **Analysis set.** All scenarios with ≥ 1 common repeat. **Every confirmatory comparison uses this one set**; H5a uses
  its subset of scenarios with ambiguous gold nodes.
- **Stop rule.** If more than 5% of planned calls are infrastructure-missing after the retry policy, stop and report before any analysis.

| Event | Handling |
|---|---|
| API / infrastructure failure (HTTP 5xx, 429 after retries, timeout) | Retry with backoff as in the pilot; then one re-run of that call later. Originals kept in a failures log. Still failing → infrastructure missing. |
| Model unavailable | D5. Never switch model or settings mid-run. |
| Genuine model failure (non-JSON, schema-invalid, truncated, unmapped labels, invented content) | **Never excluded.** Scored per §4.1. |
| Extraction failure | Every Condition B method receiving it is scored as a failed output for that repeat. Classified for RQ4. |
| Solver failure on a valid extraction | Failed output for that method only; reported. |

**Missingness report** (always published): for each condition × method × category, calls planned, ok, model failures,
infrastructure missing, repeats used, scenarios excluded (by id), and missing-prediction node counts.

## 8. Held-out set (D3)

**8.1 Who.** Author: the owner (N2). Reviewer: a second person who did not write B5. The agent sessions that built B5
do not write, review or see held-out scenarios before they are frozen.

**8.2 Construction.** About 2 scenarios per category: Cat 1–5 two each, Cat 6 one C6-A and one C6-B, Cat 7 two that
contain at least one AMBIGUOUS gold node (14 total). Written from the category definitions and the scenario schema only,
not from B5's code or report. New domains and names; no edited copies of the 63. Structural near-duplicate check: no
held-out scenario may match a canonical one on node count, edge-type multiset and rule formulas together (scripted).

**8.3 Gold validation.** Author writes gold labels by hand. They must agree with the independent exact generator
`gt_engine.py` on every node's label, values and determinability, and pass the linter and the R-N leakage checker.
Disagreements are resolved by the author with a written note before freezing; a scenario `gt_engine` cannot express is
dropped, not hand-patched. Only evaluator-side tools (`gt_engine`, linter, renderer, leakage checker) may run on held-out
scenarios before freezing; no compared method (B1–B5) and no LLM.

**8.4 Leakage prevention.** The held-out files get their own SHA-256 manifest, separate from benchmark v0.2.0 (which is
not changed). Its hash goes into the protocol lock before any call. B5 stays at v0.1.0; any B5 change after held-out
results are seen invalidates the held-out evaluation.

**8.5 Timing.** The held-out manifest must be frozen **before the main run starts**. If it is not ready by the deadline
(N3), the protocol is frozen without it and the limitation is reported. A held-out set built after main results exist
is labelled post-hoc and exploratory.

**8.6 Analysis and scope of claims.** Same calls, settings, repeats, endpoints and statistics as the main run, analysed
**separately** (never pooled with the 63). It is a pre-registered **replication**, not part of the confirmatory family:
estimates and 95% CIs are reported, p-values unadjusted and descriptive, no verdicts. Per hypothesis it is reported as
*consistent* (estimate on the same side as the main result and CI not entirely on the opposite side) or *not
consistent*. Claim supported: "the direction of the main result holds on 14 unseen scenarios", nothing stronger.

## 9. Fingerprints and the pre-call gate

Code: `reflica_bench/protocol_lock.py`. Tests: `tests/test_protocol_lock.py`.

`fingerprints()` records: protocol file hash; benchmark manifest hash (and every scenario file, via `rn.verify_manifest`);
B5 file hashes and version id (recomputed from the files: first 16 hex of sha256 of the sorted file→hash JSON); LLM
config hash and every prompt and schema hash; client (`_api.py`) hash; hash of the deterministic renders of all 63
scenarios plus render version; hashes of the analysis code (evaluator, endpoints, stats, schema, loader, adapters,
baseline, extraction schema, protocol_lock); held-out manifest hash if any.

`record_problems()` checks the existing records against disk (benchmark manifest, `b5/FROZEN.json`, config v1.7 prompts,
schemas, client, extraction schema, render leakage). `assert_ready_for_llm_calls()` raises unless the protocol is
frozen, the lock is valid, there are no record problems and every fingerprint equals the active lock entry. **The
full-run runner (task 2) must call it before its first request** and store its output in the run folder, together with
its own runner fingerprint, Python and package versions, and the shuffled run order (seed 20261010).

## 10. Freezing and amendments

- **Draft:** no `protocol_lock.json`; `PROTOCOL.md` status line says DRAFT and NOT FROZEN (test-enforced). No LLM call possible.
- **Freeze** (only after the owner's written approval): copy the approved text to `PROTOCOL.v1.0.md` with status FROZEN, and write `protocol_lock.json` with version, file, sha256, date, approver and the full `fingerprints()` output.
- **After freezing:** a test fails if any listed file is edited or deleted, or if its status line does not say FROZEN.
- **Amendment:** a new file `PROTOCOL.v1.N.md`, a new lock entry whose `supersedes` equals the previous hash, and an `AMENDMENTS.md` entry with both hashes, the date, the reason and the expected effect. Earlier files are never edited. Amendments after the first full-run call apply only to a new, separate run.
- During the run: no change to protocol, prompts, schemas, metrics or verdict rules; no look at aggregated results before the completeness check passes; deviations go to `DEVIATIONS.md` before analysis. All hypotheses are reported whatever the verdict.

## 11. Known limitations (to report in the thesis)

- B5 was designed with the 63 scenarios visible; structured-input agreement is expected (held-out set, §8, partly addresses this).
- Hypotheses were revised after Condition A sanity results (N4); no LLM full-run data existed.
- H5a rests on 11 scenarios and 19 ambiguous nodes; its power is limited (§5).
- B3 and B4a cannot output attribute values, so their correctness is label-only and they are excluded from confirmatory tests.
- One primary LLM, one provider (free tier); replication model not available.
- Synthetic, template-rendered language; real user text may be harder.

---

## Appendix A — checks performed for v0.2 (2026-10-10, no model or API calls)

| # | Check | Result |
|---|---|---|
| 1 | `node_counts` vs evaluator `evaluate_category_7`, all 63 scenarios × B3/B4a/B4b/B5 on gold input: false-confidence, false-abstention, selective risk, determinability accuracy, and the four-way node partition | **145 cross-checks, 0 mismatches**; partition holds on all 252 runs |
| 2 | Condition A summary (gold input; 230 nodes, 19 ambiguous) | mean primary: B3 0.885, B4a 0.904, B4b 0.952, B5 1.000. False confident: 19, 15, 11, 0. False abstained: 0, 2, 0, 0. Cat 5–6 labels: 107/107 for all four → H3 not testable (N1) |
| 3 | Scenarios with ambiguous gold nodes | 11 (all Cat 7); nodes per scenario 1,1,1,1,1,1,2,2,2,3,4 |
| 4 | Pilot scorer on failed outputs | gives a status but no metrics → rule written into §4.1 and implemented (`node_counts(None, …)`) |
| 5 | Wilcoxon | equals brute-force enumeration on 200 random cases with ties and zeros, and scipy's exact test on 50 no-tie cases |
| 6 | Bootstrap, quantiles, Holm, verdict boundaries, common-repeat rule | unit-tested, including strict boundaries (−0.05, 0.15, α) |
| 7 | Existing records vs disk | benchmark manifest, B5 FROZEN.json (files and version id), config v1.7 prompts, schemas, client, extraction schema: **all match**. The B5 id and the client hash were not checked by any test before; now they are |
| 8 | Renders of all 63 scenarios | leakage checker: 0 problems |
| 9 | Freeze rule | edit, deletion, wrong status, undocumented amendment, broken chain and file reuse all fail; a documented amendment passes; the gate refuses calls in draft and on any tampered fingerprint |
| 10 | Mutation check of the new code (7 deliberate bugs) | every bug made a test fail |
| 11 | Full test suite | **234 passed** (203 existing + 31 new) |

## Appendix B — changes from v0.1

Owner decisions D1–D5 recorded · H3 withdrawn pending N1 · Holm family fixed to 5 tests · exact estimands per
hypothesis · H5a estimand and test aligned (pooled-rate difference ↔ per-scenario count differences) · failed-output,
missing-node and label-only rules made explicit · common-repeat rule, single analysis set and missingness report ·
test/CI consistency and discordance rule · composite verdict rules · power note for H5a · held-out protocol (§8) ·
fingerprint list and pre-call gate (§9) · versioned freeze and amendment rule (§10) · Pratt sensitivity analysis removed
(not implemented) · new code: `reflica_bench/endpoints.py`, `stats.py`, `protocol_lock.py` and three test files.
