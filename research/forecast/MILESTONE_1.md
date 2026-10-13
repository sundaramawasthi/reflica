# Milestone 1: one question, end to end (design, not code)

Date: 14 October 2026. Status: proposed; the user writes the code.

Goal: one question passes **validation → forecast → freeze → resolution → scoring**, proven by tests.

## 1. Three record types, each immutable

A question file never changes after approval. Its outcome is **not** stored in it; outcomes go in a separate resolution record. A question's status is derived from which records exist (no forecasts yet / forecasts frozen / resolved / invalid).

### 1.1 `question@1`

| Field | Type | Rule |
|---|---|---|
| `schema` | `"question@1"` | fixed |
| `id` | string | pattern `^(IN|WE)-(ECO|CLI|INF)-[A-Z0-9]+-\d{4}$`; `TEST-…` reserved for test fixtures |
| `question` | string | one sentence, ends with `?` |
| `details` | string | definitions a forecaster needs |
| `region` | `india` \| `western` | |
| `category` | `economy` \| `climate` \| `infrastructure` | |
| `topic` | string | e.g. `monetary_policy` |
| `type` | `binary` | only binary in milestone 1 |
| `created_at` | datetime **with time zone** | |
| `forecast_deadline` | datetime with time zone | after `created_at` |
| `expected_resolution_date` | date | after the deadline's date |
| `resolution_deadline` | date | ≥ expected date; if no result by then → `invalid` |
| `resolution_source` | `{name, publisher, url}` | `url` must be `https://` |
| `resolution_rule` | string | how to read Yes/No from the source |
| `invalid_rule` | string | when the question is annulled |
| `pair_id` | string or null | links an India question to its Western twin |
| `origin` | `{method: manual \| generator, note}` | where the question came from |
| `author` | string | |

**Question hash** = SHA-256 of the canonical JSON (keys sorted, no extra spaces, UTF-8). Every forecast and resolution stores this hash, so any later edit to the question is detectable.

### 1.2 `forecast@1` (append-only)

| Field | Rule |
|---|---|
| `schema` | `"forecast@1"` |
| `forecast_id` | unique; duplicates refused |
| `question_id`, `question_hash` | hash must match the question file |
| `question_set_hash` | hash of the sorted list of question hashes in the frozen set (for the pilot: a set of one) |
| `model` | `{provider, name, version}` (`version` = exact model id string returned by the API) |
| `condition` | `no_news` \| `news` |
| `prompt_version`, `config_hash` | SHA-256 of the canonical JSON of prompt template + settings (temperature, max tokens, seed…) |
| `created_at` | UTC datetime; must be **before** `forecast_deadline` |
| `evidence_cutoff` | latest publication time allowed for evidence; ≤ `created_at` and ≤ `forecast_deadline` |
| `probability` | 0 ≤ p ≤ 1, or null if `status` ≠ `ok` |
| `rationale` | short text |
| `evidence` | list of `{url, title, published_at}`; every `published_at` ≤ `evidence_cutoff`; empty for `no_news` |
| `usage` | `{input_tokens, output_tokens, cost_usd, runtime_s}` |
| `status`, `error` | `ok` \| `failed` \| `refused` \| `unparseable`; error text if not ok |
| `supersedes` | earlier `forecast_id` or null (an update is a new record) |

### 1.3 `resolution@1`

| Field | Rule |
|---|---|
| `schema` | `"resolution@1"` |
| `question_id`, `question_hash` | must match |
| `outcome` | `yes` \| `no` \| `invalid` |
| `observed` | what the source said (e.g. "repo rate 6.00% → 5.75%") |
| `source_url`, `source_published_at` | the official document actually used |
| `resolved_at`, `resolved_by` | when and who (a person in milestone 1) |
| `note` | |

`resolved_at` must be after `forecast_deadline`. Only `yes`/`no` are scored; `invalid` is counted and reported, never scored.

## 2. Proposed first real question

```json
{
  "schema": "question@1",
  "id": "IN-ECO-RBI-0001",
  "question": "Will the RBI Monetary Policy Committee cut the policy repo rate at its first policy decision announced on or after 1 January 2027?",
  "details": "A cut means the repo rate announced in that decision is lower than the repo rate in effect immediately before the announcement. Scheduled and unscheduled MPC decisions both count.",
  "region": "india",
  "category": "economy",
  "topic": "monetary_policy",
  "type": "binary",
  "created_at": "2026-12-01T10:00:00+05:30",
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
  "origin": {"method": "manual", "note": "Milestone 1 pilot question"},
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
research/forecast/questions/IN-ECO-RBI-0001.json
research/tests/test_forecast_schema.py     valid question loads; each broken rule rejected
research/tests/test_forecast_scoring.py    hand-computed Brier values
research/tests/test_forecast_e2e.py        TEST- question + FakeClient → freeze → resolve → score
```

Order to write them: `schema.py` → its test → `validate.py` → `scoring.py` → its test → `store.py` → `runner.py` (with a `FakeClient` returning a fixed probability) → e2e test. A real LLM client comes after the e2e test passes.

Hand-checked Brier values for the scoring test: p = 0.7, Yes → 0.09; p = 0.7, No → 0.49; p = 0.5 either way → 0.25; p = 1.0, No → 1.0.

E2E test must also check that: a forecast after the deadline is rejected; writing the same `forecast_id` twice fails; a changed question file breaks the hash check; an `invalid` resolution is excluded from the score.

## 4. Timestamps: what git proves and what it does not

- Commit dates come from the computer's clock and can be set to anything (`GIT_COMMITTER_DATE`, amend, rebase). A commit date alone proves nothing to a reviewer.
- Pushing to GitHub adds a server-side record, but it is not designed as a public, permanent timestamp proof.
- Signed commits prove **who** made a commit, not **when**.

Stronger method, used for every frozen forecast batch before its deadline:
1. Compute the SHA-256 of the batch file.
2. Get an **RFC 3161 timestamp token** for that hash from a public timestamp authority (e.g. FreeTSA). Store the `.tsr` file next to the batch. Anyone can verify it with `openssl ts -verify`.
3. Also stamp the hash with **OpenTimestamps** (anchored in the Bitcoin blockchain; free). Store the `.ots` file.
4. Optional, for publication: deposit each frozen batch on **Zenodo** (dated DOI).

Only the hash leaves the machine, so forecasts stay private until you publish them.
