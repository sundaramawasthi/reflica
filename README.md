# Reflica

A living strategic-planning and decision-support platform. Reflica turns messy real-world information (text, voice, documents, images, video) into a structured, evidence-aware state graph that keeps updating as reality changes — so plans can be checked, traced, reported against, and repaired.

This repository holds two independent tracks that share one vision:

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

A separate Python benchmark for the thesis:

> *Attribute-aware revision of LLM-extracted state graphs under partial-satisfaction and capacity constraints — evaluated across add, edit, delete, and relationship-change operations against classical ATMS, constraint-programming, and LLM-regeneration baselines.*

All 7 benchmark categories and the cross-category synthesis (allocation / regimes / schema / baseline interface / metric matrix / reporting matrix) are locked. Phase 1 of the implementation is in — Category 1 floor cases with deterministic baselines B3 / B4a / B4b, no LLM code yet.

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
reflicaa/
├── lib/                # Flutter sources
├── android/, ios/, web/, macos/, linux/, windows/
├── assets/
├── test/               # Flutter tests
├── research/           # M.Tech Python workspace (separate venv, separate tests)
│   ├── reflica_bench/
│   ├── scenarios/
│   └── tests/
├── PROGRESS.md         # authoritative board — read this first
└── pubspec.yaml
```

## Owner

Sundram Awasthi · M.Tech CSE 2026–28 · GLA University.
