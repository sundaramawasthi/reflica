# Reflica — PROGRESS

> **Vision:** Human-Centered Multimodal Cognitive Intelligence & Closed-Loop Decision-Support Platform.
> A **living strategic planning architecture** where a goal → structured strategy graph stays continuously updated by real-world reports. The mind map is the human-facing view of the underlying structured system, not the product.
> **Owner:** Sundram Awasthi · M.Tech CSE (2026–28), GLA University.
> **Last updated:** 2026-10-07

---

## One-sentence definition

Reflica keeps an explicit, evidence-aware model of a changing situation so that AI-generated plans can be checked, traced, reported against, and repaired as reality changes — serving individuals, organisations, research institutions, government bodies, and disaster responders through one general engine.

---

## Two levels (do not conflate)

| Level | Scope | State |
|---|---|---|
| **A — Long-term platform (Reflica)** | Multimodal, closed-loop, serves individuals → organisations → government with reporting + impact propagation + federated connection layer. | Flutter product Stage 0+ complete. |
| **B — M.Tech research** | Attribute-aware revision of LLM-extracted state graphs under partial-satisfaction + capacity constraints. Sub-component of Reflica's Capability C (Change / Revision Engine). | Direction + 7 categories + cross-category synthesis locked 2026-10-07. No research code yet. |

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

## M.Tech research track — current status (2026-10-07)

**Thesis sentence (locked):**
> Attribute-aware revision of LLM-extracted state graphs under partial-satisfaction and capacity constraints — evaluated across add, edit, delete, and relationship-change operations against classical ATMS, constraint-programming, and LLM-regeneration baselines.

**Where it fits:** sub-component of **Capability C — Change / Revision Engine**. Not Reflica itself.

### 7 benchmark categories (all locked 2026-10-07)
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

### Research track next step
Instantiate scenarios + Python code only AFTER the benchmark contract is implemented. Separate workspace from this Flutter product.

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

## Stage 0+ → Stage 1 roadmap

**Stage 0+ (done)** — scaffolding, 7-mode input intake, live persistence, mind-map rendering, editor, notifications, auth, offline-safe delete, mobile responsiveness, pro home page with 6 sections.

**Stage 1 (next):**
- [ ] Gemini extractor via `firebase_ai` from text → structured JSON matching `Plan`/`PlanNode`/`PlanEdge`.
- [ ] Document extraction (PDF/DOCX text) → same extractor.
- [ ] Vision model for images (future).
- [ ] **Reporting on nodes** — planned vs actual, deviation detection, impact propagation.
- [ ] Build the Python research workspace (NetworkX/OR-Tools) for the M.Tech thesis — separate repo.

**Stage 2:**
- [ ] Collaboration + role-based visibility (government / institutional).
- [ ] Scenarios (what-if branches).
- [ ] Combined `/graph` view across plans.
- [ ] Audit log + export.

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
