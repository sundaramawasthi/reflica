# Edits after removing the old Reflica (for the user to make)

Date: 14 October 2026. On 14 Oct the user decided to delete everything from the old plan-based Reflica, keeping only what serves the predictive-AI direction. Claude deleted the files; **the user makes the edits below** (decision: "Claude deletes, I edit").

**The app does not compile until section A is done.** Work on your Mac, then run the checks in section D.

Archive (nothing is lost; restore any file with `git checkout <branch> -- <path>`):
- `archive/old-reflica-2026-10-14` @ `b40ef22`: the complete old version (plan app, `reflica_bench`, B5 engine, LLM pilot, 203 tests).
- `archive/stage-1-2026-10-14` @ `ae7084e`: the stage-1 branch (`reflica_service`, impact analysis, graph@1).

These are branches (the network proxy refused tags). Protect them on GitHub (Settings → Branches → add a rule for `archive/*`) so they cannot be deleted by mistake.

## A. Required: the app will not build until these are done

### `lib/main.dart`
- Delete the imports on lines 8, 10, 11: `screens/new_plan_flow.dart`, `screens/plan_detail_screen.dart`, `screens/plans_screen.dart`.
- Delete the whole `onGenerateRoute: (settings) { ... }` block (lines 45–69). It only handled `/plan` and `/new-plan`.
- In `routes:` delete `/new-plan`, `/plans`, `/graph`, `/scenarios`, `/documents`. **Keep** `/`, `/dashboard`, `/settings`.

### `lib/screens/home_screen.dart` (signed-out landing page)
- Delete the imports on lines 5, 7, 8, 9, 10: `audience_section`, `evidence_section`, `hero_section`, `input_modes_section`, `living_loop_section`.
- In the `Column` children delete `HeroSection()`, `LivingLoopSection()`, `InputModesSection()`, `AudienceSection()`, `EvidenceSection()` and their comments. Keep `SizedBox(height: 72)` and `CtaFooter()`. A forecasting hero comes in Phase 2.

### `lib/screens/dashboard_screen.dart`
- Delete the imports on lines 4, 7, 8, 9, 10: `activity_table`, `how_it_works_strip`, `quick_actions_panel`, `quick_input_strip`, `use_cases_row`.
- In `_MainArea` delete `QuickInputStrip()`, `UseCasesRow()` (and the `SizedBox`es between them), and the whole `LayoutBuilder(...)` that builds `ActivityTable` / `QuickActionsPanel` / `HowItWorksStrip`. Keep `DashboardTopBar` and `WelcomeCard`.

### `lib/widgets/dashboard/dashboard_sidebar.dart`
- Delete the imports on lines 3–4: `models/plan.dart`, `services/plan_repository.dart`.
- In the items list delete `New Plan`, `My Plans`, `Knowledge Graph`, `Scenarios`, `Documents`. Keep `Home` and `Settings`; forecasting items come in Phase 2.
- Delete the classes `_RecentSection` (line 150), `_RecentRow` and `_RecentRowState` (lines 192–242; they use `Plan` and `/plan`), and remove the `_RecentSection()` child at line 74 together with its wrapper widget. Keep `_HelpCard` (line 243).

### `lib/widgets/dashboard/welcome_card.dart`
- Delete the imports on lines 5–6: `models/plan.dart`, `screens/new_plan_flow.dart`.
- It is built around starting a plan (`_submit` with `NewPlanArgs` and `InputMode`, a mode picker, plan example prompts such as "Plan my exam preparation", buttons to `/new-plan`). **Simplest:** reduce it to a static welcome text ("AI Forecasting for India" plus one sentence, `UI_SPEC.md` §3.1) with no input box. Delete `_PromptBar`/`_PromptBarState` (lines 100–170, including `_submit`), `_AttachMenu` (172), `_StartButton`/`_StartButtonState` (216–271) and `_ExampleChips`/`_Chip`/`_ChipState` (272 onward, "Plan my exam preparation", `/new-plan`), plus the places in the card's `build` that use them.

### `lib/widgets/dashboard/dashboard_top_bar.dart`
- Line 345: tapping a notification calls `pushNamed('/plan', arguments: n.planId)`, which now leads nowhere. Change it to just close the panel (`Navigator.of(context).maybePop()`), or remove the `onTap` navigation.

### `pubspec.yaml`
- Remove the `assets:` entries for `assets/images/audience/` (lines ~82–88). The folder was deleted, and Flutter **fails to build** if a listed asset is missing.
- Remove the now-unused packages `file_picker`, `flutter_svg` and `google_fonts` (and the comment above `flutter_svg`). **Keep** `uuid` (used by notifications), and `firebase_ai` / `firebase_analytics` (earlier decision).
- Run `flutter pub get` to update `pubspec.lock`.

## B. Recommended text clean-up (not needed to compile)

- `lib/widgets/app_top_bar.dart` line 386: the rotating words `['Understand', 'Reason', 'Plan', 'Adapt']`. Change "Plan" (e.g. to "Forecast").
- `lib/widgets/dashboard/dashboard_top_bar.dart` line ~60: `_Pipeline('Plan')`. Change the pipeline words to forecasting steps.
- `lib/widgets/cta_footer.dart`: plan wording ("Living strategic planning…", "planning…"). Rewrite for forecasting.
- `lib/models/notification.dart`: `NotificationKind.planCreated/planUpdated/planDeleted` and `planId`. Nothing emits these any more; replace them with forecasting kinds when deadline alerts are built (Phase 2+). They can stay for now; the code compiles.

## C. Research workspace (`research/`)

- `research/pyproject.toml`: rename the package (e.g. `name = "reflica-forecast"`), update the description, and change `include = ["reflica_bench*"]` to the forecasting package (`["forecast", "forecast.pipeline*"]`) when the pipeline code is written (decision D8). The `csp` (`ortools`) extra was only for the old benchmark and can be removed.
- `research/pytest.ini`: `testpaths = tests` points to a folder that no longer exists. Keep it if forecasting tests will live in `research/tests/` (they will, per `MILESTONE_1.md`), or change it then.

## D. Checks on your Mac after the edits

```
flutter pub get
flutter analyze        # expect: No issues found
flutter test           # test/widget_test.dart (placeholder) should pass
flutter run -d chrome  # sign in → dashboard shows Home + Settings, welcome card, no plan items
```
Then send me the output of `flutter analyze` and `git diff` to review.
