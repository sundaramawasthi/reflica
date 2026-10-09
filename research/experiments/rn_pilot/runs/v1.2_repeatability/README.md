# v1.2 repeatability check (2026-10-08) — preserved, NOT for model evaluation

Typed extractor schema. cat7 T7.9: 3/3 parse + formula-valid + B4b-executable, semantically identical
(only free-text `human` differs), ambiguity captured (target_ref "Supplier A"). cat5 T5.9a: 2/3 truncated
at the 4,000-token limit (invalid JSON); 1/3 parsed but crashed B4b on explicit `"when_linked": null`.
Defects: output limit too low for typed output + reasoning; null-vs-absent mismatch at the schema→B4b
boundary. Fixed in v1.3.
