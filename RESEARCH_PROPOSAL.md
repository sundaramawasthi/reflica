# Research Proposal: Predictive AI for India's Economy and Public Policy

**Researcher:** Sundram Awasthi · M.Tech Computer Science and Engineering (2026–2028) · GLA University, Mathura
**Supervisor:** *(to be added)*
**Document date:** 16 October 2026
**Status:** Research proposal. No implementation, data collection or experiments have started; **no results are reported**. Minor Project 1's title is fixed by the student. Its scope, and everything about Minor Project 2, still need supervisor approval.

> **Evidence labels used below**
> - **[Verified]** supported by a paper we read in full or in key sections.
> - **[Search-level]** supported only by an abstract, project page or summary.
> - **[Proposed]** our planned design.
> - **[Hypothesis]** a claim that must be tested experimentally.
> - **[Open]** needs a decision or a check.
>
> **No novelty is claimed.** Every research gap below is a *candidate* until the literature review confirms it.

---

## Contents

1. [Research classification](#1-research-classification)
2. [Overall research problem](#2-overall-research-problem)
3. [Minor Project 1](#3-minor-project-1)
4. [Minor Project 2](#4-minor-project-2)
5. [Relationship between the projects](#5-relationship-between-the-projects)
6. [Key references](#6-key-references)

---

## 1. Research classification

| Level | Classification |
|---|---|
| **Research field** | **Predictive AI for India's Economy and Public Policy** |
| **Area** | Artificial Intelligence |
| **Subfield** | Machine Learning and Predictive AI |
| **Domain** | Indian economy and public policy: inflation and prices, official economic statistics, RBI monetary policy, Union Budget and government policy events |
| **Specific area** | Hybrid forecasting that combines numerical time-series models with evidence extracted by language models from dated news and official statements; and prospective, leakage-controlled evaluation of the accuracy and calibration of AI forecasts |

**Note.** The 14 October 2026 record listed the specific area as "agent-based event forecasting". That label fits Minor Project 2 better than Minor Project 1, so the final per-project wording is **[Open]** for the supervisor.

---

## 2. Overall research problem

India's economic and policy environment changes constantly. Inflation, food and fuel prices, industrial output, the exchange rate, RBI decisions and government policy all shape household and business conditions. AI forecasting systems that try to predict such outcomes face four challenges:

1. **Prediction:** using only the information available at the time of forecasting.
2. **Evidence:** showing which data and documents support or contradict a forecast.
3. **Revision:** deciding whether new information should change a forecast, and by how much.
4. **Uncertainty and honesty:** stating probabilities that can be trusted, and admitting when the evidence is not enough.

> **Overall research question.** Can combining historical economic data, information extracted from dated news and official statements, and machine learning improve the forecasting of Indian economic and policy outcomes, when evaluated fairly against real outcomes?

---

## 3. Minor Project 1

### 3.1 Title

**IndiaEconForecast / Reflica India: Hybrid AI Forecasting of Indian Economic and Policy Outcomes**

**Period:** January–May 2027. Feasibility work and the literature review run from October to November 2026.

### 3.2 Introduction

Minor Project 1 studies AI forecasting of India through **two connected but separately evaluated experiments** that run on shared infrastructure:

- **Part A: LLM forecasting benchmark.** Large language models give probabilities for about 160–250 objectively resolvable yes/no questions about Indian economic and policy events. Each question is fixed **before** its outcome is known. The forecasts are then scored against the official outcomes.
- **Part B: Numerical CPI forecasting with evidence-aware revision.** Statistical and machine-learning models forecast next-month Indian CPI inflation. We then test whether claims extracted from dated news and official releases add predictive value, and whether a simple, pre-specified rule for revising a forecast helps.

The two parts answer different questions with different metrics. **Their scores are never combined into one number.**

### 3.3 Problem statement

1. **Part A.** We do not know how accurate, or how well calibrated, current LLMs are when forecasting *Indian* events. Most forecasting benchmarks we found do not focus on India **[Search-level]**. LLM forecasts can also look correct only because the model memorised outcomes from its training data **[Verified: Gao et al.]**.
2. **Part B.** Numerical CPI models use past numbers well, but they do not directly use newly published text. Systems that do use text usually turn it into one aggregate index, or let the AI decide freely whether to update. They rarely test, under strict time controls, **when** new evidence should change a numerical forecast **[Verified: Pratap et al. 2021; Das & Das 2024; Forecast-Dojo]**.

### 3.4 Motivation

- **Trust:** an AI forecast is useful only if it is stated together with a measured record of how accurate and calibrated such forecasts have been.
- **India-specific evidence:** policymakers, researchers and businesses in India need testing on Indian data and Indian institutions, not only on US or European events.
- **Evidence that text can mislead:**
  - unfiltered news made forecasts **worse** in one study **[Verified: Wang et al. 2024]**;
  - text worsened some models for India inflation **[Verified: Das & Das 2024]**.

  How to use text is therefore an open, testable question.
- **Weak real-time LLM forecasting:** real-time LLM inflation forecasts have been found stale **[Search-level: ChatMacro]**, and in a live US test, CPI, PCE prices and retail sales accounted for 87% of LLM agents' shortfall against the professional consensus **[Verified: LiveMacroEval]**.

### 3.5 Real-life applications (potential)

| User | Possible use |
|---|---|
| Economic researchers and analysts | Inspect a forecast together with its evidence, and see what changed between versions |
| Policy and planning teams | Use a well-evaluated forecast as **one** input to planning and risk analysis |
| Businesses (retail, agriculture, finance) | Track food and fuel price pressure and policy-event probabilities |
| AI evaluation and auditing | Check whether a given AI model can be trusted for Indian forecasting questions |
| Education and journalism | Explain forecasts with sources, uncertainty and a public track record |

These are potential uses. The system will **not** replace official statistics or expert judgement, and its accuracy is unknown until it has been tested.

### 3.6 Literature summary and research gaps

**What already exists:**

| Area | Existing work | Reading level |
|---|---|---|
| LLM forecasting benchmarks | ForecastBench (dynamic benchmark of future questions; experts beat the best LLM); Forecast-Dojo (replayable event forecasting with dated news) | Abstract (ForecastBench); key sections (Forecast-Dojo) |
| Live LLM macro nowcasting | LiveMacroEval: LLM agents nowcast 16 **US** indicators, including CPI, hourly and live; updating is left to the LLM's judgement, with no explicit rule | Full text |
| Indian CPI forecasting | Mohan et al. 2025 (RBI): 216-model performance-weighted combination; Singh & Bhoi 2022; Pratap & Sengupta 2019 | Full text |
| Text and inflation (India) | Pratap et al. 2021 (news sentiment, food inflation: mixed results); Das & Das 2024 (headline words: helped one model, hurt others) | Full text |
| Text features (other countries) | Kalamara et al. (UK newspaper term counts help, especially in crises); Thorsrud (Norway topic factors) | Key sections; abstract only |
| Forecast updating | Nowcasting news decomposition (Bańbura et al.): automatic revision at every data release | Full text |
| Leakage | Gao et al.: LLMs memorise past outcomes; a lookahead-propensity test | Full text |

**Candidate research gaps (provisional, not proven):**

| # | Candidate gap | Supporting evidence | What could disprove it |
|---|---|---|---|
| **G1 (Part A)** | We found **no India-specific, prospective LLM forecasting benchmark** of economic and policy events with official resolution sources and calibration analysis | Our searches; ForecastBench and Forecast-Dojo focus on general or market events **[Search-level]** | A full-text check of ForecastBench, FutureX and MIRAI, or an Indian-venue search, finds such a benchmark |
| **G2 (Part B, narrowed v8)** | Updating forecasts with news (Thorsrud), attributing inflation-forecast revisions to new information (Modugno) and free LLM updating (LiveMacroEval) **already exist**. The candidate gap is narrower: whether **claim-level, source-linked news evidence plus a pre-specified, bounded revision policy** adds value for **Indian headline CPI y-o-y** beyond strong numeric baselines and simple text indices, tested against other update policies | LiveMacroEval, Forecast-Dojo **[Verified]**; Thorsrud WP 20/2016, Modugno WP 1324 **[Reported by user]** | A study combining claim-level news extraction with a tested revision policy (still to check: Thorsrud "Words are the New Numbers", focused search) |
| **G3 (Part B)** | Evidence on whether text adds value beyond numbers for **Indian CPI** is **limited and mixed** | Pratap et al. 2021 (mixed); Das & Das 2024 (mixed; single split, no significance tests) **[Verified]** | This is an empirical question. Any outcome, positive or null, is informative |

**Contradictory evidence we must respect:**
- LLMs often do worse than experts or markets.
- Memory and evidence ledgers do not reliably help.
- Text can hurt forecasts.
- Strong numerical combinations (Mohan et al.) set a high bar.

### 3.7 Issues and challenges

| Challenge | Why it matters |
|---|---|
| **Information leakage** | A forecast that uses information published after its origin, or an LLM that "remembers" the answer, overstates skill |
| **CPI series change** | The CPI 2024 = 100 base was introduced in Feb 2026 (reported), so the historical series must be linked carefully |
| **Release timestamps and data vintages** | We need to know exactly when each number was published, and its first-release value |
| **Horizon definition** | Draft checkpoints were really current-month nowcasts. We must choose genuine one-month-ahead forecasting or nowcasting **[Open]** |
| **News access and licensing** | Dated archives and terms of use limit the evidence we can store and process |
| **Few observations** | Monthly CPI gives few test points, and Part A questions are correlated |
| **Unresolvable or ambiguous questions** | These reduce the number of scored questions in Part A |
| **LLM extraction errors** | Wrong claims could cause wrong revisions |
| **API cost and model version changes** | These affect budget and reproducibility |
| **Over-scoping** | Two experiments in five months is demanding |

### 3.8 What we are adding (candidate contributions)

1. **Part A:** a prospective benchmark of Indian economic and policy questions, frozen before outcomes and resolved from official Indian sources, with LLMs compared with and without dated news against simple baselines **[Proposed]**.
2. **Part B:** a point-in-time evaluation of whether **claim-level** evidence from dated news and official releases adds value to numerical CPI forecasts **[Proposed / Hypothesis]**.
3. **Part B:** a minimal, **pre-specified and auditable revision rule** that logs every keep-or-revise decision with its evidence and reason, compared with simpler update policies **[Proposed / Hypothesis]**.
4. **Shared:** a reproducible, leakage-controlled forecasting record: timestamped data, an append-only forecast log and versioned prompts **[Proposed]**.

These contributions concern **evaluation and method testing**, not a claim of a new capability. Whether they are new depends on the gap checks in §3.6.

### 3.9 System architecture [Proposed]

```
 ┌──────────────────────────── DATA SOURCES ─────────────────────────────┐
 │ MoSPI CPI · RBI/FBIL · PPAC fuel · DCA prices · IMD · PIB · dated news │
 └───────────────────────────────────┬────────────────────────────────────┘
                                     ▼
             ┌──────────────────────────────────────────────┐
             │ F2  Timestamped multi-source data store       │
             │     (source, publication time, retrieval time,│
             │      vintage, point-in-time cutoffs)          │
             └───────┬───────────────────────────┬──────────┘
                     │                           │
                     ▼                           ▼
     ┌───────────────────────────┐   ┌──────────────────────────────┐
     │ F3 Evidence store / graph │   │ F1 Numerical forecasting     │
     │ LLM extracts claims:      │   │ engine: naive, ARIMA,        │
     │ quote, source, date,      │   │ XGBoost, combination         │
     │ indicator, direction      │   └──────────────┬───────────────┘
     └───────┬───────────────────┘                  │
             │                                      ▼
             │                       ┌──────────────────────────────┐
             ├──────────────────────▶│ F5 Revision rule (minimal):  │
             │                       │ keep or revise, with reason  │
             │                       └──────────────┬───────────────┘
             ▼                                      ▼
 ┌────────────────────────────┐      ┌──────────────────────────────┐
 │ PART A  LLM benchmark      │      │ PART B  CPI forecasts        │
 │ questions → 2–3 LLMs       │      │ + F4 intervals               │
 │ (no news / dated news)     │      │                              │
 └─────────────┬──────────────┘      └──────────────┬───────────────┘
               ▼                                    ▼
 ┌────────────────────────────────────────────────────────────────────┐
 │ Append-only forecast log → F7 evaluation (Part A and B SEPARATELY) │
 └───────────────────────────────────┬────────────────────────────────┘
                                     ▼
                 ┌─────────────────────────────────────┐
                 │ F8 Minimal dashboard (Flutter +     │
                 │ Firebase): scoreboard, forecasts,   │
                 │ evidence, revision history          │
                 └─────────────────────────────────────┘
```

**Technology [Proposed]:**
- **Python** for data, models, LLM extraction and evaluation.
- **Flutter + Firebase** (free Spark plan) for the dashboard.
- API keys are kept out of the client app.

**The eight features:**

| # | Feature | Priority |
|---|---|---|
| F1 | Numerical forecasting engine | Core |
| F2 | Multi-source, timestamped data | Core (shared) |
| F3 | Evidence intelligence and evidence graph | Core (simple initial schema) |
| F4 | Forecast uncertainty | Core: basic intervals and calibration; advanced methods if feasible |
| F5 | Smart forecast revision | Minimal prototype after the baselines; advanced version only if time allows |
| F6 | What-if scenarios | Optional extension |
| F7 | Experimental evaluation | Core |
| F8 | Reflica India dashboard | Core, deliberately minimal |

### 3.10 Methodology [Proposed]

**Part A: LLM forecasting benchmark**
1. **Question design:** 160–250 yes/no questions across statistics, prices, RBI, the Budget, and policy and infrastructure events. Each question has a written resolution rule, a named official source, a deadline and a resolution date. Questions are frozen before the first forecast.
2. **Forecasting:** 2–3 LLMs, each under Condition A (no news) and Condition B (news published before the forecast time). Every forecast records the model version, settings and a UTC timestamp, and is hashed and stored append-only.
3. **Baselines:** constant 0.5; historical base rate; a statistical baseline for numeric-threshold questions.
4. **Evaluation:**
   - Brier score and Brier skill score;
   - reliability diagrams (calibration) and log score;
   - results by question family, with cluster-bootstrap confidence intervals;
   - all invalid and unresolved questions reported.

**Part B: CPI forecasting and evidence-aware revision**
1. **Target:** all-India CPI (Combined) headline inflation, year-on-year, next month. Before freezing, we fix the horizon, the series linking and the release timestamps.
2. **Baselines:** naive/persistence, ARIMA/SARIMA, XGBoost (if the data allow), and a simple combination.
3. **Walk-forward evaluation:** at each forecast origin, use only data published by then. Never shuffle the data. The test period is not used for tuning.
4. **Evidence experiment:** extract claims (quote, source, publication time, indicator, direction), then compare a numbers-only model with numbers plus text features.
5. **Minimal revision experiment:** apply a pre-specified rule (keep, or a bounded revision) and compare it with never-update and text-always policies. Thresholds are tuned on validation data only.
6. **Metrics:**
   - MAE and RMSE;
   - Diebold–Mariano tests with a small-sample correction;
   - revision frequency, and how many revisions were helpful or harmful;
   - interval coverage, only if the intervals are implemented correctly.

**Leakage controls (both parts):**
- strict point-in-time cutoffs;
- each model's knowledge cutoff recorded;
- news restricted to items published before the forecast time;
- a lookahead-propensity check;
- prospective forecasting in Part A.

**Staged plan:**

| Stage | Dates | Output |
|---|---|---|
| Feasibility and literature review | Oct–Nov 2026 | Data, licence and budget checks; gap matrix; supervisor approval |
| Data and evaluation pipeline | Dec 2026 – Jan 2027 | Timestamped store; scoring; 20-question pilot |
| Baselines | Jan 2027 | Part A baselines; Part B walk-forward results |
| Experiments | Jan–Apr 2027 | Part A live forecasts; Part B baseline analysis |
| Evidence integration | Feb–Mar 2027 | Claim extraction; text-feature test |
| Minimal revision experiment | Mar–Apr 2027 | Revision results, or a documented reason why it was not feasible |
| Dashboard and report | Apr–May 2027 | Minimal dashboard; final report |

**Go/no-go checkpoints:**
- at least 120 questions catalogued by 31 Dec 2026;
- at least 150 frozen by 31 Jan 2027;
- at least 60% resolved by 15 Apr 2027.

If a checkpoint is missed, the scope is reduced; evaluation quality is not compromised.

### 3.11 Expected outcomes

1. A frozen Indian forecasting question set with LLM forecasts, baselines and a calibration report (Part A).
2. A point-in-time CPI dataset, baseline results and a text-vs-numbers comparison (Part B).
3. A minimal revision experiment with decision logs.
4. A minimal dashboard and a final report.

**Every hypothesis can fail.** LLMs may not beat the baselines, text may not help, and the revision rule may make no difference or make forecasts worse. All such results will be reported honestly.

---

## 4. Minor Project 2

> **Status: provisional.** The title, scope and literature review are not final; they depend on the Minor Project 1 results and supervisor approval. Its research gap is **not yet verified**.

### 4.1 Provisional title

**Honest Forecasting of India's Policy Decisions: Calibrated Probabilities and Abstention**

### 4.2 Introduction

Minor Project 1 predicts numbers (CPI inflation) and tests LLMs on yes/no events. Many important policy outcomes, however, are **choices between options**. Examples:
- Will the RBI **cut, hold or raise** the repo rate?
- Will the Budget announce a specified measure?

Minor Project 2 would build a system that gives **probabilities** for such outcomes, checks whether those probabilities are **calibrated** (does "70%" come true about 70% of the time?), and **abstains**, saying "not enough evidence", when it should not make a confident prediction.

### 4.3 Problem statement

AI systems can give confident answers about policy outcomes without any evidence that their confidence matches their real reliability. They may also answer when the evidence is weak or contradictory. Users then cannot tell which predictions to trust.

### 4.4 Motivation

- Policy decisions affect loans, prices and investment, so overconfident AI predictions can mislead.
- Calibration and abstention make AI forecasts **safer to use**: the system speaks only when it has reason to.
- Minor Project 1 will produce resolved forecasts and evidence infrastructure that can be reused here.

### 4.5 Real-life applications (potential)

- Probabilities of RBI policy outcomes for researchers, analysts and students.
- Risk planning for businesses exposed to interest-rate or policy changes.
- A tested "know when not to answer" mechanism for AI decision-support tools.

### 4.6 Research gaps (to be verified)

| # | Candidate gap | Status |
|---|---|---|
| **G4** | Calibrated, abstaining AI forecasts of **Indian policy decisions**, evaluated chronologically on held-out events | **Not verified.** Requires a review of RBI policy-forecasting literature, ForecastBench, LLM calibration work (e.g., BLF uses Platt calibration) and selective prediction |
| **G5** | Whether abstention reduces confident errors **without abstaining so often** that the system becomes useless (risk–coverage trade-off) in this domain | **Not verified.** Empirical question |

### 4.7 Issues and challenges

- **Few events:** the RBI MPC meets only about 6 times a year, so historical data are limited.
- **Class imbalance:** "hold" decisions dominate.
- **Policy regime changes:** past patterns may not hold.
- **Leakage:** later announcements must not enter earlier forecasts.
- **Calibration on small samples is unstable:** ECE is reported with caution.
- **Too much abstention** can make the system useless; coverage must always be reported.

### 4.8 What we would add (candidate contributions)

1. A point-in-time dataset of Indian policy decisions with the evidence that was available before each decision **[Proposed]**.
2. A calibrated probability model, compared with base-rate and statistical baselines **[Proposed / Hypothesis]**.
3. A pre-specified abstention rule based on uncertainty, evidence conflict, source coverage or model disagreement, evaluated with risk–coverage analysis **[Proposed / Hypothesis]**.

### 4.9 Architecture (outline) [Proposed]

```
Policy event definition (e.g. RBI: cut / hold / hike) + deadline
                 │
                 ▼
Point-in-time evidence (reused F2 + F3 from Minor 1)
                 │
                 ▼
Probability model (statistical / ML / LLM) ──▶ Calibration (validation data only)
                 │
                 ▼
Abstention rule ──▶ predict  OR  "insufficient evidence"
                 │
                 ▼
Chronological evaluation: Brier, reliability, risk–coverage
```

### 4.10 Methodology (outline) [Proposed]

1. Define each event, its mutually exclusive outcomes and its prediction deadline.
2. Build historical records using **only** information available before each decision.
3. Establish base-rate and statistical or classification baselines.
4. Produce a probability for each outcome.
5. Calibrate on validation data only, using a method suited to the small sample (e.g., Platt scaling or isotonic regression).
6. Define abstention using pre-specified signals.
7. Evaluate chronologically on held-out events with the Brier score, reliability diagrams and risk–coverage curves, reporting coverage and error together.

### 4.11 Relationship to Minor Project 1

Minor Project 2 would reuse the timestamped data store, evidence store, forecast log and evaluation code, **but only if** Minor Project 1 shows that they are reliable. It would not automatically reuse the CPI model or revision rule, because categorical policy decisions are a different problem.

---

## 5. Relationship between the projects

| | Minor Project 1 | Minor Project 2 |
|---|---|---|
| Output | Yes/no probabilities (Part A); CPI numbers (Part B) | Probabilities over policy outcomes, or abstention |
| Main question | How good are LLMs on Indian events? Does text evidence help CPI forecasts? | Can probabilities be calibrated, and can the system know when not to predict? |
| Main metrics | Brier and calibration (A); MAE and RMSE (B), reported separately | Brier, reliability, risk–coverage |
| Status | Title fixed; scope pending supervisor approval | Provisional |

The final M.Tech thesis is outside the scope of this document. It will be defined later from the evidence produced by both minor projects.

---

## 6. Key references

Reading levels: F = full text · K = key sections · A = abstract or search-level. Full citations are kept in `docs/research_archive/literature/VERIFICATION.md`. Details still marked "verify" there must be checked before academic submission.

1. Bańbura, M., & Modugno, M. (2010). Maximum likelihood estimation of factor models on datasets with arbitrary pattern of missing data. ECB Working Paper 1189. **F**
2. Bańbura, M., Giannone, D., & Reichlin, L. (2010). Nowcasting. ECB Working Paper 1275. **F**
3. Das, P. K., & Das, P. K. (2024). Improvement in inflation forecasting: Ensembling text mining with macro data in machine learning models. *International Journal of Economics and Finance*, 16(6), 92–101. DOI 10.5539/ijef.v16n6p92. **F**
4. Gao, Z., Jiang, W., & Yan, Y. (2025/26). Detecting lookahead bias in LLM forecasts. arXiv:2512.23847. **F**
5. Kalamara, E., Turrell, A., Redl, C., Kapetanios, G., & Kapadia, S. Making text count: Economic forecasting using newspaper text. Bank of England SWP 865 (2020); *Journal of Applied Econometrics* (2022). **K**
6. Karger, E., et al. (2025). ForecastBench: A dynamic benchmark of AI forecasting capabilities. ICLR 2025. **A**
7. Mohan, R., Hasan, S., Roy, S., Sarkar, S., & John, J. (2025). Predicting CPI inflation in India: Combining forecasts from a "suite" of statistical and machine learning models. *RBI Bulletin*, 25 June 2025. **F** (article text)
8. Murphy (2026). Agentic forecasting with structured linguistic beliefs (BLF). arXiv:2604.18576. **K**
9. Pratap, B., Ranjan, A., Kishore, V., & Bhoi, B. B. (2021). Forecasting food inflation using news-based sentiment indicators. *RBI Occasional Papers*, 42(2). **F**
10. Pratap, B., & Sengupta, S. (2019). Macroeconomic forecasting in India: Does machine learning hold the key? RBI WP 04/2019. **F** (conference draft)
11. Singh & Bhoi (2022). Inflation forecasting in India: Are machine learning techniques useful? *RBI Occasional Papers*, 43(2). **F**
12. Thorsrud, L. A. Words are the new numbers: A newsy coincident index of the business cycle. *Journal of Business & Economic Statistics*, 393–409. **A**
13. Wang, X., Feng, M., Qiu, J., Gu, J., & Zhao, J. (2024). From news to forecast. NeurIPS 2024. **F**
14. Ye et al. (2026). Forecast-Dojo: Replayable environments for benchmarking and training LLM forecasting agents. arXiv:2609.28876. **K**
15. Zhao, X., Zhang, R., Ye, L., Cao, R., Xie, P., & Chava, S. (2026). Can LLMs take the pulse of the economy? A real-time evaluation of LLM nowcasts on macroeconomic indicators (LiveMacroEval). arXiv:2608.30110v1. **F**
16. Alam, Boyle, Li, & Sekhposyan (2026). ChatMacro: Evaluating inflation forecasts of generative AI. FRB San Francisco WP 2026-04. **A**

The research-gap matrix, with problem, data, method, baselines, findings and limitations for each paper, is in `research/forecast/RESEARCH_GAP_MATRIX.md`.
