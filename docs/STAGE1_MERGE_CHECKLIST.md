# Stage-1 merge checklist (draft v2 for review; nothing merged)

Date: 14 October 2026 (v2 after the user's review). Status: **merge NOT approved. Firestore changes: approval pending.** UI work (Phase 2) starts only after the merge decision is settled.
Implementation order: Documentation → Flutter UI → Python backend → connect the UI to real data. Exception: the December 2026 pilot is recorded by hand. The research direction is chosen by the student; formal M.Tech guide approval is pending.

## 1. Facts (checked 14 Oct 2026)

| Item | Value |
|---|---|
| Source | `origin/reflica/stage-1-flutter-integration` @ `ae7084e` (9 commits, 91 files differ from `main`) |
| Target | `claude/lucid-mendel-zy17b7` (= `main` @ `4d55b8f` + forecasting documentation only) |
| Common base | `4d55b8f`; neither side was rebased; stage-1 contains all of `main` |
| Trial merges (scratch copies, cancelled) | At `43a35bf` / `1182570`: 1 conflict (`PROGRESS.md`). At `90ae02a` and the current head: **3 conflicts, all documentation** (`PROGRESS.md`, `README.md`, `research/README.md`); the two READMEs were edited on our side in `90ae02a`. Re-check on merge day. |
| Existing backup | `backup/lucid-mendel-pre-stage1-2026-10-14` @ `43a35bf` (verified on GitHub 14 Oct). **Older than the current head; not sufficient.** |
| Earlier test results | Python 1030 passed / 4 skipped on stage-1 alone. **Evidence of a previous run only; says nothing about the combined branch.** Flutter has never been run in the cloud. |

## 2. What stage-1 changes

- **Python:** `research/reflica_service/` (local FastAPI on `127.0.0.1`, optional `service` extra): LLM extraction, the `graph@1` contract, impact preview and decisions, `describe`/`regress`.
- **Flutter:** `reflica_api.dart`, `graph/graph1.dart`, graph widgets, a proposal review screen, changes to the plan detail and new-plan screens, the `http` package, 6 new Flutter test files (one is the live test `test/live/live_service_test.dart`, skipped unless `REFLICA_LIVE=true`) and JSON fixtures.
- **Android:** a debug-only manifest allows plain `http://`. Release builds are unchanged.
- **Documents:** six stage-1 documents describe earlier directions (they get "superseded" banners; nothing is deleted).

### 2.1 Legacy plan storage and behaviour: approval pending

| Change | What the code shows (static reading, 14 Oct) | Still to confirm |
|---|---|---|
| Optional `graph` field on plan documents | Additive. `main`'s `Plan.fromJson` reads only named keys, so an **old build can read** a stage-1 plan. | Run it on the Mac. |
| ⚠️ Old build **editing** a stage-1 plan | `main` saves with `set(plan.toJson())`, a **full overwrite without merge**. An old build that edits a stage-1 plan would **silently drop its `graph` field**. | Matters if old and new builds are used at the same time (e.g. an older Android install and new web). Mitigation options: update all devices together, or change saves to merge (needs your approval). |
| `users/{uid}/plans/{planId}/events/{eventId}` subcollection | Append-only decision log with a server timestamp. | Firestore **rules** must allow it. Rules are not in the repo; if they only cover `plans/{planId}`, event writes fail. |
| ⚠️ Deleting a plan | Stage-1 deletes only the plan document. Firestore does not cascade, so its `events` stay behind with no plan. | Decide: accept, or delete events too (code change, needs approval). |
| **New plans no longer get starter nodes** | A **user-visible behaviour change**: new plans start with an empty `graph@1` graph. | Confirm it is intended; check plan creation and editing on the Mac. |

## 3. Decisions needed before any merge

1. **Firestore changes** (section 2.1): hold until this diff and the combined tests are reviewed. Then approve, adjust or reject each row.
2. **Starter nodes:** keep the stage-1 behaviour (empty graph) or restore starters?
3. **Firestore rules:** export the current rules from the console and add them to the repo before approving the `events` subcollection.
4. **Who runs the merge:** Claude in the cloud (you pull and test on the Mac), or you on the Mac with this checklist.
5. **`main`:** merge into `main` later, through a pull request, after the Mac tests pass.

## 4. Steps (once approved)

**Before**
- [ ] `git status` clean; `git fetch origin`; stage-1 still at `ae7084e` (if it moved, review the new commits first).
- [ ] Create a **fresh backup of the exact current head**: `git branch backup/lucid-mendel-pre-stage1-merge HEAD` and push it.
- [ ] **Verify the backup:** `git rev-parse backup/lucid-mendel-pre-stage1-merge` equals `git rev-parse HEAD`, and the remote branch shows the same hash.
- [ ] Export the Firestore rules into the repo (`firestore.rules`) and read them.

**Merge**
- [ ] `git merge --no-ff origin/reflica/stage-1-flutter-integration`. No rebase, no force-push.
- [ ] `PROGRESS.md`: keep our forecasting header; keep **every log row from both sides** in date order; keep stage-1's status sections, labelled as previous or paused work.
- [ ] `README.md`: keep our forecasting introduction and order sentence, and stage-1's service and run instructions.
- [ ] `research/README.md`: keep the paused banner and stage-1's service notes.
- [ ] Edit no other file during conflict resolution.

**Documentation after the merge (no deletions)**
- [ ] Banners on `research/MTECH_PLAN.md`, `SCIENCE_DIRECTION.md`, `RESEARCH_OUTLINE.md`, `PLATFORM_AUDIT.md`: "Superseded by `NEW_DIRECTION.md` (14 Oct 2026); kept for history."
- [ ] A note on `reflica_service/NOTES.md` and `ARCHITECTURE_MEMORY.md`: preserved as a candidate for the final project's impact analysis.
- [ ] Update `docs/ARCHITECTURE.md` section 2 and `PROGRESS.md`.

**Verify the combined branch (fresh runs; earlier results do not count)**
- [ ] Cloud: `cd research && pip install -e ".[dev,csp,service]" httpx && pytest`. Record the exact counts and any failure in full.
- [ ] Mac: `flutter pub get`, `flutter analyze`, `flutter test`. Record the output.
- [ ] Web: sign in and out; dashboard; My Plans; open an **old** plan; create a new plan (check the starter-node behaviour); edit; delete.
- [ ] Stage-1 screens with the service **off**: a clear error, no crash. Optional with the demo service on: extraction review and impact approval.
- [ ] Android debug build: sign-in and plans work.
- [ ] **Compatibility test:** open a stage-1-created plan in an old `main` build and confirm it reads. Do **not** save it from the old build unless you are testing the overwrite risk on a throwaway account.
- [ ] Firestore console: old plan documents unchanged; a new plan has `graph`; `events` appear only after a decision; event writes are allowed by the rules.

**After**
- [ ] Push the merge commit; log results in `PROGRESS.md`.
- [ ] Only then: the Phase 2 UI plan review.

## 5. Rollback: code only, not data

- Before pushing: `git merge --abort`, or `git reset --hard backup/lucid-mendel-pre-stage1-merge`.
- After pushing: `git revert -m 1 <merge-commit>`. This keeps history; no force-push.
- **A code rollback does not undo data changes.** Plan documents with a `graph` field and any `events` documents written while the stage-1 build was in use stay in Firestore. Removing them would need a separate, explicitly approved clean-up. After a rollback, the old build reads those plans but would **drop `graph` on save** (section 2.1).
- To limit data exposure, test the merged build first with a **test account** before using it with real plans.
