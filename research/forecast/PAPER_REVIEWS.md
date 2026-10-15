# Paper reviews in simple language (15 Oct 2026)

For Minor 1: **predict next month's India CPI inflation, and decide when to change (revise) the forecast using dated evidence.**

For every paper this file answers: who wrote it, the title, the problem, the method, the result, the limits, the research gap, how Reflica fills that gap, how useful it is for us, and how Reflica can do better.

**How to read the ratings**
- **Trust** asks whether we can believe the paper's numbers. *High* means a strong journal, public code and fair testing. *Low* means a serious testing mistake.
- **Use for us** asks how much the paper helps Minor 1 (India CPI and forecast revision).

Part 1 covers the 4 papers you uploaded, which I read in **full text**. Part 2 covers the other related papers. Most of those were read at **abstract level only**, so read each one fully before citing it.

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
| **Mahajan & Srinivasan (2019, CAFRAL)** | Emerging markets incl. India → deep networks | Good, **except 1-month ahead** | Numbers only | High / **High**: 1-month ahead is our horizon and is hard |

### 2b. News or LLMs for inflation (closest method; mostly outside India)

| Paper | Problem → Method | Result | Gap | Trust / Use |
|---|---|---|---|---|
| **InflaBERT**: Allard, Teiletche, Zinebi (2024), arXiv 2410.20198 | US → BERT reads news and builds an inflation-mood **index** for the nowcast | Small gain (mainly in the pandemic) | One index; no claims; no revision | Medium / **High** |
| **BIS working paper (2026)** | Emerging economies → LLM news index | Error down up to 32% | One index; **check if India is included** | High / **High** |
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
| One mood score (InflaBERT, BIS, Das & Das) | Separate claims, each with source and date |
| LLM forecasts don't update (ChatMacro) | An explicit revision rule, tested against never and always update |
| No uncertainty | Prediction intervals and coverage |

**Honest caution:** this gap is based on full text for 4 papers and abstracts for the rest. Before we claim novelty, read Das & Das 2024, the BIS 2026 paper, ChatMacro, InflaBERT and From News to Forecast in full.
