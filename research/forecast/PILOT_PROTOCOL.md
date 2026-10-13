# Forecasting records and the December 2026 pilot: protocol

Date: 14 October 2026 (decisions D1–D9 recorded the same day). Status: **approved in principle by the user, subject to final content review.** The research direction is chosen by the student; **formal M.Tech guide approval is pending.**

This is the **single source** for forecasting record formats. `MILESTONE_1.md`, `docs/ARCHITECTURE.md`, `docs/UI_SPEC.md` and the future Python backend refer to this file and must stay compatible with it. The paused Reflica benchmark in `../reflica_bench/` is not affected.

**Why it exists.** The implementation order is documentation → Flutter UI → Python backend → connect. The backend will not exist in December, so the 20-question pilot is recorded **by hand** in JSON/JSONL. The backend must later import these files **without changing** their content, timestamps, versions or provenance.

## 0. Recorded decisions (14 October 2026)

| # | Decision |
|---|---|
| D1 | **Primary leaderboard:** for each question, forecaster and condition, use the **latest eligible on-time forecast** made before the deadline. "Eligible" and the selection order are defined in section 7.1. Every other forecast record is kept for secondary analyses. |
| D2 | **Persistence baseline:** no arbitrary probability. Its method is documented and validated before any evaluation uses it (section 5). |
| D3 | **Official-forecast baseline:** **deferred** from the initial pilot unless a defensible conversion to a probability is established and documented in advance. |
| D4 | **Pilot models:** start the 20-question pilot with **2–3 models**; estimate API costs before expanding. |
| D5 | **Western comparison:** aim for **4–6 matched Western questions**; the comparison is **exploratory** and its limitations are reported. |
| D6 | **Forecast ID:** opaque unique id `FC-YYYYMMDD-NNNNNN` (e.g. `FC-20261201-000001`); model, question, condition and timestamps are stored in their own fields, never parsed from the id. |
| D7 | **Time and integrity:** UTC timestamps and record hashes are required. An external timestamping service is **evaluated before it is relied on**. Git timestamps alone are not tamper-proof proof. |
| D8 | **Code location:** the Python package stays inside `research/forecast/`, with code clearly separated from data (section 2). |
| D9 | **Late forecasts** are kept with an explicit `late` status and excluded from on-time evaluation. |

## 1. Workflow

```
official sources → candidate questions (generator or hand) → human review (editable)
  → frozen question definition → forecasts (append-only) → official outcome check
  → separate resolution record → scoring and reports
```

- A **candidate** may be edited freely during review. Its edits live only in git history.
- A question is **frozen** when its definition is appended to `questions/questions.jsonl`. This must happen **before its first forecast**. For the pilot, all 20 are frozen together in one `question_set` record before any forecast is collected.
- Once frozen, a definition is never changed. If a material defect is found, the question is **invalidated with a documented reason** (a `correction` record) and, if needed, replaced by a **new question ID**.

## 2. Folders

```
research/forecast/
  questions/
    candidates/            editable drafts, one JSON file per candidate (not research records)
    questions.jsonl        append-only: frozen question definitions, question_set freezes, corrections
  results/
    forecasts/forecasts.jsonl       append-only: model and baseline forecasts, corrections
    resolutions/resolutions.jsonl   append-only: outcomes, corrections
    reports/               generated tables and plots (re-creatable, not source data)
  prompts/                 prompt templates and baseline rules; never edited (new file = new version)
  stamps/                  external timestamp evidence (.tsr, .ots) and stamps.jsonl, used only if a service is adopted (D7)
  historical/              A3 past questions and their forecasts (same formats, kept apart)
  fixtures/                SYNTHETIC test records only (ids start with TEST-)
  pipeline/                Python code only (Phase 3; written by the user); no data files inside
```

Code and data are separate (D8): only `pipeline/` (plus `__init__.py` files) is Python code. Every other folder holds data or documents and is excluded from packaging.

Separation rules, which the importer enforces:
- `questions/` and `results/` hold only real prospective records. They must not contain a `TEST-` id, `"synthetic": true`, or `"kind": "historical"`.
- `historical/` holds only `"kind": "historical"`. Its results are never reported as the main forecasting performance.
- `fixtures/` holds only `TEST-` ids with `"synthetic": true`.

## 3. Line format, hashing and time

Every line in a `.jsonl` file is:

```json
{"record_type": "forecast", "record": { ... }, "record_hash": "sha256:<64 hex>"}
```

- `record` is the **original frozen record**, exactly as first written. Lines are never edited, deleted or re-ordered.
- `record_hash` = SHA-256 of `json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")`. This exact rule is part of the protocol, and the backend reuses it. Until the backend exists:
  ```
  python3 -c "import json,hashlib,sys;r=json.load(open(sys.argv[1]));print('sha256:'+hashlib.sha256(json.dumps(r,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest())" rec.json
  ```
- **Time:** every timestamp is timezone-aware ISO 8601. `*_utc` fields are UTC with `Z` and are authoritative. Records may also carry `*_ist` copies (`+05:30`) for display; they must be the same instant. Deadlines are written with an explicit offset.
- **Evidence hierarchy:** (1) the immutable record itself is primary; (2) its `record_hash` and the frozen `question_set` manifest are integrity evidence; (3) an external timestamp is additional timing evidence once tested and adopted (D7); (4) Git commits are supporting history only. Commit dates come from the local clock and can be changed, so they are not independent proof.
- **Derived reports** (scores, leaderboards, calibration tables) are always recalculated from the frozen records and never edited by hand.

## 4. Record types

### 4.1 `question` (`question@1`), immutable once frozen

| Field | Rule |
|---|---|
| `schema` | `"question@1"` |
| `question_id` | `IN-ECO-RBI-0001` style: `IN`/`WE` region, `ECO`/`CLI`/`INF` domain |
| `version` | review version of the candidate that was frozen (1, 2…); never changes after freezing |
| `kind` | `prospective` or `historical` |
| `question_text` | exact wording, one sentence ending in `?` |
| `details` | definitions a forecaster needs |
| `why_it_matters` | one or two sentences for the Question Details screen |
| `region` | `india` \| `western` |
| `domain` | `economy` \| `climate` \| `infrastructure` (energy is part of infrastructure) |
| `topic` | e.g. `monetary_policy`, `inflation` |
| `type` | `binary` |
| `indicator` | for numeric questions: `{name, units, period, threshold, comparison: "gt" \| "ge" \| "lt" \| "le", rounding, release: "first_official_release"}`; null otherwise |
| `created_at_utc` | when the frozen version was written |
| `forecast_deadline` | strictly before `expected_resolution_date` |
| `expected_resolution_date` | date, or the start of a window |
| `resolution_deadline` | if there is no result by then → `invalid` |
| `resolution_source` | `{name, publisher, url}` |
| `resolution_rule` | exact Yes/No rule; must agree with `indicator` |
| `invalid_rule` | when the question is annulled |
| `pair` | `{pair_id, matched_on: [...], known_differences: "..."}` or null (section 6) |
| `origin` | `{method: "manual" \| "generator", source_url, fetched_at_utc, note}` |
| `author` | person |

Question status is **not** stored in the question. It is derived from the records, checking these rules from the top and stopping at the first that matches (`now` = current UTC time):

| # | Condition | Derived status |
|---|---|---|
| 1 | Question invalidated by a `correction`, or its current resolution record says `invalid` | **Invalid** |
| 2 | Current resolution record says `yes` or `no` | **Resolved** |
| 3 | Frozen, and `now` ≥ `forecast_deadline` (with or without forecasts) | **Forecast Frozen** |
| 4 | Frozen, and `now` < `forecast_deadline` | **Open for Forecasting** |
| 5 | Candidate with `review_status: "validated"` (not yet frozen) | **Validated** |
| 6 | Candidate still being edited | **Draft** |

- "Current resolution record" = the latest resolution for the question that has not been superseded or invalidated by a `correction`.
- A question past its deadline is **never** shown as open, even if no forecast was collected. The app shows "0 forecasts" instead.
- *Draft* and *Validated* are review states of files in `questions/candidates/` (field `review_status`). Candidates are not research records.

### 4.2 `question_set` (`question_set@1`)

`{set_id: "pilot_v1", members: [{question_id, version, record_hash}, …] (sorted by id), frozen_at_utc}`.
Its `record_hash` is the **question-set hash** stored in every forecast. It is externally timestamped before the first forecast.

### 4.3 `forecast` (`forecast@1`), append-only

| Field | Rule |
|---|---|
| `forecast_id` | `FC-YYYYMMDD-NNNNNN` (UTC date the record is written + running number across all forecasts; e.g. `FC-20261201-000001`). Opaque: never parse meaning from it (D6) |
| `question_id`, `question_version`, `question_hash`, `question_set_hash` | must match the frozen records |
| `question_text`, `forecast_deadline`, `resolution_rule` | exact copies, so the record stands alone |
| `forecaster` | `{type: "model" \| "baseline", provider, name, version, access: "api" \| "console", stated_knowledge_cutoff}`; for baselines `provider: "baseline"`, `name` = rule id |
| `condition` | `no_news` \| `news` \| `baseline` |
| `prompt_version`, `prompt_hash` | the file in `prompts/` and the SHA-256 of its bytes (baselines: the rule file) |
| `settings`, `config_hash` | temperature, max tokens, seed, tools on/off…; hash of `settings` + `prompt_hash` |
| `created_at_utc` (+ optional `created_at_ist`) | when the answer was produced |
| `recorded_at_utc` | when the line was written |
| `evidence_cutoff_utc` | ≤ `created_at_utc` and ≤ `forecast_deadline` |
| `evidence` | `[{url, title, publisher, published_at_utc}]`, each ≤ cutoff; `[]` for `no_news` |
| `probability` | 0–1, or null when `status` ≠ `ok` |
| `rationale`, `raw_response` | short explanation; full verbatim reply |
| `usage` | `{input_tokens, output_tokens, cost_usd, runtime_s}`, null where unknown |
| `status`, `error` | `ok` \| `failed` \| `refused` \| `unparseable` |
| `collection_method`, `recorded_by` | `"manual_v1"` for the pilot; person |
| `timing_status` | `on_time` if `created_at_utc` **and** `recorded_at_utc` are before `forecast_deadline`, else `late` (D9). Set when the line is written; never changed |
| `supersedes` | earlier `forecast_id` for a deliberate update, else null |

### 4.4 `resolution` (`resolution@1`)

`{question_id, question_version, question_hash, outcome: "yes" | "no" | "invalid", observed_value, observed, source_url, source_published_at_utc, resolved_at_utc, resolved_by, note}`.
`resolved_at_utc` must be after `forecast_deadline`. Only `yes`/`no` are scored; `invalid` is counted and reported.

### 4.5 `correction` (`correction@1`)

`{corrects_record_hash, action: "invalidate" | "supersede", replacement_record_hash, reason, created_at_utc, author}`. The original line always stays.

## 5. Baselines: rules fixed in advance

Each baseline is a written rule in `prompts/baseline_<name>_v1.md`, hashed and frozen **before the deadline of every question it is applied to**. Its output is stored as an ordinary forecast record (`forecaster.type: "baseline"`, `condition: "baseline"`).
- **Base rate (pilot):** the share of Yes outcomes in a documented reference class and period (e.g. MPC decisions from date A to date B that were cuts), stored with the count. With very small counts, the documented rule states the smoothing used (for example adding one Yes and one No).
- **Persistence ("same as last time") (D2):** no arbitrary probability. Before use, the rule document must state how the probability is **estimated** (for example the observed frequency with which the outcome repeated in the documented reference class) and how it was **validated** on historical or development data. Until that document exists and is reviewed, this baseline is not used in any evaluation.
- **Official forecast (D3): deferred** from the initial pilot. A numeric official projection (e.g. an RBI CPI projection) is not a probability. It is used only after a conversion method is documented and justified in advance (for instance an error distribution estimated from past projection errors), or where the official source itself gives probabilities (e.g. IMD's category probabilities), with the category-to-Yes mapping written down first.

## 6. India–Western pairs

The pilot aims for **4–6 matched Western questions** (D5). The comparison is **exploratory**; no India-gap claim is made from it. A pair is a **matched comparison, not an equivalent question**. Match as closely as possible on indicator, forecast horizon, release schedule, threshold difficulty (e.g. distance from the last value) and wording. Record `matched_on` and the unavoidable `known_differences`, such as a different release lag or different rounding. Verify each Western question's release calendar and rule before freezing. Report results per pair set with its sample size and these limitations.

## 7. Collecting forecasts by hand

1. Freeze and stamp the question set first. No forecast before that.
2. Use the provider's API or console with known settings. Do not use a consumer chat app, whose browsing, memory and hidden settings make "no news" uncheckable. Web search is off for `no_news`.
3. **News condition:** collect the evidence first, record each item's publication time, set the cutoff, and give the model only that evidence.
4. Write the record the same day, hash it, append it, commit, and stamp the file.
5. **Never backdate.** If the exact call time is unknown, use the recorded time.
6. **On time vs late (D9):** a forecast is `on_time` only if it was produced **and** written to the file before the deadline. Write, hash and commit it the same day. Anything else is kept with `timing_status: "late"` and excluded from on-time evaluation. If an external stamp is adopted (D7), on-time records must also be covered by a stamp dated before the deadline.
7. **Updates** are new records with `supersedes`. The primary leaderboard uses the selection rule in section 7.1 (D1). All other records stay available for secondary analyses.
8. **Failures** are recorded and count towards the failure rate.

### 7.1 Eligible forecasts and the primary leaderboard (D1)

A forecast is **eligible** for the primary Brier-score leaderboard only when **all** of these hold:
1. `status` is `ok`;
2. `probability` is a number with 0 ≤ p ≤ 1;
3. its `record_hash` validates, and `question_hash` and `question_set_hash` match the frozen records;
4. `timing_status` is `on_time`;
5. its question's current resolution is `yes` or `no`;
6. the forecast is not invalidated by a `correction` record.

**Selection:** for each (question, forecaster, condition), first keep only the eligible forecasts, then take the **latest** of them by `created_at_utc` (ties broken by the later `forecast_id`). Do **not** take the latest record first and then drop it if it is ineligible: an earlier eligible forecast is used instead. If none is eligible, that combination has no primary-leaderboard entry.

Reported alongside, never mixed in:
- **Failure rate:** records with `status` ≠ `ok`, out of all records per forecaster and condition.
- **Late count:** records with `timing_status: late`.
- **Invalid and unresolved questions** are counted and reported. They are **never** treated as incorrect forecasts and are excluded from Brier scores.
- **Secondary analyses** (all versions, late forecasts, past questions) are labelled as such.

**External timestamps (D7: candidate, to be evaluated before relying on it).** The minimum for the pilot is UTC times, record hashes and same-day commits. These are supporting evidence, not tamper-proof proof. In November, evaluate RFC 3161 (e.g. FreeTSA) and OpenTimestamps on test files (cost, reliability, verification steps) and record the decision. If adopted, after each session:
1. Hash each changed `.jsonl` file.
2. Get an RFC 3161 token (e.g. FreeTSA; verify with `openssl ts -verify`) and an OpenTimestamps proof.
3. Append `{file, sha256, line_count, tsa, stamped_at_utc, proof_file}` to `stamps/stamps.jsonl`.

Because files are append-only, a stamp of the whole file also covers every earlier line. Only hashes leave the machine. Optional: a Zenodo deposit per frozen batch for publication.

## 8. Importing into the backend later

The backend reads the files **read-only**. It verifies every `record_hash`, the question-set membership, the folder separation rules and the stamp log, and refuses the files on any mismatch. It keeps every original field exactly. Import provenance (`imported_from: "results/forecasts/forecasts.jsonl#L12"`, `imported_at_utc`) is stored **outside** the original record. The original files are never rewritten.

## 9. Examples

### 9.1 Event question (`IN-ECO-RBI-0001`)
See `MILESTONE_1.md` section 2. "Will the RBI MPC cut the policy repo rate at its first policy decision announced on or after 1 January 2027?" (`indicator: null`). The dates marked `XX` must be filled from RBI's schedule before freezing.

### 9.2 Threshold question (consistent threshold, rounding, first release)

```json
{
  "schema": "question@1",
  "question_id": "IN-ECO-CPI-0001",
  "version": 1,
  "kind": "prospective",
  "question_text": "Will India's all-India CPI (Combined) year-on-year inflation for January 2027, as first officially released by MOSPI, be above 4.0%?",
  "indicator": {"name": "CPI (Combined) y/y inflation, all India", "units": "%", "period": "2027-01", "threshold": 4.0, "comparison": "gt", "rounding": "as published, one decimal place", "release": "first_official_release"},
  "resolution_rule": "Use the first official MOSPI release of the January 2027 figure, as published to one decimal place. Strictly greater than 4.0 → Yes; 4.0 or below → No. Later revisions are ignored.",
  "invalid_rule": "Invalid if MOSPI has not released the January 2027 figure by the resolution deadline, or the series definition changes before release.",
  "pair": {"pair_id": "CPI-2027-01", "matched_on": ["indicator type", "reference month", "threshold set from recent trend"], "known_differences": "US CPI (BLS) is released on a different date and uses a different basket; record both release dates before freezing."}
}
```

Fields not shown follow section 4.1. The release date, the series definition and the base year must be checked on MOSPI's site before freezing. The threshold `4.0` appears identically in the text, the `indicator` and the rule.

## 10. Pilot timeline (working targets)

| When | Step |
|---|---|
| Oct–Nov 2026 | Approve this protocol; write prompt v1 and the baseline rules; draft ~20 India candidates + a few Western pairs; check every source, release date and rule |
| Nov 2026 | Evaluate an external timestamping service (D7); document the base-rate rule; estimate API cost for 2–3 models |
| Late Nov 2026 | Final review; choose the 2–3 models (D4) and the monthly API budget |
| By 1 Dec 2026 | Append the frozen definitions and the `question_set`; stamp them |
| Dec 2026 | Record forecasts and the base-rate baseline before each deadline; commit (and stamp, if adopted) after each session |
| Jan–May 2027 | Resolve from the named sources; score `yes`/`no` only; report invalid, late and failed counts |
