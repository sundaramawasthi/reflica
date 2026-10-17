# Presenter's Guide: Know Reflica Inside Out (Semester 1)

> For the **first PPT** and the **semester-1 paper**. Simple explanations, key numbers, and likely faculty questions with answers.
> Related files: `docs/PPT_CONTENT.md` (slides), `docs/research_archive/review_paper/REVIEW_PAPER_DRAFT.md` (paper, v0.6), `docs/PROJECT_REPORT.md` (what we did).

---

## 1. Do we have enough for semester 1?

| Deliverable | Needed | Do we have it? |
|---|---|---|
| **1st PPT** | Problem, literature, gap, proposed system, method, plan | ✅ **Yes**: everything in `PPT_CONTENT.md` |
| **Semester-1 paper** (review + proposal paper) | Literature review, comparison, gap, proposed framework, dataset | ✅ **Yes**: `REVIEW_PAPER_DRAFT.md` v0.6 |
| Results / accuracy | Only for the final PPT | ❌ **Not needed now.** Say clearly: "experiments are next semester" |

**So yes, the data and material are enough for semester 1.** Don't show fake results. Faculty respect "planned evaluation" more than invented numbers.

---

## 2. Your 1-minute pitch (memorise this)

> "India's inflation, measured by CPI, affects every household. New AI tools claim to predict the economy, but they are rarely tested fairly on Indian data, and they don't explain **why** a forecast changes.
> My project, **Reflica India**, forecasts India's CPI inflation with a numerical model. It then reads official documents from the **RBI and the government**, extracts specific dated claims, and uses a **fixed, bounded rule** to decide whether the forecast should change and by how much. Every change is logged with its source.
> I'll test it fairly: only information available **before** each forecast date, compared with simple and strong baselines.
> So far I've reviewed about 59 papers, found the research gap, and built a dataset of **613 months of CPI, 33 first releases with exact dates, and 81 official documents**, including all 22 RBI policy statements since 2023. Next semester I run the experiments."

---

## 3. Key concepts, explained simply

| Term | Simple meaning | Why it matters to us |
|---|---|---|
| **CPI** | Consumer Price Index: the average price of what households buy | Our target |
| **Headline CPI inflation (y-o-y)** | How much prices rose compared with the same month last year | What we forecast (e.g., Aug 2026 = 4.82%) |
| **Base year** | The reference year where the index = 100 | Changed from 2012 to 2024 in Feb 2026, which creates a **series break** |
| **Linking factor** | A number to convert the old series to the new one | 0.5267 for Combined |
| **First release** | The value published the first time | A fair test must use this, not later revised values |
| **Revision** | A later change to a published value | e.g., Jan 2026: 2.75% → 2.74% |
| **Point-in-time / no leakage** | Use only what was public at that moment | Our most important rule |
| **Walk-forward test** | Train on the past, forecast the next month, then move forward one month | The fair way to test time series |
| **Baseline** | A simple model to beat | Naive (last value), SARIMA, XGBoost |
| **SARIMA** | A classic statistical model for time series with seasons | Strong for Indian CPI in past studies |
| **XGBoost** | A machine-learning model (boosted trees) | A non-linear baseline |
| **Claim** | One dated sentence from an official document, e.g. "wheat stock limits tightened to moderate prices" | Our evidence unit |
| **Source-linked** | Every claim keeps its document, date and link | Makes forecasts explainable and auditable |
| **Bounded revision rule** | A fixed rule that may adjust the forecast only by a limited amount | Prevents overreaction to news |
| **Never / always update** | Comparison policies: ignore news vs always follow it | We test whether our rule beats both |
| **MAE / RMSE** | Average size of the forecast error (RMSE punishes big errors more) | Main metrics for CPI |
| **Diebold–Mariano (DM) test** | A statistical test of whether one forecast is really better than another | Avoids claiming luck as skill |
| **Brier score / calibration** | Accuracy of yes/no probabilities: does "70%" happen about 70% of the time? | For Part A (LLM benchmark) |
| **MPC** | RBI's Monetary Policy Committee, which sets the repo rate about 6 times a year | Its statements are our richest evidence |

---

## 4. Numbers to remember

- ~**59** papers checked, **22** read in full.
- **613** rows of CPI (2013 – Sep 2026).
- **33** first releases with exact dates (Dec 2025; Jan 2024 – Aug 2026).
- **81** official documents: **22** MPC resolutions (all, Apr 2023 – Oct 2026), **8** Monetary Policy Reports, **2** MPC minutes, the **Economic Survey** 2025-26, and **14** PIB price releases.
- CPI inflation in 2026: **2.75% (Jan) → 4.82% (Aug)**.
- CPI base change: **2012 → 2024**, from the **Jan 2026** data (first released **12 Feb 2026**).
- Release time: **4:00 PM**, normally on the 12th. It moves when the 12th is a weekend (13 Apr, 13 Jul, 14 Sep 2026).

---

## 5. The research gap in one breath

> "Numerical CPI models exist (RBI, 2025). News-based inflation indices exist (Pratap 2021, Das & Das 2024). LLMs that update forecasts from news exist (LiveMacroEval 2026), and LLM text has been added to CPI models (LLM-CPI 2025). But **among the works I reviewed**, none tests **claim-level, source-linked evidence with a fixed bounded revision rule** on **Indian headline CPI**, compared with never- and always-update policies under strict point-in-time testing."

**Don't say** "first" or "novel". **Say** "among the works reviewed".

---

## 6. Likely faculty questions, with answers

1. **Why not just use an LLM to predict inflation?**
   In a live test, LLM agents were **weakest on inflation** (LiveMacroEval), and LLMs may have memorised past values. So a numerical model forecasts, and the LLM only extracts claims.
2. **What's new compared with existing work?**
   The combination: claim-level evidence, a bounded revision rule, a policy comparison, and Indian headline CPI with point-in-time data. It's a fair **test**, not a claim to have invented news-based forecasting.
3. **Why official documents and not newspapers?**
   We need exact publication times and full text. Free news archives end around 2023 and lack links. RBI and PIB documents are dated, public and linkable.
4. **How do you avoid data leakage?**
   Every value and document has a publication time, and we use first-release CPI values in testing. For example, an RBI press-conference transcript held on 8 Feb 2024 was only published on about 15 Apr 2024, so we use it only from that date.
5. **What about the CPI base-year change?**
   We use the official linking factor (0.5267), run a robustness check around Jan 2026, and flag COVID-imputed months (Apr–May 2020).
6. **What if your method doesn't improve accuracy?**
   That's still a valid result. It shows that text evidence doesn't help beyond strong numbers, and we will report it honestly.
7. **How many test points do you have?**
   About 32 monthly first releases (Jan 2024 – Aug 2026), plus a longer walk-forward test on the revised history. It's small, so we use the DM test and confidence intervals, not just averages.
8. **Which metrics, and why not accuracy or F1?**
   CPI is a **number** (regression), so we use MAE, RMSE and the DM test. Accuracy and F1 are for classification. Brier score and calibration are used only for Part A's yes/no questions.
9. **What is a "bounded" revision?**
   The rule may move the forecast only up to a set limit. Research shows forecasters often overreact to news (Bordalo et al. 2020), so smaller, controlled updates can be more accurate.
10. **Real-world use?**
    Inflation monitoring for researchers, analysts and students; explainable forecasts with sources. Not a replacement for RBI or official statistics.
11. **What technology?**
    Python (pandas, statsmodels, scikit-learn, XGBoost), an LLM for extraction, and Flutter + Firebase for the dashboard.
12. **What's Minor Project 2?**
    Calibrated probabilities for RBI policy decisions (cut / hold / hike), with the ability to say "not enough evidence". It's provisional.

---

## 7. Semester-1 paper plan (review + proposal paper)

**File:** `docs/research_archive/review_paper/REVIEW_PAPER_DRAFT.md` (v0.6). **Type:** review and proposal paper, with **no results**, which is fine for semester 1.

| Section | Content | Status |
|---|---|---|
| Abstract | Problem, review, gap, proposed framework | ✅ (refresh the final wording) |
| I. Introduction | CPI in India, why revision matters | ✅ |
| II. Background | CPI, revision, leakage | ✅ |
| III. Review method | How papers were selected and read | ✅ |
| IV. Literature review | Numeric CPI, text indices, LLM forecasting, revision, leakage | ✅ |
| V. Comparative analysis | Table comparing the studies | ✅ |
| VI. Research gap | Narrowed gap (v8) + RQ1–RQ3 | ✅ updated |
| VII. Proposed framework | Pipeline, revision rule, evaluation plan | ✅ |
| VII-A. Dataset | What we collected | ✅ new |
| VIII. Limitations | Reading levels, small test set | ✅ |
| IX. Conclusion | Contributions and next steps | ✅ |
| References | 46, each with its reading level | ✅ (check the [A] / [verify] items before submission) |

**Before submitting:**
1. Add your guide's name.
2. Convert to the IEEE Word template (the `.docx` in the same folder is from v0.5, so regenerate it).
3. Check every reference marked **[A]** (abstract only) or **[verify]**.
4. Keep the wording "among the works reviewed".

---

## 8. Present status honestly

- **Done:** literature review, research gap, proposal, data collection.
- **Next semester:** claim extraction, freezing the protocol, experiments, dashboard.
- **Never** show accuracy numbers until the experiments are run.
