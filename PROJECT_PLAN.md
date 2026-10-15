# Reflica India: Project Planning and Guidelines

**Saved:** 15 October 2026, from the user's text, word for word; only the formatting was tidied.
**Status:** working research definitions for discussion. Titles and scope are **provisional until the supervisor approves them** after the literature review. Papers and later stages are targets, not guaranteed outcomes.
**Authority:** this is the current plan. Earlier plans in `NEW_DIRECTION.md` and `research/forecast/` are kept as history.

---

# Locking the Research Direction and Both Minor Projects

We should define these as one connected research programme with three stages: the overall research problem, Minor Project 1, and Minor Project 2. Each stage should answer a specific question, build something concrete, and produce evidence that the method works—or reveal where it fails.

The most important decision is this: we are not building three unrelated AI projects. We are developing one forecasting system, then testing and extending its capabilities.

## The research roadmap

| Stage | Title | Question / aim |
|---|---|---|
| **Overall research** | Predictive AI for India's Economy and Government Policy | Research how AI can make forecasts that are evidence-based, uncertainty-aware, and responsibly revised as new information arrives. |
| **Minor Project 1** | Reflica India: Evidence-Aware Economic Forecasting and Forecast Revision | Can dated evidence and careful revisions improve next-month CPI inflation forecasts? |
| **Minor Project 2** | Honest Forecasting of India's Policy Decisions | Can AI estimate the probabilities of policy outcomes reliably—and recognize when it should not make a confident prediction? |
| **Long-term thesis** | | Combine economic and policy forecasting with calibrated uncertainty, careful forecast revision, and carefully evaluated relationships between events and their possible consequences. |

These are working research definitions, not yet claims of originality or guaranteed research results. The final titles and scope should be approved by your supervisor after the literature review.

---

# Part 1 — Overall research

## 1. What problem are we trying to solve?

India's economic and policy environment changes over time. Inflation, food and fuel prices, industrial production, currency movements, employment, and government or RBI decisions can all affect future conditions.

An AI forecasting system faces four challenges:

1. **Prediction:** How can it use historical data to estimate what may happen next?
2. **Evidence:** Can it show which available information supports or challenges its forecast?
3. **Revision:** When new evidence arrives, should it change the prediction, and by how much?
4. **Uncertainty:** When is its forecast dependable, and when should it admit that the evidence is insufficient?

The overall research problem is therefore not simply "predict the future." It is:

> **How can we build and evaluate AI systems that forecast important Indian economic and policy outcomes, explain their evidence, revise their predictions responsibly, and communicate uncertainty honestly?**

## 2. Proposed research gap

We must verify this through a literature review; we should not claim that no one has solved it before.

The gap we will investigate is whether forecasting systems can combine numerical forecasting, time-stamped textual evidence, controlled revision, and honest uncertainty evaluation in a single reproducible workflow.

| Existing approach to investigate | Limitation we will examine |
|---|---|
| Numerical time-series models | May not directly incorporate the information contained in newly published reports and news |
| LLM-based forecasting | May give plausible explanations without sufficiently reliable probabilities, reproducibility, or outcome-based evaluation |
| News-augmented forecasting | May use text, but we need to investigate whether it tracks evidence provenance and tests the value of each piece of evidence |
| Forecast updating | Updating too often may introduce noise; not updating may ignore important information |
| Forecast uncertainty | A stated confidence or prediction range may not be reliable unless it is tested against actual outcomes |

The research contribution must come from the method and the experiments—not from combining fashionable AI components. We need to establish what previous research already does, then identify the precise missing capability that our work can test.

## 3. How we plan to solve it

We will develop Reflica India around this shared pipeline:

1. **Collect information:** historical numbers, official releases and dated documents.
2. **Extract evidence:** identify claims, dates, sources, direction and uncertainty.
3. **Produce a forecast:** a forecasting model estimates the target outcome.
4. **Check new information:** assess novelty, credibility, relevance and strength.
5. **Revise or retain:** change the forecast only under a tested revision rule.
6. **Evaluate the result:** compare forecasts with actual outcomes and baselines.

The shared pipeline stays broadly the same. What changes across the projects is the prediction target, modelling method, evaluation metric, and level of uncertainty handling.

---

# Part 2 — Minor Project 1: Reflica India

**Planned period:** January–May 2027 · **Main focus:** economic forecasting

## 1. Project definition

**Proposed project title:** Reflica India: Evidence-Aware Economic Forecasting and Forecast Revision

- **Problem:** A model can forecast inflation from historical numbers, but it may not use newly available evidence effectively. A system that incorporates news also needs to distinguish credible, relevant information from noise and prove whether that information improves its predictions.
- **Solution:** Build a forecasting system that predicts India's next-month CPI inflation, links its forecast to time-stamped evidence, and uses a testable rule to decide whether new evidence justifies a revision.
- **Main contribution to investigate:** An evidence-aware forecast revision method that can be compared experimentally with simpler alternatives.

## 2. What exactly will we predict?

We need to define this precisely before writing code.

- **Target:** India's all-India combined Consumer Price Index (CPI) inflation rate, measured year-on-year, for the next month.
- **Output:** A numerical forecast, such as 4.8%, plus a prediction interval and supporting evidence.
- **Input:** Historical CPI and selected economic indicators, along with reports and news available before the forecast cutoff.
- **Prediction timing:** Several fixed checkpoints before the target month's CPI release, where practical.
- **Official outcome:** The published CPI inflation figure for the same target month and the same series.

One important data decision: MoSPI introduced a revised CPI series with base year 2024=100 in February 2026. We must use a consistent, documented series and handle any historical back-series or methodology issues carefully.

For example, if the target is November CPI inflation, Reflica might predict the value in late October, revise it in early November if justified, and compare its final pre-release forecast with the official November result. The dates are illustrative; the real schedule must follow the official release calendar.

## 3. The research gap we will test

The gap is not simply "AI does not predict inflation." Many forecasting approaches already exist. Our question is more specific:

> **Can a system that tracks dated evidence and revises forecasts selectively improve forecast accuracy or reliability compared with forecasting from numerical data alone, using text without a revision rule, or using simple update strategies?**

We will examine three potential weaknesses in existing approaches:

1. Numerical models may not directly use the information in newly published textual reports.
2. Text-based systems may struggle to provide reproducible, source-linked evidence for their predictions.
3. Forecasts can be too rigid or too reactive: a system may ignore important new evidence or overreact to weak reports.

These are research hypotheses, not established facts about every existing system. We will review forecasting, economic NLP, news-based prediction, and forecast-revision research before finalizing the exact gap.

## 4. The eight features: what we will build and how

### Feature 1 — Numerical forecasting engine
- **Purpose:** Produce a baseline prediction for next-month CPI inflation.
- **Method:** Start with simple baselines, then test statistical forecasting such as ARIMA and a machine-learning model such as XGBoost if the available training data supports it. Use lagged CPI and carefully selected economic indicators.
- **Example:** "Forecast for November CPI inflation: 4.8%."
- **Deliverable:** A reproducible model that accepts data available at a specified cutoff and returns a forecast.

### Feature 2 — Multi-source, time-stamped data
- **Purpose:** Make sure the model only uses information that was available at the time of prediction.
- **Method:** Collect historical CPI, food-price indicators, fuel-related indicators, exchange-rate data where appropriate, and selected official economic releases. Store the publication date, observation period, source, and retrieval details.
- **Example:** A report published on October 20 can be used for a forecast made on October 22; a report published on October 25 cannot.
- **Deliverable:** A documented dataset with point-in-time cutoffs and a clear record of each input's origin.

### Feature 3 — Evidence intelligence and evidence graph
- **Purpose:** Turn relevant text into structured information the system can inspect.
- **Method:** Use an LLM to extract a claim, source, publication date, affected indicator, likely direction, and any uncertainty. Link the extracted claim to its source and the forecast it may affect.
- **Example:** "Heavy rainfall damaged vegetable crops" may be tagged as a potential upward food-price signal. A report indicating improved supply may provide a counter-signal.
- **Important:** The LLM extracts and organizes evidence; it does not get to invent the final CPI forecast. Extracted claims must be checked, and their directions are hypotheses rather than proof of causation.
- **Deliverable:** A browsable evidence graph with source links, dates, and traceable claims.

### Feature 4 — Forecast uncertainty
- **Purpose:** Show that a forecast is an estimate, not a guaranteed outcome.
- **Method:** Estimate a prediction interval using historical forecast errors or another suitable method. Check whether the interval covers actual outcomes at approximately the intended rate during backtesting.
- **Example:** "CPI forecast: 4.8%; illustrative prediction interval: 4.2%–5.4%."
- **Deliverable:** A forecast with a validated interval, plus an explanation of relevant evidence conflicts or limitations. The example range is not a real forecast.

### Feature 5 — Smart forecast revision (main research contribution)
- **Purpose:** Decide when new evidence should change a forecast and when the existing forecast should remain unchanged.
- **Method:** Evaluate each new item for novelty, source reliability, relevance to CPI, strength, and agreement or conflict with existing evidence. Test a predefined revision rule against alternative strategies.
- **Example:** The forecast starts at 4.8%. A new official release changes the relevant numerical inputs, and the tested revision method moves the estimate to 5.0%. The system records the evidence and reason. A weak or duplicated news story may leave the forecast unchanged.
- **Deliverable:** A revision engine that logs the old forecast, new forecast, evidence considered, decision, and reason. We must experimentally test whether this rule actually helps.

### Feature 6 — What-if scenario analysis
- **Purpose:** Explore how a forecast responds to hypothetical changes.
- **Method:** Change a selected input or scenario assumption and run the model again. Label the result as a conditional scenario, not a proven causal effect.
- **Example:** "What would the model forecast if the selected food-price indicator rose by 10%?"
- **Deliverable:** A scenario comparison. This feature is optional if the core forecasting and revision experiments take longer than expected.

### Feature 7 — Experimental evaluation
- **Purpose:** Establish whether the proposed approach is better than alternatives.
- **Method:** Use rolling or walk-forward historical backtesting. Compare a naive baseline, ARIMA, XGBoost if suitable, a text-informed approach, and the proposed revision strategy.
- **Metrics:** MAE and RMSE for point forecasts; interval coverage and width for uncertainty; additional metrics where justified.
- **Deliverable:** A reproducible benchmark with results, limitations, and error analysis. A model that performs worse must be reported honestly.

### Feature 8 — Reflica India dashboard
- **Purpose:** Let a researcher inspect forecasts and understand how they were produced.
- **Method:** Display the target month, forecast, prediction interval, data cutoff, evidence graph, conflicting claims, revision history, model version, and experiment results.
- **Deliverable:** A working prototype that makes the underlying research inspectable—not merely a chatbot that generates a number and an explanation.

### What is mandatory and what is optional?

| Build for Minor 1 | Add only if the core work is stable |
|---|---|
| Numerical forecasting | Interactive what-if scenarios |
| Dated data pipeline | Additional economic indicators |
| Evidence extraction and graph | More sophisticated LLM approaches |
| Prediction intervals | Extra dashboards and visual polish |
| Forecast revision method | Additional forecasting models |
| Historical backtesting | More live forecast demonstrations |
| Dashboard and revision log | RBI policy forecasting |

The rule is simple: **do not sacrifice experimental quality to add more features.**

## 5. The complete method, from data to results

1. **Define the prediction.** Specify the CPI series, target month, forecast horizons, cutoff rules, and release-date convention.
2. **Collect historical data.** Assemble CPI observations and selected indicators, recording when each observation became available.
3. **Create a simple baseline.** Train and evaluate a numerical forecasting model before introducing textual evidence.
4. **Build the evidence pipeline.** Collect dated documents and use an LLM to extract source-linked claims and potential inflation signals.
5. **Connect evidence to forecasts.** Create a defined way to represent relevant, conflicting, repeated, weak, and strong evidence.
6. **Implement revision strategies.** At fixed forecast checkpoints, compare never-update, always-update or predetermined update rules, and the proposed evidence-aware revision method. Define these strategies precisely before testing.
7. **Run historical backtests.** Replay the process month by month, using only information available at each historical cutoff. Fit models only on data that would have been available then.
8. **Evaluate uncertainty and errors.** Calculate forecast errors, check interval coverage, inspect failed predictions, and compare all methods fairly.
9. **Build the dashboard and conduct a live trial.** Save prospective forecasts before outcomes are released, then compare them with actual results.
10. **Write the research report.** Explain the method, experiments, results, weaknesses, and what the results do and do not establish.

## 6. How we will test the two research questions

**Research question 1: Does adding dated textual evidence improve CPI forecasts over numerical data alone?**
We compare models using equivalent forecast dates and information cutoffs. A useful experiment would compare numerical-only forecasting with a version that adds signals extracted from documents. We must prevent future information from entering historical forecasts.

**Research question 2: Does evidence-aware revision outperform simple update strategies?**
We replay historical forecast checkpoints under several strategies:
- Never update after the initial forecast.
- Update at each scheduled checkpoint using a defined standard approach.
- Revise using the proposed evidence-aware rule.

The models must be compared at the same target months and horizons. If the methods use different information or different amounts of training data, the comparison could be misleading.

**Main evaluation:** MAE and RMSE measure numerical error; interval coverage checks whether uncertainty ranges are reliable. We will also examine revision frequency, unnecessary changes, and missed important updates.

**A critical limitation.** A five-month live trial may produce only a handful of independent monthly outcomes. That is useful for demonstrating the software and documenting real forecasts, but not enough by itself to prove general superiority. Historical backtesting must be the main evaluation, and a live trial should supplement it.

Also, an LLM may have encountered historical economic outcomes during training. Restricting documents by date helps prevent direct leakage from our dataset, but does not completely eliminate memorization risk. We should document this limitation and design the evaluation accordingly.

## 7. How will Minor 1 help in the real world?

- **Economic researchers and analysts:** They could inspect a forecast alongside the evidence and identify what changed between successive predictions.
- **Policy and planning teams:** They could use a well-evaluated forecast as one input into planning and risk analysis—not as a replacement for official statistics or expert judgment.
- **Auditing and research reproducibility:** Researchers could trace why a forecast changed, which documents were used, and whether the prediction later proved accurate.

These are potential applications, not claims that the prototype is already accurate enough for operational policy decisions.

## 8. What should exist by May 2027?

1. A functioning CPI forecasting model.
2. A time-stamped dataset and point-in-time evaluation pipeline.
3. An LLM-based evidence extraction and graph component.
4. A tested forecast revision method.
5. A historical benchmark comparing the alternative strategies.
6. A dashboard showing forecasts, evidence, uncertainty, and revisions.
7. A research report and a Paper 1 draft, if the results and time support it.

The success criterion is not "the forecast looks intelligent." It is that we can demonstrate exactly what the system did, evaluate it fairly, and explain the evidence for any performance claim.

---

# Part 3 — Minor Project 2: Honest forecasting of policy decisions

**Planned after Minor 1** · Exact schedule and title subject to supervisor approval

## 1. Why do we need a second project?

Minor 1 predicts a numerical value: CPI inflation might be 4.8%.

But many government and economic events are not simple numerical forecasts. They involve different possible decisions. For example:

- Will the RBI cut, hold, or increase the repo rate?
- Will a particular GST rule change?
- Will the Union Budget announce a specified policy?
- Will a particular MSP increase meet a defined threshold?

For these questions, Reflica should not merely generate a confident-sounding answer. It should estimate probabilities, show the evidence, and identify cases where it does not have enough information.

## 2. Proposed project definition

**Provisional title:** Honest Forecasting of India's Policy Decisions: Calibrated Probabilities and Abstention

- **Problem:** AI may predict a policy outcome without demonstrating that its stated confidence matches its actual reliability. It may also give an answer when the available evidence is weak or contradictory.
- **Solution:** Extend the Reflica pipeline to selected policy events, produce probabilities for clearly defined outcomes, test whether those probabilities are calibrated, and introduce an abstention mechanism for cases where the system should not make a confident prediction.
- **Main contribution to investigate:** Whether calibrated probabilities and selective abstention improve the reliability and usefulness of AI policy forecasts.

## 3. Research questions

1. Can Reflica estimate probabilities for selected Indian policy decisions more reliably than simple base-rate or other suitable baselines?
2. Are its predicted probabilities calibrated against actual historical outcomes?
3. Can a system that abstains when evidence is insufficient reduce confident errors without abstaining so often that it becomes useless?
4. Does evidence-aware revision improve the quality of policy forecasts as new information arrives?

The fourth question reuses the revision concept from Minor 1. It should remain in scope only if it can be evaluated without making the project too broad.

## 4. Features and methods

### Feature 1 — Policy-event forecasting
Define a small number of events with precise outcomes. A practical first candidate is the RBI repo-rate decision: cut, hold, or hike at a specified policy meeting.
- **Method:** Build a historical event dataset with the outcome, forecast cutoff, available indicators, official communications, and dated evidence. Select events only after checking that enough consistent historical examples are available.
- **Deliverable:** A reproducible dataset and policy forecasting task.

### Feature 2 — Probabilistic predictions
Instead of saying "the RBI will hold," Reflica could say "hold: 60%, hike: 25%, cut: 15%."
- **Method:** Use a suitable statistical or machine-learning classifier, with an optional LLM-derived evidence component. Compare it with a historical base-rate baseline and other appropriate baselines.
- **Deliverable:** A probability distribution over defined outcomes. The example percentages are illustrative, not a current forecast.

### Feature 3 — Probability calibration
- **Purpose:** Test whether the system's confidence means what it says.
- **Method:** Use calibration plots and metrics such as the Brier score and expected calibration error (ECE), with careful handling of small datasets and multiclass outcomes.
- **Example:** Across enough comparable forecasts assigned a 70% probability, the event should occur roughly 70% of the time if that probability level is well calibrated.
- **Deliverable:** Evidence about the reliability of probabilities—not just whether the most likely outcome was correct.

### Feature 4 — Abstention: knowing when not to predict
- **Purpose:** Avoid presenting weak predictions as dependable.
- **Method:** Set a decision rule using uncertainty, evidence quality, model confidence, or a combination of these. If the rule is triggered, Reflica reports that it cannot provide a sufficiently reliable forecast and explains why.
- **Deliverable:** An abstention mechanism evaluated against coverage and error. We must report both how often it abstains and how accurate it is when it does predict.

### Feature 5 — Evidence graph and revision
Reuse Minor 1's source tracking, evidence extraction, and revision history. Add policy-specific evidence, such as inflation trends, official statements, and relevant economic indicators.
- **Method:** Test whether a forecast's probability distribution changes appropriately when new evidence arrives. Track why the probabilities changed.
- **Deliverable:** A transparent history of policy forecast revisions.

### Feature 6 — Evaluation and comparison
Compare Reflica against historical base rates and other feasible forecasting approaches.
- **Method:** Use chronological or walk-forward testing, Brier score, calibration analysis, and measures of selective performance when the system abstains. Compare methods on the same events and information cutoffs.
- **Deliverable:** A benchmark showing whether the system's probabilities and abstentions are actually useful.

### Feature 7 — Policy forecasting dashboard
Display possible outcomes and their probabilities, the evidence behind them, calibration history, abstention decisions, and forecast revisions.
- **Deliverable:** An extension of Reflica India for policy-event analysis.

## 5. How Minor 2 will work

1. **Choose a precise policy event:** define outcomes, dates and historical examples.
2. **Collect historical evidence:** store only information available at each forecast cutoff.
3. **Estimate probabilities:** use a classifier or other suitable forecasting method.
4. **Calibrate and assess uncertainty:** test probability reliability on held-out events.
5. **Abstain when warranted:** apply a defined rule when the evidence is insufficient.
6. **Evaluate and explain:** compare against baselines and inspect both correct and incorrect forecasts.

## 6. How Minor 2 differs from Minor 1

| Dimension | Minor 1 | Minor 2 |
|---|---|---|
| Main target | Next-month CPI inflation | Selected policy-event outcomes |
| Output | Numerical estimate and prediction interval | Probabilities for multiple outcomes |
| Core question | Does evidence-aware revision improve forecasting? | Are probabilities reliable, and does abstention help? |
| Main metrics | MAE, RMSE, interval coverage | Brier score, calibration, coverage and selective error |
| Shared components | Evidence graph, dated inputs, revision log | Reuses and extends these components |
| Main new capability | Selective forecast revision | Calibrated probabilities and abstention |

## 7. How it could help in the real world

Policy researchers, analysts, and planning teams could use a system like this to examine multiple plausible outcomes rather than treating one prediction as certain. They could see which evidence supports each outcome, how probabilities changed, and when the system recommends withholding judgment.

It would be a decision-support tool, not a system that determines government policy. A well-calibrated forecast can still be wrong, especially when events are rare or circumstances change abruptly.

## 8. What should exist at the end of Minor 2?

- A policy-event dataset with explicit outcome definitions.
- A probabilistic forecasting model.
- A calibration and abstention method.
- A benchmark against suitable baselines.
- A dashboard showing probabilities, evidence, uncertainty, and revision history.
- A second research paper draft if the evidence, novelty, and available time support it.

The scope should start with one policy-event family, most plausibly RBI repo-rate decisions. Add GST, Budget, or MSP forecasts only if the data and time justify them. Otherwise, the project risks becoming a large collection of shallow predictors.

---

# Part 4 — Final thesis and the complete research programme

The long-term thesis combines the strongest validated components from both projects. It should not simply combine every feature we can imagine; it should extend what the experiments establish.

## 1. Overall thesis

- **Working thesis title:** Honest AI Forecasting of India's Economic and Policy Events: Calibrated Probabilities, Abstention and Live Evaluation
- **Research objective:** Develop and evaluate AI methods that produce traceable forecasts, incorporate new evidence, revise predictions carefully, quantify uncertainty, and recognize when they lack sufficient evidence.
- **Possible final contribution:** An evaluated framework for evidence-aware forecasting and forecast revision, extended to calibrated policy probabilities and abstention.

## 2. What will be added at the thesis stage?

- **Feature 1 — Connected economic and policy evidence:** Extend the evidence graph to represent relationships among indicators, reports, claims, policy events, and forecast targets. Every relationship should carry a clear meaning and source.
- **Feature 2 — Potential downstream consequences:** Explore relationships such as an RBI rate change and possible effects on borrowing costs, demand, and inflation. Use suitable economic models and evidence to distinguish plausible mechanisms from simple correlations.
- **Feature 3 — Longitudinal live evaluation:** Save forecasts prospectively over a longer period, evaluate them when outcomes become available, and study performance under changing economic conditions. The duration will depend on the research schedule and available events.
- **Feature 4 — Reliability and failure analysis:** Investigate when the system fails: conflicting reports, unexpected shocks, data revisions, poor calibration, weak evidence, or changes in the underlying economic relationships.

The thesis should aim to explain not only what the model predicts, but also why the forecast changes, how reliable the prediction is, and under what conditions the method fails.

---

# Part 5 — What is the research contribution?

Here is the distinction we need to preserve.

| Stage | Main research contribution being investigated |
|---|---|
| Overall research | A reproducible approach to honest, evidence-aware forecasting for India's economy and policy |
| Minor Project 1 | A method for incorporating dated textual evidence and revising numerical economic forecasts selectively |
| Minor Project 2 | A method for producing calibrated policy-event probabilities and abstaining when evidence is insufficient |
| Final thesis | A validated integration of these methods, potentially extended to relationships between events and downstream consequences |

A project is not novel just because it uses an LLM, a knowledge graph, XGBoost, or a dashboard. The research contribution must be a clearly defined method, supported by a literature review and experiments that show what it adds beyond previous work.
