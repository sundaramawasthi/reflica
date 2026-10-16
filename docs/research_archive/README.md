# Research archive

Created 15 October 2026 in the documentation reset. It preserves research work; **nothing here is the active Minor 1 plan**.

- **Active plan:** `../../MINOR1_PLAN.md` (interim; to be replaced by the user's final plan).
- **Titles, fields and decisions:** `DECISION_RECORD.md`.

| Folder | Contents |
|---|---|
| `literature/` | Literature tables, the bibliography of record, full-text readings and paper reviews |
| `research_gaps/` | Closest-method comparison and gap v6 (deferred CPI study) |
| `superseded_plans/` | Superseded and deferred plans and reports (see its README) |
| `project_history/` | Dated audit snapshot and the cancelled stage-1 checklist |

**Bibliography of record:** `literature/VERIFICATION.md`. It records the verified citations, reading levels (Level 1 bibliographic / Level 2 content) and corrections. No separate bibliography file was created, to avoid duplicate, diverging copies.

## Preservation inventory (all Markdown files, 15 Oct 2026)

**Dispositions:** Retained (active) · Archived (moved here, unchanged except notes and links) · Redundant (safe to remove; none removed) · Awaiting user.

| File | Contents | Disposition | Location now |
|---|---|---|---|
| `MINOR1_PLAN.md` | Interim Minor 1 plan (benchmark) | **Retained**; to be replaced by the user's plan | repo root |
| `README.md` | Project overview | **Retained** (pointers updated) | repo root |
| `PROGRESS.md` | Dated progress and decision log (all history) | **Retained** (header updated; log rows unchanged) | repo root |
| `docs/ARCHITECTURE.md` | App and data architecture | **Retained** (links updated) | docs/ |
| `docs/UI_SPEC.md` | Forecasting UI spec | **Retained** | docs/ |
| `docs/FIREBASE_SPARK.md` | Firebase security review (in effect) | **Retained** | docs/ |
| `docs/CLEANUP_EDITS.md` | 14 Oct app clean-up edits; section C (pyproject update) still pending | **Awaiting user**: active or history? | docs/ |
| `research/README.md`, `research/forecast/README.md` | Workstream readmes | **Retained** (updated) | research/ |
| `research/forecast/PILOT_PROTOCOL.md` | Record formats, decisions D1–D9, December pilot | **Retained** (technical; benchmark) | research/forecast/ |
| `research/forecast/MILESTONE_1.md` | First backend milestone | **Retained** | research/forecast/ |
| `FINAL_TABLE.md` | 46-row paper table | **Archived** | `literature/` |
| `VERIFICATION.md` | Citation verification, reading levels, corrections | **Archived** (bibliography of record) | `literature/` |
| `LEVEL2_READINGS.md` | Full-text readings (rounds 1–7), gap v2–v5 | **Archived** | `literature/` |
| `LITERATURE_FORECASTING.md` | 13 Oct 21-paper analysis and gap checklist | **Archived** | `literature/` |
| `LITERATURE_MATRIX.md` | First-pass matrix (CPI) | **Archived** | `literature/` |
| `PAPER_REVIEWS.md` | Simple-language paper reviews | **Archived** | `literature/` |
| `CLOSEST_METHODS.md` | Step-1 comparison, gap v6 | **Archived** | `research_gaps/` |
| `AUDIT.md` → `AUDIT_2026-10-14.md` | Repository audit snapshot | **Archived** | `project_history/` |
| `docs/STAGE1_MERGE_CHECKLIST.md` → `…_cancelled.md` | Cancelled merge checklist | **Archived** | `project_history/` |
| `NEW_DIRECTION_2026-10-14.md` | 14 Oct direction, field/subfield, publication plan | **Archived** | `superseded_plans/` |
| `MINOR1_DESIGN_benchmark_2026-10-14.md` | Detailed benchmark design | **Archived** (reference) | `superseded_plans/` |
| `PROJECT_PLAN_CPI_2026-10-15.md` | CPI plan (8 features, Minor 2, thesis) | **Archived, deferred** | `superseded_plans/` |
| `RESEARCH_REPORT_CPI_2026-10-15.md` | CPI medium report | **Archived, deferred** | `superseded_plans/` |
| `REFLICA_INDIA_RESEARCH_PROGRAMME_REPORT_CPI.md` (+ `.docx`) | Full CPI programme report | **Archived, deferred** | `superseded_plans/` |
| `TARGET_PROTOCOL_CPI_draft.md` | CPI target protocol (has a known nowcast issue) | **Archived, deferred** | `superseded_plans/` |
| `cpi_review_paper/REVIEW_PAPER_DRAFT.md` (+ `.docx`) | CPI review paper v0.5 (43 references) | **Archived, deferred** | `superseded_plans/cpi_review_paper/` |
| `MINOR1_PLAN.md` (interim benchmark version) → `MINOR1_PLAN_interim_benchmark_2026-10-15.md` | Interim benchmark-only plan, replaced by the safer-merge plan | **Archived** (copied before the replacement) | `superseded_plans/` |
| `superseded_plans/README.md` | Archive note: CPI study deferred, not abandoned | Archived (new) | `superseded_plans/` |
| `ios/.../LaunchImage.imageset/README.md` | Flutter template asset note | **Retained** (not research) | ios/ |
| `research/.pytest_cache/README.md` | Auto-generated cache (git-ignored) | **Redundant**: not research; left untouched | research/ |

**Non-Markdown assets (untouched):**
- `research/pyproject.toml` and `pytest.ini`: these still describe the old `reflica_bench` package. **Awaiting user** decision (`CLEANUP_EDITS.md` §C).
- `firestore.rules`, `database.rules.json`, `docs/rules-tests/`, `lib/`, `test/`.
- The `.docx` copies above (moved with their `.md` files).

**No datasets, schemas, experiment results or forecasting code exist in the repository.** The old benchmark code, scenarios and 203 tests are preserved in branch `archive/old-reflica-2026-10-14`.

**Outside the repository (not preserved here):** the user's uploads, such as `Research_Work_paper.docx` (22-paper notes) and the paper PDFs read in full. Copying them in is a user decision.
