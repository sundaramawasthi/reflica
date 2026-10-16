# Reflica

AI forecasting research platform for Indian economic and policy outcomes (M.Tech research, GLA University).

- **Minor Project 1 title (official, per student, 16 Oct 2026):** *IndiaEconForecast / Reflica India: Hybrid AI Forecasting of Indian Economic and Policy Outcomes*.
- **Structure:** safer merge. Part A is an LLM forecasting benchmark of Indian yes/no events; Part B is numerical CPI forecasting with evidence-aware revision. A new plan document will be written. **Supervisor approval pending.**
- **Research:** [`docs/research_archive/`](docs/research_archive/) contains the literature, research gaps and the review paper draft. The gap matrix is in [`research/forecast/RESEARCH_GAP_MATRIX.md`](research/forecast/RESEARCH_GAP_MATRIX.md).
- **Status:** Flutter + Firebase app shell only. No forecasting code, data or experiments yet. Progress: [`PROGRESS.md`](PROGRESS.md).

## Layout

```
reflica/
├── PROGRESS.md           # status and condensed decisions log
├── firestore.rules       # Firestore rules (owner-only notifications; published)
├── database.rules.json   # Realtime Database rules (locked)
├── docs/                 # architecture, UI spec, Firebase (Spark) review, rules tests
│   └── research_archive/ # literature, research gaps, review paper
├── lib/  test/           # Flutter app and tests
└── research/forecast/    # Part A record protocol, backend milestone, gap matrix
```

## Flutter app

Firebase project `reflica-593b4` (free Spark plan): Firebase Auth (Google sign-in) and Cloud Firestore.

```bash
flutter pub get
flutter analyze
flutter run -d chrome
```

Old Reflica code: branch `archive/old-reflica-2026-10-14`.

Owner: Sundram Awasthi · M.Tech CSE 2026–28 · GLA University.
