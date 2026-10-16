# Level-2 (content) readings: full text (15 Oct 2026)

> **Status note (16 Oct 2026):** this is a **literature record** (research kept). Statements here about "Reflica", "our gap" or "Minor 1" were written for the CPI evidence-aware revision study, which is now **Part B** of the safer-merge Minor 1 direction. The old plan documents were removed at the user's request (they remain in git history).

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

---

## Round 3 (15 Oct 2026): testing the gap against revision, nowcasting and LLM-updating work

**Important:** none of these papers could be read in full; every paper host is blocked from the cloud environment. This round is **search-level** (abstracts, official summaries, software documentation, secondary citations). It is enough to show *what kind* of method exists, **not** enough to quote page numbers. Details and identities are in `VERIFICATION.md` §G.

### What existing methods actually do with incoming information

1. **Nowcasting news decomposition is not just "mechanical".** In Bańbura–Giannone–Reichlin and Bańbura–Modugno, each release's *news* is the **surprise** (actual minus model expectation). The revision equals a **weighted sum of surprises**, with weights from the model's covariance structure. So the update is **automatically selective in magnitude**: an expected release (zero news) moves nothing, and a noisy series gets a small weight. Revisions are **attributed** to individual releases (ECB toolbox, statsmodels `.news()`). Modugno (2013) applies this to **inflation**.
   → *Implication for Reflica:* "attribute each revision to its source" and "ignore unsurprising information" **already exist** for **numeric** releases. Our claim must not be "first explainable revision".
2. **Text has entered factor and nowcast models** (Thorsrud: newspaper topics in a DFM; Kalamara et al.: newspaper text improves UK inflation and GDP forecasts; Zheng et al.: China). In those, text enters as **topic or term series** (aggregate indices). We found **no** search-level evidence of a news decomposition at the level of **individual articles or claims** with source reliability. This is **not verified from full text**.
3. **Forecast-revision efficiency literature** (Nordhaus 1987; Isiklar–Lahiri–Loungani 2006; Coibion–Gorodnichenko 2015) shows that professional forecasters **under-react / smooth**: revisions are serially correlated and predict errors. This *evaluates* revision behaviour; it does not propose a gating rule.
4. **Judgmental adjustment literature** (O'Connor et al. 2000; Goodwin 2000; Fildes et al. 2009) asks *when changing a statistical forecast helps*. Finding: **large, information-driven adjustments help; small ones often hurt; people make unnecessary changes.** This is the closest conceptual precedent for "revise only when evidence is strong", but it is about **human** adjusters and is not automated from text.
5. **Human forecaster updating** (Atanasov et al. 2020): the best forecasters update **frequently and in small steps**. This is a direct challenge to a "revise rarely" design. Our rule must be tested against **small-step** policies, not only never/always.
6. **Operations "nervousness"** (Blackburn et al. 1986): **change costs** or **freezing** reduce churn. This is a threshold-like precedent from supply chains.
7. **LLM forecast updating (2025–2026) is now an active area:**
   - **EvolveCast** measures whether LLMs update after new news; they are under-responsive.
   - **BLF** (Murphy 2026) maintains a **belief state with a structured evidence summary**, revised sequentially per evidence step.
   - **Forecast-Dojo** replays dated news so agents **revisit forecasts over time**, with deduplication.
   - **Corroboration Illusion** shows news-driven forecasters are easily **poisoned**, and simple source filters are bypassable.

   These are mostly **binary event questions** (ForecastBench, Polymarket), with the **LLM as the forecaster**, **not** inflation targets.

### Updated E-element check (search level unless marked)

| Prior method | Revises an issued forecast on new information? | Uses textual news? | Selective decision (gate) whether to change? | Scores individual items (novelty / reliability / relevance / strength)? | Compares never / always / selective policies? | Inflation or macro target? |
|---|---|---|---|---|---|---|
| BGR / Bańbura–Modugno news decomposition | **Yes** (each release) | No (numeric releases) | **Implicit**: magnitude ∝ surprise × weight; no discrete gate | Partly: **surprise** ≈ novelty; **weight** ≈ relevance/reliability of the series | No (not as policies) | **Yes** (GDP; inflation in Modugno 2013) |
| Thorsrud; Kalamara et al.; Zheng et al. | Yes (model re-estimated or filtered with new text) | **Yes** (topic/term series) | No | No (aggregate series) | No | **Yes** (GDP, inflation) |
| Cleveland Fed nowcast | Yes (daily oil, monthly CPI) | No | No | No | No | **Yes** (inflation) |
| RBI TOP news (2021) **[full text]** | Re-estimated each period | Yes (daily lexicon index) | No | No | No | Yes (food/veg CPI, India) |
| From News to Forecast (2024) **[full text]** | **No** (training-time reflection) | Yes (selected article summaries) | No | Relevance/direction only | No | No |
| Judgmental adjustment (Fildes 2009 etc.) | Yes (humans adjust) | Human information | **Yes (human judgement)** | Not formalised | Adjusted vs unadjusted | No (supply chain) |
| Atanasov et al. (2020) | Yes | Human information | Human | No | Studies update **frequency/magnitude** styles | No (geopolitics) |
| MRP nervousness (Blackburn 1986) | Yes | No | **Yes (change cost / freeze)** | No | **Yes (dampening strategies compared)** | No (production) |
| EvolveCast (2025) | Yes (LLM given new news) | Yes | No (measures behaviour) | No | No | No (event questions) |
| BLF (Murphy 2026) | **Yes** (sequential belief state) | Yes (web search) | Implicit (LLM decides) | Structured evidence summary; **scoring not stated** | No | No (binary events) |
| Forecast-Dojo (2026) | **Yes** (revisit at successive dates) | Yes (18.8M dated articles) | Agent-decided | Deduplication at corpus level | Not stated | No (Polymarket events) |
| Corroboration Illusion (2026) | — | Yes | — | Shows source filters fail | — | No |

### Revised gap statement (v3; strongest version we can currently defend)

> **What already exists.**
> - Model-based nowcasts revise forecasts with every data release and attribute each revision to the "news" (surprise) in specific **numeric** series; this has been applied to inflation [Bańbura & Modugno 2014; Bańbura, Giannone & Reichlin 2011; Modugno 2013].
> - Newspaper text improves macro and inflation forecasts when entered as **aggregate topic, term or sentiment series** [Thorsrud; Kalamara et al. 2022; Pratap et al. 2021].
> - Human-judgment research shows that **large, information-based adjustments help while small or unnecessary ones hurt** [Fildes et al. 2009; Goodwin 2000; O'Connor et al. 2000], and that the best humans update **often in small steps** [Atanasov et al. 2020].
> - LLM agents now revise binary event forecasts as dated news arrives [Murphy 2026; Forecast-Dojo 2026], but they under-react [Yuan et al. 2025] and are vulnerable to poisoned sources [Lu & Zhang 2026].
>
> **What we have not found (search level, 37 + 22 papers; full text for 13).** A method that, for a **monthly inflation target**:
> - (i) converts incoming **text** into **individual dated, source-linked claims**;
> - (ii) applies an **explicit, pre-registered gate** combining claim novelty, source reliability, CPI-weight relevance and strength to decide **whether** an issued numeric forecast is revised;
> - (iii) **logs the reason**; and
> - (iv) evaluates this gate against **never-update, always-update (news-decomposition-style) and small-step update policies** at equal horizons, with intervals, in a point-in-time backtest with an LLM-memorisation check.
>
> **Framing for the paper:** a *text-claim analogue of nowcasting news decomposition, with an explicit revision gate*. This is not "the first explainable revision".

**Status:** provisional. Full-text checks still needed for Bańbura–Modugno, Thorsrud, Kalamara et al., BLF and Forecast-Dojo, to make sure none of them gates revisions on individual text claims.

---

## Round 4 (15 Oct 2026): full text of the nowcasting papers and Das & Das

User-uploaded PDFs, each read in full by a separate reader. Key quotes were **re-checked by hand** against the extracted text (marked ✔).

### 6. Bańbura & Modugno (2010), ECB WP 1189 (working-paper version of JAE 2014)

- **Model.** Euro-area dynamic factor model in state-space form. EM estimation for an arbitrary pattern of missing data. Data are 14/46/101 series as available on 15 Oct 2009. GDP nowcasting evaluated 2000Q1–2007Q4, **pseudo real-time** using final data.
- **News.** Released value minus the model's forecast of it. The revision is "a weighted average of the news in the latest release" ✔ (p.17). The weights come from model covariances, so **size of news × relevance** together set the revision size.
- **No news, no change.** If the data match the model's prediction, "there is no news… the forecast will not be revised" ✔ (p.17).
- **Data revisions** are set aside (p.16). The effect of **re-estimating the parameters** is logged as a separate "Re-est" category.
- **Attribution.** The revision can be split "into contributions from the news in individual (groups of) series" ✔ (p.18). Figure 1 (2008Q4) shows "the biggest news impact comes from the surveys" ✔ at long horizons, and real data later.
- **No gate, no text, no update-policy comparison.** Updating is automatic at every release. News is defined "with respect to the model and not market expectations" ✔ (fn 6).
- **Target:** GDP only; **no inflation application**.

### 7. Bańbura, Giannone & Reichlin (2010), "Nowcasting", ECB WP 1275 (SSRN 1717887)

- Nowcasts are "updated as new data arrive". The model does what practitioners do by judgement "in a fully automatic way" ✔ (p.4).
- The unexpected part of a release is "the news" ✔. A release exactly as predicted means "the nowcast will not be revised" ✔ (p.11). The revision depends "on the size of the news and… on its relevance for the target variable" ✔ (p.12). The decomposition is "also useful when the forecast is updated less frequently than at each new release" ✔ (p.12). That is a batching remark, **not a decision rule**.
- **Targets:** euro-area GDP 2008Q4 and **HICP inflation** (Dec 2008), but inflation "is not our focus" ✔ (p.21). For HICP, "the largest revisions are caused by the releases of HICP itself" ✔ and of commodity prices (p.22).
- **Timeliness vs precision:** surveys are timely but less precise (pp.7, 19). Soft data lose value once hard data arrive (p.26).
- **Evaluation:** pseudo real-time, 2000–2007, RMSFE falling across the release calendar (Table 2). **No significance tests; no comparison of update policies.**

### 8. Das & Das (2024), IJEF 16(6):92–101 (closest India text paper)

- **India confirmed:** headlines "specific to India" ✔. The source is **Times of India headlines only**, from Kulkarni's Kaggle / Harvard Dataverse corpus ✔ (p.96). CPI from Jan 2012 ✔. The exact CPI series, y-o-y vs m-o-m, and the horizon are **not stated**.
- **Text representation:** monthly relative frequencies of 166 dictionary words. There is **no sentiment polarity**. The dictionary starts from words "in at least 75% of the months (200 out of 270 months)" ✔, covering **2001–2023, which includes the test period** (a look-ahead risk). The step from 1,415 to 166 words is **undocumented**.
- **Evaluation:** single "70% … training … 30% … test" split ✔ (~40 test months; order not stated). RMSE only, **no significance tests**. Best: ANN with text RMSE 1.560 vs best no-text RF 1.654 ✔ (about 6% better). **Text worsened** Elastic Net and RF (RF 1.654 → 1.900 ✔). Yet the text claims text models "consistently demonstrate lower Relative RMSE" ✔, which contradicts its own table.
- **No revision mechanism, no claim-level provenance, no intervals.** E1 partly · E2 no · E3 no · E4 no · E5 no · E6 no.
- **Reuse:** the 166-word list as a "word-frequency index" baseline, rebuilt on a **pre-test window only** and lagged to pre-release information. The ToI corpus is a usable dated source.

### 9. Mohan et al. (2025), RBI Bulletin: still not read in full

The user supplied the **RBI press release text** only (not the article PDF). Highlights there: forecast combination of statistical, ML and DL models "is found to have similar or even better accuracy over standalone models"; it "can also generate density forecasts" and "provides confidence bands". **Weights, RMSEs and evaluation design remain unverified.**

### Gap after round 4 (v4)

Full text now confirms what round 3 found at search level:

1. Nowcasting **revises forecasts automatically** at every numeric release. The revision equals relevance-weighted surprise ("news") and is **attributed** to series. **No gate, no text, no comparison of update policies.** Inflation appears only as a side target (BGR).
2. The two closest **India text** papers (Pratap et al. 2021; Das & Das 2024) use **aggregate text indices or word frequencies**, with no revision logic. In both, **text sometimes hurts out-of-sample** (veg y-o-y 0.77 → 0.79; RF 1.654 → 1.900). This supports *gating* text rather than always adding it.
3. Still search-level only: Thorsrud, Kalamara et al., Modugno 2013, BLF, Forecast-Dojo and EvolveCast. These are the **remaining risks** for claim-level, text-gated revision.

**Defensible framing (unchanged, now better supported):** Reflica is a *text-claim analogue of nowcasting news decomposition*. Each claim's surprise (novelty) and relevance play the role of news × weight. Reflica adds an **explicit, pre-registered gate** with source reliability, and evaluates **update policies** (never / always (news-decomposition-style) / small-step / gated) for India CPI.

### 10. Thorsrud, "Words are the New Numbers" (JBES, pp. 393–409): **abstract only**

Source: the publisher's abstract, pasted by the user.
- **Method.** Daily business-newspaper text is "decomposed into time series representing news topics" (LDA). A **time-varying dynamic factor model** builds a daily business-cycle index from quarterly GDP plus the topics, with "dynamic sparsity … enforced upon the factor loadings using a **latent threshold mechanism**."
- **Results claimed.** It classifies business-cycle phases "with almost perfect accuracy". Out-of-sample nowcasts are "competitive with forecast combination systems and expert judgment" and have "predictive power for future revisions in GDP".

**Why it matters for our gap:**
- The **latent threshold** is a data-driven *gate*: at each time it switches whole **news topics** on or off in the factor loadings. This is **closer to our gate than earlier assumed**.
- The differences, at abstract level:
  - It gates **topic series** (aggregate), not individual dated claims with sources.
  - The threshold is **learned statistically**, not a pre-registered rule using novelty, source reliability and strength.
  - It builds an **index or nowcast**, and does not decide whether to revise an issued forecast.
  - There is **no comparison of update policies**.
  - The target is **GDP / business cycle**, not inflation.
- **Action:** cite it as prior evidence that **selective (sparse, time-varying) use of news** helps nowcasting. Read the full text to see how the threshold behaves and whether any revision attribution to topics is reported.

### 11. Modugno (2013), "Now-casting inflation using high frequency data" (IJF 29(4):664–675): **partial** (abstract + introduction + snippets)

Source: the ScienceDirect preview, pasted by the user. Quotes are from that text.

- **Target:** **US CPI inflation** (total and components: energy, services and goods, transport, food and beverages, housing).
- **Data:** four groups chosen for "a high correlation with inflation, and timeliness":
  - daily **World Market Prices of Raw Materials**;
  - **Weekly Retail Gasoline and Diesel Prices**;
  - daily **financial variables**;
  - (a further group not described in the snippet).
- **Model:** a trading-day-frequency factor model with missing data in state space, estimated with the Bańbura–Modugno EM.
- **News and revisions:** the framework allows one "to disentangle the model-based news from each data release and subsequently to assess its impact on the forecast revision". News is "the difference between the data released and the respective model predictions". The paper produces "a sequence of forecasts, which are updated when new data" are released (Section 5).
  - The **main accuracy exercise** assumes "forecasts are produced once per month, i.e., after the CPI release". Continuous updating is shown as an **illustration** (Section 5, not read).
- **Results claimed:**
  - Significantly beats the monthly-only factor model, random walk and IMA at h = 0 and 1 month.
  - The gains come mainly from the **energy and transport** components.
  - Raw-material and gasoline data "improve the accuracy of the model significantly".
  - Financial variables add "only a marginal contribution".
- **For our gap:**
  - This is the **closest inflation-specific precedent** for explainable, release-by-release revision. Its timeliness argument parallels ours (signals before the CPI release).
  - But the inputs are **numeric price series**, updates are **automatic**, there is **no gate**, **no text**, no source reliability, and **no comparison of update policies**.
  - The finding that **energy and fuel prices drive inflation nowcast gains** suggests that Reflica's claim **relevance** should weight fuel, food and commodity-price claims highly.
- **Reuse:** daily or weekly fuel and commodity prices (for India: PPAC retail fuel prices, DCA daily retail food prices) as a **numeric always-update baseline**, built in news-decomposition style.

### 12. Mohan, Hasan, Roy, Sarkar & John (2025), "Predicting CPI inflation in India: Combining Forecasts from a 'Suite' of Statistical and Machine Learning Models", RBI Bulletin, 25 Jun 2025

**Source:** the full article text pasted by the user. The **charts and the equation images (RMSE, weights, asymmetry formulas) were not included**, so the weighting formula and the RMSE levels are not verified.

- **Data:** NSO CPI, **Jan 2012–Jul 2024**. Headline and core (excluding food and fuel).
  - Exogenous variables: Indian-basket crude price (PPAC), INR–USD, real GDP and output gap (HP filter; quarterly → monthly by Denton–Cholette), repo rate.
- **Target transform:** X-13 seasonal adjustment, then **seasonally adjusted annualised rates (SAAR)**. This is **not y-o-y**.
- **Models:** **216** = 108 specifications × 2 rolling windows (36 and 96 months).
  - Statistical: RW, AR, MA, ARMA(X), ARCH-type, VAR, BVAR.
  - ML: SVM, ensemble learning, RF, GPR, NARNET(X).
  - DL: LSTM.
  - Built as a MATLAB toolbox.
- **Combination:** weights from each model's recent **12-month-window RMSE** (the "performance-weighted" combination).
- **Density:** RMSE-weighted standard deviations above and below the combined forecast, giving a **split-normal** distribution with asymmetric intervals and a skew measure.
- **Evaluation:** **pseudo-out-of-sample** (data up to *t* only, including forecasts of the exogenous variables), horizons 1–12 months.
  - Average RMSE across 12 horizons is "approximately **70 per cent lower** than the benchmark random walk". The combination beats ">75 per cent of models in all horizons".
  - **Diebold–Mariano tests with the Harvey–Leybourne–Newbold correction**, plus Wilcoxon signed-rank tests. Performance-weighted is **never significantly worse** than the simple average. It is significantly better in 12/16 cases (headline, 3-year window) but only 2/16 (headline, 8-year window).
- **Illustration:** 2024 monthly outcomes "fell well within the range of forecasts" made with data to Dec 2023.
- **No text, no news, no revision logic, no gate.** Forecasts are produced from data up to each origin.
- **Note:** this contrasts with Pratap & Sengupta (2019), where equal weights beat inverse-RMSE weights on one 6-month test. Mohan et al. use a much longer pseudo-OOS evaluation with significance tests. It also cites **John, Singh & Kapur (2020), "Inflation Forecast Combinations: The Indian Experience", RBI WP 11/2020** (add to the reading list).
- **E1–E6:** E1 **yes** (India headline CPI, though as SAAR) · E2 no · E3 no · E4 no · E5 **yes** (split-normal density, asymmetric bands) · E6 partly (pseudo-OOS, no real-time vintages; HP output gap).
- **For Reflica:** this is the **official numeric baseline to match or beat**. Reuse:
  - its design (rolling 36/96 windows, performance weighting, split-normal bands, DM+HLN tests);
  - its exogenous set (crude, INR–USD, repo, output gap).
  - Our forecast target (y-o-y) differs from their SAAR target, so a conversion or a parallel SAAR evaluation is needed for comparability.

## Round 6 (15 Oct 2026): Forecast-Dojo, BLF and Kalamara et al. (full-text PDFs uploaded by the user)

The parallel readers stopped early because of a usage limit. These sections were read **directly by targeted inspection of the extracted text**: abstract, method, prompt appendix and key results. They were **not** read line by line. The quotes below are verified against the text.

### 13. Ye, Wang, Ahmed, Zhang, He, Lin, Yin, Peng, Galarnyk, Chava, Zhang (2026), "Forecast-Dojo: Replayable Environments for Benchmarking and Training LLM Forecasting Agents", arXiv 2609.28876v1 (Georgia Tech, Amazon, Univ. of Florida)

- **Task:** 1,568 resolved **Polymarket** events (binary and multiple-choice) and 18.8M dated news articles (2025-03 to 2026-06). Agents "revisit their predictions at successive historical dates".
- **Point-in-time controls:**
  - URL, title and MinHash near-duplicate removal, keeping "the earliest-published representative".
  - Reliable timestamps and a content-level outcome-leakage screen.
  - Each model's knowledge cutoff precedes the evaluation period (Table 9).
- **Memory-on "belief notebook" (Figure 6 prompt). This is the closest prior design to Reflica's claim log.** It is an **append-only evidence_ledger**. Each entry has:
  - `claim`
  - `supports` / `rules_out`
  - **`date_observed`** ("the date carried by the evidence itself")
  - `status` (**"active" or "superseded"**)
  - a `note` on "provenance or quality caveat — the source, whether it was corroborated, or … several reports tracing back to one original"

  The agent is told to keep p "consistent with the active ledger … moved only as far as that evidence justifies."
- **Results:**
  - Research tools lower Brier for all 12 models.
  - Forecast improvements are "concentrated at steps with more newly recorded evidence" (mean step Brier change −0.007 in the lowest new-evidence quartile vs −0.071 in the highest).
  - The notebook "lowers research cost but does not consistently improve forecast quality" (better for 6 models, worse for 6).
  - All models trail the market (best Brier 0.546 vs market 0.498).
- **For our gap:**
  - It **does** revise forecasts over calendar time from dated text, with **claim-level, dated, provenance-annotated evidence** and supersession.
  - The decision to change is left to the **LLM's judgement**. There is **no explicit, pre-registered gate**, and novelty, reliability, relevance and strength are **not scored numerically**; quality lives in free-text notes.
  - The **LLM is the forecaster**; targets are **binary/multiple-choice events**, **not inflation**.
  - It compares **memory-on vs memory-free**, **not** never / always / small-step / gated update policies.
- **Also cites a new close paper (not read):** Zhao, Zhang, Ye, Cao, Xie, Chava (2026), "Can LLMs take the pulse of the economy? A real-time evaluation of LLM nowcasts on macroeconomic indicators", arXiv 2608.30110. **Must check: possible macro/inflation LLM nowcasting with real-time updates.**

### 14. Murphy (2026), "Agentic Forecasting with Structured Linguistic Beliefs" (BLF), arXiv 2604.18576v5, 27 Sep 2026 (UBC). The title changed from earlier versions.

- **Task:** **binary** ForecastBench questions: 400 question-date instances (market + dataset questions; the dataset questions include **binarized FRED / yfinance** series).
- **Belief state:** probability, confidence (low/medium/high), key evidence for and against (natural-language summaries), open questions. It is "updated by the LLM at each step of the agent loop". The update is "Bayesian-inspired … the actual update is just an LLM forward pass."
- **When it updates:** **within one forecast's research loop** (search steps), **not** as revisions of an issued forecast over calendar time.
- **Results and controls:**
  - Highest Brier Index among compared agents.
  - The belief-state ablation is reported in Table 3.
  - Four-layer date-leakage defence with ~1.5% residual leakage.
  - Paired bootstrap comparisons (question difficulty explains 62% of variance).
- **For our gap:** no item-level scoring of reliability or novelty, no gate, no update-policy comparison, no numeric inflation target. **Reusable:** paired evaluation with bootstrap CIs; leakage-audit layers.

### 15. Kalamara, Turrell, Redl, Kapetanios & Kapadia (2020), "Making text count", BoE Staff WP 865 (published JAE 2022)

- **Text:** The Guardian, Daily Mirror and Daily Mail (≈528k articles, 1990/95–2019). Many text metrics were compared: dictionaries, Boolean counts, topic models, and **term counts combined with supervised ML** (9,660 dictionary-derived terms).
- **Targets and design:** GDP, **CPI inflation**, unemployment. Rolling 36-month re-estimation. The paper discusses real-time pitfalls of text (e.g., corpus-wide vocabularies are "not possible in real-time").
- **Finding:** text improves forecasts, especially in stress periods.
- **For our gap:** text enters as **aggregate term-count features**. No claim-level evidence, no revision gate, no update-policy comparison. **Reuse** as the strongest "**text-as-features**" baseline (term counts + ML) to compare against claim-gated revision.

### Gap after round 6 (v5): **narrowed; must be stated carefully**

**Now shown to exist (full text):**

| Capability | Who already does it |
|---|---|
| Revising forecasts at successive dates as dated text arrives | Forecast-Dojo (LLM agents, events) |
| Claim-level, dated evidence log with provenance notes and supersession | Forecast-Dojo belief notebook |
| Attribution of revisions to new information | Nowcasting news decomposition (numeric) |
| Selective use of text (learned) | Thorsrud latent threshold (topics; abstract only) |
| Text improves inflation forecasts | Kalamara et al.; Pratap et al.; Das & Das |
| Strong India numeric baseline with density bands and DM tests | Mohan et al. 2025 |

**What remains unaddressed in everything read (37 + 22 papers; 22 read in full or near-full):**

1. An **explicit, pre-registered, auditable revision gate**. Each claim's novelty, source reliability, relevance (CPI weight) and strength are **scored**, and a rule (not the LLM's free judgement) decides revise or keep.
2. The forecast comes from a **numeric model**, with the LLM limited to extraction (vs LLM-as-forecaster in Forecast-Dojo, BLF and From News to Forecast).
3. A **comparison of update policies** (never / always (news-decomposition-style) / small-step / gated) at equal horizons.
4. Applied to a **monthly inflation target (India CPI)**, with intervals and a lookahead-bias check.

**Positioning sentence (v5):**
> Prior work either revises numeric nowcasts automatically from data surprises, or lets LLM agents revise event forecasts with free-form evidence ledgers. Reflica tests whether an **explicit, scored revision gate over dated text claims**, applied to a **numeric** inflation forecast, beats never-, always- and small-step updating.

**Must read next:** Zhao et al. (2026), arXiv 2608.30110 (LLM macro nowcasts in real time). It is the **highest remaining risk**.

## Round 7 (15 Oct 2026): Step-1 comparison

See **`../research_gaps/CLOSEST_METHODS.md`** for the comparison of Mohan et al., LiveMacroEval, Forecast-Dojo, Kalamara et al. and Thorsrud against Reflica, and for **gap v6**.

Key update: **LiveMacroEval** (search-level) already has LLM agents **revising US CPI nowcasts hourly** as news arrives, so news-driven CPI revision is **not new**. The remaining question is whether an **explicit, scored, pre-registered gate on a numeric forecast** beats never / always / small-step updating.

## Round 8 (16 Oct 2026): LiveMacroEval, full text

### 16. Zhao, Zhang, Ye, Cao, Xie & Chava (2026), "Can LLMs Take the Pulse of the Economy? A Real-Time Evaluation of LLM Nowcasts on Macroeconomic Indicators" (LiveMacroEval), arXiv 2608.30110v1 [cs.CL], 31 Aug 2026 (Georgia Tech; UC San Diego)

**Source:** PDF uploaded by the user, 48 pages. Read: main text (§1–5 and Limitations) and Appendices D (prompt), E, F, G, H, I, J, O, R and S (key parts). Appendices K–N, P and Q (score derivations, per-model breakdowns) were only skimmed.

| Item | Finding |
|---|---|
| Problem | Can web-search LLM agents nowcast headline macro indicators before their official release? Historical evaluation is contaminated by memorisation, so the evaluation must be **live** |
| Data / targets | **16 US indicators** in 4 themes. Includes **CPI All Items (YoY %)**, PPI, PCE price index, GDP, payrolls, unemployment, housing. Released values come from the agencies; release timestamps from the Bloomberg calendar |
| Period | Live, target months **Nov 2025 – Mar 2026** (releases 1 Dec 2025 – 5 May 2026). Agent-design study: Jul–Aug 2026. Rationale study: Jun–Aug 2026 |
| Agents | GPT-5, Claude-sonnet-4.5, Qwen3-235B, Qwen3-80B, each with web search. The agent decides what and when to search |
| How forecasts are produced | The window opens in the last week of the reference month and closes at the release (e.g., March CPI from end-March to 10 April). **Hourly** calls; two independent calls per agent per hour (two indicator groups). **The prompt (App. D, Fig. 6) contains no placeholder for the agent's previous nowcast.** It tells the agent to "Identify information shocks and update your prediction" and to use the latest information |
| Revision policy | **No explicit rule.** Revisions are whatever the LLM produces at each hourly call. There is no gate, no evidence scoring and no claim ledger. Revisions are studied **after the fact** (App. R: GPT-5's March 2026 CPI nowcast jumped from ~2.7% to ~3% on 8 Apr 2026, consistent with the EIA petroleum report and the FOMC minutes) |
| Baselines | Bloomberg ECOS consensus (median); 5 Fed regional-bank nowcasts (Cleveland Fed for CPI); **univariate auto-ARIMA, fitted once at window start and held fixed for the whole window** (App. I), i.e. effectively a "never-update" numeric baseline |
| Metrics | **LiveMacro Score:** model-implied equity return (β × standardized surprise) vs the realized E-mini S&P return in a [−5, +30] min window; a bounded out-of-sample R²; 0 = consensus. **LiveBetting Score:** hourly $1 Polymarket-style bets. Squared relative error is in App. J only |
| Findings | GPT-5 **ties** the Bloomberg consensus overall (+0.004, not significantly different). The other agents are below the consensus but above ARIMA, except Qwen3-80B (≈ ARIMA). **CPI, retail sales and the PCE price index account for 87% of the average agent's shortfall.** On CPI, the Cleveland Fed and Bloomberg consensus beat all LLM agents. LLMs do better on supply/production and housing. A multi-agent team (researcher + verifier) is the only design above consensus (+0.020), because it predicts **smaller surprises** and gets the direction right more often (54% vs 38%) |
| Leakage controls | Live only; nowcasting strictly before release (post-release runs snap onto the released value, App. E); three tests showing no copying of the consensus or Fed nowcasts (App. F) |
| Uncertainty | **Point nowcasts only.** No prediction intervals, no probabilities, no calibration analysis |
| Limitations (authors) | (1) Few release events (structural for live evaluation). (2) **US-only.** Non-US economies are left to future work; they name the euro area as the clearest next case. India is not mentioned |
| **For our gaps** | **G2 survives, narrowed:** there is no explicit, pre-registered, scored revision rule and no comparison of update policies (never / always / small-step / gated); the ARIMA baseline is frozen. It **confirms** that free LLM updating already exists and that LLM agents are **weakest on CPI**, which supports keeping a numeric model as the forecaster. The team result (smaller predicted surprises score better) is relevant to **bounded** revisions. **G1:** not India, and numeric nowcasts rather than yes/no events, so it does not cover an India benchmark. Its live, contamination-resistant design is a template for Part A |
| **Reuse** | Strict prompt with units and transformation; forecasting window anchored to the official release; post-release snap test; no-copying tests; event-time attribution of revisions; frozen ARIMA as a never-update baseline |

## Round 9 (16 Oct 2026): Thorsrud WP 20/2016 and Modugno ECB WP 1324, **reported by the user**

**Source note:** the user read both PDFs (methods and forecast-revision sections) outside this session and pasted a summary. **The PDFs were not available here, so we did not check these findings ourselves.** Reading level: **K (reported)**. Quote nothing from these papers until a direct check is done.

### 17. Thorsrud (2016), "Nowcasting using news topics: Big Data versus big bank", Norges Bank Working Paper 20/2016
- **This is not "Words are the New Numbers" (JBES).** That paper (§10) is still read at abstract level only.
- **Method (reported):** topics extracted from a large Norwegian business-newspaper corpus; topic series adjusted for news **tone**; combined with a **dynamic factor model** to nowcast **Norwegian GDP growth**.
- **Updating (reported):** estimates update as new information arrives, in a **real-time out-of-sample** experiment.
- **Comparison (reported):** simple forecasts, and Norges Bank's professional and model-based nowcasts.
- **For G2:** **text-based economic nowcasting that updates with incoming news already exists.** It does not establish individual, source-linked claims, a pre-specified bounded revision rule, or Indian headline CPI.

### 18. Modugno (2011), "Nowcasting Inflation Using High Frequency Data", ECB Working Paper 1324 (journal version IJF 29(4), 2013)
- Extends §11 (which was preview-level).
- **Method (reported):** weekly and daily energy and raw-material prices; a statistical factor model estimates the **unexpected component ("news")** of each data release.
- **Targets (reported):** euro-area HICP and US CPI.
- **Revision decomposition (reported):** a revised forecast is explicitly decomposed into **the previous forecast plus the contribution of newly released information**, illustrated for the euro-area inflation nowcast during March 2009.
- **Finding (reported):** high-frequency data improve on monthly data alone, with much of the gain from **energy inflation**.
- **For G2:** **measuring new information and linking it to an inflation forecast revision is established.** The inputs are **numeric releases, not text**, and updating is model-automatic. There is no claim extraction and no comparison of revision policies (reported).

### Consequence: G2 narrowed (gap v8); see `../research_gaps/CLOSEST_METHODS.md`

## Round 10 (16 Oct 2026): LLM-CPI, full text (PDF uploaded by the user, 73 pages)

### 19. Fan, Lv, Sun & Wang (2025), "LLM-Powered CPI Prediction Inference with Online Text Time Series" (LLM-CPI), arXiv 2506.09516v1 [stat.ML], 11 Jun 2025 (USC; Xiamen)
Read: abstract, introduction, Sections 2–3 (labelling and model) and Section 5 (real data), plus keyword checks across the whole PDF. The theory sections and appendix tables were not read line by line.

| Point | Record |
|---|---|
| Problem | Use high-frequency online text, processed by LLMs, to improve CPI **prediction and prediction intervals**, while keeping an interpretable econometric model |
| Data | **China** NBSC monthly CPI, "last month = 100", i.e. **month-on-month** inflation (standardised); national urban unemployment rate; **Weibo** social-media posts (incl. news posts, opinions and ads). Intro: train Jan 2019 – Sep 2022, test Oct 2022 – Dec 2023. Feature selection on Jan 2019 – Oct 2021 |
| Method | GPT-4 chain-of-thought annotation → fine-tuned BERT filters ads and scores posts with a continuous inflation score in [0,1] → **daily LLM CPI surrogate**. Text embeddings via LDA and BERT. **Monthly ARX** (CPI + text embeddings + unemployment) linked to a **daily VARX** on the surrogates (correlated errors). Multi-step forecasts via a rolling horizon. Box–Jenkins and bootstrap prediction intervals; asymptotic theory |
| Baselines | RW, AVE, AR, ARX (unemployment), LDA-only, BERT-only |
| Metrics | Relative root prediction MSE (rPMSE) vs AR; relative sign error; interval coverage and length |
| Findings | Text (LDA) shortens intervals at nominal coverage. LLM+LDA gives the shortest intervals (avg length 3.254, coverage 0.963 vs AR 4.159); the paper reports LLM-CPI outperforming the benchmarks; BERT-only is weak |
| Limitations | Authors note LLM predictions are **stochastic** (sensitive to runs and prompts). Ours: China, m-o-m, social media; short test window; **aggregate scores and embeddings, not source-linked claims** |
| Revision | **No forecast-revision mechanism or update-policy comparison.** "revis" occurs 0 times; forecasts are model outputs per origin |
| **For G2** | Establishes **LLM-processed text + numeric CPI model + intervals**. It does **not** establish claim-level, source-linked evidence, a bounded revision policy, policy comparison, or India. **G2 (v8) survives** |
