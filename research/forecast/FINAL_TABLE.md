# Final combined table: all papers (15 Oct 2026)

**Read:** F = full text read; A = abstract or summary only; N = from your own notes only.
**Trust / Use:** H = high, M = medium, L = low. ⭐ = must read or cite.

| # | Paper (authors, venue, year) | Problem | Method | Result | Gap / weakness | How Reflica fills it | Trust / Use | Read |
|---|---|---|---|---|---|---|---|---|
| **A. India CPI and inflation** |||||||||
| 1 | Chaos + ML hybrid for India CPI (Sarveswararao & Ravi, IEEE SSCI 2020) | Forecast India monthly CPI | Chaos test → 9 models (GRNN best) | SMAPE 10.3, direction 83% | 6 test months; top models not significantly different; numbers only | Long walk-forward test, DM test, ranges, news-based revision | M / ⭐H | F |
| 2 | ML for India macro forecasting (Pratap & Sengupta, RBI WP 04/2019) | India CPI and its parts | ML vs statistical models | ML better; simple average of models best | Numbers only | Use the simple average as a baseline | H / ⭐H | A |
| 3 | Food inflation from news sentiment (Pratap, Ranjan, Kishore, Bhoi, RBI Occ. Papers 2021) | Tomato, onion, potato prices | Sentiment index from 9 newspapers | News improves food-inflation forecast | One index per item; no revision | Separate dated claims; revision rule | H / ⭐H | A |
| 4 | Indian inflation expectations via text mining (Banerjee, Kanodia, Ray, Indian Econ. Review 2021) | Inflation expectations | Text index by CPI category | Tracks inflation well | Aggregate; tracking only | Claim-level evidence; forecasting + revision | H / H | A |
| 5 | Inflation forecasting: text mining + macro data (Int. J. Econ. & Finance 2024; authors to verify) | India inflation | Headline text series + ML ensembles | Text improves forecast | Aggregate; no revision | Claims with source and date | M / H | A |
| 6 | RBI Bulletin 2025 (model combination) | Headline and core CPI | Weighted statistical + ML + DL | Mix beats single models | Numbers only | Official baseline to beat | H / H | A |
| 7 | MPCE prediction (Karthick et al., IEEE ICACRS 2025) | India household spending | LSTM on CPI, GDP, unemployment | R² 0.93 | 3 real points, rest interpolated; ~7 test points | Real monthly CPI target | L / M | F |
| 8 | CPI-IW forecasting (IEEE WiSPNET 2024) | Industrial-worker CPI | LSTM, BiLSTM, XGBoost, RF | — | Numbers only | — | M / M | A |
| 9 | CPI prediction for India (IEEE INOCON 2023) | India CPI | Statistical vs LSTM | Statistical won | Small data | Supports simple baselines | M / H | A |
| 10 | Deep learning for EM inflation (Mahajan & Srinivasan, CAFRAL 2019) | EMs incl. India | Deep networks | Weak at 1-month ahead | Numbers only | Our horizon is 1 month: shows it is hard | H / H | A |
| **B. News or text indices (other countries)** |||||||||
| 11 | Online News-Based Economic Sentiment Index (Kang et al., IEEE Trans. Big Data 2025) | Korea ICT economy | KoBERT relevance + sentiment → one index → VAR | RMSE 1.718 vs 1.736 | ~1% gain, 8 quarters, no test; one number | Traceable claims; revision; more test months | M / ⭐H | F |
| 12 | InflaBERT (Allard, Teiletche, Zinebi, arXiv 2024) | US inflation nowcast | BERT news index | Small gain | One index | Claim-level evidence | M / H | A |
| 13 | LLM news inflation expectations (PIER Thailand DP 252, 2026) | Thailand inflation | LLM news index | RMSE down up to 32% | One index; not India | Claims + revision for India | M / H | A |
| 14 | News indices: Philippines, Russia, Brazil, France, China (2023–26) | Inflation | Mood indices + ML | Usually helps | All aggregate; none India | Same as above | M / M | A |
| **C. LLM and deep forecasting** |||||||||
| 15 | LSTM vs Transformer vs LLM (Fang et al., IEEE ISCMI 2024) | S&P 500 prices | LSTM, GPT-3.5 zero-shot | 15–23% (guess ≈ 14%) | Copied baseline; outliers removed after; LLM memory | LLM only extracts; a numeric model forecasts | L / M | F |
| 16 | STCInterLLM (Li et al., IEEE Trans. Cybernetics 2025) | Power and traffic | Causal encoder + LLM | ≥7.5% better MAE | 8 GPUs; numbers only | "Check link first" → 4 revision checks | H / M | F |
| 17 | LLM trajectory with chain-of-thought (Liu et al., IEEE IC-NIDC 2025) | Car paths | GPT-4 CoT → small Qwen | 23% better, 28 ms | Traffic only | Step-by-step extraction; small free model | M / L | F |
| 18 | TimeRAG (ICASSP 2025) | LLM forecasting | Retrieve similar past patterns | ~3% better | No news; no revision | — | M / M | A |
| 19 | From News to Forecast (Wang et al., NeurIPS 2024) | News + time series | Agents pick news, reflect, fix forecast | Better accuracy | Not India; no update-strategy test | Explicit rule tested vs never/always update | H / ⭐H | A |
| 20 | ChatMacro (Alam, Boyle, Li, Sekhposyan, SF Fed 2026) | US inflation by ChatGPT | Real-time vs backtest | Real-time forecasts **stale** | No evidence trail | Revision rule + live trial | H / ⭐H | A |
| 21 | PaLM inflation forecasts (St. Louis Fed 2023) | US inflation | LLM as forecaster | Beat survey | Likely leakage | Leakage controls | M / M | A |
| 22 | GPT-4o-mini inflation (Argentina 2025) | Argentina | LLM as forecaster | Failed on spikes | No evidence | — | M / L | A |
| 23 | Stock trend MS-MI (Srivani et al., IEEE GSEACT 2026) | Dow Jones up/down | spaCy + VADER + XGBoost | 95.8% | **Leakage**: same-day close as input | Strict evidence cutoff dates | L / M (warning) | F |
| **D. Event graphs and causality** |||||||||
| 24 | STEM event model (Schramm, IEEE ICKG 2023) | Events + time series in a KG | Ontology: Event, Actor, Place, Time, Impact | No results | Never forecasts | Working claim graph in a real loop | M / ⭐H | F |
| 25 | IBM news event KG toolkit (IJCAI 2022) | News → KG | Concept mapping, human causal analysis | Demo | Not numeric | — | M / M | A |
| 26 | LLM multi-causal event mining (2025) | Finance text | Event graph, multi-hop | — | Past only | Cause chains for claims | — / M | N |
| 27 | News graph for oil price (2026) | Oil price | LLM + GNN + TFT | — | No uncertainty; costly | News → number idea | — / M | N |
| **E. Revision and evaluation** |||||||||
| 28 | Updating forecasts with new data (Int. J. Forecasting 2000) | When to update | Experiment | Helps for trends only | Mechanical | Selective revision | H / ⭐H | A |
| 29 | Stability-aware metric (arXiv 2026) | Forecast flip-flops | Stability metric | — | — | Count unnecessary revisions | M / H | A |
| 30 | Lookahead-bias test (Gao, Jiang, Yan, arXiv 2025) | LLM memory | LAP test | Gains vanish after training cutoff | — | Run this check on our extraction | H / ⭐H | A |
| 31 | Chronologically consistent LLMs (arXiv 2025) | LLM memory | Date-limited training | Bias modest | — | Option or stated limitation | M / M | A |
| 32 | ForecastBench (Karger et al., ICLR 2025) | AI forecasting test | Score before resolution | — | US yes/no only | Fits Minor 2 | H / M | A |
| **F. Your earlier list (other domains)** |||||||||
| 33 | LLMs for conflict outcomes; MENTOR; LLM China stocks ×2; NIFTY big moves (2025–26) | Wars, stocks | LLMs, agents | 56% (China stocks) | No %; leakage risk; not CPI | — | — / L | N |
| 34 | Sentiment time series; LLM-agent survey; FinPulse (2026–27) | Mood, survey, markets | LLM agents | — | Not CPI | Background | — / L–M | N |
| 35 | Disaster UWSN; climate migration ABM; RL attention; multi-task events (TKDE) | Other fields | ML, RL | — | Not economics | — | — / L | N |
| 36 | CausalFormer; ST-LLM+; building load LLMs ×2; graph LLM survey (TKDE, TPWRS 2025–26) | Causality, traffic, power | Transformers, LLMs | Load error −57% | No events | Background | H / L | N |

**Bottom line.** Every paper either predicts from **numbers only** (1, 2, 6–10, 15–18) or turns news into **one index** (3–5, 11–14). Some have **leakage or tiny tests** (1, 7, 11, 15, 23). Nobody uses **dated claims with sources** to decide **when to revise** an India CPI forecast and tests that against **never update** and **always update**. That is Reflica's gap.
