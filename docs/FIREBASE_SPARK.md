# Firebase on the free Spark plan: setup and security review

Date: 14 October 2026. Status: **review and proposal. Nothing deployed or changed in Firebase.** Project `reflica-593b4`, Cloud Firestore `(default)` database (created 14 Oct 2026 by the user, empty).
Implementation order: Documentation → Flutter UI → Python backend → connect the UI to real data. Exception: the December 2026 pilot is recorded by hand. Research direction chosen by the student; formal M.Tech guide approval pending.

## 1. What the app actually uses (checked in code on `main` and the stage-1 branch)

| Product | Used? | Evidence |
|---|---|---|
| Firebase Auth (Google sign-in) | **Yes** | `lib/services/auth_service.dart`; `google_sign_in` on Android, popup on web |
| Cloud Firestore `(default)` | **Yes** | `FirebaseFirestore.instance` in `main.dart`, `plan_repository.dart`, `notification_service.dart`; offline persistence on |
| Realtime Database | **No** | No `firebase_database` package or API. `databaseURL` appears only in the generated `firebase_options.dart` |
| Firebase Analytics | Package only | `firebase_analytics` is in `pubspec.yaml` but never called from Dart. The Android SDK may still collect automatic events (e.g. first open); free on Spark |
| Firebase AI Logic (`firebase_ai`) | Package only | Never called. Not to be used for forecasting (decision: model keys stay server-side) |
| Cloud Storage, Functions, Hosting, Messaging | **No** | Not in `pubspec.yaml`; no `firebase.json` |

Configuration points to the right project:
- web `projectId: 'reflica-593b4'` (`lib/firebase_options.dart`);
- Android `google-services.json` has `project_id: reflica-593b4` and package `com.reflicaa.app`, matching `applicationId` in `android/app/build.gradle.kts`;
- iOS and desktop are not configured; the app throws `UnsupportedError` there, as before.

Paths the app read and wrote before the 14 Oct clean-up (all per user; after it, only notifications remain):
- `users/{uid}/plans/{planId}`: create, set (full overwrite), delete; list ordered by `updatedAt`;
- `users/{uid}/notifications/{id}`: create; `update({read: true})`; `markAllRead` = query `read == false` then a batch update; delete; list ordered by `createdAt`, limit 50;
- `users/{uid}/plans/{planId}/events/{eventId}`: **stage-1 only**; create with `created_at = serverTimestamp()`.

## 2. Can it run on Spark without paid services? Yes, for everything planned up to Phase 4

| Need | Spark? | Plan |
|---|---|---|
| Sign-in, Firestore reads and writes from the app | Yes | As now |
| Security rules | Yes | Published by hand in the console after approval |
| December pilot (JSONL by hand, git) | Yes | No Firebase involved |
| Python backend run on your own computer, writing to Firestore with the Admin SDK | Yes | Counts toward the same free quotas; service-account key kept outside Git |
| Scheduled jobs (Cloud Functions, Cloud Scheduler) | **No (needs Blaze)** | **Postponed.** Run scripts by hand or with a local scheduler (cron, launchd) |
| Firestore managed backups / point-in-time recovery ("Disaster Recovery" tab) | **No (needs Blaze)** | **Postponed.** Research records are safe in Git; app plan data has no backup (accepted risk for now) |
| Firestore export to a Cloud Storage bucket | Needs billing | **Postponed** |
| Paid LLM APIs | Not a Firebase cost | Pilot uses free tiers or local open models where possible; free tiers have rate limits and may have different data-use terms. **Decision needed in November** |
| Firebase Hosting for the web app | Free tier exists | Not configured; decide later |

## 3. Free quotas and what happens when they run out

Spark quotas, to be **re-checked on the Firebase pricing page before relying on them** (they can change):
- **Cloud Firestore:** 1 GiB stored; about 50,000 document reads/day, 20,000 writes/day and 20,000 deletes/day; 10 GiB/month network egress. Daily quotas reset around midnight US Pacific time.
- **Realtime Database:** 1 GB stored, 10 GB/month downloaded, 100 simultaneous connections. Not used by the app.
- **Auth:** Google sign-in has no per-use charge on Spark. If the project is ever upgraded to Identity Platform, Spark has a daily-active-user cap.

**When a quota is exceeded on Spark, there is no charge.** That operation type stops working until the quota resets (Firestore returns quota or resource-exhausted errors), so the app can fail to load or save. Nothing is "unlimited". To stay well inside the limits:
- keep lists limited (notifications already limit to 50);
- avoid listeners on large collections;
- the offline cache reduces repeated reads;
- forecasting data will be read as small summary documents (Phase 4).

## 4. Proposed Firestore rules (`firestore.rules` in the repo root: NOT published)

> **Update, 14 Oct 2026 (after the old plan app was deleted).** `firestore.rules` now allows **only** `users/{uid}/notifications/{id}` (owner-only, unchanged validation). The plan and stage-1 event paths were removed, so they are now denied like everything else. Emulator re-run with `docs/rules-tests/firestore.rules.test.mjs` (updated to match):
> - proposed rules **22/22 passed** (5 allow, 17 deny, including 7 checks that the old plan and event paths are closed);
> - deny-all control: 0/6 allow (5 checks + the setup write), 17/17 deny;
> - allow-all control: 5/5 allow, 0/17 deny.
>
> The event-deletion decision is no longer needed. The description and 37-check matrix below record the earlier version (commit `b40ef22`).

Design:
- Owner-only access. `request.auth != null && request.auth.uid == uid` for every operation on the three paths.
- **Everything else is denied** because no rule matches it: the `users/{uid}` document itself, other users' data, `users/demo/...`, and any `questions`/`forecasts`/`resolutions`/`scores` collections. Nothing is public.
- The signed-out `demo` fallback gains nothing. Signed-out requests have `request.auth == null`, and no real user's uid is `demo`.
- **Light validation**, matching the fields the code writes:
  - **plans:** `id` equals the document id, `ownerId` equals `uid`, `title` is a string. `set()` overwrites are allowed; the stage-1 `graph` field is allowed.
  - **notifications:** on create, `id`/`ownerId` match and `read` is a boolean. Updates may change **only** `read`, which covers `markRead` and the `markAllRead` batch.
  - **events:** append-only. Create requires `id` = document id, `actor_uid` = `uid`, `type` is a string, and `created_at` = server time (the code uses `serverTimestamp()`, so a backdated event is refused). **Updates are denied.** Deletes by the owner are **allowed**, so events can be cleaned up when a plan is deleted. This is an open decision (section 6).
- Firestore's own document limit (1 MiB) applies; no extra size rules for now.

### Test matrix: run on 14 Oct 2026 in the local Firestore emulator, **37/37 passed**

Script: `docs/rules-tests/firestore.rules.test.mjs`. It was written by Claude as verification evidence; you may rewrite it.

| Area | Allowed (expected and observed) | Denied (expected and observed) |
|---|---|---|
| Plans | owner create; read; list ordered by `updatedAt`; full `set` overwrite; plan with `graph`; delete | ownerId changed to another user; `id` ≠ document id; missing title; other user read, list or write; signed-out read; signed-out or signed-in write to `users/demo` |
| Notifications | owner create; latest-50 query; `update({read: true})`; `markAllRead` query plus batch; delete | changing `title`; `read` not boolean; other user read; signed-out write to `users/demo`; ownerId of another user |
| Events | owner append with `serverTimestamp()`; owner read; owner delete | client-chosen `created_at`; `actor_uid` of another user; editing an event; other user read |
| Everything else | none | the `users/{uid}` document itself (read or write); `forecasts` read when signed out; `questions` write when signed in; unknown sub-path |

How to re-run (Node 22 and Java required; downloads only the local emulator; nothing touches the real project):
```
mkdir rulestest && cd rulestest && npm init -y
npm i firebase-tools@13.29.1 @firebase/rules-unit-testing@3.0.4 firebase@10.14.1
cp ../firestore.rules . && cp ../docs/rules-tests/firestore.rules.test.mjs test.mjs
echo '{"firestore":{"rules":"firestore.rules"},"emulators":{"firestore":{"host":"127.0.0.1","port":8080}}}' > firebase.json
npx firebase emulators:exec --only firestore --project demo-reflica-rules "node test.mjs"
```
(`demo-` project ids never connect to a real Firebase project.)

No `firebase.json` is added to the repository, so `firebase deploy` from the repo cannot publish the rules by accident.

## 5. Realtime Database (not used by the app)

Its rules currently allow public reads and writes. The data is `null`, but **anyone on the internet could write to it**, using its free quota and storing content under the project's name.

**Recommendation:** in the console (Realtime Database → Rules) replace the rules with:
```json
{ "rules": { ".read": false, ".write": false } }
```
- **Effect on the app: none.** The app never uses the Realtime Database, and Cloud Firestore has its own separate rules.
- **Reversible:** the rules can be edited again later.
- Deleting the database is not needed; locking it is enough.

**Not done; waiting for your approval.**

## 6. Decisions for the user

1. **Publish `firestore.rules`** to the console (copy the text into Firestore → Rules → Publish)? Until then, the deny-all rules block the app completely.
2. **Event deletion:** keep "owner may delete" (allows cleanup and lets users remove their own data), or deny it to make events a stricter audit log (orphans then stay after a plan is deleted)?
3. **Lock the Realtime Database** as in section 5?
4. **Plans saved offline on your devices:** with deny-all rules, any pending offline writes that reach the server will be **rejected and removed from the device**. With the proposed rules they will upload. Real or test data?
5. **Pilot models on free tiers or local open models** (November), since paid AI APIs are excluded.

## 7. Code changes needed

**None** to use the new database. The app already uses the `(default)` Firestore database of `reflica-593b4`.

Optional later cleanup (needs approval): the notification service's signed-out `'demo'` fallback produces harmless permission-denied errors. It could skip the write instead.
