# Presentation Content: IndiaEconForecast / Reflica India

> Prepared 17 Oct 2026 from the project records: `RESEARCH_PROPOSAL.md`, `research/forecast/*`, `docs/research_archive/*` and `data/README.md`.
> **No results exist yet.** Anything not yet built or decided is marked **[TBD]** and should be left out of the slides.

---

# Part 1: First Presentation (14 slides)

### Slide 1. Title
- **IndiaEconForecast / Reflica India: Hybrid AI Forecasting of Indian Economic and Policy Outcomes**
- Sundram Awasthi · M.Tech CSE (2026–28) · GLA University, Mathura
- Guide: **[add name]**

### Slide 2. Introduction & Motivation
- Inflation (CPI), RBI policy and government price measures affect every Indian household and business.
- AI tools now "predict" the economy, but **few are tested fairly on Indian data**, and few show **why** a forecast changed.
- News and official statements (RBI, PIB) arrive between CPI releases. **Can that evidence improve forecasts honestly?**
- Evidence so far is mixed: in Indian studies, text sometimes helped and sometimes hurt (Pratap 2021; Das & Das 2024). In a live US test, LLM agents were **weakest on inflation** (LiveMacroEval 2026).

### Slide 3. Problem Statement
> Can claim-level, source-linked evidence from dated official documents, combined with a pre-specified **bounded forecast-revision rule**, improve **India's headline CPI (y-o-y)** forecasts beyond strong numerical models and simple text methods, using only information available at each forecast date?

There is also a companion question (Part A): how accurate and calibrated are LLMs on Indian economic and policy yes/no events?

### Slide 4. Objectives & Scope
**Objectives**
1. Build a point-in-time dataset: CPI first releases with dates, and dated RBI, PIB and Ministry of Finance documents.
2. Build numerical CPI baselines (naive, SARIMA, XGBoost).
3. Extract dated, source-linked **claims** from official documents.
4. Design and test a **bounded revision rule**, compared with never, always and text-always updating.
5. Evaluate fairly (walk-forward), and benchmark LLMs on Indian yes/no questions (Part A).

**In scope:** India headline CPI-C y-o-y; official sources (MoSPI, RBI, PIB, MoF); 2013–2026.
**Out of scope:** an agent that answers questions, abstention (Minor 2), impact chains, trading or policy advice.

### Slide 5. Literature Review & Limitations of Existing Systems
| Work | What it does | Limitation for our problem |
|---|---|---|
| Mohan et al. 2025 (RBI) | 216-model CPI combination, ~70% below a random walk | Numbers only; no text or revision; SAAR target |
| Pratap et al. 2021 (RBI) | News sentiment for food inflation | Mixed results; aggregate index; no significance tests |
| Das & Das 2024 | Newspaper headline words + ML | Text hurt 2 of 3 models; look-ahead risk |
| Fan et al. 2025 (LLM-CPI) | LLM text + CPI model, with intervals | China; social media; no revision policy |
| LiveMacroEval 2026 | Live LLM nowcasts of US indicators | No update rule; weakest on CPI; US only |
| Modugno 2013 / Thorsrud 2016 | News-driven nowcast updating | Numeric or topic level; no claim-level rule |

**Gap (provisional, not a novelty claim):** among the works reviewed, none tests **claim-level evidence + a fixed bounded revision rule** on **Indian headline CPI** against other update policies.

### Slide 6. Proposed System & Features ⭐
1. Numerical forecasting engine (core)
2. Multi-source timestamped data (core)
3. Evidence store / claim extraction (core)
4. Forecast uncertainty: basic intervals (core, simplified)
5. Smart forecast revision: minimal bounded rule (after the baselines)
6. What-if scenarios (optional)
7. Experimental evaluation (core)
8. Minimal research dashboard (core, minimal)

Plus Part A: an LLM forecasting benchmark of Indian yes/no events.

### Slide 7. Architecture / Pipeline
```
MoSPI CPI · RBI · PIB · MoF ─► timestamped data store (publication time kept)
         │                              │
         ▼                              ▼
 numerical models               claim extraction (quote, source, date, direction)
 (naive/SARIMA/XGBoost)                 │
         └──────────► bounded revision rule ◄──┘
                          │  keep / revise + reason
                          ▼
           forecast log ─► walk-forward evaluation ─► dashboard
```

### Slide 8. Methodology
1. Collect official data with publication dates (done for CPI and RBI).
2. Build the CPI series (revised values for training, first releases for testing).
3. Build the baselines, plus text baselines (sentiment index, word counts).
4. Extract claims from dated documents.
5. Apply the bounded revision rule, with thresholds tuned on validation data only.
6. Run a walk-forward test that uses only information available before each forecast.
7. Compare policies: never, always, small-step, text-always, and our bounded rule.

### Slide 9. Model Comparison & Proposed Model
| Model (from the literature) | Strength | Weakness |
|---|---|---|
| Random walk / naive | Simple, hard to beat short term | No information use |
| SARIMA | Strong for Indian CPI (Pratap & Sengupta: best) | Numbers only |
| XGBoost / ML | Non-linear | Overfits on short samples |
| Model combinations (Mohan) | Best accuracy | Complex; no text |
| LLM as forecaster | Uses news directly | Weak on CPI (LiveMacroEval); memorisation risk |

**Proposed:** a **numerical model as the forecaster**, with the LLM used **only to extract claims**, and a **bounded revision rule** deciding whether to adjust. Why: LLMs are weak at forecasting CPI, while bounded updates limit overreaction (Bordalo et al. 2020).

### Slide 10. Technology Stack
- **Research engine:** Python (pandas, statsmodels, scikit-learn, XGBoost), LLM API for claim extraction
- **Data:** CSV / JSON with provenance; MoSPI e-Sankhyiki API
- **App / dashboard:** Flutter (web, Android)
- **Backend:** Firebase Auth + Cloud Firestore (free Spark plan)
- **Version control:** Git / GitHub

### Slide 11. Evaluation Metrics & Expected Outcomes
- **Part B (CPI):** MAE, RMSE, Diebold–Mariano test, interval coverage, and revision counts (helpful vs harmful).
- **Part A (LLM benchmark):** Brier score, calibration.
- **Expected outcomes:** a public point-in-time India CPI evidence dataset, a fair comparison of revision policies, and an honest result, **including the possibility that the method does not help**.

### Slide 12. Timeline
| Period | Work |
|---|---|
| Oct 2026 | Literature, gap, proposal ✅ · data collection 🟡 |
| Nov 2026 | Claim extraction; freeze protocol; supervisor approval |
| Dec 2026 – Jan 2027 | Baselines; data pipeline; Part A pilot |
| Feb – Mar 2027 | Text evidence + bounded revision experiments |
| Apr 2027 | Evaluation, robustness |
| May 2027 | Dashboard, report, final presentation |

### Slide 13. References (key)
1. Mohan et al. (2025), *RBI Bulletin*
2. Pratap, Ranjan, Kishore & Bhoi (2021), *RBI Occasional Papers* 42(2)
3. Das & Das (2024), *IJEF* 16(6)
4. Fan, Lv, Sun & Wang (2025), arXiv 2506.09516
5. Zhao et al. (2026), LiveMacroEval, arXiv 2608.30110
6. Ye et al. (2026), Forecast-Dojo, arXiv 2609.28876
7. Modugno (2013), *IJF* 29(4)
8. Bordalo, Gennaioli, Ma & Shleifer (2020), *AER* 110(9)
9. Gao, Jiang & Yan (2025), arXiv 2512.23847

Full list: `RESEARCH_PROPOSAL.md` §6.

### Slide 14. Thank You / Q&A

---

# Part 2: Final Presentation (outline; fill in after the experiments)

| # | Slide | What we can already say | Status |
|---|---|---|---|
| 1 | Title | As above | ✅ |
| 2 | Introduction & Problem | Recap of slides 2–3 | ✅ |
| 3 | Objectives & Scope | Mark each objective ✔ or ✘ | [TBD after results] |
| 4 | Literature & Gap (1 slide) | Gap v8 summary | ✅ |
| 5 | Proposed System & Features | What was actually built | [TBD] |
| 6 | Final Architecture | Update the diagram if it changes | [TBD] |
| 7 | Methodology | Steps actually followed | [TBD] |
| 8 | Dataset | CPI 2013–2026 (613 rows); 32 first releases; 64 dated official documents (22 MPC resolutions, 8 MPRs, Economic Survey, PIB releases) | ✅ partly; claims count TBD |
| 9 | Model Comparison & Selected Model | Our own experiment results | [TBD] |
| 10 | Model Training Pipeline | Walk-forward setup, parameters | [TBD] |
| 11 | Technology Stack | Final tools | [TBD] |
| 12 | Implementation / Modules | Data, extraction, models, revision, dashboard | [TBD] |
| 13 | Screenshots / Demo ⭐ | Dashboard | [TBD] |
| 14 | Results & Evaluation | MAE / RMSE / DM; Brier (Part A). Not accuracy/F1, since the CPI task is regression | [TBD] |
| 15 | Testing | Leakage tests, unit tests | [TBD] |
| 16 | Challenges | Already known: CPI base change (2012 → 2024), first releases vs revisions, release-date shifts (13 Apr, 13 Jul, 14 Sep), cloud access blocks, thin news archives | ✅ partly |
| 17 | Limitations & Future Scope | Minor 2: calibrated policy probabilities + abstention | ✅ partly |
| 18 | Conclusion | [TBD] | [TBD] |
| 19 | References | As above, plus any new ones | ✅ |
| 20 | Thank You / Q&A | — | ✅ |

**Note:** the CPI task is **regression**, so accuracy, precision, recall, F1 and the confusion matrix **don't apply** to Part B. Use MAE, RMSE and the DM test. A confusion matrix or calibration plot fits only Part A (yes/no).
