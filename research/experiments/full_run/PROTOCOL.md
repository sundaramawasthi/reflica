# Full experiment — protocol

**Status: DRAFT v0.1 (2026-10-10) — NOT FROZEN. No full-run call may be made under this document until it is approved and frozen.**
Benchmark v0.2.0 (manifest `27b6ea09…6915`) · B5 v0.1.0 (id `fc9524a4ea38cca5`) · LLM config v1.7 (`../rn_pilot/config.frozen.json`)

Freezing = the owner approves in writing, the open decisions in §0 are closed, the file's SHA-256 is recorded in
`PROTOCOL.frozen.json`, and a test fails if this file changes afterwards. Later changes are amendments (§10), never edits.

---

## 0. Open decisions (owner must close before freezing)

| # | Decision | Proposed default |
|---|---|---|
| D1 | Meaning of the locked "τ_FA 0.15": maximum acceptable **false-abstention rate** of B5 on determinable nodes (H5). | As stated |
| D2 | Meaning of the locked "δ 0.05": **non-inferiority margin** on the primary endpoint, B5 vs B4b (H4). | As stated |
| D3 | B5 was built and validated with all 63 scenarios visible (B5_REPORT §6). Add a small **held-out set** (e.g. 2 new scenarios per category, written and frozen before the run, never shown to B5's author) for a confirmatory replication? | Yes, if time allows; otherwise state as a limitation |
| D4 | Repeats per LLM call. | 3 (as pilot) |
| D5 | Model unavailable mid-run (HTTP 504 history on the free endpoint): pause and resume with the same model, or restart everything under a new frozen config? Never mix models in one analysis. | Pause ≤ 7 days, then restart under amendment |

---

## 1. Research questions

- **RQ1 (architecture).** Under natural-language input, does *extract → symbolic revision → determinability check* (B5) revise a plan more correctly than direct LLM reasoning (B1 regeneration, B2 delta)?
- **RQ2 (attribute awareness).** Does attribute-aware revision handle partial satisfaction and capacity constraints (Cat 5–6) better than classical reachability (B3) and ATMS (B4a) revision?
- **RQ3 (knowing when not to answer).** Does B5's determinability stage reduce false confidence on ambiguous nodes (Cat 7 and any AMBIGUOUS gold node) compared with B4b, B1 and B2, without excessive abstention?
- **RQ4 (failure attribution, exploratory).** When the pipeline is wrong, is the error caused by extraction or by revision?

## 2. Hypotheses (confirmatory family)

All use the scenario as the unit of analysis (§5). "B-X" = method X run on the shared LLM extraction (Condition B).

| ID | Hypothesis | Endpoint | Comparison | Type |
|---|---|---|---|---|
| H1 | B-B5 is more correct than B1 | Primary endpoint (§4.1), all 63 | B-B5 − B1 > 0 | Superiority, two-sided |
| H2 | B-B5 is more correct than B2 | Primary endpoint, all 63 | B-B5 − B2 > 0 | Superiority, two-sided |
| H3 | On Cat 5–6, B-B5 gets outcome labels right more often than both classical baselines | Label accuracy (§4.2), Cat 5–6 (25 scenarios) | B-B5 − B-B3 > 0 **and** B-B5 − B-B4a > 0 | Superiority, both must hold |
| H4 | B-B5 is not meaningfully worse than the constraint-programming baseline | Primary endpoint, all 63 | B-B5 − B-B4b > −δ (δ = 0.05) | Non-inferiority, one-sided |
| H5 | B5 is less falsely confident than every other method, and does not over-abstain | False-confidence rate (§4.2) on AMBIGUOUS nodes; false-abstention rate on determinable nodes | (a) B-B5 < B-B4b, B1, B2 on false confidence; (b) B-B5 false abstention < τ_FA = 0.15 | (a) superiority; (b) threshold |

H3 note: B3 and B4a have no notion of partial satisfaction, so they are expected to lose on Cat 5–6. H3 confirms the
benchmark discriminates; it is **not** evidence of novelty over B4b. Against B4b, B5's distinctive claim is H5.

## 3. Conditions and methods

| Condition | Input | Methods | Role |
|---|---|---|---|
| **B (main)** | plan_text + change_text → shared extractor (one call per scenario per repeat) → identical structured input to every symbolic method | B3, B4a, B4b, **B5** | Confirmatory (H1–H5) |
| **Direct LLM** | plan_text + change_text | B1 full regeneration, B2 delta | Confirmatory comparators (H1, H2, H5) |
| **A (sanity)** | gold structured input, no LLM | B3, B4a, B4b, B5 | Descriptive only. Never evidence of extraction accuracy; B5 agreement here is expected by construction |
| **B6 oracle scope** | canonical input | evaluator-side | Diagnostic upper bound only |

Fixed for every call (from config v1.7): model `nvidia/nemotron-3-ultra-550b-a55b`, temperature 0, seed 20261008,
thinking on, max 16,384 output tokens, prompts `b1_full_regeneration.v1.1`, `b2_delta.v1.1`, `extractor.v1.1`,
`common_reasons`, schemas `extractor_output.schema.v1.4`, `revision_output.schema.v1`. Served-model id must equal the
config id or the call aborts. All three LLM conditions receive the same abstention-reason list.

Volume: 63 scenarios × 3 repeats × {B1, B2, EXTRACT} = **567 LLM calls**. Symbolic methods add no LLM calls.

## 4. Metrics

### 4.1 Primary endpoint — node correctness (per scenario-repeat)
Fraction of gold nodes the method handles correctly:
- determinable gold node → committed (not abstained) **and** correct (outcome label matches; every gold attribute value matches, numeric tolerance 1e-3) — i.e. the evaluator's `_node_correct`;
- AMBIGUOUS gold node → abstained (UNCERTAIN or REQUIRES_REEVALUATION, or determinability AMBIGUOUS).

One number per scenario-repeat in [0, 1]; per scenario = mean over repeats. A method that does not output attribute
values is scored on labels only (the evaluator's existing rule); this is reported next to every result that involves it.
A method that never reports determinability (B3; B4a on some scenarios) is scored as committing on every node with the
label it gave — it cannot abstain except through an abstention label.

### 4.2 Secondary endpoints
- **Outcome-label accuracy** (labels only, determinable nodes) — used by H3.
- **False-confidence rate** = committed AMBIGUOUS nodes / AMBIGUOUS nodes. Reported first in every Cat 7 table, never averaged with anything (evaluator rule).
- **False-abstention rate** = abstained determinable nodes / determinable nodes.
- Category metrics already implemented in `reflica_bench/evaluator.py`: over-flip, inertia, affected-node precision/recall, attribute-value accuracy, termination accuracy (Cat 3), false invalidation (Cat 4), partial-satisfaction preservation and binarisation error (Cat 5), feasibility and optimal-combination accuracy (Cat 6), pathology precision/recall, coverage and selective risk (Cat 7).
- Cost: output tokens, latency, LLM-call count.
- Extraction quality (Condition B): entity recall, link recall, pre-value accuracy, pre-state reproduction, update correctness (as in the pilot).

Unsupported metrics are N/A, never zero.

## 5. Statistical analysis plan

- **Unit:** scenario (n = 63; n = 25 for H3). Repeats are averaged inside a scenario before any test. Every scenario has equal weight. Sensitivity analysis: equal weight per category.
- **Paired design:** every method sees the same scenarios (and, in Condition B, the same extraction), so all comparisons are paired by scenario.
- **Effect size:** mean paired difference, with a 95% CI from a scenario-level bootstrap stratified by category (10,000 resamples, percentile method, seed 20261010). Also matched-pairs rank-biserial correlation.
- **Superiority tests (H1, H2, H3, H5a):** two-sided Wilcoxon signed-rank on per-scenario differences (zero differences dropped, Pratt variant reported as sensitivity). Node-level rates (H5) use the same scenario-level bootstrap, because nodes within one scenario are not independent.
- **Non-inferiority (H4):** supported if the lower bound of the two-sided 95% CI of (B-B5 − B-B4b) is above −0.05.
- **Threshold (H5b):** supported if the upper bound of the 95% CI of B-B5's false-abstention rate is below 0.15.
- **Multiple comparisons:** Holm–Bonferroni over the confirmatory p-values {H1, H2, H3 (two tests), H5a (three tests)}, familywise α = 0.05. H4 and H5b are CI-based and are not part of the Holm family. Secondary and per-category results are exploratory: CIs shown, no p-value used for a claim.
- **Per-category results:** descriptive only (n = 4–16 per category is too small for tests).
- **Repeatability:** per-call agreement across the 3 repeats is reported for each LLM condition (temperature 0 is not guaranteed deterministic on this endpoint; the pilot recorded seed behaviour as unverified).

## 6. Verdict rules (applied automatically by the analysis script)

| Verdict | Superiority (H1, H2, H3, H5a) | Non-inferiority (H4) | Threshold (H5b) |
|---|---|---|---|
| **Supported** | Holm-adjusted p < 0.05 **and** 95% CI excludes 0 in the predicted direction | CI lower bound > −0.05 | CI upper bound < 0.15 |
| **Contradicted** | 95% CI entirely in the opposite direction | CI upper bound < −0.05 | CI lower bound > 0.15 |
| **Inconclusive** | anything else, including all-zero differences | anything else | anything else |

H3 is Supported only if both comparisons are Supported. H5a is reported per comparator and as a whole (all three Supported).
Every verdict is reported with its effect size and CI, never as a bare "significant / not significant".

## 7. Failures, exclusions and missing data

| Event | Handling |
|---|---|
| API / infrastructure failure (HTTP 5xx, timeout) | Retry with backoff as in the pilot; if still failing, re-run that call once later. Original failure kept in a failures log. |
| Persistent infrastructure failure | Call marked missing. Scenario kept if ≥ 1 repeat succeeded (mean over available repeats). If 0 succeeded: scenario excluded from comparisons that need it, listed by id. If > 5% of calls are missing: stop and report before analysis. |
| Genuine model failure (non-JSON, schema-invalid, truncated, unmapped labels, invented content) | **Not excluded.** Scored as the method's output: unparseable → every node incorrect; unmapped labels → those nodes incorrect. |
| Extraction failure in Condition B | Every symbolic method receiving that extraction is scored as failing it (same as the pilot's T7.2 case). Classified separately for RQ4. |
| Solver failure on a valid extraction | Scored as incorrect for that method; reported. |
| Model unavailable | See D5. Never switch model or settings mid-run. |

## 8. Error attribution (RQ4, exploratory)

For every Condition B scenario-repeat where B-B5 is wrong: if the extraction differs from gold on anything the scenario's
answer depends on → **extraction error**; if the extraction is correct and B5 is still wrong → **revision error**;
otherwise **both / unclear**. Condition A (gold → B5) bounds the revision-only error.

## 9. Reproducibility

Before the first call, record in the run folder: benchmark manifest hash, B5 version id, `config.frozen.json` hash, prompt
and schema hashes, runner and client fingerprints, this protocol's hash, Python and package versions. Every request and
raw response is logged (API key never stored). Analysis is one script run on the logged data with a fixed seed; it
re-checks all hashes and refuses to run on a mismatch. Run order: scenarios shuffled once with seed 20261010, the order saved.

## 10. Rules during and after the run

- No change to protocol, prompts, schemas, metrics or verdict rules once the first full-run call is made.
- No look at aggregated results before all calls are complete and the data-completeness check passes.
- Any deviation is written to `DEVIATIONS.md` with date, reason and expected effect, **before** analysis.
- An amendment after freezing creates `PROTOCOL.v0.2.md`; the frozen file is never edited.
- All hypotheses are reported, whatever the verdict. Exploratory findings are labelled exploratory.

## 11. Known limitations (to report in the thesis)

- B5 was designed with the benchmark visible; structured-input agreement is expected (see D3).
- One primary LLM, one provider (free tier); replication model (kimi-k3) not available yet.
- Small categories; per-category conclusions are descriptive.
- Synthetic, template-rendered natural language; real user text may be harder.
- B4b already matches gold on Cat 5–6 under gold input; B5's advantage over B4b is expected only on ambiguity handling.
