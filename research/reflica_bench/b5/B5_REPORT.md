# B5 (Reflica) — implementation & validation report · v0.1.0 · id `fc9524a4ea38cca5` · frozen 2026-10-09

## 1. Architecture / decision flow
Input: `MethodInputStructured` (gold structured input, or LLM extraction via ExtractionOutput).
1. **Change detection** (`reflica.py`): apply the update to a copy; name-only targets resolved by name (+ scope);
   unavailable target → P8a; undeclared attribute → P8b. Nothing guessed: open choices kept.
2. **Consistent completions**: one run per combination of open choices — shared name (P9), unstated link kind (P3),
   conflicting reports without a *valid* preference rule (P2), duplicate active rules (P5). A preference rule naming a
   source no claim carries is rejected and logged.
3. **Dependency analysis** (`engine.py`): rule-dependency graph over (node, attribute) incl. link-sets, node existence
   and units; downstream closure of the change = revision scope.
4. **Revision**: recompute only in-scope keys, dependencies first; cycles via finite-domain fixed-point search (P4).
5. **Verification/repair**: re-check every rule; in-scope violations repaired, out-of-scope ones reported, never changed.
6. **Determinability**: a value is committed only if known and identical in every completion; otherwise the node
   abstains with reason codes. Label: REQUIRES_REEVALUATION when only completions disagree (a provisional answer exists),
   else UNCERTAIN. Trace per completion: choices, seeds, scope, cycles, verification, repairs, notes.

## 2. Files
`reflica_bench/b5/engine.py` (stages 3–5), `reflica_bench/b5/reflica.py` (stages 1–2, 6; `B5Reflica` baseline),
`tests/test_b5.py`. Fingerprints in `FROZEN.json`.

## 3. Offline tests (75, all pass; suite 203/203)
Independence (AST import audit; no gold in input) · gold agreement on all 63 · irrelevant change · transitive scope +
trace · partial status not binarised · conflict without rule abstains · valid preference applied · invented preference
rejected · `$unknown` value abstains · adversarial out-of-scope inconsistency reported not repaired · boundary
coverage = 1 → FULL · regression: the real pilot T7.2 extraction with invented `prefer_source: "plan"`.

## 4. Independence audit
B5 imports only `schema`, `adapters`, `baseline` (shared types) and its own modules; a test fails on any import of
gt_engine, groundtruth*, evaluator, linter, loader, rn, B3/B4a/B4b. Gold labels are used only in tests.

## 5. Gold comparison (structured input, 63 scenarios)
Determinability, outcome labels (determinable nodes), attribute values and pathology codes: **0 disagreements**
in every category (Cat 1–7). Escalation label on ambiguous nodes: **11/19** agree — B5 uses its own fixed rule,
not the benchmark's per-scenario escalation policy (secondary metric; left as is).

## 6. Limitations / unresolved
- **Defect found and fixed during validation:** dependency analysis missed that `<attr>_unit` changes affect rules
  reading `<attr>` (T7.7/T7.14). Fixed on principle (unit is part of the value), before freezing.
- Agreement on gold input is expected: B5 implements the same declared rule semantics independently. It says nothing
  about robustness to extraction errors — that is what the experiment measures.
- The in-scope **repair** path is never triggered by consistent inputs; only out-of-scope reporting is exercised.
- Completion enumeration is exponential in open choices (benchmark has ≤ 2).
- With pilot extraction for T7.2 r1, B5 also flags P5 because that extraction contains two rules for one value.
- Committed to the repository in `886095d`; version id = hash of B5 source files.

## 7. Reproduce
`cd research && .venv/bin/python -m pytest tests/test_b5.py -q`
