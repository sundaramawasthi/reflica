# Data Feasibility Report (Task 2), Part B CPI

> **Date:** 16 Oct 2026 · **Method:** web search only. MoSPI, RBI and PIB sites are blocked from this cloud, so **no data was downloaded**.
> **Statuses:** **Verified** = checked against source or data (none yet) · **Partially verified** = search result or incomplete documentation · **Blocked** = unresolved.

| # | Check | Source and URL | Coverage / frequency | Timing | Access | Status | Risks |
|---|---|---|---|---|---|---|---|
| 1 | Historical CPI (all-India Combined, y-o-y) | MoSPI / e-Sankhyiki; [PIB first release, base 2024](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2227012&reg=3&lang=1); [MoSPI FAQ on the 2024 series](https://www.mospi.gov.in/uploads/documents/documents/1770891066052-Annexure_V.pdf) | Monthly. Old series base 2012 (from 2011/2013). New series base **2024 = 100** from **Jan 2026** (first release 12 Feb 2026; Jan 2026 = **2.75%** provisional). Official **back series of annual inflation rates Jan 2014 – Dec 2024** announced (one secondary source says 2013) | — | Public (download page not confirmed) | **Partially verified** | Exact back-series range; whether indices or only rates are published |
| 2 | Release dates and times | [MoSPI Advance Release Calendar](https://mospi.gov.in/sites/default/files/Advance_Release_Calendar.pdf); [MoSPI PIB note, 18 Nov 2024](https://mospi.gov.in/sites/default/files/press_release/MoSPI_PIB_Press_release_18112024.pdf) | — | **12th of each month** (next working day if a holiday); **5:30 PM → 4:00 PM IST from the Oct 2024 data** | Public | **Partially verified** | Actual historical release timestamps (not just the rule) need a per-month list; first-release vs revised values (vintages) not yet found |
| 3 | Base-year transition | [PIB release](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2227012&reg=3&lang=1); [secondary explainer](https://www.drishtiias.com/daily-updates/daily-news-analysis/cpi-base-year-revised-to-2024) | Linking factor **Combined 0.5267** (Rural 0.5222, Urban 0.5320), from 2025 overlap-year averages; old index × factor = new-base index | — | Public | **Partially verified** | The back series is **mechanical** (old basket rescaled, not reweighted). Possible break at Jan 2026; y-o-y in 2026 compares new-basket vs linked-old values |
| 4 | Dated news | [Kulkarni "India News Headlines" (Kaggle via Baselight)](https://baselight.app/u/kaggle/dataset/therohk_india_headlines_news_dataset); [Times of India headlines (HF/TFDS)](https://www.tensorflow.org/datasets/community_catalog/huggingface/times_of_india_news_headlines) | Times of India **headlines only**, 2001 → **June 2023** (~3.9M rows; HF version to mid-2020); daily date (yyyyMMdd), no time of day | Date-level only | Kaggle; **licence unclear** (HF lists none) | **Partially verified** | **No coverage after Jun 2023**; headlines lack article text and source URLs, so claim extraction is weak; GDELT India not checked; official text (PIB, RBI press releases and MPC statements) is a likely dated, public alternative (**not yet checked**) |
| 5 | Feasible test period | Derived from 1–4 | CPI y-o-y usable ~2014 → present (≈150 months). News (ToI) to Jun 2023 | — | — | **Partially verified** | Overlap of CPI and ToI ≈ 2014 – Jun 2023 (≈114 months), but this includes COVID. Post-2023 tests need a new news source. The 2026 base change falls inside any live period |

## Provisional design implications (not frozen)

1. **CPI target:** use the official linked series. Run a robustness check that excludes, or flags, months after the base change (2026 onward).
2. **Split (candidate):** train 2014–2019, validate 2020–2021, test 2022 – Jun 2023, all on the linked old series with ToI news. Only ~18 test months, so statistical power is low; report confidence intervals.
3. **News:** ToI headlines are enough for the **index baselines** (sentiment, word counts). **Claim-level, source-linked extraction needs article text and URLs.** Candidates are PIB, RBI and MoSPI official releases (dated, public) and a licensed news archive. **This is the main blocker for G2.**
4. **Point-in-time:** release rule known (12th, 4 PM / 5:30 PM). Historical per-month dates and first-release values still have to be compiled.

## Blocked / to resolve

- **Post-2023 dated news with full text and URLs** (needed for claim-level evidence and any live test): **Blocked**.
- CPI vintages (first-release values): **Blocked**, not found yet.
- Download of the official back series: needs your browser (MoSPI is blocked here).

## Overall verdict (provisional)

The **numeric part is feasible**. **Index-level text tests are feasible to Jun 2023.** The **claim-level G2 test is not yet feasible** until a full-text, dated news or official-release source is secured. We may need to centre claim evidence on **official releases** (PIB, RBI, MoSPI) rather than newspapers.
