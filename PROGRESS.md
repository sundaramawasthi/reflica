# Reflica — PROGRESS

> **Owner:** Sundram Awasthi · M.Tech CSE (2026–28), GLA University · **Last updated:** 2026-10-17
> **Minor Project 1 title (official, per student, 16 Oct 2026):** *IndiaEconForecast / Reflica India: Hybrid AI Forecasting of Indian Economic and Policy Outcomes*.
> **Research field:** Predictive AI for India's Economy and Public Policy. **Supervisor approval pending.**
> Shortened on 16 Oct 2026 (user's request). The full earlier log, including the old plan-product and old thesis sections, is in git history (commit `43890fe` and earlier).

## Current status (16 Oct 2026)

- **Minor 1 plan:** the old plan documents were removed at the user's request. A new plan will be written later. The direction chosen on 15 Oct is the **safer merge**:
  - Part A: an LLM forecasting benchmark of Indian yes/no events;
  - Part B: numerical CPI forecasting with evidence-aware revision;
  - the two parts are evaluated separately.
- **Research kept:**
  - `docs/research_archive/literature/` (paper tables, verification, full-text readings, reviews);
  - `docs/research_archive/research_gaps/CLOSEST_METHODS.md`;
  - `docs/research_archive/review_paper/` (review paper draft);
  - `research/forecast/RESEARCH_GAP_MATRIX.md`.
- **Code:** Flutter/Firebase app shell only. **No forecasting code, data or experiments.** The old Reflica code and its 203 tests are in branch `archive/old-reflica-2026-10-14`.
- **Firebase (live):** Firestore rules allow owner-only notifications, and everything else is denied. The Realtime Database is locked. Spark (free) plan only.

## Decisions log (condensed)

| Date | Decision |
|---|---|
| 2026-10-13 | M.Tech research direction changed to AI forecasting of Indian events (old plan-graph thesis paused) |
| 2026-10-14 | Old Reflica deleted from the main code and archived (`archive/old-reflica-2026-10-14`, `archive/stage-1-2026-10-14`); stage-1 merge cancelled |
| 2026-10-14 | Firestore rules published (owner-only notifications); Realtime Database locked; Spark review in `docs/FIREBASE_SPARK.md` |
| 2026-10-14 | Part A record formats and decisions D1–D9 in `research/forecast/PILOT_PROTOCOL.md`; first backend milestone in `research/forecast/MILESTONE_1.md` |
| 2026-10-14 | App builds and runs after the clean-up (confirmed on the Mac); homepage rebuilt for forecasting |
| 2026-10-15 | Literature review: about 59 papers checked, 22 read in full or near-full. Corrections recorded in `VERIFICATION.md`. Gap v6 is provisional (`CLOSEST_METHODS.md`). **No novelty claimed** |
| 2026-10-15 | Minor 1 direction: **safer merge** (Part A benchmark + Part B CPI, evaluated separately; all 8 CPI-plan features kept with priorities) |
| 2026-10-16 | Minor 1 title set by the student as official: *IndiaEconForecast / Reflica India: Hybrid AI Forecasting of Indian Economic and Policy Outcomes*. The earlier title (*AI-Powered Research Knowledge Graph and Change Impact Analysis System*) is no longer used |
| 2026-10-16 | Old plan and history `.md` files removed at the user's request; research files kept; READMEs shortened |

## Status update (17 Oct 2026)

- **Steps 1–6 done:** direction, literature review, research gap (v8), proposal, data feasibility, **data collection**.
- **Data:**
  - CPI revised series 2013 – Sep 2026 (613 rows, MoSPI API);
  - first-release calendar for 33 months (Dec 2025, Jan 2024 – Aug 2026);
  - 81 registered documents: all 22 RBI MPC resolutions (Apr 2023 – Oct 2026), 8 Monetary Policy Reports, 2 MPC minutes, the Economic Survey 2025-26, and 14 PIB price-evidence releases.
- **Next:** step 7, claim extraction into `data/processed/claims.csv`.
- **Reports:** `docs/PROJECT_REPORT.md` (step by step), `docs/PROJECT_DOCUMENTATION.md`, `docs/PPT_CONTENT.md`.

| 2026-10-16 – 17 | Data collection: CPI via MoSPI API and press releases; RBI/PIB/MoF documents with verified timestamps; project report and documentation written |

## Rules going forward

- Never claim "first" or "novel" until the literature review supports it.
- No secrets (Firebase service keys, API keys) in client code or the repository.
- No Firestore rule changes without discussion. Stay on the Spark plan.
- Every new UI widget is **width-reactive**, never platform-reactive.

## How to run

```bash
flutter pub get
flutter analyze
flutter run -d chrome
```
