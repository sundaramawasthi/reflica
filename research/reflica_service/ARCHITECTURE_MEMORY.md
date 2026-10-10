# Reflica: researcher memory, longitudinal graphs, personalization: architecture proposal

Status: **proposal**. Nothing in sections 2–6 is implemented unless it is marked *implemented*.
The current milestone is still Stage 1: text → graph proposal → review → saved graph → impact
preview → approval.

## 1. What exists today (implemented and tested)

| Capability | Where | Relevance to memory |
|---|---|---|
| `graph@1`: `kind` (what an item is) separate from `basis` (where it came from); verbatim source spans; `legacy_unverified`; review notes | `graph/contract.py` | Research knowledge with provenance; "explicit vs inferred" is already a field |
| preview → fingerprint → decision → apply; `ChangeRecord`, `AcceptanceRecord` | `graph/impact.py`, `extraction/extract.py` | The approval pattern every memory change will reuse; records are the raw material of history |
| Extraction proposals: model suggests, service verifies quotes, researcher reviews | `extraction/` | Same shape as a memory proposal |
| `regress@1` run records (dataset hash, plan hash, approver, versions) | `analyses/regress.py` (uncommitted patch) | Reproducible results to link into history |
| Firebase sign-in; per-user Firestore paths `users/{uid}/plans`, `users/{uid}/notifications` | Flutter app | Per-researcher storage boundary (but **no security rules are in the repository**) |

Not implemented: researcher profiles, projects, event history, memory items, retrieval,
personalization, pattern learning, emotion-aware responses, consent, export or delete tooling.

## 2. Four mechanisms (kept separate)

- **Memory**: approved information kept across sessions.
- **Personalization**: using approved, relevant memory to adapt a response. Each response
  records which memory items it used.
- **Pattern learning**: proposing an inferred memory from repeated, attributable events, with
  confidence. It is saved only after the researcher reviews it.
- **Model improvement**: changing the model or shared behaviour. Out of scope. It never
  happens as a side effect of storing memory, and private data is never used for it without
  explicit authorization.

## 3. One store, four memory layers

The layers are views over three record types, not four separate databases.

| Layer | Stored as | Notes |
|---|---|---|
| B. Research knowledge | `graph@1` graphs, one or more per project | Exists. Needs the `graph@2` kinds in section 5 |
| C. Research history | **Append-only event log** per project | Each event names actor, time, the record (acceptance, impact decision, analysis run, memory decision) and the graph hash before and after |
| A. Identity and preferences | `MemoryItem` with `layer = identity \| preference` | Explicit statements by the researcher, or approved proposals |
| D. Working patterns | `MemoryItem` with `layer = working_pattern`, `origin = inferred` | Always cites the events it was inferred from |

**MemoryItem** (planned):
```
id, scope{owner_id, workspace_id, project_id?, visibility: private|project|team}
layer: identity | preference | working_pattern
statement: str                        # plain language, editable by the researcher
origin: explicit | inferred           # never shown as "you said" when inferred
evidence: [EventRef | SourceSpan]     # required; at least N events for an inferred item
confidence: float | null              # inferred only; stated_by = "pattern_detector@k"
status: proposed | approved | rejected | superseded
created_at, reviewed_at, reviewed_by, superseded_by, valid_from
sensitivity: normal | personal        # personal items need explicit consent to persist
```
Changing a preference supersedes the old item; it does not overwrite it. History is kept, and
the old item is marked inactive.

**Longitudinal graph.** "How did the central hypothesis change over six months?" is answered
by replaying the event log for a node's ID together with its `supersedes` chain (section 5),
citing each event. Questions about evidence or assumptions use graph queries plus impact
analysis. If no event or source supports an answer, the reply says it was not found in memory;
it never fills the gap from the model.

## 4. Personalization, pattern learning and emotional intelligence

- **Context pack**: before an LLM call, the service picks the approved memory items relevant to
  the request (by scope, layer and project). They are passed to the model as an explicit, cited
  list and recorded as `memory_used` on the response. The researcher can always see why a
  response looked the way it did.
- **Pattern detectors**: deterministic first, run over the event log. Example: in 8 of the last
  10 reviews the researcher removed `llm_inferred` items. That produces a proposal: "Prefers
  evidence-backed items; hide or flag inferred suggestions?" with the 8 events cited and a
  confidence value. It is accepted, edited or rejected through the same proposal → decision
  flow. LLM-assisted detectors come later and must cite events.
- **Emotional intelligence**: affect cues in a message, such as possible frustration or
  overload, are treated as uncertain signals for the current conversation only. They are
  **not stored** by default and never become personality or mental-health attributes. Stored
  communication preferences (depth, tone, "critique first") are ordinary, explicit
  `preference` items. A setting `emotional_adaptation: off | on`, off until the researcher
  opts in. When intent is unclear, ask: support, critical feedback or practical next steps?
  Never pretend to feel, flatter, or encourage dependence.

## 5. Prepare now (cheap, additive) vs later

**Now, inside the Flutter milestone:**
1. Store each plan's `graph@1` JSON, plus append-only **events** in
   `users/{uid}/plans/{planId}/events/{eventId}`. Each event holds `{type, record,
   graph_before_sha256, graph_after_sha256, actor_uid, created_at (server time)}`.
   This is the start of layer C.
2. Record `decided_by` as the signed-in account's stable ID (not free text) on every decision.
3. Keep timestamps and actor IDs on stored events, **outside** the fingerprinted contract
   objects, so fingerprints stay deterministic.
4. Write Firestore security rules (owner-only access to `users/{uid}/**`) and add them to the
   repository.

**Reserve, don't build yet:**
- `graph@2`, additive:
  - node kinds `project`, `paper`, `experiment`, `dataset`, `conclusion`, `decision`;
  - edge types `contradicts` (does not propagate) and `supersedes` (records how a node
    evolved);
  - optional node attributes for B5.
- A scope envelope (`owner_id`, `workspace_id`, `project_id`, `visibility`) on every stored
  object once teams exist.
- API: `/v1/memory/{proposals,items,decide,export,delete}` and `/v1/history/query`, using the
  same error format and decision pattern as `/v1/impact/*`.

## 6. Privacy and ownership (plan)

- Consent record before any persistent personalization.
- Every memory item can be viewed, edited, exported and deleted. Deletion removes content and
  leaves a tombstone event with no content.
- Personal, project and team scopes are separate. Every query filters on the caller's scopes,
  and tests check that one researcher's memory never appears for another.
- Only the context pack is sent to a model provider, never the whole memory. Use provider
  settings that exclude training on submitted data. A self-hosted service is an option for
  sensitive research.
- Encryption at rest (Firestore default) plus a retention setting per workspace.

## 7. Stages and acceptance criteria

| Stage | Done when (measured) |
|---|---|
| 1. Knowledge Mapper | In the app: text → proposal → review → saved graph → edit or delete → impact preview → approve or reject, with the event stored. Covered by service tests and Flutter tests |
| 2. Persistent memory | Profiles, projects, event log and memory items with review controls. Export and then import gives an identical store. Delete leaves no content. Cross-user isolation test passes |
| 3. Adaptive partner | Retrieval cites sources on a gold set of history questions. False-memory rate (answers with no supporting record) below an agreed threshold. Every response records `memory_used` |
| 4. Emotional intelligence | Adaptation can be switched off and is off by default. No affect data stored. Blind human rating of tone appropriateness on a scenario set |
| 5. Scientific intelligence | Contradiction and gap detection checked against annotated cases. `sweep@1` and analyses linked as `computed` nodes |
| 6. Continuous evaluation | The metrics above run on every release. After an update, impact analysis changes only the affected nodes (the benchmark's ground truth) |
