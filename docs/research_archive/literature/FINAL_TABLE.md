# Final combined table: all papers (15 Oct 2026)

> **Status note (16 Oct 2026):** this is a **literature record** (research kept). Statements here about "Reflica", "our gap" or "Minor 1" were written for the CPI evidence-aware revision study, which is now **Part B** of the safer-merge Minor 1 direction. The old plan documents were removed at the user's request (they remain in git history).

> **Verification (step B) done on 15 Oct 2026; see `VERIFICATION.md`.** Corrections are applied below. ❌ = could not be verified; do not cite.

**Read:** F = full text read; A = abstract or summary only; N = from your own notes only.
**Trust / Use:** H = high, M = medium, L = low. ⭐ = must read or cite.

| # | Paper (authors, venue, year) | Problem | Method | Result | Gap / weakness | How Reflica fills it | Trust / Use | Read |
|---|---|---|---|---|---|---|---|---|
| **A. India CPI and inflation** |||||||||
| 1 | Chaos + ML hybrid for India CPI (Sarveswararao & Ravi, IEEE SSCI 2020) | Forecast India monthly CPI | Chaos test → 9 models (GRNN best) | SMAPE 10.3, direction 83% | 6 test months; top models not significantly different; numbers only | Long walk-forward test, DM test, ranges, news-based revision | M / ⭐H | F |
| 2 | ML for India macro forecasting (Pratap & Sengupta, RBI WP 04/2019) | India CPI and its parts | ML vs statistical models | ML better; simple average of models best | Numbers only | Use the simple average as a baseline | H / ⭐H | A |
| 3 | Food inflation from news sentiment (Pratap, Ranjan, Kishore, Bhoi, RBI Occ. Papers 2021) | Tomato, onion, potato prices | Sentiment index from 9 newspapers | News improves food-inflation forecast | One index per item; no revision | Separate dated claims; revision rule | H / ⭐H | A |
| 4 | Indian inflation expectations via text mining (Banerjee, Kanodia, Ray, Indian Econ. Review 2021) | Inflation expectations | Text index by CPI category | Tracks inflation well | Aggregate; tracking only | Claim-level evidence; forecasting + revision | H / H | A |
| 5 | Inflation forecasting: text mining + macro data (P. K. Das & P. K. Das, Int. J. Econ. & Finance 16(6):92–101, 2024; **India confirmed**: Times of India headlines; full text read: single 70/30 split, no significance tests, dictionary built on full sample, text hurt RF and Elastic Net) | India inflation | Headline text series + ML ensembles | Text improves forecast | Aggregate; no revision | Claims with source and date | M / H || F |
| 6 | Predicting CPI Inflation in India: a 'Suite' of models (Mohan, Hasan, Roy, Sarkar, John, RBI Bulletin Jun 2025): **full text**: 216 models, 36/96-month rolling windows, SAAR target, ~70% lower RMSE than RW, DM+HLN tests, split-normal bands | Headline and core CPI | Weighted statistical + ML + DL | Mix beats single models | Numbers only | Official baseline to beat | H / H | A |
| 7 | MPCE prediction (Karthick et al., IEEE ICACRS 2025) | India household spending | LSTM on CPI, GDP, unemployment | R² 0.93 | 3 real points, rest interpolated; ~7 test points | Real monthly CPI target | L / M | F |
| 8 | Industrial workers' inflation (Amirthavarshini, Singh, Prasanna Kumar, IEEE WiSPNET 2024) | Industrial-worker CPI | LSTM, BiLSTM, XGBoost, RF | — | Numbers only | — | M / M | A |
| 9 | CPI prediction for India: statistical vs neural networks (Singh, Shukla, Jos, IEEE INOCON 2023) | India CPI | Statistical vs LSTM | Statistical won | Small data | Supports simple baselines | M / H | A |
| 10 | Deep learning for EM inflation (Mahajan & Srinivasan, CAFRAL 2019) | EMs incl. India | Deep networks | India: 44–63% lower error, **except 1 month ahead** | Numbers only | Our horizon is 1 month: shows it is hard | H / H | A |
| **B. News or text indices (other countries)** |||||||||
| 11 | Online News-Based Economic Sentiment Index (Kang et al., IEEE Trans. Big Data 2025) | Korea ICT economy | KoBERT relevance + sentiment → one index → VAR | RMSE 1.718 vs 1.736 | ~1% gain, 8 quarters, no test; one number | Traceable claims; revision; more test months | M / ⭐H | F |
| 12 | InflaBERT (Allard, Teiletche, Zinebi, arXiv 2024) | US inflation nowcast | BERT news index | Small gain | One index | Claim-level evidence | M / H | A |
| 13 | LLM news inflation expectations (Tawichsri, Tuarob, Nookhwun, Sangasaeng, PIER DP 252, 2026) | Thailand inflation | LLM news index | RMSE down up to 32% | One index; not India | Claims + revision for India | M / H | A |
| 14 | News indices: Philippines (Guliman et al., BSP), Russia (Volgina 2025), Brazil (PROPOR 2026), China (Fan et al. 2025); ❌ France/Reddit removed (not found) | Inflation | Mood indices + ML | Usually helps | All aggregate; none India | Same as above | M / M | A |
| **C. LLM and deep forecasting** |||||||||
| 15 | LSTM vs Transformer vs LLM (Fang et al., IEEE ISCMI 2024) | S&P 500 prices | LSTM, GPT-3.5 zero-shot | 15–23% (guess ≈ 14%) | Copied baseline; outliers removed after; LLM memory | LLM only extracts; a numeric model forecasts | L / M | F |
| 16 | STCInterLLM (Li et al., IEEE Trans. Cybernetics 2025) | Power and traffic | Causal encoder + LLM | ≥7.5% better MAE | 8 GPUs; numbers only | "Check link first" → 4 revision checks | H / M | F |
| 17 | LLM trajectory with chain-of-thought (Liu et al., IEEE IC-NIDC 2025) | Car paths | GPT-4 CoT → small Qwen | 23% better, 28 ms | Traffic only | Step-by-step extraction; small free model | M / L | F |
| 18 | TimeRAG (Yang, Wang, Zheng, Jin, arXiv 2024; ICASSP not confirmed) | LLM forecasting | Retrieve similar past patterns | ~3% better | No news; no revision | — | M / M | A |
| 19 | From News to Forecast (Wang et al., NeurIPS 2024) | News + time series | Agents pick news, reflect, fix forecast | Better accuracy | Not India; no update-strategy test | Explicit rule tested vs never/always update | H / ⭐H | A |
| 20 | ChatMacro (Alam, Boyle, Li, Sekhposyan, SF Fed 2026) | US inflation by ChatGPT | Real-time vs backtest | Real-time forecasts **stale** | No evidence trail | Revision rule + live trial | H / ⭐H | A |
| 21 | Artificial Intelligence and Inflation Forecasts (Faria-e-Castro & Leibovici, St. Louis Fed WP 2023-015) | US inflation | LLM as forecaster | Beat survey | Likely leakage | Leakage controls | M / M | A |
| 22 | Forecasting inflation with AI, GPT-4o Mini (Gonzalez, Rev. Métodos Cuantitativos) | Argentina | LLM as forecaster | Failed on spikes | No evidence | — | M / L | A |
| 23 | Stock trend MS-MI (Srivani et al., IEEE GSEACT 2026) | Dow Jones up/down | spaCy + VADER + XGBoost | 95.8% | **Leakage**: same-day close as input | Strict evidence cutoff dates | L / M (warning) | F |
| **D. Event graphs and causality** |||||||||
| 24 | STEM event model (Schramm, IEEE ICKG 2023) | Events + time series in a KG | Ontology: Event, Actor, Place, Time, Impact | No results | Never forecasts | Working claim graph in a real loop | M / ⭐H | F |
| 25 | Knowledge-Based News Event Analysis and Forecasting Toolkit (Hassanzadeh et al., IBM, IJCAI 2022 demo) | News → KG | Concept mapping, human causal analysis | Demo | Not numeric | — | M / M | A |
| 26 | LLM multi-causal event mining (2025) | Finance text | Event graph, multi-hop | — | Past only | Cause chains for claims | — / M | N |
| 27 | News graph for oil price (2026) | Oil price | LLM + GNN + TFT | — | No uncertainty; costly | News → number idea | — / M | N |
| **E. Revision and evaluation** |||||||||
| 28 | Does updating judgmental forecasts improve accuracy? (O'Connor, Remus, Griggs, Int. J. Forecasting 16(1), 2000) | When to update | Experiment | Helps for trends only | Mechanical | Selective revision | H / ⭐H | A |
| 29 | Stability-aware metric (Ma, Pomazkin, Saggese, Smith, arXiv 2026) | Forecast flip-flops | Stability metric | — | — | Count unnecessary revisions | M / H | A |
| 30 | Lookahead-bias test (Gao, Jiang, Yan, CUHK, arXiv 2025) | LLM memory | LAP test | Gains vanish after training cutoff | — | Run this check on our extraction | H / ⭐H | A |
| 31 | Chronologically consistent LLMs (He, Lv, Manela, Wu, arXiv 2025) | LLM memory | Date-limited training | Bias modest | — | Option or stated limitation | M / M | A |
| 32 | ForecastBench (Karger et al., ICLR 2025) | AI forecasting test | Score before resolution | — | US yes/no only | Fits Minor 2 | H / M | A |
| **F. Your earlier list (other domains)** |||||||||
| 33 | LLMs for conflict outcomes; MENTOR; LLM China stocks ×2; NIFTY big moves (2025–26) | Wars, stocks | LLMs, agents | 56% (China stocks) | No %; leakage risk; not CPI | — | — / L | N |
| 34 | Sentiment time series; LLM-agent survey; FinPulse (2026–27) | Mood, survey, markets | LLM agents | — | Not CPI | Background | — / L–M | N |
| 35 | Disaster UWSN; climate migration ABM; RL attention; multi-task events (TKDE) | Other fields | ML, RL | — | Not economics | — | — / L | N |
| 36 | CausalFormer; ST-LLM+; building load LLMs ×2; graph LLM survey (TKDE, TPWRS 2025–26) | Causality, traffic, power | Transformers, LLMs | Load error −57% | No events | Background | H / L | N |
| 37 | **NEW:** Inflation Forecasting in India: Are ML Techniques Useful? (Singh & Bhoi, RBI Occasional Papers 43(2), 2022) | India inflation | ML vs time-series models, pre- and post-COVID | ML improves forecasts | Numbers only | Baseline evidence | H / H | A |


## G. Added in round 3: revision, nowcasting and LLM updating (search level only; see `VERIFICATION.md` §G)

| # | Paper | What it does | Relation to Reflica | Read |
|---|---|---|---|---|
| 38 | Bańbura & Modugno (ECB WP 1189 / JAE 2014); Bańbura, Giannone & Reichlin (ECB WP 1275 / Oxford Handbook 2011) | Nowcast revisions = weighted sum of each release's **news** (surprise); "fully automatic"; revisions attributed per series; HICP only as a side target (BGR) | **Closest prior idea:** explainable, magnitude-selective revision, but on **numeric releases**, with **no gate** and **no update-policy comparison** | **F** (WP versions) |
| 39 | Modugno (2013, IJF 29(4):664–675) | News decomposition applied to **US CPI inflation** with daily raw-material and weekly gasoline prices; significantly better at h = 0–1 than RW/IMA; gains from energy and transport; financial data marginal | Closest **inflation** precedent: automatic, numeric, no gate, no text | Partial (intro + abstract) |
| 40 | Thorsrud (JBES, pp. 393–409, online 2018); Kalamara et al. (2022, JAE) | Newspaper topics or terms inside nowcast / forecast models; text helps inflation and GDP. Thorsrud uses a **latent threshold** that switches news **topics** on/off over time (a topic-level, learned gate) | Text as **aggregate series**, no claim gate | A |
| 41 | Nordhaus (1987); Isiklar et al. (2006); Coibion & Gorodnichenko (2015) | Revision efficiency: forecasters **smooth / under-react** | Evaluation tools for our revisions | A |
| 42 | O'Connor et al. (2000); Goodwin (2000); Fildes et al. (2009) | When adjusting a forecast helps: large, informed changes help, small ones hurt | Conceptual precedent for a gate (human, not text-automated) | A |
| 43 | Atanasov et al. (2020) | Best humans update **often, in small steps** | We must test a **small-step policy** too | A |
| 44 | Blackburn et al. (1986) | Change-cost / freeze rules reduce planning nervousness | Threshold precedent (operations) | A |
| 45 | EvolveCast (Yuan et al. 2025) [A]; **BLF (Murphy 2026) [F]**; **Forecast-Dojo (Ye et al. 2026) [F]**; Corroboration Illusion (Lu & Zhang 2026) [A] | LLM agents revising event forecasts. **Forecast-Dojo keeps a claim-level, dated evidence ledger (provenance notes, active/superseded) across successive dates**; BLF updates a belief state within one research loop | **Closest on claim logs**, but the LLM decides (no scored gate), the LLM is the forecaster, binary events, no update-policy comparison | F/A |
| 46 | **LiveMacroEval**: Zhao, Zhang, Ye, Cao, Xie, Chava (2026), "Can LLMs Take the Pulse of the Economy?" arXiv 2608.30110 | LLM agents with web search give **hourly US CPI and macro nowcasts** until release; live 6 months; GPT-5 ≈ Bloomberg consensus; agents weakest on inflation | **News-driven CPI revision already exists (US, LLM judgement)**; no explicit scored gate known; numeric forecaster and policy comparison absent (search-level) | S |

**Bottom line (revised in round 3).** Numbers-only models (1, 2, 6–10, 15–18) and aggregate text indices (3–5, 11–14, 40) dominate. Revision itself is well studied:
- nowcasting news decomposition attributes revisions to numeric surprises (38, 39);
- judgment research shows when adjustments help (42);
- LLM agents now revise event forecasts with dated news (45).

What we have **not found** is an explicit, pre-registered **gate on individual text claims** (novelty, reliability, relevance, strength) for a **monthly inflation** forecast, tested against never/always/small-step policies. This is provisional: 38–45 are search-level only.
