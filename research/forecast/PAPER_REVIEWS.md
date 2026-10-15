# Paper reviews in simple language (15 Oct 2026)

For Minor 1: **predict next month's India CPI inflation, and decide when to change (revise) the forecast using dated evidence.**

For every paper this file answers: who wrote it, the title, the problem, the method, the result, the limits, the research gap, how Reflica fills that gap, how useful it is for us, and how Reflica can do better.

**How to read the ratings**
- **Trust** asks whether we can believe the paper's numbers. *High* means a strong journal, public code and fair testing. *Low* means a serious testing mistake.
- **Use for us** asks how much the paper helps Minor 1 (India CPI and forecast revision).

Part 1 covers the 4 papers you uploaded, which I read in **full text**. Part 2 covers the other related papers. Most of those were read at **abstract level only**, so read each one fully before citing it.

---

## Master table: every paper you gave me (updated 15 Oct 2026)

**Read:** F = full text read; A = abstract or search summary only.
**Trust** = can we believe its numbers. **Use** = how much it helps Minor 1 (India CPI and revision).

### Table 1. PDFs you uploaded (8 files, 7 different papers; STCInterLLM was sent twice)

| # | Title (short) | Authors · Venue · Year | Problem | Method | Result / accuracy | Main limitation / gap | How Reflica fills it | Trust | Use | Read |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **Chaos + ML hybrid for India CPI inflation** | Sarveswararao & Ravi (Univ. of Hyderabad, IDRBT) · IEEE SSCI · 2020 | Forecast India monthly CPI (headline, food, fuel) | Chaos test → 9 models (GRNN, MLP, SVM, RF, XGBoost, ARIMA, LSTM…) | Headline: GRNN SMAPE 10.3, Theil's U 0.58, direction 83% | Only 6 test months; best model **not significantly** better (DM p = 0.62–0.96); numbers only; no range | Many walk-forward months, DM test, intervals, news-based revision | Medium | ⭐ Very high | F |
| 2 | **Online News-Based Economic Sentiment Index** | Kang et al. (Yonsei and others, Korea) · IEEE Trans. Big Data · 2025 | Official data is late; build a faster index from news | KoBERT relevance + sentiment → clustering → MCDA index → VAR forecast of ICT-GDP | Out-of-sample RMSE 1.718 vs 1.736 (survey index), only 8 quarters | Gain about 1%, no significance test; one aggregate number; method chosen using the actual GDP | Separate dated claims, traceable revisions, more test periods | Medium | High | F |
| 3 | **AI-Driven Predictive Analytics for MPCE** | Karthick et al. (Alagappa Univ., India) · IEEE ICACRS · 2025 | Estimate India household spending between surveys | LSTM on CPI, GDP growth and unemployment (quarterly 2011–23) | R² 0.93, MAPE 4.1%; CPI most important | Only 3 real target values (rest interpolated); about 7 test points | Real monthly CPI target; long walk-forward test | Low | Medium (India data) | F |
| 4 | **Multi-Source Multi-Instance stock trend (MS-MI)** | Srivani et al. (CMR Institute of Technology, Hyderabad) · IEEE GSEACT · 2026 | Dow Jones up or down from news + prices | spaCy events + VADER + Word2Vec + 6 price numbers → SVM, XGBoost | 95.8% accuracy | **Leakage**: today's close is an input; random split | Evidence cutoff dates, walk-forward by date | Low | Medium (warning example) | F |
| 5 | **Comparative study: LSTM vs Transformer vs LLM** | Fang et al. (USA) · IEEE ISCMI · 2024 | Best model for S&P 500 prices | LSTM, GPT-3.5 zero-shot; Transformer results copied from another paper | Bucket accuracy 22.8 / 15.6 / 15.3% (guessing ≈ 14%) | Copied baseline; LLM outliers removed after seeing results; possible LLM memory | LLM only extracts; a numeric model forecasts | Low–medium | Low–medium | F |
| 6 | **STCInterLLM: Causal intervention for LLM forecasting** | Li et al. (South China Univ. of Tech.) · IEEE Trans. Cybernetics · 2025 | Power-load and taxi forecasts with sparse data; false links; hallucination | Causal encoder + chain-of-action prompts + frozen Vicuna-7B | At least 7.5% lower MAE than 7 baselines | 8 large GPUs; numbers only; no range; no revision | Borrow "check before trusting a link" → 4 revision checks | High | Low–medium | F |
| 7 | **STEM: Simple Timeseries Event Model** | Schramm (Univ. Bamberg / BMW) · IEEE ICKG · 2023 | Store events + time series in one knowledge graph for explainable forecasting | Ontology design: Event, Actor, Place, Time, Impact; official vs user views | No forecasting results (design only) | Never used to forecast; links are human guesses | Working claim graph used in a real revision loop | Medium | High (claim schema) | F |
| 8 | **LLM trajectory prediction with chain-of-thought** | Liu et al. (Tsinghua) · IEEE IC-NIDC · 2025 | Predict car paths at traffic signals, fast and safe | GPT-4 step-by-step prompts → distilled into small Qwen-1.5 | 0.93 m error, 23% better; 28 ms | Own dataset; traffic only | Borrow: step-by-step extraction prompts; big model teaches small free model | Medium | Low | F |

### Table 2. Papers you assigned by name (not uploaded)

| # | Title | Authors · Venue · Year | Problem → Method | Result | Gap | Use | Read |
|---|---|---|---|---|---|---|---|
| 9 | TimeRAG | ICASSP 2025 (arXiv 2412.16643) | LLM forecasting → retrieves similar past patterns (DTW) | About 3% better | Numbers only; no news; no revision | Medium | A |
| 10 | Time-series LLM systematic review (IEEE Access) | exact title not found | — | — | — | Please send the title or DOI | — |

### Table 3. Papers from your earlier list (`Research_Work_paper.docx`, 22 papers)

These are summarised from **your own notes**; I have not read them. Use for Minor 1 is low unless marked.

| # | Paper (year) | Area | Gap you noted | Use for Minor 1 |
|---|---|---|---|---|
| 11 | LLMs for event forecasting, conflict outcome (2025) | War / geopolitics | One conflict; no % or check | Low (Minor 2) |
| 12 | MENTOR, multi-agent narrative trends (2025) | China markets | Leakage risk; no % | Low |
| 13 | LLM event-driven financial forecasting (2026) | China stocks | 56% accuracy; fixed forms | Low–medium (event forms) |
| 14 | LLM multi-causal event causality mining (2025) | Finance text | Past only | Medium (cause chains for claims) |
| 15 | Hierarchical semantic extraction + heterogeneous GNN, oil (2026) | Oil price + news | No uncertainty; costly | Medium (news → number) |
| 16 | LLM framework for big NIFTY moves (2026) | **India** stocks | Big moves badly predicted | Low–medium |
| 17 | LLM adaptive stock forecasting under China policy (2026) | China stocks | Mood judgement unchecked | Low |
| 18 | LLM-augmented sentiment time series (2027) | Public mood | Only "looks like" check | Low |
| 19 | LLM agents for forecasting: survey (2026) | Survey | Need live testing, cost reporting | Medium (background) |
| 20 | ForecastBench (2024–26) | Benchmark | US-focused; yes/no only | Medium (Minor 2) |
| 21 | ML disaster forecasting + multi-agent RL, underwater sensors | Networking | Synthetic data | None |
| 22 | ML + agent-based modelling, climate migration | Society | Yearly; no news | Low |
| 23 | RL-enhanced attention for adaptive time series | Method | Numbers only | Low |
| 24 | FinPulse multi-agent event-driven markets | Finance | No results shown | Low |
| 25 | Deep multi-task incomplete event forecasting (TKDE 2024) | Social events | No LLM; not India | Low |
| 26 | CausalFormer (TKDE 2025) | Causal discovery | Numbers only | Low–medium |
| 27 | ST-LLM+ traffic (TKDE 2025) | Traffic | No events | Low |
| 28 | LLMs for building-level load (TPWRS 2025) | Electricity | No events | Low |
| 29 | Mid-term load with in-context LLMs (TPWRS 2026) | Electricity | No events | Low |
| 30 | Survey: LLMs on generative graph analytics (TKDE 2025) | Graphs | Dynamic graphs under-explored | Low–medium |
| 31 | **From News to Forecast** (Wang et al., NeurIPS 2024) | News + time series (electricity, exchange rates and others) | Agents choose news, **reflect and fix forecasts**; LLaMA-2 fine-tuned; code released | **High**: closest to our revision idea; read in full |

### Table 4. More India papers found by searching today (abstract or search summary)

| # | Title | Authors · Venue · Year | What it does | Result | Gap | Use |
|---|---|---|---|---|---|---|
| 32 | Macroeconomic Forecasting in India: Does Machine Learning Hold the Key to Better Forecasts? | Bhanu Pratap & Shovon Sengupta · RBI Working Paper 04/2019 | ML vs statistical models for headline, food, fuel and core CPI | ML generally better; **simple average of models beats all single models**; forecasting headline directly is as good as building it from parts | Numbers only | ⭐ Very high: an RBI baseline; use a simple-average combination as a baseline |
| 33 | Forecasting Food Inflation using News-based Sentiment Indicators | Pratap, Ranjan, Kishore, Bhoi · RBI Occasional Papers 42(2), 2021 (released 2022) | Sentiment indices for **tomato, onion, potato** from 9 English dailies (2011–2021) | Adding news sentiment **improved food-inflation forecasts**; sentiment moves opposite to prices | One index per item; no claim-level evidence; no revision rule | ⭐ Very high: **the closest India "news → CPI" paper**, from the RBI itself; read in full |
| 34 | Deciphering Indian inflationary expectations through text mining | Banerjee, Kanodia, Ray · Indian Economic Review 56, 2021 | Text-mine Economic Times and Business Line by CPI category (food, fuel, clothing, misc.) | Text index tracks actual inflation well | Aggregate index; tracking, not revising | High |
| 35 | Improvement in Inflation Forecasting: Ensembling Text Mining with Macro Data in ML Models | Int. J. Economics and Finance 16(6), 2024 (authors to verify; earlier listed as "Das & Das") | Headlines + macro data in ML ensembles | Text improves forecasts (abstract) | Aggregate; no revision | High |
| 36 | ChatMacro: Evaluating Inflation Forecasts of Generative AI | Alam, Boyle, Li, Sekhposyan · FRB San Francisco WP 2026-04 | ChatGPT inflation forecasts, real time vs backtest | Backtests look fine, but **real-time forecasts are inaccurate and stale** | Shows LLMs don't update well | ⭐ Very high: motivates our revision rule and live trial |

**What the table shows:** India CPI work is either **numbers only** (#1, #32) or **one news index** (#33, #34, #35). Nobody keeps **each claim with its date and source** and uses it to decide **when to revise** the forecast, then tests that against "never update" and "always update". That is still our gap, and the RBI's own news-sentiment work (#33) makes the gap **more** relevant for India, not less.

---

## Part 1. The 4 papers you uploaded (full text read)

### Paper 1. Comparing LSTM, Transformer and LLM for stock prices

| Field | Answer |
|---|---|
| **Title** | A Comparative Study of Sequential Deep Learning Models in Financial Time Series Forecasting |
| **Authors** | Jingxing Fang, Zhaomin Xiao, Yingyi Wu, Jinran Zhang, Zhuoer Xu, Zhelu Mai (USA: independent researcher, Univ. of North Texas, Meta, HPE and others) |
| **Venue** | IEEE ISCMI 2024 (conference). DOI 10.1109/ISCMI63661.2024.10851487 |
| **Problem** | Which model predicts the daily S&P 500 price best: LSTM, Transformer or an LLM? |
| **Method** | S&P 500 daily prices from 1927 to 2024. The last 20% (2005–2024) is the test set. LSTM: 3 layers. LLM: GPT-3.5 with no training (zero-shot), reading the prices as text. Transformer: they **did not run it**; they copied the numbers from another paper. Returns are put into 7 buckets, and accuracy means landing in the right bucket. |
| **Result** | Bucket accuracy: Transformer 22.8%, LSTM 15.6%, LLM 15.3%. With 7 buckets, random guessing gets about 14%, so all three are close to guessing. Price error (RMSE): LSTM 180.9, LLM 1739.6. After **removing the LLM's broken outputs**, the LLM's RMSE drops to 33.9. |
| **Limits (theirs)** | Price only, one series, no news. The LLM often printed only the first digit of a number. |
| **Problems we found** | (1) The Transformer result is copied, not re-run, so it is not a fair comparison. (2) They removed the LLM's bad answers *after* seeing the results, which makes the LLM look better than it is. (3) GPT-3.5 was trained on internet text up to about 2021, so it may already "know" the 2005–2021 test prices (leakage). (4) Only one random-looking split; no walk-forward test. |
| **Research gap** | No news or evidence; no honest leakage control; one-shot forecast with no revision. |
| **How Reflica fills it** | We do **not** let the LLM predict numbers. The LLM only **reads and extracts claims**, and a numeric model (ARIMA or XGBoost) predicts CPI. That avoids the broken-number problem this paper shows. We use walk-forward testing and keep every failed output in the score. |
| **Trust** | **Low to medium** (small conference; copied baseline; outliers removed after the fact). |
| **Use for us** | **Low to medium.** Good to cite as proof that **LLMs are bad at predicting numbers directly**, which supports our design choice. |
| **How we can be better** | Run every baseline ourselves on the same split. Never delete bad outputs after seeing results. Check for leakage. |

---

### Paper 2. Stock up/down using news plus market numbers (MS-MI)

| Field | Answer |
|---|---|
| **Title** | A Comprehensive Multi-Source Multi-Instance Learning Framework for Predicting Stock Market Trends Utilizing Financial News and Market Indicators to Enhance Accuracy |
| **Authors** | Dr. N. Srivani, Chilukuri Dileep, Balla Vaishnavi, Bangaru Saptharshi, L. Shiva Ganesh Reddy, Mohammed Zaffer Sadik (CMR Institute of Technology, Hyderabad, India) |
| **Venue** | IEEE GSEACT 2026 (conference). DOI 10.1109/GSEACT68539.2026.11619959 |
| **Problem** | Predict whether the US Dow Jones index goes **up or down** each day, using news headlines plus price data. |
| **Method** | Kaggle dataset: 25 Reddit WorldNews headlines per day, 2008–2016, about 1,989 days. News goes through spaCy (finds who did what), VADER (positive or negative mood) and Word2Vec (word meaning), giving 104 numbers. Six price numbers are added: Open, High, Low, **Close**, Volume, **Adj Close**. That is 110 features in total. Models: SVM and XGBoost, with an 80/20 split. |
| **Result** | XGBoost: **95.8% accuracy**, F1 95.1%. SVM with prices only: 82.2%. |
| **Limits (theirs)** | They mention few; they claim to beat every earlier method. |
| **Problems we found** | **Very likely leakage.** The label is "did today's Close go up compared with yesterday?", but **today's Close and Adj Close are inputs**. The model can see the answer. That is why even the prices-only SVM gets 82%; real daily stock direction is usually about 50–55%. The 80/20 split also seems random rather than by date, which mixes future days into training. So 95.8% **cannot be trusted**. Reddit WorldNews is general world news, not financial news. |
| **Research gap** | Real event-level news use with honest time order is missing; no probability; no revision. |
| **How Reflica fills it** | Every input has an **evidence cutoff date** before the forecast is made. Every claim is stored with its source and date. Testing is **walk-forward by date**, never random. |
| **Trust** | **Low** (the target is leaked into the inputs). |
| **Use for us** | **Medium, as a warning.** The idea of pulling "who did what" events out of news is close to our claim extraction. Use it in the thesis as an **example of leakage** and explain how our timeline fields (creation date, evidence cutoff, target month, release date) prevent it. |
| **How we can be better** | Separate claims (not one mood score), honest dates, chronological testing, and simple baselines run ourselves. |

---

### Paper 3. Predicting India's household spending (MPCE) with LSTM

| Field | Answer |
|---|---|
| **Title** | AI-Driven Predictive Analytics for Monthly Per Capita Expenditure using Macroeconomic Indicators |
| **Authors** | A.V. Karthick, Nagarani Muthukrishnan, S. Suganya, G. Parimalarani, H. Sudarsan, Arun Kumar Parthasarathy (Alagappa University and Madurai Kamaraj University College, India; plus industry in the USA) |
| **Venue** | IEEE ICACRS 2025 (conference). DOI 10.1109/ICACRS67045.2025.11324119 |
| **Problem** | India's household spending survey (HCES) happens only once every few years. Can we estimate monthly per-person spending (MPCE) in between, using CPI, GDP growth and unemployment? |
| **Method** | Quarterly data from Q1 2011 to Q1 2023. MPCE is known for only **3 survey rounds** (2011-12, 2017-18, 2022-23); the other quarters are **filled in with a smooth curve (cubic spline)**. LSTM with 64 units, 4-quarter look-back, 70/15/15 split by time. Baselines: ARIMA, SVR, Random Forest. SHAP for explanation. |
| **Result** | LSTM: RMSE ₹121.46, MAPE 4.12%, R² 0.93. Random Forest R² 0.87, SVR 0.80, ARIMA 0.74. SHAP: **CPI inflation matters most**. |
| **Limits (theirs)** | Quarterly only; assumes old patterns continue; national level only; few variables. |
| **Problems we found** | (1) Only **3 real target values**. Everything else is a made-up smooth curve, so the model mostly learns the curve, and R² 0.93 means little. (2) About 49 quarters × 15% ≈ **7 test points**, which is too few. (3) The government **did not officially release the 2017-18 survey results** (they were withheld in 2019), so the source of that value must be checked. (4) They say the 2020 pandemic is "outside our training window", but their data covers 2011–2023, which contradicts that. (5) Figure 1 is only a "conceptual description", not a real plot. |
| **Research gap** | No text or evidence; no uncertainty (no range); no revision when new data arrives. |
| **How Reflica fills it** | We forecast **real monthly CPI**, which MoSPI publishes every month, so there is no invented target. We add **prediction intervals** and **evidence-based revision**. |
| **Trust** | **Low** (target mostly interpolated, tiny test set). |
| **Use for us** | **Medium.** It is **Indian**, it uses the **same Indian data sources** (MoSPI, RBI, CMIE), it shows CPI is the most important driver, and it cites Das & Das (2024), our closest India paper. Cite it for India context and the data list, not for its numbers. |
| **How we can be better** | Monthly real targets, about 10+ years of walk-forward test months, ARIMA and naive baselines, intervals, and logged revisions. |

---

### Paper 4. STCInterLLM: causal checking plus an LLM for city forecasting

| Field | Answer |
|---|---|
| **Title** | Causal Intervention Is What Large Language Models Need for Spatio-Temporal Forecasting |
| **Authors** | Shijie Li, He Li, Xiaojing Li, Yong Xu, Zhenhong Lin, Huaiguang Jiang (South China University of Technology; Guangdong University of Technology, China) |
| **Venue** | **IEEE Transactions on Cybernetics**, vol. 55, no. 8, Aug 2025 (Q1 journal). DOI 10.1109/TCYB.2025.3569333. Code: github.com/lishijie15/STCInterLLM |
| **Problem** | Predict power load (with solar and wind) and taxi traffic across many places when data is scarce. Two issues: (a) the model links places that are not really connected (**false links**), and (b) the LLM **makes things up** (hallucination). |
| **Method** | (1) A **causal intervention encoder** removes false links between places. (2) **Chain-of-Action prompts** make the LLM predict step by step. (3) A small alignment module connects the encoder to a **frozen LLM** (Vicuna-7B). Data: a power grid in Colorado (USA) with the IEEE 8500-node feeder, and NYC taxi data. Trained on 8 large GPUs (A800/H100). |
| **Result** | Better than 7 models (GRU, T-GCN, AGCRN, MegaCRN, MPGTN, UrbanGPT …) by **at least 7.46% MAE, 8.12% RMSE and 14.60% MAPE**. Ablation tests show each part helps. |
| **Limits (theirs)** | Plan to try climate and hospital demand next. |
| **Limits we see** | Needs **very expensive GPUs**; numbers only (no news); short horizon (up to 12 hours); one point forecast with no uncertainty; no revision; USA/China data only. |
| **Research gap** | Uses causal ideas to clean **number links**, not to judge **news evidence**. No forecast revision, no economics, no India. |
| **How Reflica fills it** | We borrow the **idea**, not the model: before evidence changes a forecast, check that it is truly **relevant** (not a false link). Our 4 revision checks (novelty, reliability, relevance, strength) play that role, in a cheap and explainable way. |
| **Trust** | **High** (Q1 journal, public code, ablations). |
| **Use for us** | **Low to medium.** Different domain (traffic and power). Cite it for "LLMs hallucinate, so add a check step" and "false links must be removed". |
| **How we can be better** | Our method runs on a laptop or free tier, works on monthly economic data, explains every revision in a log, and reports intervals. |

---

## Part 1b. Second batch of uploads (full text read, 15 Oct 2026)

The second upload of STCInterLLM is the **same file** as Paper 4 (identical checksum), so it is not reviewed again.

### Paper 5. Chaos + ML hybrid for India CPI inflation ⭐ (most relevant so far)

| Field | Answer |
|---|---|
| **Title** | Chaos, Machine Learning and Deep Learning based Hybrid to forecast Consumer Price Index Inflation in India |
| **Authors** | Vangala Sarveswararao (University of Hyderabad) and Vadlamani Ravi (IDRBT, Hyderabad, the RBI's banking-technology institute), India |
| **Venue** | IEEE SSCI 2020 (Symposium Series on Computational Intelligence, Canberra; a good conference) |
| **Problem** | Forecast **India's monthly CPI inflation**: headline, food & beverages, and fuel & light. |
| **Method** | Two stages. **Stage 1** tests whether the series behaves "chaotically" (Lyapunov exponent; all 3 series do) and rebuilds the inputs using the best lag and number of past values (Cao's method). **Stage 2** runs 9 models on those inputs: RF, SVM, MLP, XGBoost, KNN, LSTM, ARIMA, GMDH and GRNN. Data: MoSPI monthly CPI inflation from **Jan 2012 to Dec 2018 (84 months)**. Test set: the **last 6 months only**. Metrics: SMAPE, Theil's U (below 1 means better than "no change"), direction accuracy, and the Diebold–Mariano test. |
| **Result** | **GRNN with chaos** was best on headline CPI: SMAPE 10.32, Theil's U 0.58, direction correct 83%. Compared with the earlier RBI paper (Pratap & Sengupta 2019), SMAPE improved by 15.5% (headline), 60% (fuel) and 63% (food). **LSTM did badly** because there is too little data. |
| **Limits (theirs)** | LSTM needs more data. |
| **Problems we found** | (1) Only **6 test months**, which is far too few to trust. (2) Their own **Diebold–Mariano test shows the top two models are NOT significantly different** (p = 0.96, 0.65, 0.62), so "GRNN is best" is not proven. (3) Hyperparameters were tuned, but they don't say on which data; if it was the test months, that is leakage. (4) One fixed split, not walk-forward. (5) Numbers only: no news, no evidence, no forecast range. (6) Old base year (2012 = 100); India moved to the new **2024 = 100** series in 2026. |
| **Research gap** | Numbers-only CPI forecasting; tiny test; no uncertainty; no revision; no text. |
| **How Reflica fills it** | Same target (India CPI) but tested on **many walk-forward months**, with a **significance test** (Diebold–Mariano) reported honestly, prediction intervals, and dated news evidence used only to decide **revisions**. |
| **Trust** | **Medium** (good venue, Indian experts, real MoSPI data; but a tiny test set and no significant winner). |
| **Use for us** | **Very high.** Our closest **numeric India CPI** paper. Use it to: (a) take their **baseline list** (ARIMA, RF, SVM, XGBoost, MLP, GRNN); (b) take their **metrics** (SMAPE, Theil's U, direction accuracy, DM test); (c) show that "LSTM fails on small data", which supports simple models; (d) cite **Pratap & Sengupta (2019, RBI Working Paper 04/2019)**, another India CPI ML paper we should add. |
| **How we can be better** | 60+ test months instead of 6, significance tests, intervals, the new 2024 base series, and evidence-aware revision. |

---

### Paper 6. STEM: an event knowledge graph for time series

| Field | Answer |
|---|---|
| **Title** | Constructing the Simple Timeseries Event Model |
| **Author** | Simon Schramm (University of Bamberg and BMW Group, Germany), single author |
| **Venue** | IEEE ICKG 2023 (International Conference on Knowledge Graph) |
| **Problem** | How do we **store events** (e.g. COVID, the Inflation Reduction Act) together with **time series** (car sales, inflation, GDP) in one knowledge graph, so forecasts can later be **explained**? The older "Simple Event Model" (SEM, 2011) cannot record "humans think event X affected Y". |
| **Method** | Designs an **ontology** (a data schema) called STEM. Core classes: **Event** (what), **Actor** (who), **Place** (where), **Time** (when), **Impact** (who is affected). Numbers are attached to the **links** (e.g. "Inflation Reduction Act → hasImpact(−1) → Germany"). There are **Authority vs User** views (official source vs human opinion) and a **View** for **conflicting opinions**. Example: the US car market (BMW, Tesla) with inflation and GDP. |
| **Result** | **No forecasting results at all.** It is a design paper, shown with an example. |
| **Limits (theirs)** | Links about the future rest on human judgement, so they are **uncertain**; the schema covers only one event type (macro event → market). |
| **Research gap** | The graph is never used to **forecast or revise** anything; no accuracy test; no automatic extraction (humans add links). |
| **How Reflica fills it** | Our evidence graph is a **working version** of this idea: an LLM extracts each claim (who, what, when, source, direction), stores it with a **date and source**, and the revision rule **uses** it to decide whether to change the CPI forecast. Then we **measure** whether it helps. |
| **Trust** | **Medium** (sound design; no experiments to trust or distrust). |
| **Use for us** | **High for design.** Borrow its schema ideas for our claim record: event, actor, place, time, impact (direction and size), **source type (official vs other)** and **conflicting views**. Cite it as "event KGs for explainable time-series forecasting exist only as designs". |
| **How we can be better** | Use the graph in a real forecasting loop and report MAE, RMSE and revision quality. |

---

### Paper 7. LLM chain-of-thought for car paths at traffic signals

| Field | Answer |
|---|---|
| **Title** | LLM-Driven Trajectory Prediction at Intersections with Chain-of-Thought Reasoning |
| **Authors** | Yanbin Liu, Guangyu Tian, Wei Zhong, Xiaojing Qi, Yiran Wang (Tsinghua University and South China University of Technology, China) |
| **Venue** | IEEE IC-NIDC 2025 (conference) |
| **Problem** | Predict where a car will go in the next 5 seconds at a traffic signal, safely and fast. Old models ignore traffic rules (19% violate signals), and GPT-4 is too slow (over 500 ms). |
| **Method** | (1) **Step-by-step prompts (chain-of-thought)** make GPT-4 Turbo reason about signals and right-of-way. (2) **Knowledge distillation**: a small model (Qwen-1.5) learns to copy GPT-4's reasoning, so it is fast and cheap. (3) A fusion network joins this with speed and position data **without using future information**. They release their own dataset, **SIGNAL** (Zhejiang test zone, China). |
| **Result** | Position error 0.93 m average and 1.86 m final, **23% better** than the best baseline (V2X-TrajNet); signal violations 1.7%; 28 ms on a small Jetson device. |
| **Limits** | Their own new dataset (hard to check); one target vehicle only; one region in China. |
| **Research gap** | Not economics; no evidence over days or months; no revision. |
| **How Reflica fills it** | Not directly. We borrow **two ideas**: (a) **step-by-step prompts** for claim extraction (read → find claim → date → direction → strength), which reduce LLM mistakes; (b) a **big LLM teaches a small free model**, which keeps us on a free budget. |
| **Trust** | **Medium** (conference, own dataset). |
| **Use for us** | **Low.** Cite only for "chain-of-thought reduces LLM errors" and "distil a big LLM into a small one to save cost". |
| **How we can be better** | Not comparable (different field). |

---

### Paper 8. Online News-Based Economic Sentiment Index (Korea) (assigned paper A1)

| Field | Answer |
|---|---|
| **Title** | Online News-Based Economic Sentiment Index |
| **Authors** | Nathaniel Kang, Dongeun Min, Yonghun Cho, Dong-Whan Ko, Hyun Hak Kim, Joon Yeon Choeh, Jongho Im (Yonsei, Kookmin and Sejong Universities, Korea National Defense University) |
| **Venue** | **IEEE Transactions on Big Data**, vol. 11, no. 3, 2025 (journal). DOI 10.1109/TBDATA.2024.3474211 |
| **Problem** | Official economic data comes **late** and gets **revised**; surveys are slow and costly. Can **daily news** give a faster index of how an industry is doing? |
| **Method** | (1) About **49 million** Korean news articles (2010–2021), sampled down. (2) 4,000 hand-labelled articles train **two KoBERT models**: one for "is this about ICT?" (relevance) and one for positive, neutral or negative tone (sentiment). (3) Each article becomes a small picture of its scores, and pictures are **clustered** into 6 groups. (4) **MCDA** (a multi-criteria ranking method) weights the clusters into one index, **ICT-NSI**. (5) Test: predict quarterly **ICT-GDP growth** with a VAR model using NSI, vs the survey index ICT-BSI. Train 2010–2019; test **2020–2021 (8 quarters)**. |
| **Result** | Out-of-sample RMSE **1.718 (news) vs 1.736 (survey)**; MAE 1.441 vs 1.501. In-sample RMSE 0.952 vs 1.164. |
| **Limits (theirs)** | Only one industry (ICT) and one country; news only (no social media); not real-time yet; suggest LLMs and adaptive weights in future. |
| **Problems we found** | (1) The out-of-sample gain is **tiny (about 1% RMSE)** on only **8 quarters**, with **no significance test**, so it may be luck. (2) They **chose the MCDA method by its correlation with actual ICT-GDP**, which uses the answer to build the index (a mild leakage). (3) No simple baseline such as "GDP alone" (AR model). (4) The whole news flow becomes **one number**, so you cannot see **which** news moved it. |
| **Research gap** | One aggregate mood index; no claim-level evidence, sources or dates; no forecast revision; not India; not CPI. |
| **How Reflica fills it** | We keep **each claim separately** (source, date, direction, strength), so every forecast change can be **traced to specific news**. We use the evidence for **revision decisions**, test on many months, and add significance tests and simple baselines. |
| **Trust** | **Medium** (good journal and a careful pipeline; but a weak, tiny out-of-sample test). |
| **Use for us** | **High.** It is the best example of the "**news → one sentiment index → forecast**" approach that we improve on. Its **relevance + sentiment** scoring is like our **relevance + direction** checks. Its point that official data is **late and revised** supports recording CPI release dates. |
| **How we can be better** | Claim-level and explainable instead of one index; honest leakage control; more test periods; India CPI; revision log. |

---

## Part 2. Other papers related to our topic

**Abstract-level only** unless marked. Full details are in `LITERATURE_MATRIX.md`.

### 2a. India CPI and inflation forecasting (closest domain)

| Paper | Problem → Method | Result | Gap | Trust / Use for us |
|---|---|---|---|---|
| **Das & Das (2024)**, *Int. J. of Economics and Finance*, "Improvement in Inflation Forecasting: Ensembling Text Mining with Macro Data…" | India inflation → 3.9 million newspaper headlines turned into **monthly text series**, plus macro data, in ML ensembles | Text **improved** the forecast | Text averaged into one series; no separate claims, no sources, no revision | Medium / **Very high**: our closest India paper, **read in full first** |
| **Mohan et al., RBI Bulletin (Jun 2025)** | India headline and core CPI → weighted mix of statistical, ML and deep models | Mix beats single models | Numbers only; no text, no revision | High / **High**: our official **baseline** |
| **IEEE WiSPNET 2024** (Amrita) | CPI for industrial workers → LSTM, BiLSTM, XGBoost, RF | (check full text) | Different CPI series; numbers only | Medium / Medium |
| **IEEE INOCON 2023** (Christ University) | India CPI → statistical vs LSTM | **Simple statistical model beat LSTM** | Numbers only | Medium / **High**: proves we need simple baselines |
| **RBI study (2023)**, ML vs econometrics | India inflation, quarterly 1996–2022 → ANN, LSTM vs ARIMAX | Mixed; ARIMAX good after COVID | Quarterly; numbers only | High / Medium |
| **Sarveswararao & Ravi (2020)**, IEEE SSCI: **full review in Paper 5 above** | India CPI (headline, food, fuel) → chaos + 9 ML models | GRNN best, but not significantly | 6 test months; numbers only | Medium / **Very high** |
| **Pratap & Sengupta (2019)**, RBI Working Paper 04/2019, "Macroeconomic Forecasting in India: Does Machine Learning Hold the Key to Better Forecasts?" (found via Paper 5) | India CPI → ML models | Baseline for Paper 5 | Numbers only | High / **High**: **get the full text** |
| **Mahajan & Srinivasan (2019, CAFRAL)** | Emerging markets incl. India → deep networks | Good, **except 1-month ahead** | Numbers only | High / **High**: 1-month ahead is our horizon and is hard |

### 2b. News or LLMs for inflation (closest method; mostly outside India)

| Paper | Problem → Method | Result | Gap | Trust / Use |
|---|---|---|---|---|
| **InflaBERT**: Allard, Teiletche, Zinebi (2024), arXiv 2410.20198 | US → BERT reads news and builds an inflation-mood **index** for the nowcast | Small gain (mainly in the pandemic) | One index; no claims; no revision | Medium / **High** |
| **PIER Thailand, Discussion Paper 252 (May 2026)**, "News-Based Inflation Expectations: LLM-Assisted Measurement and Forecasting" (earlier wrongly listed as "BIS 2026") | Thailand → LLM reads 1.1 million Thai news articles (2015–2024) and builds an inflation-expectation index | RMSE down up to 32% (headline) vs autoregressive models | One index; **not India** | Medium-high / **High** |
| **ChatMacro, FRB San Francisco (2026)** | US → GPT-4 forecasts in real time (2024–25) | LLM forecasts were **stale: they barely changed** when new data came | No evidence trail; no revision rule | High / **Very high**: it shows LLMs **fail to revise**, which is our exact problem |
| **St. Louis Fed (2023)**, PaLM | US → LLM as forecaster | Beat the expert survey | **Likely leakage** (model saw the period) | Medium / Medium: leakage example |
| Russia (RJMF 2025), Philippines (BSP), Brazil (PROPOR 2026), France (BdF 2026), China (LLM-CPI 2025) | News or social-media mood indices + ML | Usually helps | All use **one mood number**; none are India; none revise | Medium / Medium |

### 2c. Forecast revision (our main contribution area)

| Paper | Idea | Use for us |
|---|---|---|
| **Int. J. of Forecasting (2000)**, study on updating forecasts | Updating helps for trending series, not for stable ones | **High**: supports "update only when needed" |
| **Stability metric**, arXiv 2601.10863 | Penalise forecasts that flip back and forth | **High**: a way to count unnecessary revisions |
| Statistical-agency revision rules (UN, US Census, ECB) | Many small revisions vs few revisions | Medium: defines our "always" vs "never" update baselines |
| Cleveland Fed nowcasting | Update every time new data arrives | **High**: the "always update" baseline |

### 2d. Leakage (making our test fair)

| Paper | Idea | Use for us |
|---|---|---|
| **Lookahead-bias test**, Gao, Jiang, Yan (arXiv 2512.23847) | Tests whether an LLM "remembers" the answer; the gain disappears after its training cutoff | **Very high**: we will run this check |
| **ChronoBERT**, Chen et al. (arXiv 2502.21206) | Models trained only on text up to each date | Medium: an option, or note it as a limit |

### 2e. Your earlier 22-paper list (`Research_Work_paper.docx`)

Those papers cover wars, Chinese stocks, oil prices, traffic, electricity, migration and ForecastBench. For **Minor 1 (CPI)** they matter less. The most useful ones are:
- **From News to Forecast** (NeurIPS 2024): LLM agents pick news and **reflect and fix** forecasts. This is the closest idea to our revision step. **High use**; read it in full.
- **Event causality mining** and **oil price with news graph** (2025–26): the evidence-graph idea. Medium use.
- **ForecastBench**: honest live scoring; it fits **Minor 2** (probabilities and abstention) more than Minor 1.
- **NIFTY big-move LLM paper (2026)**: the only Indian one there, but about the stock market. Low to medium use.

Your 5 gaps (no calibration, no "I don't know", no live testing, no effects, no India) are mostly **Minor 2 and thesis** gaps. Minor 1 focuses on gap 3 (honest time testing), gap 5 (India) and the **revision** gap below.

---

## Part 3. Summary: the gap and how Reflica is better

**What everyone does:** they predict a number once, from past numbers or from one "news mood" score. Many test with a random split or let the model see the future (leakage).

**What nobody does (so far, from what we checked):** for India CPI, uses **separate dated claims with sources** to decide **whether to change** a forecast, **logs why**, and proves this beats **never updating** and **always updating** in an honest walk-forward test.

| Problem we saw in papers | Reflica's answer |
|---|---|
| LLMs garble numbers (Paper 1) | LLM only extracts claims; a numeric model forecasts |
| Answer leaked into inputs (Paper 2) | Every forecast records creation date, evidence cutoff, target month and release date; nothing after the cutoff is used |
| Made-up targets, tiny tests (Paper 3) | Real monthly CPI; many walk-forward test months |
| Hallucination and false links (Paper 4) | 4 revision checks: novelty, reliability, relevance, strength |
| One mood score (InflaBERT, PIER Thailand, Das & Das, RBI food-news index) | Separate claims, each with source and date |
| LLM forecasts don't update (ChatMacro) | An explicit revision rule, tested against never and always update |
| No uncertainty | Prediction intervals and coverage |

**Honest caution:** this gap is based on full text for 4 papers and abstracts for the rest. Before we claim novelty, read Das & Das 2024, the RBI food-inflation news paper (2021), Pratap & Sengupta 2019, ChatMacro, InflaBERT and From News to Forecast in full.
