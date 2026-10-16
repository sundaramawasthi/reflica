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
