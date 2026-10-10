# Hypothesis changes before freezing

This file records every change to the hypotheses made while the protocol was a draft. It is part of the protocol record
and is reported in the thesis. The original draft is kept unchanged at `drafts/PROTOCOL.draft-v0.1.md`
(sha256 `e112437b0dabb99285ae8ffe3d7aefa469fbcfe57ed01ca3b98f889258450176`, commit `2f69c09`).

## Change 1 — H3 withdrawn from the confirmatory family

| | |
|---|---|
| **Date** | Found 2026-10-10 (draft v0.2 review); decided by the owner 2026-10-10 (decision N1). |
| **Draft affected** | v0.1 → v0.3 (v0.2 proposed it; archived at `drafts/PROTOCOL.draft-v0.2.md`). |
| **Original H3 (v0.1)** | "On Cat 5–6, B-B5 gets outcome labels right more often than both classical baselines": outcome-label accuracy, B-B5 − B-B3 > 0 and B-B5 − B-B4a > 0, superiority, inside the Holm family. |
| **New status** | Withdrawn. RQ2 is answered descriptively (protocol §4.3). The ID H3 stays reserved so the numbering shows the change. The Holm family goes from 7 tests (H1, H2, H3×2, H5a×3) to 5 (H1, H2, H5a×3). |

**Rationale.** H3 did not measure what it claimed. B3 and B4a cannot represent partial satisfaction or capacity at
all: they output no attribute values (`attribute_values` is None on all 63 scenarios), so every Cat 5–6 attribute
metric is N/A for them. Their outcome labels on Cat 5–6 are already all correct with gold input. Under LLM extraction
every symbolic method receives the same extraction, so a label-accuracy difference between B5 and B3/B4a would mostly
reflect how each method propagates the same extraction errors, not attribute awareness. A confirmatory test of it would
be uninformative or misleading.

**Evidence inspected (and only this).** Condition A, the gold-input sanity condition: B3, B4a, B4b and B5 on all 63
canonical scenarios, deterministic, no LLM. Script: `endpoints.node_counts` over `StructuredAdapter_v1(...).adapt(sc,
"gold")` for each method (reproduced by `tests/test_endpoints.py`).

| Method | Mean primary endpoint | Falsely confident (of 19 ambiguous) | Falsely abstained | Cat 5–6 labels correct | Cat 5–6 attribute metrics |
|---|---|---|---|---|---|
| B3 | 0.885 | 19 | 0 | 107/107 | N/A (no attribute output) |
| B4a | 0.904 | 15 | 2 | 107/107 | N/A (no attribute output) |
| B4b | 0.952 | 11 | 0 | 107/107 | computed |
| B5 | 1.000 | 0 | 0 | 107/107 | computed |

No Condition B data, no LLM output on the full 63 and no held-out data existed or were looked at. The R-N pilot
(16 scenarios, B1/B2/extraction→B4b, finished 2026-10-09) was already known when v0.1 was written; it was not
re-analysed for this change.

**Implications.**
1. The confirmatory claims are now H1, H2 (B5 vs direct LLM), H4 (non-inferiority to B4b) and H5 (false confidence and abstention). None of them concerns attribute awareness directly.
2. The thesis cannot claim, from a confirmatory test, that attribute awareness beats classical revision. It can report descriptively that B3/B4a cannot represent Cat 5–6 attributes at all (a design property, not a statistical finding) and how accurately B4b and B5 compute them after LLM extraction.
3. B5's advantage over B4b is expected only on ambiguity handling (H5a). On gold input B4b already matches gold on Cat 5–6.
4. Changing a hypothesis after seeing any result is a researcher degree of freedom. The change was triggered by a structural property (unsupported output dimensions) visible in sanity data, it removes a test rather than adding one that favours B5, and it was decided before any confirmatory data existed. These three facts, and this file, are reported with the results.
5. Fewer tests in the Holm family make each remaining test slightly easier to pass (smallest p must be < 0.01 instead of < 0.0071). That is a consequence of the change and is stated.

## Change 2 — sign-flip test for H1, H2, H5a (proposed in v0.3; approved conditionally; withdrawn in v0.4)

| | |
|---|---|
| **Date** | Proposed 2026-10-10 (v0.3). Approved by the owner 2026-10-10 **on condition** that its assumptions are documented and checked, with an alternative proposed if they are not defensible. Checked and withdrawn 2026-10-10 (v0.4). |
| **What it was** | Exact paired sign-flip test on Σ d_s (mean difference for H1/H2, pooled-rate difference for H5a), Wilcoxon as sensitivity. |
| **Assumption** | Under H0 each per-scenario difference d_s is symmetric about 0 and independent across scenarios. This holds if the two methods' outputs are exchangeable within a scenario, but **not** under the hypotheses' actual null (equal *expected* values), when the methods have different error structures. |
| **Check performed** | Offline simulation at the protocol's structure (Appendix C of the protocol): B5 is deterministic per scenario given the extraction, so its errors are all-or-nothing; B1/B2 vary node by node and are averaged over 3 repeats. |
| **Result** | Not defensible. H5a: with equal means, false "B5 better" at α = 0.01 was 1.95% (nominal one-sided 0.5%). H1/H2 (63 scenarios, accuracy ≈ 0.95): 10.9% at α = 0.05 (nominal 2.5%) and 6.3% at α = 0.01. Wilcoxon: 82% false "B5 better" for H1. The percentile bootstrap CIs also under-covered (H4 90–92%; H5b 70% for rare, clustered abstentions). |
| **Evidence inspected** | Simulations only. No experimental data. |
| **Implication** | Every error points in B5's favour, so keeping these tests would bias the thesis towards its own hypotheses. Replaced by change 3 (pending). The sign-flip and Wilcoxon results remain in the report as descriptive numbers that cannot change a verdict. |

## Change 3 — binary per-scenario endpoints with exact/score methods (proposed in v0.4; NOT approved by the owner 2026-10-10; under review)

| | |
|---|---|
| **Date** | Proposed 2026-10-10. Not approved. |
| **What** | H1/H2: per-scenario "fully correct" (all gold nodes correct). H4: the same endpoint, non-inferiority margin δ = 0.05 on the difference in the proportion of fully-correct scenarios. H5a: per-scenario "falsely confident on ≥ 1 ambiguous node". H5b: per-scenario "falsely abstains on ≥ 1 determinable node", Supported if the exact Clopper–Pearson upper bound is < τ_FA = 0.15. An indicator is 1 when it holds in at least half of the scenario's common repeats. Tests: exact McNemar (Holm over the same 5 tests). CIs: Newcombe hybrid score (method 10) for paired differences, Clopper–Pearson for H5b. |
| **Why valid** | For a paired binary outcome, "both methods equally likely to be 1 in a scenario" makes d_s ∈ {−1, 0, 1} exactly symmetric, so the exact test needs no extra assumption. Simulated false-support rates were at or below nominal under every null tried, including the all-or-nothing structure (Appendix C). Newcombe coverage was 94–99%; H4 false support at the margin 1.9–2.6% (nominal 2.5%); H5b 1.1%. |
| **Cost** | Partial credit is ignored for the verdicts (node-level accuracy and rates stay as descriptive results), and power is lower. |
| **What changes in D1/D2** | D1 and D2 were approved for node-level quantities. Under S1, τ_FA = 0.15 bounds the **proportion of scenarios** with any false abstention (stricter: one wrong abstention counts the whole scenario), and δ = 0.05 is a margin on the **proportion of fully-correct scenarios** (3 of 63). The owner must approve these readings explicitly. |
| **Evidence inspected** | Simulations only. |

**Owner response (2026-10-10).** Not approved. Asked for: the cause of the 2.6% H4 rate, an expanded simulation
(edge cases, clustering, prevalence, both directions), comparison with credible alternatives, and explicit
original-vs-proposed estimands. Done in `DECISION_REPORT_S1_S4.md`. Findings that bear on this change: (i) the 2.6%
came mainly from an implementation bug (uncorrected Newcombe correlation term, up to 8.6% false pass), now fixed;
(ii) corrected Newcombe still reaches 3.8%, Tango 3.0%; (iii) the binary endpoint favours a method with clustered
errors even at equal node-level accuracy (up to 98% "Supported"). No D1/D2 or hypothesis change is in force.

## Change 4 — Newcombe paired interval corrected (implementation fix, 2026-10-10)

| | |
|---|---|
| **What** | `stats.newcombe_paired_ci` used ψ = (ad − bc)/√P. Newcombe's paired method 10 (as implemented in contingencytables 3.1.0) uses ψ = (A − N/2)/√P if A > N/2, 0 if 0 ≤ A ≤ N/2, A/√P if A < 0, and 0 if any margin is 0. Fixed to the published form. |
| **How found** | External verification requested by the owner (S3). `Epi::ci.pd`, the first suggested reference, turned out to compute an unpaired interval; contingencytables provided the paired one. |
| **Evidence** | 958 tables, max difference 6e-16 after the fix; `tests/test_reference_r.py`. |
| **Effect** | The uncorrected interval was too narrow for positively correlated pairs: false pass at the H4 margin up to 8.6% (simulated). No experimental data existed. |

## Change 5 — confirmatory verdicts replaced by descriptive estimates (provisional owner decision S1 = D, protocol v0.6)

| | |
|---|---|
| **Date** | 2026-10-10. Provisional; to be confirmed by the owner before freezing. |
| **Decided by** | The owner (S1 = D, S2, S3, S4). |
| **What** | H1, H2, H4, H5a, H5b are no longer tested. They are kept as directional expectations stated before the run and answered by node-level estimates: means and paired differences with 95% t-intervals (H1, H2, H4); counts and rates without intervals (H5a, H5b). No Supported/Contradicted verdicts, no p-values, no multiplicity adjustment. Scenario-level binary results are secondary and printed with a clustering caution. D1 and D2 keep their approved node-level meaning and are reported only as reference lines. |
| **Why** | No procedure examined was both calibrated and able to answer the approved node-level questions at n = 63 / 11: node-level tests and intervals over-rejected under the plausible error structure (H4 up to 4.0%, superiority tests up to 10.9% one-directional); binary endpoints were calibrated but answer a different question that rewards clustered errors (up to 98% "Supported" at equal node accuracy); finite-sample-valid bounds had no power. |
| **Evidence inspected** | Simulations and implementation checks only (`DECISION_REPORT_S1_S4.md`). No experimental data. |
| **Implications** | The thesis reports this run as descriptive by design and cannot claim superiority, non-inferiority or threshold compliance with controlled error rates. Confirmatory claims, if wanted, require a separate, newly pre-registered study on new scenarios, designed after this run (protocol §2, "Future confirmatory design"). Change 3 (binary endpoints) is not adopted. |
