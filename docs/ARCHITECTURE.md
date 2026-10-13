# Reflica architecture: current state and forecasting plan

Date: 14 October 2026. Status: current-state facts checked in the repository; forward-looking parts are **proposals awaiting the user's approval**. M.Tech guide approval of the research direction is pending.
Authority: `../NEW_DIRECTION.md`. Dated audit snapshot with full details: `../research/forecast/AUDIT.md`.

## 1. Implementation order

**Documentation → Flutter UI → Python backend → connect the UI to real data.**
Exception: the December 2026 pilot is collected by hand in the format in `research/forecast/PILOT_PROTOCOL.md`.

| Phase | Content | Gate |
|---|---|---|
| 1 | Documentation (this set) | user approval |
| 2 | Flutter UI with honest empty states / labelled demo data (`UI_SPEC.md`); **no Firestore collections or published records** | stage-1 merge reviewed and settled (`STAGE1_MERGE_CHECKLIST.md`); user review after each UI stage |
| — | December pilot, manual (`PILOT_PROTOCOL.md`) | question set frozen before any forecast |
| 3 | Python backend: validation → storage → runner → resolution → scoring → evaluation (`MILESTONE_1.md`) | user review at each component |
| 4 | Connect UI to real data (Firestore display layer) | section 5.1 decided; rules versioned and emulator-tested |
| 5+ | A2 generator, A3 past-question study, news experiments, India vs Western | separate, tested components |

## 2. Current Flutter app (checked on `main`, 14 Oct 2026)

- **Entry:** `lib/main.dart` initialises Firebase (falling back to demo mode on failure), turns on Firestore offline persistence and uses `MaterialApp` named routes.
- **Routes:** `/` → `AuthGate` (signed out → `HomeScreen` landing; signed in → `DashboardScreen`); `/dashboard`, `/new-plan`, `/plans`, `/plan`; placeholders `/graph`, `/scenarios`, `/documents`, `/settings`.
- **Reusable as-is:** `AuthService` (Google sign-in, demo mode), `AppColors`/`AppText`, `BrandMark`, `responsive.dart`, the dashboard frame (sidebar, top bar, notifications bell, user menu).
- **Plan system (legacy):** `models/plan.dart`, `services/plan_repository.dart`, `new_plan_flow.dart`, `plans_screen.dart`, `plan_detail_screen.dart`, `widgets/plan/plan_mind_map.dart`.
- **Notifications:** `services/notification_service.dart`, client-written on plan changes only. There are no background jobs.
- **Branch `reflica/stage-1-flutter-integration`** (not merged): adds `research/reflica_service/` (localhost FastAPI, `graph@1`, impact preview, LLM extraction), `lib/services/reflica_api.dart`, graph widgets, the `http` package and 6 new Flutter test files (one is a live test, skipped by default); 91 files differ from `main` in total. Trial merges (scratch copies, cancelled), checked again on 14 Oct: at `43a35bf` and `1182570` → **1 conflict** (`PROGRESS.md`); at `90ae02a` and later → **3 conflicts** (`PROGRESS.md`, `README.md`, `research/README.md`), because both READMEs were edited on our side in `90ae02a`. All are documentation; no code conflicts. Backup branch `backup/lucid-mendel-pre-stage1-2026-10-14` points to `43a35bf`, older than the current head. A fresh backup is required before merging (`STAGE1_MERGE_CHECKLIST.md`).

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

## 5. Forecasting data architecture (provisionally approved; Firestore parts not yet decided)

```
Append-only research files (JSONL)  ──import/verify──▶  Python backend  ──derive──▶  score reports
   research/forecast/{questions,results}/*.jsonl              │ (server credentials only)
                                                              ▼
Flutter app  ◀──read──  Firestore display layer (proposed, not created): questions / forecasts / resolutions / scores
```

**Evidence hierarchy** (what each kind of evidence shows):
1. **Primary record:** the immutable forecast JSONL record (forecast timestamp, model and version, question ID, probability, configuration hash, evidence cutoff, `timing_status`).
2. **Integrity evidence:** the record hash and the frozen question-set manifest (`question_set` record).
3. **Additional timing evidence:** an independently verifiable external timestamp, **only once the method has been evaluated and adopted** (D7). Until then no record is described as independently time-verified.
4. **Supporting history:** Git commits and repository history. Useful for versioning and spotting changes, but **not** independent proof that a forecast existed before the outcome was known.

- **Raw records vs derived reports:** scores, leaderboards and reports are always **recalculated** from the frozen records by code. They are never edited by hand, and are stored apart (`results/reports/`, later `scores` in Firestore).
- **Immutability:** forecast records are created once. Changes are new records (`supersedes`) or correction records, never updates.
- **Firestore is a display copy only** and is **not created yet**. Collection names are candidates.

### 5.1 Firestore security: decisions required before Phase 4 (nothing is defaulted)

| Question | Options | Status |
|---|---|---|
| May **unauthenticated** visitors read questions, published forecasts, resolutions and aggregate scores? | public read · signed-in read only | **undecided** |
| Who may **publish or resolve** official records? | only the trusted server (proposed) | proposed; **clients must never create, modify or delete official records** |
| Where are **server credentials** kept and how are they restricted? | service-account key outside Flutter and Git (environment or secret store), least-privilege role, rotation plan | to specify |
| How are the **rules tested**? | Firebase emulator tests proving clients cannot create, update or delete forecasting documents, and that `users/{uid}` stays private | to specify |
| App Check for public data? | evaluate at Phase 4 | open |

Personal account data and settings stay under `users/{uid}` and remain private in every option. The current live rules must be exported and versioned first (they are not in the repo).

## 6. Backend (Phase 3, proposal)

- Python package inside `research/forecast/`: code only in `research/forecast/pipeline/`, data in the sibling folders (decision D8); kept separate from `reflica_bench`. Concerns: question validation · record storage (append-only) · model runner (cache, cost log) · evidence retrieval · resolution · scoring and evaluation · later impact analysis.
- Model calls run only server-side. API keys and the Firebase service-account key live in environment variables or a local secrets file outside the repository; never in Flutter, never in git.
- First runs are by hand. Scheduling (local cron, GitHub Actions or Cloud Functions on the Blaze plan) is decided later. Jobs never silently replace forecasts or historical scores.
- The stage-1 FastAPI service is a candidate home for an HTTP API later. It is not required for Phases 3–4.

## 7. Security

- Model API keys and Firebase Admin / service-account credentials: never in Flutter, never in Git.
- Firebase client config (`firebase_options.dart`, `google-services.json`) is not secret; protection comes from rules.
- Rules are versioned, reviewed and emulator-tested before the first write (section 5.1).
- External timestamping sends only hashes.

## 8. Research integrity, evaluation and testing

- Integrity rules: `NEW_DIRECTION.md` section 8. Record and pilot rules (candidates editable, definitions frozen before the first forecast, no backdating, late forecasts excluded, corrections as new records, baselines with rules fixed in advance, India–Western pairs as matched comparisons, synthetic and historical records kept apart): `PILOT_PROTOCOL.md`.
- Evaluation: Brier on `yes`/`no` only; calibration with sample size and uncertainty; baselines with rules fixed in advance (base rate in the pilot; persistence only after its method is documented and validated, D2; official RBI/IMD forecasts deferred unless a defensible conversion exists, D3); primary leaderboard = latest **eligible** forecast per question, model and condition, with eligibility and selection order defined in `PILOT_PROTOCOL.md` section 7.1 (D1); question status derived by the ordered rules in its section 4.1; late forecasts kept but excluded (D9); India vs Western matched pairs (4–6, exploratory, D5); A3 past-question results reported separately.
- Testing:
  - **Python:** `reflica_bench` tests unchanged (203); new `research/tests/test_forecast_*.py` (schema, validator, hashing, append-only store, timeliness rule, Brier hand values, end-to-end with `TEST-` fixtures, pilot-file import without changes).
  - **Flutter:** `flutter analyze` and `flutter test` on the Mac. Screen empty states, navigation (including legacy routes), demo-flag behaviour and model JSON round-trip (`UI_SPEC.md` section 6). The cloud environment has no Flutter SDK.

## 9. Risks

1. Stage-1 and `main` diverge (91 files). Integrate before Phase 2, or the UI work will conflict.
2. Unknown live security rules.
3. The December deadline: the protocol and question drafts must be ready in November.
4. Manual collection errors (wrong times, edited lines). These are mitigated by hashes, same-day stamps and the importer's checks.
5. Public read costs once the app is live.
6. Fabricated-looking UI numbers. Prevented by the demo flag and banner.

## 10. Open decisions

Decided on 14 Oct 2026: D1–D9 (`research/forecast/PILOT_PROTOCOL.md` section 0). Documentation approved in principle, subject to final content review.

Still open:
1. Final content review of this documentation set.
2. Stage-1 merge: review `STAGE1_MERGE_CHECKLIST.md`, then merge and test on the Mac. **No UI work starts before this is settled.**
3. Approve the UI navigation and the "Legacy Plans in Settings" placement.
4. Which 2–3 pilot models and the monthly API budget (November).
5. Timestamping service evaluation (D7, November).
6. Export the current Firestore rules from the console (needed before Phase 4).
