# Minor Project 1: detailed design

Date: 14 October 2026. Moved here from the earlier `NEW_DIRECTION.md`, where the user approved it as the Minor 1 description.
Status: the student's chosen plan; **M.Tech guide approval pending**.
Authority: `../../NEW_DIRECTION.md` section 3 is authoritative. This file gives the detail. Where they differ, `NEW_DIRECTION.md` wins.
Mapping: Part 1 here = **A2** (automatic question generator). Part 6D experiment 3 here = **A3** (past-question study). Both are upgrades within Minor 1.
Implementation order: documentation → Flutter UI → Python backend → connect. The December 2026 pilot is collected by hand (`PILOT_PROTOCOL.md`).

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

Every generated question passes the same checks as hand-written ones; review a sample by hand and report the rejection rate. Respect each site's terms and robots.txt; prefer official APIs or downloadable files; store the source URL and fetch time. News headlines about scheduled events are a secondary source, used only when an official resolution source exists.

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

- **Start with 2–3 accessible models** (decision D4); estimate API costs before expanding to 3–4.
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
- **Official Indian forecasts (addition; deferred from the initial pilot by decision D3 unless a defensible probability conversion is documented in advance; see `PILOT_PROTOCOL.md`):** compare the AI with **RBI's own inflation projections** (published in the monetary-policy statements) and **IMD's own forecasts** (e.g. monsoon long-range and extended-range forecasts). Official forecasts are often a point value or a range rather than a probability, so the rule for turning each into a forecast for a question must be **written before** the questions resolve (IMD's categorical monsoon forecasts already give probabilities). If the AI cannot beat India's official forecasters, that is an important finding; if it can, that is stronger still.

**D. Research comparisons.**
1. **Does news help?** Each model with vs without timely retrieved news.
2. **India gap?** Indian vs Western questions matched on category, difficulty and horizon. A difference is a finding only if the evidence supports it.
3. **Historical vs prospective (A3, past-question study).** Past questions are used for (1) end-to-end pipeline testing, (2) development data, and (3) a leakage study. Record each model's stated knowledge cutoff and split past questions into "before cutoff" and "after cutoff". In the news condition, give only news published before that question's forecast date. Compare cautiously with live forecasts: a difference alone does **not** prove memorisation. Past-question results are reported separately, never as the main forecasting performance and never mixed into prospective benchmark scores.

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

