# Reflica — PROGRESS

> **Vision:** Human-Centered Multimodal Cognitive Intelligence & Closed-Loop Decision-Support Platform.
> A **living strategic planning architecture** where a goal → structured strategy graph stays continuously updated by real-world reports. The mind map is the human-facing view of the underlying structured system, not the product.
> **Owner:** Sundram Awasthi · M.Tech CSE (2026–28), GLA University.
> **Last updated:** 2026-10-09

---

## One-sentence definition

Reflica keeps an explicit, evidence-aware model of a changing situation so that AI-generated plans can be checked, traced, reported against, and repaired as reality changes — serving individuals, organisations, research institutions, government bodies, and disaster responders through one general engine.

---

## Two levels (do not conflate)

| Level | Scope | State |
|---|---|---|
| **A — Long-term platform (Reflica)** | Multimodal, closed-loop, serves individuals → organisations → government with reporting + impact propagation + federated connection layer. | Flutter product Stage 0+ complete. |
| **B — M.Tech research** | Attribute-aware revision of LLM-extracted state graphs under partial-satisfaction + capacity constraints. Sub-component of Reflica's Capability C (Change / Revision Engine). | Benchmark v0.2.0 (63 scenarios, 7 categories) built and frozen; R-N pilot complete (144/144 calls); B5 engine frozen v0.1.0; 203 tests passing. Full experiment not started. |

---

## Current snapshot (what works right now)

### Product UI — fully running on Chrome + Android

| Area | State | Notes |
|---|---|---|
| Flutter app shell | ✅ | Web (Chrome) + Android (Realme RMX3997) both running |
| **Google sign-in** | ✅ Native | Web: Firebase popup. Android: `google_sign_in` package → native bottom sheet (no separate activity) |
| Demo-mode fallback | ✅ | Any platform without Firebase config falls through |
| Sign-in error dialog | ✅ | Network / cancelled / popup-blocked / other — all have specific messages + hints |
| Sign-out | ✅ | Confirmation dialog · in-progress snackbar · native `disconnect()` + `signOut()` + Firebase sign-out · route stack cleared + back to `/` |
| **Firestore offline persistence** | ✅ Explicit | Unlimited cache. Writes queue offline, sync on reconnect, survive logout + login |
| Public landing page | ✅ | Hero · Living Loop · 7 Input Modes · Audience · Evidence · CTA · Footer |
| Dashboard shell | ✅ | Sidebar · top bar · welcome · 7-mode Quick Capture · use cases · live activity · quick actions · how-it-works |
| Plan model + repository | ✅ | JSON round-trip, Firestore + in-memory |
| New Plan wizard | ✅ | 4 steps · 7 input modes · accepts `NewPlanArgs(audience, mode, seedText)` for pre-filled flows |
| All 7 input modes | ✅ | Text · structured form · voice · documents · images · video · live camera |
| My Plans grid | ✅ | Live stream, hover cards, empty state |
| Plan detail + mind map | ✅ Adaptive | `CustomPainter` + pan/zoom · nodes scale with canvas · edge labels hide on narrow |
| Plan editor | ✅ | Inline title · raw-text · node add/edit/remove · live save |
| Delete | ✅ Reliable | Fire-and-forget Firestore delete, offline-queue safe, survives logout → login |
| Notifications | ✅ | Live badge · panel · mark-read · auto-emit on every write |
| Favicon + logo | ✅ | `BrandMark` single source of truth + SVG favicon |
| **Mobile responsiveness** | ✅ All screens | See responsiveness matrix below |

### Dependencies (pubspec)

- `firebase_core 4.15.0`, `firebase_auth 6.7.0`, `cloud_firestore 6.10.0`, `firebase_analytics 12.6.0`, `firebase_ai 4.0.0` — pinned, FlutterFire plugins move together.
- `flutter_svg: ^2.0.10+1` — audience illustrations.
- `file_picker: ^8.1.4` — cross-platform input artefacts.
- `uuid: ^4.5.1` — plan + notification IDs.
- `google_sign_in: ^6.2.1` — native Android account picker (bottom sheet).
- `google_fonts: ^6.2.1` — kept as transitive, **not called anywhere** (system fonts via `AppText` for offline safety).

---

## M.Tech research track — current status (2026-10-09)

**Thesis sentence (locked):**
> Attribute-aware revision of LLM-extracted state graphs under partial-satisfaction and capacity constraints — evaluated across add, edit, delete, and relationship-change operations against classical ATMS, constraint-programming, and LLM-regeneration baselines.

**Where it fits:** sub-component of **Capability C — Change / Revision Engine**. Not Reflica itself.

### 7 benchmark categories (locked 2026-10-07; implemented 2026-10-08; frozen as benchmark v0.2.0)
1. Irrelevant change / no propagation
2. Direct dependency / single hop
3. Multi-hop propagation
4. Alternative-justification preservation
5. **Partial satisfaction + attribute change** ⭐ candidate novelty
6. **Capacity-constrained alternatives** ⭐ candidate novelty
7. Ambiguity / structural edge cases

### Cross-category synthesis — six sections locked
Scenario allocation · input-regime allocation · unified schema · common baseline interface · master metric matrix · thesis reporting matrix (10 tables + 5 figures).

### Baselines
B1 LLM regeneration · B2 LLM re-prompt with graph · B3 Reachability-only invalidation · B4a Classical ATMS · B4b Weighted CSP + rule engine (OR-Tools) · B5 **Proposed** attribute-aware revision · B6 Oracle scope (evaluator-side upper-bound).

### Research track — done so far
- **Benchmark v0.2.0:** 63 scenarios, SHA-256 manifest (`research/reflica_bench/frozen_manifest.json`; v0.1.0 kept for history).
- **Ground truth:** hand-written labels cross-checked against the independent exact generator `gt_engine.py`.
- **Deterministic baselines:** B3, B4a, B4b (OR-Tools CP-SAT; matches ground truth on all of Cat 5–6).
- **Natural-language layer:** template renderer + leakage checker (`rn.py`); B1/B2/extractor prompts and typed extraction schema.
- **R-N pilot (config v1.7, nemotron-3-ultra-550b-a55b):** 16 scenarios × 3 repeats = 144/144 calls; one genuine extraction failure (T7.2 invented preference rule). See `research/experiments/rn_pilot/PILOT_HEALTH.md`.
- **B5 (Reflica engine) v0.1.0:** frozen; 0 disagreements with gold on all 63 scenarios. See `research/reflica_bench/b5/B5_REPORT.md`.
- **Tests:** 203 passing.

### Research track next steps
1. Freeze the full protocol (conditions, statistics plan).
2. Run the full 63-scenario experiment.
3. Statistics (95% CIs, paired tests) and hypothesis verdicts.
4. Failure analysis and component ablations.
5. Deep literature review and contribution statement.
6. Thesis writing.

---

## Responsiveness matrix

All layouts are **width-reactive** (not platform-reactive). Same code produces the right layout on a 360-px Android phone, a 768-px tablet web view, or a 1440-px desktop.

| Section | Phone (<560 px) | Tablet (560–900 px) | Desktop (900–1180 px) | Wide (≥1180 px) |
|---|---|---|---|---|
| Landing nav | logo + Get Started | logo + Get Started | all + nav links | all + tagline (≥1480) |
| Hero | stacked, 44 pt headline | stacked, 58 pt | side-by-side, 58 pt | side-by-side, 72 pt |
| Living Loop | vertical step list | vertical step list | elliptical ring diagram | ring |
| 7 Input Modes | 1 col | 2 cols | 3 cols | 4 cols |
| Audience | 1 col | 2 cols | 3 cols | 5 cols |
| Evidence (5 cards) | 1 col, intrinsic | 2 cols | 2 cols | 5 cols |
| Dashboard sidebar | drawer (menu icon) | drawer | drawer | pinned 240 px |
| Dashboard top bar | avatar + bell + menu | + search | + search + pipeline | + tagline |
| Welcome card | stacked, icon-only Start | stacked | side-by-side | side-by-side |
| Quick Input Strip (7 modes) | 2 cols | 3 cols | 4 cols | 7 cols |
| Use cases | 1 col | 2 cols | 3 cols | 5 cols |
| Recent Activity | **stacked cards** (<760) | **table** | table | table |
| Plan detail top bar | minHeight 84, pad 8 | 72, 20 | 72, 20 | 72, 20 |
| Mind map | shrunk nodes, no edge labels | small nodes, labels | full | full |
| Plans grid | 1 col | 2 cols | 3 cols | 4 cols |
| New Plan wizard progress strip | truncated labels | full | full | full |
| Footer | brand block + 2×2 wrap | 2-col wrap | 5-col | 5-col |

---

## Architecture at a glance

```
            Audience + Input mode + Content
                       │
            ┌──────────▼──────────┐
            │   NewPlanFlow       │   4-step wizard
            └──────────┬──────────┘   (accepts NewPlanArgs
                       │                 from Quick Capture strip)
       ┌───────────────▼───────────────┐
       │     PlanRepository            │   create / save / rename
       │   (Firestore + in-memory)     │   upsertNode / removeNode
       └───────────────┬───────────────┘   addEdge / removeEdge
                       │                   delete(plan: Plan)
         ┌─────────────┼─────────────┐
         ▼             ▼             ▼
   watchMyPlans   watchPlan    emit notification
         │             │             │
   ┌─────┴────┐   ┌────┴────┐   ┌────┴─────────┐
   │ Activity │   │ Plan    │   │ Notification │
   │  cards   │   │ detail  │   │   panel      │
   │ /table   │   │ + mind  │   │ + bell badge │
   │ + sidebar│   │   map   │   │              │
   │ + grid   │   │ + editor│   │              │
   └──────────┘   └─────────┘   └──────────────┘
```

Every write path:
1. Writes to Firestore (or memory in demo mode).
2. **Firestore offline persistence** — if offline, write queues locally and survives app restart / logout / login until synced.
3. Live streams fire → UI updates in the same frame everywhere.
4. A matching `AppNotification` is emitted → badge increments, panel updates.

---

## Auth flow

```
Landing → "Get Started" / "Start Exploring"
            │
            ▼
   AuthService.signInWithGoogle()
            │
   ┌────────┴────────┐
   ▼                 ▼
 WEB              ANDROID / iOS
 FirebaseAuth    GoogleSignIn (bottom sheet)
 .signInWithPopup   │
                    ▼
            account.authentication → id/access tokens
                    │
                    ▼
         GoogleAuthProvider.credential(...)
                    │
                    ▼
         FirebaseAuth.instance.signInWithCredential(...)
                    │
                    ▼
         authStateChanges emits user
                    │
                    ▼
         AuthGate rebuilds → DashboardScreen

Sign-out: confirmation dialog → native disconnect() + signOut()
          → FirebaseAuth.signOut() → stream emits null
          → Navigator.pushNamedAndRemoveUntil('/', ...) → HomeScreen

Errors: specific messages (network / cancelled / popup-blocked / …)
        shown in a branded dialog with hints box when offline.
```

Auth-related files:
- [services/auth_service.dart](lib/services/auth_service.dart) — `SignInException` + `signInWithGoogle` + `signOut` with native disconnect
- [widgets/app_top_bar.dart](lib/widgets/app_top_bar.dart) — `handleGetStarted` + `handleSignOut` + `showSignInErrorDialog`
- [screens/auth_gate.dart](lib/screens/auth_gate.dart) — streams `AppUser` and swaps Home ↔ Dashboard

---

## Code layout

```
lib/
├── main.dart                       # routes + Firebase init + Firestore persistence
├── firebase_options.dart           # web + android config
├── theme/
│   └── app_theme.dart              # colour tokens + system-font text styles
├── models/
│   ├── plan.dart                   # Plan, Node, Edge, Audience, InputMode, EvidenceType
│   └── notification.dart           # AppNotification, NotificationKind
├── services/
│   ├── auth_service.dart           # Google sign-in (Firebase popup / google_sign_in) + demo fallback
│   ├── plan_repository.dart        # CRUD + live streams + notification emission + offline-safe delete
│   └── notification_service.dart   # badge counter + mark-read + panel stream
├── screens/
│   ├── auth_gate.dart              # routes to Home or Dashboard based on auth state
│   ├── home_screen.dart            # public landing (6 sections)
│   ├── dashboard_screen.dart       # signed-in home
│   ├── new_plan_flow.dart          # 4-step wizard, 7 modes, NewPlanArgs preset support
│   ├── plans_screen.dart           # live grid
│   ├── plan_detail_screen.dart     # mind map + edit mode + delete
│   └── placeholder_screen.dart     # stubs for /graph /scenarios /settings
└── widgets/
    ├── brand_mark.dart             # the one logo
    ├── app_top_bar.dart            # landing nav + handleGetStarted/SignOut
    ├── hero_section.dart           # gradient headline + mind-map preview
    ├── living_loop_section.dart    # 6-step loop (ring on wide, list on mobile)
    ├── input_modes_section.dart    # 7 mode cards + typed-output footer
    ├── audience_section.dart       # 5 cards with real images (SVG + PNG/JPG)
    ├── evidence_section.dart       # 5 evidence types
    ├── features_bar.dart           # pill row
    ├── cta_footer.dart             # CTA card + dark footer (brand + 4 cols + newsletter + socials)
    ├── situation_graph.dart        # animated flood-response demo (hero)
    ├── responsive.dart             # breakpoint helpers
    ├── plan/
    │   ├── plan_mind_map.dart      # CustomPainter, pan+zoom, adaptive scaling
    │   └── node_editor_dialog.dart # add/edit node modal
    └── dashboard/
        ├── dashboard_sidebar.dart  # nav + live recent plans + help card
        ├── dashboard_top_bar.dart  # search + bell + user menu + sign-out
        ├── welcome_card.dart       # greeting + prompt bar (seeds wizard) + attach menu
        ├── quick_input_strip.dart  # 7 mode shortcuts → /new-plan with preset
        ├── use_cases_row.dart      # 5 sector cards with images
        ├── activity_table.dart     # live Recent Activity (table on wide, cards on mobile)
        ├── quick_actions_panel.dart# 4 action rows → routes
        └── how_it_works_strip.dart # 5-step pipeline
```

---

## Routes

| Route | Screen | Notes |
|---|---|---|
| `/` | `AuthGate` | Home when signed out, Dashboard when signed in |
| `/dashboard` | `DashboardScreen` | — |
| `/new-plan` | `NewPlanFlow` | Accepts `NewPlanArgs { audience?, mode?, seedText? }` via `settings.arguments` to pre-fill the wizard |
| `/plans` | `PlansScreen` | Live grid |
| `/plan` (arg = planId) | `PlanDetailScreen` | Mind map + editor |
| `/graph`, `/scenarios`, `/documents`, `/settings` | `PlaceholderScreen` | "In development" stubs |

---

## Data model (Firestore)

```
users/{uid}/
├── plans/{planId}
│   ├── id, ownerId, title
│   ├── audience (individual|organization|research|government|disaster)
│   ├── inputMode (text|form|voice|document|image|video|camera)
│   ├── rawText
│   ├── artefacts: [{fileName, mimeType, bytes}]
│   ├── nodes:     [{id, label, subLabel, type, x, y, confidence, source}]
│   ├── edges:     [{from, to, kind}]
│   ├── status (draft|verified|changed|repaired)
│   └── createdAt, updatedAt
└── notifications/{notifId}
    ├── id, ownerId, kind, title, body
    ├── planId (nullable)
    ├── read
    └── createdAt
```

Evidence types: `fact | observation | prediction | hypothesis | assumption`.
Edge kinds: `dependsOn | blocks | enables | causes | requires | supports`.
Notification kinds: `planCreated | planUpdated | planDeleted | nodeAdded | nodeUpdated | nodeRemoved | edgeAdded | edgeRemoved`.

---

## Android configuration

- `AndroidManifest.xml` has `INTERNET` + `ACCESS_NETWORK_STATE` permissions.
- App label: **Reflica** (was "reflicaa").
- `google-services.json` with Android OAuth client (debug SHA-1 `21:4F:FA:71:0B:2D:7C:08:FE:8E:23:6D:B2:1A:CD:38:62:45:12:E4` registered).
- `google_sign_in` wired to the **web** OAuth client ID (`53064442729-mnva30m81sr31010lss08uidrlcpshen.apps.googleusercontent.com`) so the ID token is valid for Firebase.

---

## Roadmap — tracked against the 10-step user flow

Reflica's full user flow has **10 steps** (locked 2026-10-08). The product's current coverage:

| # | Step | Covered now | Stage |
|---|---|---|---|
| 1 | **INPUT** — text · voice · documents · images · video · camera · (later: workspace extensions) | ✅ 6 of 7 modes, extensions later | Stage 0+ |
| 2 | **READ** — LLM extracts tasks, people, resources, deadlines, links | ⬜ (deterministic seed graph as placeholder) | **Stage 1** |
| 3 | **CONFIRM** — user checks the map, AI marks and asks about unsure parts | ⬜ | Stage 1 |
| 4 | **STORE** — typed graph (fact / observation / prediction / hypothesis / assumption) + confidence + source | ✅ | Stage 0+ |
| 5 | **CHANGE** — a change arrives (typed, spoken, or auto) | ✅ via editor | Stage 0+ |
| 6 | **SEARCH** — graph search finds everything connected | ⬜ | Stage 2 |
| 7 | **UPDATE (B5)** — attribute-aware revision with ATMS + CSP + fixed-point stopping | ⬜ (this is the M.Tech thesis) | Stage 2 |
| 8 | **EXPLAIN** — "Cause: X. Effects: A, B, C. No change: D, E." | ⬜ | Stage 2 |
| 9 | **APPROVE** — human accepts or rejects | ⬜ | Stage 2 |
| 10 | **ALERT** — shown in app, inside user's tool, or posted back via API | ✅ (in-app audit trail via notifications) | Stage 0+; expand in Stage 3 |

### Stage 0+ (done — product foundation)
Scaffolding · 7-mode input intake · live persistence · mind-map rendering · editor · notifications · auth · offline-safe delete · mobile responsiveness · pro home page with 6 sections.

### Stage 1 (next — bring in the LLM)
- [ ] Gemini extractor via `firebase_ai`: text → structured JSON matching `Plan` / `PlanNode` / `PlanEdge`.
- [ ] Document extraction (PDF/DOCX text) → same extractor.
- [ ] Vision model for images (basic).
- [ ] **Confirmation step** — show the extracted map to the user with "unsure" markers; let them accept or revise before saving.
- [ ] **Reporting on nodes** — planned vs actual, deviation detection, impact propagation.
- [ ] Build the Python research workspace (NetworkX / OR-Tools) for the M.Tech thesis — **separate repo**.

### Stage 2 (the Change Engine — ties into the thesis)
- [ ] Change intake (typed, spoken, or structured delta from an API).
- [ ] Graph search over typed edges (BFS/DFS).
- [ ] First version of **B5** (attribute-aware revision) wired into the product.
- [ ] **Explain** output: cause → effects → no-change breakdown, surfaced in the plan detail.
- [ ] **Approve** step: human accepts/rejects each proposed change before it commits.
- [ ] Scenarios (what-if branches).
- [ ] Combined `/graph` view across plans.
- [ ] Audit log + export.

### Stage 3 (reach into the user's workspace)
- [ ] **Workspace extensions** (one at a time — Calendar or Excel first):
  Google Calendar / Outlook · Excel · VS Code · Word · Jira / Trello · Gmail / Teams / Slack · Power BI / Data Studio.
  Each extension watches a scoped data source (with explicit user permission), sends only the delta to Reflica, and renders the alert back inside the same tool.
- [ ] **API / webhooks** so third-party systems can push changes and receive effects.
- [ ] **Local-install package** (small local LLM + offline-first) for defence / government / sensitive deployments.
- [ ] Role-based visibility and collaboration (government / institutional use).

### Delivery modes

Reflica ships as **three products that share one engine**:
- **App** — individuals, small teams. ✅ (current Flutter app covers this)
- **API / plug-in** — companies, banks (their software sends changes, gets effects back). Stage 3.
- **Local install** — defence, government (own computers, no internet, secure). Stage 3.

---

## Decisions log

| Date | Decision | Why |
|---|---|---|
| 2026-10-06 | Thesis stack = Python + NetworkX + OR-Tools (separate workspace); product UI = Flutter | Research laptop-sized; product cross-platform |
| 2026-10-06 | Flutter app = demo-mode fallback when Firebase not configured | Lets web preview run before Firebase Web app registered |
| 2026-10-06 | `BrandMark` is the single logo widget; favicon mirrors it | One place to change the brand |
| 2026-10-07 | Reflica refined to "living strategic planning architecture" | Earlier framing was too narrow |
| 2026-10-07 | Repository emits a notification on every write | Users need an audit trail |
| 2026-10-07 | Plan edits save immediately per field (not "save button") | Living strategic model — plans never go stale |
| 2026-10-07 | Thesis locked: attribute-aware revision; 7 categories × 4 ops × 7 baselines | After literature-search rounds |
| 2026-10-07 | **System fonts via `AppText`, no `google_fonts` runtime fetching** | Offline-safe on mobile; no async font-fetch exceptions in logs |
| 2026-10-07 | **`google_sign_in` for Android, Firebase popup for web** | In-app bottom-sheet UX on Android, no separate `GenericIdpActivity` |
| 2026-10-07 | **Firestore offline persistence explicit, unlimited cache** | Deletes made offline survive logout + login and sync on reconnect |
| 2026-10-07 | **`delete()` is fire-and-forget** — no pre-read, Plan passed by caller | Previously `get()` could hang offline; now UI reacts instantly |
| 2026-10-07 | **Width-reactive layouts** (not platform-reactive) | Same code produces right layout on any viewport, Android or web |
| 2026-10-07 | **Python research workspace scaffolded** (`research/`): schema, linter, ground-truth generator, adapters, baselines B3/B4a/B4b, 4 Cat 1 floor scenarios, 18 pytest tests all passing | First executable research deliverable; no LLM baselines yet |
| 2026-10-07 | **`PlanRepository._requireOwnerId()` replaces every `demo` fallback**; dashboard user menu adds a copy-to-clipboard `uid` chip | Fixes silent cross-device sync breakage when `currentUser` was briefly null; makes cross-device uid parity diagnosable in one tap |
| 2026-10-07 | **Research track: Categories 2, 3, 4 implemented** with 61 passing tests; integrity audit complete; Cat 4 adds `justifications` rule block with ATMS-style preservation (B3 structurally fails preservation while B4a succeeds) | Benchmark is now at the floor of each category; next is Cat 5 (partial satisfaction, ⭐ candidate novelty) which also triggers the ground-truth / B4b independence requirement via CP-SAT. |
| 2026-10-08 | **Research track: Categories 5, 6 (6-A + 6-B), 7 implemented** — 41 new scenarios (63 total), 100 passing tests. New `gt_engine.py` (exact Python ground truth, consistent-completion enumeration for Cat 7) and `b4b_cpsat.py` (B4b via OR-Tools CP-SAT). B4b agrees with ground truth on every Cat 5/6 scenario; on Cat 7 it detects P1/P2/P4/P5/P6 and commits on P3/P7/P8a/P8b/P9/P10. B4a catches P4/P5 but false-abstains on the dormant-cycle control. | Ground-truth / B4b circularity from the Cat 4 audit is now broken. Scenario counts are below Phase A allocation; next is B5 or literature review. |
| 2026-10-08 | **R-N layer + pilot built (no LLM yet).** Canonical benchmark frozen at 63 (SHA-256 manifest + test). `rn.py`: deterministic template renderer (neutral labels, never reads ground truth), leakage checker (outcome/ambiguity vocabulary, P-codes, template ids, node ids, post-event-only numbers), `NaturalLanguageAdapter_v1` (prose only; alias map evaluator-side). 16 pilot R-N files, 117 tests passing. Design locked: API model at temperature 0, τ_FA 0.15, δ 0.05 non-inferiority. | Known issue: frozen `cat1_add_disconnected_001` contains the word "unrelated" → blocked from R-N until a versioned fix is approved. Next: extractor output schema + LLM integration after review. |
| 2026-10-08 | **Benchmark v0.2.0** — hygiene fix to `cat1_add_disconnected_001` ("unrelated reminder" → "reminder note"), found by the leakage checker **before any LLM results**. v0.1.0 manifest kept (`frozen_manifest_v0.1.0.json`); all 63 now render leak-free; 118 tests. Draft pilot prompts/schemas/config in `research/experiments/rn_pilot/`. | Blocked: no API key / SDK in the environment, so the GPT-5.6 model id cannot be verified or frozen. |
| 2026-10-09 | **R-N pilot complete (config v1.7).** Primary model `nvidia/nemotron-3-ultra-550b-a55b` (temp 0, seed 20261008, thinking on, 16,384 max tokens) after Gemini, Kimi K3, Nemotron Lightning and gpt-oss-20b were tried and rejected (each logged under `experiments/rn_pilot/runs/`). 144/144 calls, 0 truncation; extraction recall 1.0, pre-state reproduction 0.993; one genuine failure kept (T7.2 invented `prefer_source`). | Infrastructure healthy; full experiment blocked until B5 built and frozen. |
| 2026-10-09 | **B5 (Reflica engine) v0.1.0 frozen** — change detection → dependency scope → scoped revision → verify/repair → determinability across consistent completions. Independent of ground-truth code (enforced by test); 0 disagreements with gold on 63 scenarios; rejects the T7.2 invented rule. 203 tests passing. | Next: freeze full protocol, then run the 63-scenario experiment. |

---

## Rules going forward

- Platform vision is broad. M.Tech is narrow. **Do not conflate.**
- Never claim "first" or "novel" until the 2025–26 literature search is done.
- Keep out-of-scope items (federated systems, autonomous execution, personal "replica", trained-from-scratch LLMs) out of M.Tech code.
- Every input mode produces the same typed JSON before the graph is touched.
- Reporting (planned vs actual) is first-class, not an afterthought.
- Every write → live stream fires → notification emits → audit trail recorded.
- Every new UI widget is **width-reactive**, never platform-reactive (`MediaQuery.sizeOf(context).width` or `LayoutBuilder`, never `Platform.isAndroid` or `kIsWeb` for layout decisions).

---

## How to run

```bash
# Install dependencies
flutter pub get

# Web
flutter run -d chrome

# Android (device/emulator)
flutter run -d <device-id>

# Lint
flutter analyze     # should print "No issues found!"
```

If assets or dependencies change: `q` to quit, then `flutter run -d <device>` for a cold start (hot restart doesn't rebuild the asset bundle).
