# Reflica

**Reflica is being rebuilt as an AI forecasting and research platform for important Indian events**: clearly defined Yes/No questions, probability forecasts from several AI models with their evidence, an immutable forecast history, real outcomes, and transparent evaluation (Brier score, calibration, baselines).

**Current plan: `PROJECT_PLAN.md`** (15 Oct 2026): Reflica India, AI forecasting of India's economy and government policy (Minor 1: CPI inflation with evidence-aware revision; Minor 2: policy decisions with calibrated probabilities and abstention). Earlier direction: `NEW_DIRECTION.md` (history). The direction is chosen by the student; formal M.Tech guide approval is pending.
Implementation order: Documentation → Flutter UI → Python backend → connect the UI to real data. Exception: the December 2026 pilot is recorded by hand (`research/forecast/PILOT_PROTOCOL.md`).

## Status (14 Oct 2026)

- **Forecasting:** documentation and Firestore rules only. No forecasting code yet.
- **Old Reflica removed:** the plan-based app and the old thesis research were deleted from the main code on 14 Oct 2026. They are kept in branch `archive/old-reflica-2026-10-14` (and stage-1 in `archive/stage-1-2026-10-14`).
- **The app builds and runs again** after the clean-up (confirmed on the Mac, 14 Oct 2026): sign-in, dashboard shell, forecasting welcome card.

## Layout

```
reflica/
├── PROJECT_PLAN.md       # current research plan and guidelines (read first)
├── NEW_DIRECTION.md      # earlier direction documents (history)
├── PROGRESS.md           # dated progress log
├── firestore.rules       # Cloud Firestore rules (published 14 Oct 2026)
├── database.rules.json   # Realtime Database rules: locked (published 14 Oct 2026)
├── docs/                 # UI spec, architecture, Firebase (Spark) review, clean-up edits, rules tests
├── lib/                  # Flutter app: sign-in, landing and dashboard shell, notifications
├── android/, ios/, web/, macos/, linux/, windows/
├── test/                 # Flutter tests
└── research/
    └── forecast/         # forecasting protocol, Minor 1 design, milestone plan, literature
```

## Flutter app

Firebase project `reflica-593b4` (free Spark plan): Firebase Auth (Google sign-in) and Cloud Firestore. Web and Android.

```bash
flutter pub get
flutter analyze
flutter run -d chrome
```

## Owner

Sundram Awasthi · M.Tech CSE 2026–28 · GLA University.
