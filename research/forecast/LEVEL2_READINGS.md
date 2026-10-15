# Level-2 (content) readings: full text (15 Oct 2026)

**Method.** Five full-text PDFs were provided by the user. Each was read in full by a separate reader against the 11-point checklist in `VERIFICATION.md` §F. The key claims were then **spot-checked by hand against the extracted text**: quotes and numbers for NTF Tables 1–2, the reflection wording, the TOP target series and evaluation window, and the Pratap & Sengupta SARIMA result and test set.

**Not yet read at Level 2:** Mohan et al. (RBI Bulletin 2025), O'Connor et al. (2000), Das & Das (2024).

---

## 1. Pratap, Ranjan, Kishore, Bhoi (2021): Forecasting Food Inflation using News-based Sentiment Indicators

*RBI Occasional Papers 42(2), 2021. Received 1 Jun 2022, accepted 13 Jul 2022. The SSRN 4125337 copy is the same paper. The text contains no "Catching up on the TOP News" title, so the ResearchGate record title is unexplained.*

| Item | Finding (printed page) |
|---|---|
| Target | CPI-Vegetables and CPI-Food & beverages, m-o-m and y-o-y (p.18). **Not headline CPI.** |
| Data | Monthly. Train Jan 2011–Aug 2019; **test Sep 2019–Aug 2021 (24 months)**. News from nine English dailies (not named) via Meltwater; keyword filter (commodity + supply-demand + price words) (p.11). Article counts are not given in the text. |
| How news enters | Lexicon sentiment (Loughran-McDonald, valence-shifting bigrams, R *sentometrics*) → document score → **daily net sentiment score (NSS)** → monthly regressor or daily MIDAS input (pp.13–14, 24). **Aggregate index, not claims.** |
| Revision mechanism | **None.** NSS is always included as a regressor. |
| Evidence properties | Relevance via keywords only. No reliability, novelty, strength or conflict; no newspaper weighting. |
| Models | AR(1) benchmark; ARIMA, SARIMA (± NSS, ± exogenous: global food prices, rainfall, MSP); VAR with DCA daily prices vs VAR with NSS; MIDAS. |
| Evaluation | Rolling-window out-of-sample, h = 1–12, **relative RMSE vs AR(1)**. **No significance tests.** |
| Results | Mixed. Veg m-o-m h=1: SARIMA+NSS 0.93 vs SARIMA 0.95. Veg y-o-y h=1: SARIMA+NSS 0.79 vs SARIMA 0.77 (**news slightly worse**). Food y-o-y: VAR-NSS 0.44 at h=1. MIDAS food y-o-y is worse than AR(1) at several horizons. |
| Leakage | Not discussed. No release-date alignment, no vintages. |
| Uncertainty | None; the authors say so explicitly (p.26). |
| Explainability | Episode-level only (shaded shock periods). A forecast change cannot be traced to specific articles. |
| Our concerns | Short test window that includes COVID; some table rows are duplicated; generic finance lexicon used for farm news; newspapers unnamed. |
| **E1–E6** | E1 partly (food/veg CPI) · E2 no · E3 no · E4 no · E5 no · E6 partly |
| **Reuse** | Keyword pre-filter (fn 9); DCA daily retail prices and Agmarknet arrivals as data; AR(1)/SARIMA(+Exo) baselines; relative-RMSE-by-horizon reporting; lexicon NSS as a cheap **"index" baseline** to compare our claims against. |

## 2. Wang, Feng, Qiu, Gu, Zhao (2024): From News to Forecast (NeurIPS 2024), our closest method

| Item | Finding (page) |
|---|---|
| Domains | Electricity (Australia, half-hourly), AUD exchange rate (daily), California traffic (hourly), Bitcoin (daily). **No CPI, no India**; inflation appears only as a supplementary input. |
| How news enters | GPT-4 Turbo agents select news; the selected items (summary, time, region, "rationality") go **as text into the prompt**. The **forecaster is the LLM itself**: Llama-2-7B fine-tuned with LoRA to output the series digits (pp.5–7, 14–15). |
| Reflection | An evaluation agent compares validation predictions with ground truth, finds "missed news" and **rewrites the news-selection logic**. Then news is re-selected and the model **re-fine-tuned** (3–4 iterations). Verified quotes: "adjusts the news filtering strategy for the **training data**" (p.6); "definitive news filter for training the final model" (p.7). **Training-time only.** |
| Decision to revise an issued forecast | **None.** Each forecast is made once from the news available before the prediction date. |
| Evidence properties | Relevance, direction (+/−), duration (short/long/real-time), region, time. **No source reliability** (named only as future ethics work, p.10), **no novelty, no strength, no conflict handling.** |
| Evaluation | Validation set "randomly extracted from the training data" (p.7). Chronological test split **not stated**; test length not stated; **no significance tests**; point metrics only. |
| Results | Electricity RMSE: no news 336.41 → filtered news 280.39; **unfiltered news 407.86 (worse than no news)**. Reflection gains are **not monotonic** (313.89 → 287.35 → 303.03 → 280.39). |
| Leakage | Only "updated the Exchange and Electricity datasets up to 2022" to avoid LLM pre-training bias (p.7); news limited to "before the prediction". GPT-4 / Llama-2 cutoffs are not discussed; Traffic 2015–16 and Bitcoin 2019–21 likely fall inside pre-training data. |
| Uncertainty | None. |
| Explainability | Timestamped news with rationale in the prompt; per-forecast attribution is listed as **future work** (p.10). |
| **E1–E6** | E1 no · E2 partly (dated article summaries, not atomic claims) · E3 **no** · E4 no · E5 no · E6 partly (weak) |
| **Reuse** | "Unfiltered news hurts" (Table 1) as motivation for **gating evidence**; their JSON fields (time, region, rationality, effect duration) as a start for our claim schema; the "missed news" analysis as an **offline diagnostic** on past data only; the ablation design (no news / unfiltered / filtered). Code is public. |

## 3. Singh & Bhoi (2022): Inflation Forecasting in India: Are Machine Learning Techniques Useful?

*RBI Occasional Papers 43(2), pp. 46–88. Received 12 Sep 2022, accepted 8 Feb 2023.*

| Item | Finding |
|---|---|
| Target | Headline CPI-C (2012=100, back-cast to 1995 with CPI-IW). **Quarterly** q-o-q momentum, converted to y-o-y. |
| Features | M3, output gap (full-sample HP filter), rainfall deviation, MSP, agricultural wages, call rate (WACR), exchange rate, crude oil, global food and non-fuel prices, GSCPI, a seasonal dummy. |
| Models | Random walk, ARIMA, SARIMA, linear regression, ARIMAX, NKPC, VAR, ANN, LSTM (each NN averaged over 500 random seeds); simple-average pairwise combinations. |
| Evaluation | Tuning window 2017Q1–2018Q4; expanding window; **12 one-quarter-ahead forecasts (2019Q1–2021Q4)**, 6 per sub-period. RMSE only; **no significance tests**. |
| Results | 1Q ahead RMSE: univariate ANN 0.58, univariate LR 0.66, SARIMA 0.79, RW 0.92, NKPC 1.53. LSTM is worse than ANN; multivariate models weaker after COVID. |
| Leakage | Revised data, contemporaneous regressors, full-sample HP filter, no vintages. |
| **E1–E6** | E1 partly (quarterly) · E2 no · E3 no · E4 no · E5 no · E6 partly |
| **Reuse** | Monthly versions of the feature list; modelling momentum and then converting to y-o-y; expanding window with a separate tuning window; averaging NNs over seeds; the SPF median as a second comparison. |

## 4. Pratap & Sengupta (2019): Macroeconomic Forecasting in India: Does ML Hold the Key?

*This copy is the ISI Delhi growth-conference draft of 15 Sep 2019. Its relation to RBI WP 04/2019 is not confirmed from the text.*

| Item | Finding |
|---|---|
| Target | All-India CPI-C y-o-y, monthly: headline (2002–2018, back-cast) plus food, fuel and core (2012–2018). Univariate only. |
| Models | RW, ARIMA, SARIMA, STL, RF, XGBoost, NNAR, LSTM, GRU, KNN, SVM; equal-weight vs inverse-RMSE combinations of the top 5. |
| Evaluation | **One origin; test = last 6 months (Jul–Dec 2018)**, h = 1–6 pooled. RMSE, relative RMSE, SMAPE; **no significance tests**. |
| Results | Headline: **SARIMA RMSE 0.24** (best; verified), NNAR 0.41, RW 1.81. Equal-weight combination 0.38 beats inverse-RMSE weighting 0.51 but **not SARIMA**. Forecasting headline directly is better than aggregating components. |
| Leakage | **The test set was used for model choice and combination weights** (top-5 by test SMAPE; inverse-RMSE weights on test RMSE, fn 8). |
| **E1–E6** | E1 yes · E2 no · E3 no · E4 no · E5 partly (intervals mentioned only) · E6 partly |
| **Reuse** | RW, SARIMA, NNAR and XGBoost on 24 lags as baselines; an **equal-weight combination of a pre-fixed model set**; relative RMSE vs RW. Avoid their test-set selection. |

## 5. Gao, Jiang, Yan (2025/26): Detecting Lookahead Bias in LLM Forecasts

*arXiv 2512.23847v2, 12 Jun 2026 (earlier title "A Test of Lookahead Bias in LLM Forecasts"). CUHK.*

| Item | Finding |
|---|---|
| Idea | **Lookahead Propensity (LAP)**: ask the model only "entity + target date: up / down / unknown?" and read the token probabilities. LAP = P(up) + P(down). High LAP means the model "remembers" the outcome. |
| Test | Regress the outcome on LLM signal + LAP + signal × LAP. A positive interaction indicates contamination. **Placebo:** post-cutoff dates should show no effect. Needs logprobs (open model or API), or repeated sampling. |
| Applications | US news headlines → next-day returns; earnings calls → capex. Llama-3.3-70B (cutoff Dec 2023). **No macro or India application.** |
| Findings | Memorisation is strong in-sample (mean LAP 0.88 in 2020) and ~0 after the cutoff. The LLM signal is amplified where LAP is high, and the placebo is null. |
| Advice | If contaminated, restrict backtests to post-cutoff data; masking need not remove the bias; use frozen open checkpoints. |
| **E1–E6** | E6 **strong**; others no. |
| **Reuse (plan)** | Run a LAP-style recall query for each CPI item × month (and state, if available) with a frozen open model; test whether our claim-based signal works more strongly where LAP is high; use 2024–2026 (after the cutoff) as a placebo window; check that every extracted claim actually appears in its source text (extraction-faithfulness check, our own addition). |

---

## Summary across the five papers

| Element | TOP news (RBI 2021) | News→Forecast (NeurIPS 2024) | Singh & Bhoi 2022 | Pratap & Sengupta 2019 | Gao et al. 2025 |
|---|---|---|---|---|---|
| E1 India CPI | Partly (food/veg) | No | Partly (quarterly) | Yes | No |
| E2 Claim-level dated evidence | No (daily index) | Partly (article summaries) | No | No | No |
| E3 Decide whether to revise an issued forecast | No | **No** (training-time reflection) | No | No | No |
| E4 Never- vs always-update comparison | No | No | No | No | No |
| E5 Uncertainty | No | No | No | Partly | No |
| E6 Leakage control | Partly | Partly (weak) | Partly | Partly (test-set selection) | **Yes** |

**Common weakness:** none of the four forecasting papers reports a significance test. Test windows are short: 6 months, 6 quarters per sub-period, 24 months, or not stated.

## What this does to the research gap (still provisional)

**Supported by full text (5 papers):** the closest India news study (RBI 2021) uses an **aggregate daily sentiment index as a regressor**. The closest LLM method (NeurIPS 2024) uses **reflection to rewrite news-selection logic during training**. Neither, nor the India numeric baselines, **decides at forecast time whether an already-issued forecast should be revised**, scores evidence for novelty or reliability, logs revision reasons, compares update policies, or gives intervals.

**Not yet ruled out:**
1. **Nowcasting "news" decomposition** (e.g. Bańbura & Modugno; Bańbura, Giannone & Reichlin). In dynamic-factor nowcasting, every new **data release** revises the nowcast, and the revision is attributed to that release's "news" (surprise). This is a strong, established form of **explainable forecast revision**. The difference to argue: they update on **every numeric release** (always-update), not on text claims with reliability and novelty gating. **Must be read and cited.**
2. **Judgmental forecast adjustment** (Goodwin 2000; Fildes et al.): when experts *should* override statistical forecasts after special events. Very close to our "revise or not" question, but done by humans.
3. Text-based macro nowcasting with news topics (e.g. Thorsrud; Larsen & Thorsrud): check for any **update rules**.
4. Mohan et al. (RBI 2025) and Das & Das (2024): full text is still needed.

**Working gap statement (v2, narrower and safer):**
> For India's CPI inflation, existing studies either forecast from numbers alone or add news as an aggregate sentiment index, and LLM-based methods use news to train or prompt the forecaster. None of the studies read in full **decides, at forecast time, whether to revise an issued forecast** based on individual dated, source-linked claims scored for novelty, reliability, relevance and strength, **logs the reason**, and **tests this rule against never-update and always-update policies** with intervals in a point-in-time backtest. Nowcasting models do revise forecasts and attribute revisions, but **mechanically on every numeric data release**. Our contribution is **selective, text-evidence-gated revision**.
