# Research direction: Reflica → AI forecasting of Indian events

First recorded: 13 October 2026. Updated: 14 October 2026 (Minor 1 rewritten; platform evolution added). Moved from `research/forecast/DIRECTION.md`.
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

### Platform evolution (added 14 October 2026)

Reflica's **primary product direction** changes from goal/plan management to an AI forecasting and research platform, starting with Indian events. This is an evolution of the existing app, not a new one. Users will be able to: explore upcoming Indian events; view clearly defined Yes/No questions; see probability forecasts from several AI models; read the evidence and sources; track predictions over time without historical records changing; check outcomes after resolution; compare models with Brier scores, calibration and baselines; and explore research comparisons (Indian vs Western, with vs without news).

Old plan features are **hidden from the main navigation, not deleted**. Nothing is removed without approval. The repository audit and the feature-by-feature table are in `research/forecast/AUDIT.md`.

**Implementation phases** (one at a time; the user writes the code with Claude's guidance and review):
1. Audit and plan (no app code changes).
2. Homepage and navigation for forecasting (app stays buildable; old routes kept).
3. Question catalogue (data model + UI: sources, resolution rules, deadlines).
4. Immutable, timestamped forecast records + a safe server-side point for model calls.
5. Evaluation: outcomes, scoring, model comparison, scoreboard from real resolved data only.
6. Advanced research: question generator, news-retrieval experiments, historical evaluation, Indian vs Western, as separate tested components.

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

**Goal.** Not an app that asks AI questions, but the first scientific foundation of the long-term vision. The platform is the tool; the experiments are the research; the findings are what make the work valuable to other researchers.

**Central research question.** How reliably can AI forecast future events in India, what information improves its predictions, and where does it fail?

### The research pipeline

| Step | What happens |
|---|---|
| 1. Find questions | Collect upcoming Indian events and official data. |
| 2. Validate | Every question has a clear outcome, deadline and resolution rule. |
| 3. Forecast | Ask several LLMs for probabilities, with controlled information access. |
| 4. Freeze | Save timestamped probabilities, evidence and model details. Never overwrite. |
| 5. Resolve | Check what happened against the official source named in advance. |
| 6. Evaluate | Score predictions; compare models, news conditions and baselines. |
| 7. Publish | Dashboard, analysis and the paper. |

**Most important practical rule:** get **one question working end to end** (generate → validate → forecast → freeze → resolve → score) before scaling up. Do not build a giant platform first.

### Part 1. Automatic question generation

A program reads structured data from official sources and turns it into **candidate** forecast questions.

- **Economy (RBI, MOSPI):** monetary-policy decisions and indicators such as CPI inflation; "will indicator X cross threshold T in the next period?".
- **Climate (IMD):** defined rainfall, temperature and monsoon thresholds.
- **Infrastructure (Grid-India, CWC):** electricity demand, power shortage, reservoir levels, only where reliable data and resolution rules exist.

Example: the last inflation value was 4.8% → template → "Will the indicator exceed 5% in the next reporting period?". The generator records indicator, units, period, threshold, data source, forecast deadline and resolution rule.

The generator **does not trust its own output.** Every candidate is checked for ambiguity, duplicates, triviality (too easy) and resolvability before it enters the benchmark.

ForecastBench already shows that automatic questions from time-series data can support a dynamic benchmark. This project must show what an **India-focused** version adds, not reproduce it.

### Part 2. Benchmark design

A standardized test: questions from selected Indian domains plus a **smaller, comparable Western set**.

| Field | Example |
|---|---|
| Question | Will indicator X exceed 5%? |
| Geography | India / Western |
| Category | Economy / Climate / Infrastructure |
| Source of the question | data record or event it came from |
| Forecast deadline | specified date and time |
| Resolution date | when the official result becomes available |
| Resolution source | named official publication |
| Resolution rule | written in advance, unambiguous |
| Outcome | Yes = 1, No = 0, or unresolved/invalid |
| Difficulty / horizon | recorded using predefined rules |
| Pair ID | links a matched Indian and Western question |

The forecast deadline must be **earlier** than the resolution date.

**Scope.** Pilot of **20 questions** to test the whole pipeline; then expand towards 200–300 as time, budget and the supply of useful questions allow. **1,000 generated questions are not automatically better than 200 good ones**: questions must be meaningful, varied and independently informative.

**Collection timeline.** Start building and reviewing the catalogue in **December 2026**; prefer questions that resolve by **May 2027**. **Never change a question's criteria after seeing predictions or the outcome**; a correction creates a new question ID and the old one is kept with a note.

### Part 3. Forecasting with the LLMs

- **Start with 2–3 accessible models**; expand to 3–4 only if the budget allows. (This is the agreed number for all documents.)
- Each model returns a **probability**, not "yes, probably".
- Two information conditions, everything else kept the same (model version, question, prompt structure, settings):
  - **Condition A, no retrieved news:** question + its specified baseline information.
  - **Condition B, retrieved news:** the same, plus relevant news **published before the forecast deadline**. Record the exact sources given and the retrieval time.

### Part 4. Permanent forecast records

Every forecast stores: question ID; model and version; probability; forecast timestamp; forecast deadline; prompt version and information condition; evidence references with their publication dates; settings; token usage, cost, runtime; failure status.

Once submitted, a forecast is **never silently replaced**. An update is a **new version** with a new timestamp; the old one stays available for evaluation. The existing Reflica Flutter app and Firebase provide the UI and storage foundation; inspect the repository before deciding which collections and components to reuse.

### Part 5. Resolving questions

When the resolution condition is met, a result checker (a human reviewer at first) verifies the answer from the source defined in advance. Example: "Did the policy rate increase at the named meeting?" → official RBI policy statement → Yes/No → link and date.

If the source is unavailable or the result is genuinely ambiguous, mark the question **unresolved or invalid** by a predefined rule. Never force an answer to grow the sample.

### Part 6. Scientific evaluation

**A. Brier score.** For a binary question, BS = (p − o)², where p is the probability of Yes and o is 1 if Yes happened, 0 if No. A lower average is better.

**B. Calibration.** If a model says about 70% for a group of similar events, about 70% of them should happen. Calibration needs many resolved forecasts; always report the number resolved and the uncertainty.

**C. Baselines.** A complex model is not valuable if a simple one does as well.
- Historical **base rate** and **persistence** ("same as last time").
- **Official Indian forecasts (addition):** compare the AI with **RBI's own inflation projections** (published in the monetary-policy statements) and **IMD's own forecasts** (e.g. monsoon long-range and extended-range forecasts). Official forecasts are often a point value or a range rather than a probability, so the rule for turning each into a forecast for a question must be **written before** the questions resolve (IMD's categorical monsoon forecasts already give probabilities). If the AI cannot beat India's official forecasters, that is an important finding; if it can, that is stronger still.

**D. Research comparisons.**
1. **Does news help?** Each model with vs without timely retrieved news.
2. **India gap?** Indian vs Western questions matched on category, difficulty and horizon. A difference is a finding only if the evidence supports it.
3. **Historical vs prospective.** Historical questions test the pipeline and probe possible training-data contamination. Compare them cautiously with live forecasts: a difference alone does **not** prove memorisation. Historical results are reported separately and never mixed into the prospective benchmark scores.

**E. Optional extra experiments (only if time allows; they would strengthen the India-specific contribution):**
- **Human vs AI:** GLA students forecast the same questions before the same deadlines. Needs informed consent, and GLA ethics approval if the university requires it; record each participant's forecast time the same way as the models'.
- **Hindi/regional vs English news:** in Condition B, give the same model news in Hindi (or another Indian language) vs English for the same questions and deadlines, with the amount of evidence matched as closely as possible.

For every comparison report sample sizes, uncertainty, costs and failures. A well-designed experiment that shows no improvement is still a useful result.

### Part 7. Dashboard inside Reflica

Four views: **Question bank** (questions and deadlines), **Forecasts** (probabilities and evidence), **History** (immutable records), **Scoreboard** (resolved forecasts and metrics). The app clearly separates: forecasts still unknown; resolved forecasts that can be scored; questions invalidated or unresolvable. No "accuracy" is shown for unresolved questions.

Use Firebase for what it already does well; add a secure model-calling service only if the architecture requires one. API keys never go in the Flutter client.

### Part 8. API budget and cost control

- Set a **monthly API budget** and estimate the cost of each experiment before running it.
- Prefer free or low-cost models and open models where practical. **Open models are not free to run**: include compute or hosting costs.
- **Cache model outputs**; do not repeat identical calls without reason (a repeat run for variance is a planned, recorded condition).
- Record model version, settings, token usage, cost, failures and runtime for every call.
- **Estimate the full cost before expanding** beyond the 20-question pilot.

### Part 9. From results to a paper (Conference Paper 1)

The manuscript explains: (1) the research gap from the literature review; (2) how questions are generated, validated and resolved; (3) models, information conditions and baselines; (4) how forecasts were stored and leakage prevented; (5) what the metrics show, with uncertainty and limitations; (6) what worked, what failed, and what future work should do.

ForecastBench (ICLR 2025) is the key precedent: a dynamic benchmark of 1,000 questions comparing LLMs with human forecasters. The novelty here must be **demonstrably different**: for example the quality of the India-focused question pipeline, a well-controlled local-information experiment, comparison with official Indian forecasters, or findings existing benchmarks do not already establish. Publication is an aspiration, not a guaranteed outcome.

### Roadmap

| Period | Main target |
|---|---|
| October–November 2026 | Read the core literature, refine the research questions, inspect the Reflica repository. |
| December 2026 | Start question collection and validation; first 20-question pilot; forecast logging. |
| January–March 2027 | Expand the benchmark; run controlled model/news experiments. |
| April–May 2027 | Resolve available questions, analyse results, document limitations, prepare the report. |

Working targets, subject to GLA requirements and the real resolution dates of events.

**Proposed contribution.** An openly documented, prospective benchmark of AI forecasting on Indian events, with timestamped predictions, controlled news and India-vs-West comparisons, official-forecast baselines and reproducible evaluation. Do not claim that India-specific forecasting or calibration is unexplored without verifying the literature first.

### How Minor 1 fits the long-term vision

1. **Minor 1, measure the future:** which forecasts deserve trust, what evidence helps, where AI fails.
2. **Minor 2, improve the forecaster:** an agent that researches, gives calibrated probabilities and abstains when evidence is weak.
3. **Final project, understand the consequences:** how a forecast event affects other events and sectors. The Reflica graph engine may help with dependency reasoning, but probability propagation needs separate validation.

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
| Minor 1 | Conference Paper 1 + open benchmark v1 | Benchmark design, news vs no-news and Indian vs Western comparisons, official-forecast baselines, empirical findings |
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
6. After approval, help the user get **one question working end to end**, then the 20-question pilot (collection from December 2026) and a minimal forecast dashboard.
7. Keep the progress log and docs updated as real work is completed.
