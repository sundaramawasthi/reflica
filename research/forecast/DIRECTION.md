# Research direction change: from Reflica to honest AI forecasting of Indian events

Date: 13 October 2026.
Status: decided by the user; **guide approval still pending**.

## 1. What changed

The M.Tech research moves from **Reflica** (revising a plan graph correctly when a fact changes) to **predictive AI**: an AI agent that forecasts major Indian events honestly and shows their effects.

Why: the user wants to become a leading researcher in predictive AI. A literature review of 21 recent papers (2024–2027, including 6 IEEE Q1 journal papers) found an open space in AI event forecasting, especially for India.

## 2. What happens to the existing Reflica work

- **Keep everything.** Do not delete the repo, the benchmark, Categories 1–7, the 63 scenarios, or baselines B3, B4a, B4b (and B5 v0.1.0, already frozen).
- **Pause new Reflica work** (no new categories, no B5 changes) unless the user asks.
- The Reflica graph engine (a change spreads through a dependency graph and stops when nothing more changes) will be **reused in the final project** as the engine that propagates a forecast event to its downstream effects. The "unknown" idea (Category 7) becomes the abstention rule.

## 3. The new research

**Research area:** CSE → Artificial Intelligence → Predictive AI / Forecasting → Agent-based event forecasting.
**Domain:** India: economy, critical infrastructure, geopolitics.

**Research idea (one line):** An AI agent that reads Indian news, predicts major Indian events with an honest (calibrated) % chance, shows what will happen next because of them, says "I don't know" when evidence is weak, and is tested live against what really happens.

**Research gaps found in the literature (to be re-checked, see README "Literature checks"):**
1. No honest % (forecasts are rarely calibrated or checked).
2. No system says "I don't know" (no abstention).
3. Little live testing; most work tests on old data the LLM may already know (leakage). Only ForecastBench tests on unresolved events.
4. Cause chains are extracted from past text but never used forward to predict effects.
5. India is missing (only one paper, Indian stock indices).
Supporting: rare big events are fragile; single-case evaluation; LLM extraction errors are never measured.

## 4. Project plan (dates are estimates; check GLA rules)

**Minor Project 1, India Forecast Benchmark (approx. Jan–May 2027).**
Question: how accurately and honestly do current LLMs forecast Indian economic, infrastructure and geopolitical events, compared with Western events and simple baselines?
Build: 200–300 date-stamped questions about future Indian events with clear answer sources (RBI, MOSPI, Grid-India, CWC, IMD, PIB, GDELT, ACLED); a runner that asks 3–4 LLMs with and without news search and stores answers before resolution; baselines "same as last time" and "base rate"; a scorer.
Measure: accuracy, Brier score, calibration, Indian vs Western questions. Output: conference paper 1 + open benchmark v1.

**Minor Project 2, honest forecasting agent (approx. Jul–Dec 2027).**
Question: does an agent with Indian news search, calibration and an abstain rule make fewer confident mistakes than plain LLMs while still answering most questions?
Build: retrieval agent with reasons; ensemble + calibration (Platt, isotonic or conformal); abstain rule (few sources, disagreeing sources, disagreeing runs); live testing.
Measure: Brier, calibration error, false-confidence rate, coverage, cost. Output: conference paper 2 + open agent.

**Final Project, impact-aware forecasting tested live (final year).**
Question: if a forecast is passed through an Indian cause–effect graph, are downstream effects predicted better than by asking the LLM directly?
Build: cause–effect graph for one or two systems (heatwave → power demand → shortage → water → hospitals/industry; monsoon → crops → food prices → CPI → RBI); propagate forecast probabilities with the Reflica engine; run live 6–12 months.
Output: final research paper (main AI conference, International Journal of Forecasting or IEEE TKDE) + thesis + live India Forecast Board.

## 5. Key papers to read first
- LLM-based Agents for Forecasting and Prediction: Methods, Training, Evaluation, and Applications (survey, arXiv 2608.23058, 2026)
- ForecastBench: A Dynamic Benchmark of AI Forecasting Capabilities (ICLR 2025)
- From News to Forecast: Integrating Event Analysis in LLM-Based Time Series Forecasting with Reflection (NeurIPS 2024)
- Application of Large Language Models in the Problem of Event Forecasting (2025)
- Hierarchical Semantic Extraction and Heterogeneous GNNs for Event-Driven Time Series Forecasting (Scientific Reports 2026)
- A Large Language Model Framework for Predicting Significant Equity Index Fluctuations (NIFTY, 2026)

Full analysis of all papers: review page https://claude.ai/artifact/B61G9cki25mLr8aRaSXK81 and the user's files `LITERATURE_FORECASTING.md` and `Research Brief - Honest AI Forecasting of Indian Events.docx` (not in this repo).

## 6. How to work with the user
- The user **writes the code themselves**. Claude explains, plans and reviews; it does not write whole modules unless asked.
- The repository and its tests are the source of truth for status, not plans or schedules.
- Messages are often voice-typed; answer in short, simple English.
- Keep a short dated log of what was done (`PROGRESS.md`).

## 7. First tasks
1. Propose a folder layout for the new workstream (see `README.md`).
2. Design the question schema.
3. Write the first 20 questions resolving January–May 2027, so collection can start in December 2026.
4. Explain how to call an LLM API and save a date-stamped answer; the user writes the runner.
5. Explain the Brier score; the user writes the scorer.
6. Update `PROGRESS.md` with this direction change.
