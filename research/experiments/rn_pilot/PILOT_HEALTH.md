# Pilot Health Report — R-N pilot, config v1.7 (2026-10-09)

Model nvidia/nemotron-3-ultra-550b-a55b · temp 0 · seed 20261008 · thinking on · max 16,384 · benchmark v0.2.0
16 scenarios × 3 repeats × {B1, B2, EXTRACT} = 144 calls.

| Item | Result |
|---|---|
| Completion | **144/144** (after rerunning 2 API-failed calls) |
| API failures | 2 (HTTP 500; HTTP 503 after all retries), both `cat3_early_termination_edit_001` EXTRACT r0/r2 → **infrastructure**; rerun OK; originals kept in `pilot_api_failures.jsonl` |
| Transient retries | 79 (429/503), all recovered |
| Non-JSON / fenced output | 0 |
| Truncation | 0 (max 5,708 / 16,384 output tokens) |
| Latency | median 60 s, max 279 s |
| Output tokens | median 1,536, max 5,708 |
| B1 / B2 parse | 48/48, 48/48; unmapped labels 0 |
| Extraction → B4b | 47/48 ok; **1 extraction failure** |
| B4b solver failures on valid extractions | 0 |
| Extraction quality (47 valid) | entity recall 1.0, link recall 1.0, pre-value accuracy 1.0, pre-state reproduction 0.993, update correct 1.0 |
| gold → B4b, B6 | 16/16 each |

## Failure classification
| Case | Class | Detail |
|---|---|---|
| cat3_early_termination EXTRACT r0, r2 | API/infrastructure | server 500/503; rerun succeeded |
| cat7_conflicting_evidence EXTRACT r1 | **extraction failure (genuine model behaviour)** | extractor invented a resolution rule (`prefer_source: "plan"`) absent from the text; B4b cannot resolve a nonexistent source. Counted as extraction failure — not repaired. Research-relevant: hallucinated resolution of a P2 conflict. |

## Verdict
Infrastructure **healthy**. No defect requiring a code change; no scoring rule or hypothesis changed.
Only action taken: rerun of the 2 API-failed calls (Phase 2, data completion).
Next: build B5 → offline validation → freeze B5 → freeze full protocol. Full experiment NOT started.
