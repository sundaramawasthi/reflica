# G2 focused search (16 October 2026)

> **Purpose:** look for studies that would narrow or falsify gap v8 (`CLOSEST_METHODS.md`): claim-level, source-linked news evidence plus a pre-specified, bounded revision policy, tested against other update policies for Indian headline CPI y-o-y.
> **Method:** five web searches. arXiv, RBI and publisher sites are blocked from this cloud, so **no full texts were opened**.
> **Reading level of every result: search-level (S).** A result's absence of a feature is **not** evidence that the paper lacks it.

## Queries

1. LLM claim extraction from news to revise numerical inflation forecasts
2. Bounded / partial-adjustment forecast-revision policies vs never/always update (inflation, news)
3. LLM + news + India CPI forecasting (2025–2026)
4. Structured event extraction from news for macro/inflation forecasting (knowledge graph, source-linked)
5. Identity check: arXiv 2506.09516

## New or newly relevant results

| # | Study | What it does (search-level) | Overlap with gap v8 | Priority |
|---|---|---|---|---|
| S1 | **Fan, Lv, Sun & Wang (2025), "LLM-Powered CPI Prediction Inference with Online Text Time Series" (LLM-CPI), arXiv 2506.09516** (USC; Xiamen) | Chinese social-media posts are labelled with ChatGPT and BERT; LDA/BERT text embeddings; a **monthly ARX CPI model** with text and macro variables plus a **daily VARX** on LLM-generated CPI surrogates; asymptotic theory; **two kinds of prediction intervals** | **High:** a numeric CPI model plus LLM-derived text, with intervals. Not India; social media, not source-linked claims; no revision policy reported at search level | **Read in full (top priority)** |
| S2 | **BIS Working Paper 1294**, decomposing macroeconomic sentiment with LLMs | LLMs extract growth and inflation sentiment from financial news; recursive AR(1) vs local projections; CPI, core CPI, PCE | Medium: LLM extraction for inflation, but sentiment-level, not claims | Read key sections |
| S3 | InflaBERT, arXiv 2410.20198 (already in our list) | BERT inflation-sentiment index added to the Cleveland Fed nowcast; marginal gain, mainly during the pandemic | Medium: text inside an inflation nowcast; index-level | Read key sections |
| S4 | PIER Thailand DP 252 (already in our list) | LLM-assisted news inflation-expectations index; up to 32% RMSE reduction over AR benchmarks; results sensitive to prompt design | Medium: index-level; non-India emerging market | Already Level 1 |
| S5 | "Econometric forecasting using ubiquitous news text: Text-enhanced factor model", *Int. J. Forecasting* (2024; ScienceDirect S0169207024001055) | Text-enhanced factor model | Medium–high: may involve news-driven updating of factor forecasts | Read abstract and method |
| S6 | Predicting market inflation expectations with news topics and sentiment, arXiv 2107.07155 | GDELT themes and tone → breakeven inflation, 8 countries | Low–medium: GDELT event layer, aggregate features | Optional |
| S7 | Tilly & Livan, "Macroeconomic forecasting with statistically validated knowledge graphs", arXiv 2104.10457 | Theme knowledge graphs from news; industrial production | Low–medium: graph of themes, not claims; not inflation | Optional |
| S8 | Das & Das (2025), "Artificial Intelligence and Inflation Forecasting: A Contemporary Perspective" (SAGE, DOI 10.1177/22779787251318831) | Same authors as P3; India context (to confirm) | Possibly India-relevant review | Read abstract |

## What the search did **not** find

- No study, at search level, combining **claim-level, source-linked news extraction** with a **tested revision policy** (never / always / small-step / bounded) for inflation.
- No LLM-based **India CPI** forecasting study.
- No inflation study that explicitly compares **bounded or partial-adjustment** revision rules. The economics literature on forecast under- and over-reaction (e.g., sticky or noisy information, forecast-revision regressions) is the right background for bounded updating, but it was not covered by these queries. **To search next.**

## Effect on G2

- **Gap v8 is not falsified** at search level.
- **S1 (LLM-CPI) is now the closest known study** and must be read in full before G2 is closed. If it includes a revision mechanism or policy comparison, G2 narrows further. The likely distinction (to verify): source-linked claims from dated news and official releases, a pre-specified bounded policy, and India.
- Status: **G2 remains provisional.**

## Sources

- [PIER DP 252](https://www.pier.or.th/en/dp/252/) · [InflaBERT arXiv 2410.20198](https://arxiv.org/abs/2410.20198) · [St. Louis Fed: AI and inflation forecasts](https://www.stlouisfed.org/publications/review/2024/nov/artificial-intelligence-and-inflation-forecasts)
- [LLM-CPI arXiv 2506.09516](https://arxiv.org/pdf/2506.09516) · [Pith summary](https://pith.science/paper/2506.09516) · [UCI talk abstract](https://ics.uci.edu/event/llm-powered-prediction-inference-with-online-text-time-series/)
- [BIS WP 1294](https://www.bis.org/publ/work1294.pdf) · [Text-enhanced factor model (IJF)](https://www.sciencedirect.com/science/article/abs/pii/S0169207024001055) · [arXiv 2107.07155](https://arxiv.org/pdf/2107.07155) · [arXiv 2104.10457](https://arxiv.org/pdf/2104.10457)
- [Das & Das 2025 (SAGE)](https://journals.sagepub.com/doi/10.1177/22779787251318831) · [Bank of England SWP 1190](https://www.bankofengland.co.uk/-/media/boe/files/working-paper/2026/inflation-attitudes-of-large-language-models.pdf) · [LiveMacroEval arXiv 2608.30110](https://arxiv.org/pdf/2608.30110)

## Addendum: forecast-revision literature (Step 1, item 3; search-level)

| # | Study | Relevance to a bounded revision policy |
|---|---|---|
| R1 | Coibion & Gorodnichenko (2015): test whether forecast errors are predictable from forecast revisions | Gives an **evaluation tool**: regress our forecast errors on our revisions to detect under- or over-reaction. Original paper **not yet read** |
| R2 | Bordalo, Gennaioli, Ma & Shleifer (2020), "Overreaction in Macroeconomic Expectations", *AER* 110(9): 2748–82 (NBER w24932) | Individual forecasters **overreact** to news, while consensus forecasts **underreact**. This motivates bounding revisions (against overreaction) without freezing them (against underreaction) |
| R3 | Shrinkage-as-optimal-update and partial updating between periods (academia.edu "Beyond Optimal Forecasting"; Economics Discussion Paper 2009-22; Kansas City Fed RWP 04-10) | Theoretical precedent: under noise, partial (shrunk) updates can minimise MSE. **Bounded updating is therefore not new as a principle.** Our contribution is testing it on claim-level text evidence for India CPI |

**Not found:** a study applying a pre-specified bounded or partial-adjustment rule to **text-derived claim evidence** for inflation.

**Implications:**
- The research question should cite R2 and R3 as the theoretical basis for bounded updates.
- R1's error-on-revision regression should be added as a diagnostic in Part B.

Sources: [NBER w24932](https://www.nber.org/papers/24932) · [AER (IDEAS)](https://ideas.repec.org/a/aea/aecrev/v110y2020i9p2748-82.html) · [Beyond Optimal Forecasting](https://www.academia.edu/22488069/Beyond_Optimal_Forecasting) · [EDP 2009-22](https://www.deutsche-digitale-bibliothek.de/item/2664KZTPZCGF3FBLNZT7LY3ECGXK4YDX) · [KC Fed RWP 04-10](https://www.kansascityfed.org/documents/5375/pdf-RWP04-10.pdf)
