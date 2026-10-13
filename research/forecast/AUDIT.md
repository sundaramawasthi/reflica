# Reflica → forecasting platform: repository audit (Phase 1)

Date: 14 October 2026. Read-only audit; no application code was changed.

> **Snapshot.** This file records the repository as found on 14 October 2026 and is kept unchanged as history. Current architecture and plans: `../../docs/ARCHITECTURE.md`; record formats: `PILOT_PROTOCOL.md`. Corrected since: section 4 says "the git commit time is an independent timestamp"; it is **not** independent proof (see the evidence hierarchy in `docs/ARCHITECTURE.md` section 5), and "read for everyone" is not a decided rule (section 5.1 there). The implementation order has since changed to documentation → Flutter UI → Python backend → connect (December pilot by hand).
Checked on `main` (4d55b8f) and on the unmerged branch `reflica/stage-1-flutter-integration` (ae7084e).

## 1. What is in the repository

### Branches
- `main`: the Flutter app and the `reflica_bench` research workspace.
- `reflica/stage-1-flutter-integration` (9 commits ahead of `main` and contains all of `main`, so a fast-forward merge is possible): adds `research/reflica_service/` (local FastAPI HTTP API, `graph@1` contract, impact preview/decision, LLM text extraction, `regress@1`), Flutter screens that call it, and 7 Flutter test files.
- Working branch `claude/lucid-mendel-zy17b7` = `main` + forecasting documents only.

### Flutter app (`lib/`, `main`)
- **Entry:** `lib/main.dart` initialises Firebase (falls back to demo mode if it fails), enables Firestore offline persistence (unlimited cache), uses `MaterialApp` named routes.
- **Routes:** `/` → `AuthGate` (signed out → `HomeScreen` landing page; signed in → `DashboardScreen`); `/dashboard`, `/new-plan`, `/plans`, `/plan` (with id → `PlanDetailScreen`); `/graph`, `/scenarios`, `/documents`, `/settings` are **placeholders** (`PlaceholderScreen`).
- **Landing page** (`home_screen.dart`): Hero, Living Loop, 7 Input Modes, Audience, Evidence types, CTA/footer. All copy is about plans.
- **Dashboard** (`dashboard_screen.dart`): sidebar (Home, New Plan, My Plans, Knowledge Graph, Scenarios, Documents, Settings + recent plans), top bar (search field, notifications, user menu), Welcome card, Quick input strip, Use cases, Activity table (live from the user's plans), Quick actions, How it works. No hard-coded metric numbers were found.
- **Auth:** `services/auth_service.dart`: Firebase Auth; Google popup on web, `google_sign_in` on Android; demo-mode fallback.
- **Data:** `services/plan_repository.dart` and `services/notification_service.dart`. All data is **per user**: `users/{uid}/plans/{planId}` and `users/{uid}/notifications/{id}`. Models: `models/plan.dart` (Plan, PlanNode with `EvidenceType` fact/observation/prediction/hypothesis/assumption, PlanEdge with kinds dependsOn/blocks/enables/causes/requires/supports), `models/notification.dart`.
- **Mind map:** `widgets/plan/plan_mind_map.dart` (CustomPainter, pan/zoom), `widgets/situation_graph.dart` (landing illustration).
- **Theme / layout:** `theme/app_theme.dart` (`AppColors`, `AppText`), `widgets/responsive.dart` (width-based sizes), `widgets/brand_mark.dart`.
- **Notifications:** written by the client on plan create/update/delete only. **No background jobs** exist anywhere.

### Firebase
- Project `reflica-593b4`. Configured for **web and Android** only (iOS/macOS/etc. throw `UnsupportedError`).
- Packages: `firebase_core`, `firebase_auth`, `cloud_firestore`, `firebase_analytics`, `firebase_ai`. **`firebase_analytics` and `firebase_ai` are not imported anywhere in `lib/`.**
- `android/app/google-services.json` and `lib/firebase_options.dart` are committed. These hold client identifiers, which is normal for Firebase; protection comes from security rules.
- **No `firestore.rules` or `firebase.json` in the repository.** The live rules exist only in the Firebase console and must be checked before any new collection is added.

### Python research (`research/`)
- `reflica_bench/`: benchmark v0.2.0 (63 scenarios, 7 categories), schema with `Provenance` and `Determinability`, ground truth, baselines B3/B4a/B4b, B5 engine, LLM pilot in `experiments/rn_pilot/`.
- `forecast/`: new, documents only (`README.md`, this audit).

### Tests and build status (run 14 October 2026 in the cloud container)
| Suite | Result |
|---|---|
| `main` Python (`research/`, `pytest`) | **203 passed** |
| stage-1 Python (`research/`, `pytest`, with `service` extra) | **1030 passed, 4 skipped** (1 file skipped because `httpx` is not installed; 3 skips are intentional) |
| Flutter tests / build | **Not run**: no Flutter SDK in the cloud container. Must be run on the Mac (`flutter analyze`, `flutter test`). On `main` the only Flutter test is a placeholder smoke test. |

Known issues: no Flutter tests on `main` cover real screens; security rules are not versioned; two unused Firebase packages.

## 2. Feature-by-feature table

A = reuse · B = adapt · C = hide from main navigation · D = preserve for future work · E = remove only after approval

| Feature / file | Action | Reason |
|---|---|---|
| Firebase init + offline persistence (`main.dart`) | A | Works; forecasts can be cached offline the same way. |
| Auth (`auth_service.dart`, `auth_gate.dart`, sign-in/out, demo mode) | A | Same accounts; forecasts can be public read, sign-in for personal features. |
| Theme, `AppText`, `BrandMark`, `responsive.dart` | A | Visual identity and width-based layout carry over. |
| Dashboard shell: sidebar, top bar, user menu, notifications bell | B | Keep the frame; change sidebar items and the search target. |
| Dashboard body: Welcome card, Use cases, How it works, Quick actions | B | Rewrite content for forecasting (welcome, summary cards, upcoming questions). |
| Activity table | B | Same pattern, but list recent forecasts/resolutions instead of plans. |
| Landing page sections (Hero, Living Loop, Audience, Evidence, CTA) | B | Rewrite copy and visuals for forecasting; keep the section structure. |
| Input modes section, Quick input strip | C | Plan input, not part of the forecasting flow. |
| New Plan wizard (`new_plan_flow.dart`), My Plans, Plan editor/detail | C | Not in the main forecasting workflow. Keep routes working, reachable from a "Plans (legacy)" link or settings. |
| `PlanRepository`, `users/{uid}/plans` data | D | Real user data; no migration or deletion. |
| `NotificationService` | B (later) | Could carry forecast-deadline/resolution notices; it is per-user and client-written today. |
| Mind map (`plan_mind_map.dart`), `situation_graph.dart` | D | Candidate base for the Final-project impact map; evaluate then. |
| Placeholder screens `/graph`, `/scenarios`, `/documents`, `/settings` | C (Settings: B) | Remove from navigation; Settings can later hold account/model preferences. |
| `reflica_bench` (benchmark, ground truth, baselines, B5), rn_pilot | D | Old research, paused, kept intact with its tests. |
| stage-1 `reflica_service` (FastAPI, graph@1, impact, extraction, regress) | D now, B later | The natural home for server-side model calls and for impact analysis in the Final project. |
| `firebase_ai`, `firebase_analytics` packages | E | Unused in `lib/`. `firebase_ai` must not be used for privileged forecasting calls. Remove only if you approve. |

Nothing is proposed for deletion now.

## 3. What the old research can give the new work

| Old component | Reusable for | Verdict |
|---|---|---|
| `Provenance` and typed evidence (`EvidenceType`: fact/observation/prediction/…) | Recording forecast evidence: source, date, type | Reuse the **idea**; forecasting needs its own fields (URL, publication date, retrieval time). |
| `Determinability` / Category 7 "unknown" | The abstention concept for Minor 2 | Concept only. Abstention must be tested on forecasting data. |
| Frozen manifest + SHA-256 fingerprints | Freezing the question set and forecast files (proof nothing changed later) | **Directly reusable pattern.** |
| Linter, loader, evaluator, pydantic schemas, pytest layout | Question validation, schema checks, scoring harness | Reuse the pattern; new code in `forecast/`. |
| rn_pilot harness (config freezing, raw JSONL logs, failure logs, repeatability) | The forecasting runner (logging every call, failures, config versions) | **Strongly reusable pattern.** |
| Leakage checker (`rn.py`) | Checking that retrieved news is dated before the forecast deadline | Same idea, different check. |
| B3/B5 propagation, `graph@1` impact preview | Final project: event → consequence graph | Deterministic only. **Cannot propagate probabilities.** A separate probability layer is needed and must be tested. |

All 203 old tests stay as they are. Forecasting tests go in new files (`research/tests/test_forecast_*.py`, or a separate test folder), and old benchmark results stay separate from the forecasting benchmark.

## 4. Proposed architecture (for approval)

```
Python pipeline (your Mac, later scheduled)          Firestore (display copy)        Flutter app
 research/forecast/                                   questions/{qid}        read-only  Home, Questions,
  questions/*.json  ──validate──▶ freeze (hash)  ───▶ forecasts/{fid}      ◀───────────  Forecasts, Scoreboard
  runner  ──LLM APIs (keys in env vars)──▶            resolutions/{qid}
  results/forecasts/*.jsonl (append-only, in git)     scores/{summaryId}
  scoring ──▶ results/reports
```

- **Source of truth = the Python pipeline's append-only files committed to git.** The git commit time is an independent timestamp. Firestore is the display copy the app reads.
- **New top-level collections**, separate from `users/{uid}/…`: `questions`, `forecasts`, `resolutions`, `scores`. They are global, not per user. Existing data is untouched; no migration.
- **Writes only from the server side** (Python with the Firebase Admin SDK and a service-account key kept outside the repository). **Security rules:** read for everyone (or signed-in users); `create/update/delete` denied to clients. Forecast documents are never updated: a new forecast is a new document with `version` and `supersedes`.
- **Model API keys** live only in environment variables on the machine that runs the pipeline. Never in Flutter, never in git.
- **Scheduled jobs:** not needed for the pilot. Run by hand first; later choose cron on your Mac, GitHub Actions or Cloud Functions (needs the Blaze plan).
- Alternative for later: extend the stage-1 `reflica_service` as the forecasting API. This is not needed for Phases 2–5.

## 5. Implementation sequence

| Phase | Goal | Files (you write them) | Data-model effect | Tests |
|---|---|---|---|---|
| 1 | Audit + plan | this file, `NEW_DIRECTION.md` | none | none |
| 2 | Forecasting homepage + navigation | new `lib/screens/forecast_home_screen.dart`, `lib/widgets/forecast/*`; edit `dashboard_sidebar.dart`, `main.dart` routes, landing copy | none; empty states only ("No resolved forecasts yet") | widget tests: home renders empty state; old `/plans` route still opens |
| 3 | Question catalogue | `research/forecast/` question schema + validator (Python); `lib/models/forecast_question.dart`, `lib/services/forecast_repository.dart`, questions list/detail screens | new `questions` collection + rules | pytest for validator (deadline before resolution date, rule present…); Flutter JSON round-trip test |
| 4 | Forecast records | runner (Python), publisher to Firestore, `lib/models/forecast.dart`, forecasts view | `forecasts` collection, create-only | pytest: append-only, config hash, cache; rules test: client update denied |
| 5 | Evaluation | resolver + Brier/calibration scorer (Python), scoreboard screen | `resolutions`, `scores` | pytest with hand-computed Brier values; UI shows nothing for unresolved questions |
| 6 | Advanced research | generator, news retrieval, historical runs, India vs West | extra fields only | separate test files per component |

**Recommended first concrete step:** do Phase 3's Python part (schema + validator + one question JSON) and get **one question end to end in Python** before any Flutter work. Phase 2 (homepage) can run in parallel but should show only empty states until real data exists.

## 6. Risks

1. **Two app lines.** `main` and stage-1 differ by 91 files. Decide whether to merge stage-1 into the working branch before Phase 2, or Flutter changes will conflict later.
2. **Unknown security rules.** If the current rules allow any signed-in user to write anywhere, new public collections could be edited by anyone. Export and version the rules (`firestore.rules`) first.
3. **No Flutter SDK in the cloud.** Flutter changes must be built and tested on your Mac; Claude can only review them here.
4. **Public read costs.** Global collections read by many users cost Firestore reads; keep summary documents small.
5. **Leakage and integrity.** Forecasts must be committed and published before the deadline; news must be dated before it. These are checked by tests, not by trust.
6. **Scope creep.** Phase 2 must not show fabricated numbers; sample data only in a clearly labelled debug preview.

## 7. Decisions needed from you
1. Merge `reflica/stage-1-flutter-integration` into the working branch first? (Recommended: yes. It contains `main`, so it is a clean fast-forward.)
2. Approve the data approach: git files are the source of truth, Firestore is the read-only display copy, and the server writes with the Admin SDK.
3. Forecast pages public, or signed-in only?
4. Start with Phase 3-Python (one question end to end) or Phase 2 (homepage)?
5. Keep or remove the unused `firebase_ai` / `firebase_analytics` packages?
