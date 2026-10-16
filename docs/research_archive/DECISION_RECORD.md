# Reflica Research Decision Record

**Created:** 15 October 2026, in the documentation reset. **Owner:** Sundram Awasthi, M.Tech CSE 2026–28, GLA University.

**Purpose:** one place for the decisions that must stay visible. It records **only what existing records or the user state**. Conflicts are flagged for the user; none is resolved by guesswork.

**Labels:**
- **Decided** = stated by the user as a decision.
- **Provisional** = working choice, not approved.
- **Unresolved** = no agreed choice yet.
- **Conflict** = records disagree.

## 1. Titles

| Item | Value | Status | Source |
|---|---|---|---|
| **Official university title (on record)** | **AI-Powered Research Knowledge Graph and Change Impact Analysis System** | **Decided:** unchanged unless formally approved for revision | User instruction (15 Oct 2026). Not found in any earlier repository file |
| **Minor Project 1 title** | *How Well Can Language Models Forecast India? A Prospective Benchmark of Indian Economic, Infrastructure and Policy Events* | **Provisional.** Taken from the interim `../../MINOR1_PLAN.md`. **Will be replaced by the title in the user's forthcoming authoritative plan** | User instruction (15 Oct cleanup task); `MINOR1_PLAN.md` |
| Minor 1: earlier titles (history) | (a) "Minor Project 1: India Forecast Benchmark and Forecast Dashboard" (14 Oct); (b) "Reflica India: Evidence-Aware Economic Forecasting and Forecast Revision" (15 Oct, CPI) | (a) superseded; (b) **deferred** | `superseded_plans/NEW_DIRECTION_2026-10-14.md` §3; `superseded_plans/PROJECT_PLAN_CPI_2026-10-15.md` Part 2 |
| **Minor Project 2 title** | **Conflict, unresolved.** (a) "Interactive and Evidence-Grounded Forecasting Agent" (14 Oct). (b) "Honest Forecasting of India's Policy Decisions: Calibrated Probabilities and Abstention" (15 Oct) | **Provisional / Conflict.** Needs the user's and supervisor's decision after Minor 1 | `NEW_DIRECTION_2026-10-14.md` §4; `PROJECT_PLAN_CPI_2026-10-15.md` Part 3 |
| **Final M.Tech thesis title** | **Conflict, unresolved.** (a) "Final Project: Impact-Aware Forecasting" (14 Oct). (b) "Honest AI Forecasting of India's Economic and Policy Events: Calibrated Probabilities, Abstention and Live Evaluation" (15 Oct working title) | **Provisional / Conflict.** Depends on results and supervisor guidance | `NEW_DIRECTION_2026-10-14.md` §5; `PROJECT_PLAN_CPI_2026-10-15.md` Part 4 |
| Overall programme title (history) | "Predictive AI for India's Economy and Government Policy" (15 Oct, CPI programme) | Superseded with the CPI plan | `PROJECT_PLAN_CPI_2026-10-15.md` |
| Previous vision (history) | "Human-Centered Multimodal Cognitive Intelligence & Closed-Loop Decision-Support Platform" | History | `../../PROGRESS.md` header |
| Previous thesis sentence (history) | "Attribute-aware revision of LLM-extracted state graphs under partial-satisfaction and capacity constraints…" | Paused 13 Oct, archived 14 Oct (branch `archive/old-reflica-2026-10-14`) | `../../PROGRESS.md` "Previous M.Tech research track" |

## 2. Field and subfield

| Project | Field / subfield | Status | Source |
|---|---|---|---|
| Overall research (all stages) | **Area:** Artificial Intelligence · **Subfield:** Machine Learning and Predictive AI · **Specific area:** Agent-based event forecasting · **Initial domain:** Indian economy, climate, critical infrastructure, selected geopolitical events | **Recorded once** (14 Oct). The user's own notes (`Research_Work_paper.docx`, uploaded, **not in the repository**) list the same | `superseded_plans/NEW_DIRECTION_2026-10-14.md` §1 |
| Minor Project 1 | Not separately recorded. Note: "agent-based" fits Minor 2 better than a benchmark of existing LLMs | **Unresolved** | — |
| Minor Project 2 | Not separately recorded | **Unresolved** | — |
| Final thesis | Not separately recorded. The title on record suggests knowledge graphs / change-impact analysis | **Unresolved** | — |

## 3. Long-term vision (kept separate from Minor 1 deliverables)

**Honest AI Forecasting of Indian Events** (user, 15 Oct). An AI system that:
- forecasts important Indian economic, infrastructure and policy/geopolitical events from dated public evidence;
- gives calibrated probabilities;
- abstains when evidence is insufficient;
- explains possible downstream consequences;
- is evaluated against real outcomes.

The 14 Oct version adds a public website, an "Ask the Forecaster" agent and a cause-and-effect graph (`NEW_DIRECTION_2026-10-14.md` §1). **None of these is a Minor 1 deliverable.**

## 4. Research gaps: history and verification status

**No novelty claim is established.** All gaps below are candidates.

| Gap statement | For | Verification status | Where |
|---|---|---|---|
| 5 gaps: no calibrated %, no abstention, no live testing, no downstream effects, India missing (22-paper review) | Programme | Abstract level, from the user's notes. Partly contradicted later: ForecastBench (live, calibration) and LiveMacroEval (live) exist | `Research_Work_paper.docx` (outside repo); `literature/LITERATURE_FORECASTING.md` |
| No India-specific prospective LLM forecasting benchmark found | **Current Minor 1** | **Search-level only, not exhaustive.** Verification tasks are listed in `MINOR1_PLAN.md` §3 | `../../MINOR1_PLAN.md` §3 |
| CPI gap v1–v6 (from "nobody uses news to revise India CPI forecasts" to v6: "explicit, pre-registered, scored gate over dated text claims on a numeric CPI forecast vs never/always/small-step updating") | **Deferred** CPI study | v6 provisional. LiveMacroEval was read only at search level. The nowcasting literature shows revision attribution exists; Forecast-Dojo shows claim ledgers exist | `research_gaps/CLOSEST_METHODS.md`; `literature/LEVEL2_READINGS.md` (rounds 2–7) |
| Rejected or corrected gap claims: "no one revises forecasts with news" (revision exists: nowcasting, Forecast-Dojo, LiveMacroEval); "BIS 2026 32%" (was the PIER Thailand paper); "Banque de France Reddit" (not found) | — | Rejected or corrected | `literature/VERIFICATION.md` §E–G |

## 5. Deferred ideas (not Minor 1 requirements)

- CPI evidence-aware forecast revision: numeric model + LLM claim extraction + revision gate (`superseded_plans/`).
- Calibrated forecasting agent with abstention ("Ask the Forecaster").
- RBI policy-decision probabilities with calibration and abstention.
- Downstream impact / cause-and-effect graph (possibly linked to the title on record).
- Hindi/regional-news condition; human-forecaster comparison; external timestamping service (D7).
- Public dashboard beyond a scoreboard.

## 6. Decisions still open (need the user and/or supervisor)

1. Whether, and how, to change the official title on record.
2. The final Minor 1 plan and title (the user will supply them).
3. Minor 2 title and scope (conflict in §1).
4. Final thesis title (conflict in §1).
5. Field/subfield per project (§2).
6. Whether to copy the user's `Research_Work_paper.docx` (22-paper notes) into this archive.
