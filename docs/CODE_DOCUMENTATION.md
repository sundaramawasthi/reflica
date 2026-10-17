# Reflica: Code Documentation

> Updated 17 Oct 2026. It covers the code that **exists today**: the Flutter app shell, the data scripts and the Firebase rules.
> **Not yet written:** forecasting models, claim extraction, the revision rule and the evaluation pipeline (steps 7–9).

## 1. Overview

| Part | Language | Location | Status |
|---|---|---|---|
| Web / Android app (UI shell) | Dart / Flutter | `lib/`, `test/` | ✅ Builds and runs; `flutter analyze` is clean |
| Firebase security rules | Firestore rules, JS tests | `firestore.rules`, `database.rules.json`, `docs/rules-tests/` | ✅ Published |
| Data collection scripts | Python 3 | `data/scripts/` | ✅ Used to build the CPI datasets |
| Forecasting engine | Python (planned) | `research/forecast/pipeline/` (planned) | ⏳ Not started |

About **3,300 lines** of Dart in `lib/`.

## 2. Flutter app (`lib/`)

**Dependencies** (`pubspec.yaml`, package name `reflicaa`): `firebase_core`, `firebase_auth`, `cloud_firestore`, `firebase_analytics`, `firebase_ai`, `google_sign_in`, `uuid`.

### 2.1 Entry point and routing
- **`main.dart`** initialises Firebase and runs `ReflicaApp`, a `MaterialApp` with named routes:
  - `/` → `AuthGate` (shows the home page or the dashboard, depending on sign-in)
  - `/dashboard` → `DashboardScreen`
  - `/settings`, and other sidebar routes → `PlaceholderScreen` ("coming soon")
- **`firebase_options.dart`** holds the generated Firebase config for project `reflica-593b4`. This is a public client config, not a secret; security comes from the rules.

### 2.2 Screens (`lib/screens/`)
| File | Purpose |
|---|---|
| `auth_gate.dart` | Listens to `AuthService.authState`. It shows `HomeScreen` when signed out, `DashboardScreen` when signed in, and a loader while waiting |
| `home_screen.dart` | Public landing page: top bar, hero ("Better forecasts. A clearer tomorrow."), feature cards, "How it works", footer. Question Bank and Forecasts show an honest "coming soon" dialog. Colours are in `HomeColors` |
| `dashboard_screen.dart` | Signed-in layout: sidebar, top bar, main area with the welcome card |
| `placeholder_screen.dart` | Reusable "coming soon" page for routes that aren't built yet |

### 2.3 Services (`lib/services/`), all singletons (`.instance`)
| Service | Main API | Notes |
|---|---|---|
| `AuthService` | `authState` (stream of `AppUser?`), `signInWithGoogle()`, `signOut()` | Google sign-in through a Firebase popup on web and `google_sign_in` on Android. Errors are raised as `SignInException` |
| `NotificationService` | `watchMyNotifications()`, `watchUnreadCount()`, `emit()`, `markRead()`, `markAllRead()`, `delete()` | Reads and writes `users/{uid}/notifications/{id}`, which only the owner may access |

### 2.4 Model (`lib/models/notification.dart`)
- `AppNotification` has the fields `id`, `ownerId`, `kind`, `read`, title and body text, and a timestamp. It has `toJson` / `fromJson`.
- `NotificationKind` is an enum with an icon for each kind.
- **Technical debt:** some kinds, such as `planUpdated`, are left over from the old plan app. They should be replaced with forecasting kinds later (deadline, resolution, revision).

### 2.5 Widgets and theme
| File | Purpose |
|---|---|
| `widgets/app_top_bar.dart` | Public top navigation bar, plus the mobile menu |
| `widgets/brand_mark.dart` | The single logo widget |
| `widgets/cta_footer.dart` | Footer |
| `widgets/dashboard/dashboard_sidebar.dart` | Sidebar items → `Navigator.pushNamed(route)` |
| `widgets/dashboard/dashboard_top_bar.dart` | Dashboard header, user menu, notifications |
| `widgets/dashboard/welcome_card.dart` | "AI Forecasting for India" welcome card |
| `widgets/responsive.dart` | `Breakpoints` (sm 560, md 900, lg 1180, xl 1240), `ScreenSize`, `PageWrap` |
| `theme/app_theme.dart` | `AppColors` and the theme. Text uses system fonts (no runtime font download) |

**UI rule:** layouts respond to **screen width**, not platform (`MediaQuery.sizeOf(context).width`).

### 2.6 Tests (`test/`)
- `widget_test.dart` is a placeholder smoke test only. **There are no real app tests yet**, so this is a known gap.

## 3. Firebase

| File | What it does |
|---|---|
| `firestore.rules` | **Owner-only** access to `users/{uid}/notifications/{id}`. Create requires `id == docId`, `ownerId == uid` and a boolean `read`. Everything else is denied. Published 14 Oct 2026 |
| `database.rules.json` | Realtime Database is fully locked (`.read`/`.write` false). It isn't used |
| `docs/rules-tests/firestore.rules.test.mjs` | Emulator test matrix for the rules (allow and deny cases) |
| `docs/FIREBASE_SPARK.md` | Security review; free Spark plan only |

Rules change **only with approval**, and are republished by hand in the Firebase console.

## 4. Data scripts (`data/scripts/`)

All scripts follow the data rules in `data/README.md`: keep originals, never estimate dates, never overwrite existing rows.

| Script | Input → output | How to run |
|---|---|---|
| `fetch_cpi_api.py` | MoSPI e-Sankhyiki API → `data/raw/cpi_api/<run>/` (raw JSON pages + `manifest.json`) | `MOSPI_USER=… MOSPI_PASS=… python3 data/scripts/fetch_cpi_api.py --base-year 2012 --level group --from-year 2013 --to-year 2025` |
| `build_cpi_series.py` | Raw API pages → `data/processed/cpi_series_revised_<date>.csv` (All-India General, Rural/Urban/Combined; `vintage=latest_revised`) | `python3 data/scripts/build_cpi_series.py` |
| `fetch_cpi_releases.py` | MoSPI CPI press-release PDFs for a month range → `data/raw/cpi_releases/CPI_<YYYY-MM>_press_release.pdf` + `.txt` + manifest | `python3 data/scripts/fetch_cpi_releases.py 2024-01 2025-11` |
| `parse_cpi_releases.py` | Release texts → new rows in `cpi_release_calendar.csv` (first-release value; date and time only as printed) | `python3 data/scripts/parse_cpi_releases.py 2024-01 2025-11` |

**Notes**
- `fetch_cpi_api.py` uses **curl**, not Python `urllib`, because the MoSPI server needs legacy TLS renegotiation. It logs in with `MOSPI_USER` and `MOSPI_PASS` (environment only, never saved) and refreshes the token every 25 minutes. The `level` parameter must be capitalised (for example "Group").
- The cloud session **cannot reach mospi.gov.in**, so run these scripts on the Mac.
- Document files (RBI / PIB PDFs) were added by hand. Each was checked for duplicates (by file bytes and by press-release ID), its text extracted with `pdftotext` or `pypdf`, and a row added to `source_documents.csv`.

## 5. Data contracts

| File | Key columns |
|---|---|
| `cpi_series_revised_*.csv` | `reference_month, base_year, series, sector, index, yoy_inflation, api_status, source, retrieved_at, vintage` |
| `cpi_release_calendar.csv` | `reference_month, release_date, release_time_ist, source_url, base_year, status, headline_cpi_index, headline_yoy_inflation, retrieved_at, first_release_verified` |
| `source_documents.csv` | `document_id, source, title, published_at, url, document_type, full_text_path, retrieved_at, timestamp_confidence, search_keywords, review_status` |
| `claims.csv` (empty) | `claim_id, document_id, claim_text, topic, direction, published_at, source_url, extraction_confidence` |

**ID format:** `SOURCE_YEAR_NNN`. **`timestamp_confidence`:** verified / date-only / uncertain.

## 6. Planned code (not yet written)

| Module | Purpose |
|---|---|
| `research/forecast/pipeline/` | Python package for the experiments |
| `claims/` | LLM claim extraction with source quotes; faithfulness check against the source text |
| `models/` | Naive, SARIMA, XGBoost baselines; text-index baselines |
| `revision/` | Bounded revision rule plus the comparison policies (never / always / small-step / text-always) |
| `evaluation/` | Walk-forward backtest using first-release values; MAE, RMSE, DM test, coverage; leakage checks |
| App | Forecast, evidence and revision views (`docs/UI_SPEC.md`); a Firestore data layer only after the rules are approved |

Part A record formats and the first milestone are specified in `research/forecast/PILOT_PROTOCOL.md` and `MILESTONE_1.md`.

## 7. How to run

```bash
# App
flutter pub get
flutter analyze        # expected: No issues found
flutter test
flutter run -d chrome

# Data (on the Mac)
export MOSPI_USER=...; export MOSPI_PASS=...      # never commit these
python3 data/scripts/fetch_cpi_api.py --base-year 2024 --from-year 2025 --to-year 2026
python3 data/scripts/build_cpi_series.py
```

## 8. Known issues / technical debt
1. There are no real Flutter tests; only a placeholder.
2. The notification kinds still include old plan-app names.
3. `research/pyproject.toml` and `pytest.ini` still describe the removed `reflica_bench` package. Update them when the pipeline is written.
4. `data/scripts/__pycache__/` exists locally. Make sure it stays git-ignored.
5. The MoSPI password was shared in chat earlier, so change it.
