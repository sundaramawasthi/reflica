# M.Tech Plan (2026–28) — Proposed

> **Status:** proposed plan, to be confirmed with the supervisor and checked against GLA University's academic calendar and rules. Semester dates, project requirements and required publication indexing (Scopus / Web of Science / UGC-CARE) are assumptions until confirmed. Publications are possible outcomes, not guaranteed deliverables. The locked thesis scope in `../PROGRESS.md` is unchanged.

**Assumed structure:** Sem 1 ≈ Aug–Dec 2026 · Sem 2 ≈ Jan–May 2027 · Sem 3 ≈ Aug–Dec 2027 · Sem 4 ≈ Jan–May 2028. Minor projects in Sems 1–2, dissertation in Sems 3–4, plus a separate data analytics course project.

## Overview

| Semester | Project | Builds on | Possible papers |
|---|---|---|---|
| Sem 1 | **Minor Project 1** — reliability of LLM extraction of structured state graphs | R-N pilot (done) + literature review | P1 survey, P2 LLM extraction study |
| Sem 1 | **Data analytics project** — Reflica Analytics Workbench | `reflica_service` (`describe@1` done; `regress@1` next) | P4 applied analytics (optional) |
| Sem 2 | **Minor Project 2** — Reflica reproducible, human-approved analysis workflow | Platform steps 3–8 (`PLATFORM_AUDIT.md`) | P3 software / tool paper |
| Sem 3 | **Dissertation Part 1** — full thesis experiment and analysis | Benchmark v0.2.0, B1–B5 | P5 benchmark paper |
| Sem 4 | **Dissertation Part 2** — ablations, thesis, defence | B5 + results | P6 main methods paper (journal) |

## Semester 1

### Minor Project 1 — *How reliably do LLMs extract structured, constraint-aware state graphs from natural-language plans?*

- **Problem:** the thesis depends on LLM extraction; errors there propagate into every revision.
- **Questions:** extraction accuracy for nodes, edges, attributes and rules; which content fails (constraints, preferences, ambiguity); whether strict schemas and validation reduce errors.
- **Method:** extend the existing R-N pilot (16 scenarios × 3 repeats, temperature 0) to more scenarios and 2–3 models; build an error taxonomy (e.g. the T7.2 invented rule).
- **Done already:** pilot harness and first results. **Remaining:** more models/scenarios, error analysis, report.

### Data analytics project — *Reflica Analytics Workbench*

One application combining the lab topics: data cleaning and validation (done), exploratory statistics and correlation (`describe@1`, done), regression with diagnostics (`regress@1`, next), visualisation, and optional clustering / classification / time series if covered in the lab. Distinctive feature: trustworthy results — provenance, uncertainty, explicit warnings, no causal claims from correlation, no extrapolation.

### Writing
- **P1 — Survey:** LLMs, knowledge graphs and belief revision: keeping AI-generated structured knowledge consistent under change (from the literature review).
- **P2 — Empirical short paper:** results of Minor Project 1.

## Semester 2

### Minor Project 2 — *Reflica: a provenance-tracked, human-approved scientific analysis workflow*

- **Scope:** `regress@1`, `sweep@1`, run records and storage, FastAPI routes, Flutter screens (upload → confirm variables → approve → results), dataset-version comparison.
- **Evaluation:** known-answer and reproducibility tests; small pilot with 5–10 researchers or students (check GLA ethics requirements first; informed consent; anonymised notes).
- **Alternative (if the supervisor prefers a research focus):** a science evidence-change benchmark (support, contradiction, retraction, failed replication, narrowed scope) — see `SCIENCE_DIRECTION.md`.

### Writing
- **P3 — Software / tool paper** on the analysis service.
- **P4 — Applied analytics paper** (optional, only with a real contribution).
- Revise P1–P2 after reviews.

## Semester 3 — Dissertation Part 1

**Locked thesis:** attribute-aware revision of LLM-extracted state graphs under partial-satisfaction and capacity constraints — evaluated across add, edit, delete and relationship-change operations against classical ATMS, constraint-programming and LLM-regeneration baselines.

1. Freeze the full experiment protocol (conditions, statistics plan).
2. Connect B5 to the experiment runner.
3. Run the full 63-scenario experiment (structured and natural-language regimes).
4. Statistics: 95% confidence intervals, paired tests, hypothesis verdicts.
5. Failure analysis; complete the literature review and contribution statement.

- **P5 — Benchmark paper:** the 63-scenario benchmark, categories and baseline results.

## Semester 4 — Dissertation Part 2

1. Ablations of B5 stages (dependency closure, verify/repair, determinability).
2. Robustness: other LLMs, natural-language input.
3. Optional, only if agreed: a first test of B5 on scientific claim–evidence scenarios as future-direction evidence.
4. Thesis writing and defence.

- **P6 — Main methods paper (journal):** B5, evaluation and ablations.

## Publication guidance

| Paper | Type | Example venues to evaluate |
|---|---|---|
| P1 Survey | Journal | IEEE Access; Artificial Intelligence Review; Knowledge-Based Systems; ACM Computing Surveys (very selective) |
| P2 LLM extraction | Conference / workshop | ACL / EMNLP workshops; CODS-COMAD; ICON; later a journal version |
| P3 Software | Journal | Journal of Open Source Software; SoftwareX |
| P4 Applied analytics | Conference | IEEE INDICON / CONECCT; reputable IEEE or Springer proceedings (verify indexing) |
| P5 Benchmark | Conference / journal | NeurIPS Datasets & Benchmarks (very selective); LREC-COLING; Data in Brief |
| P6 Method | Journal / conference | Knowledge-Based Systems; Applied Intelligence; Engineering Applications of AI; JAIR (selective); KR; ECAI |

- Verify current indexing (Scopus / Web of Science / UGC-CARE as required), fees and review times; confirm venues with the supervisor; avoid predatory journals.
- A realistic, strong outcome: 4–5 submissions, 1–2 accepted. Submit conference / workshop papers early and journal versions later.
- Each paper needs a distinct contribution; no splitting one result across papers and no duplicate publication.

## Next actions

1. Confirm minor-project topics, semester rules and thesis scope (including whether the science extension is in or out) with the supervisor.
2. Check the GLA academic calendar and required indexing.
3. Start the literature review (P1) and the extended LLM extraction study (Minor Project 1).
4. Engineering: Task 3 — `regress@1` (serves the data analytics project and Minor Project 2).
