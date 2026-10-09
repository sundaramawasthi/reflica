# R-N pilot — experimental conditions (benchmark v0.2.0)

| Condition | Input | Purpose |
|---|---|---|
| **B1** full regeneration | plan_text + change_text | Direct LLM reasoning baseline |
| **B2** delta | plan_text + change_text | Direct LLM reasoning baseline |
| **A. Gold extraction → B4b / B5** | sanitised canonical structured input (no LLM) | **Downstream sanity check only.** Shows the revision pipeline works when extraction is perfect. **Never evidence that the extractor is accurate.** |
| **B. LLM extraction → B4b / B5** | plan_text + change_text → shared extractor → same structured output to both | **The experiment:** extraction + revision under natural language |
| B6 oracle scope | canonical input | Diagnostic upper bound for scope only |

**Shared extractor (by design, not a flaw).** Extract→B4b and B5 receive the
*identical* extractor output (one prompt, one call per scenario per repeat),
including its uncertainty markers (`$unknown`, `candidate_types`, `target_ref`,
`evidence.claims`). B1/B2 are direct-reasoning baselines and do not receive
that intermediate representation; all three LLM conditions get the same
abstention-reason list. Differences between B and B1/B2 therefore measure the
architecture (extract → symbolic revision → determinability check) versus
direct reasoning.

**Rules.** No run without a frozen config (`config.frozen.json`) approved by the
user. API key read only from `OPENAI_API_KEY`; never printed or stored.
Pilot = 16 scenarios (`rn.PILOT_IDS`); the full 63 is not run yet.
