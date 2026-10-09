# v1.0 repeatability check (2026-10-08) — preserved, NOT for model evaluation

Model nvidia/nemotron-3-ultra-550b-a55b, temperature 0, seed 20261008, max 4000, thinking on.
- 6/6 calls succeeded; all served by the frozen model (no silent swap).
- 8 transient retries (429/503); no truncation (max 3,803 / 4,000 tokens).
- Exact repeatability 0/3 for both scenarios → endpoint non-deterministic despite temperature 0 + fixed seed.
- 0/6 outputs conformed to the extractor schema.

**Setup defect:** the prompts said "matching the schema" but the runner never sent the schema.
These outputs are therefore INVALID for model-performance evaluation; they are valid only as
evidence of that defect and of endpoint non-determinism. Fixed in config v1.1 (schema delivered in prompt).
