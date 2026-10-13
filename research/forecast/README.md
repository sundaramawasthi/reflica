# forecast — India Forecast Benchmark (workstream started 2026-10-13)

New M.Tech direction: honest AI forecasting of Indian events. See `../../NEW_DIRECTION.md`.
The Reflica benchmark (`../reflica_bench/`) is kept and paused.

## Proposed layout (user writes the code)

```
research/forecast/
  README.md           this file
  questions/          one JSON file per question (q0001.json ...), never edited after freeze
  generator/          turns official data (RBI, MOSPI, IMD, Grid-India, CWC) into CANDIDATE questions
                      (candidates are checked by hand before they enter questions/)
  sources/            notes per source: RBI, MOSPI, Grid-India, CWC, IMD, PIB, GDELT, ACLED
                      (URL, release calendar, how to read the answer)
  runner/             asks each LLM each open question, saves the raw answer with a timestamp
  scoring/            resolves questions and computes Brier, accuracy, calibration
  results/
    forecasts/        append-only JSONL, one line per (question, model, run)
    resolutions/      the real answer + evidence URL + date checked
    reports/          tables and plots
research/tests/test_forecast_*.py   tests for schema, runner, scorer
```

Rules:
- Forecasts are **append-only**. Never edit a saved forecast. This is the proof it was made before the event.
- A question is **frozen** once the first forecast for it is saved. Fixes make a new id.
- Commit forecasts to git the same day they are made; the commit time is a second, independent timestamp.

## Question schema (draft for the user to decide)

| Field | Example | Why |
|---|---|---|
| `id` | `IN-ECO-0001` | stable key |
| `question` | "Will India's CPI inflation (combined, y/y) for January 2027, as first released by MOSPI, be above 4.0%?" | one clear yes/no |
| `category` | `economy` / `infrastructure` / `geopolitics` | |
| `region` | `india` / `western` | the India-vs-West comparison |
| `indicator` / `units` / `period` / `threshold` | `CPI combined y/y`, `%`, `2027-01`, `5.0` | filled by the generator for data-based questions |
| `question_source` | data record or event it was made from | traceability |
| `horizon_days` / `difficulty` | `45` / rule-based label | for matching Indian and Western questions |
| `pair_id` | `CPI-2027-01` | links an Indian question to a matched Western one (US CPI) so difficulty is comparable |
| `type` | `binary` | start with yes/no only |
| `created_date` | `2026-12-01` | when written |
| `forecast_close_date` | `2026-12-15` | last day a forecast counts |
| `resolve_date` | `2027-02-12` | when the answer is expected |
| `source_name` / `source_url` | MOSPI CPI press release | |
| `resolution_rule` | "Use the first release, not revisions. Round to 1 decimal. Exactly 4.0 = No." | removes arguments later |
| `base_rate` | `0.35` + how computed | for the base-rate baseline |
| `last_value` | `3.8` | for the "same as last time" baseline |
| `official_forecast` | RBI projection or IMD forecast + rule used to turn it into a probability | official-forecast baseline (rule fixed before resolution) |
| `answer` | `null` until resolved, then `true`/`false` | |
| `status` | `candidate` / `open` / `resolved` / `unresolved` / `invalid` | unresolved/invalid by a predefined rule, never forced |
| `notes` | | |

## Literature checks before claiming any gap

These must be read before a paper says "nobody has done X":
- Halawi et al. 2024, "Approaching Human-Level Forecasting with Language Models": retrieval + LLM + ensembling, Brier on questions after the model's cutoff. Overlaps gaps 1 and 3.
- Zou et al. 2022, "Forecasting Future World Events with Neural Networks" (Autocast); Jin et al. 2021, ForecastQA.
- Schoenegger et al. 2024, "Wisdom of the Silicon Crowd" (LLM ensembles vs human crowd).
- Paleka et al. 2025, "Pitfalls in Evaluating Language Model Forecasters" (leakage problems).
- Wen et al. 2024, "Know Your Limits: A Survey of Abstention in Large Language Models" (gap 2 exists in general LLM work, not for forecasting).
- Bayesian networks / probabilistic causal graphs (gap 4: reviewers will ask "why not a Bayesian network?").
