# Step 1: Closest-paper comparison (15 Oct 2026)

> **Status note (16 Oct 2026):** this is a **literature record** (research kept). Statements here about "Reflica", "our gap" or "Minor 1" were written for the CPI evidence-aware revision study, which is now **Part B** of the safer-merge Minor 1 direction. The old plan documents were removed at the user's request (they remain in git history).

**Purpose:** settle what the five closest studies actually do, before claiming any contribution.
**Reading level:** each row states it. **F** = full text (or full article text); **K** = key sections of the full text; **S** = search-level only (abstract, project page, secondary summaries). Do not treat S rows as verified detail.

## Comparison table

| Question | **Mohan et al. 2025** (RBI Bulletin) | **LiveMacroEval** (Zhao et al. 2026, arXiv 2608.30110) | **Forecast-Dojo** (Ye et al. 2026, arXiv 2609.28876) | **Kalamara et al.** (BoE SWP 865, 2020; JAE 2022) | **Thorsrud** (JBES, pp. 393–409; online 2018) | **Reflica India (proposed)** |
|---|---|---|---|---|---|---|
| **Reading level** | F (article text; charts and equations missing) | **F** (full text, 16 Oct 2026; see `LEVEL2_READINGS.md` §16) | K (method, prompt appendix, results) | K | Abstract only | — |
| **Existing method: what it implements** | 216 statistical, ML and DL models combined by recent-RMSE performance weights; split-normal density | LLM agents (GPT-5, Claude Sonnet 4.5, Qwen3) with **web search** produce **hourly nowcasts** of 16 US macro indicators until each release | LLM agents revisit **Polymarket** event forecasts at successive dates using a replayed dated-news corpus; optional **belief notebook** | Newspaper text → many text metrics; best is **term counts + supervised ML** | Newspaper **LDA topics** in a time-varying factor model with a **latent threshold** on loadings | Numeric model forecasts; LLM **only extracts** dated claims; a **pre-registered gate** decides whether to revise |
| **Target and horizon** | **India** headline and core CPI as **SAAR**; 1–12 months ahead | **US** indicators incl. **CPI**; nowcast during the pre-release window (e.g., March CPI from end-March to the April release) | Binary or multiple-choice **events**; several dates before resolution | UK GDP, **CPI inflation**, unemployment | Norwegian GDP / daily business-cycle index; nowcasts | **India all-India CPI-C y-o-y, next month**; fixed checkpoints before the MoSPI release |
| **Evidence handling** | Numeric only: CPI, crude (PPAC), INR–USD, GDP / output gap, repo rate | Free web search by the agent; the hourly prompt has **no slot for the previous nowcast**. Revisions are attributed to events (EIA petroleum report, FOMC minutes) **after the fact** (App. R) | Dated articles (18.8M; URL, title and MinHash dedup). The notebook's **append-only evidence ledger** has, per claim, `date_observed`, provenance/quality note, `active/superseded` | Aggregate term-count features; rolling 36-month re-estimation | Aggregate topic series; the latent threshold switches topics on/off over time | **Per-claim records**: item, direction, size, region, date, source, source type; **scored** on novelty, reliability, relevance (CPI weight), strength |
| **Revision policy: what decides whether the forecast changes** | None. Forecasts are re-produced at each origin from data available then | **The LLM's own judgement** at each hourly run. **No explicit rule, gate or evidence scoring** (verified). Auto-ARIMA baseline is **frozen** for the window (effectively never-update) | **The LLM's judgement**, instructed to keep p "consistent with the active ledger … moved only as far as that evidence justifies". No scored or pre-registered gate | None. The model is re-estimated on a schedule | **Learned statistical threshold** on topic loadings (not on individual claims; not a revise/keep decision on an issued forecast) | **Explicit, pre-registered, auditable gate** (thresholds fixed on training years); bounded revision size; every decision logged with a reason |
| **Evaluation** | Pseudo-out-of-sample; RMSE vs random walk (~70% lower on average); **DM + Harvey–Leybourne–Newbold** and Wilcoxon tests; density bands | **Live** 6-month test (contamination-resistant). **LiveMacro Score** weights indicators by S&P-futures reaction (+1 perfect, 0 = Bloomberg consensus). Also a **LiveBetting Score**. GPT-5 ties consensus overall (+0.004, n.s.); CPI, retail sales and PCE prices = **87% of the average agent's shortfall**; on CPI the Cleveland Fed and the consensus beat all agents. Point nowcasts only, no intervals | Brier and accuracy vs **market prices** (market better; best agent 0.546 vs 0.498). Memory-on vs memory-free. Gains concentrated where more new dated evidence appears | Out-of-sample text vs no-text models; gains largest in stress periods | Out-of-sample nowcasts vs forecast combinations and expert judgement; predictive power for GDP revisions | Walk-forward point-in-time backtest + a live trial; MAE/RMSE, **DM tests**, interval coverage, revision count and direction quality; lookahead-bias check |
| **What it does not establish (remaining question)** | Whether **text** or **revision** helps; it only tests model combination | Whether a **rule-based gate** beats the agent's free updating; whether a **numeric forecaster + extracted claims** beats an LLM forecaster on CPI; **update-policy comparison** (never / always / small-step / gated): **not done** (verified); **US only** (non-US left to future work; India not mentioned) | Whether a **scored, explicit gate** beats LLM free judgement; numeric targets; **inflation**; update-policy comparison | Claim-level evidence; **revising an issued forecast**; update policies | Claim-level gating; inflation; explicit revise/keep decisions; update policies | — |

## What this changes

1. **"Revising a CPI nowcast as news arrives" already exists.** LiveMacroEval does it for **US CPI** with LLM agents, hourly, live, and links revisions to events *(search-level)*. We must **not** claim news-driven CPI revision as new.
2. **"Claim-level, dated, provenance-annotated evidence ledgers" already exist** (Forecast-Dojo).
3. **India numeric baseline is strong and already rigorous** (Mohan et al.: 216-model combination, DM tests, density). Any Reflica gain must be measured **against a Mohan-style combination**, not a weak ARIMA.
4. **Evidence that leaves room for us:**
   - LiveMacroEval agents were **weakest on inflation/CPI** *(S)*. This supports keeping a **numeric model as the forecaster** and using text only to gate revisions.
   - In the India text papers, text **sometimes hurt** (RBI 2021; Das & Das 2024). Forecast-Dojo found unfiltered memory **did not consistently help**. This supports **gating** evidence rather than always using it.

## Provisional research gap (v6)

> Existing work forecasts India CPI with strong numeric model combinations (Mohan et al. 2025). It adds newspaper text as aggregate features (Kalamara et al.; Pratap et al. 2021; Das & Das 2024), and lets LLM agents revise US CPI nowcasts or event forecasts as news arrives, using their own judgement over free-form or ledger-style evidence (LiveMacroEval; Forecast-Dojo). **We have not found a study that tests whether an explicit, pre-registered, scored revision gate over dated text claims, applied to a numeric CPI forecast, improves on never-, always- and small-step updating at equal horizons.** Reflica will test this for India's monthly CPI, with intervals and leakage controls.

**Status: provisional.** *(16 Oct 2026: the LiveMacroEval column has now been checked against the full text; see gap v7 below.)* Originally, the LiveMacroEval row was search-level. Its "unknown" cells mean **not yet checked**, not "absent". Absence from an abstract is not evidence that the paper lacks an explicit update rule or a policy comparison.

**Target mismatch with Mohan et al.:** they forecast a **seasonally adjusted annualised rate (SAAR)** at 1–12 months, while Reflica targets **y-o-y** CPI-C inflation at fixed checkpoints. **Published RMSEs are not comparable.** We will re-implement a Mohan-style combination on our own target, origins and test period (the draft CPI target protocol was removed on 16 Oct; a new Part B protocol is needed, and the draft checkpoints were really current-month nowcasts).

**What would falsify or shrink this:**
- LiveMacroEval's full text shows an explicit update rule or a policy comparison.
- A study is found that gates numeric forecast revisions on scored text claims.

**Next reading:** LiveMacroEval full text (arXiv 2608.30110 PDF). Optional: Thorsrud full text (Norges Bank WP 21/2016).

## Decision for the supervisor discussion

The contribution is now **a method-and-evaluation question, not a new capability**:
> *Does a rule-based, evidence-scored revision gate beat simpler update policies for India CPI, on top of a strong numeric baseline?*

A **negative or null result is still publishable** if the evaluation is clean, because it would show that free or always-on use of news does not help. Steps 2–4 (target definition, numeric baseline, policy test) are what answer it.

Sources (search-level for LiveMacroEval): [arXiv 2608.30110](https://arxiv.org/abs/2608.30110v1), [project site](https://livemacroeval.github.io/), [GitHub](https://github.com/Zukahi/LiveMacroEval), [Pith summary](https://pith.science/paper/2608.30110).

## Update after reading LiveMacroEval in full (16 Oct 2026): gap v7

**Result of the check.** LiveMacroEval's full text shows **no explicit update rule and no comparison of update policies**. The first falsification condition above is therefore **not met**. What the paper does establish:
- free, LLM-driven revision of a **US CPI** nowcast as news arrives;
- event-time attribution of revisions;
- LLM agents are **weakest on inflation** (CPI, PCE prices and retail sales account for 87% of the average agent's shortfall);
- a multi-agent design that predicts **smaller** surprises scores better.

> **Provisional research gap (v7).** Existing work forecasts India CPI with strong numeric model combinations (Mohan et al. 2025) and adds newspaper text as aggregate features (Kalamara et al.; Pratap et al. 2021; Das & Das 2024). LLM agents revise US CPI nowcasts (LiveMacroEval) or event forecasts (Forecast-Dojo) as news arrives, but the update is left to the model's own judgement, and neither paper compares update policies. **We have not found a study that tests whether an explicit, pre-registered, scored revision rule over dated text claims, applied to a numeric CPI forecast, improves on never-, always- and small-step updating at equal horizons, for India or elsewhere.**

**Still open:**
- This gap holds only for the papers we have read. Other nowcasting-with-text work, such as Thorsrud (full text) and Modugno 2013 (full text), may still narrow it.
- LiveMacroEval's poor CPI results come from US data. They support, but do not prove, using a numeric model as the CPI forecaster.

## Update after Thorsrud WP 20/2016 and Modugno ECB WP 1324 (16 Oct 2026): gap v8

**Source:** the user's reading of both PDFs (methods and revision sections); **reported, not checked by us**. Details: `../literature/LEVEL2_READINGS.md` §17–18.

| Possible contribution | Status after these two papers |
|---|---|
| Updating forecasts as new information arrives | **Already established** (nowcasting literature; Modugno; Thorsrud; LiveMacroEval) |
| Using newspaper-derived text to nowcast an economic indicator | **Already established** (Thorsrud: tone-adjusted topics + DFM, real-time, GDP) |
| Quantifying how unexpected releases change an inflation forecast | **Already established** (Modugno: forecast = previous forecast + news contributions; HICP/US CPI) |
| An "explicit revision rule" in general | **Not a distinction.** Model-based news decomposition is itself an explicit, deterministic update mechanism |
| Extracting dated, source-linked **claims** from news and deciding which affect CPI forecasts | **Not established by these papers** (this does not prove no one has done it) |
| Testing a **pre-specified, bounded revision policy** against alternative update policies for **Indian headline CPI y-o-y** | **Not established by these papers** (same caveat) |

> **Provisional research gap (v8, replaces v7).** Prior research has established both news-based economic nowcasting (Thorsrud) and model-based attribution of inflation forecast revisions to incoming information (Modugno; Bańbura et al.). LLM agents also revise CPI nowcasts freely as news arrives (LiveMacroEval). **The remaining question is whether a claim-level, source-linked representation of dated news, combined with a pre-specified, bounded revision policy, adds forecasting value for Indian headline CPI year-on-year inflation beyond strong numerical baselines and simpler text-based methods** (sentiment and word-frequency indices). The method is evaluated against alternative revision policies (never, always, small-step, text-always) under point-in-time controls and chronological out-of-sample testing.

**Contribution type:** a **rigorous test** of a specific representation plus policy on an Indian target. It is **not** a claim to have invented news-driven updating.

**Still required before G2 is closed:**
1. Read **Thorsrud, "Words are the New Numbers"** (JBES) in full. The uploaded PDF was the different WP 20/2016.
2. Run a focused search for claim-level news extraction for forecasting, forecast-revision policies, and bounded or partial updating (especially for inflation).
3. Directly check §17–18 against the PDFs if they become available in this session.

## Update (16 Oct 2026): LLM-CPI read (key sections)

LLM-CPI (Fan et al. 2025) combines **LLM-labelled text with a numeric CPI model** (ARX + daily VARX) and gives prediction intervals. Its target is China m-o-m CPI and its text is Weibo social media. It has **no revision mechanism and no update-policy comparison**, and its text evidence is aggregate (scores and embeddings), not source-linked claims. **Gap v8 survives.** "Using LLMs and news to predict inflation" is **not** a contribution. Only the claim-level representation plus the bounded policy, tested on Indian headline CPI y-o-y, remains.

**Still open before G2 closes:** Thorsrud "Words are the New Numbers" full text (only the abstract is available so far).

