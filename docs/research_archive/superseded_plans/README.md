# Superseded and deferred plans

Part of the research archive: `../README.md`. Decision record: `../DECISION_RECORD.md`.

**Archived on:** 15 October 2026, in the repository clean-up.
**Current Minor Project 1 plan:** [`../../../MINOR1_PLAN.md`](../../../MINOR1_PLAN.md) (India Forecast Benchmark). Nothing in this folder is the active plan.

The files are kept for history and reuse. Links *inside* these files may point to their old locations.

| File | What it was | Status |
|---|---|---|
| `NEW_DIRECTION_2026-10-14.md` | 14 Oct direction: long-term vision, Minor 1 = India Forecast Benchmark, Minor 2 = evidence-grounded agent, final = impact-aware forecasting | **Superseded.** The benchmark parts and long-term vision were carried into `MINOR1_PLAN.md` |
| `MINOR1_PLAN_interim_benchmark_2026-10-15.md` | Interim benchmark-only Minor 1 plan (15 Oct), kept word for word | **Superseded (15 Oct, safer merge).** Its benchmark content became Part A of `MINOR1_PLAN.md` |
| `MINOR1_DESIGN_benchmark_2026-10-14.md` | Detailed benchmark design (A2 generator, A3 past-question study, India–West pairs, Hindi-news and human-forecaster options, dashboard views, budget) | **Superseded / incorporated.** Still a useful reference for detail |
| `PROJECT_PLAN_CPI_2026-10-15.md` | 15 Oct plan: Minor 1 = CPI forecasting with evidence-aware revision; Minor 2 = policy probabilities and abstention | **Deferred** (not the active Minor 1) |
| `RESEARCH_REPORT_CPI_2026-10-15.md` | Medium report built on the CPI plan | **Deferred** |
| `REFLICA_INDIA_RESEARCH_PROGRAMME_REPORT_CPI.md` / `.docx` | Full research-programme report for the CPI plan (literature, gap v6, methodology, risks) | **Deferred**. Useful literature and limitations text |
| `TARGET_PROTOCOL_CPI_draft.md` | Draft CPI target and point-in-time protocol | **Deferred.** Known issue: C1 falls inside month m, so the task is a current-month **nowcast**, not one month ahead. Must be fixed before any reuse |
| `cpi_review_paper/REVIEW_PAPER_DRAFT.md` / `.docx` (v0.5) | Review and proposal paper on evidence-aware CPI revision | **Deferred** |

## Note on the CPI evidence-aware revision proposal

The CPI study (a numerical CPI forecast plus LLM-extracted, dated claims plus a pre-registered revision gate, compared with never / always / small-step / text-always updating) is **deferred, not abandoned**. It is a candidate for Minor Project 2 or the final project.

It was deferred on 15 Oct 2026 for four reasons:
- a historical Indian news archive with reliable timestamps has not been found;
- CPI vintages and the 2024 = 100 linking factor are unresolved;
- its novelty narrowed after LiveMacroEval, Forecast-Dojo and the nowcasting literature;
- the benchmark first tests whether LLM forecasting of Indian events is worth improving at all.

The **literature work is preserved** in `../literature/` (`FINAL_TABLE.md`, `VERIFICATION.md`, `LEVEL2_READINGS.md`, `PAPER_REVIEWS.md`, `LITERATURE_MATRIX.md`, `LITERATURE_FORECASTING.md`) and `../research_gaps/CLOSEST_METHODS.md`. They were moved there on 15 Oct 2026; internal paths in the archived plans still name their old `research/forecast/` locations.
