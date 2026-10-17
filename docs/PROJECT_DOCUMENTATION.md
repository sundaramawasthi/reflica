# Reflica: Project Documentation

> **Project:** IndiaEconForecast / Reflica India: Hybrid AI Forecasting of Indian Economic and Policy Outcomes
> **Owner:** Sundram Awasthi · M.Tech CSE (2026–28), GLA University · **Updated:** 17 Oct 2026
> **Repository:** `sundaramawasthi/reflica`, branch `claude/lucid-mendel-zy17b7` (public; never commit secrets)

## 1. What Reflica is
A research platform that forecasts Indian economic and policy outcomes with AI, and tests the forecasts fairly. It has two separately evaluated parts:
- **Part A: LLM forecasting benchmark.** LLMs answer yes/no questions about Indian events and are scored with the Brier score and calibration.
- **Part B: CPI forecasting with evidence-aware revision.** A numerical model forecasts headline CPI (y-o-y), and dated, source-linked claims from official documents feed a **bounded revision rule**.

## 2. Repository layout
```
reflica/
├── README.md, PROGRESS.md        overview and status log
├── RESEARCH_PROPOSAL.md          full proposal (Minor 1 + Minor 2)
├── docs/
│   ├── PROJECT_REPORT.md         step-by-step report of the work done
│   ├── PROJECT_DOCUMENTATION.md  this file
│   ├── PPT_CONTENT.md            presentation content
│   ├── ARCHITECTURE.md, UI_SPEC.md, FIREBASE_SPARK.md   app design and security
│   └── research_archive/         literature, research gaps, review paper, old plans
├── research/forecast/            gap matrix, literature records, data feasibility,
│                                 Part A protocol (PILOT_PROTOCOL.md, MILESTONE_1.md)
├── data/                         datasets (see §4)
├── lib/, test/                   Flutter app
└── firestore.rules, database.rules.json
```

## 3. System architecture (planned)
```
Official sources (MoSPI, RBI, PIB, MoF)
        │  saved with publication time
        ▼
Timestamped data store (data/raw + data/processed)
        ├──► numerical CPI models (naive, SARIMA, XGBoost)
        └──► claim extraction (LLM extracts quote, topic, direction, date, source)
                      │
                      ▼
           bounded revision rule ─► forecast log (keep / revise + reason)
                      │
                      ▼
        walk-forward evaluation ─► dashboard (Flutter + Firebase)
```

**The 8 features and their priority**
1. Numerical engine (core)
2. Timestamped data (core)
3. Evidence / claims (core)
4. Uncertainty intervals (core, simplified)
5. Bounded revision (minimal version first)
6. What-if scenarios (optional)
7. Evaluation (core)
8. Minimal dashboard (core)

## 4. Data
**Main rule:** a value or document is used only after its actual publication time.

| Path | Content |
|---|---|
| `data/processed/cpi_series_revised_2026-10-16.csv` | Revised CPI, 2013 – Sep 2026 (training only) |
| `data/processed/cpi_release_calendar.csv` | First-release CPI with release date and time and link (testing) |
| `data/processed/cpi_vintage_*.csv`, `cpi_revisions.csv` | Release versions and revisions |
| `data/processed/source_documents.csv` | One row per document: ID, source, title, published_at, URL, type, path, timestamp confidence, review status |
| `data/processed/claims.csv` | Extracted claims (empty until step 7) |
| `data/raw/cpi_releases/`, `cpi_api/` | Original CPI press releases, annexures, API pages |
| `data/raw/rbi_documents/` | MPC resolutions, minutes, reports, transcripts (PDF + text) |
| `data/raw/pib_documents/` | PIB releases (PDF + text) |
| `data/raw/wpi_releases/`, `secondary_notes/` | WPI release; secondary notes (not for forecasting) |
| `data/scripts/fetch_cpi_api.py` | MoSPI API downloader; run on the Mac with `MOSPI_USER` and `MOSPI_PASS` set |

**Document ID format:** `SOURCE_YEAR_NNN`, for example `RBI_2024_027` or `PIB_2025_005`.
**Timestamp confidence:** `verified` (date and time printed), `date-only`, or `uncertain`.

## 5. Methods (planned)
- **Target:** All-India CPI-C headline inflation, y-o-y, with the horizon fixed in the protocol (step 8).
- **Numerical baselines:** naive, SARIMA, XGBoost, simple combination.
- **Text baselines:** sentiment index, word-frequency index (built on pre-test data only).
- **Our method:** claim-level evidence plus a bounded revision rule, with thresholds tuned on validation data only.
- **Comparison policies:** never update, always update, small step, text-always.
- **Evaluation:** walk-forward with first-release values. MAE, RMSE, Diebold–Mariano (HLN) test, interval coverage. Part A: Brier score and calibration.

## 6. Technology stack
- **Research:** Python (pandas, statsmodels, scikit-learn, XGBoost) and an LLM API for claim extraction.
- **App:** Flutter (web and Android), Firebase Auth and Cloud Firestore on the free Spark plan. The Firestore rules allow owner-only notifications; the Realtime Database is locked.
- **Tools:** Git / GitHub; `pdftotext` / `pypdf` for document text.

## 7. How to run
```bash
# App
flutter pub get && flutter analyze && flutter run -d chrome

# CPI data (on your own computer)
export MOSPI_USER=...; export MOSPI_PASS=...   # never commit these
python3 data/scripts/fetch_cpi_api.py --base-year 2012 --level group --from-year 2013 --to-year 2025
python3 data/scripts/fetch_cpi_api.py --base-year 2024 --from-year 2025 --to-year 2026
```

## 8. Rules
- Never claim "first" or "novel" until the literature supports it.
- Never use information before its publication time.
- No secrets, personal documents or copyrighted papers in the repo (use `docs/local_private/`, which is git-ignored).
- No Firestore rule changes without discussion; stay on the Spark plan.
- Report all results honestly, including when the method does not help.

## 9. Status
- **Done:** direction, literature review, research gap, proposal, data feasibility, data collection.
- **Next:** claim extraction (step 7), then freezing the protocol, the experiments, and the dashboard and report.
- **Details:** `docs/PROJECT_REPORT.md`.
