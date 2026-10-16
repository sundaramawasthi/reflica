# Reflica forecasting UI: specification

Date: 14 October 2026. Status: **proposed; needs the user's approval before Phase 2 starts.** M.Tech guide approval of the research direction is pending.
Minor 1 direction: safer merge (this spec covers Part A views; Part B views to be designed). Architecture: `ARCHITECTURE.md`. Record formats: `../research/forecast/PILOT_PROTOCOL.md`.

Implementation order: Documentation → Flutter UI → Python backend → connect the UI to real data. Exception: the December 2026 pilot is recorded by hand (`../research/forecast/PILOT_PROTOCOL.md`). UI work starts only after the clean-up edits (done 14 Oct 2026) are done and `flutter analyze` is clean. (The stage-1 merge is cancelled.)

This describes the desired experience. It does not give permission to rebuild the app or discard existing functionality. Phase 2 extends the existing Flutter app.

## 1. Identity and visual direction

Reflica is becoming an AI forecasting and research platform, starting with future events in India. It must feel like a **serious forecasting research platform**: scientific, clear about probabilities and uncertainty, evidence-backed, and transparent about past performance. It must not look like a productivity app, a social network, a trading terminal or a generic AI chat.

- Deep navy or indigo navigation; white or soft-neutral workspace; blue and violet as restrained accents.
- Green for verified positive status and red for negative outcomes, only where appropriate. **Never colour alone**: every status also has a text label or icon.
- Rounded cards, subtle borders, consistent spacing, clear typography, restrained shadows; no heavy gradients or animation.
- Extend the existing `AppColors` / `AppText` / `BrandMark` (`lib/theme/app_theme.dart`, `lib/widgets/brand_mark.dart`) instead of a new design system.
- Responsive by **width** (existing rule): sidebar on desktop; drawer on mobile and tablet; cards stack vertically on narrow screens.

### The dashboard mockup (14 Oct 2026)

Use it as **layout inspiration only**: dark sidebar, welcome banner, four summary cards, upcoming questions, performance chart with tabs, insights, domain chart, recent activity.
Everything inside the mockup is invented and must **not** appear as real content:
- the counts and scores (248 questions, 86 active, 142 resolved, Brier 0.182, "+12 this month", "8% vs last month");
- the insight percentages (+12%, −11%, +22%);
- the model names (GPT-4o, Claude 3.5, Gemini 1.5) and the activity items.

Also not carried over: the "Health" domain (not in the plan) and question wording such as "Will the RBI change the repo rate in the next policy…", which is too vague for our rules.

## 2. Navigation

```
Sidebar / drawer
├── Home                 /dashboard        (signed-in landing; existing route reused)
├── Question Bank        /questions
│     └── Question Details   /questions/:id
├── Forecasts            /forecasts
│     └── Forecast Details   /forecasts/:id
├── History              /history
├── Scoreboard           /scoreboard
├── Insights             /insights         (explanatory empty state until real results exist)
└── Settings             /settings         (existing route; becomes a real screen)

Old plan routes (/plans, /plan, /new-plan, /graph, /scenarios, /documents): removed with the old plan app
on 14 Oct 2026 (archived in branch archive/old-reflica-2026-10-14).
Signed-out landing: existing HomeScreen at "/", rebuilt for forecasting
```

No navigation item leads to a blank or misleading screen. Every screen has a proper empty state.

## 3. Screens

### 3.1 Home
- **Top bar:** title, search over questions and topics, the existing notifications bell, the account menu.
- **Welcome:** "AI Forecasting for India", followed by "Explore upcoming events, inspect model predictions, and evaluate forecasts against real-world outcomes." Actions: *Explore Questions*, *View Forecasts*. It makes no claim that Reflica predicts reliably.
- **Summary cards:** validated questions · active forecasts · resolved questions · evaluation status. Real data only. Otherwise an empty state ("No resolved questions yet").
- **Upcoming questions:** title, domain, forecast deadline, status, link.
- **Research performance preview:** shown only with real, sufficient data (views: model, domain, news vs no-news, India vs Western, historical vs prospective). Otherwise it explains what data is needed.
- **Recent activity:** forecasts published, questions resolved, reports generated. Development placeholders are labelled.

### 3.2 Question Bank
- **Row or card:** ID, wording, domain, forecast deadline, resolution date or window, status, forecast count (real only).
- **Status values:** Draft · Validated · Open for Forecasting · Forecast Frozen · Resolved · Invalid. Status is *derived* from records using the ordered rules in `PILOT_PROTOCOL.md` section 4.1, never typed by hand. A question past its deadline is never shown as open, even with 0 forecasts.
- **Search and filters:** domain, status, deadline, resolution date, horizon, India vs comparison region.
- **Sort:** deadline, newest, domain.

### 3.3 Question Details
Full wording · why it matters · forecast deadline · resolution date or window · exact Yes/No rule and invalid rule · official source · evidence cutoff · domain, region, horizon · paired comparison question · forecast records. For an RBI question, show the decision, reference rate, comparison rule and source. An AI-generated question is not "validated" until it passes the documented checks.

### 3.4 Forecasts list
Question · model and version · P(Yes) · timestamp · deadline · condition (With news / Without news) · record status (On time / Late / Failed, from `timing_status` and `status`). A visible note says a probability is a model estimate, not a guarantee.

### 3.5 Forecast Details
- **Probability:** P(Yes) displayed prominently, with P(No) beside it.
- **Model and configuration:** model and version, created and recorded times, prompt version, config hash, news on/off.
- **Evidence:** each source with its publication date and URL. Published facts are visually separated from the model's reasoning.
- **Uncertainty and limitations:** missing or conflicting evidence, abstention (Minor 2).
- **Record history:** later versions shown as separate records, linked by `supersedes`, plus the record hash and, only if an external timestamp service has been adopted (D7), its timestamp evidence. The UI never labels a record "time-verified" otherwise.

### 3.6 History
- **Filters:** resolved/unresolved, model, domain, forecast date, resolution date, outcome (Yes, No, Invalid).
- **Each entry links** to its frozen forecast and its resolution record.
- **For resolved questions:** original probability, outcome, source, resolution date, and the Brier score (yes/no outcomes only).
- **Invalid** outcomes are clearly marked and excluded from the Brier score. Unresolved forecasts are never shown as successes or failures.

### 3.7 Scoreboard
- **Metrics:** Brier (lower is better) · calibration · accuracy at a stated threshold, where suitable · number of eligible resolved forecasts · failure and abstention rates · cost and runtime.
- **Every metric shows** its population, time period and sample size.
- **Primary leaderboard (D1):** the latest **eligible** forecast per question, model and condition, as defined in `PILOT_PROTOCOL.md` section 7.1 (ok status, valid probability, hashes valid, on time, Yes/No resolution, not invalidated). Failure rate and late counts are shown beside it; invalid and unresolved questions are counted, never scored as wrong. Other records appear only in clearly labelled secondary views.
- **Comparisons:** by model, domain, news condition, India vs Western (labelled **exploratory**, D5), historical vs prospective. Historical (A3) results are labelled and never merged into the prospective ranking.
- **Small samples** show "Insufficient data" instead of a ranking. Incompatible question sets are never pooled.

### 3.8 Insights
Sections for the research questions: does news help, domain differences, India vs Western, past vs future, failure, abstention and calibration. Each insight links to its experiment, dataset version and evaluation report. Until then the screen explains that findings appear after forecasts are resolved and evaluated.

### 3.9 Settings
Account, display and notification preferences (where supported); research information and app version. (No Legacy Plans entry: the plan app was deleted on 14 Oct 2026.) No model controls, and nothing that suggests users can change the benchmark protocol.

## 4. Shared states and accessibility
Every data screen handles: loading · empty · error · offline · insufficient research data · invalid or unresolved records.
Shared components keep badges, cards, tables, filters, dates (IST display) and probability displays consistent. Text stays readable, tap targets are adequately sized, charts are labelled, and the layout is keyboard-navigable where Flutter supports it.

## 5. Data in the first UI pass
- **Typed local demo objects** (planned, not yet created) will live under `lib/forecast/demo/`. They are shown **only** in a development preview with a visible "Sample data, not research results" banner, behind a `--dart-define=FORECAST_DEMO=true` flag.
- Normal builds show honest empty states.
- **No new Firestore collections, rules or backend calls** in Phase 2.
- Demo objects use the same field names as `PILOT_PROTOCOL.md`, so swapping in real data later is a data-source change, not a redesign.

## 6. Implementation stages (one at a time, user review after each)

1. Shared theme extensions, navigation and responsive shell.
2. Home.
3. Question Bank and Question Details.
4. Forecasts list and Forecast Details.
5. History.
6. Scoreboard.
7. Insights and Settings.

### Files (proposed; the user writes them)

| Reuse as-is | `main.dart` Firebase init, `auth_service.dart`, `auth_gate.dart`, `theme/app_theme.dart`, `brand_mark.dart`, `responsive.dart`, `dashboard_top_bar.dart` (bell, user menu) |
|---|---|
| **Change** | `widgets/dashboard/dashboard_sidebar.dart` (forecasting items; recent-plans list already removed in the clean-up) · `screens/dashboard_screen.dart` (body becomes the forecasting Home) · `main.dart` (add routes; keep all old ones) · `screens/home_screen.dart` + landing widgets (copy only) · `/settings` route (real screen) |
| **Add** | `lib/forecast/models/` (question, forecast, resolution) · `lib/forecast/data/forecast_source.dart` (interface; empty source + demo source) · `lib/forecast/widgets/` (status badge, probability display, summary card, empty state, filter bar) · `lib/forecast/screens/` (question_bank, question_details, forecasts, forecast_details, history, scoreboard, insights, settings) |
| **Untouched** | `NotificationService` (forecast-deadline kinds added later), Firestore data. Plan code was deleted on 14 Oct |

### Tests (run on the Mac: `flutter analyze`, `flutter test`)
- Each new screen renders its **empty state** without demo data.
- Navigation: every sidebar item opens its screen; no item or link leads to a removed plan route.
- The demo banner appears only when `FORECAST_DEMO` is on, and demo objects never appear when it is off.
- Status badges show text, not just colour.
- Status derivation (`PILOT_PROTOCOL.md` §4.1) on both sides of the deadline: `deadline − 1 s` → "Open for Forecasting"; exactly `deadline` → "Forecast Frozen"; a resolved question → "Resolved" regardless of the deadline. (Uses an injectable clock, not the device time.)
- Models parse a `PILOT_PROTOCOL.md` example record (JSON round-trip).
- Brier is shown only for `yes`/`no` outcomes.
