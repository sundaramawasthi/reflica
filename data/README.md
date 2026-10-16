# data/: IndiaEconForecast datasets

**Key rule:** never use a document or CPI value in a historical forecast before its **actual publication time**.

```
data/
  raw/cpi_releases/     original MoSPI/PIB CPI press releases + Excel/PDF annexures (keep the originals)
  raw/pib_documents/    original PIB releases (HTML/PDF), named <document_id>.<ext>
  raw/rbi_documents/    original RBI statements, minutes and reports, named <document_id>.<ext>
  processed/cpi_release_calendar.csv   Dataset 2: release dates + first-release values
  processed/source_documents.csv       Dataset 3: one row per document
  processed/claims.csv                 Dataset 3: one row per extracted claim
```

## Rules
- Record the publication date/time **shown on the release**. If it is missing, leave it blank and mark it; **never estimate it from the usual schedule**.
- Mark `first_release_verified = Yes` only when the value comes from the **original dated release**, not from a later historical table.
- Keep the original file. Do not replace it with an AI summary.
- `timestamp_confidence`: verified / date-only / uncertain.
- `direction` (claims) = the claim's *potential* implication: inflationary / disinflationary / mixed / unknown. It is not a judgement of truth.
- One row per URL. If several keywords find the same document, list all of them in `search_keywords` (separated by `;`).

## Pilot (Jan–Mar 2026)
- **CPI releases:** start with the latest month and work backwards.
- **PIB keywords (essential):** inflation, CPI, Consumer Price Index, retail inflation, headline inflation, core inflation, food inflation, rural inflation, urban inflation, inflation outlook; food prices, vegetable prices, pulses, edible oil, wheat, rice, onion, tomato, buffer stock, food supply; monsoon, rainfall, kharif, rabi, crop production, heatwave, drought, flood; fuel prices, petrol, diesel, LPG price, excise duty, crude oil, electricity tariff, freight; export ban, import duty, stock limits, MSP, PMGKAY, open market sale scheme.
- **RBI:** Monetary Policy Statement, MPC Resolution, MPC Minutes, Governor's Statement, inflation outlook, State of the Economy, Inflation Expectations Survey of Households, food inflation.
- Then audit: timestamp quality, full-text availability, number of inflation-relevant documents before each cutoff.

PIB_2026_001 and PIB_2026_002 were found by the user (search "inflation", posted 29 Jan 2026). Their URL, time and full text are **still to be filled in**.

## Revised CPI series (training only), added 2026-10-16
`processed/cpi_series_revised_2026-10-16.csv`: All-India CPI General, Rural/Urban/Combined, from the
MoSPI CPI API (login token; see `docs/CPI API User Manual.pdf`). **vintage = latest_revised: never first release.**
- 2012=100 **Current** series: index 2013-01 → 2025-12; y-o-y 2014-01 → 2025-12.
- 2012=100 **Back** series: 2011-01 → 2013-05 (Rural to 2012-12); y-o-y from 2012-01. Back/Current overlap Jan–May 2013 with different values: keep the `series` column.
- 2024=100 series: index 2025-01 → 2026-09; y-o-y from 2026-01 (2025 = linking overlap year).
- y-o-y missing for **Apr–May 2020** (COVID lockdown; not published). Not imputed.
- Raw pages + manifest (request URL, time): `raw/cpi_api/`. Rebuild: `data/scripts/fetch_cpi_api.py` then `data/scripts/build_cpi_series.py`.
- API quirks: page limit 100; `level=Group` (case-sensitive); All-India = `state_code=99` (base 2012) but `state_code=1` (base 2024); headline = `division_code=0` (2024); `series=Current|Back` (2012); Python ssl fails → curl. Credentials only in env `MOSPI_USER`/`MOSPI_PASS`.
