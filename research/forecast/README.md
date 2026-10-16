# forecast: forecasting workstream

Part A (LLM benchmark) record formats and milestone, plus the research-gap matrix. No code yet; supervisor approval pending.

| Document | Purpose |
|---|---|
| `PILOT_PROTOCOL.md` | **Single source** for Part A record formats, hashing, timestamps, baselines and the manual December 2026 pilot |
| `MILESTONE_1.md` | First backend milestone: minimum Python files and tests; first question |
| `RESEARCH_GAP_MATRIX.md` | Literature-review matrix (closest work, contradictory evidence, candidate gaps) |
| `../../docs/research_archive/` | Literature record, research gaps, review paper |

## Layout (proposed; folders are created when first needed; the user writes the code)

```
research/forecast/
  questions/candidates/        editable drafts during review
  questions/questions.jsonl    frozen definitions + question_set + corrections (append-only)
  results/forecasts/           append-only forecast records (models and baselines)
  results/resolutions/         append-only outcome records
  results/reports/             generated tables and plots
  prompts/                     prompt templates and baseline rules (versioned files)
  stamps/                      external timestamp evidence (only if a service is adopted, D7)
  historical/                  A3 past questions, kept apart from prospective records
  fixtures/                    synthetic TEST- records for tests only
  generator/                   A2: official data → CANDIDATE questions (later)
  sources/                     notes per source: RBI, MOSPI, IMD, Grid-India, CWC… (release calendar, how to read the answer)
research/tests/test_forecast_*.py   forecasting tests (the old reflica_bench tests were archived with it)
```

Key rules (details in `PILOT_PROTOCOL.md`):
- Question definitions, forecasts and resolutions are **separate records**. A question never stores its own answer or status.
- Candidates can be edited; a definition is **frozen before its first forecast**. Material defects → documented invalidation + new question ID.
- Forecasts are **append-only**; updates are new records. Times are timezone-aware UTC (IST for display).
- Evidence hierarchy: the record itself → its hash and the frozen question-set manifest → an external timestamp (only after evaluation and adoption, D7) → Git history as supporting history only.
- Every baseline has a calculation rule fixed in advance; an official point forecast is not a probability without a documented conversion.
