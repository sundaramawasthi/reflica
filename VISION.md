# Reflica — Vision

> Reflica is a JARVIS-like assistant that connects to your world, turns your
> plans, work and situations into an accurate living mind map, keeps it correct
> as reality changes, suggests what to do, lets you decide, and learns from
> every decision — for individuals, organizations, governments and disasters.

## 0. Current status (9 October 2026)

Stage: working prototype + research validation. Details live in `PROGRESS.md`.

| Area | Status |
|---|---|
| Flutter app (sign-in, dashboard, New Plan wizard, 2D mind map, Firestore + offline, notifications) | Built (Stage 0+) |
| AI plan extraction in the app (Gemini "READ" step) | Not built — the app still creates a placeholder seed graph |
| B5 wired into the app (change → affected nodes → explain → approve) | Not built (Stage 2) |
| Benchmark v0.2.0: 63 scenarios, 7 categories, independent ground truth | Built and frozen |
| Baselines B3 (reachability), B4a (ATMS), B4b (CP-SAT); conditions B1, B2, extraction→B4b, extraction→B5 | Built |
| Natural-language pilot (16 scenarios × 3 = 144 calls, Nemotron-3-Ultra, config v1.7) | Done; one genuine extraction failure (T7.2 invented rule) |
| B5 v0.1.0 | Frozen; 0 disagreements with gold on 63 scenarios; 203 tests passing |

### UI pages (routes in `lib/main.dart`)

| Page | Route | Status |
|---|---|---|
| Landing page | `/` (signed out) | Built |
| Sign-in gate | `/` (AuthGate) | Built |
| Dashboard | `/dashboard` | Built |
| New Plan wizard | `/new-plan` | Built (6 of 7 input modes end to end) |
| My Plans | `/plans` | Built |
| Plan detail + mind map | `/plan` | Built; no explain/approve step yet |
| Notifications | panel | Built |
| Combined graph | `/graph` | Placeholder |
| Scenarios (what-if) | `/scenarios` | Placeholder |
| Documents | `/documents` | Placeholder |
| Settings | `/settings` | Placeholder |

7 of 11 pages are built. The UI is not connected to the research engine:
no AI extraction (the app creates a placeholder seed graph) and no B5 behind
plan changes. Planned after the experiment (Stage 1–2).

### Rough progress (judgement, not measured)

| Area | Done | Remaining |
|---|---|---|
| UI pages (~55%) | 7 of 11 pages | `/graph`, `/scenarios`, `/documents`, `/settings` |
| App logic (~35%) | Sign-in, Firestore + offline, save/edit/delete, notifications | AI extraction + confirm step, B5 in app, explain, approve/reject |
| Research (~65%) | Benchmark, gold answers, B3/B4a/B4b, B5 frozen, pilot, first literature pass | Deep literature review, thesis writing |
| Experiment (~50%) | Protocol v2, runner incl. B5, statistics, 63 scenario texts, 233 tests, dry run (`research/experiments/full_experiment/`) | Owner's 5 open decisions, NVIDIA key rotation, paid run (567 calls), H1–H3 results, failure analysis |
| Vision (~5%) | Written down (this file) | Voice, integrations, watcher, camera, world knowledge, memory, disaster mode; 3D/AR paused |

Known B5 limitations: matching gold on clean input does not prove robustness;
the repair-within-scope path is not yet exercised; UNCERTAIN vs
REQUIRES_REEVALUATION matches gold only 11/19 times.

Contribution stance: B5 is not claimed as novel. The contribution is an
evaluated combination (LLM extraction → dependency-aware revision →
determinability check) on natural-language input, tested against hypotheses:

- H1 — fewer over-flips and missed changes on Cat 1–4.
- H2 — non-inferior to extraction→B4b on Cat 5–6 (margin 0.05).
- H3 — less false confidence on Cat 7, with false abstention ≤ 0.15.

Next steps, in order:

1. Protocol v2 and runner ready (see `research/experiments/full_experiment/`); owner answers 5 open decisions.
2. Run the full 63-scenario experiment.
3. Statistics (95% CIs, paired tests) and H1–H3 verdicts.
4. Failure analysis and component ablations.
5. Deep literature review and contribution statement.
6. Thesis writing.
7. Product: Gemini extractor, then B5 inside the app.

## 1. Core principle — the loop

```
                     REFLICA: LIVING WORLD MODEL
                                 │
 SEE & CONNECT ──→ REPRESENT ──→ KNOW ──→ VERIFY ──→ SUGGEST
 You: text, voice,  Accurate 2D   Current     Satellites,   Hints, risks,
 docs, camera,      mind map      affairs,    sensors;      predictions
 "Hey Reflica"      (foundation   policies,   confirmed vs  (never
 Auto: calendar,    first)        internet    unconfirmed   overclaiming)
 email, files,                                                  │
 tasks, GitHub                                                  │
 LEARN ←────────── UPDATE ←────────── HUMAN DECIDES & ACTS ←────┘
 User's thinking   Only what changed  Final say is always human;
 + history         (B5 engine)        Reflica acts only with approval
```

## 2. The eight parts

| # | Part | What it does |
|---|---|---|
| 1 | See & connect | Text, voice, documents, images, video, camera — plus automatic collection from calendar, email, files, tasks, GitHub |
| 2 | Represent | AI builds an accurate 2D mind map (goals, tasks, risks, links, deadlines, with source and confidence), stored once in Firebase as the single source of truth |
| 3 | Know | Adds live world knowledge: news, government policies, internet |
| 4 | Verify | Cross-checks conflicting sources against independent evidence (satellites, sensors); marks confirmed vs unconfirmed |
| 5 | Suggest | Informs, predicts, suggests, prepares drafts — always honest about uncertainty |
| 6 | Human decides | User approves, edits or ignores; Reflica acts only with approval |
| 7 | Update | The B5 engine revises only what is affected when anything changes |
| 8 | Learn | Remembers the user's habits, decision style and past outcomes |

Users call Reflica anytime ("Hey Reflica", a shortcut, or a button), or let it
watch connected tools and alert them. Answers arrive as voice, notifications
and the 2D mind map.

## 3. One engine, every level

| Individual | Organization | Government | Disaster |
|---|---|---|---|
| Exams, research, career — a personal assistant | Strategy, projects, operations | City planning, policy | Scan the site → condition → share with responders → live updates |

## 4. Research problems

| # | Problem | Stage |
|---|---|---|
| 1 | Reality → accurate living graph (multimodal extraction) | Next |
| 2 | **Continuous revision when facts change (B5)** | **Now — M.Tech thesis** |
| 3 | Evidence fusion when sources conflict | Next |
| 4 | Human–AI decision loop (calibrated suggestions, re-planning) | PhD |
| 5 | Personal decision models (with privacy) | PhD |
| 6 | Collective decision memory | Long term |
| 7 | 2D vs 3D spatial-view study | Paused |

Grand goal: a living world model for human decision-making — a shared,
verifiable, continuously updated model of reality in which humans and AI plan
together.

## 5. Architecture

```
 INTEGRATIONS  calendar, email, files, GitHub, news, satellites, camera
 AI LAYER      extract → verify → B5 revise → suggest → learn
 DATA          living plan graph in Firebase (single source of truth)
 VIEWS         2D mind map (Flutter) + voice + notifications
 INTERACTION   touch, keyboard, "Hey Reflica"
 ACROSS ALL    privacy, consent, activity logs, human approval
```

Each layer is separate, so one can change without breaking the others.

## 6. Roadmap

| Stage | Build | Research |
|---|---|---|
| Now | Current app (2D, 7 input modes) | Finish the 63-scenario experiment + paper |
| Next 6–12 months | "Hey Reflica" voice + calendar and file connections | — |
| 1–2 years | Watcher, suggestions, email drafts, camera input, world knowledge | Problems 1 and 3 |
| PhD / startup | Actions with approval, personal memory, disaster mode with satellites | Problems 4 and 5 |
| Long term | Organization and government scale | Problem 6 |

## 7. Principles

1. Accuracy first — the map must be right before anything else.
2. One source of truth — every view shows the same data.
3. Grounded in reality — live data, not guesses.
4. Verify, don't assume — show what is confirmed.
5. Humans decide — Reflica suggests, people act.
6. Always learning — from each user and from history.
7. Privacy by design — the user controls what is connected and can disconnect anytime.
8. Helps everyone — from one student to a whole nation.

## 8. What is real today vs. later

| Buildable today | Partly possible | Not yet possible |
|---|---|---|
| Text, voice, files → mind map | Deep personal decision modelling | Reading thoughts from the brain |
| Calendar, email, file connections | Camera scan → full situation understanding | Certain predictions of physical events |
| "Hey Reflica" voice assistant | Satellite verification (passes every few hours) | Fully autonomous decisions |
| B5 revision engine | Collective learning across organizations | |

## 9. Paused

- 3D holographic view
- AR view
- 2D vs 3D research study

These can return at any time as extra views of the same data; nothing else
needs to change.
