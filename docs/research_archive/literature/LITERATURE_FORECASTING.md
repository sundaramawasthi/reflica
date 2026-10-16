# Literature analysis: LLM / agent-based event forecasting (2026-10-13)

> **Archive note:** literature record (13 Oct 2026, abstract level) moved here from `research/forecast/`. **Status note (16 Oct 2026):** this is a **literature record** (research kept). Statements here about "Reflica", "our gap" or "Minor 1" were written for the CPI evidence-aware revision study, which is now **Part B** of the safer-merge Minor 1 direction. The old plan documents were removed at the user's request (they remain in git history).

Based on titles and abstracts only, as pasted by the user. Read the full papers before citing.
"Year not given" means the year was not in what the user pasted.

---

## Paper 1. Application of Large Language Models in the Problem of Event Forecasting
- **Year / venue:** Dec 2025, Automatic Control and Computer Sciences (Dakhnovich, Bogina, Makeeva)
- **Domain:** Geopolitics (conflict outcome)
- **Sub-domain:** LLM-agent event forecasting with RAG
- **Tech / AI used:** LLMs Mistral and DeepSeek; RAG over agency reports, opinion leaders and news; LLM agents (reviewed: ChatDev, MetaGPT, MAD, ChatEval, WebAgent, WebVoyager, Generative Agents, EconAgent)
- **Problem:** Classical forecasting (regression, time series) can't use opinions, news and analysis; sources are polarised.
- **Solution:** Reviews agent types (cooperative ChatDev/MetaGPT; debate MAD/ChatEval; web agents; simulation agents Generative Agents/EconAgent). Experiment: Mistral + DeepSeek with RAG over analytical agencies, opinion leaders and news, to predict one conflict's outcome. Finding: forecasts from opposite-side sources converge. Proposes requirements: weight sources by expert value, filter neutral data, balance samples.
- **Research gap:** One conflict only, so no statistics; no scoring against what really happened; no calibrated %; source weighting proposed but not built; no "unknown"; no impact chain; no benchmark.
- **Relevance:** Very high (geopolitics + agents + RAG).

## Paper 2. MENTOR: multi-agent framework for event and narrative trend prediction
- **Year / venue:** Oct 2025, Frontiers of Information Technology & Electronic Engineering
- **Domain:** Finance (narrative economics, investing)
- **Sub-domain:** Multi-agent LLM event and narrative trend prediction
- **Tech / AI used:** Multi-agent LLM framework; teacher-student iterative reasoning; task decomposition into 3 subtasks; portfolio backtesting (LLM names not in abstract)
- **Problem:** Markets move on stories (narratives); current LLM methods don't break the task into steps and don't fit financial use.
- **Solution:** Multi-agent teacher-student iterative reasoning in 3 steps: (1) detect and rank trending events, (2) forecast future events from narratives, (3) predict industry index performance. Data: self-built Chinese KOL articles + English financial news. Beats StkFEP and SEP; portfolio backtest improves.
- **Research gap:** China/English finance only; self-built data (leakage risk: the LLM may already know outcomes; hard to reproduce); no calibrated probabilities; no "unknown"; event → industry is one step, not a full impact chain; no live forward test.
- **Relevance:** High ("event → which sectors are affected" is close to impact chains).

## Paper 3. An LLM-based event-driven forecasting framework for intelligent financial services
- **Year / venue:** Sep 2026, Service Oriented Computing and Applications
- **Domain:** Finance (Chinese stocks, CSI 300)
- **Sub-domain:** Event-driven forecasting: text → structured events + numbers
- **Tech / AI used:** LLM schema-guided event extraction; template-based event encoding; multi-scale convolutional sparse attention; adaptive gated fusion; metrics ACC, MCC
- **Problem:** Hard to turn messy text into useful structured inputs; past work ignores event scope (local vs global), event interactions, and fuses text and numbers shallowly.
- **Solution:** Schema-guided LLM extraction (fixed event types + arguments) → local/global events → template text; multi-scale convolutional sparse attention for event links; adaptive gated fusion with market data. ACC 56.06%, MCC 0.1238 (2022–2024).
- **Research gap:** Weak absolute result (MCC 0.12 is only slightly better than chance); fixed schema misses new event types; China only; up/down only, no probabilities; no big rare events; no explanation of impact; no live test.
- **Relevance:** Medium-high (the extraction pipeline technique is reusable).

## Paper 4. LLM-enhanced multi-causal event causality mining in financial texts
- **Year / venue:** Nov 2025, Journal of King Saud University – Computer and Information Sciences
- **Domain:** Finance (news)
- **Sub-domain:** Event causality extraction (NLP), not forecasting
- **Tech / AI used:** Fine-tuned LLaMA encoder; structured event extraction; event-centric graph reasoning with multi-hop propagation; metric F1
- **Problem:** Current methods find single, surface-level cause → effect pairs; real news has many causes, many effects, and indirect chains across sentences.
- **Solution:** Fine-tuned LLaMA encoder + structured events (actor, action, object, time, place) + event graph with multi-hop reasoning for indirect causes. +5–10% F1 over 10 baselines on 3 public benchmarks.
- **Research gap:** Finds causes in the past, doesn't predict the future; no probability on links; offline text, not live; doesn't test whether the chains improve forecasts.
- **Relevance:** High for the impact-chain part (use these chains forward).

## Paper 5. Hierarchical semantic extraction and heterogeneous GNN for event-driven time series forecasting
- **Year / venue:** Jun 2026, Scientific Reports
- **Domain:** Energy / commodities (crude oil price)
- **Sub-domain:** Event-driven time-series forecasting with LLM extraction + heterogeneous graph + Temporal Fusion Transformer
- **Tech / AI used:** LLM hierarchical semantic extraction; heterogeneous information graph; Relational GCN with relation-aware attention; Temporal Fusion Transformer; environment-state detection
- **Problem:** Deep-learning models assume the past repeats, so they fail on shocks; text methods squash a document into one vector and lose stance, event type and causal links.
- **Solution:** (1) LLM extracts 4 layers: entity stance, event type, causal chains between events, sentiment; (2) heterogeneous graph + relational GCN models cumulative, spreading and combined effects; (3) detects the current "environment state" and re-weights features. +17.7% accuracy overall, +34.7% in event-heavy periods.
- **Research gap:** One case (oil); likely point forecasts, no uncertainty; "works in other domains" claimed, not shown; LLM extraction errors not measured; heavy and costly pipeline; no "unknown".
- **Relevance:** Very high (closest design: events + causal chains + graph).

## Paper 6. A large language model framework for predicting significant equity index fluctuations
- **Year / venue:** Aug 2026, Innovations in Systems and Software Engineering (Nag, Choudhury)
- **Domain:** Finance, India (NIFTY50, NIFTYBANK, NIFTYIT, 2007–2025)
- **Sub-domain:** Rare / big-event detection + next-day direction
- **Tech / AI used:** LLM-based framework (exact LLM role not in abstract); classification; fixed split vs rolling-window validation; Precision, Recall, F1, Accuracy; backtests (Total Return, Sharpe)
- **Problem:** Big one-day moves are rare, depend on market regime, and are swamped by normal days; results are easily over-stated.
- **Solution:** Predicts direction and big moves together; fixed split vs rolling window; precision/recall/F1 + backtests (return, Sharpe). Finding: direction is stable, big-move detection is fragile; accuracy stays high while F1 collapses.
- **Research gap:** Big-event prediction still unsolved; the abstract doesn't say how the LLM is used (check the full paper); no calibrated %; no reasons; markets only, not the wider economy.
- **Relevance:** Very high (Indian data, big events, evaluation lessons).

## Paper 7. LLM-driven framework for adaptive stock forecasting under China's policy-driven market (DPAD-Net)
- **Year / venue:** Jul 2026, Discover Artificial Intelligence
- **Domain:** Finance (China A-shares, policy-driven)
- **Sub-domain:** Regime-adaptive forecasting; LLM as "macro-regime strategist"
- **Tech / AI used:** LLM producing "dynamic priors"; DPAD-Net + RAND-Net (regime-adaptive non-linear decomposition neural network); MSE, Sharpe
- **Problem:** Policy news causes sudden regime shifts; LLM text is used as fixed features, so the model doesn't change its logic.
- **Solution:** LLM reads live multi-source information → "dynamic priors" (judgement of market state) → network changes its structure and splits price into a stable value part + a sentiment part. −13.6% MSE, +27.6% Sharpe; robust in policy rallies and crashes.
- **Research gap:** China only; no check of whether the LLM's market judgement is right or how sure it is; possible leakage; point forecasts; no event-level explanation; no "unknown".
- **Relevance:** Medium-high (India is also policy-driven: RBI, budget, elections).

## Paper 8. Large Language Model Augmented Forecasting for Sentiment Time Series
- **Year / venue:** 2027 conference volume, Intelligent Systems and Applications (Mitic)
- **Domain:** Sentiment time series
- **Sub-domain:** LLM agent + tools pipeline for forecasting
- **Tech / AI used:** LLM AI agents with tool use via local API (tools do the number forecasting); extra LLM API queries review forecasts against current context; autocorrelation and volatility checks
- **Problem:** Can LLMs forecast sentiment series? LLMs are weak at heavy number work.
- **Solution:** Agents send number work to tools through a local API; the LLM then reviews the forecast against current context. Keeps 83% of autocorrelation and 93% of volatility patterns; 3 examples.
- **Research gap:** Checks only that the forecast "looks like" past data, not accuracy against the real future; few examples; no probabilities; no events.
- **Relevance:** Medium (useful design pattern).

## Paper 9. LLM-based Agents for Forecasting and Prediction: Methods, Training, Evaluation, and Applications
- **Year / venue:** 2026, arXiv 2608.23058 (survey; abstract not pasted, based on search summary)
- **Domain:** General (energy, operations, etc.)
- **Sub-domain:** Survey of LLM forecasting agents
- **Tech / AI used:** (survey) LLM agents with retrieval and tools; hybrid LLM + statistical / time-series foundation models; training incl. reinforcement learning on outcomes
- **Problem:** Field is new and scattered.
- **Solution:** Groups systems into 3 types: LLM directly on time series/events; tool + retrieval agents; hybrids with statistical/foundation models. Covers training, evaluation, negative results (sometimes removing the LLM doesn't hurt).
- **Research gap (named by authors):** Need calibrated, leakage-proof live evaluation; report cost vs accuracy.
- **Relevance:** Very high (read first as the field map).

## Paper 10. ForecastBench: A Dynamic Benchmark of AI Forecasting Capabilities
- **Year / venue:** 2024 (ICLR 2025), updated through 2026; Forecasting Research Institute
- **Domain:** General world events
- **Sub-domain:** Forecasting evaluation / benchmarks
- **Tech / AI used:** Auto-generated question pipeline; LLMs vs superforecasters vs public; Brier score; significance test; public leaderboard
- **Problem:** No standard way to test ML forecasters; leakage.
- **Solution:** 1,000 auto-generated questions about unresolved future events, regularly updated; experts, public and LLMs compared; experts beat the best LLM (p < 0.001); public leaderboard.
- **Research gap:** Questions mostly about the US/West (check); yes/no questions only; no impact; no abstain option.
- **Relevance:** Very high (template for an India benchmark).

## Paper 11. Integrating ML-Based Disaster Forecasting with Multi-Agent RL for Disaster-Resilient UWSN
- **Year:** not given
- **Domain:** Networking (underwater sensor networks), disasters
- **Sub-domain:** Forecast-informed routing (ML + multi-agent RL)
- **Tech / AI used:** Random Forest (6-step window); multi-agent reinforcement learning (tabular Q-learning); synthetic data
- **Problem:** Keep data flowing during underwater earthquakes and tsunamis.
- **Solution:** Synthetic data (100 nodes, 2,000 steps); Random Forest predicts disaster risk per node; tabular multi-agent Q-learning routes around risky nodes; fewer lost packets.
- **Research gap:** Synthetic only; simple models; not real-world event forecasting.
- **Relevance:** Low (only the "forecast → action" idea).

## Paper 12. An Integrated ML and Agent-Based Modelling Pipeline for Socio-Environmental Forecasting
- **Year:** not given
- **Domain:** Climate and society (climate-driven migration, 20 countries, 2009–2023)
- **Sub-domain:** ML forecasting + agent-based simulation + SHAP
- **Tech / AI used:** Random Forest, XGBoost, CatBoost, LightGBM; agent-based simulation (not LLM); SHAP
- **Problem:** Feedback loops and human behaviour break normal forecasting.
- **Solution:** RF/XGBoost/CatBoost/LightGBM (LightGBM explains ~61% of variance) + simulation of people's behaviour and policy feedback; SHAP: extreme heat and institutional capacity are top drivers.
- **Research gap:** Yearly coarse data; 61% explained; no text/LLM; scenarios not checked against reality.
- **Note:** "Agent" here means simulated people, not LLM agents.
- **Relevance:** Medium (scenario / what-if idea).

## Paper 14. Adaptive Time-Series Forecasting through Reinforcement Learning Enhanced Attention
- **Year:** not given
- **Domain:** General time series (4 benchmark datasets)
- **Sub-domain:** Deep-learning architecture (RL adjusts attention)
- **Tech / AI used:** BiLSTM and Transformer attention; reinforcement learning agent tuning attention weights; McNemar's test
- **Problem:** Drift, noise and changing patterns; attention is static.
- **Solution:** RL agent tunes attention weights using accuracy as reward; McNemar's test confirms significance.
- **Research gap:** Numbers only, no events/text; benchmark data only.
- **Note:** "Agent" here means an RL agent, not an LLM agent.
- **Relevance:** Low-medium.

## Paper 15. Event-Driven Financial Market Analyses Using a Multi-Agent Framework (FinPulse)
- **Year:** not given
- **Domain:** Finance (macro events → asset returns and volatility)
- **Sub-domain:** Multi-agent, explainable, event-driven forecasting with what-if simulation
- **Tech / AI used:** ML models for returns and volatility; multi-agent framework for causal interpretation, counterfactual (what-if) simulation and narrative generation
- **Problem:** Need financial predictions that are event-driven and explainable.
- **Solution:** Historical macro events aligned with market reactions; ML predicts returns and volatility over several horizons; agents give causal explanations, simulate counterfactuals ("what if"), write plain-language narratives.
- **Research gap:** No numbers reported in the abstract; "causal" explanations come from the model (may be correlation); future work = real-time, more event types, UI; no calibration or "unknown"; no India.
- **Relevance:** High (closest to the product vision: impact + explanation + what-if).

---

# Added 2026-10-13: IEEE Q1 journal papers (+1 top conference)

Finding: IEEE Q1 journals have very few LLM event-forecasting papers yet. Most LLM forecasting in IEEE Q1 journals is energy (load) forecasting; event forecasting with LLMs mostly appears in conferences (NeurIPS, ACL) and arXiv.

## Paper 16. Deep Multi-Task Learning for Spatio-Temporal Incomplete Qualitative Event Forecasting
- **Year / venue:** Dec 2024, IEEE Transactions on Knowledge and Data Engineering (TKDE) 36(12), DOI 10.1109/TKDE.2024.3460539 (Chowdhury, Gao, Liang Zhao)
- **Domain:** Society / civil events (Liang Zhao's group works on protests and unrest)
- **Sub-domain:** Spatio-temporal event forecasting (deep learning, non-LLM)
- **Tech / AI used:** Deep multi-task learning across locations and time (details not verified; abstract not retrieved)
- **Problem (from title):** Forecast what kind of event will happen, where and when, when past labels are incomplete.
- **Research gap:** No LLM; no news reasoning; calibration and abstention unknown; India not mentioned. Read the abstract.
- **Relevance:** High (direct event forecasting in a Q1 IEEE journal).

## Paper 17. CausalFormer: An Interpretable Transformer for Temporal Causal Discovery
- **Year / venue:** Jan 2025, IEEE TKDE 37(1)
- **Domain:** General time series
- **Sub-domain:** Temporal causal discovery (what causes what over time)
- **Tech / AI used:** Transformer trained on time series, then interpreted to extract a causal graph
- **Problem:** Deep models find patterns but not causes; causal discovery methods are often not interpretable.
- **Research gap:** Numbers only (no news/events); finds causes but does not forecast events or impacts.
- **Relevance:** Medium-high (tool for building impact chains from data).

## Paper 18. ST-LLM+: Graph Enhanced Spatio-Temporal Large Language Models for Traffic Prediction
- **Year / venue:** 2025, IEEE TKDE (per curated list)
- **Domain:** Infrastructure (road traffic)
- **Sub-domain:** LLM for spatio-temporal forecasting
- **Tech / AI used:** Pre-trained LLM with location/time tokens; graph-enhanced attention using the road network; parameter-efficient fine-tuning
- **Problem:** Traffic models need lots of data and miss road-network structure.
- **Research gap:** Sensor numbers only, no events/news; point forecasts; no abstention.
- **Relevance:** Medium (infrastructure + LLM + graph).

## Paper 19. Empower Pre-trained Large Language Models for Building-level Load Forecasting (BlackInter)
- **Year / venue:** Sep 2025, IEEE Transactions on Power Systems 40(5) (Zhou, Wang)
- **Domain:** Infrastructure (electricity)
- **Sub-domain:** LLM-based load forecasting with little or no history
- **Tech / AI used:** Pre-trained LLM with a black-box tuning inductive adapter; uses nearby buildings' spatial correlation; no fine-tuning
- **Problem:** New buildings have little or no past data, so normal ML fails.
- **Solution / result:** Error only 42.88% and 69.44% of the best alternatives (limited / no history).
- **Research gap:** Electricity numbers only; no events (heatwaves, outages); no uncertainty; no India.
- **Relevance:** Medium (shows LLMs help when data is scarce, which applies to India).

## Paper 20. Mid-Term Load Forecasting With Minimal Data: An In-Context-Learning-Aware Approach Using LLMs (Load-Context)
- **Year / venue:** Jul 2026, IEEE Transactions on Power Systems 41(4), DOI 10.1109/TPWRS.2026.3654059 (Zhou, Zhang, Wang)
- **Domain:** Infrastructure (electricity, weeks–months ahead)
- **Sub-domain:** Few-shot / zero-shot LLM forecasting
- **Tech / AI used:** Frozen pre-trained LLM + small trainable adapter; prompts carrying spatial correlation and periodic patterns; in-context learning
- **Problem:** Mid-term forecasting needs long history that is often missing; transfer learning needs lots of source data and fine-tuning.
- **Research gap:** No events or news; no uncertainty; results only in abstract terms.
- **Relevance:** Medium.

## Paper 21. A Survey of Large Language Models on Generative Graph Analytics
- **Year / venue:** Dec 2025, IEEE TKDE 37(12)
- **Domain:** Graphs (general)
- **Sub-domain:** LLM + graph survey
- **Tech / AI used:** (survey) LLMs and GNNs for graph tasks
- **Problem:** Map how LLMs are used on graphs.
- **Research gap (named):** Predicting how graphs evolve over time (dynamic graphs) is under-explored; suggests combining LLMs with GNNs.
- **Relevance:** Medium (supports an evolving cause-effect graph).

## Paper 22. From News to Forecast: Integrating Event Analysis in LLM-Based Time Series Forecasting with Reflection
- **Year / venue:** NeurIPS 2024 (top A* conference, not IEEE) (Wang, Feng, Qiu, Gu, Zhao)
- **Domain:** General time series affected by news (e.g. electricity, economy)
- **Sub-domain:** News-driven forecasting with LLM agents
- **Tech / AI used:** LLM agents that filter irrelevant news and reflect on their predictions; LLaMA-2 fine-tuned on news + numbers
- **Problem:** Number-only models ignore news events that change the future.
- **Research gap (authors):** Weak where human activity matters little (e.g. precise weather); limited by LLM token length. Also: no calibration, no abstention, no impact chain, no India.
- **Relevance:** Very high (closest method to the user's idea; read in full).

Not added (could not verify details): "Compressing transfer: mutual learning-empowered knowledge distillation for TKG reasoning" (IEEE TNNLS 2025); "Combining Financial Data and News Articles for Stock Price Movement Prediction Using LLMs" (IEEE Xplore, venue unconfirmed). India-related preprint to check: "Adaptive Financial Sentiment Analysis for NIFTY 50 via Instruction-Tuned LLMs, RAG and RL" (arXiv 2512.20082).

---

## Gap matrix (from abstracts)

| # | Text/news events | Causal graph | Calibrated % | Says "unknown" | Forward impact chain | Live test | India |
|---|---|---|---|---|---|---|---|
| 1 | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| 2 | ✅ | ❌ | ❌ | ❌ | ⚠️ one step | ❌ | ❌ |
| 3 | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| 4 | ✅ | ✅ (past) | ❌ | ❌ | ❌ | ❌ | ❌ |
| 5 | ✅ | ✅ | ❌ | ❌ | ⚠️ inside model | ❌ | ❌ |
| 6 | ? | ❌ | ❌ | ❌ | ❌ | ⚠️ rolling | ✅ |
| 7 | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| 10 | ✅ | ❌ | ⚠️ Brier | ❌ | ❌ | ✅ | ❌ |
| 15 | ✅ | ⚠️ | ❌ | ❌ | ⚠️ what-if | ❌ | ❌ |

## Common gaps
1. Almost no calibrated probabilities.
2. None says "I don't know".
3. Only ForecastBench tests live; others risk leakage.
4. Causal chains are extracted (P4, P5) but not used forward to forecast impacts across sectors.
5. India nearly absent (only P6, market data only).
6. Big rare events remain fragile (P6).
7. Single domain, single case (P1, P5).
8. LLM extraction errors not measured (P3, P4, P5).

## Where the user's research fits
Calibrated, abstaining, impact-aware event forecasting for India, evaluated live:
P1/P2 agents + P4/P5 causal graph + P10 live evaluation + P6 rare-event lessons.

---

## Notes added by Claude (14 October 2026)

- **Numbering:** there is no Paper 13 in this list (12 → 14), so 21 papers are numbered 1–22. Keep the numbers stable so the gap matrix still matches; mention the gap if the list is cited.
- **The gap claims cover only this set of 21 abstracts.** Before any paper claims "no calibrated %", "none says I don't know" or "only ForecastBench tests live", read these core LLM-forecasting works, which are outside this set and partly address those gaps:
  - Halawi et al. 2024, "Approaching Human-Level Forecasting with Language Models" (retrieval, ensembling and calibrated probabilities on questions after the model's cutoff);
  - Zou et al. 2022, Autocast; Jin et al. 2021, ForecastQA;
  - Schoenegger et al. 2024, "Wisdom of the Silicon Crowd";
  - Paleka et al. 2025, "Pitfalls in Evaluating Language Model Forecasters" (leakage);
  - Wen et al. 2024, "Know Your Limits" (abstention in LLMs, not specific to forecasting);
  - Bayesian-network work, for the forward-impact-chain gap.
  Verify each of these references yourself before citing.

---

## Gap-verification checklist (fill from the full text before any gap is claimed)

A paper that uses retrieval or Brier scoring does not invalidate this research direction. It means the novelty claim must be stated more precisely. For each paper that touches a claimed gap, record:

| Paper | What it actually tested | Data (region, period, question type) | Evaluation (metrics, live or historical, leakage control) | Overlap with our contribution | How our claim differs (precise wording) | Read in full? |
|---|---|---|---|---|---|---|
| ForecastBench (P10) | | | | | | ☐ |
| Halawi et al. 2024 | | | | | | ☐ |
| From News to Forecast (P22) | | | | | | ☐ |
| NIFTY framework (P6) | | | | | | ☐ |
| Paleka et al. 2025 | | | | | | ☐ |
| … | | | | | | ☐ |

A gap goes into a paper only when every row that touches it is filled from the full text.
