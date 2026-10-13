# Reflica

**Current direction (14 Oct 2026):** Reflica is evolving into an **AI forecasting and research platform for important Indian events**: clearly defined Yes/No questions, probability forecasts from several AI models with their evidence, immutable forecast history, real outcomes, and transparent evaluation (Brier score, calibration, baselines). Read `NEW_DIRECTION.md` first. The direction is chosen by the student; formal M.Tech guide approval is pending.

Forecasting docs: `docs/UI_SPEC.md`, `docs/ARCHITECTURE.md`, `research/forecast/` (`PILOT_PROTOCOL.md`, `MINOR1_DESIGN.md`, `MILESTONE_1.md`, `LITERATURE_FORECASTING.md`). Nothing in the forecasting workstream is implemented yet.

*Previous description (the existing app below still implements it):* a living strategic-planning and decision-support platform that turns messy real-world information into a structured, evidence-aware state graph.

This repository holds two independent tracks:

## 1. Flutter product (`lib/`, `android/`, `ios/`, `web/`, …)

The user-facing app. Runs on Chrome and Android today.

- Firebase Auth (Google sign-in: Firebase popup on web, native in-app bottom-sheet on Android), Firestore with offline persistence enabled.
- Landing page, dashboard, 4-step New Plan wizard across 7 input modes (text / structured form / voice / documents / images / video / live camera), live mind-map viewer, inline editor, per-write audit notifications.
- Width-reactive layouts across every screen.
- See `PROGRESS.md` for the authoritative board.

Run it:

```bash
flutter pub get
flutter run -d chrome       # web
flutter run -d <device-id>  # android/ios
flutter analyze             # should print "No issues found!"
```

## 2. M.Tech research workspace (`research/`)

A separate Python benchmark for the **previous** thesis topic (paused since 2026-10-13, preserved unchanged):

> *Attribute-aware revision of LLM-extracted state graphs under partial-satisfaction and capacity constraints — evaluated across add, edit, delete, and relationship-change operations against classical ATMS, constraint-programming, and LLM-regeneration baselines.*

Current state:

- **Benchmark v0.2.0:** 63 scenarios across 7 categories, fingerprinted and frozen.
- **Baselines:** B3 (reachability), B4a (ATMS), B4b (OR-Tools CP-SAT), plus LLM baselines B1/B2.
- **B5 (the Reflica revision engine) v0.1.0:** frozen; agrees with gold on all 63 scenarios.
- **Natural-language pilot:** complete (144/144 calls).
- **Tests:** 203 passing.

The full 63-scenario experiment is paused. The new forecasting workstream lives in `research/forecast/` (documentation only so far).

Run it:

```bash
cd research
python3 -m venv .venv
. .venv/bin/activate
pip install -e ".[dev,csp]"
pytest
```

## Repository layout

```
reflica/
├── lib/                # Flutter sources
├── android/, ios/, web/, macos/, linux/, windows/
├── assets/
├── test/               # Flutter tests
├── research/           # M.Tech Python workspace (separate venv, separate tests)
│   ├── reflica_bench/
│   ├── scenarios/
│   └── tests/
├── NEW_DIRECTION.md    # authoritative research direction — read this first
├── docs/               # forecasting UI spec and architecture
├── PROGRESS.md         # dated progress log and status board
└── pubspec.yaml
```

## Owner

Sundram Awasthi · M.Tech CSE 2026–28 · GLA University.
