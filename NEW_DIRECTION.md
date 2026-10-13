# Research Direction: Reflica → AI Forecasting of Indian Events

**Date:** 14 October 2026 (replaces the 13 October version)
**Status:** Final decision by the user (13 October 2026). M.Tech guide approval is pending.
**Written for:** Claude Code working in the Reflica repositories (Flutter app and Python research code).

> **[Addition, 14 Oct 2026, not in the user's text]**
> - **Approval status:** this is the student's chosen direction. **Formal M.Tech guide approval is pending** until the guide confirms it.
> - **Implementation order (user decision):** **Documentation → Flutter UI → Python backend → connect the UI to real data.** Exception: the December 2026 pilot is recorded **by hand** following `research/forecast/PILOT_PROTOCOL.md`, so the Minor 1 timeline is protected. Section 9's tasks are read in this order. They are not permission to start backend code now.
> - **Recorded decisions D1–D9** (leaderboard selection, baselines, models, Western set, forecast IDs, timestamps, code location, late forecasts): `research/forecast/PILOT_PROTOCOL.md` section 0.
> - **Related documents:** `research/forecast/MINOR1_DESIGN.md` (detailed Minor 1 design) · `research/forecast/PILOT_PROTOCOL.md` (record formats) · `docs/UI_SPEC.md` · `docs/ARCHITECTURE.md` · `research/forecast/MILESTONE_1.md` (backend milestone) · `research/forecast/LITERATURE_FORECASTING.md` · `research/forecast/AUDIT.md` (snapshot) · `PROGRESS.md`.
> - This file is the authoritative high-level direction. If another document disagrees, this file wins until it is updated.

## 1. Overall vision

I want to evolve my existing Reflica platform into an AI forecasting platform focused on important Indian events.

The long-term goal is a website where students, researchers, companies, banks, and government officers can:

- See forecasts of important Indian events.
- View the probability of each event happening.
- Understand the evidence and reasons behind a forecast.
- Track whether predictions were correct.
- Ask an AI forecasting agent their own questions.
- Explore the possible consequences of predicted events through a cause-and-effect graph.

The research area is:

- **Area:** Artificial Intelligence
- **Subfield:** Machine Learning and Predictive AI
- **Specific area:** Agent-based event forecasting
- **Initial domain:** Indian economy, climate, critical infrastructure, and selected geopolitical events (geopolitics added later, once objective resolution rules are clear).

The goal is not merely to create a website. Each project must contain a research question, an experiment, measurable results, and a defensible contribution. Each project also produces one paper (see section 7).

## 2. Important instruction: reuse the existing Reflica platform

Reflica already exists. It is not a new project to create from scratch.

The existing Flutter application runs on Chrome and Android. It already includes Google sign-in, Firebase integration, offline storage, a seven-input plan wizard, a mind-map view, a plan editor, and notifications.

The Python research repository also contains the Reflica benchmark, ground truth, reasoning baselines, tests, and graph-related research code.

### Rules for working in the repository

1. Inspect the current repository before proposing changes.
2. Read `NEW_DIRECTION.md`, the progress notes, and the existing architecture documentation if available.
3. Identify the existing Firebase products, collections, authentication flow, data models, and configuration. Do not assume which Firebase services are used without checking.
4. Preserve the existing Reflica application, authentication, Firebase integration, and research work.
5. Do not delete, replace, or unnecessarily rewrite working features.
6. Keep Reflica's old plan-revision research paused unless I explicitly ask to resume it.
7. Add forecasting features incrementally, reusing existing Flutter screens and components where appropriate.
8. Do not expose Firebase credentials, service-account keys, API keys, or other secrets in client code or public repositories.
9. Do not run destructive database migrations or make major architectural changes without explaining the impact and receiving my approval.
10. I want to write the code myself. Explain the implementation step by step, let me write it, and then review and debug my work. Do not generate entire modules unless I explicitly request that.

Before changing anything, propose a repository structure and an incremental integration plan. Wait for my approval before making major changes.

## 3. Minor Project 1: India Forecast Benchmark and Forecast Dashboard

**Estimated period:** January–May 2027, subject to university requirements. **Question collection starts in December 2026** (see Scope control).

### Purpose

Build the first working forecasting module inside the existing Reflica platform.

This project must do more than compare AI models. It must actually generate forecasts, save them, display them, and track their outcomes.

### Research question

How accurately and reliably do large language models forecast unresolved Indian economic, climate, and infrastructure events? Does providing current, authoritative Indian information improve their forecasts? Do the same models forecast Indian events worse than comparable Western events?

### Features to build

**A. Forecast question catalogue**

Create a page listing objectively verifiable questions about future events in India.

Example questions:

- Will India's CPI inflation for a specified month exceed a defined threshold?
- Will a specified region experience a defined extreme-weather event during a specified period?
- Will an officially reported electricity shortage exceed a specified threshold during a given period?

Each question must have:
- A unique ID.
- Clearly worded question.
- Event category.
- Region tag: India (main set) or Western (small comparison set).
- Creation timestamp.
- Forecast deadline (always before the resolution date).
- Resolution deadline.
- Official resolution source.
- Unambiguous resolution rule.
- Resolution status and final outcome.

Avoid vague questions such as "Will the Indian economy perform well?"

**Western comparison set.** Add a small, carefully selected set of objectively resolvable Western questions (for example US or EU inflation and central-bank decisions in the same months), so the study can test whether models perform worse on Indian events. Match the two sets as closely as possible on topic, difficulty, forecast horizon, deadlines and resolution criteria, and keep the question format identical. Report sample sizes, uncertainty and limitations for the comparison. Do not claim an India-specific performance gap unless the results support it.

**A2. Automatic question generator (upgrade, added 14 Oct 2026)**

Build a program that creates questions automatically, so the catalogue can grow to 1,000+ questions and refresh every month.
- Main source: official data feeds and pages with scheduled releases (RBI policy and DBIE, MOSPI CPI/IIP, IMD forecasts and warnings, Grid-India daily reports, CWC reservoir bulletins). Turn each scheduled release into a question with a template, for example "Will [indicator] for [period] be above [threshold]?"
- Secondary source: news headlines about upcoming scheduled events (policy meetings, data releases), converted into questions only when an official resolution source exists.
- Every generated question must pass the same checks as hand-written ones (clear rule, official source, forecast deadline before resolution date). Review a sample by hand and report the rejection rate.
- Respect each website's terms and robots.txt; prefer official APIs or downloadable files; store the source URL and fetch time.

> **[Addition, 14 Oct 2026, not in the user's text]** Size is not the goal by itself: 1,000 generated questions are not automatically better than 200 good ones (see `research/forecast/MINOR1_DESIGN.md`).

**A3. Past-question study (upgrade, added 14 Oct 2026)**

Also create questions about events that have already happened, so models can be tested instantly while live questions wait to resolve.
- Use these for three things: (1) testing the whole pipeline end to end, (2) development data, and (3) a **leakage study**: compare model scores on past questions (answers the model may already know from training) with scores on future questions.
- Record each model's stated knowledge cutoff and split past questions into "before cutoff" and "after cutoff".
- When giving news to the model for a past question, give only news published before that question's forecast date.
- Past-question results must never be reported as the main forecasting performance. The prospective (future) questions remain the main evaluation.

> **[Addition, 14 Oct 2026, not in the user's text]** A2 and A3 are upgrades **within** Minor Project 1, not separate projects. A3's past questions serve pipeline testing, development and the leakage study; prospective questions remain the primary evaluation. A past-vs-future score difference does not by itself prove memorisation.

**B. Forecast generation**

For each question, the system should request forecasts from three or four selected AI models, subject to budget and API availability.

> **[Addition, 14 Oct 2026, not in the user's text]** Decision D4: the 20-question pilot **starts with 2–3 models**; API costs are estimated before expanding.

Where possible, compare:
- Model without live news retrieval.
- The same model with current, relevant evidence.
- Simple baselines such as a historical base rate or persistence.

> **[Addition, 14 Oct 2026, not in the user's text]** Baseline decisions: every baseline's calculation rule is documented and fixed in advance; persistence gets no arbitrary probability and is validated before use (D2); the official-forecast baseline (RBI/IMD) is **deferred** from the initial pilot unless a defensible conversion to a probability is established (D3). Primary leaderboard = latest eligible on-time forecast per model and condition; late forecasts are kept, marked late, and excluded from on-time evaluation (D1, D9).

Each forecast should record:
- Model and version.
- Forecast timestamp.
- Probability of the event.
- Short explanation.
- Supporting evidence and source URLs, where applicable.
- Experimental condition, such as search enabled or disabled.
- Prompt/configuration version.
- Error or failure status.

Save the prediction before the outcome becomes known. Never overwrite an earlier prediction; subsequent forecasts must be separate, timestamped records.

**API budget and cost control.** Calling several models, with and without retrieval, on hundreds of questions costs money.
- Set a monthly API budget and an estimated cost per experiment.
- Prefer free or low-cost models and open models where practical. Open models are not automatically free: include compute or hosting costs.
- Cache model outputs and avoid repeating identical calls.
- Record model version, settings, token usage, cost, failures and runtime for every run.
- Estimate the total cost before expanding from the 20-question pilot to 200–300 questions.

**C. Forecast history and scoreboard**

The Flutter application should display:
- Upcoming forecast questions.
- Predictions from each model.
- Forecast timestamps.
- Explanations and source links.
- Resolved outcomes.
- Model performance and leaderboard.
- Historical forecast records.

Do not show an unearned "accuracy" score for unresolved questions. Clearly distinguish preliminary results from scores based on resolved outcomes.

**D. Resolution and scoring**

When an event's official result becomes available, resolve the question using its predefined rule and record the outcome with the source and resolution timestamp.

Calculate:
- Brier score for probabilistic predictions.
- Calibration, with uncertainty-aware interpretation when the sample is small.
- Resolution rate and unresolved-question counts.
- Performance against baseline forecasts.
- Indian vs Western performance.
- Cost and failure rate, where practical.

For binary questions, the Brier score is the squared difference between the forecast probability and the final outcome coded as zero or one. Lower scores are better.

### Proposed research contribution

An openly documented, automatically updated, prospective benchmark of AI forecasting on Indian events, with timestamped predictions, a Western comparison set, a past-vs-future leakage study, and reproducible evaluation.

The website is the working product; the benchmark design and empirical findings form the research contribution.

Do not claim that India-specific forecasting or calibration is entirely unexplored without verifying the literature first.

### Scope control

Start with a pilot of 20 carefully specified questions. Test the complete workflow before expanding towards 200–300 questions.

Questions take weeks or months to resolve. Begin building and reviewing the question catalogue in December 2026:
- For every question, record its source, topic, resolution criteria, resolution source, forecast deadline and final resolution date.
- The forecast deadline must be earlier than the resolution date.
- Prefer questions that resolve by May 2027 for the initial Minor 1 evaluation.
- Never change a question's criteria after seeing model predictions or the outcome.

Minor Project 1 does not need a free-form forecasting chatbot. Its primary focus is the curated catalogue, forecast generation, history, scoring, and scoreboard.

### Output

Working Module 1 in the Reflica app + open benchmark v1 + **Conference paper 1** (benchmark design and findings).

## 4. Minor Project 2: Interactive and Evidence-Grounded Forecasting Agent

**Estimated period:** July–December 2027, subject to university requirements.

### Purpose

Extend the working forecasting module so a user can ask a new question in natural language and receive a transparent, evidence-grounded probabilistic forecast.

### Research question

Can an evidence-grounded forecasting agent with calibrated probabilities and a tested abstention rule reduce confident forecasting errors while retaining useful coverage?

### Features to build

**A. Ask the Forecaster**

Add a screen to the existing application where users can ask questions such as:

"Is there a high chance of electricity demand exceeding available supply in this region next week?"

The agent should:
1. Check whether the question is specific and forecastable.
2. Identify the relevant time period and event definition.
3. Search appropriate current sources when retrieval is available.
4. Evaluate the quality, freshness, and consistency of the evidence.
5. Produce a probability when the available evidence supports one.
6. Explain the main reasons and cite the evidence used.
7. Say "insufficient evidence" or abstain when appropriate.
8. Save the question, forecast, timestamp, evidence references, and configuration for later evaluation.

The system must not fabricate sources or claim that a probability is calibrated merely because it provides a percentage.

**B. Honest probability estimation**

Investigate and compare appropriate methods for probability estimation and calibration.

Potential methods include:
- A plain LLM forecast.
- Forecasting with retrieved evidence.
- Aggregation of multiple forecasts.
- Calibration using previously resolved predictions, where enough data is available.
- An abstention rule based on evidence quality, model uncertainty, or validation results.

Do not assume that agreement between models or multiple runs guarantees correctness.

**Calibration data.** Use suitable resolved forecasts collected during Minor Project 1 as calibration and evaluation data for Minor Project 2.
- Aim for a few hundred resolved forecasts if feasible; the amount needed depends on event balance and forecast quality.
- Separate development data from held-out evaluation data.
- Prevent leakage from future news, outcomes, or any information unavailable at forecast time.
- If too few forecasts have resolved, report that limitation and use simpler methods.

**C. Abstention**

When the system lacks sufficient evidence, it should be able to decline to issue a confident forecast.

Measure:
- Brier score on answered questions.
- Calibration.
- False-confidence rate.
- Coverage: the proportion of questions for which the system issues a forecast.
- The trade-off between forecast risk and coverage.
- Performance on the questions where the agent abstains (what it would have scored), to show whether abstaining was justified.

Choose the abstention threshold using development data and evaluate it on separate test data. Avoid selecting a threshold after inspecting the final test outcomes.

**D. Evaluation**

Compare the new agent against appropriate baselines using a reproducible test set. Continue prospective testing where possible.

### Proposed research contribution

An experimentally evaluated approach to evidence-grounded and uncertainty-aware forecasting for Indian events.

The contribution must be supported by results showing whether the approach improves forecast quality or reduces false confidence. Do not assume that the proposed method will outperform the baselines.

### Output

Working Module 2 ("Ask the Forecaster") + open agent code + **Conference paper 2** (evidence-grounded, calibrated, abstaining forecasting).

## 5. Final Project: Impact-Aware Forecasting

**Estimated period:** Final project period, according to GLA requirements.

### Purpose

Integrate the forecasting agent with a cause-and-effect graph so users can explore the possible downstream consequences of a predicted event.

This is where the existing Reflica graph-reasoning work becomes especially useful.

### Research question

Does using an explicit cause-and-effect model to estimate downstream consequences of forecast events produce better forecasts of those consequences than asking an LLM to predict the consequences directly?

### Example

Suppose the system forecasts an elevated probability of an extreme heat event.

A possible dependency graph is:

Extreme heat → electricity demand → supply shortage → water-pumping disruption → effects on hospitals and industry.

These are hypotheses about possible dependencies, not guaranteed outcomes. The system must represent uncertainty and account for relevant conditions, such as available generation, water storage, local infrastructure, and mitigation measures.

### Features to build

**A. Interactive impact map**

Reuse the existing Reflica mind-map or graph interface where practical.

Display:
- The initial forecast and its probability.
- Downstream events or consequences.
- The relationship connecting each node.
- Evidence supporting each relationship.
- Conditional probabilities or uncertainty ranges when adequately estimated.
- Important assumptions and missing information.
- Observed outcomes when the event has been resolved.

**B. Reuse the Reflica engine**

Evaluate whether the existing graph propagation, ground truth, constraint reasoning, and relevant components can support the new impact-analysis task.

Do not assume that the old engine can directly propagate probabilities. Its existing plan-revision behaviour must be assessed against the mathematical and causal requirements of forecasting.

Where necessary, implement and test a separate probabilistic propagation layer rather than forcing the old engine to perform a task it was not designed for.

**C. Scientific evaluation**

Compare at least:
1. Direct LLM prediction of downstream effects.
2. A suitable baseline that does not use the explicit graph.
3. The graph-based approach using Reflica components, if technically appropriate.

Evaluate against predefined outcomes using appropriate probability scores, calibration, and other task-specific metrics.

The main challenge is obtaining reliable labels for downstream effects and avoiding the assumption that a temporal sequence proves causation.

### Proposed research contribution

A tested method for combining event forecasts with explicit dependency reasoning to estimate downstream effects. The contribution must show when graph-based propagation helps, when it fails, and how uncertainty changes along the graph.

### Output

Working Module 3 (Impact Map) + live track record + **Final research paper** + M.Tech thesis.

## 6. Shared platform and architecture

The three projects should extend one platform, with features added in stages.

### Frontend

Reuse the existing Flutter application and its working components.

Proposed additions:
- Forecast catalogue and details.
- Forecast history and leaderboard.
- Ask the Forecaster.
- Evidence viewer.
- Impact map.

Do not rebuild the frontend in React or Next.js unless there is a demonstrated need and I approve the change. (This replaces the earlier FastAPI/Streamlit/React suggestion in the 13 October version.)

### Existing Firebase integration

Inspect the existing Firebase setup first and reuse the appropriate services for authentication, persistence, and any existing offline functionality.

Design the new forecasting data models around the current architecture. Avoid duplicating users or replacing working sign-in and storage systems.

The frontend must not directly hold privileged LLM API keys.

### Forecasting backend

Determine the best integration with the existing project before choosing the implementation.

A Python service may be appropriate for model calls, scoring, scheduled evaluation, and graph reasoning. FastAPI is a candidate, not a mandatory decision.

Keep the following concerns separated:
- Question management.
- Forecast generation.
- Evidence retrieval.
- Immutable forecast history.
- Resolution and scoring.
- Graph-based impact analysis.

If a separate Python service is needed, explain how it will authenticate, communicate with Firebase, and protect secrets.

### Automated jobs

Eventually support:
- Scheduled forecasts.
- Checking whether questions have resolved.
- Recording official outcomes.
- Recalculating leaderboard summaries.
- Logging failures and retrying safely.

Automated jobs must not silently replace existing predictions or alter historical scores without an auditable correction record.

## 7. Publications

| Paper | From | Working title | Target venue |
|---|---|---|---|
| Conference paper 1 | Minor Project 1 | Benchmark design, Indian vs Western comparison and empirical findings ("How well do LLMs forecast Indian events? A prospective benchmark") | NeurIPS / ACL workshop, or an IEEE conference |
| Conference paper 2 | Minor Project 2 | The honest forecasting agent: evidence retrieval, probability calibration and abstention ("Knowing when not to forecast") | AAAI / EMNLP / ACL workshop, or IEEE conference |
| Final research paper + M.Tech thesis | Final Project | Impact-aware forecasting and downstream consequence analysis, with live evaluation | Main AI conference (ACL, EMNLP, AAAI), International Journal of Forecasting, or IEEE TKDE |
| Optional review | Literature work | A systematic review of LLM agents for event forecasting | Artificial Intelligence Review (Springer) |

These are research goals, not guaranteed publication outcomes. Each paper reports only what the experiments show, including negative results.

## 8. Research integrity rules

1. Preserve all historical forecasts and their original timestamps.
2. Store forecast probabilities before outcome resolution.
3. Define outcome sources and resolution rules in advance.
4. Prevent future information from leaking into historical or prospective forecasts.
5. Use clear train, calibration, development, and evaluation periods where relevant.
6. Report sample sizes and uncertainty alongside scores.
7. Compare against meaningful baselines.
8. Separate correlation, prediction, and causal claims.
9. Verify every claimed literature gap against the actual paper, not only its abstract or a summary.
10. Report negative results honestly.
11. Keep the product roadmap separate from the evidence supporting the research claims.

## 9. Immediate tasks

Do these tasks in order:

1. Inspect the current repository and report the actual state of the Flutter application, Firebase integration, Python research code, tests, and documentation.
2. Identify which Reflica components can be reused directly and which require adaptation.
3. Propose a minimal integration architecture and folder layout for the new forecasting workstream.
4. Propose the question and forecast data schemas (including the India/Western region tag), and how immutable prediction history and resolution records will work with the existing Firebase setup.
5. Explain the proposed changes before implementing them.
6. After I approve the plan, help me write and timestamp the first 20 pilot questions (December 2026) and implement a minimal working forecast dashboard.
7. Help me set an API budget and choose low-cost models for the pilot.
8. Keep a short dated progress log and update the project documentation as real implementation work is completed.

> **[Addition, 14 Oct 2026, not in the user's text]** Status of section 9 on 14 Oct 2026: tasks 1–2 done (`research/forecast/AUDIT.md`, `docs/ARCHITECTURE.md`); tasks 3–4 proposed (`docs/ARCHITECTURE.md`, `research/forecast/PILOT_PROTOCOL.md`) and approved in principle; the tasks follow the implementation order stated at the top.

**Working principle:** I write the code and learn the underlying concepts. You guide the design, explain the reasoning, review my code, help debug errors, and check scientific validity. The actual repository and tests are the source of truth for implementation status.

## Appendix: literature background (from the 13 October review)

Gaps found in 21 recent papers (abstract-level; verify in full texts): forecasts are rarely calibrated; no system abstains; little prospective (live) testing, so leakage is likely; cause chains are extracted from past text but not used forward; India is almost absent (one paper, stock indices). Supporting: rare big events are fragile; single-case evaluations; LLM extraction errors unmeasured.

Read first: the survey "LLM-based Agents for Forecasting and Prediction" (arXiv 2608.23058, 2026); "ForecastBench" (ICLR 2025); "From News to Forecast" (NeurIPS 2024); "Application of Large Language Models in the Problem of Event Forecasting" (2025); "Hierarchical Semantic Extraction and Heterogeneous GNNs for Event-Driven Time Series Forecasting" (Scientific Reports 2026); "A Large Language Model Framework for Predicting Significant Equity Index Fluctuations" (NIFTY, 2026).

Full analysis: review page https://claude.ai/artifact/B61G9cki25mLr8aRaSXK81, plus `LITERATURE_FORECASTING.md` and the research brief (Word) in the Windows folder.

> **[Addition, 14 Oct 2026, not in the user's text]** `LITERATURE_FORECASTING.md` is now also in this repository (`research/forecast/`), with a gap-verification checklist and papers outside the 21 that must be read before any gap is claimed (e.g. Halawi et al. 2024, Autocast, ForecastQA).
