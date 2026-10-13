# Stage-1 merge checklist (draft for review; nothing merged yet)

Date: 14 October 2026. Status: **draft for the user's review.** No merge happens until the user approves this checklist. UI work (Phase 2) starts only after the merge is settled.
Implementation order: Documentation → Flutter UI → Python backend → connect the UI to real data. Exception: the December 2026 pilot is recorded by hand. The research direction is chosen by the student; formal M.Tech guide approval is pending.

## 1. Facts (checked 14 Oct 2026)

| Item | Value |
|---|---|
| Source | `origin/reflica/stage-1-flutter-integration` @ `ae7084e` (9 commits, 90 files) |
| Target | `claude/lucid-mendel-zy17b7` (= `main` @ `4d55b8f` + forecasting documentation only) |
| Common base | `4d55b8f`; neither side was rebased; stage-1 contains all of `main` |
| Trial merge (scratch copy, cancelled) | **3 conflicts, all documentation:** `PROGRESS.md`, `README.md`, `research/README.md`. No code conflicts. |
| Existing backup | `backup/lucid-mendel-pre-stage1-2026-10-14` @ `1182570` (older than the current head) |
| Stage-1 tests (earlier run) | Python 1030 passed, 4 skipped; Flutter not run (no SDK in the cloud) |

## 2. What stage-1 changes (review before approving)

- **Python:** `research/reflica_service/`, a local FastAPI service bound to `127.0.0.1` (optional `service` extra) with LLM extraction, the `graph@1` contract, impact preview and decisions, and `describe`/`regress`.
- **Flutter:** `lib/services/reflica_api.dart`, `lib/graph/graph1.dart`, graph widgets, `proposal_review_screen.dart`, changes to the plan detail and new-plan screens, the `http` package, and 7 test files plus a live test (skipped unless `REFLICA_LIVE=true`).
- **Android:** a debug-only manifest allows plain `http://` to reach the local service. Release builds are unchanged.
- **⚠️ Firestore (legacy plan data), additive changes that need your explicit approval:**
  - plan documents gain an optional `graph` field. Old plans keep `null` and their nodes and edges;
  - a new append-only subcollection `users/{uid}/plans/{planId}/events/{eventId}` records graph decisions;
  - **new** plans no longer get the fixed starter nodes; they start with an empty `graph@1` graph.

  Nothing is deleted or migrated, and existing plans stay readable. This is still a change to the legacy data model, so approve or reject it explicitly.
- **Documents:** `research/MTECH_PLAN.md`, `SCIENCE_DIRECTION.md`, `RESEARCH_OUTLINE.md`, `PLATFORM_AUDIT.md`, `reflica_service/NOTES.md` and `ARCHITECTURE_MEMORY.md` describe the earlier directions (an LLM-extraction Minor 1, "scientific discovery").

## 3. Decisions needed before merging

1. Approve the additive Firestore changes in section 2. If you reject them, the merge waits until a plan exists to keep that code inactive.
2. Who runs the merge: Claude in the cloud (then you pull and test on the Mac), or you on the Mac with this checklist?
3. Merging into `main` happens later, through a pull request, after the Mac tests pass. Agree?

## 4. Steps

**Before**
- [ ] `git status` is clean; `git fetch origin`.
- [ ] Stage-1 is still at `ae7084e`. If it moved, review the new commits first.
- [ ] Create and push a **new** backup of the current head: `backup/lucid-mendel-pre-stage1-merge`.

**Merge**
- [ ] `git merge --no-ff origin/reflica/stage-1-flutter-integration` on `claude/lucid-mendel-zy17b7`. No rebase, no force-push.
- [ ] Resolve `PROGRESS.md`: keep the forecasting header from our side. In the decisions log, keep **every row from both sides** in date order (stage-1's 10-10 rows before our 10-13/10-14 rows). Keep stage-1's status sections, labelled as previous or paused work where relevant.
- [ ] Resolve `README.md`: keep our forecasting introduction and order sentence; keep stage-1's service and run instructions under the product and research tracks.
- [ ] Resolve `research/README.md`: keep the "paused" banner and stage-1's service install and run notes.
- [ ] No other file is edited during conflict resolution.

**Documentation after the merge (no deletions)**
- [ ] Add a banner to `research/MTECH_PLAN.md`, `SCIENCE_DIRECTION.md`, `RESEARCH_OUTLINE.md` and `PLATFORM_AUDIT.md`: "Superseded by `NEW_DIRECTION.md` (14 Oct 2026); kept for history."
- [ ] Add a note to `reflica_service/NOTES.md` and `ARCHITECTURE_MEMORY.md`: "Preserved; candidate component for the final project's impact analysis; not current work."
- [ ] Update `docs/ARCHITECTURE.md` section 2 (stage-1 merged; new plan `graph` field and `events` subcollection) and `PROGRESS.md` (log row).

**Verify in the cloud**
- [ ] `cd research && pip install -e ".[dev,csp,service]" httpx && pytest`. Record the counts. Expect at least 1030 passed; the API test file runs once `httpx` is installed.

**Verify on the Mac**
- [ ] `flutter pub get` → `flutter analyze` (record the output) → `flutter test` (record the counts).
- [ ] Web (`flutter run -d chrome`): sign in, sign out, dashboard, My Plans, open an **old** plan, create a new plan, edit, delete.
- [ ] Stage-1 screens with the service **off**: a clear error, no crash. Optional with the demo service on (`python -m reflica_service.demo …`): extraction review and impact approval.
- [ ] Android debug build: sign-in and plans work.
- [ ] Firestore console: an old plan document is unchanged; a new plan has a `graph` field; `events` appears only after a graph decision.

**After**
- [ ] Push the merge commit. Log the results in `PROGRESS.md` and record any test failure in full.
- [ ] Only then: the Phase 2 UI plan review.

## 5. Rollback

- Before pushing: `git merge --abort`, or `git reset --hard backup/lucid-mendel-pre-stage1-merge`.
- After pushing: `git revert -m 1 <merge-commit>` (keeps history; no force-push).
- Plans created with the stage-1 app keep their `graph` field and `events` after a revert. The older app ignores the extra field, but this should be confirmed on the Mac before relying on it.
