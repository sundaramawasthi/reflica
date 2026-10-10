# Decision report — S1 to S4 (2026-10-10)

For the owner. **No decision in this file is taken; nothing is frozen.** Protocol status: DRAFT v0.5, NOT FROZEN.
No model or API call was made. Raw outputs: `simulations/s1_study_output.txt`, `reference/`.

## 1. Verified vs simulated

| Item | How established | Status |
|---|---|---|
| Endpoint code = evaluator semantics | 145 cross-checks on gold input, 0 mismatches | **Verified (exact)** |
| Newcombe paired (corrected), Tango, Agresti–Min, Bonett–Price CIs; McNemar exact and mid-p; Clopper–Pearson; Wilson | Compared with R 4.3.3 + contingencytables 3.1.0 / base R on 958 tables (every table for N = 1, 2, 3, 5, 12; 400 random N = 63; 13 edge cases) and all k of 63; max difference ≤ 2e-15 (Tango 2.4e-8, R's root tolerance) | **Verified externally**; regression test `tests/test_reference_r.py` |
| `Epi::ci.pd(20, 12, 2, 16)` as a reference | Source read: `ci.pd` treats aa, bb, cc, dd as **two independent groups** (p1 = aa/(aa+cc), p2 = bb/(bb+dd)); its "method 10" is Newcombe's *unpaired* method | **Not a valid reference** for the paired interval (S3) |
| v0.4 Newcombe implementation | R comparison: v0.4 used the uncorrected correlation term; published method 10 uses ψ = (A − N/2)/√P for A > N/2, 0 for 0 ≤ A ≤ N/2 | **Bug found and fixed**; (20,12,2,16) now (0.05616, 0.32921) = R |
| Runner, gate, logging, validation, analysis | Offline tests with network blocked and pilot-response replay; 17 deliberate-bug checks | **Verified offline in the review container only** |
| Preflight on the intended machine | `preflight.py` written; run here passes (282 tests) | **Not done on the intended machine** |
| Type-I error, coverage and power of every candidate procedure | Monte Carlo (seeds fixed), `simulations/s1_study.py` | **Simulated only**; MC s.e. ≈ 0.16 points at 2.5% (10,000 sims), ≈ 0.11 (20,000) |
| That the simulated structures resemble the real experiment | Assumption | **Unverified** — the real error structure is unknown until data exist |

## 2. Why H4 reached 2.6%, and what the expanded study shows

**Cause.** Mainly the v0.4 bug: the uncorrected Newcombe interval is too narrow for positively correlated pairs. Over
the expanded grid (prevalence 0.5–1.0, within-pair dependence ρ 0–0.9, homogeneous or mixed scenario difficulty,
n = 63, true difference exactly at the margin) its false-pass rate reached **8.6%** (nominal ≤ 2.5%). The earlier
2.6% was one cell of that pattern plus Monte Carlo error (s.e. 0.25 points at 4,000 sims).

**H4 false pass at the margin (P(lower > −0.05) when the true difference is −0.05), worst cell per method:**

| Method | Worst false pass | Where | Typical | Note |
|---|---|---|---|---|
| Newcombe v0.4 (bug) | 8.6% | p 0.5, ρ 0.9 | 2.3–3.5% | withdrawn |
| Newcombe paired, corrected | 3.8% | p 0.5, ρ 0.9 | 0–3.4%; 0% at p = 1 | over nominal at moderate prevalence + strong dependence |
| **Tango score** | **3.0%** | p 0.5, ρ 0.3, mixed | 1.2–2.7% | best calibrated; lower power than Agresti–Min |
| Agresti–Min Wald | 4.4% | p = 1.0 | 2.4–4.4% | worst exactly where B5 is expected (high prevalence) |
| Bonett–Price Wald | 4.4% | p = 1.0 | 1.6–4.4% | same |
| Exact unconditional (Berger–Boos type) | ≤ 2.5% by construction | — | — | **not implemented or simulated**; feasible for one analysis (≈ 2,000 (b, c) pairs × nuisance grid) |

The other tail (false "Contradicted") was ≤ 2.7% for all methods. Power at p_B4b 0.9, ρ 0.6: P(Supported) when the
true difference is 0 was 0.22 (Newcombe, Tango), 0.32 (Agresti–Min); at +0.05: 0.71 (0.47 with mixed difficulty).

**Superiority tests (H1, H2, H5a), split by direction.** Null rejection per direction at α 0.05 (nominal 2.5%):
exact McNemar ≤ 1.7% (conservative everywhere), mid-p ≤ 2.4%, asymptotic up to 2.7% (n = 63) — under homogeneous,
heterogeneous, and "weak-null" (scenario-level asymmetry averaging to zero) structures. At n = 11 (H5a) all are far
below nominal; power with exact McNemar for a large effect: 12% (α .05), 2% (α .01). Power at n = 63 with 20%
discordance and a 0.8/0.2 split: exact 0.48, mid-p 0.57.

**H5b scenario-level.** Clopper–Pearson and Wilson give identical decisions at n = 63 (both pass only with ≤ 3
scenarios); false pass 1.1% at a true rate 0.15.

**Original node-level estimands (D in the study).** Coverage of the mean-difference CI over clustering patterns:
scenario t-interval 0.934–0.959, bootstrap-t 0.896–0.948, stratified percentile bootstrap 0.907–0.933. H4 false pass at
the margin: t-interval up to **4.0%**, bootstrap-t up to 4.6%, percentile up to 5.3%. The finite-sample-valid
empirical-Bernstein bound had coverage 1.000 and **zero power** at n = 63. Earlier: sign-flip on node-level means gave
10.9% one-directional false support (α .05) when B5's errors are all-or-nothing.

**Estimand divergence (E in the study) — the decisive finding for S1.** If B5 and a comparator have the **same
node-level accuracy** but B5's errors come all-or-nothing per scenario (as a deterministic pipeline's tend to), the
binary "fully correct" endpoint still favours B5 by +0.35, +0.22, +0.12, +0.03 at accuracy 0.80, 0.90, 0.95, 0.99, and
an H1-type comparison is "Supported" in **98%, 81%, 47%, 2%** of simulations. This is not a statistical error of the
binary method — it is what the binary estimand measures — but it means a binary-endpoint "win" can occur with no
per-node accuracy advantage. Any thesis claim from it must say "handles more scenarios completely", not "is more
accurate".

## 3. Unresolved statistical risks

1. **No procedure is both valid for the original node-level estimands and usable at n = 63 / 11.** Approximate methods over-reject by up to 1.6–2.8 points (H4) and much more for superiority tests under skew; valid bounds have no power.
2. **Binary endpoints change the question** and reward error clustering, which is B5's design. Statistically well calibrated (exact tests, Tango CI) but substantively favourable to B5.
3. **Every candidate's residual error points the same way** in the plausible structure (B5 all-or-nothing, comparators node-wise): toward B5.
4. **Simulated structures are assumptions.** Real error structures are unknown; the pilot (16 scenarios) could inform them, but using pilot outcomes to choose a test is itself a researcher degree of freedom and was not done.
5. **The scenarios are a fixed benchmark, not a random sample.** All inference treats them as exchangeable draws; generalisation beyond this benchmark rests on that assumption (and on the held-out set, if built).
6. **H5a power is very low** (≤ 11 scenarios): Inconclusive is the likely outcome even with a real effect.

## 4. Proposed S1–S4 decisions (options for the owner; my suggestion marked, not decided)

**S1 — confirmatory estimand and method.**

| Option | Estimand | Inference | Pros | Cons |
|---|---|---|---|---|
| **A** keep original (v0.3 node-level, D1/D2 as approved) | mean node correctness; pooled rates | scenario t-interval; sign-flip or t-test | answers the approved question | simulated over-rejection (H4 ≤ 4.0%; superiority far more under skew); verdicts favour B5 when errors cluster |
| **B** binary scenario-level (v0.4) | proportion of scenarios fully correct / with any false confidence / any false abstention | exact McNemar (or mid-p); **Tango** CI for H4 (not Newcombe); Clopper–Pearson for H5b | error rates ≈ nominal (Tango ≤ 3.0%, exact ≤ 1.7%) | different question; rewards clustered errors (98% "Supported" at equal node accuracy 0.80); lower power; changes D1/D2 |
| **C** both, conjunctive | node-level and binary | Supported only if both rules support | a B5 "win" must hold on both lenses | false support ≈ the node-level rate in the skewed case; more complex; still approximate |
| **D** descriptive-only | node-level (as approved) | estimates + t-intervals, no confirmatory verdicts; binary results and exact tests as supporting | honest about n = 63 / 11 and a fixed benchmark | weaker thesis claims; departs from "hypothesis verdicts" |

*My suggestion (owner decides):* **C or D**. B alone answers a question the thesis did not set out to ask and is
structurally favourable to B5; A alone over-claims under the most plausible error structure. If B or C is chosen, use
**Tango** for H4 (best calibrated) and either **exact McNemar** (guaranteed, conservative) or **mid-p** (closer to
nominal, not guaranteed). An exact unconditional H4 test can be implemented if strict ≤ 2.5% is required.

**S2 — estimands and thresholds (nothing changed silently).** See §5. *Suggestion:* keep D1/D2 as approved
(node-level). If any scenario-level rule is adopted, add it as a separately named secondary with its own threshold,
approved explicitly, rather than redefining D1/D2.

**S3 — Newcombe verification.** Externally verified against contingencytables 3.1.0 (R 4.3.3) after correcting the
correlation term; `Epi::ci.pd` is not a valid paired reference. *Proposed:* close S3 as verified; record versions
(R 4.3.3 from Ubuntu 24.04; Epi 2.47.1 Ubuntu r-cran-epi; contingencytables 3.1.0 and PropCIs 0.3.0 installed from the
GitHub CRAN mirror because CRAN is blocked here; MASS 7.3-60.0.1; boot 1.3-30). Optional: repeat `reference/refgrid.R`
on the intended machine with packages from CRAN.

**S4 — environment and freeze readiness.** Keep DRAFT. Run `python experiments/full_run/preflight.py report.json` on the
intended machine; it must pass before freezing. The review-container run (`reference/preflight_review_container.json`)
passed but **does not count**.

## 5. D1/D2 and each hypothesis — original vs proposed

Numbers: 63 scenarios; 230 gold nodes (3.65 per scenario); 211 determinable (3.35 per scenario); 19 ambiguous in 11 scenarios.

| | Original (approved D1/D2, v0.3) | Proposed v0.4 (option B) | Practical reading |
|---|---|---|---|
| **H1/H2** | mean per-scenario node correctness, B-B5 − B1/B2 > 0 | proportion of fully-correct scenarios, B-B5 − B1/B2 > 0 | node: "more nodes right on average"; binary: "more plan updates entirely right" |
| **H4 (D2)** | δ = 0.05 on mean node correctness | δ = 0.05 on proportion fully correct (≈ 3 of 63) | at accuracy 0.95 with independent errors, a node-level gap of 0.05 equals a fully-correct gap of ≈ 0.15; with all-or-nothing errors the two coincide. So binary δ 0.05 is **up to 3× stricter** than node δ 0.05 for scattered errors and equal for clustered ones |
| **H5a** | pooled false-confidence rate on 19 ambiguous nodes | proportion of 11 ambiguous scenarios with any false confidence | binary counts a scenario once however many nodes are wrong |
| **H5b (D1)** | τ_FA = 0.15 on false-abstention rate over 211 determinable nodes (≈ 32 nodes) | τ_FA = 0.15 on proportion of 63 scenarios with any false abstention (≈ 9 scenarios; passes only with ≤ 3 observed) | a node rate 0.15 spread one-per-scenario ≈ scenario rate 0.42 (1 − 0.85^3.35); clustered ≈ 0.15. Scenario-level 0.15 is **equal to or up to ≈ 2.8× stricter** |

**Threshold recommendation.** No change to D1 or D2 is recommended without a substantive reason. The numbers 0.05 and
0.15 were set for node-level quantities; carrying them to scenario level is not neutral. If a scenario-level H5b is
wanted, a defensible threshold comes from the use case ("at most 1 plan update in N needs an unnecessary human
check"), not from conversion: 0.15 means "≤ 15% of plan updates", which the owner should confirm as acceptable or
adjust explicitly. For a scenario-level H4 margin, 0.05 (≈ 3 scenarios) is strict; a margin derived from the node-level
δ under independent errors would be ≈ 0.15, which is lenient — neither is clearly right; the owner should set it from
what difference would matter to a user.

## 6. Remaining freeze blockers

1. **S1 decision** (owner) — and, if B or C, switch H4's interval to Tango in `analysis.py` (currently Newcombe) and re-run tests.
2. **S2 decision** on D1/D2 wording and any new thresholds (owner).
3. **Preflight on the intended machine** passes; its `report.json` and fingerprints are reviewed (owner).
4. **Environment lock** confirmed or regenerated on that machine (P3).
5. **Held-out set**: built and independently reviewed by 2026-10-24, or omitted and disclosed (D3/N2/N3); if built, the runner needs held-out loading (amendment before freeze).
6. **Final protocol text** updated to the chosen option, then the owner's explicit written approval to freeze.

## 7. Owner's provisional decisions (2026-10-10) and how v0.6 implements them

| Decision | Implemented in the proposal (not yet applied to the repository) |
|---|---|
| S1 = D, descriptive only | `analysis.py` rewritten: no verdicts, no p-values (structural test); node-level estimates with t-intervals; counts for H5a/H5b; scenario-level tables as secondary with caution; error patterns and RQ4 attribution |
| S2, D1/D2 unchanged at node level | reference lines only, labelled "orientation only"; protocol §2 states what each question can and cannot establish |
| S3 accepted provisionally | corrected Newcombe and reference tests kept; protocol Appendix D gives method, versions, cases, limitations; t quantile added to the reference checks |
| S4 DRAFT | protocol v0.6 still DRAFT / NOT FROZEN; freeze checklist unchanged except step 1 |
