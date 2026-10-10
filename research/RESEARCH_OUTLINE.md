# Reflica — Research Outline

> **Status:** planning outline. No part of the scientific-discovery direction has been validated. The research gap, novelty claims, technology choices, publications and timeline are all provisional. Companion to `SCIENCE_DIRECTION.md`; implementation status lives in `../PROGRESS.md`.

**Two levels — do not conflate**

- **Immediate M.Tech thesis (locked in `PROGRESS.md`, 2026-10-07):** *attribute-aware revision of LLM-extracted state graphs under partial-satisfaction and capacity constraints*, on the existing 63-scenario plan/state-graph benchmark.
- **Long-term Reflica vision:** an AI research partner for scientific discovery. The scientific claim–evidence work below is a **proposed extension** of the thesis engine. Whether it becomes part of the thesis, or stays a follow-on, must be agreed with the supervisor.

---

## 1. Research title (working)

**Evidence-aware revision of scientific conclusions using LLM-extracted claim–evidence graphs.**
Short name: *Reflica — an AI research partner for scientific discovery.* Working title for the proposed extension, not the locked thesis title.

## 2. Problem statement

Research literature changes constantly through new results, contradictions, retractions and failed replications. Many AI tools summarise or re-read papers without explicitly tracking which evidence supports which conclusion, so updates may be inconsistent or untraceable. (To be confirmed by the literature review.)

## 3. Motivation

Researchers must keep conclusions current as evidence changes. A trustworthy AI partner should explain *why* a conclusion changed, not just produce a new summary.

## 4. Research questions

- **RQ1:** Does explicit evidence-dependency tracking revise conclusions more correctly than LLM reanalysis?
- **RQ2:** Does it reduce over-revision (unnecessary changes) and under-revision (missed changes)?
- **RQ3:** Can every revision be traced back to its evidence?
- **RQ4:** What is the cost in time, tokens and model calls compared with baselines?
- **RQ5 (exploratory):** How do researchers track and revise evidence today, and what would make them trust an AI tool?

## 5. Hypothesis

Evidence-dependency-aware revision yields fewer over- and under-revisions, and better traceability, than LLM reanalysis on the same scenarios. Untested.

## 6. Objectives

- **General:** develop and evaluate an evidence-aware method for revising scientific conclusions.
- **Specific:** study researcher workflows, design a claim–evidence schema, build a benchmark, adapt the revision engine, compare it with verified baselines, and pilot on real papers.

## 7. Research gap (provisional)

Belief revision, claim extraction and LLM literature tools exist separately; limited attention *appears* to have gone to combining LLM extraction with formal, traceable revision when findings change. **This gap and any novelty are provisional until the literature review is completed.** No absolute claims such as "first ever".

## 8. Expected contributions (provisional)

- A benchmark of scientific evidence-change scenarios.
- A hybrid method: LLM extraction plus formal revision.
- Metrics for over-revision, under-revision and traceability.
- Findings on what researchers actually need.

Each depends on the literature review confirming it is not already established.

## 9. Research philosophy

Pragmatism with mixed methods: quantitative experiments for performance, qualitative interviews for researcher needs.

## 10. Methodology

- **Exploratory:** literature review (identifies the gap) and researcher workflow study (establishes actual needs). Separate but complementary; neither alone proves novelty or usefulness.
- **Descriptive:** measure how often current LLM approaches mis-revise conclusions.
- **Experimental:** independent variable = revision method; dependent variables = correctness, over/under-revision, traceability, cost.

## 11. System architecture (high level, proposed)

**Papers → LLM extraction → claim–evidence graph → change detection → scoped revision → explanation → human review.**
The human approves or rejects every suggested change. The existing B5 pipeline (change detection → dependency scope → scoped revision → verify/repair → determinability) covers the middle stages for plan/state graphs only.

## 12. Technology stack

- **In the repo now:** Python research workspace (NetworkX, Pydantic, optional OR-Tools, pytest; LLM client for the pilot) and Flutter/Dart app with Firebase/Firestore and a mind-map view.
- **Reasoning components in the repo:** ATMS-style baseline (B4a) and OR-Tools CP-SAT baseline (B4b).
- **Proposed, not yet added:** arXiv / Semantic Scholar APIs for papers; pandas and matplotlib for analysis.

## 13. Dataset

- **Controlled scenarios:** handmade, expected outcomes frozen before any evaluation.
- **Pilot:** 10–20 related AI/ML papers, manually annotated. **Exploratory only; it does not establish general scientific-discovery capability.**

## 14. Baselines

- **Candidates:** B1 (LLM regeneration), B2 (LLM re-prompt with graph), B4a (classical ATMS), B4b (constraint solving). Also available in the existing benchmark: B3 (reachability) and B6 (oracle upper bound).
- **Status:** B3, B4a and B4b exist as code; B1/B2 currently exist as prompts and schemas used in the pilot. **Suitability and integration of every candidate for scientific scenarios must be verified before comparison.**
- **Proposed method:** B5, which is frozen for the existing plan/state-graph benchmark (0 disagreements with gold on 63 scenarios). **It still needs scientific claim–evidence adaptation and experiment-runner integration before any scientific evaluation.**
- **Fairness:** all methods get equivalent evidence and revision opportunities; settings documented per run.

## 15. Evaluation metrics

Correctness, over-revision, under-revision, traceability, and efficiency (cost, latency, number of calls). Report per scenario type with failure analysis.

## 16. Expected challenges and mitigations

| Challenge | Mitigation |
|---|---|
| LLM extraction errors | Structured schemas, validation, human-checked samples |
| No ready-made dataset | Small benchmark with frozen expected outcomes |
| Novelty may already exist | Literature review first; narrow the claim |
| Unfair comparison | Same evidence and settings for all methods; document everything |
| LLM run-to-run variation | Temperature 0, fixed seeds, logged runs |
| API cost | Small pilot first, caching, cheaper models for development |
| Few interview participants | Start with GLA faculty and students; 5–10 suffices for exploration |
| Ethics | Check GLA requirements before recruiting; consent; anonymisation |
| Single field (AI/ML) | State as a limitation; expand later with domain experts |
| Thesis scope creep | Agree with supervisor how much of the science extension enters the thesis |

## 17. Usefulness (potential impact)

If the hypothesis holds: more reliable literature reviews, traceable conclusion updates, less researcher time lost, and a foundation for trustworthy AI research assistants. Practical value must be confirmed by the workflow study.

## 18. Limitations

Covers conclusion revision, not autonomous discovery. One field, small dataset, small interview sample.

## 19. Ethics

Informed consent, anonymisation, GLA ethics approval, and respect for paper licences and copyright.

## 20. Future work

Other scientific fields with domain experts, experiment suggestion, and specialist tools (for example quantum chemistry simulation) when a concrete use case justifies them.

---

## 21. Mapping to M.Tech deliverables (proposed)

| Deliverable | Suggested content |
|---|---|
| **Minor project 1** | Literature review, researcher workflow study, claim–evidence schema |
| **Minor project 2** | Science benchmark plus extraction pipeline from paper abstracts |
| **Major project / thesis** | Locked thesis (plan/state-graph revision, full 63-scenario experiment) plus, if agreed with the supervisor, adapted B5 on scientific scenarios and the paper pilot |
| **Data analytics project** | Research-paper analytics dashboard: collection, cleaning, EDA, visualisation, statistics/ML for trends and clustering, claim–evidence networks — connecting the lab topics |

## 22. Possible publications

Possible outcomes, **not guaranteed deliverables**; each depends on results and peer review.

1. Survey: AI for evidence tracking and belief revision in science.
2. Benchmark/dataset paper: evidence-change scenarios.
3. Methods paper: evidence-aware revision vs LLM baselines.
4. User-study paper: how researchers handle changing evidence.
5. Applied/analytics paper: research-literature analytics dashboard.

Target reputable, indexed venues chosen with the supervisor; avoid predatory journals.

## 23. Timeline (provisional)

- **Semester 1:** literature review, interviews, schema (Minor 1); data analytics project.
- **Semester 2:** benchmark and extraction (Minor 2); survey paper draft.
- **Semester 3:** adapt B5, integrate with the runner, run experiments; benchmark paper.
- **Semester 4:** paper pilot, thesis writing, methods and user-study papers.

**Dependencies that could shift it**

- The locked thesis still needs its full 63-scenario experiment and statistics (`PROGRESS.md` next steps).
- Literature review outcome may narrow or redirect the contribution.
- GLA ethics approval timing gates the interviews.
- B5 adaptation and runner integration gate all scientific experiments.
- Baseline verification gates the comparison.
- LLM API access and cost.
- Supervisor agreement on thesis scope and course deadlines.
- Peer-review cycles for any publication.
