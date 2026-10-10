# Reflica — Platform Audit

> **Status:** architecture audit and product decisions for the long-term Reflica platform, based on a read-only inspection of the repository on 2026-10-10. Proposed capabilities are not implemented unless marked so. Companion to `SCIENCE_DIRECTION.md` and `RESEARCH_OUTLINE.md`; implementation status lives in `../PROGRESS.md`.

**Two levels — do not conflate**

- **Locked M.Tech thesis (`PROGRESS.md`, 2026-10-07):** attribute-aware revision of LLM-extracted state graphs under partial-satisfaction and capacity constraints, on the frozen 63-scenario plan/state-graph benchmark. This document does not change that scope.
- **Long-term product vision:** an AI research partner that researchers connect to their ongoing work — papers, datasets, code, notebooks, videos, lab records, simulations and tools — and that helps them plan, run, compare and explain research tasks under human control. The thesis engine is one component (Layer 4). Any change to thesis scope is to be discussed with the supervisor.

---

## 1. Decisions (2026-10-10)

1. **Bridge:** a local Python service for initial development, behind a clearly defined interface so it can be replaced or supplemented by a hosted service later.
2. **First input:** CSV experiment data plus a research-question description. CSV is the **first vertical slice, not the product boundary**; the architecture must support papers/PDFs, videos, notebooks, code and other connected tools as future adapters.
3. **Audit location:** this file.
4. **Dependencies:** service-specific dependencies go in a separate optional `service` extra; the core `reflica-bench` dependencies are unchanged.
5. **Package location:** `research/reflica_service/`.
6. **Initial operations:** `describe`, `regress` and `sweep` only, each with validated inputs, explicit schemas and documented outputs:
   - `describe` — validate the CSV and report columns, missing values, basic statistics and data-quality issues.
   - `regress` — fit a supported, built-in statistical regression model and report diagnostics and uncertainty.
   - `sweep` — evaluate approved parameter combinations with the fitted model, record results and flag extrapolation beyond the observed data range.

   No arbitrary user-supplied code is executed. Every run requires explicit approval and a reproducible run record. ("Regression" here means statistical regression, not software regression testing.)

**Routing principle:** each question is routed to the method that can actually answer it. B5 propagates *declared* relationships; it does not discover real-world causal laws from data. Statistical analysis, experimental-design knowledge and, where relevant, scientific simulators are separate methods.

---

## 2. Findings from the repository

- **The app does not extract anything yet.** Mind-map nodes come from a deterministic seed graph (`lib/services/plan_repository.dart`); `PROGRESS.md` records this as a placeholder. `firebase_ai` is a declared dependency but is not called anywhere in `lib/`.
- **Uploaded files are not stored.** `InputArtefact` (`lib/models/plan.dart`) records only file name, MIME type and size. There is no Firebase Storage; no input mode reads file contents.
- **The app and the Python workspace are not connected.** No API, service or bridge exists.
- **The Python workspace is the most mature part:** typed graph schema with provenance and confidence (`schema.py`), change events, a rule formula grammar, strict LLM extraction schema (`extraction_schema.py`), baselines B3/B4a/B4b, the B5 engine, evaluator, frozen manifests and a reproducible, resumable pilot runner. 203 tests are recorded as passing.
- **B5 answers a deterministic form of "if X changes, what happens to Y?"** It recomputes only the downstream closure of a change under declared rules and abstains when the answer is not determined. It is not statistics and not causal inference from data. It is frozen for the plan/state-graph benchmark, not connected to the experiment runner, and not adapted or tested on scientific data.

---

## 3. Target architecture (seven layers, proposed)

| Layer | Purpose |
|---|---|
| 1. Research workspace | Projects, files, connections, permissions, approvals (Flutter + Firebase) |
| 2. Ingestion | Separate typed adapters per input type: CSV first; PDF, notebook/code, video, lab records later |
| 3. Research model | Typed graph of variables, parameters, conditions, runs, results, claims, evidence, hypotheses, assumptions, sources and uncertainty |
| 4. Reasoning | Dependency paths (B3), assumptions (B4a), constraints and feasible combinations (B4b), declared-rule revision (B5) |
| 5. Execution | Approved, built-in analyses and parameter sweeps; reproducible run records; later a sandbox for user code |
| 6. Research guidance | Suggested analyses and next experiments, always labelled as unverified suggestions |
| 7. Verification and learning | Compare predictions with outcomes, preserve provenance, revise the research model |

A human approves every action that executes and every change accepted into the model.

---

## 4. Capability mapping

A = reusable as-is · B = reusable after adaptation · C = missing · D = uncertain, needs further inspection

| Layer | Component | Status | Notes |
|---|---|---|---|
| 1 | Flutter shell, auth, dashboard | A | Runs on web and Android |
| 1 | Firestore with offline persistence | A | Can hold project records |
| 1 | `Plan` model → research project | B | Add project fields, connections, approvals |
| 1 | Sharing, roles, connection permissions | C | Not present |
| 2 | Seven input-mode UI | B | Collects files but does not read them |
| 2 | File storage | C | No Firebase Storage; local service storage proposed for v1 |
| 2 | CSV / PDF / code / video adapters | C | None exist |
| 2 | LLM extraction + `extraction_schema.py` | B | Strict typed output, tested in pilot; built for plan prose |
| 2 | `firebase_ai` in the app | D | Declared, unused; decide app-side vs service-side extraction |
| 3 | `schema.py` Graph/Node/Edge | B | Extend with research types and richer provenance |
| 3 | Edge types | B | Add contradicts, measured_in, produced_by, controls_for, etc. |
| 3 | `Rules` formula grammar | B | Can express declared relationships; not fitted models |
| 3 | Uncertainty representation | C | Single confidence value only |
| 4 | B3 reachability | A/B | Which nodes a change can reach |
| 4 | B4a ATMS | B | Assumptions and alternative justifications |
| 4 | B4b CP-SAT | B | Feasible parameter combinations under constraints |
| 4 | B5 revision engine | B | Declared-rule revision; not statistical or causal |
| 5 | Execution layer, approval gate, run records | C | Pilot runner's logging/resume is a useful pattern |
| 5 | Parameter-sweep runner | C | Not present |
| 6 | Next-step suggestions | C | Not present |
| 7 | Evaluator, ground truth, frozen manifests | B | Template for per-layer validation |
| 7 | Prediction-vs-outcome loop | C | Not present |
| — | App ↔ Python bridge | C | Decision 1 |
| — | Existing tests and frozen benchmark | A | Regression guards; must stay unchanged |

---

## 5. First vertical slice (MVP)

**CSV upload → validated dataset → researcher confirms variables and units → question and analysis plan → explicit approval → built-in analysis and parameter sweep → recorded results and uncertainty → explanation → human-reviewed update.**

- Only built-in, versioned analyses run; no user-supplied code is executed.
- Results on observational data are labelled as associations, not causes; extrapolation beyond observed ranges is flagged.
- The plan step separates what existing data can answer, what needs a model or simulation, and what needs a new physical experiment.

---

## 6. Risks

| Risk | Mitigation |
|---|---|
| Presenting correlation as causation | Fixed labels; causal wording only for controlled designs |
| Executing untrusted code | v1 runs built-in analyses only; sandbox is a later, separate project |
| Wrong variables or units | Typed validation; mandatory human confirmation |
| "200 experiments in a second" expectations | True only for computation on existing data or cheap simulations; physical experiments take real time |
| Scope too wide | CSV first, then PDF, then code/notebooks, video last |
| Local service exposed to the network | Bind to localhost; token; size limits |
| Thesis drift | Thesis scope unchanged; changes discussed with supervisor |

---

## 7. Implementation sequence (proposed)

1. Local Python service and file handling.
2. CSV adapter and research-model schema (extending `schema.py`, with tests).
3. Confirmation UI reusing the mind map and node editor.
4. Built-in analyses, sweep runner, approval gate and run records.
5. Explanation layer with uncertainty and association/causation labels.
6. B5 adaptation for declared relationships and runner integration, validated on a small controlled benchmark.
7. PDF/claims adapter (`SCIENCE_DIRECTION.md`), next-step suggestions, code/notebook execution in a real sandbox.
8. Video and lab-tool connections; domain tools (including quantum simulation) where justified.

Each step must leave the existing tests passing and the frozen benchmark manifest unchanged.

---

## 8. Long-term intelligence vision (proposed — not implemented)

> **Status:** this section describes where Reflica is meant to go. None of these capabilities exists today except where a row says so. It does not change the locked M.Tech thesis, and it is not evidence that the combination will produce discoveries; each capability must be shown to improve research quality before it is relied on.

**Aim.** An AI research partner that does as much of the research workflow as it reliably can — understanding the goal, investigating what is known, planning and running approved work, learning from results and recommending what to do next — while the scientist keeps control of consequential decisions. The guiding question for every feature: *does it help a scientist understand evidence, make a better research decision, test an idea, or discover something they would otherwise have missed?*

### 8.1 Six capabilities

| Capability | Intended purpose | Evidence that would show it is useful | Limitations and risks | Exists today |
|---|---|---|---|---|
| **Vision intelligence** | Hold the scientist's ultimate goal, motivation, intended beneficiaries and success criteria; keep daily work connected to them; notice when a result does not actually achieve the goal. | Researchers rate goal summaries as accurate; recommendations that cite the goal are judged more relevant than ones that do not, in blinded comparisons. | Goals can be misread or drift; the system must restate and confirm them rather than infer. Over-steering towards one stated goal can hide legitimate changes of direction. | Nothing. The Flutter `Plan` holds a title and free text only. |
| **World intelligence** | Track relevant, dated, sourced developments — new papers, failed replications, retractions, competing approaches, costs, regulations, real-world conditions — and explain how they affect the current direction. | Precision and recall of flagged developments against expert judgement; share of alerts researchers find relevant; time saved versus their usual monitoring. | Misinformation and low-quality sources; stale or paywalled data; alert fatigue. Every item must carry source, date and status (verified fact, emerging report, forecast, interpretation). Monitoring external services may expose what a researcher is working on. | Nothing. |
| **Human-aware (emotional) intelligence** | Adapt explanations, level of detail and plans to the researcher's stated experience, workload, preferences and constraints; respond constructively to failed experiments without hiding bad results. | Researchers report the interaction as helpful and honest in user studies; no increase in misreported results; preferences are respected. | **Unsupported emotional inference** — the system must not claim to know how someone feels; it responds to what they state. False reassurance, manipulation or paternalism. Sensitive personal data needs explicit consent, minimal retention and the ability to delete it. | Nothing. |
| **Safety and impact intelligence** | Assess potential benefits and harms to people, society and the environment; identify misuse potential, unintended consequences, missing validation and when qualified human review is required. | Expert reviewers agree with the hazards and required reviews it identifies; it does not miss known hazards in seeded test cases; no result is labelled safe without the validation behind it. | Incomplete hazard knowledge; false confidence from a checklist; dual-use information. It must never give a simple "safe" verdict on incomplete evidence, and must defer high-stakes decisions to qualified people. | Nothing. Only the analysis-level rules in `reflica_service/NOTES.md` (no causal claims from correlation, no extrapolation). |
| **Progress intelligence** | Track agreed objectives, milestones, experiments, deadlines, completed work and blockers from actual project records; flag stalled work constructively and suggest a manageable next action. | Researchers find check-ins timely and useful rather than intrusive; blockers are resolved faster than without it; schedules can be changed easily. | Surveillance concerns; nagging; treating slow progress as laziness. It must ask about blockers, accept pauses and changes of direction, and use only records the researcher chose to share. | Nothing for research projects. |
| **Scientific reasoning and experimental intelligence** | Connect questions, papers, claims, hypotheses, datasets, methods, experiments, results and conclusions; find contradictions, gaps and testable hypotheses; prepare and run approved analyses, simulations or experiment plans; revise only the affected conclusions when evidence changes; recommend the most informative next step. | Revision correctness and traceability against fair baselines (`SCIENCE_DIRECTION.md`); hypotheses judged novel and testable by experts; analyses that are reproducible from their run records. | LLM extraction errors; hypotheses presented as findings; over-automation of consequential actions; correlation read as causation. AI-generated hypotheses are always labelled as unverified. | **Partly.** B5 revises declared relationships on the frozen plan/state-graph benchmark only (not scientific claims). `reflica_service` implements CSV ingestion and `describe@1` with provenance and a time limit. Everything else is proposed. |

### 8.2 The full research workflow (target)

1. Understand the scientist's vision, constraints and success criteria (asking, not assuming).
2. Investigate existing knowledge and relevant world conditions.
3. Build a traceable model of the research and its evidence.
4. Identify promising gaps and formulate testable hypotheses, labelled as unverified.
5. Plan analyses, simulations or experiments, with the reason for each.
6. Validate methods, resources, risks and permissions; obtain approval before consequential actions.
7. Run authorised work through validated tools and evaluate results against predefined criteria.
8. Update only the conclusions affected by new evidence, recording what changed and why.
9. Assess benefits, safety, uncertainty and real-world feasibility.
10. Monitor progress and blockers.
11. Recommend the most useful next step, considering uncertainty, cost, time and feasibility.
12. Produce a reproducible report: methods, results, failed tests, sources, limitations and open questions.

Some steps can eventually run automatically (for example a CSV analysis or a safe simulation). Operating lab equipment, handling hazardous materials, spending money or research involving people always requires human oversight and the relevant permissions. The aim is maximum *useful* autonomy, not uncontrolled autonomy.

### 8.3 Shared research-project model (proposed)

All capabilities read and write one project model rather than separate features. It connects:

- the scientist's **vision** and success criteria;
- **research questions** and **hypotheses** (with status: proposed by AI, accepted by researcher, tested, supported, refuted);
- **sources**, **claims** and **evidence**, with provenance (paper, page, dataset row, run);
- **datasets**, **analyses**, **experiments** and **results** (each result points to an immutable run record);
- **risks**, **uncertainties** and potential **impacts**;
- **milestones**, **blockers** and **progress**;
- **recommendations** and their rationale.

Every element records who or what created it, when, from which inputs, and whether a human confirmed it. Today's `describe@1` output already carries the dataset fingerprint, operation, method version and service version, so it can later be attached to this model as evidence without changes to its meaning.

### 8.4 Cross-cutting risks

- **Misinformation:** external and extracted information can be wrong; sources, dates and confidence must always be visible.
- **Researcher privacy:** unpublished work and personal context must stay under the researcher's control (local-first, explicit consent for external services, deletion on request).
- **Over-automation:** the more the system does, the easier it is to accept its output unchecked; consequential actions need approval and every result needs a run record.
- **Unsupported emotional inference:** respond to what people say, never claim to read their feelings.
- **Overclaiming:** no claim of novelty, discovery, safety or superiority over other tools without the literature review, fair comparisons and validation.

### 8.5 How this relates to the roadmap

Section 7 remains the build order. This vision explains *why* each step records provenance and keeps humans in control; it does not add work to the current step. New capabilities are added only after the foundations they depend on exist and their usefulness can be tested.

---

## 9. Learning from experience and reinforcement learning (proposed — Task 4, not implemented)

> **Status:** planned capability, after Tasks 1–3 (timeout-risk fix, Step 2 commit, `regress@1`). Nothing in this section exists today. It does not change the frozen benchmark or the locked M.Tech thesis scope.

**Aim.** Reflica should learn which research actions work in which situations — from recorded actions, measured outcomes and verified feedback — and use that to make better future recommendations. It should not merely remember what happened, and it must never change its own trusted analysis code or treat an unverified outcome as established knowledge.

### 9.1 Design requirements

1. **Experience records.** Every action (analysis, method choice, experiment proposal), its configuration, inputs (with fingerprints), outcome, failures, researcher feedback and reproducibility metadata (code version, Python version, seed) is stored as an immutable, append-only record. `describe@1` already records dataset fingerprint, operation, method version and service version; run records (Step 5) extend this.
2. **Evidence-based rewards.** Rewards come from measured quantities — held-out predictive performance, reproducibility on re-run, constraint satisfaction, agreement with independently verified outcomes, cost and time — never from how plausible an answer sounds. A well-run negative result earns credit; a "positive" result that fails replication does not.
3. **Honest evaluation.** A learned policy is compared against fixed baselines (for example "always use the default method" and a hand-written rule set) on held-out tasks it was not trained on, with confidence intervals. It is adopted only if it is measurably better.
4. **Offline first.** Learning starts on logged historical data or a simulated environment (for example synthetic datasets with known ground truth), never by experimenting live on researchers' projects.
5. **Separation.** Learned policies only *choose or rank* actions; they live outside the trusted analysis engine (`reflica_service/analyses`) and the frozen benchmark, and cannot alter either.
6. **Human control.** Consequential actions still require approval; every policy decision is logged with the policy version; any policy can be rolled back.
7. **Knowledge protection.** Unverified results, noisy or contradictory feedback, and single failed experiments are recorded as evidence with uncertainty, not promoted to trusted knowledge. Promotion requires the verification rules of the research model (section 8.3).

### 9.2 Phased path

| Phase | What it adds | Infrastructure required | Evidence required before the next phase |
|---|---|---|---|
| **A. Experience logging and feedback** | Run records, outcomes and researcher feedback for every analysis; a simple "what worked before in similar cases" view, with no learning yet. | Persistent run-record store (Step 5), feedback capture in the UI, consent and privacy controls. | Records are complete and reproducible; researchers find the history useful. |
| **B. Small offline RL / bandit experiment** | A contextual bandit that picks between a few analysis methods (e.g. which regression diagnostics to run first) from dataset features. | Phase A data or a simulator with known ground truth; a fixed evaluation harness; baselines. | On held-out tasks, the policy beats fixed baselines with a confidence interval excluding no improvement; failure cases analysed. |
| **C. Controlled adaptive research agent** | The agent proposes multi-step investigations (analysis → result → next step), still offline or in simulation, then in shadow mode alongside researchers (suggest only). | Planner over the shared research model (section 8.3), safety rules, approval workflow, rollback. | Shadow-mode suggestions judged better than baselines by researchers; no unsafe or unsupported recommendation in audits. |
| **D. Limited live adaptation** | The approved policy influences real recommendations for low-risk computational actions only. | Monitoring, drift detection, automatic fallback to the baseline policy, audit dashboard. | Sustained improvement in live use; no knowledge corruption; researchers retain control. |

### 9.3 Risks

- **Reward hacking:** a policy optimises the measured reward rather than real research value — mitigated by multiple independent measures and held-out evaluation.
- **Feedback noise and bias:** one researcher's preferences or a few failures can mislead learning — mitigated by uncertainty-aware updates and minimum evidence thresholds.
- **Distribution shift:** what worked in one field or dataset may not transfer — mitigated by evaluating per domain and falling back to baselines.
- **Privacy:** experience records contain unpublished work — local-first storage, consent, and no pooling across researchers without permission.
- **Over-automation:** see section 8.4; learning does not relax approval requirements.
