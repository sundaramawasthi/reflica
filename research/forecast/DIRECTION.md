# Research direction: Reflica → AI forecasting of Indian events

First recorded: 13 October 2026. Updated: 14 October 2026.
Status: proposed research roadmap; **M.Tech guide approval is pending**.

## 1. What changed and why

The M.Tech research moves from Reflica plan revision (revising a plan graph correctly when a fact changes) to **predictive AI**: agent-based forecasting of important Indian events.

Why: the user wants to become a researcher in predictive AI. A literature review of 21 recent papers (2024–2027, including 6 IEEE Q1 journal papers) suggested open space in AI event forecasting, especially for India. These gaps must still be verified against the full papers and the wider forecasting literature (see section 10).

## 2. Overall vision

Evolve the existing Reflica platform into an AI forecasting platform for important Indian events. The long-term goal is a website where students, researchers, companies, banks and government officers can:

- See forecasts of important Indian events.
- See the probability of each event.
- Understand the evidence and reasons behind a forecast.
- Track whether predictions were correct.
- Ask an AI forecasting agent their own questions.
- Explore possible consequences of predicted events through a cause-and-effect graph.

Research area:
- Area: Artificial Intelligence
- Subfield: Machine Learning and Predictive AI
- Specific area: Agent-based event forecasting
- Initial domain: Indian economy, climate, critical infrastructure. Selected geopolitical events are a later extension, because they are harder to resolve objectively.

The goal is not just a website. Each project must have a research question, an experiment, measurable results and a defensible contribution.

**One platform, three modules.** Each academic project adds a module to the same Reflica platform.

## 3. What happens to the existing Reflica work

- **Reflica already exists. It is not rebuilt from scratch.** It is the foundation.
- **Keep everything.** Do not delete the Flutter app, authentication, Firebase integration, the benchmark (v0.2.0, 63 scenarios, Categories 1–7), baselines B3, B4a, B4b, or B5 v0.1.0.
- **Old plan-revision research is paused** unless the user explicitly asks to resume it.
- The Reflica graph engine may be reused in the final project for impact analysis. The Category 7 "unknown" idea is the starting point for the abstention rule. Neither is assumed to work for forecasting without testing (see section 7).

### Current foundation (checked in the repository on 14 October 2026)

- `main`: Flutter app (Chrome + Android). Firebase products in `pubspec.yaml`: `firebase_core`, `firebase_auth` (+ `google_sign_in` on Android), `cloud_firestore` (offline persistence on), `firebase_analytics`, `firebase_ai`. Firestore collections used in `lib/`: `users`, `plans`, `notifications`.
- `main`: Python research workspace `research/reflica_bench/` (benchmark, ground truth, baselines, B5, tests).
- Branch `reflica/stage-1-flutter-integration` (not merged into `main`): adds `research/reflica_service/`, an optional FastAPI HTTP API (`service` extra) bound to localhost, with LLM extraction, a `graph@1` contract and `graph/impact.py`, plus Flutter screens that call it. This is the most likely place for a forecasting backend. Decide how this branch relates to `main` before building on it.

## 4. Minor Project 1: India Forecast Benchmark and Forecast Dashboard

Estimated period: January–May 2027 (subject to GLA rules). **Question collection starts December 2026.**

**Research question.** How accurately and reliably do large language models forecast unresolved Indian economic, climate and infrastructure events? Does giving them current, authoritative Indian information improve their forecasts? Do they perform differently on Indian events than on comparable Western events?

### A. Forecast question catalogue
A page listing objectively verifiable questions about future events. Examples:
- Will India's CPI inflation for a specified month exceed a defined threshold?
- Will a specified region have a defined extreme-weather event in a specified period?
- Will an officially reported electricity shortage exceed a threshold in a given period?

Each question has: unique ID; clear wording; category; topic; creation timestamp; forecast deadline; resolution deadline; official resolution source; unambiguous resolution rule; status and final outcome. Avoid vague questions such as "Will the Indian economy perform well?".

### B. Indian vs Western comparison (addition 1)
- Add a small, carefully selected set of **Western questions** alongside the Indian ones (or reuse ForecastBench-style questions).
- Match the two sets as far as possible: comparable topic (e.g. India CPI ↔ US CPI, RBI ↔ US Federal Reserve), difficulty, forecast horizon, deadlines and resolution criteria. Link matched questions with a pair ID.
- Report sample sizes, uncertainty and limitations. **Do not claim an India-specific performance gap unless the results support it.**
- Geopolitics stays a later extension.

### C. Question collection timeline (addition 3)
- Start building and reviewing the catalogue in **December 2026**, because questions take weeks or months to resolve.
- For every question record: where it came from, topic, resolution criteria, resolution source, forecast deadline and final resolution date.
- **The forecast deadline must be earlier than the resolution date.**
- Prefer questions that resolve by **May 2027** for the initial Minor 1 evaluation.
- **Never change a question's criteria after seeing model predictions or the outcome.** A correction creates a new question ID and keeps the old one with a note.

### D. Forecast generation
For each question, request forecasts from three or four AI models (subject to budget and API availability). Compare where possible:
- the model without live news retrieval;
- the same model with current, relevant evidence;
- simple baselines: historical base rate and persistence ("same as last time").

Each forecast records: model and version; settings; forecast timestamp; probability; short explanation; evidence and source URLs where applicable; experimental condition (search on/off); prompt/configuration version; token usage, cost and runtime; error or failure status.

Save the prediction before the outcome is known. **Never overwrite a prediction**; later forecasts are separate, timestamped records.

### E. API budget and cost control (addition 4)
- Set a **monthly API budget** and estimate the cost of each experiment before running it.
- Prefer free or low-cost models and open models where practical. **Open models are not free to run**: include compute or hosting costs.
- **Cache model outputs** and do not repeat identical calls without a reason (a repeat run for variance is a planned, recorded condition, not an accident).
- Record model version, settings, token usage, cost, failures and runtime for every call.
- **Estimate the full cost before expanding** from the 20-question pilot to 200–300 questions.

### F. Forecast history and scoreboard
The Flutter app shows: upcoming questions; predictions from each model; timestamps; explanations and source links; resolved outcomes; model performance and leaderboard; historical records.
Do not show an unearned "accuracy" for unresolved questions. Clearly separate preliminary results from scores on resolved outcomes.

### G. Resolution and scoring
When the official result is available, resolve the question with its predefined rule and record the outcome, the source and the resolution timestamp. Calculate:
- Brier score: for a binary question, (forecast probability − outcome)², with outcome 0 or 1. Lower is better.
- Calibration, interpreted with uncertainty when the sample is small.
- Resolution rate and unresolved counts.
- Performance against baselines.
- Indian vs Western results.
- Cost and failure rate.

### Scope control
Start with a **pilot of 20 carefully specified questions** and test the whole workflow before expanding towards 200–300. Minor 1 does not need a free-form chatbot.

**Proposed contribution.** An openly documented, prospective benchmark of AI forecasting on Indian events, with timestamped predictions, an Indian vs Western comparison and reproducible evaluation. The website is the working product; the benchmark design and empirical findings are the research contribution. Do not claim that India-specific forecasting or calibration is unexplored without verifying the literature first.

## 5. Minor Project 2: Interactive, evidence-grounded forecasting agent

Estimated period: July–December 2027 (subject to GLA rules).

**Research question.** Can an evidence-grounded forecasting agent with calibrated probabilities and a tested abstention rule reduce confident forecasting errors while keeping useful coverage?

### A. Ask the Forecaster
A new screen in the existing app. The agent:
1. Checks whether the question is specific and forecastable.
2. Identifies the time period and event definition.
3. Searches appropriate current sources when retrieval is available.
4. Evaluates evidence quality, freshness and consistency.
5. Gives a probability when the evidence supports one.
6. Explains the main reasons and cites the evidence.
7. Says "insufficient evidence" or abstains when appropriate.
8. Saves the question, forecast, timestamp, evidence references and configuration.

It must not fabricate sources or call a probability calibrated just because it is a percentage.

### B. Honest probability estimation
Compare: plain LLM forecast; forecast with retrieved evidence; aggregation of several forecasts; calibration on previously resolved predictions (when enough data exists); abstention based on evidence quality, model uncertainty or validation results. Agreement between models or runs does not guarantee correctness.

### C. Calibration data from Minor 1 (addition 5)
- Use suitable **resolved forecasts from Minor 1** as calibration and evaluation data for Minor 2. This links the two projects.
- Aim for **a few hundred resolved forecasts** if feasible. The amount needed depends on how balanced the outcomes are and how good the forecasts are; report it honestly if there is too little.
- **Separate development data from held-out evaluation data** (for example by time period). Choose the abstention threshold and calibration settings on development data only, then test once on the held-out data.
- Prevent leakage from future news, outcomes or anything unavailable at forecast time.
- Report calibration, Brier score, coverage, and performance when the agent abstains.

### D. Abstention and evaluation
Measure Brier score on answered questions, calibration, false-confidence rate, coverage and the risk–coverage trade-off. Compare against baselines on a reproducible test set and continue prospective testing where possible.

**Proposed contribution.** An experimentally evaluated approach to evidence-grounded, uncertainty-aware forecasting of Indian events, supported by results showing whether it improves forecast quality or reduces false confidence. Do not assume it beats the baselines.

## 6. Final project: Impact-aware forecasting

Estimated period: final project period (GLA rules).

**Research question.** Does an explicit cause-and-effect model for estimating downstream consequences of forecast events predict those consequences better than asking an LLM directly?

Example: elevated chance of extreme heat → electricity demand → supply shortage → water-pumping disruption → effects on hospitals and industry. These are hypotheses about dependencies, not guaranteed outcomes. The system must represent uncertainty and relevant conditions (available generation, water storage, local infrastructure, mitigation).

### A. Interactive impact map
Reuse the Reflica mind-map / graph interface where practical. Show the initial forecast and probability; downstream nodes; the relationship on each edge; evidence for each relationship; conditional probabilities or uncertainty ranges where adequately estimated; assumptions and missing information; observed outcomes once resolved.

## 7. Reusing the Reflica engine (final project)

Evaluate whether the existing graph propagation, ground truth, constraint reasoning and related components can support impact analysis. **Do not assume the old engine can propagate probabilities**: it was built for deterministic plan revision. Assess it against the mathematical and causal requirements of forecasting. Where needed, build and test a **separate probabilistic propagation layer** instead of forcing the old engine. Reviewers will ask why not a Bayesian network; have an answer.

**Scientific evaluation.** Compare at least: (1) direct LLM prediction of effects; (2) a baseline without the explicit graph; (3) the graph-based approach using Reflica components, if technically appropriate. Use predefined outcomes, probability scores, calibration and task-specific metrics. The main challenges are reliable labels for downstream effects and not treating a time sequence as proof of causation.

**Proposed contribution.** A tested method combining event forecasts with explicit dependency reasoning, showing when graph propagation helps, when it fails, and how uncertainty changes along the graph.

## 8. Research outputs (addition 2)

These are research goals, not guaranteed publications.

| Project | Target output | Content |
|---|---|---|
| Minor 1 | Conference Paper 1 + open benchmark v1 | Benchmark design, Indian vs Western comparison, empirical findings |
| Minor 2 | Conference Paper 2 + open agent | Honest forecasting agent: calibration, evidence retrieval, abstention |
| Final project | Final research paper + M.Tech thesis | Impact-aware forecasting and downstream consequence analysis |

## 9. Shared platform and architecture

**Frontend.** Reuse the existing Flutter app and components. Additions: forecast catalogue and details; history and leaderboard; Ask the Forecaster; evidence viewer; impact map. No rebuild in React/Next.js unless there is a demonstrated need and the user approves.

**Firebase.** Inspect and reuse the existing setup (authentication, Firestore, offline persistence). Design forecasting data around the current architecture. Do not duplicate users or replace working sign-in or storage. The frontend must never hold privileged LLM API keys.

**Forecasting backend.** Choose after checking the existing project. A Python service may fit (model calls, scoring, scheduled jobs, graph reasoning); FastAPI is a candidate, not a decision (one already exists on the stage-1 branch). Keep separate: question management; forecast generation; evidence retrieval; immutable forecast history; resolution and scoring; impact analysis. If a separate service is used, explain how it authenticates, talks to Firebase and protects secrets.

**Automated jobs (later).** Scheduled forecasts; resolution checks; recording outcomes; leaderboard recalculation; failure logging and safe retries. Jobs must never silently replace predictions or change historical scores without an auditable correction record.

## 10. Research integrity rules

1. Preserve all historical forecasts and their original timestamps.
2. Store probabilities before resolution.
3. Define outcome sources and resolution rules in advance.
4. Prevent future information leaking into forecasts.
5. Use clear train, calibration, development and evaluation periods.
6. Report sample sizes and uncertainty with every score.
7. Compare against meaningful baselines.
8. Separate correlation, prediction and causal claims.
9. Verify every claimed literature gap against the actual paper, not its abstract or a summary.
10. Report negative results honestly.
11. Keep the product roadmap separate from the evidence for research claims.

### Literature gaps to verify (from the 21-paper review)
1. Forecast probabilities rarely calibrated or checked.
2. No abstention ("I don't know") in forecasting systems.
3. Little prospective (live) testing; leakage risk on historical data. ForecastBench is the main exception.
4. Cause chains extracted from past text but not used forward.
5. India largely missing (one paper, Indian stock indices).

Papers to read before claiming any of these: Halawi et al. 2024 "Approaching Human-Level Forecasting with Language Models"; Autocast (Zou et al. 2022); ForecastQA (Jin et al. 2021); "Wisdom of the Silicon Crowd" (Schoenegger et al. 2024); "Pitfalls in Evaluating Language Model Forecasters" (Paleka et al. 2025); "Know Your Limits" abstention survey (Wen et al. 2024); Bayesian-network work for gap 4.

Key papers from the review to read first: LLM-based Agents for Forecasting and Prediction (survey, arXiv 2608.23058); ForecastBench (ICLR 2025); From News to Forecast (NeurIPS 2024); Application of LLMs in the Problem of Event Forecasting (2025); Hierarchical Semantic Extraction and Heterogeneous GNNs for Event-Driven Time Series Forecasting (Scientific Reports 2026); LLM Framework for Predicting Significant Equity Index Fluctuations (NIFTY, 2026). Full analysis: https://claude.ai/artifact/B61G9cki25mLr8aRaSXK81 and the user's `LITERATURE_FORECASTING.md` (not in this repo).

## 11. How to work in this repository

1. Inspect the repository before proposing changes; read this file, `PROGRESS.md` and any architecture docs.
2. Check the actual Firebase products, collections, auth flow, data models and configuration; do not assume.
3. Preserve the Reflica app, authentication, Firebase integration and research work. Do not delete or needlessly rewrite working features.
4. Add forecasting features incrementally, reusing Flutter screens and components.
5. Never put Firebase credentials, service-account keys or API keys in client code or public repositories.
6. No destructive database migrations or major architecture changes without explaining the impact and getting approval.
7. **The user writes the code.** Claude explains step by step, reviews, debugs and checks scientific validity; it does not generate whole modules unless asked.
8. The repository and its tests are the source of truth for status. Keep a short dated log in `PROGRESS.md`.
9. Messages are often voice-typed; answer in short, simple English.

## 12. Immediate tasks (in order)

1. Inspect the repository and report the real state of the Flutter app, Firebase, Python code, tests and docs.
2. Identify which Reflica components can be reused directly and which need adaptation.
3. Propose a minimal integration architecture and folder layout.
4. Propose question and forecast schemas, including immutable history and resolution records in the existing Firebase setup.
5. Explain proposed changes before implementing them.
6. After approval, help the user build the 20-question pilot (collection from December 2026) and a minimal forecast dashboard.
7. Keep the progress log and docs updated as real work is completed.
