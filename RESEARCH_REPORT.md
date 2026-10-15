# Predictive AI for India's Economy and Government Policy

**Student:** Sundram Awasthi · M.Tech CSE (2026–28) · GLA University, Mathura
**Report date:** 15 October 2026 · **Status:** working plan, provisional until the supervisor approves it

---

## 1. Introduction

India's economy changes every month. Food and fuel prices, inflation and RBI decisions all move, and many decisions depend on what happens next. AI can help forecast these outcomes, but most forecasting systems have four weaknesses:

1. They predict from **past numbers only** and ignore news and reports that arrive every day.
2. When they do use news, they turn it into **one mood score**, so nobody can see *which* news changed the forecast.
3. They do not decide **when a forecast should change**. They either never update or update on everything.
4. They rarely show **how sure** they are, and they never say *"I don't know."*

Our research builds and tests **Reflica India**, one AI forecasting system developed in three stages:

| Stage | Title (provisional) | Main question |
|---|---|---|
| **Minor Project 1** | Reflica India: Evidence-Aware Economic Forecasting and Forecast Revision | Can dated evidence and careful revision improve next-month CPI inflation forecasts? |
| **Minor Project 2** | Honest Forecasting of India's Policy Decisions: Calibrated Probabilities and Abstention | Can AI give reliable probabilities for policy decisions and know when **not** to predict? |
| **Final thesis** | Honest AI Forecasting of India's Economic and Policy Events: Calibrated Probabilities, Abstention and Live Evaluation | Can we combine both into one honest, tested forecasting framework? |

**Our approach:** collect dated data → an LLM **extracts** claims (it never makes the forecast) → a numeric model forecasts → a rule decides **revise or keep** → every step is logged → results are compared with baselines in a fair, time-ordered test.

---

## 2. Minor Project 1: Evidence-Aware CPI Forecasting and Revision

**Period:** January–May 2027

### 2.1 What it is

A system that predicts **India's all-India combined CPI inflation (year-on-year) for the next month**, giving:
- a forecast number;
- a prediction range;
- the evidence behind the forecast;
- a log of every revision and why it was made.

**Why CPI first:**
- MoSPI publishes it every month on a fixed date.
- There are many years of data for testing.
- Food, fuel, monsoon and policy news affects it every day.

The method is **general**: it can later be applied to WPI, IIP, GDP or RBI decisions. The new CPI series (base 2024=100, from Feb 2026) will be handled carefully.

### 2.2 Problems we are solving

1. Numeric models ignore new reports and news.
2. News-based models give no traceable, source-linked evidence.
3. Forecasts are either **too rigid** (they ignore important news) or **too reactive** (they change on weak news).
4. Forecasts give no reliable uncertainty range.
5. Many published results suffer from **leakage**: the model sees future information.

### 2.3 Research papers we are reading

We reviewed **37 papers**: 13 in full text and the rest from abstracts or our notes. All bibliographic details were checked (`research/forecast/VERIFICATION.md`). The most important ones:

| Group | Key papers | What we learned |
|---|---|---|
| **India CPI (numbers)** | Sarveswararao & Ravi (IEEE SSCI 2020); Pratap & Sengupta (RBI 2019); Singh & Bhoi (RBI 2022); Mohan et al. (RBI Bulletin 2025); Mahajan & Srinivasan (CAFRAL) | Simple models and simple averages are hard to beat. Test periods are very short (6 months to 6 quarters). No significance tests. 1-month-ahead forecasting is hard. |
| **India news → inflation** | Pratap, Ranjan, Kishore, Bhoi (RBI 2021, food news); Banerjee et al. (2021); Das & Das (2024) | News helps, but it is reduced to **one daily sentiment index** that is always added to the model. There is no revision decision and no uncertainty. |
| **News indices abroad** | Kang et al. (IEEE TBD 2025, Korea); InflaBERT (US); PIER (Thailand); Russia; Philippines; China | The same pattern: one combined index, small or untested gains. |
| **LLM forecasting** | From News to Forecast (NeurIPS 2024); ChatMacro (SF Fed 2026); Fang et al. (2024); STCInterLLM (IEEE TCYB 2025); TimeRAG | LLMs predict numbers poorly. Real-time LLM forecasts are **stale**. News to Forecast's "reflection" only changes news selection **during training**. Unfiltered news made forecasts worse. |
| **Event graphs** | STEM (IEEE ICKG 2023); IBM news-event toolkit (IJCAI 2022) | Good designs for storing events (actor, time, impact), but **never used to forecast**. |
| **Revision** | O'Connor et al. (IJF 2000); Goodwin (2000); stability metric (2026) | Updating helps only sometimes, and people make **unnecessary changes**. This supports selective revision. |
| **Leakage** | Gao, Jiang, Yan (lookahead test); ChronoBERT; Srivani et al. (an example of leakage) | LLMs can "remember" outcomes; a test (LAP) can detect this. |

### 2.4 Gaps we found

| Gap | Evidence |
|---|---|
| **G1.** News is used as **one index**, not as separate dated claims with sources | RBI 2021, Kang 2025, InflaBERT, Das & Das |
| **G2.** No system decides **at forecast time whether to revise** an issued forecast | All 5 full-text priority papers. News to Forecast's reflection is training-time only. |
| **G3.** No comparison of **update policies** (never vs always vs selective) | None of the papers read |
| **G4.** No source **reliability or novelty** checks on evidence | News to Forecast lists reliability only as future work |
| **G5.** Weak evaluation: short tests, no significance tests, leakage, no intervals | Pratap & Sengupta, Singh & Bhoi, RBI 2021, Srivani 2026 |

**Honest caution.** This gap is **provisional**. The nowcasting literature (Bańbura, Giannone, Reichlin; Bańbura & Modugno) already revises forecasts and explains each revision, but it does so **mechanically on every new data release**. Our difference is **selective, text-evidence-gated revision**. These papers, plus Mohan 2025, O'Connor 2000 and Das & Das 2024, must still be read in full.

### 2.5 How Minor 1 fills the gaps

| Gap | Our answer |
|---|---|
| G1 | The LLM extracts **separate claims** (item, direction, size, region, date, source) into an evidence graph |
| G2 | A **revision rule** checks novelty, reliability, relevance and strength, then revises or keeps the forecast |
| G3 | We test **never-update vs always-update vs evidence-aware** at the same horizons |
| G4 | Reliability and novelty scores are part of the rule |
| G5 | Walk-forward backtest, Diebold–Mariano tests, prediction intervals, strict evidence cutoffs, a lookahead-bias check |

### 2.6 Objectives

1. Build a reproducible next-month CPI forecasting baseline.
2. Build a point-in-time (dated) dataset of numbers and news.
3. Extract source-linked claims with an LLM into an evidence graph.
4. Design and test an evidence-aware revision rule.
5. Show whether it beats never-update and always-update, with honest reporting.
6. Give validated prediction intervals.
7. Build a dashboard that shows forecasts, evidence and revisions.

### 2.7 Features

| # | Feature | Required? |
|---|---|---|
| 1 | Numerical forecasting engine (naive, SARIMA, XGBoost, simple-average combination) | ✅ |
| 2 | Multi-source, time-stamped data (CPI, food/fuel prices, DCA retail prices, news) | ✅ |
| 3 | Evidence intelligence and evidence graph (the LLM extracts only) | ✅ |
| 4 | Forecast uncertainty (prediction intervals and coverage) | ✅ |
| 5 | **Smart forecast revision (main contribution)** | ✅ |
| 6 | What-if scenarios | Optional |
| 7 | Experimental evaluation (walk-forward backtest) | ✅ |
| 8 | Reflica India dashboard (Flutter web/Android) | ✅ |

### 2.8 Methodology

1. **Define the target.** All-India CPI-C y-o-y, next month. Each forecast records its **creation date, evidence cutoff, target month and expected release date**.
2. **Collect data.** MoSPI CPI (old and new base), DCA retail prices, fuel, rainfall, exchange rate; dated news from public sources. Store the publication time of every item.
3. **Baselines first.** Random walk, SARIMA, XGBoost, and an **equal-weight combination of a fixed model set** (lessons from the RBI papers).
4. **Claim extraction.** The LLM uses step-by-step prompts and outputs: item, direction, size, region, date, source, source type. Each claim is checked against its article (faithfulness check).
5. **Revision rule.** At fixed checkpoints before the CPI release, score new claims (novelty, reliability, relevance by CPI weight, strength). Revise only if the score passes a threshold **set on training years**. Revisions are bounded and logged.
6. **Walk-forward backtest.** Replay month by month using only past information. Compare:
   - never update;
   - always update;
   - evidence-aware;
   - an "index" baseline (lexicon sentiment, as in RBI 2021).
7. **Metrics.**
   - MAE and RMSE.
   - Diebold–Mariano significance tests.
   - Interval coverage and width.
   - Number of revisions and the share of revisions that moved toward the outcome.
8. **Leakage checks.**
   - Strict cutoffs.
   - A LAP-style memory test (Gao et al.).
   - A post-training-cutoff test window (2024–26).
9. **Live trial (supplementary).** Save forecasts before each release and score them afterwards.

**Tools:** Python (pandas, statsmodels, XGBoost), a small open or free-tier LLM, Firebase (free Spark plan), Flutter.

---

## 3. Minor Project 2: Honest Forecasting of Policy Decisions

**Period:** after Minor 1

### 3.1 What it is

Extend Reflica from **numbers** (CPI = 4.8%) to **decisions** (RBI repo rate: cut / hold / hike). It gives **probabilities** (e.g. hold 60%, hike 25%, cut 15%) and **abstains** ("not enough evidence") when it should. It starts with **RBI repo-rate decisions**; GST, Budget or MSP come only if time allows.

### 3.2 Problems we are solving

1. AI gives confident answers without proving its confidence is correct (**no calibration**).
2. AI never says *"I don't know"* (**no abstention**).
3. LLM forecasts may use memorised outcomes (**leakage**).
4. Almost no AI forecasting work covers **Indian policy events**.

### 3.3 Research papers (initial list; literature review still to be done)

| Paper | Relevance |
|---|---|
| ForecastBench (Karger et al., ICLR 2025) | Leakage-free scoring of AI forecasts; experts still beat LLMs; US-focused, yes/no only |
| ChatMacro (SF Fed 2026) | LLM forecasts look good on past data but fail in real time |
| Gao et al. (lookahead bias) | Memorisation test, reused here |
| LLM event-forecasting papers from our earlier list (conflict outcomes, MENTOR, FinPulse) | No probabilities, no abstention, no India |
| To read | Calibration methods (Platt, isotonic, conformal); selective prediction / risk-coverage; RBI policy-prediction studies |

### 3.4 Gaps

1. Probabilities are rarely **checked for calibration** (Brier score, ECE).
2. **No abstention** in AI forecasting systems.
3. Little **live, pre-outcome** testing.
4. **India policy events** are missing.

*(These are provisional, based on our earlier 22-paper notes; a full review is needed.)*

### 3.5 How Minor 2 fills the gaps

- Every forecast is a **probability over clear outcomes**.
- **Calibration:** reliability plots, Brier score, ECE, and Platt or isotonic correction.
- An **abstention rule** based on weak, conflicting or few sources and low model agreement, reported with **coverage vs error**.
- The **evidence graph and revision log** from Minor 1 are reused.

### 3.6 Objectives

1. Build an RBI policy-event dataset with dated evidence.
2. Produce probability forecasts that beat base-rate baselines.
3. Show the probabilities are calibrated.
4. Show that abstention reduces confident errors without abstaining too often.

### 3.7 Features

1. Policy-event forecasting (RBI first).
2. Probabilistic predictions.
3. Probability calibration.
4. Abstention ("I don't know").
5. Evidence graph and revision (reused from Minor 1).
6. Evaluation against baselines.
7. Policy dashboard.

### 3.8 Methodology

Define the event and its outcomes → collect dated evidence for each past meeting → classifier plus LLM-extracted evidence → calibrate on held-out events → apply the abstention rule → chronological testing → Brier score, ECE, risk–coverage curve → compare with base rates.

---

## 4. Final Research (Thesis)

### 4.1 What it is

Combine the **validated** parts of Minor 1 and Minor 2 into one framework for **honest AI forecasting** of India's economic and policy events. The framework should be traceable, revise carefully, be calibrated, abstain when needed and be tested live.

### 4.2 Problems we are solving

- Forecasts are not linked across economy and policy (an RBI decision affects borrowing, demand and inflation).
- Nobody forecasts the **effects** of an event, only the event itself.
- Most systems are never tested **live over a long period**.
- Failures are rarely studied.

### 4.3 Research papers

All Minor 1 and Minor 2 papers, plus:
- event and causal graph work (STEM, IBM toolkit, causal event mining, CausalFormer);
- From News to Forecast (reflection);
- live benchmarks (ForecastBench).

### 4.4 Gaps

1. No connected **economy + policy evidence graph** used for forecasting.
2. No tested **forward chain of effects** (event → consequences with probabilities).
3. Little **long-term live evaluation** of AI forecasts in India.
4. Little **failure analysis**: shocks, data revisions, conflicting reports.

### 4.5 How the thesis fills the gaps

- A connected graph of indicators, claims, policy events and targets, each link with a meaning and a source.
- Possible downstream effects, carefully separated from correlation.
- A long-term live forecast record.
- A systematic study of when and why the system fails.

### 4.6 Objectives

1. Integrate evidence-aware revision (M1) with calibration and abstention (M2).
2. Extend the evidence graph across economy and policy.
3. Run and publish a long-term live evaluation.
4. Explain *what* the system predicts, *why* forecasts change, *how reliable* they are and *when* they fail.

### 4.7 Features

1. Connected economic and policy evidence graph.
2. Potential downstream consequences.
3. Longitudinal live evaluation.
4. Reliability and failure analysis.

### 4.8 Methodology

Reuse the shared pipeline (collect → extract → forecast → check → revise or keep → evaluate). Add graph links between events and targets, propagate uncertainty along links, keep a dated public forecast log, and analyse errors by type of situation.

---

## 5. Current Status and Next Steps

| Done | Next |
|---|---|
| Project plan (`PROJECT_PLAN.md`) | **Guide approval** of the direction and title change |
| 37 papers reviewed; citations verified; 13 read in full | Full text: Bańbura et al. (nowcasting news), Mohan 2025, O'Connor 2000, Das & Das 2024 |
| Final table, review-paper draft v0.2 | Final research-gap statement, then update the review paper |
| Firebase (free plan) secured; homepage rebuilt | Test the homepage on the Mac, then the dashboard |
| — | Data collection and Python baselines (Jan 2027) |

**Key documents:**
- `PROJECT_PLAN.md`
- `research/forecast/FINAL_TABLE.md`
- `research/forecast/LEVEL2_READINGS.md`
- `research/forecast/VERIFICATION.md`
- `research/forecast/paper/REVIEW_PAPER_DRAFT.md`

*All titles, gaps and contributions are provisional until the literature review is complete and the supervisor approves them. No experimental results exist yet.*
