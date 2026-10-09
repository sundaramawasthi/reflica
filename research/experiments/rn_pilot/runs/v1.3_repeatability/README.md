# v1.3 repeatability check (2026-10-09) — preserved, NOT for model evaluation

5/6 calls fully valid (schema, parse, formulas, B4b; no truncation, max 4,497 tokens; B4b status identical
across valid repeats). 1 cat7 call schema-invalid: `{"$unknown": "undefined"}` placed as a Src fallback.
Setup inconsistency: renderer writes "otherwise undefined", prompt says unknown → `$unknown`, grammar
expresses "no fallback" by omission. Fixed in v1.4 at the conversion boundary.
