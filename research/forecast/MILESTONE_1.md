# Milestone 1 (backend): one question, end to end (design, not code)

Date: 14 October 2026. Status: proposed; the user writes the code. M.Tech guide approval of the overall direction is pending.
**When:** Phase 3 (Python backend), after the documentation and the Flutter UI phases. The December 2026 pilot does not wait for this milestone; it is collected by hand (`PILOT_PROTOCOL.md`).

Goal: one question passes **validation → forecast → freeze → resolution → scoring**, proven by tests.

## 1. Record formats

Moved to `PILOT_PROTOCOL.md` (single source for `question@1`, `question_set@1`, `forecast@1`, `resolution@1`, `correction@1`, hashing and timestamps). The backend must read the manual December pilot files in that format without changing them.

## 2. Proposed first real question

```json
{
  "schema": "question@1",
  "question_id": "IN-ECO-RBI-0001",
  "version": 1,
  "kind": "prospective",
  "question_text": "Will the RBI Monetary Policy Committee cut the policy repo rate at its first policy decision announced on or after 1 January 2027?",
  "details": "A cut means the repo rate announced in that decision is lower than the repo rate in effect immediately before the announcement. Scheduled and unscheduled MPC decisions both count.",
  "why_it_matters": "The repo rate is India's main policy rate; a clear, officially published decision makes it a clean test of forecasting Indian monetary policy.",
  "region": "india",
  "domain": "economy",
  "topic": "monetary_policy",
  "type": "binary",
  "created_at_utc": "2026-11-XXT00:00:00Z (time of writing)",
  "forecast_deadline": "2026-12-31T23:59:59+05:30",
  "expected_resolution_date": "2027-02-XX (fill from RBI's published MPC schedule)",
  "resolution_deadline": "2027-03-31",
  "resolution_source": {
    "name": "Monetary Policy Statement / Resolution of the Monetary Policy Committee",
    "publisher": "Reserve Bank of India",
    "url": "https://www.rbi.org.in/ (exact press-release URL recorded at resolution)"
  },
  "resolution_rule": "Yes if the repo rate announced in the first MPC decision on or after 2027-01-01 is lower than the repo rate in effect immediately before that announcement. No if it is equal or higher.",
  "invalid_rule": "Invalid if no MPC repo-rate decision is announced between 2027-01-01 and 2027-03-31.",
  "pair_id": "CB-FIRST-2027",
  "origin": {"method": "manual", "source_url": null, "fetched_at_utc": null, "note": "Pilot question"},
  "author": "Sundram Awasthi"
}
```

Why this one: the RBI publishes a clear, dated, official answer; Yes/No is mechanical; the "first decision on or after 1 Jan" wording survives a change in meeting dates; a base-rate baseline exists (share of past MPC decisions that were cuts); a natural Western twin exists (the first US FOMC decision of 2027 cutting the target range). Check the 2027 MPC dates on the RBI website before freezing.

## 3. Minimum files (the user writes them)

```
research/forecast/__init__.py        makes it a package (and add "forecast*" to pyproject include)
research/forecast/schema.py          pydantic models Question, Forecast, Resolution + canonical_hash()
research/forecast/validate.py        cross-field checks (deadlines, hashes, evidence dates, probability)
research/forecast/store.py           append-only JSONL write/read; refuse duplicate ids
research/forecast/runner.py          make_forecast(question, client, condition) -> Forecast; ModelClient protocol
research/forecast/scoring.py         brier(p, outcome); score(forecasts, resolutions) skipping invalid
research/forecast/fixtures/*.jsonl                 TEST- records only (synthetic)
research/tests/test_forecast_schema.py     valid question loads; each broken rule rejected
research/tests/test_forecast_scoring.py    hand-computed Brier values
research/tests/test_forecast_e2e.py        TEST- fixture question + FakeClient → freeze → resolve → score; also imports a protocol-format file unchanged
```

Order to write them: `schema.py` → its test → `validate.py` → `scoring.py` → its test → `store.py` → `runner.py` (with a `FakeClient` returning a fixed probability) → e2e test. A real LLM client comes after the e2e test passes.

Hand-checked Brier values for the scoring test: p = 0.7, Yes → 0.09; p = 0.7, No → 0.49; p = 0.5 either way → 0.25; p = 1.0, No → 1.0.

E2E test must also check that: a forecast after the deadline is kept but labelled late and excluded from scoring; a baseline record scores like a model record; writing the same `forecast_id` twice fails; a changed question file breaks the hash check; an `invalid` resolution is excluded from the score.

## 4. Timestamps

See `PILOT_PROTOCOL.md` section 5 (RFC 3161 + OpenTimestamps; git dates are supporting evidence only).
