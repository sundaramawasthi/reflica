> **Archived 15 Oct 2026:** this is the interim benchmark-only Minor 1 plan, kept word for word below this note. It was replaced by the **safer-merge** plan in `../../../MINOR1_PLAN.md` (Part A benchmark + Part B CPI). Its benchmark detail is carried into Part A of the new plan.

# Minor Project 1 — Authoritative Plan

> **INTERIM (15 Oct 2026):** this is the current *working* Minor 1 plan until the user supplies the final authoritative plan, which will **replace this file**. Titles and decisions: `docs/research_archive/DECISION_RECORD.md`.
> Any other document that describes a different Minor 1 (for example CPI evidence-aware revision) is **superseded or deferred** and is kept in `docs/research_archive/superseded_plans/`.
> **Adopted:** 15 October 2026 (student's decision). **Supervisor approval: PENDING.**
> **Labels:** [V] verified in repo or sources · [R] reported / search-level · [P] proposed · [H] hypothesis · [U] unresolved / needs a decision.

## 0. Titles and status

| Item | Value |
|---|---|
| **University title on record** | **AI-Powered Research Knowledge Graph and Change Impact Analysis System**. This stays the official title until the supervisor and the university approve a change [V, per student] |
| **Proposed Minor 1 title (provisional)** | **How Well Can Language Models Forecast India? A Prospective Benchmark of Indian Economic, Infrastructure and Policy Events** [U] |
| Long-term vision | *Honest AI Forecasting of Indian Events*: calibrated probabilities, abstention, evidence-aware revision, downstream impact analysis (future work; §13) |
| Period | Question catalogue from **December 2026**; Minor 1 evaluation **January–May 2027** (subject to GLA rules) |
| Code status | Flutter/Firebase shell only; **no forecasting code, data or experiments yet** [V] |

## 1. Research question

**Primary RQ.** How accurate and how well calibrated are current LLMs at forecasting resolvable Indian economic, infrastructure and policy events, compared with simple statistical and base-rate baselines, under prospective, leakage-free evaluation?

**Secondary RQs [H]:**
1. Does giving the model dated news, published before the forecast time, improve its Brier score?
2. Do models perform worse on Indian questions than on matched Western questions? *(exploratory; D5)*
3. Which question families (statistics, prices, RBI, budget, elections, infrastructure, policy) are hardest?
4. Where a probability conversion is documented in advance, how do LLMs compare with official Indian forecasts (RBI projections, IMD category probabilities)? *(deferred by D3 unless the conversion is documented)*

## 2. Scope and exclusions

**In scope [P]:**
- binary (Yes/No) questions about Indian events with a named official resolution source;
- 2–3 existing LLMs (D4);
- two information conditions;
- simple baselines;
- prospective forecasting from Dec 2026 to Apr 2027;
- scoring and calibration analysis;
- a scoreboard view, if time allows.

**Excluded from Minor 1:**
- building a custom forecasting agent;
- abstention policies;
- evidence-aware forecast revision (the **CPI revision-gate study is deferred**; see `docs/research_archive/superseded_plans/README.md`);
- impact or consequence chains;
- numeric-interval forecasting;
- free-form chatbot;
- predicting every Indian event.

CPI appears **only as one question family** (threshold questions with a statistical baseline). There is no revision experiment.

## 3. Research gap and related-work verification

**What exists [V/R]:**
- **ForecastBench** (Karger et al., ICLR 2025): a dynamic, prospective LLM forecasting benchmark with time-series-generated questions [R; identity verified].
- **FutureX** (live agent benchmark), **MIRAI** (international events from GDELT) [R].
- **LiveMacroEval** (Zhao et al. 2026): live LLM nowcasts of 16 **US** macro indicators [R, search-level].
- **Forecast-Dojo** (Ye et al. 2026): replayable event forecasting [V, key sections].
- **ChatMacro** (2026): real-time LLM inflation forecasts were stale [R].

Benchmarks, calibration, abstention, live evaluation and event forecasting are therefore **not novel by themselves**.

**Candidate gap [U]:**
- No **India-specific** prospective LLM forecasting benchmark was found in our searches (search-level, not exhaustive).
- The candidate contribution is:
  - India coverage built from official Indian sources;
  - official-forecast baselines where these can be converted;
  - a matched India-vs-West comparison;
  - a public, reproducible dataset.

**Verification tasks before claiming the gap:**
1. Read the full texts of ForecastBench, FutureX and MIRAI, and record their geographic coverage.
2. Run a targeted search for India-focused forecasting benchmarks and datasets, including in Indian venues.
3. Read the LiveMacroEval full text (positioning only).
4. Record the outcome in `docs/research_archive/literature/VERIFICATION.md`.

## 4. Questions: selection and resolution rules

**Families and estimated counts, resolving by about 15 May 2027 [P/H]:**

| Family | Examples | Estimate |
|---|---|---|
| Monthly official statistics | CPI headline and food, WPI, IIP, core sector, GST collections, trade deficit, PLFS unemployment vs a threshold | 40–80 |
| Prices and markets (month-end) | Nifty 50, INR/USD (RBI reference rate), Delhi petrol price, gold | ~20 |
| RBI | MPC decisions in the window (dates **[U] verify**) | ~9 |
| Union Budget 2027-28 | Fiscal deficit target, capex, tax changes (date **[U] verify**) | ~10 |
| Elections | State elections in the window (**[U] which, when**) | 0–20 |
| Infrastructure / climate | Peak power demand (Grid-India/CEA), reservoir storage (CWC), IMD rainfall categories | 20–30 |
| Policy / geopolitics | Bills passed, scheduled agreements, notified rules | 15–25 |
| Matched Western set | Same indicator types (US/UK) | Pilot 4–6 (D5); full set 30–40 [P] |

**Realistic total:** about **160–250**. **300 is not realistic prospectively.** Many questions are correlated, so results are reported by family with cluster-bootstrap CIs.

**Rules (record details in `research/forecast/PILOT_PROTOCOL.md`, the single source for formats):**
1. Every question has a binary outcome, a written resolution rule, a **named official resolution source**, a forecast deadline and a resolution date. The deadline must come before resolution.
2. Reject questions that are ambiguous, trivial (threshold too close to or too far from the last value, under a pre-set rule), duplicated or unresolvable. Log the rejection rate.
3. Template-generated candidates (A2 generator) pass the same checks as hand-written ones. A sample is reviewed by hand.
4. A definition is **frozen before its first forecast**. It is never edited afterwards; a correction gets a new ID and the old one is kept.
5. If the source is unavailable or the outcome is genuinely ambiguous, the question is marked **invalid** under a pre-written rule. An answer is never forced.

## 5. Data sources and timestamping

**Sources (official first) [P; each calendar U until verified]:**
- MoSPI (CPI, IIP, PLFS);
- DPIIT (WPI);
- Ministry of Finance (GST, Budget);
- RBI / FBIL;
- NSE;
- Grid-India / CEA;
- CWC;
- IMD;
- ECI;
- PIB / Gazette;
- for the Western set: BLS, ONS, FRED.

**Timestamping (D6, D7, D9):**
- append-only JSONL;
- UTC timestamps;
- a record hash for each record;
- a frozen `question_set` manifest before any forecast;
- same-day commits;
- an external timestamping service only after it has been evaluated;
- late forecasts are kept, marked `late`, and excluded from on-time scoring.

## 6. Models, information conditions and baselines

- **Models:** 2–3 accessible LLMs (D4). Record model version, settings and knowledge cutoff. Cache outputs.
- **Condition A (no news):** the question plus its stated baseline information.
- **Condition B (dated news):** the same, plus news **published before the forecast time**. Record sources and retrieval time.
- **Lead times:** fixed (e.g., about 14 days and about 3 days before the deadline) [P]. The primary leaderboard uses the latest eligible on-time forecast (D1).
- **Baselines:**
  - constant 0.5;
  - historical **base rate** for a documented reference class, with smoothing stated;
  - **persistence / statistical** baseline for numeric-threshold questions (e.g., SARIMA with its empirical error distribution, converted to a probability). The method is documented and validated before use (D2);
  - **official forecasts**, only with a conversion documented in advance (D3).

## 7. Evaluation and statistics

- **Accuracy:** Brier score, **Brier skill score** vs base rate, log score (clipped).
- **Calibration:** reliability diagram in wide bins with *n* shown; ECE reported cautiously; sharpness.
- **Comparisons:** paired, with **cluster-bootstrap CIs** (clustered by family and indicator) and paired permutation tests. Results by family. Cost per forecast.
- **Reporting:**
  - counts of resolved, invalid, late and failed questions;
  - null or negative results reported as found;
  - no accuracy shown for unresolved questions.

## 8. Leakage prevention and reproducibility

- **Prospective by design:** every forecast is made **at least 24 hours before** the earliest possible resolution. News in Condition B is restricted to articles published before the forecast time.
- Each model's knowledge cutoff is recorded.
- The **optional retrospective set** (questions resolved after the cutoff but before the forecast) is run **without web search**. It is reported **separately**, never mixed into prospective scores, and gets a lookahead-propensity check (Gao, Jiang & Yan).
- **Reproducibility:**
  - frozen prompts (versioned);
  - configs and seeds;
  - a cached raw output for every call;
  - a data manifest;
  - code and dataset released at the end (licence permitting).

## 9. Implementation architecture [P]

```
Official calendars + sources ─▶ question generator (A2) / hand catalogue ─▶ validation ─▶ frozen questions.jsonl
                                                                                              │
LLM runner (Conditions A/B, cached) ──▶ forecasts.jsonl ◀── baseline runner                  │
                                              │                                               │
                     resolution checker ─▶ resolutions.jsonl ─▶ scoring & reports ─▶ (optional) Firestore display ─▶ Flutter scoreboard
```

- **Python package** in `research/forecast/` (D8). Record formats are defined in `PILOT_PROTOCOL.md`. The first end-to-end milestone is in `research/forecast/MILESTONE_1.md`.
- **Flutter/Firebase:** the existing shell is kept. A Firestore display layer and its rules come **only after approval** (`docs/ARCHITECTURE.md`). API keys are never put in the client.
- **December pilot:** recorded by hand in JSONL before the backend exists (`PILOT_PROTOCOL.md`).

## 10. Milestones, budget and go/no-go

| Date | Milestone / gate | Go criterion | If no-go |
|---|---|---|---|
| 30 Nov 2026 | **G0** | Supervisor decision recorded; 2 or more models affordable; schema, scoring and baseline rules pre-registered; release calendar Dec 2026–May 2027 verified | Revise scope with the supervisor |
| 1 Dec 2026 | Pilot freeze | 20 questions + 4–6 Western pairs frozen and stamped | — |
| **31 Dec 2026** | **G1** | Pilot forecasts recorded correctly; **≥120 India questions catalogued** with resolution ≤ 15 May 2027 | Add the retrospective set; narrow to statistics + RBI |
| **31 Jan 2027** | **G2** | **≥150 India questions frozen**; ≥20 resolved and scored correctly; invalid/ambiguous rate < 10% | If fewer than 100 are feasible → fallback: retrospective post-cutoff India benchmark as the main study (leakage risk stated), or a narrowed numeric study decided with the supervisor |
| 15 Apr 2027 | G3 | ≥60% of frozen questions resolved | Analyse the available resolutions; report coverage |
| 31 May 2027 | Final | Report, dataset and code | — |

**Budget [U]:**
- set a monthly API cap before the pilot;
- estimate the cost of 2–3 models × about 250 questions × 2 conditions × 2 lead times;
- prefer free or low-cost models;
- open models still have compute costs.

## 11. Risks

| Risk | Response |
|---|---|
| Too few resolutions by May | G1/G2 gates; retrospective supplement |
| Correlated questions | Family-level results; cluster bootstrap |
| API cost | Cap; cache |
| Trivial or ambiguous questions | Difficulty filter; invalid rule |
| Web search reveals outcomes | Forecast-time rule; no search after the deadline |
| India and Western pairs not equivalent | Labelled exploratory (D5) |
| Novelty weaker than hoped | Positioned as an India coverage and evaluation contribution, not a new method |

## 12. Pending supervisor decisions

1. Whether the Minor 1 title changes from the title on record, and to what.
2. Approval of this benchmark as Minor 1, and deferral of the CPI revision study.
3. API budget and the model list.
4. Use of the retrospective post-cutoff set.
5. Optional human-forecaster comparison (consent / ethics).
6. Minor 2 direction (decided after Minor 1 results).

## 13. Future work (not Minor 1)

- **Minor 2 candidates:**
  - a calibrated forecasting agent with **abstention**;
  - calibrated probabilities for RBI policy decisions;
  - **evidence-aware forecast revision** (the deferred CPI study, whose protocol and literature are preserved in the archive).
- **Final project:** downstream **impact analysis** (event → consequences with probabilities). This may relate to the knowledge-graph / change-impact work in the title on record.
- Live, longer-term public forecast record.

## 14. Supporting documents (subordinate to this plan)

| File | Role |
|---|---|
| `research/forecast/PILOT_PROTOCOL.md` | Record formats, decisions D1–D9, pilot procedure (**single source for formats**) |
| `research/forecast/MILESTONE_1.md` | First backend milestone (one question end to end) |
| `docs/ARCHITECTURE.md`, `docs/UI_SPEC.md`, `docs/FIREBASE_SPARK.md` | App architecture, UI and Firebase |
| `docs/research_archive/literature/` (`FINAL_TABLE.md`, `VERIFICATION.md`, `LEVEL2_READINGS.md`, `LITERATURE_FORECASTING.md`, `LITERATURE_MATRIX.md`, `PAPER_REVIEWS.md`) and `docs/research_archive/research_gaps/CLOSEST_METHODS.md` | Literature record. Gap statements in these files about CPI revision concern the **deferred** study |
| `docs/research_archive/` | Research archive: decision record, literature, research gaps, superseded plans, project history |
