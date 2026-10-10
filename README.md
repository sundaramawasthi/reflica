# Reflica

**An AI research partner for scientific discovery.**

Reflica aims to help scientists and researchers track scientific claims, the evidence supporting them, the assumptions behind them, and how new or conflicting findings affect existing conclusions.

**Core idea:** represent scientific knowledge as an evidence-aware graph connecting claims, evidence, assumptions and contradictions. When new results, failed replications or retractions arrive, investigate which conclusions should change, which should remain valid, and why.

**Principles**

- **Human-led science:** researchers remain responsible for scientific judgments; AI provides suggestions and explanations.
- **Evidence traceability:** every supported claim and recommendation should link to its underlying evidence.
- **Explicit uncertainty:** distinguish established findings, uncertain interpretations, assumptions and unresolved contradictions.
- **Measurable progress:** evaluate proposed methods against existing approaches before claiming improved scientific discovery.
- **Incremental validation:** begin with AI/CS research scenarios, then expand to other scientific domains in collaboration with domain experts.

This is a direction under investigation, not a description of current capabilities. See `research/SCIENCE_DIRECTION.md` for the research plan and `PROGRESS.md` for status.

## Current foundation

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

Current state:

- **Benchmark v0.2.0:** 63 scenarios across 7 categories, fingerprinted and frozen.
- **Baselines:** B3 (reachability), B4a (ATMS), and B4b (OR-Tools CP-SAT); B1/B2 LLM prompt-and-schema baselines used in the pilot.
- **B5 (the Reflica revision engine) v0.1.0:** frozen and agrees with gold on all 63 scenarios in the plan/state-graph benchmark; not yet connected to the experiment runner.
- **Natural-language pilot:** complete (144/144 calls).
- **Tests:** 203 passing.

The full 63-scenario experiment is next.

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
├── PROGRESS.md         # authoritative board — read this first
└── pubspec.yaml
```

## Owner

Sundram Awasthi · M.Tech CSE 2026–28 · GLA University.
