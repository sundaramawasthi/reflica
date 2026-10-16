# Literature Records: Five Priority Papers (Step 1)

> **Date:** 16 October 2026 · **Purpose:** one consistent seven-point record per priority paper, before G3 and G2 are investigated.
> **Source rule:** each record is compiled **only** from our existing reading notes:
> - `../../docs/research_archive/literature/LEVEL2_READINGS.md` (§1, §8, §12, §13, §16)
> - `../../docs/research_archive/literature/VERIFICATION.md`
> - `../../docs/research_archive/research_gaps/CLOSEST_METHODS.md`
>
> Nothing was re-read or added from memory. **"n.r."** = not recorded in our notes; fill it from the paper, never guess.
> **Limitations** are split into **(authors)**, stated by the paper itself, and **(ours)**, our own observations. Where our notes do not say who raised a limitation, it is listed under (ours).
> **Reading level:** F = full text · K = key sections · A = abstract only.

| # | Paper | Read | Gaps it bears on |
|---|---|---|---|
| P1 | Mohan et al. (2025), RBI Bulletin | F (article text; charts and equation images missing) | G2, G3 (numeric baseline) |
| P2 | Pratap, Ranjan, Kishore & Bhoi (2021), RBI Occasional Papers | F | G3 |
| P3 | Das & Das (2024), IJEF | F | G3 |
| P4 | Ye et al. (2026), Forecast-Dojo | K (method, prompt appendix, results) | G1, G2 |
| P5 | Zhao et al. (2026), LiveMacroEval | F (main text + key appendices) | G1, G2 |

---

## P1. Mohan, Hasan, Roy, Sarkar & John (2025): "Predicting CPI Inflation in India: Combining Forecasts from a 'Suite' of Statistical and Machine Learning Models", RBI Bulletin, 25 June 2025

| Point | Record |
|---|---|
| **1. Research problem** | Can combining many statistical, ML and DL models produce better India CPI inflation forecasts than single models? |
| **2. Dataset and time period** | NSO CPI, **Jan 2012 – Jul 2024**; headline and core (excluding food and fuel). Exogenous variables: Indian-basket crude price (PPAC), INR–USD, real GDP and output gap (HP filter; quarterly → monthly by Denton–Cholette), repo rate. **Target:** X-13 seasonally adjusted, **seasonally adjusted annualised rate (SAAR)**, not y-o-y |
| **3. Methodology** | **216 models**: 108 specifications × 2 rolling windows (36 and 96 months). Statistical (RW, AR, MA, ARMA(X), ARCH-type, VAR, BVAR); ML (SVM, ensembles, RF, GPR, NARNET(X)); DL (LSTM). **Performance-weighted combination** using each model's recent 12-month RMSE. Density: RMSE-weighted split-normal bands. MATLAB toolbox |
| **4. Baselines** | Random walk; simple-average combination; the individual models |
| **5. Evaluation metrics** | Pseudo-out-of-sample, horizons 1–12 months; RMSE; **Diebold–Mariano with Harvey–Leybourne–Newbold correction**; Wilcoxon signed-rank |
| **6. Findings and limitations** | **Findings:** average RMSE across horizons ~**70% lower than the random walk**; the combination beats >75% of models at all horizons; performance weighting is never significantly worse than the simple average, and is better in 12/16 cases (headline, 3-year window) but only 2/16 (headline, 8-year window); 2024 outcomes fell within the forecast range. **Limitations (ours):** numbers only (no text, no news, no revision logic); pseudo-OOS with **no real-time vintages**; full-sample HP output gap; SAAR target not comparable with y-o-y errors; charts and equations not available to us, so the weighting formula and RMSE levels are **unverified**. **Limitations (authors):** n.r. |
| **7. Relevance and gap left** | **The official India numeric baseline to match or beat.** Reusable: rolling 36/96 windows, performance weighting, split-normal bands, DM+HLN tests, exogenous set. **Gap left:** it does not test whether **text** or **revision** helps. A reduced Mohan-style suite must be **re-implemented on our own target** (y-o-y, our origins). Also cites John, Singh & Kapur (2020), RBI WP 11/2020 (to read) |

---

## P2. Pratap, Ranjan, Kishore & Bhoi (2021): "Forecasting Food Inflation using News-based Sentiment Indicators", RBI Occasional Papers 42(2)

| Point | Record |
|---|---|
| **1. Research problem** | Does news sentiment about tomato, onion and potato (TOP) prices improve food-inflation forecasts in India? |
| **2. Dataset and time period** | Monthly. **Target:** CPI-Vegetables and CPI-Food & beverages, m-o-m and y-o-y (**not headline CPI**). Train Jan 2011 – Aug 2019; **test Sep 2019 – Aug 2021 (24 months)**. News: nine English dailies (not named) via Meltwater, keyword-filtered. Article counts not given |
| **3. Methodology** | Lexicon sentiment (Loughran–McDonald, valence-shifting bigrams, R *sentometrics*) → document score → **daily net sentiment score (NSS)** → monthly regressor or daily MIDAS input. Models: ARIMA, SARIMA (± NSS, ± exogenous: global food prices, rainfall, MSP); VAR with DCA daily prices vs VAR with NSS; MIDAS |
| **4. Baselines** | **AR(1)** benchmark; the same models without NSS |
| **5. Evaluation metrics** | Rolling-window out-of-sample, h = 1–12; **relative RMSE vs AR(1)**. **No significance tests** |
| **6. Findings and limitations** | **Findings: mixed.** Veg m-o-m h=1: SARIMA+NSS 0.93 vs SARIMA 0.95 (small gain). Veg y-o-y h=1: SARIMA+NSS 0.79 vs SARIMA 0.77 (**news slightly worse**). Food y-o-y: VAR-NSS 0.44 at h=1. MIDAS food y-o-y worse than AR(1) at several horizons. **Limitations (authors):** no uncertainty estimates (stated explicitly, p.26). **Limitations (ours):** aggregate index, not claims; NSS always included (no revision mechanism); no source reliability or novelty weighting; short test window including COVID; some duplicated table rows; generic finance lexicon for farm news; newspapers unnamed; no release-date alignment or vintages |
| **7. Relevance and gap left** | **Closest India "news + inflation" study.** Reusable: keyword pre-filter; DCA daily retail prices and Agmarknet arrivals; AR(1)/SARIMA(+exogenous) baselines; relative-RMSE-by-horizon reporting; the lexicon NSS as a cheap **index baseline**. **Gap left:** no claim-level evidence, no decision about revising an issued forecast, no significance tests; food/vegetable CPI only |

---

## P3. Das & Das (2024): "Improvement in Inflation Forecasting: Ensembling Text Mining with Macro Data in Machine Learning Models", International Journal of Economics and Finance 16(6): 92–101 (DOI 10.5539/ijef.v16n6p92)

| Point | Record |
|---|---|
| **1. Research problem** | Do newspaper-headline text features, combined with macroeconomic data, improve inflation forecasts for India with ML models? |
| **2. Dataset and time period** | **India confirmed:** Times of India headlines only (Kulkarni's Kaggle / Harvard Dataverse corpus); ~3.9 million headlines, 2001–2023. CPI from Jan 2012. **Exact CPI series, y-o-y vs m-o-m, and horizon: not stated** |
| **3. Methodology** | Monthly relative frequencies of **166 dictionary words**. No sentiment polarity. Dictionary built from words appearing "in at least 75% of the months (200 out of 270 months)", over **2001–2023**. The step from 1,415 to 166 words is undocumented. ML models with and without text (ANN, RF, Elastic Net, …) |
| **4. Baselines** | The same ML models **without text** |
| **5. Evaluation metrics** | **Single 70/30 train/test split** (~40 test months; ordering not stated); RMSE / relative RMSE. **No significance tests** |
| **6. Findings and limitations** | **Findings:** best model ANN with text RMSE **1.560** vs best no-text RF **1.654** (~6% better). **Text worsened** Elastic Net and RF (RF 1.654 → 1.900). The paper's claim that text models "consistently demonstrate lower Relative RMSE" **contradicts its own table**. **Limitations (ours):** dictionary built on a window that **includes the test period** (look-ahead risk); single split; no significance tests; no revision mechanism, claim provenance or intervals; target series unclear. **Limitations (authors):** n.r. |
| **7. Relevance and gap left** | Directly relevant to **G3**. Reusable: the 166-word list as a **word-frequency index baseline**, rebuilt on a pre-test window only and lagged to pre-release information; the ToI corpus as a dated source. **Gap left:** evidence that text helps India CPI is **weak and mixed**; no fair, point-in-time test |

---

## P4. Ye, Wang, Ahmed, Zhang, He, Lin, Yin, Peng, Galarnyk, Chava & Zhang (2026): "Forecast-Dojo: Replayable Environments for Benchmarking and Training LLM Forecasting Agents", arXiv 2609.28876v1 (Georgia Tech, Amazon, Univ. of Florida)

| Point | Record |
|---|---|
| **1. Research problem** | How can LLM forecasting agents be benchmarked and trained fairly on events, with evidence arriving over time and without outcome leakage? |
| **2. Dataset and time period** | **1,568 resolved Polymarket events** (binary and multiple-choice); **18.8M dated news articles, 2025-03 to 2026-06** |
| **3. Methodology** | Replayable environment: agents **revisit predictions at successive historical dates**. Point-in-time controls: URL, title and MinHash near-duplicate removal (earliest-published kept); reliable timestamps; content-level outcome-leakage screen; model knowledge cutoffs before the evaluation period. Optional **belief notebook**: an append-only `evidence_ledger` (claim, supports/rules_out, `date_observed`, status active/superseded, provenance note). The agent keeps p "consistent with the active ledger … moved only as far as that evidence justifies" |
| **4. Baselines** | **Market prices**; memory-off (no notebook) vs memory-on; with and without research tools; 12 models |
| **5. Evaluation metrics** | **Brier score** and accuracy |
| **6. Findings and limitations** | **Findings:** research tools lower Brier for all 12 models. Gains concentrate where more new evidence was recorded (step Brier change −0.007 in the lowest quartile vs −0.071 in the highest). The notebook lowers research cost but **does not consistently improve** quality (better for 6 models, worse for 6). **All models trail the market** (best 0.546 vs market 0.498). **Limitations (ours):** revision is left to **LLM judgement**, with no explicit or pre-registered gate; novelty, reliability, relevance and strength are not scored numerically; the LLM is the forecaster; events, not inflation; no update-policy comparison; we read key sections only. **Limitations (authors):** n.r. |
| **7. Relevance and gap left** | **Closest prior design to our evidence ledger** (claim-level, dated, provenance, supersession). Reusable: dedup rules, leakage screen, ledger fields. **Gap left:** no scored, explicit revision rule; no numeric target; no never/always/small-step comparison. Relevant to Part A as a replay-benchmark design |

---

## P5. Zhao, Zhang, Ye, Cao, Xie & Chava (2026): "Can LLMs Take the Pulse of the Economy? A Real-Time Evaluation of LLM Nowcasts on Macroeconomic Indicators" (LiveMacroEval), arXiv 2608.30110v1 (Georgia Tech, UC San Diego)

| Point | Record |
|---|---|
| **1. Research problem** | Can web-search LLM agents nowcast headline macro indicators before their official release? Historical tests are contaminated by memorisation, so evaluation must be **live** |
| **2. Dataset and time period** | **16 US indicators** in 4 themes, including **CPI All Items (YoY %)**, PPI, PCE prices, GDP, payrolls, unemployment, housing. Live target months **Nov 2025 – Mar 2026** (releases 1 Dec 2025 – 5 May 2026). Agent-design study Jul–Aug 2026 |
| **3. Methodology** | GPT-5, Claude-sonnet-4.5, Qwen3-235B, Qwen3-80B with web search. **Hourly** nowcasts from the last week of the reference month until the release. A strict prompt fixes units and transformation, and has **no slot for the previous nowcast**. **No explicit update rule.** Revisions are attributed to events after the fact (e.g., EIA report and FOMC minutes, 8 Apr 2026). No-copying tests; post-release snap test |
| **4. Baselines** | Bloomberg ECOS consensus (median); 5 Fed regional-bank nowcasts (Cleveland Fed for CPI); **univariate auto-ARIMA fitted once and frozen for the window** |
| **5. Evaluation metrics** | **LiveMacro Score** (model-implied vs realized E-mini S&P return in a [−5, +30] min window; bounded out-of-sample R²; 0 = consensus); **LiveBetting Score** (hourly simulated Polymarket bets); squared relative error (appendix only); 90% bootstrap CIs |
| **6. Findings and limitations** | **Findings:** GPT-5 ties the consensus (+0.004, not significant); the other agents are below the consensus but above ARIMA (Qwen3-80B ≈ ARIMA). **CPI, retail sales and PCE prices = 87% of the average agent's shortfall**; on CPI, the Cleveland Fed and the consensus beat all agents. Agents do better on supply/production and housing. A multi-agent team (smaller predicted surprises, 54% vs 38% correct direction) is the only design above consensus (+0.020). **Limitations (authors):** few release events; **US-only** (non-US left to future work). **Limitations (ours):** point nowcasts only (no intervals or probabilities); no update-policy comparison; market-based metrics are not directly comparable with MAE/RMSE |
| **7. Relevance and gap left** | **Most important check for G2, now done:** no explicit or scored rule and no policy comparison, so **G2 survives, narrowed (gap v7)**. LLMs are weakest on CPI, which supports a **numeric forecaster plus text evidence**. Smaller-change designs score better, which supports **bounded** revisions. **G1:** US only, numeric nowcasts not yes/no, so it does not cover an India benchmark. Template for a live, contamination-resistant design |

---

## Cross-paper summary

| | P1 Mohan | P2 Pratap | P3 Das & Das | P4 Forecast-Dojo | P5 LiveMacroEval |
|---|---|---|---|---|---|
| India | ✅ | ✅ (food/veg) | ✅ | ❌ | ❌ (US) |
| CPI target | ✅ (SAAR) | Partly | ✅ (series unclear) | ❌ | ✅ (US CPI YoY) |
| Uses text | ❌ | ✅ index | ✅ word counts | ✅ articles + ledger | ✅ web search |
| Claim-level evidence | ❌ | ❌ | ❌ | ✅ | ❌ |
| Revises an issued forecast | ❌ (re-estimates) | ❌ | ❌ | ✅ (LLM judgement) | ✅ (LLM, stateless prompt) |
| Explicit revision rule | ❌ | ❌ | ❌ | ❌ | ❌ |
| Update-policy comparison | ❌ | ❌ | ❌ | Partly (memory on/off) | ❌ |
| Significance tests | ✅ DM+HLN | ❌ | ❌ | n.r. | Bootstrap CIs |
| Uncertainty | ✅ split-normal | ❌ | ❌ | Probabilities (Brier) | ❌ |

**Next (Step 2):** the G3 comparison across P1–P3.
