---
title: "Evidence-Aware Forecast Revision for India's CPI Inflation: A Review of Numeric, News-Based and LLM Forecasting, and a Proposed Framework"
author: "Sundram Awasthi, M.Tech CSE, GLA University, Mathura, India (supervisor: to be added)"
date: "Draft v0.2, 15 October 2026 (references verified, see VERIFICATION.md)"
---

> **Draft status.** This is a review and proposal paper. It reports **no experimental results**, because the experiments have not been run yet. Sources marked *[A]* in the reference list were read at abstract or summary level only. References marked *[verify]* need their authors, pages or venue checked against the original before submission. The direction is provisional until the supervisor approves it.

## Abstract

Monthly Consumer Price Index (CPI) inflation guides monetary policy in India, and forecasters revise their estimates as new information arrives. Research on forecasting India's CPI has mostly used historical numbers alone, while studies that add news usually compress the text into a single sentiment index. Recent work on large language models (LLMs) adds two further concerns. LLMs handle numbers poorly, and they may "remember" outcomes that fall inside their training period. This paper reviews 36 studies across six groups:

- numeric CPI forecasting for India;
- news- and text-based inflation indices;
- LLM-based time-series forecasting;
- event knowledge graphs and causal methods;
- forecast revision;
- leakage-aware evaluation.

Eight studies were read in full. We compare them on six elements: India and CPI focus, claim-level evidence, a revision decision, comparison of update strategies, uncertainty, and protection against leakage. Three patterns stand out:

1. Several reported accuracies are weakened by short test periods, missing significance tests or information leakage.
2. Text is almost always reduced to one index, so a forecast change cannot be traced to specific news.
3. No reviewed study decides *whether* to revise a forecast from dated, source-linked evidence and evaluates that decision against never-update and always-update strategies.

We propose **Reflica India**, a framework that addresses these gaps. An LLM only extracts claims, a numeric model produces the forecast and its interval, and an explicit rule decides whether to revise it. Every forecast records its creation date, evidence cutoff, target month and expected release date. We also set out an evaluation plan built on a walk-forward backtest.

**Keywords:** CPI inflation, India, forecast revision, news sentiment, large language models, knowledge graph, look-ahead bias, walk-forward evaluation.

---

## I. Introduction

India adopted flexible inflation targeting in 2016, with headline CPI inflation as the target of the Reserve Bank of India (RBI). The Ministry of Statistics and Programme Implementation (MoSPI) publishes all-India CPI monthly, and from 2026 the series uses the new base year 2024 = 100. Policymakers, banks and businesses need a forecast of next month's inflation. They also need to know *when that forecast should change*, because news about vegetable prices, fuel, the monsoon or government policy arrives every day, well before the official release.

Forecasting research mostly treats prediction as a one-time act: train a model, produce a number and score it. In practice forecasts are revised. Revising too rarely ignores real information, and revising on every headline adds noise and erodes trust. A good revision policy should change the forecast only when new evidence is novel, reliable, relevant and strong enough. It should also be able to say which evidence caused each change.

Two trends make this question timely. First, text is now widely used to forecast inflation. In India this includes newspaper sentiment for food prices [3] and text-mined inflation expectations [4]. Second, LLMs can read news at scale. However, LLMs predict numbers poorly [10], they can produce stale forecasts in real time [16], and their scores can be inflated by look-ahead bias [19].

This paper makes three contributions:

1. **A structured review** of 36 studies, eight read in full, organised into six groups and compared on a common set of elements (Section IV and Table I).
2. **A critical reading of the evidence.** For each full-text study we check test length, significance testing and leakage, which often change how far its headline accuracy can be trusted (Section V).
3. **A research gap and a proposed framework** (Reflica India) with a concrete, leakage-aware evaluation plan (Sections VI–VII).

---

## II. Background

### A. CPI in India

MoSPI releases all-India CPI (rural, urban and combined) around the 12th of each month for the previous month. Food has a large weight in the basket, and a few volatile items cause much of the month-to-month swings. Tomato, onion and potato together weigh only about 2.2% of the basket, yet they drive a large share of food-inflation volatility [3]. In 2026 the base year changed to 2024 = 100. Any study using pre-2026 data must therefore handle the link between the old (2012 = 100) and new series.

### B. Forecast revision

A *revision* is a change to a forecast for the same target made at a later date. Statistical agencies and nowcasting systems usually revise mechanically, for example every time a new data point arrives. Early evidence shows that updating helps for trending series but brings little gain for stable ones [22]. Recent work proposes measuring forecast *stability* alongside accuracy [23]. These two ideas motivate our search for a *selective* revision policy.

### C. Leakage and look-ahead bias

A forecast is *leaky* if it uses information that would not have been available when the forecast was made. Common sources are:

- using same-day outcome variables as inputs [9];
- splitting time series randomly rather than by date;
- tuning model choices on the test period;
- for LLMs, *memorisation*, where the model saw the outcome during training [19], [20].

ChatMacro [16] showed the practical effect: LLM inflation forecasts that looked competitive in pseudo-out-of-sample tests were inaccurate and stale in real time.

---

## III. Review Method

**Sources.** The sources were:

- papers supplied by the author and downloaded from IEEE Xplore through institutional access;
- an earlier 22-paper reading list on AI event forecasting;
- targeted web searches for India CPI forecasting, news-based inflation indices, LLM forecasting, forecast revision and look-ahead bias.

**Depth.** Eight IEEE papers were read in full [1], [7]–[13]. The others were assessed from abstracts, official summaries or search summaries and are marked *[A]*.

**Comparison elements.** Each study was checked against six elements:

| Code | Element |
|---|---|
| E1 | India and CPI (or close macroeconomic) target |
| E2 | Claim-level, dated, source-linked evidence (not one aggregate index) |
| E3 | An explicit decision on *whether* to revise a forecast |
| E4 | Comparison against never-update and always-update strategies at equal horizons |
| E5 | Uncertainty: intervals or calibrated probabilities |
| E6 | Leakage control: chronological testing and point-in-time evidence |

**Quality checks (full-text papers).** For each full-text paper we recorded the length of the test period, the use of a significance test (e.g. Diebold–Mariano [24]), the simple baselines included, and any leakage risk.

---

## IV. Literature Review

### A. Numeric CPI forecasting for India

**Sarveswararao and Ravi [1]** forecast India's monthly CPI inflation (headline, food and beverages, fuel and light) for January 2012 to December 2018. Their method has two stages. First, a chaos test (largest Lyapunov exponent) and phase-space reconstruction (time delay from autocorrelation, embedding dimension from Cao's method) build the input vectors. Second, nine models make the forecast: RF, SVM, MLP, XGBoost, KNN, LSTM, ARIMA, GMDH and GRNN.

- **Results:** a chaos-based GRNN was best for headline inflation (SMAPE 10.32, Theil's U 0.58, directional accuracy 83.3%). LSTM performed poorly because the sample was small.
- **Limits:** the test set is the last six months only. The authors' own Diebold–Mariano tests between the top two models give p-values of 0.96, 0.65 and 0.62, so the leading models are not significantly different. The study uses numbers only and reports no intervals.

**Pratap and Sengupta [2]** (RBI) compared machine-learning and statistical models for headline, food, fuel and core inflation *[A]*.

- **Results:** ML models generally did better. Simple-average combinations beat every individual model, and simple weights beat complex ones. Forecasting headline inflation directly was as good as building it from components.
- **For us:** a simple-average combination is a strong, cheap baseline.

**Other India numeric work** reports mixed results. One IEEE conference study found statistical models beating LSTM on a small CPI sample [A], and a CAFRAL study found that deep networks cut India's forecast error by about 44–63% at every horizon *except* one month ahead [21] *[A]*. Recent RBI work combines statistical, ML and deep models with performance weights [6] *[A]*.

**Karthick et al. [8]** used an LSTM to estimate India's monthly per-capita expenditure (MPCE) from quarterly CPI inflation, GDP growth and unemployment (2011–2023).

- **Results:** R² 0.93 and MAPE 4.12%; SHAP ranked CPI inflation as the most important input.
- **Limits:** only three survey rounds provide real MPCE values, and the remaining quarters are interpolated with a cubic spline. The test set holds about seven quarterly points. The reported fit therefore largely reflects the interpolated curve.

*Summary.* India CPI forecasting is mostly numeric. Test windows are often short, and simple or combined models are hard to beat.

### B. News- and text-based inflation indices

**India.**

- **RBI food-inflation study [3]** *[A]*. Built sentiment indices for tomato, onion and potato from nine English dailies (2011–2021). The indices moved inversely to price changes and improved vegetable and food-inflation forecasts.
- **Banerjee, Kanodia and Ray [4]** *[A]*. Text-mined two financial dailies by CPI category (food, fuel, clothing, miscellaneous) into an inflation-expectation index that tracked actual inflation.
- **A 2024 study [5]** *[A]*. Combined headline-derived text series with macroeconomic data in ML ensembles and reported gains.

**Other countries.**

- **Kang et al. [7]** (read in full) built a news-based economic sentiment index for South Korea's ICT industry from about 49 million articles (2010–2021).
  - *Method:* two KoBERT models scored relevance and sentiment using 4,000 hand-labelled articles. Articles were clustered (via joint-plot images) into six groups and combined with MCDA weights. The index was then used in a mixed-frequency VAR to forecast ICT-GDP growth.
  - *Results:* out-of-sample (2020–2021, eight quarters) RMSE was 1.718 against 1.736 for the survey index, and MAE 1.441 against 1.501.
  - *Limits:* the gain is about 1% on eight quarters with no significance test. The MCDA method was selected partly by its correlation with actual ICT-GDP.
- **Other studies.**
  - InflaBERT [17] adds a BERT news index to a US nowcast and finds small gains *[A]*.
  - A Thai study [18] uses an LLM news index of inflation expectations and reports up to 32% lower RMSE against autoregressive benchmarks *[A]*.
  - Similar indices exist for the Philippines, Russia, Brazil, France and China (see the project literature matrix) *[A]*.

*Summary.* Text generally helps, but nearly every study compresses news into **one index per period**. The forecast change cannot be traced to particular articles, and none of these studies decides when to revise.

### C. LLM-based time-series forecasting

**Fang et al. [10]** compared LSTM, a Transformer and zero-shot GPT-3.5 on the daily S&P 500.

- **Results:** bucketed return accuracy was 22.8%, 15.6% and 15.3%, against about 14% for chance with seven buckets.
- **Limits:**
  - The Transformer figures were taken from another paper, not re-run.
  - GPT-3.5 often printed incomplete numbers, and its RMSE improved only after those outputs were removed post hoc.
  - The test period (2005–2024) overlaps the model's training data.

This supports the design choice of *not* using an LLM as the numeric forecaster.

**TimeRAG [14]** *[A]* (arXiv preprint) retrieves similar historical segments (by dynamic time warping) to guide an LLM, reporting about 3% improvement. **From News to Forecast [15]** *[A]* uses LLM agents to select relevant news, reason about it and *reflect* on forecast errors, then fine-tunes a model on news plus series. Its reflection loop is the closest prior idea to evidence-driven revision. **ChatMacro [16]** *[A]* evaluated ChatGPT's US inflation forecasts and found them reasonable in pseudo-out-of-sample tests but inaccurate and stale in real time.

**Li et al. [11]** (STCInterLLM, read in full) address spurious spatial links and LLM hallucination in power-load and taxi-flow forecasting.

- **Method:** a causal-intervention encoder, chain-of-action prompting and a frozen Vicuna-7B.
- **Results:** at least 7.46% MAE, 8.12% RMSE and 14.60% MAPE improvement over seven baselines.
- **Limits:** it needs multi-GPU training and handles numeric data only.

**Liu et al. [13]** distil GPT-4 chain-of-thought reasoning into a small Qwen-1.5 model for vehicle trajectory prediction. The model achieves 0.93 m average error at 28 ms latency, showing that step-by-step prompts and teacher–student distillation can make LLM reasoning cheaper.

### D. Event knowledge graphs and explainable forecasting

**Schramm [12]** proposes the Simple Timeseries Event Model (STEM), an ontology extending the Simple Event Model [26]. It has core classes Event, Actor, Place, Time and Impact. Numeric effects are attached to relations, and *views* distinguish official (authority) from user opinions, including conflicting views. STEM is demonstrated on US vehicle-market and macroeconomic data but reports **no forecasting results**. The author notes that human-entered future links are uncertain. Other work maps news to knowledge-graph concepts or forecasts on temporal graphs (see the literature matrix) *[A]*. None of it applies the graph to CPI forecasts or their revision.

### E. Forecast revision

Studies of updating show benefits for trending series and little gain for stable ones [22]. Stability-aware metrics penalise forecasts that flip back and forth [23]. Nowcasting systems update mechanically at each data release. No reviewed work conditions the revision decision on dated, source-linked claims.

### F. Leakage-aware evaluation

Gao, Jiang and Yan [19] *[A]* propose a test for look-ahead bias in LLM forecasts and show that predictive power concentrates where the model likely saw the outcome. Chronologically consistent language models [20] *[A]* restrict training text to each date. A clear example of leakage is **Srivani et al. [9]** (read in full). They predict the daily Dow Jones direction from Reddit headlines plus Open, High, Low, Close, Adjusted Close and Volume, with an 80/20 split, and report 95.8% accuracy. Because the label is whether the *same day's* close rose and the close is an input, the target is effectively visible to the model. Their price-only baseline already reaches 82%, which is consistent with this. Benchmarks such as ForecastBench [25] avoid leakage by scoring questions before they resolve.

---

## V. Comparative Analysis

**Table I. Studies compared on elements E1–E6** (✅ yes, ⚠️ partly, ❌ no; *[A]* = abstract level)

| Ref | Study | Target / data | E1 India CPI | E2 Claim-level evidence | E3 Revision decision | E4 Update strategies | E5 Uncertainty | E6 Leakage control | Key quality note |
|---|---|---|---|---|---|---|---|---|---|
| [1] | Sarveswararao & Ravi 2020 | India CPI, monthly 2012–18 | ✅ | ❌ | ❌ | ❌ | ❌ | ⚠️ chronological, 6 test months | Top models not significantly different |
| [2] | Pratap & Sengupta 2019 *[A]* | India CPI components | ✅ | ❌ | ❌ | ❌ | ? | ? | Simple averages strongest |
| [3] | RBI food-news sentiment 2021 *[A]* | India food inflation | ✅ | ⚠️ item-level index | ❌ | ❌ | ? | ? | Closest India news study |
| [4] | Banerjee et al. 2021 *[A]* | India inflation expectations | ✅ | ⚠️ category index | ❌ | ❌ | ? | ? | Tracking, not forecasting revisions |
| [7] | Kang et al. 2025 | Korea ICT-GDP | ❌ | ⚠️ aggregate index | ❌ | ❌ | ❌ | ⚠️ | ~1% gain, 8 quarters, no test |
| [8] | Karthick et al. 2025 | India MPCE | ⚠️ | ❌ | ❌ | ❌ | ❌ | ⚠️ | 3 real target points |
| [9] | Srivani et al. 2026 | US DJIA direction | ❌ | ⚠️ event tuples, aggregated | ❌ | ❌ | ❌ | ❌ same-day close as input | Likely target leakage |
| [10] | Fang et al. 2024 | US S&P 500 | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | Copied baseline; post-hoc filtering |
| [11] | Li et al. 2025 | Power load, taxi | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ chronological | Strong venue; high compute |
| [12] | Schramm 2023 | US vehicles + macro (design) | ❌ | ✅ schema only | ❌ | ❌ | ❌ | n/a | No experiments |
| [13] | Liu et al. 2025 | Vehicle trajectories | ❌ | ❌ | ❌ | ❌ | ⚠️ | ✅ | Own dataset |
| [15] | From News to Forecast 2024 *[A]* | Several domains | ❌ | ⚠️ selected news | ⚠️ reflection | ❌ | ? | ? | Closest revision idea |
| [16] | ChatMacro 2026 *[A]* | US inflation | ❌ | ❌ | ❌ | ❌ | ? | ✅ real-time | LLM forecasts stale |
| [17], [18] | InflaBERT; Thai LLM index *[A]* | US; Thailand | ❌ | ⚠️ aggregate | ❌ | ❌ | ⚠️ | ⚠️ | One index per period |
| — | **Reflica India (proposed)** | India CPI, monthly | ✅ | ✅ | ✅ | ✅ | ✅ intervals | ✅ point-in-time | To be evaluated |

**Observations.**

1. **Short or weak tests are common.** Six test months [1], eight quarters [7] and about seven points [8] are too few for reliable ranking, and only [1] reports a significance test, which finds no significant winner.
2. **Leakage appears in several forms:** same-day outcome inputs [9], post-hoc removal of bad outputs [10], design choices tuned on outcomes [7], and possible LLM memorisation [10], [16], [19].
3. **Simple models are strong.** Simple averages beat complex weights in India [2], and statistical models beat LSTM on small samples ([1], [A]).
4. **Text is aggregated.** Even the closest India studies [3]–[5] produce one index per item, category or period.
5. **Revision is unexamined.** Only [15] adjusts forecasts after reflection, and no study evaluates a revision policy against never-update and always-update baselines.

---

## VI. Research Gap

From the studies reviewed, we found **no work that, for India's CPI inflation:**

- (a) represents new information as individual claims with a date, source, direction and strength;
- (b) uses an explicit, explainable rule to decide whether a forecast should be revised;
- (c) records the reason for every revision; and
- (d) evaluates this rule against never-update and always-update strategies at equal horizons, with prediction intervals, in a point-in-time (leakage-controlled) walk-forward backtest.

This gap is provisional. Several closely related studies [2]–[5], [15], [16] were assessed at abstract level and must be read in full before any claim of novelty.

**Research questions.**

- **RQ1.** Does evidence-aware selective revision reduce error (MAE, RMSE) relative to never-update and always-update strategies at the same horizon?
- **RQ2.** Does it reduce unnecessary revisions (forecast changes that move away from the outcome) while keeping interval coverage near its nominal level?
- **RQ3.** Which evidence properties (novelty, reliability, relevance or strength) matter most for good revision decisions?

---

## VII. Proposed Framework: Reflica India

**Pipeline.**

1. **Point-in-time data collection.** Official CPI releases (MoSPI), RBI publications, PIB releases, and dated news from public sources. Every item stores its publication time.
2. **Claim extraction (LLM extracts only).** Step-by-step prompts (motivated by [11], [13]) turn each article into claims:
   - item or sector;
   - direction (up or down);
   - size, if stated;
   - region;
   - date;
   - source and source type (official or media).

   The schema follows the event, actor, place, time and impact classes of STEM [12], with official versus non-official *views* for conflicting claims. The LLM never outputs the CPI forecast. This avoids the numeric failures seen in [10].
3. **Baseline numeric forecast.** Seasonal naive, ARIMA/SARIMA, XGBoost, and a simple-average combination [2] produce a point forecast and a prediction interval for next month's all-India combined CPI inflation (year-on-year).
4. **Revision rule.** At each checkpoint before the release, new claims are scored on four checks:
   - *novelty:* not already reflected in data or earlier claims;
   - *reliability:* source type and agreement across sources;
   - *relevance:* weight of the item in the CPI basket and the horizon;
   - *strength:* size and consistency of the claimed move.

   The forecast is revised only if the combined score passes a threshold fixed *in advance on training years*. The size of the revision is bounded and logged.
5. **Revision log.** Every forecast stores its creation date, evidence cutoff, target CPI month, expected release date, the claims used, the decision and the reason.

**Evaluation plan (no results yet).**

- **Primary evaluation: walk-forward backtest.** The model is refit using only data available at each point. Many target months are tested, not a single short window.
- **Strategies compared at equal horizons:**
  - never update;
  - always update at each checkpoint;
  - evidence-aware selective update;
  - a text-only variant.
- **Metrics:**
  - MAE and RMSE;
  - interval coverage and width;
  - number of revisions, and the share of revisions that moved toward the outcome;
  - Diebold–Mariano tests for significance [24].
- **Leakage controls:**
  - evidence strictly before the cutoff;
  - chronological splits only;
  - thresholds fixed before the test period;
  - a look-ahead-bias check on the extraction step [19];
  - handling of the 2012-to-2024 base-year link.
- **Supplementary evaluation:** a live trial that records forecasts before each official release and scores them afterwards.

**Cost.** The design uses small open models or a free API tier for extraction and classical models for forecasting. It runs on a laptop and a free cloud database, in contrast to the multi-GPU setup of [11].

---

## VIII. Limitations of This Review and Threats to Validity

1. Only eight studies were read in full; the others were assessed from abstracts or summaries.
2. Search covered English-language sources, mainly IEEE Xplore and open web summaries, so Hindi and regional-language work and some journals may be missed.
3. Published accuracy figures were not reproduced.
4. Claim extraction by LLMs may itself carry look-ahead bias; this will be tested, not assumed away.
5. The CPI base-year change in 2026 complicates long backtests.

---

## IX. Conclusion

Research on forecasting India's inflation has moved from numeric models to text-augmented and LLM-based approaches. The reviewed evidence shows that short tests, missing significance checks and leakage often weaken reported gains, and that simple combinations remain hard to beat. News helps, but it is almost always reduced to a single index, and forecast revision itself has not been studied as a decision. We propose Reflica India: claim-level, dated and source-linked evidence feeds an explicit, logged revision rule, evaluated against never-update and always-update strategies in a leakage-controlled walk-forward backtest. The next steps are full-text reading of [2]–[5], [15] and [16], building the point-in-time dataset, and running the backtest.

---

## References

*[A] = read at abstract or summary level. [verify] = check authors, pages or venue before submission.*

[1] V. Sarveswararao and V. Ravi, "Chaos, machine learning and deep learning based hybrid to forecast consumer price index inflation in India," in *Proc. IEEE Symp. Series on Computational Intelligence (SSCI)*, Canberra, Australia, 2020, pp. 2551–2557.

[2] B. Pratap and S. Sengupta, "Macroeconomic forecasting in India: Does machine learning hold the key to better forecasts?" Reserve Bank of India, Working Paper No. 04/2019, 2019. [A]

[3] B. Pratap, A. Ranjan, V. Kishore and B. B. Bhoi, "Forecasting food inflation using news-based sentiment indicators," *RBI Occasional Papers*, vol. 42, no. 2, 2021 (published Oct. 2022). [A]

[4] A. Banerjee, A. Kanodia and P. Ray, "Deciphering Indian inflationary expectations through text mining: An exploratory approach," *Indian Economic Review*, vol. 56, pp. 49–66, 2021, doi: 10.1007/s41775-021-00106-9. [A]

[5] P. K. Das and P. K. Das, "Improvement in inflation forecasting: Ensembling text mining with macro data in machine learning models," *Int. J. Economics and Finance*, vol. 16, no. 6, pp. 92–100, 2024, doi: 10.5539/ijef.v16n6p92. [A] [verify that the data is Indian]

[6] R. Mohan, S. Hasan, S. Roy, S. Sarkar and J. John, "Predicting CPI inflation in India: Combining forecasts from a 'suite' of statistical and machine learning models," *RBI Bulletin*, Jun. 2025. [A]

[7] N. Kang, D. Min, Y. Cho, D.-W. Ko, H. H. Kim, J. Y. Choeh and J. Im, "Online news-based economic sentiment index," *IEEE Trans. Big Data*, vol. 11, no. 3, pp. 1464–1474, 2025, doi: 10.1109/TBDATA.2024.3474211. [verify pages]

[8] A. V. Karthick, N. Muthukrishnan, S. Suganya, G. Parimalarani, H. Sudarsan and A. K. Parthasarathy, "AI-driven predictive analytics for monthly per capita expenditure using macroeconomic indicators," in *Proc. 4th Int. Conf. Automation, Computing and Renewable Systems (ICACRS)*, 2025, doi: 10.1109/ICACRS67045.2025.11324119.

[9] N. Srivani, C. Dileep, B. Vaishnavi, B. Saptharshi, L. S. G. Reddy and M. Z. Sadik, "A comprehensive multi-source multi-instance learning framework for predicting stock market trends utilizing financial news and market indicators to enhance accuracy," in *Proc. IEEE Global Symp. Emerging and Communication Technologies (GSEACT)*, 2026, doi: 10.1109/GSEACT68539.2026.11619959.

[10] J. Fang, Z. Xiao, Y. Wu, J. Zhang, Z. Xu and Z. Mai, "A comparative study of sequential deep learning models in financial time series forecasting," in *Proc. 11th Int. Conf. Soft Computing & Machine Intelligence (ISCMI)*, 2024, pp. 22–25, doi: 10.1109/ISCMI63661.2024.10851487.

[11] S. Li, H. Li, X. Li, Y. Xu, Z. Lin and H. Jiang, "Causal intervention is what large language models need for spatio-temporal forecasting," *IEEE Trans. Cybernetics*, vol. 55, no. 8, pp. 3825–3837, Aug. 2025, doi: 10.1109/TCYB.2025.3569333. [verify end page]

[12] S. Schramm, "Constructing the simple timeseries event model," in *Proc. IEEE Int. Conf. Knowledge Graph (ICKG)*, 2023, pp. 134–139, doi: 10.1109/ICKG59574.2023.00022.

[13] Y. Liu, G. Tian, W. Zhong, X. Qi and Y. Wang, "LLM-driven trajectory prediction at intersections with chain-of-thought reasoning," in *Proc. 9th IEEE Int. Conf. Network Intelligence and Digital Content (IC-NIDC)*, 2025, doi: 10.1109/IC-NIDC67200.2025.11390125.

[14] S. Yang, D. Wang, H. Zheng and R. Jin, "TimeRAG: Boosting LLM time series forecasting via retrieval-augmented generation," arXiv:2412.16643, 2024. [A] [ICASSP 2025 venue not confirmed]

[15] X. Wang, M. Feng, J. Qiu, J. Gu and J. Zhao, "From news to forecast: Integrating event analysis in LLM-based time series forecasting with reflection," in *Advances in Neural Information Processing Systems (NeurIPS)*, 2024. [A]

[16] Alam, Boyle, Li and Sekhposyan, "ChatMacro: Evaluating inflation forecasts of generative AI," Federal Reserve Bank of San Francisco, Working Paper 2026-04, 2026. [A] [verify first names]

[17] M.-A. Allard, P. Teiletche and A. Zinebi, "Enhancing inflation nowcasting with LLM: Sentiment analysis on news," arXiv:2410.20198, 2024. [A]

[18] T. Tawichsri, S. Tuarob, N. Nookhwun and C. Sangasaeng, "News-based inflation expectations: LLM-assisted measurement and forecasting," PIER Discussion Paper No. 252, Puey Ungphakorn Institute for Economic Research, May 2026. [A]

[19] Z. Gao, W. Jiang and Y. Yan, "A test of lookahead bias in LLM forecasts" (later "Detecting lookahead bias in LLM forecasts"), arXiv:2512.23847, 2025. [A]

[20] S. He, L. Lv, A. Manela and J. Wu, "Chronologically consistent large language models," arXiv:2502.21206, 2025. [A]

[21] K. Mahajan and A. Srinivasan, "Inflation forecasting in emerging markets: A machine learning approach," CAFRAL, 2019/2020. [A]

[22] M. O'Connor, W. Remus and K. Griggs, "Does updating judgmental forecasts improve forecast accuracy?" *Int. J. Forecasting*, vol. 16, no. 1, pp. 101–109, 2000. [A]

[23] C. Ma, G. Pomazkin, G. P. Saggese and P. Smith, "Beyond accuracy: A stability-aware metric for multi-horizon forecasting," arXiv:2601.10863, 2026. [A]

[24] F. X. Diebold and R. S. Mariano, "Comparing predictive accuracy," *J. Business & Economic Statistics*, vol. 13, no. 3, pp. 253–263, 1995.

[25] E. Karger, H. Bastani, C. Yueh-Han, Z. Jacobs, D. Halawi, F. Zhang and P. E. Tetlock, "ForecastBench: A dynamic benchmark of AI forecasting capabilities," in *Proc. ICLR*, 2025. [A]

[26] W. R. van Hage, V. Malaisé, R. Segers, L. Hollink and G. Schreiber, "Design and use of the Simple Event Model (SEM)," *J. Web Semantics*, vol. 9, no. 2, pp. 128–136, 2011.

[27] Ministry of Statistics and Programme Implementation, Government of India, "Consumer Price Index: monthly press releases," 2012–2026.
