import 'dart:math' as math;

import 'package:flutter/material.dart';

import '../../models/plan.dart';
import '../../screens/new_plan_flow.dart';
import '../../services/auth_service.dart';
import '../../theme/app_theme.dart';
import '../responsive.dart';

class WelcomeCard extends StatelessWidget {
  const WelcomeCard({super.key});

  @override
  Widget build(BuildContext context) {
    return StreamBuilder<AppUser?>(
      stream: AuthService.instance.authState,
      initialData: AuthService.instance.currentUser,
      builder: (context, snap) {
        final user = snap.data;
        final first = user?.displayName?.split(' ').first;
        return _buildCard(context, first);
      },
    );
  }

  Widget _buildCard(BuildContext context, String? first) {
    final isNarrow = screenSizeOf(context).index < ScreenSize.desktop.index;

    return Container(
      padding: EdgeInsets.all(isNarrow ? 24 : 36),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(24),
        gradient: const LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            Color(0xFFE4ECF2),
            Color(0xFFC5D4DF),
          ],
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          isNarrow
              ? Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    _copy(first),
                    const SizedBox(height: 24),
                    SizedBox(height: 180, child: _ConnectedNodesGraphic()),
                  ],
                )
              : Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Expanded(flex: 7, child: _copy(first)),
                    const SizedBox(width: 24),
                    Expanded(
                      flex: 6,
                      child: SizedBox(
                          height: 220, child: _ConnectedNodesGraphic()),
                    ),
                  ],
                ),
          const SizedBox(height: 28),
          _PromptBar(),
          const SizedBox(height: 16),
          _ExampleChips(),
        ],
      ),
    );
  }

  Widget _copy(String? first) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          first == null ? 'WELCOME TO REFLICA' : 'WELCOME BACK, ${first.toUpperCase()}',
          style: AppText.eyebrow().copyWith(color: AppColors.accent),
        ),
        const SizedBox(height: 12),
        Text(
          'Your AI Decision\nIntelligence Platform',
          style: AppText.serif(size: 36, weight: FontWeight.w400),
        ),
        const SizedBox(height: 14),
        Text(
          'Understand complex situations, track changing conditions, create '
          'reliable plans and adapt — with evidence, reasoning and human control.',
          style: AppText.body(size: 15, color: AppColors.ink2),
        ),
      ],
    );
  }
}

class _PromptBar extends StatefulWidget {
  @override
  State<_PromptBar> createState() => _PromptBarState();
}

class _PromptBarState extends State<_PromptBar> {
  final _ctrl = TextEditingController();

  @override
  void dispose() {
    _ctrl.dispose();
    super.dispose();
  }

  void _submit({InputMode mode = InputMode.text}) {
    final text = _ctrl.text.trim();
    Navigator.of(context).pushNamed(
      '/new-plan',
      arguments: NewPlanArgs(
        mode: mode,
        seedText: text.isEmpty ? null : text,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.fromLTRB(14, 10, 10, 10),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: AppColors.line),
      ),
      child: Row(
        children: [
          Container(
            width: 36,
            height: 36,
            decoration: BoxDecoration(
              color: AppColors.surface2,
              borderRadius: BorderRadius.circular(8),
            ),
            alignment: Alignment.center,
            child: Icon(Icons.short_text,
                size: 18, color: AppColors.muted),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: TextField(
              controller: _ctrl,
              onSubmitted: (_) => _submit(),
              textInputAction: TextInputAction.send,
              decoration: InputDecoration(
                border: InputBorder.none,
                hintText:
                    'Describe your situation, goal or upload a document...',
                hintStyle: AppText.body(size: 15, color: AppColors.muted),
                isCollapsed: true,
              ),
              style: AppText.body(size: 15, color: AppColors.ink),
            ),
          ),
          _AttachMenu(onPick: (mode) => _submit(mode: mode)),
          const SizedBox(width: 4),
          _StartButton(onTap: _submit),
        ],
      ),
    );
  }
}

class _AttachMenu extends StatelessWidget {
  final void Function(InputMode) onPick;
  const _AttachMenu({required this.onPick});

  @override
  Widget build(BuildContext context) {
    const picks = [
      InputMode.document,
      InputMode.image,
      InputMode.video,
      InputMode.voice,
      InputMode.camera,
      InputMode.form,
    ];
    return PopupMenuButton<InputMode>(
      tooltip: 'Choose another input mode',
      icon: Icon(Icons.attach_file, color: AppColors.muted),
      color: AppColors.surface,
      offset: const Offset(0, 44),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(10),
        side: const BorderSide(color: AppColors.line),
      ),
      onSelected: onPick,
      itemBuilder: (ctx) => picks
          .map(
            (m) => PopupMenuItem<InputMode>(
              value: m,
              child: Row(
                children: [
                  Icon(m.icon, size: 16, color: AppColors.accent),
                  const SizedBox(width: 10),
                  Text(m.label,
                      style: AppText.body(
                          size: 13.5, color: AppColors.ink)),
                ],
              ),
            ),
          )
          .toList(),
    );
  }
}

class _StartButton extends StatefulWidget {
  final VoidCallback onTap;
  const _StartButton({required this.onTap});

  @override
  State<_StartButton> createState() => _StartButtonState();
}

class _StartButtonState extends State<_StartButton> {
  bool _hover = false;

  @override
  Widget build(BuildContext context) {
    // Collapse to an icon-only arrow at narrow widths so the prompt bar never
    // overflows on phones. Breakpoint matches when the welcome card typically
    // starts to wrap its hero image column.
    final isTight = MediaQuery.sizeOf(context).width < 520;
    return MouseRegion(
      cursor: SystemMouseCursors.click,
      onEnter: (_) => setState(() => _hover = true),
      onExit: (_) => setState(() => _hover = false),
      child: GestureDetector(
        onTap: widget.onTap,
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 150),
          padding: EdgeInsets.symmetric(
            horizontal: isTight ? 10 : 18,
            vertical: isTight ? 10 : 12,
          ),
          decoration: BoxDecoration(
            color: _hover ? AppColors.accent2 : AppColors.accent,
            borderRadius: BorderRadius.circular(10),
          ),
          child: isTight
              ? Icon(Icons.arrow_forward, size: 18, color: Colors.white)
              : Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(
                      'Start Planning',
                      style: AppText.body(
                        size: 14,
                        weight: FontWeight.w500,
                        color: Colors.white,
                      ),
                    ),
                    const SizedBox(width: 6),
                    Icon(Icons.arrow_forward, size: 16, color: Colors.white),
                  ],
                ),
        ),
      ),
    );
  }
}

class _ExampleChips extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    const examples = [
      'Plan my exam preparation',
      'Evacuation plan for flood',
      'Project timeline for research',
      'Resource allocation for team',
    ];
    return Row(
      crossAxisAlignment: CrossAxisAlignment.center,
      children: [
        Text(
          'Try examples:',
          style: AppText.body(size: 13, color: AppColors.muted),
        ),
        const SizedBox(width: 10),
        Expanded(
          child: Wrap(
            spacing: 8,
            runSpacing: 8,
            children: examples.map((e) => _Chip(label: e)).toList(),
          ),
        ),
      ],
    );
  }
}

class _Chip extends StatefulWidget {
  final String label;
  const _Chip({required this.label});

  @override
  State<_Chip> createState() => _ChipState();
}

class _ChipState extends State<_Chip> {
  bool _hover = false;

  @override
  Widget build(BuildContext context) {
    return MouseRegion(
      cursor: SystemMouseCursors.click,
      onEnter: (_) => setState(() => _hover = true),
      onExit: (_) => setState(() => _hover = false),
      child: GestureDetector(
        onTap: () => Navigator.of(context).pushNamed('/new-plan'),
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 120),
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
          decoration: BoxDecoration(
            color: _hover ? AppColors.accent.withValues(alpha: 0.08) : AppColors.surface,
            border: Border.all(
              color: _hover ? AppColors.accent : AppColors.line,
            ),
            borderRadius: BorderRadius.circular(999),
          ),
          child: Text(
            widget.label,
            style: AppText.body(
              size: 12.5,
              color: _hover ? AppColors.accent : AppColors.ink2,
            ),
          ),
        ),
      ),
    );
  }
}

class _ConnectedNodesGraphic extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(builder: (context, c) {
      return CustomPaint(
        size: Size(c.maxWidth, c.maxHeight),
        painter: _NodesPainter(),
      );
    });
  }
}

class _NodesPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final w = size.width;
    final h = size.height;

    final nodes = [
      _Node(Offset(w * 0.20, h * 0.55), AppColors.violet, Icons.person_outline),
      _Node(Offset(w * 0.42, h * 0.25), AppColors.accent, Icons.group_outlined),
      _Node(Offset(w * 0.70, h * 0.20), AppColors.accent2, Icons.account_balance_outlined),
      _Node(Offset(w * 0.86, h * 0.45), AppColors.amber, Icons.warning_amber_outlined),
      _Node(Offset(w * 0.72, h * 0.75), AppColors.violet, Icons.calendar_today_outlined),
      _Node(Offset(w * 0.50, h * 0.80), AppColors.sage, Icons.business_outlined),
      _Node(Offset(w * 0.30, h * 0.85), AppColors.accent, Icons.schedule_outlined),
    ];

    // edges
    final edges = <(int, int, Color)>[
      (0, 1, AppColors.accent),
      (1, 2, AppColors.accent2),
      (1, 5, AppColors.sage),
      (2, 3, AppColors.amber),
      (3, 4, AppColors.violet),
      (5, 4, AppColors.accent),
      (5, 6, AppColors.accent),
      (0, 6, AppColors.violet),
      (1, 3, AppColors.lineStrong),
    ];

    for (final e in edges) {
      final a = nodes[e.$1].pos;
      final b = nodes[e.$2].pos;
      final paint = Paint()
        ..color = e.$3.withValues(alpha: 0.35)
        ..strokeWidth = 1
        ..style = PaintingStyle.stroke;
      canvas.drawLine(a, b, paint);
    }

    // decorative dots along edges
    final rng = math.Random(7);
    for (final e in edges) {
      final a = nodes[e.$1].pos;
      final b = nodes[e.$2].pos;
      for (int i = 0; i < 3; i++) {
        final t = rng.nextDouble();
        final p = Offset.lerp(a, b, t)!;
        canvas.drawCircle(
          p,
          1.2,
          Paint()..color = e.$3.withValues(alpha: 0.5),
        );
      }
    }

    for (final n in nodes) {
      canvas.drawCircle(
        n.pos,
        24,
        Paint()..color = Colors.white.withValues(alpha: 0.9),
      );
      canvas.drawCircle(
        n.pos,
        24,
        Paint()
          ..style = PaintingStyle.stroke
          ..strokeWidth = 1.4
          ..color = n.color.withValues(alpha: 0.6),
      );
      // draw an icon via TextPainter using the icon font
      final iconText = TextPainter(
        text: TextSpan(
          text: String.fromCharCode(n.icon.codePoint),
          style: TextStyle(
            fontFamily: n.icon.fontFamily,
            package: n.icon.fontPackage,
            fontSize: 18,
            color: n.color,
          ),
        ),
        textDirection: TextDirection.ltr,
      )..layout();
      iconText.paint(
        canvas,
        n.pos - Offset(iconText.width / 2, iconText.height / 2),
      );
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter old) => false;
}

class _Node {
  final Offset pos;
  final Color color;
  final IconData icon;
  _Node(this.pos, this.color, this.icon);
}
