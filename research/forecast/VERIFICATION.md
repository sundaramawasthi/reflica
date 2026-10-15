# Step B: Verification of the literature table (15 Oct 2026)

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
