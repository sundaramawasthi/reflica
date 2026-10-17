# Project Report: How We Built IndiaEconForecast / Reflica India (Steps 1–6)

> **Student:** Sundram Awasthi · M.Tech CSE (2026–28), GLA University · **Report date:** 17 Oct 2026
> **Title:** IndiaEconForecast / Reflica India: Hybrid AI Forecasting of Indian Economic and Policy Outcomes
> **Field:** Predictive AI for India's Economy and Public Policy
> **Status:** steps 1–6 done (planning, literature, gap, proposal, feasibility, data). **No experiments or results yet.**

---

## Overview (mind map)

```
STEP 1 Direction ✅ → STEP 2 Literature ✅ → STEP 3 Gap ✅ → STEP 4 Proposal ✅
   → STEP 5 Feasibility ✅ → STEP 6 Data ✅ → STEP 7 Claims ⏳ (WE ARE HERE)
   → STEP 8 Protocol ⏳ → STEP 9 Experiments ⏳ → STEP 10 Dashboard + Report ⏳
```

---

## Step 1: Choose the direction (13–16 Oct 2026)

**What we did**
1. Paused the old Reflica thesis (plan graphs and revision of plans) and archived its code in branch `archive/old-reflica-2026-10-14`.
2. Chose a new direction: AI forecasting of Indian economic and policy events.
3. Wrote and compared two candidate Minor 1 plans:
   - **A. LLM forecasting benchmark:** LLMs answer yes/no questions about future Indian events, and are scored with the Brier score and calibration.
   - **B. CPI forecasting with news-based revision:** a numerical CPI model, plus news claims, plus a rule for when to change the forecast. It has 8 features.
4. **Decision: the "safer merge".** Keep both as Part A and Part B, evaluated separately and never combined into one score. All 8 features are kept, with priorities.
5. Fixed the official title (16 Oct) and cleaned the repository. Old plans were removed (they remain in git history), and research files were kept.

**How:** we compared the plans for feasibility, risk and evidence, and recorded each decision in `PROGRESS.md` and `docs/research_archive/DECISION_RECORD.md`.

---

## Step 2: Literature review

**What we did**
1. Checked about **59 papers**, 22 of them read in full or near-full.
2. Verified every citation and marked its reading level (full text, key sections, or abstract only). Wrong claims were corrected; for example, a paper cited as "BIS 2026" was really PIER Thailand.
3. Wrote a **7-point record** for the 5 key papers: problem, data, method, baselines, metrics, findings and limitations, and relevance to us.
   - Mohan et al. 2025 (RBI): 216-model CPI combination.
   - Pratap et al. 2021 (RBI): news sentiment for food inflation.
   - Das & Das 2024: newspaper headlines plus ML.
   - Forecast-Dojo 2026: LLM agents with an evidence ledger.
   - LiveMacroEval 2026: live LLM nowcasts of US indicators.

**How:** you uploaded PDFs, which I read section by section. Blocked sites were searched instead and marked "search-level only". Files: `docs/research_archive/literature/`, `research/forecast/LITERATURE_RECORDS.md`.

---

## Step 3: Research gap

**What we did**
1. Compared the closest methods (`CLOSEST_METHODS.md`):
   - **LiveMacroEval:** LLM updating has no fixed rule, and agents are weakest on CPI.
   - **LLM-CPI (Fan et al. 2025):** LLM text plus a CPI model, but no revision policy.
   - **Modugno / Thorsrud:** news-driven forecast updating already exists.
2. Searched the theory on forecast revision: forecasters can over- or under-react (Bordalo et al. 2020), and smaller (shrunk) updates can reduce error.
3. Investigated **G3** (does news help Indian CPI?). The Indian evidence is mixed and the study designs are weak.
4. Built the final gap matrix and narrowed G2 step by step (v6 → v7 → v8).

**Result: the candidate gaps**

| Gap | Statement | Confidence |
|---|---|---|
| G1 | No India-specific prospective LLM forecasting benchmark found | Low–medium |
| G2 (v8) | Claim-level, source-linked evidence plus a bounded revision rule for Indian headline CPI, vs other update policies | Medium |
| G3 | Whether text helps Indian CPI is an open empirical question | Medium–high |
| G4 / G5 | Minor 2: calibrated policy probabilities and abstention | Not assessed |

**No novelty is claimed.** The wording used is "among the works reviewed".

---

## Step 4: Research proposal

**What we did:** wrote `RESEARCH_PROPOSAL.md`. It covers:
- the field, subfield, domain and specific area;
- Minor 1: introduction, problem, motivation, applications, gaps, challenges, contributions, architecture, the 8 features, methodology and timeline;
- Minor 2 (provisional): calibrated probabilities and abstention for RBI decisions.

We also wrote `docs/PPT_CONTENT.md` with slide content for the first and final presentations.

---

## Step 5: Data feasibility

**What we checked** (`research/forecast/DATA_FEASIBILITY.md`)
1. **CPI base change:** 2012=100 → **2024=100** from the Jan 2026 data. The linking factor is 0.5267.
2. **Release timing:** the rule is the 12th of each month at 4 PM, but actual dates shift. For example, 13 Apr, 13 Jul and 14 Sep 2026, when the 12th fell on a weekend.
3. **News problem:** we found no dated full-text news archive after 2023. **Decision:** use **official documents** (RBI, PIB, Ministry of Finance) as the evidence source.

---

## Step 6: Data collection

**Core rule:** never use a number or a document before its **actual publication time** (`data/README.md`).

**How we collected the data**
1. **CPI revised series:** downloaded through the **MoSPI e-Sankhyiki API** (`data/scripts/fetch_cpi_api.py`, run on the Mac because the cloud was blocked). Every raw API page is saved, plus a manifest.
2. **CPI release calendar:** saved each original press release and recorded its release date, time, first-release value and link.
3. **Vintages and revisions:** compared releases and found revisions. For example, Jan 2026 inflation went 2.75% → 2.74%, and the July index went 107.94 → 107.95.
4. **Documents:** you downloaded PDFs from RBI and PIB and uploaded them. For each one I:
   - checked for duplicates, by file bytes and by press-release ID;
   - read the title, posting date and time, and press-release ID from the document itself;
   - saved the PDF plus a text copy;
   - added a row to `source_documents.csv` with a timestamp confidence (verified / date-only / uncertain).
5. Kept private or copyrighted files out of the public repo. Research papers and the company plan are in the git-ignored folder `docs/local_private/` on the Mac.

**Dataset summary (17 Oct 2026)**

| Dataset | Size |
|---|---|
| CPI revised series (2013 – Sep 2026, Rural / Urban / Combined) | 613 rows |
| CPI first-release calendar (Dec 2025 + Jan 2024 – Aug 2026) | 33 months |
| RBI MPC resolutions (Apr 2023 – Oct 2026, no gaps) | 22 |
| RBI MPC minutes / Monetary Policy Reports / transcripts | 2 / 8 / 2 |
| Economic Survey 2025-26 | 1 |
| PIB price-evidence releases (2024: 5 · 2025: 6 · 2026: 3) | 14 |
| All registered documents | 81 |
| Claims extracted | 0 (next step) |

**Data quality notes**
- Apr–May 2020 CPI values were imputed during COVID, so they will be flagged.
- PIB_2025_004 duplicates PIB_2025_003 and is still to be marked.
- The rice-export note is a secondary source and is excluded from forecasting.
- The WPI base also changed (2011-12 → 2022-23, Jun 2026).

---

## Steps 7–10: Remaining work

| Step | Work |
|---|---|
| 7 | **Claim extraction:** for each document, the claim text, topic, direction, date and source → `claims.csv` |
| 8 | **Freeze the protocol:** horizon, train / validation / test split, baselines, metrics, failure criteria |
| 9 | **Experiments:** naive / SARIMA / XGBoost → text indices → claims → bounded revision; walk-forward test; MAE / RMSE / DM (Part B), Brier / calibration (Part A) |
| 10 | Minimal dashboard (Flutter + Firebase) and final report |

**Overall progress:** planning and data are done, and the experiments haven't started. That's about **50%** of Minor Project 1.
