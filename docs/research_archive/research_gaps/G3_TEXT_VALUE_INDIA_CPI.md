# G3: Does adding news to numerical models improve Indian CPI forecasting? (Step 2)

> **Date:** 16 October 2026. **Status:** analysis of papers already read; **no new reading**.
> **Sources:** `../../../research/forecast/LITERATURE_RECORDS.md` (P1–P3) and `../literature/LEVEL2_READINGS.md` (§1, §3, §4, §8, §12, §15).
> **Question:** what do the Indian inflation studies we have read *actually* show about text adding value beyond numbers?

## 1. The three core studies side by side

| | **P1 Mohan et al. 2025** (numeric baseline) | **P2 Pratap et al. 2021** (news sentiment) | **P3 Das & Das 2024** (headline words) |
|---|---|---|---|
| Uses text? | ❌ No | ✅ Lexicon sentiment index (9 dailies) | ✅ 166-word monthly frequencies (Times of India) |
| Target | Headline and core CPI, **SAAR** | CPI-Vegetables, CPI-Food & beverages (m-o-m, y-o-y) | CPI (series and transformation **not stated**) |
| Period / test | Jan 2012 – Jul 2024; pseudo-OOS, h = 1–12 | Test Sep 2019 – Aug 2021 (24 months), rolling, h = 1–12 | Single 70/30 split (~40 test months) |
| Comparison | 216 models vs RW / simple average | Same models ± news index vs AR(1) | Same ML models ± text |
| Significance tests | ✅ DM + HLN, Wilcoxon | ❌ | ❌ |
| Point-in-time / vintages | ❌ (pseudo-OOS, revised data) | ❌ (no release-date alignment) | ❌ (dictionary built on a window that includes the test period) |
| **What text did** | — (not tested) | **Mixed:** small gain in some cases (veg m-o-m h=1: 0.93 vs 0.95), slightly **worse** in others (veg y-o-y h=1: 0.79 vs 0.77); MIDAS worse than AR(1) at several horizons | **Mixed:** best model (ANN) ~6% better with text (1.560 vs 1.654), but text **worsened** RF (1.654 → 1.900) and Elastic Net |
| Authors' own conclusion | Combinations beat single models | News sentiment improves food-inflation forecasting | Text models "consistently" better, **which contradicts their own table** |

## 2. Supporting context (not text studies for India CPI)

| Study | What it adds | Read |
|---|---|---|
| Singh & Bhoi 2022 (RBI) | Numeric only: quarterly CPI-C; ANN best (1Q RMSE 0.58) vs SARIMA 0.79 and RW 0.92; 12 test quarters, no significance tests | F |
| Pratap & Sengupta 2019 (RBI WP) | Numeric only: SARIMA best for headline CPI (RMSE 0.24); **test set used for model selection** | F |
| Banerjee, Kanodia & Ray 2021 | Text-based **inflation expectations** index tracks inflation (tracking, not forecasting) | **A only** |
| Kalamara et al. (UK, BoE) | Outside India: term counts + ML improve CPI-inflation forecasts, most in stress periods | K |
| Wang et al. 2024 (NeurIPS) | Outside India and CPI: unfiltered news **hurt** forecasts; filtered news helped | F |
| LiveMacroEval 2026 (US) | LLM agents using web news were **weakest on CPI** against the consensus | F |

## 3. Findings

1. **Evidence that text helps Indian CPI forecasts is weak and mixed.** The two Indian text studies (P2, P3) each show gains for some models or horizons and losses for others.
2. **Neither Indian text study is a fair test by current standards:**
   - no significance tests;
   - no point-in-time or vintage controls;
   - short or single-split test windows;
   - in P3, a likely look-ahead from building the dictionary on the full sample.
3. **The targets are not comparable.** P1 forecasts SAAR, P2 forecasts food and vegetable CPI, and P3's series is unclear. No study we read tests text on **headline y-o-y CPI** against a **strong numeric baseline** such as P1.
4. **Text is represented only as aggregate indices** (a sentiment index or word frequencies), never as dated, source-linked claims.
5. **Outside India, the evidence is also conditional:**
   - text helps most in stress periods (Kalamara);
   - unfiltered news can hurt (Wang et al.);
   - LLM agents struggle on CPI (LiveMacroEval).

## 4. Conclusion for G3

> **G3 is confirmed as an open empirical question, not as a novelty claim.** Among the studies we have read, no study tests, with point-in-time controls and significance tests, whether dated text evidence improves **headline y-o-y Indian CPI** forecasts beyond a **strong numeric baseline**. Prior Indian evidence is mixed and methodologically limited.

**Caveats:**
- This covers only the papers we have read.
- Banerjee et al. 2021 and John, Singh & Kapur 2020 are not yet read in full.
- A positive, null or negative result in our experiment would each be informative.

## 5. Implications for the Part B methodology (to be finalised in Step 4)

1. **Target:** headline all-India CPI-C y-o-y, with the horizon fixed in advance.
2. **Baselines:** naive, SARIMA, XGBoost, a simple combination, and a reduced Mohan-style suite on our own target.
3. **Text baselines to beat**, before any claim-level method:
   - a lexicon sentiment index (P2-style);
   - a word-frequency index (P3-style), rebuilt on **pre-test data only**.
4. **Point-in-time:** lag every text and numeric input to what was published before the forecast origin.
5. **Tests:** Diebold–Mariano with the HLN correction; report effect sizes and confidence intervals, not only RMSE.
6. **Report all model results**, including the models where text hurts, so that no single favourable model is selected.
