# Reflica: Scientific Discovery Direction

> Status: planning document. Nothing here is a result. Claims of novelty or usefulness require the literature review, the researcher workflow study and the experiments below.

## Research objective

Investigate whether explicitly representing dependencies between scientific claims and their supporting evidence enables more accurate, traceable and efficient conclusion revision when new, conflicting or withdrawn findings appear.

## Research question

Does evidence-dependency-aware revision improve the correctness and traceability of scientific conclusion updates compared with LLM-based reanalysis and other suitable reasoning baselines?

**Working hypothesis:** evidence-dependency-aware revision produces fewer over- and under-revisions than LLM reanalysis on the same scenarios.

## Current state of the foundation

- Benchmark v0.2.0 (63 plan/state-graph scenarios, 7 categories) is built and frozen.
- Revision engine B5 v0.1.0 is implemented and frozen for the plan/state-graph benchmark; it is not yet connected to the experiment runner, and not yet adapted or tested on scientific claims and evidence.
- None of this shows that the proposed scientific-reasoning method works.

## Mapping from existing work

| Existing Reflica concept | Scientific research equivalent |
|---|---|
| Plan item | Scientific claim or conclusion |
| Fact or observation | Reported result or evidence |
| Dependency | Relationship between evidence and claims |
| Constraint | Assumption, scope condition or validity requirement |
| Fact update | New finding or corrected result |
| Removal or invalidation | Retraction or invalidated evidence |
| Revision explanation | Traceable account of why a conclusion changed |

This mapping is a starting hypothesis, not an assumption that project-plan revision and scientific reasoning are identical.

## Research design

**Logical chain**

- **Motivation:** researchers must keep track of which conclusions still hold as new, conflicting or retracted results appear.
- **Problem:** many AI literature tools summarise or re-read papers without explicitly tracking which evidence supports which conclusion, so updates may be inconsistent or untraceable. (To be confirmed by the literature review.)
- **General objective:** develop and evaluate an evidence-aware method for revising scientific conclusions when evidence changes.
- **Specific objectives:**
  1. Study how researchers currently track and revise evidence.
  2. Define a claim–evidence–assumption schema.
  3. Build a controlled benchmark of evidence-change scenarios with expected outcomes.
  4. Adapt the revision engine to the schema and connect it to the runner.
  5. Compare against baselines on the metrics below.
  6. Pilot on 10–20 annotated AI/ML papers.

**Philosophy:** pragmatism with mixed methods — quantitative benchmark evaluation (positivist) plus qualitative researcher interviews (interpretivist).

**Design sequence**

| Phase | Type | Activity |
|---|---|---|
| 1 | Exploratory | Researcher workflow study and literature review |
| 2 | Descriptive | Measure how often current LLM approaches mis-revise conclusions |
| 3 | Experimental | IV = revision method; DV = correctness, over/under-revision, traceability, cost |

**Validity:** internal — frozen benchmark, fixed seeds, temperature 0, expected outcomes fixed before runs, method code independent of ground-truth code. External — limited; AI/ML papers are a pilot and do not generalise to all science.

## Literature review (first research task)

Purpose: establish what is genuinely new about the evidence-aware revision method and what specific gap remains.

Areas to cover:

- Belief revision and truth-maintenance systems (AGM, ATMS).
- Argument mining and scientific claim extraction and verification.
- Scientific knowledge graphs and evidence/provenance models.
- LLM-based literature-review and research-assistant tools.
- Knowledge editing and updating in LLMs.
- Studies of retraction and replication handling.

Output: a written review with the gap stated in nuanced terms (for example, "existing work focuses mainly on X, while limited attention has been given to Y under Z conditions"). Avoid absolute claims such as "first ever".

## Researcher workflow study

Purpose: establish whether the problem matters in practice and what researchers need before features are designed.

- **Interviews:** semi-structured interviews with 5–10 researchers (for example GLA faculty, PhD and M.Tech students).
- **Observation:** observe at least one literature review in progress.
- **Questions:**
  - How do you track claims and sources today (notes, reference managers, spreadsheets)?
  - How do you notice new or conflicting results?
  - What do you do after a retraction or failed replication?
  - **Pain points:** where do you lose time or make mistakes?
  - **Trust requirements:** what would make you trust or distrust an AI suggestion about evidence?
- **Ethics:** check GLA University's ethics requirements before recruiting participants; obtain informed consent and anonymise notes and transcripts.
- **Output:** a short report of workflows, pain points and trust requirements, used to shape the schema and features.

The literature review and the workflow study are separate but complementary activities: the literature review identifies the research gap; the workflow study establishes researchers' actual needs. Neither alone establishes novelty or usefulness.

## Initial evaluation

### Phase 1: Controlled scenarios

Construct a small benchmark covering:

- New evidence supporting an existing claim.
- Evidence contradicting an existing claim.
- Retraction or invalidation of a result.
- Failed replication.
- Findings that narrow a claim's scope.
- New evidence that should not affect unrelated claims.

Use carefully specified expected outcomes so each method can be evaluated consistently.

### Phase 2: Real AI/ML research papers

Select approximately 10–20 related papers. Manually annotate a manageable subset of claims, supporting evidence, limitations and contradictions. Record sources and annotation decisions.

Treat this as a pilot dataset, not sufficient evidence of general scientific-discovery capability.

## Baselines

- LLM-based reanalysis of the available evidence.
- An appropriate structured reasoning or dependency-tracking baseline.
- The proposed Reflica revision method, once adapted to scientific claims.

Use existing B1/B2 and B4a components only after confirming their actual interfaces and suitability for these scenarios. Evaluate B5 on scientific scenarios only after it is adapted and connected to the experiment runner.

**Fair comparison**

- The LLM baseline and the proposed Reflica method receive equivalent evidence and equivalent opportunities to revise conclusions.
- Expected outcomes are frozen before any method is evaluated.
- Experimental settings (models, prompts, temperature, seeds, budgets, versions) are documented for every run.

## Metrics

- **Revision correctness:** does the final conclusion match the predefined expected outcome?
- **Over-revision:** how often are conclusions changed unnecessarily?
- **Under-revision:** how often are conclusions left unchanged when evidence requires a change?
- **Traceability:** can each revision be linked to its supporting evidence?
- **Efficiency:** computational cost, latency and number of model calls.

Report results across scenario types and include failure analysis.

## Scope and limitations

The initial study evaluates evidence-aware conclusion revision, not autonomous scientific discovery as a whole. It does not establish that the system discovers novel scientific laws or produces new scientific knowledge.

Quantum computing and specialist domain simulations remain future extensions, to be considered when a concrete scientific use case justifies them.

## Immediate next steps

1. Conduct the literature review and the researcher workflow study.
2. Finalize the scientific claim-and-evidence schema.
3. Define benchmark scenarios and expected outcomes.
4. Select suitable baselines and evaluation metrics.
5. Adapt the revision method and connect it to the experiment runner.
6. Run reproducible comparisons, analyse failures, and document results.
