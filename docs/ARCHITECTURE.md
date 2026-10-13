# Reflica architecture: current state and forecasting plan

Date: 14 October 2026. Status: current-state facts checked in the repository; forward-looking parts are **proposals awaiting the user's approval**. M.Tech guide approval of the research direction is pending.
Authority: `../NEW_DIRECTION.md`. Dated audit snapshot with full details: `../research/forecast/AUDIT.md`.

## 1. Implementation order

**Documentation → Flutter UI → Python backend → connect the UI to real data.**
Exception: the December 2026 pilot is collected by hand in the format in `research/forecast/PILOT_PROTOCOL.md`.

| Phase | Content | Gate |
|---|---|---|
| 1 | Documentation (this set) | user approval |
| 2 | Flutter UI with honest empty states / labelled demo data (`UI_SPEC.md`) | stage-1 branch integration settled; user review after each UI stage |
| — | December pilot, manual (`PILOT_PROTOCOL.md`) | question set frozen before any forecast |
| 3 | Python backend: validation → storage → runner → resolution → scoring → evaluation (`MILESTONE_1.md`) | user review at each component |
| 4 | Connect UI to real data (Firestore display layer) | security rules versioned and reviewed |
| 5+ | A2 generator, A3 past-question study, news experiments, India vs Western | separate, tested components |

## 2. Current Flutter app (checked on `main`, 14 Oct 2026)

- **Entry:** `lib/main.dart` initialises Firebase (falling back to demo mode on failure), turns on Firestore offline persistence and uses `MaterialApp` named routes.
- **Routes:** `/` → `AuthGate` (signed out → `HomeScreen` landing; signed in → `DashboardScreen`); `/dashboard`, `/new-plan`, `/plans`, `/plan`; placeholders `/graph`, `/scenarios`, `/documents`, `/settings`.
- **Reusable as-is:** `AuthService` (Google sign-in, demo mode), `AppColors`/`AppText`, `BrandMark`, `responsive.dart`, the dashboard frame (sidebar, top bar, notifications bell, user menu).
- **Plan system (legacy):** `models/plan.dart`, `services/plan_repository.dart`, `new_plan_flow.dart`, `plans_screen.dart`, `plan_detail_screen.dart`, `widgets/plan/plan_mind_map.dart`.
- **Notifications:** `services/notification_service.dart`, client-written on plan changes only. There are no background jobs.
- **Branch `reflica/stage-1-flutter-integration`** (not merged): adds `research/reflica_service/` (localhost FastAPI, `graph@1`, impact preview, LLM extraction), `lib/services/reflica_api.dart`, graph widgets, the `http` package and 7 Flutter test files. The trial merge had one conflict, in `PROGRESS.md` only. A backup branch exists.

## 3. Treatment of legacy features

| Feature | Treatment |
|---|---|
| Auth, Firebase init, theme, layout, top bar | Reuse |
| Dashboard body, landing copy, activity list, notifications, Settings | Adapt for forecasting |
| New Plan wizard, My Plans, plan editor, input modes, placeholders | **Hide** from main navigation in Phase 2; routes keep working; reachable via Settings → Legacy Plans |
| `users/{uid}/plans`, `users/{uid}/notifications` data | Preserve; no migration |
| Mind map, `situation_graph.dart`, stage-1 impact service | Preserve; evaluate for the Final-project impact map |
| `reflica_bench` (benchmark v0.2.0, baselines, B5), rn_pilot | Preserve; paused; its 203 tests stay green |
| `firebase_ai`, `firebase_analytics` (unused in `lib/`) | Keep for now; reassess in dependency cleanup |

Nothing is deleted without the user's approval.

## 4. Firebase today

- Project `reflica-593b4`; web and Android only. Products: Auth, Firestore (offline persistence), plus the unused Analytics and AI packages.
- Collections: `users/{uid}/plans`, `users/{uid}/notifications` (per user).
- **Security rules are not in the repository.** They must be exported from the console and versioned (`firestore.rules`, `firebase.json`) before any forecasting collection is written.

## 5. Forecasting data architecture (provisionally approved)

```
Append-only research files (git + external timestamps)  ──import/verify──▶  Python backend
   research/forecast/{questions,results}/*.jsonl                                │ Admin SDK (server only)
                                                                                ▼
Flutter app  ◀──read only──  Firestore display layer: questions / forecasts / resolutions / scores
```

- **Source of truth:** the versioned, append-only research files (`PILOT_PROTOCOL.md`). Firestore is the app-facing display copy.
- **Public vs private:** approved questions, published forecasts, resolved outcomes and aggregate evaluation results are publicly readable where practical. Personal account data and settings stay under `users/{uid}` and remain private.
- **Clients never write research records.** Rules: read allowed; `create`/`update`/`delete` denied for forecasting collections. Only the backend writes, using the Admin SDK.
- **Immutability:** forecast documents are created once. Changes are new documents (`supersedes`) or correction records, never updates.
- **Collections are not created yet.** Names and rules are proposed and will be discussed before Phase 4.

## 6. Backend (Phase 3, proposal)

- Python package under `research/forecast/`, kept separate from `reflica_bench`. Concerns: question validation · record storage (append-only) · model runner (cache, cost log) · evidence retrieval · resolution · scoring and evaluation · later impact analysis.
- Model calls run only server-side. API keys and the Firebase service-account key live in environment variables or a local secrets file outside the repository; never in Flutter, never in git.
- First runs are by hand. Scheduling (local cron, GitHub Actions or Cloud Functions on the Blaze plan) is decided later. Jobs never silently replace forecasts or historical scores.
- The stage-1 FastAPI service is a candidate home for an HTTP API later. It is not required for Phases 3–4.

## 7. Security

- No secrets in client code or git. Firebase client config (`firebase_options.dart`, `google-services.json`) is not secret; protection comes from rules.
- Rules are versioned and reviewed before the first write. App Check is considered when the data is public.
- External timestamping sends only hashes.

## 8. Research integrity, evaluation and testing

- Integrity rules: `NEW_DIRECTION.md` section 8. Record and pilot rules (candidates editable, definitions frozen before the first forecast, no backdating, late forecasts excluded, corrections as new records, baselines with rules fixed in advance, India–Western pairs as matched comparisons, synthetic and historical records kept apart): `PILOT_PROTOCOL.md`.
- Evaluation: Brier on `yes`/`no` only; calibration with sample size and uncertainty; baselines (base rate, persistence, official RBI/IMD forecasts, each with a conversion rule fixed in advance; a point forecast is not a probability); India vs Western matched pairs; A3 past-question results reported separately.
- Testing:
  - **Python:** `reflica_bench` tests unchanged (203); new `research/tests/test_forecast_*.py` (schema, validator, hashing, append-only store, timeliness rule, Brier hand values, end-to-end with `TEST-` fixtures, pilot-file import without changes).
  - **Flutter:** `flutter analyze` and `flutter test` on the Mac. Screen empty states, navigation (including legacy routes), demo-flag behaviour and model JSON round-trip (`UI_SPEC.md` section 6). The cloud environment has no Flutter SDK.

## 9. Risks

1. Stage-1 and `main` diverge (90 files). Integrate before Phase 2, or the UI work will conflict.
2. Unknown live security rules.
3. The December deadline: the protocol and question drafts must be ready in November.
4. Manual collection errors (wrong times, edited lines). These are mitigated by hashes, same-day stamps and the importer's checks.
5. Public read costs once the app is live.
6. Fabricated-looking UI numbers. Prevented by the demo flag and banner.

## 10. Open decisions

1. Approve this documentation set and `PILOT_PROTOCOL.md`.
2. Merge stage-1 into the working branch now (backup exists; one `PROGRESS.md` conflict)?
3. Approve the UI navigation and the "Legacy Plans in Settings" placement.
4. Choose the pilot models (2–3) and the monthly API budget (November).
5. Export the current Firestore rules from the console (needed before Phase 4).
