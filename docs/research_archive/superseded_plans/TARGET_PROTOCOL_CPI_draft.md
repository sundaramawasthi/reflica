# Step 2: Target definition and point-in-time (leakage-control) protocol

**Version:** draft v0.1, 15 Oct 2026 · **Status:** for discussion; not frozen.
Facts marked **[verify]** must be checked against official MoSPI / RBI documents before the protocol is frozen. This file contains **no results**.

---

## 1. Target

| Item | Decision |
|---|---|
| Series | **All-India CPI – Combined (Rural + Urban), General Index**, published by NSO / MoSPI |
| Transformation | **Year-on-year inflation**, π_m = 100 × (I_m / I_{m−12} − 1), where I_m is the general index for reference month m |
| Why y-o-y | This is the headline rate the RBI targets (4% ± 2%) and the figure MoSPI publishes; it is what users read. (Mohan et al. use SAAR; see §7 for comparability) |
| Rounding | Compute from the index to 2 decimals; also store MoSPI's published rate for a cross-check |
| Base years | **2012 = 100** series up to its last published month, and the new **2024 = 100** series from its launch (reported here as Feb 2026) **[verify launch month and the official linking factor / back-series]**. Y-o-y rates spanning the change **must use MoSPI's official linking method**, never a self-made splice |
| Sub-indices (inputs only) | Food & beverages, fuel & light, core (excluding food and fuel) may be used as **inputs**, not targets, in Minor 1 |

## 2. Forecast origins (when each forecast is made)

Let **R_m** be the official CPI release date-time for reference month m. It is usually around the 12th of month m+1 **[verify the exact release rule, time of day (IST) and holiday shifts from MoSPI's advance release calendar]**.

Each target month m gets **three fixed checkpoints**. All three forecast the **same target π_m** (a fixed-event forecast).

| Checkpoint | Origin (IST) | Latest CPI known | Role |
|---|---|---|---|
| **C1** | R_{m−1} + 1 day, 23:59 (about the 13th of month m) | Month m−1 (just released) | **Initial forecast**, one month ahead: the first unpublished month |
| **C2** | Last calendar day of month m, 23:59 | Month m−1 | **Revision point 1**: the reference month is over |
| **C3** | R_m − 2 days, 23:59 (about the 10th of month m+1) | Month m−1 | **Revision point 2**: final pre-release update |

- "**One-month-ahead CPI inflation**" means **π_m forecast at C1**, where m is the first month whose CPI is not yet published.
- C2 and C3 are **revisions** of that same forecast. Revision policies are compared at **the same checkpoints**, so horizons are equal.
- The **scored forecast** for each policy is the one in force at **C3** (the last before release). C1 and C2 errors are also reported.

## 3. Available information at an origin

An item may be used at origin *t* **only if its first public timestamp is earlier than *t***.

| Source | Content | Timestamp used | Notes |
|---|---|---|---|
| MoSPI CPI press releases | Indices, provisional and final | Release date-time | Archive the PDFs to rebuild vintages (§4) |
| MoSPI / DPIIT WPI | Wholesale prices | Release date-time **[verify day]** | Optional input |
| DCA (Dept. of Consumer Affairs) | Daily retail and wholesale prices of essential items | Date of observation + publication lag **[verify]** | Key for food (tomato, onion, potato, pulses) |
| PPAC | Indian-basket crude price; retail fuel prices | Date published | |
| RBI / FBIL | INR–USD reference rate; repo rate; MPC statements | Date-time published | |
| IMD | Rainfall departure (weekly) | Date published | |
| News and official text (PIB, newspapers) | Articles from which claims are extracted | **First-publication timestamp** of each article | Drop items with no reliable timestamp. Store the URL, outlet and retrieval date |

Rules:
1. **No same-period leakage.** A feature for month m may only use data published before the origin, even if the data refer to earlier days.
2. **No revised-data leakage.** Use the **vintage** available at the origin (§4), not today's revised value.
3. **News timestamp rule:** use the earliest of (publisher timestamp, archive capture time). If they disagree by more than a day, flag the item and exclude it from the main run.
4. **Claim faithfulness:** every LLM-extracted claim must quote a span that appears in its source article. Unsupported claims are dropped.

## 4. Data revisions and vintages

- MoSPI typically publishes the latest month as **provisional** and revises the previous month to **final** in the next release **[verify]**.
- **Inputs:** use the value as known at the origin (**real-time vintage**). Rebuild vintages from archived monthly press releases. If a vintage cannot be rebuilt, record this and use the earliest available value.
- **Evaluation target:**
  - **Primary:** the **first published** value of π_m (what users saw at R_m).
  - **Robustness:** the **final** value published one month later.
- Other inputs (GDP, output gap) are revised more heavily. They are **excluded from Minor 1 baselines** unless real-time vintages are available, and any one-sided filter must use data up to the origin only (no full-sample HP filter).

## 5. Sample split (chronological; never shuffled)

| Period | Months (target m) | Use |
|---|---|---|
| Burn-in | 2012-01 → 2013-12 | First y-o-y values; lags only **[verify the CPI-C 2012 = 100 start month]** |
| **Training** | 2014-01 → 2018-12 | Fit baseline models (expanding window) |
| **Validation** | 2019-01 → 2021-12 | Choose models and **freeze all gate thresholds and weights**. Includes COVID; Mar–May 2020 imputed CPI items are flagged and reported separately |
| **Test (held-out)** | 2022-01 → base-change month − 1 | Run **once** with frozen settings. Main results |
| **Post-cutoff / live** | New base series onward, plus the live trial | Supplementary. Mostly after the LLM training cutoffs used for extraction, so it serves as a lookahead-bias check |

- Models are re-estimated at each origin on data up to that origin (walk-forward, expanding window). A rolling window is a robustness check.
- **Nothing in the test period may influence any design choice.** Any change after viewing test results must be reported as exploratory.

## 6. Revision policies to compare (defined before testing)

All policies start from the **same numeric forecast at C1** and differ only in how C2 and C3 are handled.

| Policy | Rule at C2 and C3 |
|---|---|
| **Never-update** | Keep the C1 forecast |
| **Always-update (numeric)** | Re-run the numeric model with all data available at the checkpoint (news-decomposition style; no text) |
| **Small-step** | Move a fixed fraction λ toward the always-update forecast (λ chosen on validation) |
| **Text-always** | Always-update plus all extracted text signals, with no gate |
| **Gated (Reflica)** | Revise only if the claim score (novelty, reliability, relevance by CPI weight, strength) passes a threshold fixed on validation. The step size is bounded. Every decision is logged |

## 7. Benchmarks and comparability with Mohan et al. (2025)

- Mohan et al. forecast **SAAR**, not y-o-y, over a different period and horizons. **Their published RMSEs will not be compared with ours.**
- Instead, we will **re-implement a reduced Mohan-style suite** on **our** target, origins and split:
  - random walk;
  - AR/SARIMA;
  - an ARX with crude, INR–USD and repo rate;
  - a small ML set (RF / SVR);
  - an **equal-weight** and an **inverse-RMSE** combination.
- As an optional cross-check, also report an m-o-m SAAR version of the best model.
- Other baselines: the AR(1) and SARIMA used by RBI 2021 (Pratap et al.), and a text-as-features model (word counts + ridge, as in Kalamara et al. and Das & Das, with the dictionary frozen on training data).

## 8. Metrics and tests

- MAE and RMSE (pp of y-o-y inflation) at C1, C2 and C3. **Diebold–Mariano with the Harvey–Leybourne–Newbold correction** for each policy vs never-update and vs always-update.
- Interval coverage and width (nominal 80% / 95%).
- Revision diagnostics:
  - number of revisions;
  - share of revisions that moved toward the outcome;
  - mean absolute revision;
  - Nordhaus-type serial correlation of revisions.
- Results are reported for the full test period, excluding COVID, and by food-shock months.

## 9. LLM-specific leakage controls

- Freeze the extraction model and its version. Record its training cutoff.
- Run a **lookahead-propensity check** (Gao, Jiang & Yan): ask the model, with no context, whether CPI inflation in month m rose or fell, and read the token probabilities. Report gate results split by high vs low recall.
- Report results **separately for months after the model's cutoff**.

## 10. Open items to verify before freezing

1. MoSPI CPI release rule: day, time (IST) and holiday shifts. Historical release dates for every month in the sample.
2. Launch month of the 2024 = 100 series and the official linking factor / back-series.
3. Start month of CPI-C (2012 = 100) and its availability for y-o-y from Jan 2012.
4. Whether provisional and final vintages can be rebuilt from archived press releases.
5. Availability and timestamps of DCA daily prices, PPAC fuel prices and IMD rainfall archives.
6. A news source with reliable historical timestamps for 2014–2025 (licence permitting).
7. **LiveMacroEval full text:** check for an explicit update rule or a policy comparison before freezing gap v6.
