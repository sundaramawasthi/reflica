# Confirmatory experiment protocol — benchmark v0.2.0 · config v1.7 · B5 v0.1.0

**Status: DRAFT v2 — revised with the owner's decisions D1–D7 (2026-10-09).
Awaiting final owner approval. After approval, the SHA-256 of this file is
recorded in every run's `env.json`; any later change is versioned and logged
with a reason.**

Implementation: `run.py` (runner + scoring), `analyse.py` (hypothesis
tests), `stats.py` (bootstrap, Holm), tests in
`research/tests/test_full_experiment.py`. Every rule below is implemented
there and covered by a test.

---

## 1. Research question

Does LLM extraction followed by dependency-aware revision with a
determinability check (LLM→B5) keep plan state valid under a change better
than direct LLM reasoning (B1, B2), and no worse than the same extraction
followed by a CP-SAT solver (LLM→B4b)?

B5 is **not** claimed to be novel. The contribution under test is the
evaluated combination. No hypothesis is reported as supported before the
analysis in §6 has run on the confirmatory data.

## 2. Data: confirmatory vs. pilot (D2)

- **Confirmatory data:** all 63 scenarios run **fresh** in one run, R = 3
  repeats per call → 63 × 3 calls (B1, B2, EXTRACT) × 3 = **567 calls**.
- **Pilot data** (144 calls, `experiments/rn_pilot/`) is a separate
  development dataset. It is never merged with, substituted for or used to
  tune the confirmatory run. It was used only for operational checks of the
  harness (statuses, failure attribution, confidence propagation); no pilot
  accuracy, effect size or verdict was inspected when writing this protocol.
- Natural-language inputs: `reflica_bench/rn/full/` (63 files, frozen renderer
  `rn-template-1.0.0`, 0 leakage findings, the 16 pilot scenarios identical to
  the pilot files).
- Prompts, schemas, model and settings: exactly `config.frozen.json` v1.7.
  Nothing in the frozen benchmark, gold answers, config or B5 is changed.

## 3. Conditions and comparators (D1)

| Condition | Input | Role |
|---|---|---|
| **LLM→B5** | shared extraction | **Method under test** |
| B1 full regeneration | plan + change text | Comparator (direct LLM) |
| B2 delta | plan + change text | Comparator (direct LLM) |
| LLM→B4b | the *same* extraction as LLM→B5 | Comparator (LLM + solver) |
| gold→B4b, gold→B5 | canonical structured input | Pre-run gate only, never evidence |
| B6 oracle scope | gold affected set | Scope diagnostic only |

Per scenario and repeat: exactly one EXTRACT call; its output is judged once
(§8) and, if valid, given unchanged to both B4b and B5.

**Primary comparators, explicitly:**

| Hypothesis | Comparisons (B5 − comparator) | Family / correction |
|---|---|---|
| **H1** | over-flip vs B1 · over-flip vs B2 · missed change vs B1 · missed change vs B2 | 4 tests, Holm |
| **H2** | value accuracy vs LLM→B4b: aggregate, Cat 5, Cat 6-A, Cat 6-B | Intersection–union (all must pass); no correction needed |
| **H3** | pooled false-confidence vs B1 · vs B2 · vs LLM→B4b; plus B5's own false-abstention vs 0.15 | 3 tests, Holm; threshold check separate |

Secondary (reported, no verdict): H1 metrics vs LLM→B4b.

## 4. Hypotheses and decision rules

Notation: d = B5 − comparator; CI = two-sided 95% percentile bootstrap
interval; Holm at familywise α = 0.05.

**H1 (Cat 1–4, 22 scenarios).** B5 makes fewer over-flips and fewer missed
changes than B1 and B2.
- *Supported* iff all 4 Holm-adjusted tests reject with d < 0.
- *Partially supported* iff some, not all, do. *Not supported* iff none do.
- A comparison where both methods score identically on every scenario (e.g.
  both 0: floor effect) cannot reject, so H1 cannot be fully supported; it is
  reported as a floor effect.

**H2 (Cat 5–6, 25 scenarios).** B5 is non-inferior to LLM→B4b on value
accuracy (higher is better), margin δ = 0.05.
- Non-inferiority in a group iff the **lower CI bound of d > −0.05**
  (equivalent to a one-sided test at α = 0.025).
- Groups: aggregate (mean of the 25 scenario-level values, each scenario
  weighted equally), and separately Cat 5 (12), Cat 6-A (9), Cat 6-B (4).
- *Supported* iff non-inferiority holds in the aggregate **and** in every one
  of the three categories.
- *Supported in aggregate only* iff the aggregate passes and every category's
  point estimate is > −0.05, but at least one category's CI reaches −0.05
  (non-inferiority not established there; reported per category).
- *Not supported* iff the aggregate fails, **or any category's point estimate
  is ≤ −0.05**. A strong category therefore cannot conceal a weak one.
- Cat 6-B has only 4 scenarios; its CI is expected to be wide, so "supported
  in aggregate only" is a likely outcome and will be reported as such.

**H3 (Cat 7, 16 scenarios: 19 ambiguous, 37 determinable nodes).** B5 has a
lower false-confidence rate than every comparator while keeping its
false-abstention rate ≤ 0.15.
- (a) For each comparator, Holm-adjusted test rejects with d < 0.
- (b) B5's pooled false-abstention rate with a 95% cluster-bootstrap CI:
  **PASS** iff the upper bound ≤ 0.15; **FAIL** iff the lower bound > 0.15;
  otherwise **INCONCLUSIVE**. A point estimate alone never passes (D6).
- *Supported* iff (a) for all three comparators and (b) PASS.
- *Inconclusive* iff (a) holds and (b) is INCONCLUSIVE.
- *Not supported* otherwise (any comparison fails, or (b) FAIL).
- **Power:** with 37 determinable nodes the CI half-width for a rate near 0.1
  is roughly ±0.1, so PASS requires an observed false-abstention rate close to
  0. An INCONCLUSIVE result is a likely, honestly reported outcome.

## 5. Metrics

All metric values come from `reflica_bench.evaluator` (frozen); `run.py`
only selects and combines them. N/A is never scored as 0.

### Primary metric definitions

**Over-flip rate (H1).** `over_flip_rate`: of the nodes the gold labels as
`MUST_STAY_STABLE`, the share whose predicted label is not
`MUST_STAY_STABLE` or whose predicted attributes differ from gold. An
abstention label on a stable node counts as a flip.

**Missed-change rate (H1, D3).**
- *Gold affected set* A* = nodes with `in_affected_set = true` in the frozen
  ground truth. It includes the event's own target (the added, deleted or
  edited node) and every node whose outcome must change.
- *Predicted affected set* Â = the method's `affected_set` (B1/B2: every
  entity not labelled `not_changed`, after label mapping; B4b/B5: their
  affected set, remapped to canonical ids).
- Missed-change rate = |A* \ Â| / |A*| = 1 − affected-node recall,
  **defined only when A* is non-empty**.
- *Irrelevant-change scenarios (Cat 1):* A* contains only the changed node
  itself (3 of 4 scenarios); for `cat1_relchange_nonprop_001` A* is empty, so
  that scenario contributes to over-flip only.
- *Alternative-reason scenarios (Cat 4):* a conclusion still supported by
  another reason is `MUST_STAY_STABLE` and **not** in A*; changing it is an
  over-flip, not a missed change. `cat4_add_alternative_001` and
  `cat4_relchange_breaks_one_001` have empty A* (over-flip only). Result:
  19 of 22 Cat 1–4 scenarios enter the missed-change analysis.

**Value accuracy (H2, D4).**
- Cat 5: pooled hit rate over `attribute_accuracy_by_type`: hits = discrete
  `exact_match`, bounded/unbounded `within_tolerance`, signed `sign_match`,
  each × n; divided by Σn. Missing predictions count as misses.
- Cat 6-A: the same pooling over `aggregate_value_accuracy`.
- Cat 6-B: `optimal_combination_accuracy`.

**False-confidence rate (H3).** Σ (ambiguous nodes on which the method
committed) ÷ Σ (ambiguous nodes), pooled over Cat 7 scenarios. Pooled because
the 5 false-ambiguous control scenarios have no ambiguous node.

**False-abstention rate (H3).** Σ (determinable nodes on which the method
abstained) ÷ Σ (determinable nodes), pooled (37 nodes).

### Secondary metrics

Reported per condition, no verdict: inertia, unnecessary revision,
affected-node precision, final-state accuracy, attribute accuracy by type,
termination accuracy, preservation and false invalidation, feasibility
classification, binarisation error, partial-satisfaction preservation,
feasible-combination precision/recall, correct abstention, determinability
accuracy, pathology precision/recall, escalation accuracy, coverage, selective
risk, extraction quality, token and latency costs.

**Confidence limitation.** B5 outputs only confidence 0 or 1 (all 230 gold
nodes) and B4b outputs none. No claim of calibrated uncertainty is made for
B5; the risk–coverage area is not compared across methods, and coverage /
selective risk are reported as a single operating point.

## 6. Statistical analysis (D5)

- **Unit and aggregation.** The scenario. A metric is first averaged over the
  scenario's repeats (repeats paired by index; a repeat is used only when
  both compared conditions have a value), giving one value per scenario per
  condition. Repeats are never treated as independent scenarios (tested).
- **Paired bootstrap.** For each comparison, d_s = B5_s − comparator_s per
  scenario; resample the scenarios with replacement **10,000** times with
  seed **20261009**; CI = 2.5th and 97.5th percentiles of the resampled mean
  of d. Pooled Cat 7 rates use the same scenario resampling, recomputing
  Σnum/Σden each time (cluster bootstrap); resamples with a zero denominator
  are skipped and their count reported.
- **p-values** by inverting the bootstrap distribution:
  p = 2·min(P*(d ≤ 0), P*(d ≥ 0)), capped at 1; **Holm** step-down within each
  family (§3).
- **Appropriateness per metric (checked):**
  - Over-flip, missed change, value accuracy: bounded per-scenario rates with
    many ties at 0 and 1 → nonparametric bootstrap of the mean difference is
    appropriate; a t-test is not (non-normal, small n). If all differences are
    identical the interval collapses to a point and the test cannot reject;
    this is reported as degenerate.
  - False-confidence and false-abstention: ratios of sums over clustered
    nodes → cluster bootstrap by scenario; node-level tests (e.g. McNemar)
    would wrongly treat nodes of one scenario as independent.
  - Cat 6-B (n = 4): only 35 distinct resamples exist; the interval is coarse
    and is reported with that caveat.
- **Sensitivity analyses** (reported next to the primary): exact Wilcoxon
  signed-rank is *not* used (it would need SciPy and discards ties, which are
  the majority here); instead the failure-handling variants of §8 and a
  first-repeat-only analysis (S3).
- Verified: bootstrap determinism, agreement with normal theory on a
  large synthetic sample, Holm against a hand computation, and every decision
  rule on synthetic data (`test_full_experiment.py`).

## 7. Pre-run gates (`run.py check`; the run refuses to start otherwise)

1. `pytest` passes (currently **232/232**, including `test_b5.py`'s
   0-disagreement check).
2. Benchmark manifest verifies (v0.2.0).
3. All fingerprints in `config.frozen.json` and `b5/FROZEN.json` match.
4. All 63 R-N files exist, equal a fresh render, pass the leakage checker,
   and the 16 pilot ones equal the pilot files.
5. gold→B4b and gold→B5 run and score on all 63 scenarios.
6. Prompts contain only plan text, change text, schema and the reason list;
   alias maps stay evaluator-side (frozen `render_prompt`).
7. The CLI refuses a paid run without `--i-approve-paid-run`.

## 8. Failures, retries and missing results (D7)

### Failure stages

| Stage (status) | Meaning | Applies to |
|---|---|---|
| `missing` | call never logged | API / infrastructure |
| `api_error` | call failed after retries | API / infrastructure |
| `invalid_llm_output` | B1/B2 output truncated, not JSON, or wrong shape | B1, B2 |
| `invalid_extraction` | extraction truncated, not JSON, or fails the typed schema | **shared**: LLM→B4b and LLM→B5 identically |
| `extraction_failure` | schema-valid extraction cannot become a method input, or fails formula lint | **shared** |
| `solver_failure` | B4b raised on a valid extraction | LLM→B4b only |
| `b5_failure` | B5 raised on a valid extraction | LLM→B5 only |
| `evaluation_failure` | label mapping or metric computation raised | harness defect; the run is invalid until fixed and re-scored |

A shared extraction failure is always recorded for **both** downstream
methods with the same status and the same worst-case value; it is never
attributed to one method selectively. A method that receives a valid
extraction and raises is charged with its own stage. Example from the pilot:
the extraction with an invented preference rule (T7.2) is schema- and
lint-valid; B4b raised (`solver_failure`), B5 abstained (`ok`). Abstaining is
an answer, scored by the Cat 7 metrics, never a failure.

### Retries and logging

- HTTP 429/503: frozen client policy, up to 5 retries with back-off
  15·2^k s, retry count logged.
- Every attempt is appended to `raw.jsonl` with the full output; nothing is
  deleted or overwritten. One data-completion pass (`--completion`) reruns
  only calls whose every attempt failed, at most once per call. Scoring uses
  the first successful attempt.
- Served model ≠ frozen model id → the run aborts.
- Identical outputs across repeats are kept; the share of byte-identical
  repeats is reported (temperature 0 is not deterministic for this model).

### Handling rules

| Rule | Infrastructure failures | All other failures |
|---|---|---|
| **Primary** | excluded, pairwise (a repeat counts only if both compared conditions have a value) | worst value: error rates = 1, accuracy = 0, Cat 7: committed on every ambiguous node and abstained on every determinable node |
| S1 complete case | excluded | excluded (conditional accuracy given success) |
| S2 all worst case | worst value | worst value |
| S3 first repeat | as primary, repeat 0 only | as primary |

Operational failure rates per condition and stage are reported in their own
table, separately from accuracy (S1 is the conditional accuracy).

## 9. Reproducibility

- Each run directory `runs/<run_id>/` holds `raw.jsonl` (append-only),
  `env.json` (Python version, platform, `pip freeze`, git commit and dirty
  flag, config version, model id, provider name, SHA-256 of this protocol,
  `run.py`, `analyse.py` and `stats.py`), `scores.jsonl`, `summary.json`,
  `analysis.json` and `report.md`.
- Scoring and analysis are pure functions of `raw.jsonl` + frozen code.
  Re-scoring is deterministic (sorted JSON keys, fixed bootstrap seed); the
  pilot re-scoring check reproduced the committed pilot files byte-for-byte.
- The API key is read only by the frozen client from the environment
  (`NVIDIA_API_KEY`, `REFLICA_LLM_PROVIDER=nvidia`); it is never logged,
  printed, written to `env.json` or committed.

## 10. Known limitations (to be stated in the thesis)

- B5's agreement with gold on clean input is expected; it says nothing about
  robustness to extraction errors.
- B5's in-scope **repair path is never exercised** by consistent inputs.
- B5's escalation label (UNCERTAIN vs REQUIRES_REEVALUATION) matches gold on
  only **11/19** ambiguous nodes; escalation accuracy is secondary only.
- B5 confidence is binary; no calibration claim.
- Small samples (22 / 25 / 16 scenarios; 19 ambiguous and 37 determinable
  Cat 7 nodes; Cat 6-B n = 4).
- One model on a free-trial endpoint; replication models returned HTTP 504.
- Template-rendered text is cleaner than real user writing.
- Bootstrap percentile intervals can be slightly too narrow at small n.
