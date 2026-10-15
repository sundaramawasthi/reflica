# Literature matrix for Minor Project 1 (Reflica India)

**Started:** 15 October 2026. **Status:** first pass, built from **abstracts, publisher records, preprint pages and reviews only**. No IEEE full text could be opened (no subscription; arxiv.org was also unreachable from the cloud session). Every "?" and every claim marked *(abstract)* must be checked in the full paper before it is cited.
**Plan this serves:** `../../PROJECT_PLAN.md`, Minor 1: dated, LLM-extracted, source-linked evidence used to **selectively revise** India's next-month CPI inflation forecasts, evaluated in a leakage-controlled backtest.

## How to read each paper (user's guideline, 15 Oct 2026)

Answer four questions:
1. What problem did the researchers solve?
2. What method did they use, and how did they evaluate it?
3. What limitation remains?
4. What exactly could Reflica India investigate that the paper did not?

Reading order inside a paper:
1. Abstract
2. Introduction and related work
3. Methodology (raw text, sentiment, extracted claims, retrieval, or a revision rule?)
4. Experiments (data, horizon, baselines, metrics, chronological test?)
5. Limitations and conclusion
6. References and citing papers (backward and forward)

Do not stop at IEEE: economics journals, central-bank papers and other CS venues matter as much.

### The 6 elements we test every paper against

| Code | Element |
|---|---|
| **E1** | India CPI inflation forecasting |
| **E2** | Dated, source-linked evidence extracted from text (claim level, not one aggregate score) |
| **E3** | A defined rule for whether new evidence justifies a forecast revision |
| **E4** | A revision history that explains why the forecast changed or stayed the same |
| **E5** | Fair comparison against never-update and alternative update strategies at equal horizons |
| **E6** | Leakage-controlled historical (walk-forward) evaluation |

If one paper already does most of E1–E6, the contribution must be narrowed or changed. If they appear only separately, the question is whether a principled integration adds measurable value.

---

## A. Papers the user assigned (read first)

### A1. Online News-Based Economic Sentiment Index
- **Reference:** Kang, Min, Cho, Ko, Kim, Choeh, Im. *IEEE Transactions on Big Data* 11(3):1464–1474, 2025.
- **Target:** an economic sentiment index (South Korea, ICT industry), not a CPI forecast *(abstract)*.
- **Inputs:** online news.
- **Method:** KoBERT relevance and sentiment scores, news clustered by category (with image clustering), combined by multi-criteria decision analysis into one index *(abstract)*.
- **Revision:** none described.
- **Traceability:** low. Articles are **aggregated into one index**, so individual claims and sources are lost.
- **Evaluation:** ? (check correlation with official indicators and the baselines).
- **Leakage controls:** ?
- **Limitation:** one aggregate score per period; Korea; not tested as a forecaster of inflation.
- **Reflica opportunity:** keep **claim-level, source-dated evidence** instead of one index, and test whether claim-level signals beat an aggregate sentiment index for India CPI (an ablation: index vs claims). → E2.
- **Elements covered:** none of E1–E6 (it is a building block for E2).

### A2. TimeRAG: Boosting LLM Time Series Forecasting via Retrieval-Augmented Generation
- **Reference:** Yang, Wang, Zheng, Jin. ICASSP 2025 (arXiv 2412.16643).
- **Target:** generic time-series benchmarks from several domains *(abstract)*.
- **Inputs:** numbers only; the retrieved "evidence" is **similar historical sequences**, not news.
- **Method:** sliding-window slices clustered with K-means into a knowledge base; similar sequences retrieved with Dynamic Time Warping and added to the LLM prompt; reported about **2.97%** average accuracy gain *(abstract)*.
- **Revision:** none; one-shot forecasts.
- **Traceability:** partial (which past sequences were retrieved), but no sources or dates of real-world evidence.
- **Evaluation:** standard benchmark datasets vs the original LLM forecaster; metrics ?.
- **Leakage controls:** ? (benchmarks are public and old; LLM memorisation not addressed in the summaries).
- **Limitation:** retrieval of patterns, not of new information; no economic text; no revision decision.
- **Reflica opportunity:** retrieval of **new, dated, source-linked evidence** and a test of **whether it should trigger a revision**. A TimeRAG-style "similar past months" retriever could be an extra baseline. → E2, E3.

### A3. Time-Series Large Language Models: a systematic review (IEEE Access, as cited)
- **Status:** the exact IEEE Access record was **not found** by search. Closest: Shi et al., "Large Language Models for Time Series Analysis: Techniques, Applications, and Challenges" (arXiv 2506.11040, IEEE template). Related surveys: Zhang et al., IJCAI 2024; Jin et al., arXiv 2402.03182.
- **Use:** background. Collect common datasets, evaluation practice, open problems and **temporal-leakage** discussion, and mine the references.
- **Action:** confirm the exact title, authors and DOI on IEEE Xplore before citing.

### A4. Causal Intervention Is What Large Language Models Need for Spatio-Temporal Forecasting (STCInterLLM)
- **Reference:** Li, Li, Li, Xu, Lin, Jiang. *IEEE Transactions on Cybernetics*, 2025, DOI 10.1109/TCYB.2025.3569333.
- **Target:** spatio-temporal forecasting (e.g. traffic-type data) *(abstract)*.
- **Method:** a causal-intervention encoder that corrects **spurious spatial correlations** in an adaptive graph; chain-of-action prompting to reduce **LLM hallucination**; a marker-alignment module *(abstract)*.
- **Revision / traceability / leakage:** not the focus.
- **Limitation for us:** not economic, no text evidence, no revision.
- **Reflica opportunity:** borrow the discipline of separating **useful predictive signals from spurious associations**. Every extracted claim's direction is a hypothesis, tested by ablation, not a cause. → supports E2 quality and the "what-if is not causal" rule.

---

## B. India CPI forecasting (domain baselines)

| # | Paper | Target / data | Method | Text? | Revision? | Evaluation note | Limitation → Reflica |
|---|---|---|---|---|---|---|---|
| B1 | **Das & Das (2024)**, *Int. J. of Economics and Finance*, "Improvement in Inflation Forecasting: Ensembling Text…" | India inflation; 3.9 million newspaper headlines, 2001–Jun 2023, turned into **monthly series** | ML with text-derived series | ✅ aggregate | ❌ | text **improved** forecasts vs numbers only *(abstract)* | **Closest India text paper.** Aggregated headlines, no claim-level provenance, no revision rule → Reflica tests claim-level evidence and selective revision. **Read in full first.** |
| B2 | **RBI Bulletin (Jun 2025)**, Mohan et al. | Headline CPI and CPI excl. food and fuel | Performance-weighted combination of statistical, ML and DL models | ❌ | ❌ | combination beats single models *(summary)* | Strong **official numeric baseline** to compare against; no text, no revision logic. |
| B3 | **IEEE WiSPNET 2024** (Amrita), Indian industrial workers' inflation | CPI-IW | LSTM, BiLSTM, XGBoost, RF (and a DWT-ARIMA-XGBoost hybrid in related work) | ❌ | ❌ | ? | Different CPI series (CPI-IW); numeric only. |
| B4 | **IEEE INOCON 2023** (Christ University), CPI prediction for India | CPI | Statistical vs LSTM variants | ❌ | ❌ | **statistical beat LSTM** on the small dataset *(record)* | Shows deep models are not automatically better → Reflica must include strong simple baselines. |
| B5 | **RBI Occasional Paper / study (2023)**, ML vs econometrics | India inflation, quarterly 1996–2022 | ANN, LSTM vs econometric models | ❌ | ❌ | mixed; ARIMAX best post-COVID in one report | Quarterly, numeric; evidence that results depend on the period. |
| B6 | **Asati**, OSF preprint: CPI of India, XGBoost vs Theta vs ARIMA vs Prophet vs LSTM | CPI India | 5-model comparison; MAD, RMSE, MAPE | ❌ | ❌ | not peer-reviewed | Useful baseline list. |
| B7 | **arXiv 2401.00249**, CPI under policy and geopolitical uncertainty | Brazil, Russia, India … | Proposed method beats classical, ML and DL models *(abstract)* | uncertainty indices | ❌ | ? | Uses uncertainty indices, not dated claims. |
| B8 | **Mahajan & Srinivasan (2019, CAFRAL)** | Emerging markets incl. India | Deep neural networks | ❌ | ❌ | DNN beat benchmark except at 1-month ahead | **1-month ahead is hard**, which is exactly Minor 1's horizon. |

## C. News and LLM text for inflation (closest methods; mostly outside India)

| # | Paper | Country | Text method | Revision? | Result *(abstract)* | Gap left for Reflica |
|---|---|---|---|---|---|---|
| C1 | **Allard, Teiletche, Zinebi (2024)**, "Enhancing Inflation Nowcasting with LLM: Sentiment Analysis on News" (InflaBERT, arXiv 2410.20198) | US | Fine-tuned BERT gives a monthly inflation-sentiment **index** added to the Cleveland Fed nowcast | ❌ | marginal gain during the pandemic | aggregate index; no claim provenance; no revision rule |
| C2 | **BIS Papers working paper (2026)**, LLM news index, emerging economies | non-English EMEs | LLM-based news index plus autoregressive benchmarks | ❌ | RMSE down up to 32% (headline) | **check if India is included**; aggregate index |
| C3 | **Bangko Sentral ng Pilipinas** news indices | Philippines | Lexicon + RL + LSTM sentiment indices as features | ❌ | useful for nowcasting | aggregate; no provenance |
| C4 | **RJMF (2025)**, "Forecasting Inflation Using News Indices" | Russia | News sentiment indices with ML (LSTM best), 1–6 months | ❌ | LSTM + news best | aggregate |
| C5 | **PROPOR 2026**, LLM sentiment from central-bank minutes | Brazil | LLM sentiment (bias-corrected) into ARIMA and LSTM | ❌ | improved accuracy | official text only; aggregate |
| C6 | **Banque de France (2026)**, Reddit + LLM for US inflation | US | LLM signals from Reddit; pseudo out-of-sample up to 18 months | ❌ | point and density forecasts improved | social media; aggregate |
| C7 | **LLM-CPI (arXiv 2506.09516)** | China | Daily LLM-scored social-media signal joined to econometric models | ❌ | better than monthly model | aggregate; China |
| C8 | **St. Louis Fed (2023)**, PaLM inflation forecasts | US | LLM **as the forecaster** | ❌ | beat the professional survey (SPF) | likely **leakage** (in-sample period); no evidence trail |
| C9 | **FRB San Francisco "ChatMacro" (2026)** | US | GPT-4 Turbo prompted forecasts, real time May 2024 – Jun 2025 | ❌ | forecasts **stale**, barely move with CPI | shows LLMs **fail to revise** → direct motivation for E3 |
| C10 | **Argentina study (2025)**, GPT-4o Mini | Argentina | LLM as forecaster | ❌ | matched the survey at low and moderate inflation, failed on spikes | spikes are hard; no evidence trail |
| C11 | **Bank of England "Bank Underground" (2020)** | UK | Supervised ML on news | ❌ | news helps only with supervised ML | aggregate |

## D. Forecast revision and updating

| # | Paper | Key point | Use for Reflica |
|---|---|---|---|
| D1 | *International Journal of Forecasting* (2000) experiment on updating forecasts with new data | Updating helped for **trended** series, gave no clear gain for **stable** series | Early evidence that **selective** updating is justified → E3 hypothesis |
| D2 | "Beyond Accuracy: A Stability-Aware Metric for Multi-Horizon Forecasting" (arXiv 2601.10863) | Forecast **stability** as an objective; penalise conflicting sequential forecasts | A metric idea for **unnecessary revisions** (E5) |
| D3 | Statistical-agency revision policies (UN, US Census, ECB working paper on vintages) | Trade-off: frequent small back-and-forth revisions vs fewer revisions; vintage signals improve accuracy and stability | Defines the "always update" vs "rarely update" extremes for E5 |
| D4 | Cleveland Fed real-time inflation nowcasting; nowcast-revision literature (Ireland, Peru 2026) | Mechanical updating whenever new data arrives | **Baseline strategy** "update at each checkpoint" |
| D5 | Back2Future (arXiv 2106.04420) | Learns from data backfill and revisions | Data-revision handling (CPI first release vs revised) |

**Finding so far:** revision is studied as **mechanical data updating** or **stability**. No paper found decides **whether a piece of new textual evidence justifies a revision** with a logged reason (E3 + E4).

## E. Leakage and evaluation

| # | Paper | Key point | Use for Reflica |
|---|---|---|---|
| E-1 | "A Test of Lookahead Bias in LLM Forecasts" (Gao, Jiang, Yan; arXiv 2512.23847) | Lookahead Propensity (LAP) test; LLM predictive power inflated where the model likely saw the outcome; vanishes after the training cutoff | Run a **LAP-style check** on Reflica's LLM extraction step (E6) |
| E-2 | Chronologically consistent LLMs, ChronoBERT / ChronoGPT (Chen et al., arXiv 2502.21206) | Models trained only on text available up to each date; bias modest in their setting | Option: a date-limited model for extraction; otherwise document the limitation |

## F. Evidence graphs and explainable event forecasting

| # | Paper | Key point | Use for Reflica |
|---|---|---|---|
| F1 | IBM, "Knowledge-Based News Event Analysis and Forecasting Toolkit" (IJCAI 2022 demo) | Maps headlines to KG concepts; human-in-the-loop causal analysis | Closest **evidence-graph** idea; not numeric CPI, no revision evaluation |
| F2 | Rule-based temporal KG forecasting extending TLogic (arXiv 2510.24240) | Explainable rules instead of black-box embeddings | Idea for explainable links |
| F3 | GradXKG (arXiv 2310.04889); Graph Hawkes Neural Network (arXiv 2003.13432) | Explain or forecast events on temporal KGs | Background only |

---

## Coverage of E1–E6 (first pass)

| Paper group | E1 India CPI | E2 claim-level dated evidence | E3 revision rule | E4 revision log | E5 vs update strategies | E6 leakage-controlled |
|---|---|---|---|---|---|---|
| A1 news sentiment index | ❌ | ⚠️ aggregate | ❌ | ❌ | ❌ | ? |
| A2 TimeRAG | ❌ | ❌ (pattern retrieval) | ❌ | ❌ | ❌ | ? |
| A4 STCInterLLM | ❌ | ❌ | ❌ | ❌ | ❌ | ? |
| B1 Das & Das | ✅ | ⚠️ aggregate | ❌ | ❌ | ❌ | ? |
| B2–B8 India numeric | ✅ | ❌ | ❌ | ❌ | ❌ | partly (rolling tests in some) |
| C1–C11 news / LLM inflation | ❌ (C2: check) | ⚠️ aggregate indices | ❌ | ❌ | ❌ | ⚠️ (C9 real-time; others pseudo out-of-sample) |
| D revision literature | ❌ | ❌ | ⚠️ mechanical / stability | ⚠️ agency policies | ⚠️ | n/a |
| E leakage | ❌ | n/a | ❌ | ❌ | ❌ | ✅ (method) |
| F evidence graphs | ❌ | ✅ (not numeric) | ❌ | ❌ | ❌ | ? |

**Provisional reading (to confirm in full texts):** each element exists **somewhere**, but **no paper found combines E2 + E3 + E4 + E5 for India CPI (E1) under E6.** The narrowest defensible gap is:

> Prior work adds **aggregate** text signals to inflation forecasts (mostly outside India) or updates forecasts **mechanically**. We found no study that uses **claim-level, dated, source-linked evidence** to decide **whether a CPI forecast should be revised**, logs the reason, and evaluates this rule against never-update and always-update strategies at equal horizons in a **leakage-controlled** backtest for India.

## Next reading steps

1. **Full text, highest priority:** B1 Das & Das; B2 RBI Bulletin 2025; C1 InflaBERT; C2 BIS 2026 (is India included?); C9 ChatMacro; E-1 lookahead bias test.
2. On IEEE Xplore, run the user's 7 searches (below) and add every hit to section B or C with the 9 fields.
3. For B1 and C2, follow citing papers forward (Google Scholar "Cited by") to check whether anyone has added a revision rule since.

### The 7 IEEE Xplore searches (from the user's guideline)
1. `"India" AND "CPI inflation" AND forecasting`
2. `"Consumer Price Index" AND India AND (LSTM OR XGBoost OR ARIMA)`
3. `inflation forecasting AND news sentiment AND machine learning`
4. `"large language model" AND "time series forecasting"`
5. `forecast revision AND new information AND time series`
6. `temporal leakage AND LLM forecasting`
7. `knowledge graph AND explainable forecasting AND time series`

### 9-field template for each new paper
| Field | Record |
|---|---|
| Target | What variable or event is forecast? |
| Inputs | Numbers, news, reports, LLM outputs, or a combination? |
| Method | How are inputs turned into predictions? |
| Revision | Does the forecast change when new information arrives? How? |
| Traceability | Can each prediction be linked to particular sources and claims? |
| Evaluation | Which baselines and metrics? Chronological? |
| Leakage controls | Could future information influence the forecast? |
| Limitation | What remains untested or unresolved? |
| Reflica opportunity | What precise experiment addresses that limitation? |
