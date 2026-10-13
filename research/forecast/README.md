# forecast: India Forecast Benchmark (workstream started 2026-10-13)

Research direction (authoritative): `../../NEW_DIRECTION.md`. The direction is chosen by the student; **formal M.Tech guide approval is pending**.
The Reflica benchmark in `../reflica_bench/` is kept unchanged and paused.
Implementation order: Documentation → Flutter UI → Python backend → connect the UI to real data. Exception: the December 2026 pilot is recorded by hand (`PILOT_PROTOCOL.md`).

| Document | Purpose |
|---|---|
| `PILOT_PROTOCOL.md` | **Single source** for record formats, hashing, timestamps, baselines, India–Western pairs and the manual December 2026 pilot |
| `MINOR1_DESIGN.md` | Detailed Minor Project 1 design (pipeline, A2 generator, A3 past-question study, experiments, roadmap) |
| `MILESTONE_1.md` | Backend milestone (Phase 3): minimum Python files and tests; first question |
| `LITERATURE_FORECASTING.md` | Literature analysis and the gap-verification checklist |
| `AUDIT.md` | Dated repository audit snapshot (14 Oct 2026) |

## Layout (proposed; folders are created when first needed; the user writes the code)

```
research/forecast/
  questions/candidates/        editable drafts during review
  questions/questions.jsonl    frozen definitions + question_set + corrections (append-only)
  results/forecasts/           append-only forecast records (models and baselines)
  results/resolutions/         append-only outcome records
  results/reports/             generated tables and plots
  prompts/                     prompt templates and baseline rules (versioned files)
  stamps/                      external timestamp proofs
  historical/                  A3 past questions, kept apart from prospective records
  fixtures/                    synthetic TEST- records for tests only
  generator/                   A2: official data → CANDIDATE questions (later)
  sources/                     notes per source: RBI, MOSPI, IMD, Grid-India, CWC… (release calendar, how to read the answer)
research/tests/test_forecast_*.py   forecasting tests (the existing reflica_bench tests stay unchanged)
```

Key rules (details in `PILOT_PROTOCOL.md`):
- Question definitions, forecasts and resolutions are **separate records**. A question never stores its own answer or status.
- Candidates can be edited; a definition is **frozen before its first forecast**. Material defects → documented invalidation + new question ID.
- Forecasts are **append-only**; updates are new records. Times are timezone-aware UTC (IST for display).
- Git commits are supporting evidence; proof = record hashes + external timestamps.
- Every baseline has a calculation rule fixed in advance; an official point forecast is not a probability without a documented conversion.
