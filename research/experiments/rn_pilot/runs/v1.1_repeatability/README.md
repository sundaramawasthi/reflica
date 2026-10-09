# v1.1 repeatability check (2026-10-08) — preserved, NOT for model evaluation

Schema delivered in prompt. 6/6 success, 6/6 valid JSON, 6/6 schema-valid, all served by
nvidia/nemotron-3-ultra-550b-a55b, no truncation (max 2,779 tokens), 6 transient retries.
Exact repeatability 0/2; parsed-equal 0/2 (cat5: 3 distinct, cat7: 2 distinct; cat7 differs in event.target_scope).

**Interface defect:** `rules` was a free-form dict in the v1/v1.1 extractor schema, so the model wrote rules
as English sentences — schema-valid but not executable by B4b/B5. `target_scope` had no stated meaning
(values "name", "all"). Valid only as evidence of these defects. Fixed in v1.2 (typed rule grammar + field descriptions).
