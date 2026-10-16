# Step B: Verification of the literature table (15 Oct 2026)

> **Status note (16 Oct 2026):** this is a **literature record** (research kept). Statements here about "Reflica", "our gap" or "Minor 1" were written for the CPI evidence-aware revision study, which is now **Part B** of the safer-merge Minor 1 direction. The old plan documents were removed at the user's request (they remain in git history).

**Goal:** check the title, authors, venue, year and reported result of each paper before we use it as evidence.

**How it was checked:**
- **PDF:** full text read from the IEEE PDF you uploaded (strongest check).
- **Record:** confirmed from an official page found by web search (IEEE, RBI, arXiv, NeurIPS, ICLR, RePEc, the journal's own site). The full text was **not** read, so the results come from the abstract or summary.
- Direct downloads (arXiv, RBI) are blocked from the cloud machine, so "Record" means verified **metadata plus abstract**, not full text.

**Status:**
- ✅ = verified
- ⚠️ = verified with a correction, or a detail still open
- ❌ = could not be found (do not cite yet)
- ⏳ = not checked yet

## A. Fully verified from the PDF (8 papers)

| # | Citation | Status |
|---|---|---|
| 1 | V. Sarveswararao, V. Ravi, "Chaos, Machine Learning and Deep Learning based Hybrid to forecast Consumer Price Index Inflation in India," IEEE SSCI 2020, pp. 2551–2557 | ✅ PDF |
| 7 | A.V. Karthick et al., "AI-Driven Predictive Analytics for Monthly Per Capita Expenditure using Macroeconomic Indicators," IEEE ICACRS 2025, DOI 10.1109/ICACRS67045.2025.11324119 | ✅ PDF |
| 11 | N. Kang et al., "Online News-Based Economic Sentiment Index," IEEE Trans. Big Data 11(3), 2025, DOI 10.1109/TBDATA.2024.3474211 | ✅ PDF |
| 15 | J. Fang et al., "A Comparative Study of Sequential Deep Learning Models in Financial Time Series Forecasting," IEEE ISCMI 2024, DOI 10.1109/ISCMI63661.2024.10851487 | ✅ PDF |
| 16 | S. Li et al., "Causal Intervention Is What Large Language Models Need for Spatio-Temporal Forecasting," IEEE Trans. Cybernetics 55(8), 2025, DOI 10.1109/TCYB.2025.3569333 | ✅ PDF |
| 17 | Y. Liu et al., "LLM-Driven Trajectory Prediction at Intersections with Chain-of-Thought Reasoning," IEEE IC-NIDC 2025, DOI 10.1109/IC-NIDC67200.2025.11390125 | ✅ PDF |
| 23 | N. Srivani et al., "A Comprehensive Multi-Source Multi-Instance Learning Framework for Predicting Stock Market Trends…," IEEE GSEACT 2026, DOI 10.1109/GSEACT68539.2026.11619959 | ✅ PDF |
| 24 | S. Schramm, "Constructing the Simple Timeseries Event Model," IEEE ICKG 2023, pp. 134–139, DOI 10.1109/ICKG59574.2023.00022 | ✅ PDF |

## B. Verified from official records (abstract-level results)

| # | Verified citation | What the record confirms | Status / correction |
|---|---|---|---|
| 2 | **Bhanu Pratap, Shovon Sengupta**, "Macroeconomic Forecasting in India: Does Machine Learning Hold the Key to Better Forecasts?", RBI Working Paper 04/2019 | ML generally beats statistical models; simple-average combinations beat all single models; simple weights beat complex ones; headline forecast directly is as good as from components | ✅ |
| 3 | **Bhanu Pratap, Abhishek Ranjan, Vimal Kishore, Binod B. Bhoi**, "Forecasting Food Inflation using News-based Sentiment Indicators", RBI Occasional Papers 42(2), 2021 (published 18 Oct 2022) | Tomato, onion and potato (2.2% CPI weight) sentiment from 9 English dailies, 2011–2021; sentiment moves inversely to prices; adding it improves food-inflation forecasts | ✅ (accuracy numbers need the PDF) |
| 4 | **Ashok Banerjee, Ayush Kanodia, Partha Ray**, "Deciphering Indian inflationary expectations through text mining: an exploratory approach", Indian Economic Review 56, pp. 49–66, 2021, DOI 10.1007/s41775-021-00106-9 | Economic Times and Business Line; sentiment by CPI category; tracks inflation | ✅ |
| 5 | **Pijush Kanti Das, Prabir Kumar Das**, "Improvement in Inflation Forecasting: Ensembling Text Mining with Macro Data in Machine Learning Models", Int. J. Economics and Finance 16(6), pp. 92–100, 2024, DOI 10.5539/ijef.v16n6p92 | 3.9 million headlines (Jan 2001–Jun 2023) → monthly series; text beats their own no-text ML models; an inflation word dictionary; a neural network was best | ⚠️ Authors' full names added. **Not yet confirmed that the data is Indian**; check the PDF |
| 6 | **Renjith Mohan, Saquib Hasan, Sayoni Roy, Suvendu Sarkar, Joice John**, "Predicting CPI Inflation in India: Combining Forecasts from a 'Suite' of Statistical and Machine Learning Models", RBI Bulletin, 25 Jun 2025 | Headline and CPI excl. food and fuel; statistical + ML + DL, performance-weighted; also gives density forecasts | ✅ Exact title found. A Nov 2025 follow-up covers 33 CPI sub-groups |
| 8 | **V. Amirthavarshini, Soumyendra Singh, R. Prasanna Kumar**, "Enhancing Forecasting Precision in Indian Industrial Workers' Inflation: A Comparison of Advanced Machine Learning Models", IEEE WiSPNET 2024 | CPI-IW; LSTM, BiLSTM, XGBoost, RF | ⚠️ Best model and numbers not in the record; need the PDF |
| 9 | **A. Singh, B. Shukla, J. Jos**, "Comparative Analysis of CPI prediction for India using Statistical methods and Neural Networks", INOCON 2023, DOI 10.1109/INOCON57975.2023.10101073 | Statistical model beat deep learning on the small dataset (ARIMA, Holt, GRU, LSTM) | ✅ |
| 10 | **Kriti Mahajan, Anand Srinivasan**, "Inflation Forecasting in Emerging Markets: A Machine Learning Approach", CAFRAL, 2019/2020 | India, China, South Africa; **India: deep networks cut error by ~44–63% at all horizons except 1 month ahead**; an average of networks is best | ✅ Result detail added |
| 12 | **Marc-Antoine Allard, Paul Teiletche, Adam Zinebi** (EPFL), "Enhancing Inflation Nowcasting with LLM: Sentiment Analysis on News", arXiv:2410.20198, 2024 | InflaBERT; monthly NEWS index added to the Cleveland Fed nowcast; small gain during COVID; code on GitHub | ✅ (preprint, not peer-reviewed) |
| 13 | **Tanisa Tawichsri, Suppawong Tuarob, Nuwat Nookhwun, Chinjuta Sangasaeng**, "News-Based Inflation Expectations: LLM-Assisted Measurement and Forecasting", PIER Discussion Paper 252, May 2026 | Thailand; 1.1 million Thai articles 2015–2024; topic model + LLM labels + fine-tuned BERT; RMSE down up to 32% (headline) | ✅ (earlier wrongly called "BIS 2026") |
| 14a | **Elizaveta Volgina**, "Forecasting Inflation Using News Indices", Russian J. Money and Finance 84(1), pp. 26–59, 2025 | Russia; LDA topics from RIA Novosti news; ML; 1–6 months ahead | ✅ |
| 14b | **Guliman, Arcin, Centeno, Herbo, Parmanand, Mapa** (BSP), "Hot off the Press: An Inflation News Index for the Philippines…" (CBSL conference 2024); and "Read between the headlines: can news data predict inflation?" (IFC–Bank of Italy workshop 2025) | Lexicon + RL and BiLSTM indices; improve inflation nowcasts | ✅ (venue: workshop and conference papers) |
| 14c | **Yingying Fan, Jinchi Lv, Ao Sun, Yurou Wang**, "LLM-Powered CPI Prediction Inference with Online Text Time Series", arXiv:2506.09516, 2025 | China; Sina Weibo 2019–2023; fine-tuned BERT gives a daily inflation index combined with monthly CPI | ✅ (preprint) |
| 14d | "Banque de France 2026, Reddit + LLM for US inflation" | **Not found.** Closest matches: Saito & Tsugawa, "Learning Inflation Narratives from Reddit" (ICWSM 2026, arXiv 2603.21501), and André, Bessec, Goulby (LLMs vs Banque de France models for **French GDP**, 2025) | ❌ **Remove**; replace with the Saito & Tsugawa paper if needed |
| 14e | Brazil, PROPOR 2026: "Enhancing Brazilian Inflation Forecasts through Sentiment Analysis Using LLMs" | Seen in search results only | ⚠️ Authors not checked |
| 18 | **Silin Yang, Dong Wang, Haoqi Zheng, Ruochun Jin**, "TimeRAG: Boosting LLM Time Series Forecasting via Retrieval-Augmented Generation", arXiv:2412.16643, 2024 | Retrieval of similar past segments for an LLM | ⚠️ **ICASSP 2025 venue not confirmed**; cite as arXiv unless the IEEE record is found |
| 19 | **Xinlei Wang, Maike Feng, Jing Qiu, Jinjin Gu, Junhua Zhao**, "From News to Forecast: Integrating Event Analysis in LLM-Based Time Series Forecasting with Reflection", NeurIPS 2024 (arXiv 2409.17515) | LLM agents filter news and reflect on errors; fine-tuned LLaMA-2; code and data released | ✅ (datasets and numbers need the PDF) |
| 20 | **Alam, Boyle, Li, Sekhposyan**, "ChatMacro: Evaluating Inflation Forecasts of Generative AI", FRB San Francisco WP 2026-04 | Real-time ChatGPT US inflation forecasts are inaccurate and stale; pseudo-out-of-sample results look fine | ✅ (first names still needed) |
| 21 | **Miguel Faria-e-Castro, Fernando Leibovici**, "Artificial Intelligence and Inflation Forecasts", FRB St. Louis WP 2023-015, DOI 10.20955/wp.2023.015 (Fed. Reserve Bank of St. Louis Review, Nov 2024) | PaLM forecasts 2019–2023 beat the SPF in most years; **in-sample**, so the training data may overlap | ✅ Title corrected |
| 22 | **Daniela Agostina Gonzalez** (Univ. Nacional de Córdoba), "Forecasting inflation with Artificial Intelligence…", Rev. Métodos Cuantitativos para la Economía y la Empresa (Univ. Pablo de Olavide) | GPT-4o Mini, Argentina 2023–2024, knowledge restricted to the forecast date; comparable to the central bank's REM survey at low and medium inflation, worse on spikes (e.g. MAE 0.85 vs 0.73) | ⚠️ Year and volume not confirmed |
| 25 | **Oktie Hassanzadeh et al.** (IBM Research, 10 authors), "Knowledge-Based News Event Analysis and Forecasting Toolkit", IJCAI 2022 Demo Track, pp. 5904–5907, DOI 10.24963/ijcai.2022/850 | Demo | ✅ |
| 28 | **Marcus O'Connor, William Remus, Ken Griggs**, "Does updating judgmental forecasts improve forecast accuracy?", Int. J. Forecasting 16(1), pp. 101–109, 2000 | Updating helps for trended series, no benefit for stable series | ✅ Full reference found. Related: Goodwin (2000), same issue, pp. 85–99: forecasters make **unnecessary changes** to reliable forecasts |
| 29 | **Chutian Ma, Grigorii Pomazkin, Giacinto Paolo Saggese, Paul Smith** (Causify), "Beyond Accuracy: A Stability-Aware Metric for Multi-Horizon Forecasting", arXiv:2601.10863, 2026 | Stability-aware metric | ⚠️ v1 and v2 report different numbers (15.8% vs 91.1%); cite the version you use |
| 30 | **Zhenyu Gao, Wenxi Jiang, Yutong Yan** (CUHK), "A Test of Lookahead Bias in LLM Forecasts" (later titled "Detecting Lookahead Bias in LLM Forecasts"), arXiv:2512.23847, 2025 | Lookahead-propensity test | ✅ |
| 31 | **Songrun He, Linying Lv, Asaf Manela, Jimmy Wu** (WashU), "Chronologically Consistent Large Language Models", arXiv:2502.21206, 2025 | ChronoBERT and ChronoGPT trained only on past text; look-ahead bias modest in a returns test | ✅ (the earlier note "Chen et al." was **wrong**) |
| 32 | **Ezra Karger, Houtan Bastani, Chen Yueh-Han, Zachary Jacobs, Danny Halawi, Fred Zhang, Philip E. Tetlock**, "ForecastBench: A Dynamic Benchmark of AI Forecasting Capabilities", ICLR 2025 | 1,000 questions with unknown answers; experts beat the best LLM (p < 0.001) | ✅ |

## C. New paper found during verification

| Citation | Why it matters |
|---|---|
| **Nishant Singh, Binod B. Bhoi**, "Inflation Forecasting in India: Are Machine Learning Techniques Useful?", RBI Occasional Papers 43(2), 2022 | ML improves India inflation forecasts across horizons, tested pre- and post-COVID. **Add as a key India baseline paper.** |

## D. Not yet verified

| # | Items | Note |
|---|---|---|
| 26, 27, 33–36 | Papers from your earlier list (`Research_Work_paper.docx`) | Titles in your notes are short. Send exact titles or DOIs and I will check them |
| — | Asati (OSF preprint), arXiv 2401.00249 (CPI under uncertainty), Bank of England "Bank Underground" 2020 | Low priority |

## E. What changed after verification

1. **Corrected:** #13 is PIER Thailand, not BIS; #21 title is "Artificial Intelligence and Inflation Forecasts"; #31 authors are He, Lv, Manela, Wu.
2. **Removed:** the "Banque de France 2026 Reddit" paper could not be found.
3. **Open detail:** #5 (Das & Das) is not yet confirmed to use **Indian** data. This matters because it was listed as our closest India text paper.
4. **Venue not confirmed:** #18 TimeRAG (ICASSP); cite it as arXiv for now.
5. **Strengthened:** #10 shows deep networks fail exactly at the **1-month horizon** for India, which is our Minor 1 horizon. #28 and Goodwin (2000) give classic support for **selective** revision.
6. **Added:** Singh & Bhoi (2022), RBI.

**Effect on the research gap:** no verified paper changes it. The India news papers (#3, #4, #5) all build **indices**, and none decides **when to revise**. But #3, #5 and #19 must be read in **full text** before we call the gap verified.

---

## F. Two levels of verification (added 15 Oct 2026, after review)

**Level 1, bibliographic:** the title, authors, venue and year exist and are correct. This is done for most of the papers above.
**Level 2, content:** the method, update mechanism, baselines, evaluation protocol and limitations, checked from the **full text**. This is **not done** for any of the priority papers below.

The research gap is **not established** until Level 2 is done for the closest studies. The fact that the Indian news studies use **aggregate indices** does not, by itself, show that no study uses claim-level evidence or selective revision. That has to be checked directly.

| Priority | Paper | Level 1 | Level 2 | Full-text link (open in a browser; blocked from the cloud) |
|---|---|---|---|---|
| 1 | Pratap, Ranjan, Kishore, Bhoi (2021), RBI food-inflation news sentiment | ✅ | ✅ see `LEVEL2_READINGS.md` | RBI PDF (see section B); ResearchGate record "Catching up on the TOP News: Text-mining for Food Inflation Outlook in India" (pub. 361346038); SSRN 4125337. **Check whether the RG/SSRN title is the same study or an earlier version.** |
| 2 | Wang et al. (2024), From News to Forecast, NeurIPS | ✅ | ✅ see `LEVEL2_READINGS.md` | proceedings.nips.cc …/6aef8bffb372096ee73d98da30119f89-Paper-Conference.pdf |
| 3 | Mohan et al. (2025), RBI Bulletin | ✅ | ⏳ | RBI Bulletin, 25 Jun 2025 (PredictingCPIInflation25062025.pdf) |
| 4a | Pratap & Sengupta (2019), RBI WP 04/2019 | ✅ | ✅ see `LEVEL2_READINGS.md` | isid.ac.in/~epu/acegd2019/papers/BhanuPratap.pdf; RBI WP PDF |
| 4b | Singh & Bhoi (2022), RBI Occasional Papers 43(2) | ✅ | ✅ see `LEVEL2_READINGS.md` | RBI bs_viewcontent Id=4345; ResearchGate 378023944 |
| 5 | O'Connor, Remus, Griggs (2000), IJF | ✅ | ⏳ | ScienceDirect (paywalled; try GLA library access) |
| 6 | Gao, Jiang, Yan (2025), lookahead bias | ✅ | ✅ see `LEVEL2_READINGS.md` | arxiv.org/pdf/2512.23847 |

### Level-2 extraction checklist (fill one per paper)

1. **Target and data:** which series, country, frequency, period, and the source of the text.
2. **How new information enters:** as an index, as features, as retrieved documents, or as separate claims? At what unit (day, article, claim)?
3. **Update or revision mechanism:**
   - Is there one? When does it trigger?
   - Does it change the *forecast*, the *model*, or the *news-selection logic*?
   - Is it applied at training time or at forecast time?
   - Does it decide **whether** to revise a specific forecast?
4. **Evidence properties used:** novelty, source reliability, relevance, strength, or conflict between sources?
5. **Baselines:** naive, ARIMA, ML; never-update or always-update strategies?
6. **Evaluation protocol:** walk-forward or fixed split; test length; horizons; significance tests.
7. **Leakage control:** point-in-time text, vintage data, LLM training-cutoff issues.
8. **Uncertainty:** intervals or density forecasts, and coverage.
9. **Explainability:** can a forecast change be traced to specific news?
10. **Limitations:** as stated by the authors, and as we see them.
11. **Overlap with Reflica:** which of E1–E6 it already covers, with quotes and page numbers.

---

## G. Round 3: revision, nowcasting and LLM-updating literature (15 Oct 2026)

**Access.** Every paper host was tested and **all were unreachable** from the cloud environment: ECB, arXiv, RBI, RePEc, ScienceDirect, SSRN, Wiley, Crossref, OpenAlex, and others. **No paper in this round was read in full.** Everything below comes from **web-search summaries of abstracts, official pages and secondary sources**. Level 2 (content) is **not done** for any of them.

| Paper | Level 1 (identity) | Level 2 | What the search-level evidence says | Source of evidence |
|---|---|---|---|---|
| Bańbura & Modugno (2014), "Maximum likelihood estimation of factor models on datasets with arbitrary pattern of missing data", J. Applied Econometrics 29(1):133–160 (ECB WP 1189, 2010) | ✅ | ❌ no access | Formalises the **news decomposition**: a nowcast revision is split into contributions from each release's "news" (actual minus model expectation). Implemented in statsmodels `.news()`, R `dfms::news()` and the ECB toolbox | EconPapers record; ECB WP 3004 toolbox; statsmodels / dfms docs |
| Bańbura, Giannone & Reichlin (2011), "Nowcasting", Oxford Handbook of Economic Forecasting, pp. 63–90 (ECB WP 1275, 2010) | ✅ | ❌ | "requires the assessment of the impact of new data on the subsequent forecast revisions"; revisions expressed as a function of model-based news; euro-area GDP 2008Q4 example | OUP page; ECB WP 1275 summary |
| Modugno (2013), "Now-casting inflation using high frequency data", IJF 29(4):664–675 (ECB WP 1324) | ✅ | ❌ | Daily/weekly factor model for **inflation**; lets one "disentangle the model-based news from each data release and … assess its impact on the forecast revision"; energy prices help, financial variables add little | IDEAS abstract; ECB WP |
| Knotek & Zaman (Cleveland Fed inflation nowcasting; WP 14-03; 2017 JMCB [verify]) | ⚠️ | ❌ | Nowcast moves with daily oil/gasoline prices; core components change only when CPI/PCE data arrive | Cleveland Fed FAQ and WP pages |
| Thorsrud, "Words are the new numbers: a newsy coincident index of the business cycle", JBES (DOI 10.1080/07350015.2018.1506344) [verify volume] | ✅ | ❌ | **Newspaper topics (LDA) inside a time-varying DFM** give a daily GDP index; companion paper "Nowcasting using news topics" | Norges Bank WP 20/2016 and 21/2016 |
| Kalamara, Turrell, Redl, Kapetanios, Kapadia (2022), "Making text count", J. Applied Econometrics (BoE SWP 865) | ✅ | ❌ | Newspaper text improves forecasts of GDP, **inflation** and unemployment; gains largest in stress periods | BoE page; replication-data record |
| Zheng et al. (2024), "Words or numbers? Macroeconomic nowcasting with textual and macroeconomic data", IJF 40(2):746–761 | ✅ | ❌ | China; content **not verified** (abstract not retrieved) | Xiamen faculty page; IDEAS |
| Nordhaus (1987), "Forecasting efficiency: concepts and applications", REStat 69:667–674 | ✅ (via secondary sources) | ❌ | Weak efficiency for **fixed-event forecasts**: revisions should be serially uncorrelated; positive correlation = "smoothing", negative = "jumpiness" | Secondary (USDA forecast-revision studies) |
| Isiklar, Lahiri & Loungani (2006), "How quickly do forecasters incorporate news?", JAE 21(6):703–725 | ✅ | ❌ | Consensus GDP forecasts in 18 countries: revisions **serially correlated** (inefficient); slow use of foreign news | MPRA / RePEc abstract |
| Coibion & Gorodnichenko (2015), "Information rigidity and the expectations formation process", AER [verify issue] | ✅ (NBER w16537) | ❌ | Forecast revisions **predict** forecast errors → **under-reaction** to new information | NBER / IMF records; secondary |
| O'Connor, Remus & Griggs (2000), IJF 16(1):101–109 | ✅ | ❌ | Updating helped for **trended** series; "no value in updating … when the time series were relatively stable" | IAOR abstract |
| Goodwin (2000), "Improving the voluntary integration of statistical forecasts and judgment", IJF 16(1):85–99 | ✅ | ❌ | Forecasters make **unnecessary changes** to reliable statistical forecasts | IAOR record |
| Fildes, Goodwin, Lawrence & Nikolopoulos (2009), "Effective forecasting and judgmental adjustments", IJF 25(1):3–23 | ✅ | ❌ | 60,000+ forecasts; **large adjustments improved accuracy, small ones often damaged it**; upward adjustments often wrong (optimism) | Lancaster / Bath abstracts |
| Atanasov, Witkowski, Ungar, Mellers & Tetlock (2020), "Small steps to accuracy: incremental belief updaters are better forecasters", OBHDP 160:19–35 | ✅ | ❌ | 400,000+ forecasts: the best forecasters update **frequently in small steps**; weak forecasters confirm or make rare large jumps | IDEAS; Wharton PDF listing; author blog |
| Blackburn, Kropp & Millen (1986), "A comparison of strategies to dampen nervousness in MRP systems", Management Science 32(4):413–429 | ✅ | ❌ | **Change cost** or **freezing** dominate for reducing re-planning "nervousness": a threshold-like rule in operations | INFORMS / IDEAS |
| Yuan, Ding & Vlachos (2025), "Do Language Models Update their Forecasts with New Information?" (EvolveCast), arXiv 2509.23936 | ✅ | ❌ | LLM updates after post-cutoff news are **conservative / under-responsive** vs humans | arXiv abstract; aggregators |
| Murphy (2026), "Agentic Forecasting using Sequential Bayesian Updating of Linguistic Beliefs" (BLF), arXiv 2604.18576 | ✅ | ❌ | An agent keeps a **belief state (probability + structured evidence summary)** revised at each tool step; Platt calibration; best on ForecastBench backtests; removing the belief state hurts more than removing search | arXiv abstract; Pith summary |
| Lu & Zhang (2026), "The Corroboration Illusion: When More News Makes LLM Forecasts Less True", arXiv 2609.22246 | ✅ | ❌ | One injected article flips 56% of RAG forecasts; source allow-lists, isolate-then-aggregate and perplexity filters each have **cheap bypasses** | arXiv abstract |
| Forecast-Dojo (2026), arXiv 2609.28876 | ⚠️ authors not recorded | ❌ | Replay environment: agents **revisit predictions at successive dates** (1,568 Polymarket events, 18.8M dated articles); near-duplicate removal; forecasts improve as dated evidence arrives; a belief notebook doesn't consistently help | arXiv abstract |
| Halawi, Zhang, Chen, Steinhardt (2024), "Approaching Human-Level Forecasting with Language Models", NeurIPS 2024 | ✅ | ❌ | Retrieval + LM + aggregation, tested after the cutoff, nears the crowd | arXiv / NeurIPS |
| Mohan et al. (2025), RBI Bulletin | ✅ | ❌ (PDF unreachable) | Performance-weighted suite; density forecasts. **Weights and RMSE not retrieved** | RBI page |
| Das & Das (2024), IJEF 16(6) | ✅ | ❌ | Authors at **IIFT Kolkata**; 3.9M headlines 2001–2023; inflation word dictionary; ANN best. **Newspaper names and country of the target still not confirmed** | CCSE / RePEc abstract |

### Round 4 update (15 Oct 2026): user-uploaded full texts

| Paper | Level 2 now | Note |
|---|---|---|
| Bańbura & Modugno, ECB WP 1189 (2010) | ✅ full text (WP version; JAE 2014 not compared) | See `LEVEL2_READINGS.md` §6 |
| Bańbura, Giannone & Reichlin, "Nowcasting", ECB WP 1275 (2010) | ✅ full text (WP version; Oxford Handbook chapter not compared) | §7 |
| Das & Das (2024), IJEF 16(6):92–101 | ✅ full text | §8. **India confirmed** (Times of India headlines). Pages are **92–101**, not 92–100 |
| Mohan et al. (2025), RBI Bulletin | ❌ still not read in full | Only the RBI press-release highlights (pasted by the user) |
| Modugno 2013; Thorsrud; Kalamara et al.; BLF; Forecast-Dojo; EvolveCast; Corroboration Illusion | ❌ | Still search-level |

### Round 5 update (15 Oct 2026): Thorsrud, publisher abstract page (pasted by the user)

| Paper | Level 1 | Level 2 | Note |
|---|---|---|---|
| L. A. Thorsrud, "Words are the New Numbers: A Newsy Coincident Index of the Business Cycle", *J. Business & Economic Statistics*, pp. **393–409**, DOI 10.1080/07350015.2018.1506344. Received 1 Nov 2017; accepted author version 9 Aug 2018; published online 5 Nov 2018 | ✅ publisher page | ⚠️ **abstract only** (full text not read) | Volume and issue number are **not shown** on the pasted page; check them before citing |

### Round 5b (15 Oct 2026): Modugno (2013), ScienceDirect preview (pasted by the user)

| Paper | Level 1 | Level 2 | Note |
|---|---|---|---|
| M. Modugno, "Now-casting inflation using high frequency data", *Int. J. Forecasting* 29(4):664–675, 2013, DOI 10.1016/j.ijforecast.2012.12.003 | ✅ publisher page | ⚠️ **partial**: abstract, full Introduction and section snippets; Sections 2–6 not read | **Correction:** the empirical target is **US CPI inflation** ("The empirical analysis focuses on US CPI inflation"), not the euro area. The ECB WP data list (euro-area Weekly Oil Bulletin) misled the earlier search summary |

### Round 6 update (15 Oct 2026)

| Paper | Level 1 | Level 2 | Note |
|---|---|---|---|
| Mohan, Hasan, Roy, Sarkar & John (2025), RBI Bulletin, 25 Jun 2025 | ✅ | ✅ article text (pasted by the user); charts and equation images missing | `LEVEL2_READINGS.md` §12 |
| Ye, Wang et al. (2026), Forecast-Dojo, arXiv 2609.28876v1 | ✅ authors now confirmed (11 authors, Georgia Tech / Amazon / UF) | ✅ key sections (method, prompt appendix, results) | §13 |
| Murphy (2026), BLF, arXiv 2604.18576**v5**: title now "Agentic Forecasting with Structured Linguistic Beliefs" | ✅ | ✅ key sections | §14 |
| Kalamara et al. (2020), BoE SWP 865 | ✅ | ✅ key sections | §15 |
| **NEW:** Zhao, Zhang, Ye, Cao, Xie, Chava (2026), "Can LLMs take the pulse of the economy? A real-time evaluation of LLM nowcasts on macroeconomic indicators", arXiv 2608.30110 | ⚠️ citation only (from the Forecast-Dojo reference list) | ❌ | **Highest remaining risk** |
| **NEW:** John, Singh & Kapur (2020), "Inflation Forecast Combinations: The Indian Experience", RBI WP 11/2020 | ⚠️ citation only (from Mohan et al.) | ❌ | India combination baseline |

### Round 7 (15 Oct 2026): LiveMacroEval

| Paper | Level 1 | Level 2 | Note |
|---|---|---|---|
| Zhao, Zhang, Ye, Cao, Xie & Chava (2026), "Can LLMs Take the Pulse of the Economy? A Real-Time Evaluation of LLM Nowcasts on Macroeconomic Indicators" (**LiveMacroEval**), arXiv 2608.30110v1 | ✅ arXiv listing, project site, GitHub | ❌ **search-level only** (arXiv blocked; PDF not uploaded) | Hourly LLM-agent nowcasts of 16 US indicators incl. **CPI**, live 6 months; LiveMacro Score vs Bloomberg consensus; agents weakest on inflation. See `CLOSEST_METHODS.md` |

### Round 8 (16 Oct 2026)

| Paper | Level 1 | Level 2 | Where |
|---|---|---|---|
| Zhao, Zhang, Ye, Cao, Xie & Chava (2026), "Can LLMs Take the Pulse of the Economy? A Real-Time Evaluation of LLM Nowcasts on Macroeconomic Indicators" (LiveMacroEval), arXiv 2608.30110v1 [cs.CL], 31 Aug 2026 | ✅ PDF (first names confirmed: Xinyue Zhao, Ruiyi Zhang, Liqin Ye, Rui Cao, Pengtao Xie, Sudheer Chava) | ✅ **full text** (main text + key appendices; App. K–N, P, Q skimmed) | `LEVEL2_READINGS.md` §16 |

### Round 9 (16 Oct 2026)

| Paper | Level 1 | Level 2 | Where |
|---|---|---|---|
| Thorsrud (2016), "Nowcasting using news topics: Big Data versus big bank", Norges Bank WP 20/2016 | ✅ (title and series from the user's PDF) | ⚠️ **reported by the user** (methods and revision sections); not checked here | `LEVEL2_READINGS.md` §17 |
| Modugno (2011), "Nowcasting Inflation Using High Frequency Data", ECB WP 1324 (IJF 2013 version) | ✅ (WP number confirmed by the user) | ⚠️ **reported by the user**; not checked here | `LEVEL2_READINGS.md` §18 |
| Thorsrud, "Words are the New Numbers" (JBES) | ✅ | ❌ **still abstract only**; the uploaded PDF was a different paper | §10 |

### Round 10 (16 Oct 2026)

| Paper | Level 1 | Level 2 | Where |
|---|---|---|---|
| Fan, Lv, Sun & Wang (2025), "LLM-Powered CPI Prediction Inference with Online Text Time Series", arXiv 2506.09516v1 | ✅ PDF | ✅ key sections + full keyword check | `LEVEL2_READINGS.md` §19 |
| Thorsrud, "Words are the New Numbers" (JBES) | ✅ | ❌ **still abstract only** (the user re-pasted the abstract; no full text) | §10 |

