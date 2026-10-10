import 'package:file_picker/file_picker.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';

import '../graph/graph1.dart';
import '../models/plan.dart';
import '../services/plan_repository.dart';
import '../services/reflica_api.dart';
import 'proposal_review_screen.dart';
import '../theme/app_theme.dart';
import '../widgets/dashboard/dashboard_sidebar.dart';
import '../widgets/responsive.dart';

/// Arguments the `/new-plan` route accepts. Any null field falls back to the
/// default wizard flow for that step.
class NewPlanArgs {
  final Audience? audience;
  final InputMode? mode;
  final String? seedText;
  const NewPlanArgs({this.audience, this.mode, this.seedText});
}

/// Multi-step wizard: Audience → Input mode → Content → Review.
class NewPlanFlow extends StatefulWidget {
  final NewPlanArgs? args;
  const NewPlanFlow({super.key, this.args});

  @override
  State<NewPlanFlow> createState() => _NewPlanFlowState();
}

class _NewPlanFlowState extends State<NewPlanFlow> {
  int _step = 0;
  Audience? _audience;
  InputMode? _mode;
  final _titleCtrl = TextEditingController();
  final _textCtrl = TextEditingController();
  final _formGoalCtrl = TextEditingController();
  final _formEntitiesCtrl = TextEditingController();
  final _formConstraintsCtrl = TextEditingController();
  final _formDeadlineCtrl = TextEditingController();
  final List<InputArtefact> _artefacts = [];
  bool _submitting = false;

  @override
  void initState() {
    super.initState();
    final a = widget.args;
    if (a != null) {
      _audience = a.audience;
      _mode = a.mode;
      if (a.seedText != null) {
        if (a.mode == InputMode.form) {
          _formGoalCtrl.text = a.seedText!;
        } else {
          _textCtrl.text = a.seedText!;
        }
      }
      // Skip to the first step the user hasn't satisfied yet.
      if (_audience != null && _mode != null) {
        _step = 2;
      } else if (_audience != null) {
        _step = 1;
      }
    }
  }

  @override
  void dispose() {
    _titleCtrl.dispose();
    _textCtrl.dispose();
    _formGoalCtrl.dispose();
    _formEntitiesCtrl.dispose();
    _formConstraintsCtrl.dispose();
    _formDeadlineCtrl.dispose();
    super.dispose();
  }

  bool get _canAdvance {
    switch (_step) {
      case 0:
        return _audience != null;
      case 1:
        return _mode != null;
      case 2:
        return _hasContent();
      case 3:
        return true;
    }
    return false;
  }

  bool _hasContent() {
    switch (_mode!) {
      case InputMode.text:
        return _textCtrl.text.trim().isNotEmpty;
      case InputMode.form:
        return _formGoalCtrl.text.trim().isNotEmpty;
      case InputMode.voice:
      case InputMode.document:
      case InputMode.image:
      case InputMode.video:
      case InputMode.camera:
        return _artefacts.isNotEmpty;
    }
  }

  @override
  Widget build(BuildContext context) {
    final showSidebar =
        screenSizeOf(context).index >= ScreenSize.desktop.index;

    return Scaffold(
      backgroundColor: AppColors.bg,
      drawer: showSidebar
          ? null
          : Drawer(
              backgroundColor: AppColors.surface,
              child: DashboardSidebar(
                selected: 1,
                onSelect: (i) {
                  Navigator.of(context).maybePop();
                  if (i == 0) {
                    Navigator.of(context)
                        .pushNamedAndRemoveUntil('/', (r) => false);
                  } else if (sidebarItems[i].route != '/new-plan') {
                    Navigator.of(context)
                        .pushReplacementNamed(sidebarItems[i].route);
                  }
                },
              ),
            ),
      body: SafeArea(
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (showSidebar)
              SizedBox(
                width: 240,
                child: DashboardSidebar(
                  selected: 1,
                  onSelect: (i) {
                    if (i == 0) {
                      Navigator.of(context)
                          .pushNamedAndRemoveUntil('/', (r) => false);
                    } else if (sidebarItems[i].route != '/new-plan') {
                      Navigator.of(context)
                          .pushReplacementNamed(sidebarItems[i].route);
                    }
                  },
                ),
              ),
            Expanded(
              child: Container(
                decoration: const BoxDecoration(
                  border: Border(left: BorderSide(color: AppColors.line)),
                ),
                child: Column(
                  children: [
                    _TopBar(showMenu: !showSidebar),
                    _ProgressStrip(step: _step),
                    Expanded(child: _buildStepBody()),
                    _BottomBar(
                      step: _step,
                      canAdvance: _canAdvance && !_submitting,
                      submitting: _submitting,
                      onBack: _step == 0
                          ? null
                          : () => setState(() => _step--),
                      onNext: () async {
                        if (_step < 3) {
                          setState(() => _step++);
                        } else {
                          await _submit();
                        }
                      },
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStepBody() {
    switch (_step) {
      case 0:
        return _AudiencePicker(
          selected: _audience,
          onSelect: (a) => setState(() => _audience = a),
        );
      case 1:
        return _InputPicker(
          selected: _mode,
          onSelect: (m) => setState(() => _mode = m),
        );
      case 2:
        return _ContentStep(
          mode: _mode!,
          textCtrl: _textCtrl,
          formGoalCtrl: _formGoalCtrl,
          formEntitiesCtrl: _formEntitiesCtrl,
          formConstraintsCtrl: _formConstraintsCtrl,
          formDeadlineCtrl: _formDeadlineCtrl,
          artefacts: _artefacts,
          onPick: _pickArtefacts,
          onRemove: (a) => setState(() => _artefacts.remove(a)),
          onContentChanged: () => setState(() {}),
        );
      case 3:
        return _ReviewStep(
          audience: _audience!,
          mode: _mode!,
          titleCtrl: _titleCtrl,
          textCtrl: _textCtrl,
          formGoalCtrl: _formGoalCtrl,
          formEntitiesCtrl: _formEntitiesCtrl,
          formConstraintsCtrl: _formConstraintsCtrl,
          formDeadlineCtrl: _formDeadlineCtrl,
          artefacts: _artefacts,
        );
    }
    return const SizedBox.shrink();
  }

  Future<void> _pickArtefacts() async {
    FileType type;
    List<String>? exts;
    switch (_mode!) {
      case InputMode.document:
        type = FileType.custom;
        exts = ['pdf', 'docx', 'doc', 'txt', 'csv', 'xlsx', 'md'];
        break;
      case InputMode.image:
      case InputMode.camera:
        type = FileType.image;
        break;
      case InputMode.video:
        type = FileType.video;
        break;
      case InputMode.voice:
        type = FileType.audio;
        break;
      default:
        type = FileType.any;
    }
    final result = await FilePicker.platform.pickFiles(
      type: type,
      allowedExtensions: exts,
      allowMultiple: _mode == InputMode.document || _mode == InputMode.image,
      withData: kIsWeb,
    );
    if (result == null) return;
    setState(() {
      for (final f in result.files) {
        _artefacts.add(InputArtefact(
          fileName: f.name,
          mimeType: _mimeFor(f.extension),
          bytes: f.size,
        ));
      }
    });
  }

  String _mimeFor(String? ext) {
    if (ext == null) return 'application/octet-stream';
    switch (ext.toLowerCase()) {
      case 'pdf':
        return 'application/pdf';
      case 'docx':
      case 'doc':
        return 'application/msword';
      case 'xlsx':
      case 'xls':
        return 'application/vnd.ms-excel';
      case 'csv':
        return 'text/csv';
      case 'txt':
      case 'md':
        return 'text/plain';
      case 'png':
        return 'image/png';
      case 'jpg':
      case 'jpeg':
        return 'image/jpeg';
      case 'mp4':
        return 'video/mp4';
      case 'mp3':
        return 'audio/mpeg';
      case 'wav':
        return 'audio/wav';
      case 'm4a':
        return 'audio/mp4';
      default:
        return 'application/octet-stream';
    }
  }

  Future<void> _submit() async {
    setState(() => _submitting = true);
    try {
      String? rawText;
      if (_mode == InputMode.text) {
        rawText = _textCtrl.text.trim();
      } else if (_mode == InputMode.form) {
        rawText = _composeFormAsText();
      }
      GraphUpdate? accepted;
      if (rawText != null && rawText.isNotEmpty) {
        final (update, proceed) = await _extractAndReview(rawText);
        if (!proceed) {
          if (mounted) setState(() => _submitting = false);
          return;
        }
        accepted = update;
      }
      final plan = await PlanRepository.instance.createPlan(
        title: _titleCtrl.text.trim(),
        audience: _audience!,
        inputMode: _mode!,
        rawText: rawText,
        artefacts: List.unmodifiable(_artefacts),
        accepted: accepted,
      );
      if (!mounted) return;
      Navigator.of(context).pushReplacementNamed('/plan', arguments: plan.id);
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Could not create plan: $e')),
      );
      setState(() => _submitting = false);
    }
  }

  /// Text -> proposal (service) -> researcher review. Returns the accepted
  /// graph, or (null, true) to continue with an empty graph when extraction is
  /// unavailable and the researcher chooses to, or (null, false) to stay here.
  Future<(GraphUpdate?, bool)> _extractAndReview(String text) async {
    final api = ReflicaApi.instance;
    final title = _titleCtrl.text.trim();
    ExtractionProposalView proposal;
    try {
      proposal = await api.extract(text, title: title.isEmpty ? 'Research problem' : title);
    } on ReflicaApiException catch (e) {
      if (!mounted) return (null, false);
      final empty = await showDialog<bool>(
        context: context,
        builder: (ctx) => AlertDialog(
          title: const Text('Automatic graph extraction is unavailable'),
          content: Text('${e.message}\n\nYou can create the plan with an empty graph and '
              'add items later, or go back.'),
          actions: [
            TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Go back')),
            FilledButton(
                key: const ValueKey('create-empty'),
                onPressed: () => Navigator.pop(ctx, true),
                child: const Text('Create with empty graph')),
          ],
        ),
      );
      return (null, empty == true);
    }
    if (!mounted) return (null, false);
    final update = await Navigator.of(context).push<GraphUpdate>(MaterialPageRoute(
      builder: (_) => ProposalReviewScreen(
          proposal: proposal, api: api, decidedBy: PlanRepository.instance.actorId),
    ));
    return (update, update != null);
  }

  String _composeFormAsText() {
    final goal = _formGoalCtrl.text.trim();
    final entities = _formEntitiesCtrl.text.trim();
    final constraints = _formConstraintsCtrl.text.trim();
    final deadline = _formDeadlineCtrl.text.trim();
    return [
      if (goal.isNotEmpty) 'Goal: $goal',
      if (entities.isNotEmpty) 'Entities / resources: $entities',
      if (constraints.isNotEmpty) 'Constraints: $constraints',
      if (deadline.isNotEmpty) 'Deadline: $deadline',
    ].join('\n');
  }
}

// -------- top bar + progress --------

class _TopBar extends StatelessWidget {
  final bool showMenu;
  const _TopBar({required this.showMenu});

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 72,
      padding: const EdgeInsets.symmetric(horizontal: 20),
      decoration: const BoxDecoration(
        border: Border(bottom: BorderSide(color: AppColors.line)),
      ),
      child: Row(
        children: [
          if (showMenu)
            Builder(
              builder: (ctx) => IconButton(
                icon: const Icon(Icons.menu),
                color: AppColors.ink2,
                onPressed: () => Scaffold.of(ctx).openDrawer(),
              ),
            ),
          IconButton(
            icon: const Icon(Icons.close),
            color: AppColors.ink2,
            onPressed: () => Navigator.of(context)
                .pushNamedAndRemoveUntil('/', (r) => false),
          ),
          const SizedBox(width: 6),
          Icon(Icons.auto_awesome, size: 18, color: AppColors.accent),
          const SizedBox(width: 8),
          Text('New Plan',
              style: AppText.serif(size: 20, weight: FontWeight.w500)),
        ],
      ),
    );
  }
}

class _ProgressStrip extends StatelessWidget {
  final int step;
  const _ProgressStrip({required this.step});

  @override
  Widget build(BuildContext context) {
    const labels = ['For', 'How', 'Content', 'Review'];
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
      decoration: const BoxDecoration(
        border: Border(bottom: BorderSide(color: AppColors.line)),
      ),
      child: Row(
        children: List.generate(labels.length, (i) {
          final active = i <= step;
          final isCurrent = i == step;
          return Expanded(
            child: Row(
              children: [
                Container(
                  width: 28,
                  height: 28,
                  decoration: BoxDecoration(
                    color: active ? AppColors.accent : AppColors.surface2,
                    shape: BoxShape.circle,
                    border: Border.all(
                      color: isCurrent
                          ? AppColors.accent
                          : (active ? AppColors.accent : AppColors.line),
                      width: 1.5,
                    ),
                  ),
                  alignment: Alignment.center,
                  child: i < step
                      ? const Icon(Icons.check,
                          size: 14, color: Colors.white)
                      : Text(
                          '${i + 1}',
                          style: AppText.mono(
                            size: 11,
                            color: active ? Colors.white : AppColors.muted,
                            weight: FontWeight.w600,
                          ),
                        ),
                ),
                const SizedBox(width: 8),
                Flexible(
                  child: Text(
                    labels[i],
                    style: AppText.body(
                      size: 13,
                      weight: isCurrent ? FontWeight.w600 : FontWeight.w500,
                      color: active ? AppColors.ink : AppColors.muted,
                    ),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
                if (i < labels.length - 1)
                  Expanded(
                    child: Container(
                      margin: const EdgeInsets.symmetric(horizontal: 8),
                      height: 1.5,
                      color: i < step ? AppColors.accent : AppColors.line,
                    ),
                  ),
              ],
            ),
          );
        }),
      ),
    );
  }
}

class _BottomBar extends StatelessWidget {
  final int step;
  final bool canAdvance;
  final bool submitting;
  final VoidCallback? onBack;
  final VoidCallback onNext;
  const _BottomBar({
    required this.step,
    required this.canAdvance,
    required this.submitting,
    required this.onBack,
    required this.onNext,
  });

  @override
  Widget build(BuildContext context) {
    final isLast = step == 3;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
      decoration: const BoxDecoration(
        border: Border(top: BorderSide(color: AppColors.line)),
      ),
      child: Row(
        children: [
          if (onBack != null)
            OutlinedButton.icon(
              onPressed: submitting ? null : onBack,
              icon: const Icon(Icons.arrow_back, size: 16),
              label: const Text('Back'),
              style: OutlinedButton.styleFrom(
                side: const BorderSide(color: AppColors.lineStrong),
                foregroundColor: AppColors.ink,
                padding:
                    const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(999),
                ),
              ),
            ),
          const Spacer(),
          ElevatedButton.icon(
            onPressed: canAdvance ? onNext : null,
            icon: submitting
                ? const SizedBox(
                    width: 14,
                    height: 14,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                      valueColor: AlwaysStoppedAnimation(Colors.white),
                    ),
                  )
                : Icon(isLast ? Icons.auto_awesome : Icons.arrow_forward,
                    size: 18, color: Colors.white),
            label: Text(
              isLast ? 'Create plan' : 'Continue',
              style: AppText.body(
                size: 14,
                weight: FontWeight.w600,
                color: Colors.white,
              ),
            ),
            style: ElevatedButton.styleFrom(
              backgroundColor: AppColors.accent,
              padding:
                  const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(999),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

// -------- step 1: audience --------

class _AudiencePicker extends StatelessWidget {
  final Audience? selected;
  final ValueChanged<Audience> onSelect;
  const _AudiencePicker({required this.selected, required this.onSelect});

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 920),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Who is this plan for?',
                style: AppText.serif(size: 28, weight: FontWeight.w500),
              ),
              const SizedBox(height: 8),
              Text(
                'Reflica tunes the templates, defaults and visibility '
                'rules to the kind of user you represent.',
                style: AppText.body(size: 15, color: AppColors.ink2),
              ),
              const SizedBox(height: 28),
              Wrap(
                spacing: 14,
                runSpacing: 14,
                children: Audience.values
                    .map((a) => _OptionCard(
                          width: 280,
                          icon: a.icon,
                          title: a.label,
                          selected: selected == a,
                          onTap: () => onSelect(a),
                        ))
                    .toList(),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// -------- step 2: input mode --------

class _InputPicker extends StatelessWidget {
  final InputMode? selected;
  final ValueChanged<InputMode> onSelect;
  const _InputPicker({required this.selected, required this.onSelect});

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 920),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'How do you want to give the input?',
                style: AppText.serif(size: 28, weight: FontWeight.w500),
              ),
              const SizedBox(height: 8),
              Text(
                'Everything becomes typed facts in the same graph. Pick '
                'whichever is most natural — mix later from the plan page.',
                style: AppText.body(size: 15, color: AppColors.ink2),
              ),
              const SizedBox(height: 28),
              Wrap(
                spacing: 14,
                runSpacing: 14,
                children: InputMode.values
                    .map((m) => _OptionCard(
                          width: 280,
                          icon: m.icon,
                          title: m.label,
                          subtitle: m.hint,
                          selected: selected == m,
                          onTap: () => onSelect(m),
                        ))
                    .toList(),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _OptionCard extends StatefulWidget {
  final double width;
  final IconData icon;
  final String title;
  final String? subtitle;
  final bool selected;
  final VoidCallback onTap;
  const _OptionCard({
    required this.width,
    required this.icon,
    required this.title,
    this.subtitle,
    required this.selected,
    required this.onTap,
  });

  @override
  State<_OptionCard> createState() => _OptionCardState();
}

class _OptionCardState extends State<_OptionCard> {
  bool _hover = false;

  @override
  Widget build(BuildContext context) {
    final highlight = widget.selected || _hover;
    return MouseRegion(
      cursor: SystemMouseCursors.click,
      onEnter: (_) => setState(() => _hover = true),
      onExit: (_) => setState(() => _hover = false),
      child: GestureDetector(
        onTap: widget.onTap,
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 150),
          width: widget.width,
          padding: const EdgeInsets.all(18),
          decoration: BoxDecoration(
            color: widget.selected
                ? AppColors.accent.withValues(alpha: 0.06)
                : AppColors.surface,
            border: Border.all(
              color: highlight ? AppColors.accent : AppColors.line,
              width: widget.selected ? 2 : 1,
            ),
            borderRadius: BorderRadius.circular(14),
          ),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                width: 42,
                height: 42,
                decoration: BoxDecoration(
                  color: AppColors.accent.withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(10),
                ),
                alignment: Alignment.center,
                child: Icon(widget.icon,
                    color: AppColors.accent, size: 22),
              ),
              const SizedBox(width: 14),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Row(
                      children: [
                        Expanded(
                          child: Text(
                            widget.title,
                            style: AppText.serif(
                                size: 16, weight: FontWeight.w500),
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                        if (widget.selected)
                          Icon(Icons.check_circle,
                              color: AppColors.accent, size: 18),
                      ],
                    ),
                    if (widget.subtitle != null) ...[
                      const SizedBox(height: 4),
                      Text(
                        widget.subtitle!,
                        style:
                            AppText.body(size: 12, color: AppColors.ink2),
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ],
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// -------- step 3: content --------

class _ContentStep extends StatelessWidget {
  final InputMode mode;
  final TextEditingController textCtrl;
  final TextEditingController formGoalCtrl;
  final TextEditingController formEntitiesCtrl;
  final TextEditingController formConstraintsCtrl;
  final TextEditingController formDeadlineCtrl;
  final List<InputArtefact> artefacts;
  final Future<void> Function() onPick;
  final ValueChanged<InputArtefact> onRemove;
  final VoidCallback onContentChanged;
  const _ContentStep({
    required this.mode,
    required this.textCtrl,
    required this.formGoalCtrl,
    required this.formEntitiesCtrl,
    required this.formConstraintsCtrl,
    required this.formDeadlineCtrl,
    required this.artefacts,
    required this.onPick,
    required this.onRemove,
    required this.onContentChanged,
  });

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 760),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Icon(mode.icon, color: AppColors.accent, size: 22),
                  const SizedBox(width: 10),
                  Text(mode.label,
                      style: AppText.serif(
                          size: 24, weight: FontWeight.w500)),
                ],
              ),
              const SizedBox(height: 6),
              Text(mode.hint,
                  style:
                      AppText.body(size: 14, color: AppColors.ink2)),
              const SizedBox(height: 20),
              _body(),
            ],
          ),
        ),
      ),
    );
  }

  Widget _body() {
    switch (mode) {
      case InputMode.text:
        return _textField();
      case InputMode.form:
        return _formFields();
      case InputMode.voice:
      case InputMode.document:
      case InputMode.image:
      case InputMode.video:
      case InputMode.camera:
        return _artefactPicker();
    }
  }

  Widget _textField() {
    return Container(
      decoration: BoxDecoration(
        color: AppColors.surface,
        border: Border.all(color: AppColors.line),
        borderRadius: BorderRadius.circular(12),
      ),
      padding: const EdgeInsets.all(14),
      child: TextField(
        controller: textCtrl,
        minLines: 10,
        maxLines: 20,
        onChanged: (_) => onContentChanged(),
        decoration: InputDecoration(
          border: InputBorder.none,
          hintText:
              'Describe the situation, goal, people involved, resources '
              'available, any deadlines or constraints...',
          hintStyle: AppText.body(size: 14, color: AppColors.muted),
        ),
        style: AppText.body(size: 15, color: AppColors.ink),
      ),
    );
  }

  Widget _formFields() {
    Widget field(String label, TextEditingController ctrl,
        {String? hint, int minLines = 1, int maxLines = 3}) {
      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(label.toUpperCase(), style: AppText.eyebrow()),
          const SizedBox(height: 6),
          Container(
            decoration: BoxDecoration(
              color: AppColors.surface,
              border: Border.all(color: AppColors.line),
              borderRadius: BorderRadius.circular(10),
            ),
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
            child: TextField(
              controller: ctrl,
              minLines: minLines,
              maxLines: maxLines,
              onChanged: (_) => onContentChanged(),
              decoration: InputDecoration(
                border: InputBorder.none,
                hintText: hint,
                hintStyle:
                    AppText.body(size: 13, color: AppColors.muted),
                isCollapsed: true,
              ),
              style: AppText.body(size: 14, color: AppColors.ink),
            ),
          ),
          const SizedBox(height: 18),
        ],
      );
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        field('Goal', formGoalCtrl,
            hint: 'e.g. Evacuate 40 people to Shelter A before 18:00'),
        field('Entities / resources', formEntitiesCtrl,
            hint: '2 trucks (T1, T2), Shelter A (50 beds), 40 people'),
        field('Constraints', formConstraintsCtrl,
            hint: 'Deadline, capacity, geography, legal, financial…',
            maxLines: 4),
        field('Deadline', formDeadlineCtrl,
            hint: '2026-11-30, before 18:00, within 2 weeks'),
      ],
    );
  }

  Widget _artefactPicker() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        InkWell(
          onTap: onPick,
          borderRadius: BorderRadius.circular(14),
          child: Container(
            padding: const EdgeInsets.all(28),
            decoration: BoxDecoration(
              color: AppColors.surface,
              border: Border.all(
                color: AppColors.accent.withValues(alpha: 0.4),
                style: BorderStyle.solid,
                width: 2,
              ),
              borderRadius: BorderRadius.circular(14),
            ),
            child: Column(
              children: [
                Container(
                  width: 56,
                  height: 56,
                  decoration: BoxDecoration(
                    color: AppColors.accent.withValues(alpha: 0.12),
                    shape: BoxShape.circle,
                  ),
                  alignment: Alignment.center,
                  child: Icon(mode.icon,
                      color: AppColors.accent, size: 28),
                ),
                const SizedBox(height: 14),
                Text(_pickCta(),
                    style: AppText.serif(
                        size: 18, weight: FontWeight.w500)),
                const SizedBox(height: 6),
                Text(_pickHint(),
                    textAlign: TextAlign.center,
                    style:
                        AppText.body(size: 13, color: AppColors.ink2)),
                const SizedBox(height: 14),
                ElevatedButton.icon(
                  onPressed: onPick,
                  icon: const Icon(Icons.upload_file,
                      size: 18, color: Colors.white),
                  label: Text(
                    'Choose ${_pickNoun()}',
                    style: AppText.body(
                        size: 13,
                        weight: FontWeight.w600,
                        color: Colors.white),
                  ),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppColors.accent,
                    padding: const EdgeInsets.symmetric(
                        horizontal: 18, vertical: 12),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(999),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
        if (mode == InputMode.camera || mode == InputMode.voice) ...[
          const SizedBox(height: 12),
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: AppColors.amber.withValues(alpha: 0.08),
              border: Border.all(
                color: AppColors.amber.withValues(alpha: 0.3),
              ),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Row(
              children: [
                Icon(Icons.info_outline,
                    size: 16, color: AppColors.amber),
                const SizedBox(width: 10),
                Expanded(
                  child: Text(
                    mode == InputMode.camera
                        ? 'Live camera capture is wired on mobile. On web, '
                            'this picker accepts images (also from camera roll).'
                        : 'In-app voice recording is wired on mobile. On web, '
                            'upload a recorded audio clip.',
                    style:
                        AppText.body(size: 12, color: AppColors.ink2),
                  ),
                ),
              ],
            ),
          ),
        ],
        if (artefacts.isNotEmpty) ...[
          const SizedBox(height: 20),
          Text('ATTACHED', style: AppText.eyebrow()),
          const SizedBox(height: 10),
          ...artefacts.map((a) => _ArtefactRow(
                artefact: a,
                onRemove: () => onRemove(a),
              )),
        ],
      ],
    );
  }

  String _pickCta() {
    switch (mode) {
      case InputMode.document:
        return 'Upload documents';
      case InputMode.image:
        return 'Upload images';
      case InputMode.video:
        return 'Upload a video';
      case InputMode.voice:
        return 'Upload a voice clip';
      case InputMode.camera:
        return 'Capture or upload';
      default:
        return 'Upload';
    }
  }

  String _pickHint() {
    switch (mode) {
      case InputMode.document:
        return 'PDF, DOCX, DOC, TXT, CSV, XLSX, MD — multiple allowed.';
      case InputMode.image:
        return 'PNG, JPG — photos, scans, satellite tiles.';
      case InputMode.video:
        return 'MP4 and similar — brief clips of the situation.';
      case InputMode.voice:
        return 'MP3, WAV, M4A — spoken briefs or recordings.';
      case InputMode.camera:
        return 'Capture live or pick from the camera roll.';
      default:
        return '';
    }
  }

  String _pickNoun() {
    switch (mode) {
      case InputMode.document:
        return 'files';
      case InputMode.image:
        return 'images';
      case InputMode.video:
        return 'video';
      case InputMode.voice:
        return 'audio';
      case InputMode.camera:
        return 'photo';
      default:
        return 'file';
    }
  }
}

class _ArtefactRow extends StatelessWidget {
  final InputArtefact artefact;
  final VoidCallback onRemove;
  const _ArtefactRow({required this.artefact, required this.onRemove});

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
      decoration: BoxDecoration(
        color: AppColors.surface,
        border: Border.all(color: AppColors.line),
        borderRadius: BorderRadius.circular(10),
      ),
      child: Row(
        children: [
          Container(
            width: 32,
            height: 32,
            decoration: BoxDecoration(
              color: AppColors.accent.withValues(alpha: 0.1),
              borderRadius: BorderRadius.circular(6),
            ),
            alignment: Alignment.center,
            child: Icon(_iconFor(artefact.mimeType),
                color: AppColors.accent, size: 16),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  artefact.fileName,
                  style: AppText.body(
                      size: 14,
                      weight: FontWeight.w500,
                      color: AppColors.ink),
                  overflow: TextOverflow.ellipsis,
                ),
                Text(
                  '${artefact.mimeType} · ${_prettyBytes(artefact.bytes)}',
                  style: AppText.mono(size: 11),
                ),
              ],
            ),
          ),
          IconButton(
            icon: Icon(Icons.close, size: 16, color: AppColors.muted),
            onPressed: onRemove,
          ),
        ],
      ),
    );
  }

  IconData _iconFor(String mime) {
    if (mime.startsWith('image/')) return Icons.image_outlined;
    if (mime.startsWith('video/')) return Icons.videocam_outlined;
    if (mime.startsWith('audio/')) return Icons.mic_none;
    if (mime == 'application/pdf') return Icons.picture_as_pdf_outlined;
    if (mime.contains('spreadsheet') || mime.contains('csv')) {
      return Icons.table_chart_outlined;
    }
    return Icons.description_outlined;
  }

  String _prettyBytes(int bytes) {
    if (bytes < 1024) return '$bytes B';
    if (bytes < 1024 * 1024) return '${(bytes / 1024).toStringAsFixed(1)} KB';
    return '${(bytes / (1024 * 1024)).toStringAsFixed(1)} MB';
  }
}

// -------- step 4: review --------

class _ReviewStep extends StatelessWidget {
  final Audience audience;
  final InputMode mode;
  final TextEditingController titleCtrl;
  final TextEditingController textCtrl;
  final TextEditingController formGoalCtrl;
  final TextEditingController formEntitiesCtrl;
  final TextEditingController formConstraintsCtrl;
  final TextEditingController formDeadlineCtrl;
  final List<InputArtefact> artefacts;
  const _ReviewStep({
    required this.audience,
    required this.mode,
    required this.titleCtrl,
    required this.textCtrl,
    required this.formGoalCtrl,
    required this.formEntitiesCtrl,
    required this.formConstraintsCtrl,
    required this.formDeadlineCtrl,
    required this.artefacts,
  });

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 760),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('Review and name your plan',
                  style:
                      AppText.serif(size: 28, weight: FontWeight.w500)),
              const SizedBox(height: 20),
              Container(
                decoration: BoxDecoration(
                  color: AppColors.surface,
                  border: Border.all(color: AppColors.line),
                  borderRadius: BorderRadius.circular(12),
                ),
                padding: const EdgeInsets.all(14),
                child: TextField(
                  controller: titleCtrl,
                  decoration: InputDecoration(
                    border: InputBorder.none,
                    hintText: 'Plan title (optional — we will derive one)',
                    hintStyle:
                        AppText.body(size: 15, color: AppColors.muted),
                  ),
                  style: AppText.body(
                    size: 18,
                    color: AppColors.ink,
                    weight: FontWeight.w500,
                  ),
                ),
              ),
              const SizedBox(height: 20),
              _Summary(
                audience: audience,
                mode: mode,
                content: _contentSummary(),
                artefacts: artefacts,
              ),
            ],
          ),
        ),
      ),
    );
  }

  String? _contentSummary() {
    if (mode == InputMode.text) return textCtrl.text.trim();
    if (mode == InputMode.form) {
      final parts = <String>[];
      if (formGoalCtrl.text.trim().isNotEmpty) {
        parts.add('Goal: ${formGoalCtrl.text.trim()}');
      }
      if (formEntitiesCtrl.text.trim().isNotEmpty) {
        parts.add('Entities: ${formEntitiesCtrl.text.trim()}');
      }
      if (formConstraintsCtrl.text.trim().isNotEmpty) {
        parts.add('Constraints: ${formConstraintsCtrl.text.trim()}');
      }
      if (formDeadlineCtrl.text.trim().isNotEmpty) {
        parts.add('Deadline: ${formDeadlineCtrl.text.trim()}');
      }
      return parts.join('\n');
    }
    return null;
  }
}

class _Summary extends StatelessWidget {
  final Audience audience;
  final InputMode mode;
  final String? content;
  final List<InputArtefact> artefacts;
  const _Summary({
    required this.audience,
    required this.mode,
    required this.content,
    required this.artefacts,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.surface2,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _row(audience.icon, 'For', audience.label),
          const SizedBox(height: 10),
          _row(mode.icon, 'Input mode', mode.label),
          if (content != null && content!.isNotEmpty) ...[
            const SizedBox(height: 14),
            Text('CONTENT', style: AppText.eyebrow()),
            const SizedBox(height: 6),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.white,
                border: Border.all(color: AppColors.line),
                borderRadius: BorderRadius.circular(10),
              ),
              child: Text(content!,
                  style: AppText.body(size: 13, color: AppColors.ink2)),
            ),
          ],
          if (artefacts.isNotEmpty) ...[
            const SizedBox(height: 14),
            Text('ATTACHMENTS', style: AppText.eyebrow()),
            const SizedBox(height: 6),
            ...artefacts.map((a) => Padding(
                  padding: const EdgeInsets.only(bottom: 4),
                  child: Row(
                    children: [
                      Icon(Icons.attach_file,
                          size: 14, color: AppColors.muted),
                      const SizedBox(width: 6),
                      Expanded(
                        child: Text(
                          a.fileName,
                          style: AppText.mono(
                              size: 12, color: AppColors.ink2),
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                    ],
                  ),
                )),
          ],
        ],
      ),
    );
  }

  Widget _row(IconData icon, String label, String value) {
    return Row(
      children: [
        Icon(icon, size: 16, color: AppColors.muted),
        const SizedBox(width: 10),
        Text('$label: ',
            style:
                AppText.mono(size: 11, color: AppColors.muted)),
        Text(value,
            style: AppText.body(
              size: 14,
              color: AppColors.ink,
              weight: FontWeight.w500,
            )),
      ],
    );
  }
}
