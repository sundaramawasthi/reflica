import 'dart:math' as math;

import 'package:flutter/material.dart';

import '../theme/app_theme.dart';
import 'responsive.dart';

const _brandBlue = Color(0xFF2E6FEB);
const _brandViolet = Color(0xFF7A5BE8);

class LivingLoopSection extends StatelessWidget {
  const LivingLoopSection({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      color: AppColors.bg,
      padding: const EdgeInsets.symmetric(vertical: 96),
      child: PageWrap(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            _header(),
            const SizedBox(height: 48),
            const _LoopDiagram(),
            const SizedBox(height: 48),
            const _ValueProps(),
          ],
        ),
      ),
    );
  }

  Widget _header() {
    return Column(
      children: [
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
          decoration: BoxDecoration(
            color: _brandViolet.withValues(alpha: 0.08),
            borderRadius: BorderRadius.circular(999),
          ),
          child: Text(
            'HOW REFLICA STAYS ALIVE',
            style: AppText.mono(
              size: 10,
              color: _brandViolet,
            ).copyWith(letterSpacing: 1.5, fontWeight: FontWeight.w600),
          ),
        ),
        const SizedBox(height: 20),
        Text(
          'Plans that keep up with reality.',
          textAlign: TextAlign.center,
          style: AppText.serif(size: 42, weight: FontWeight.w600),
        ),
        const SizedBox(height: 16),
        ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 680),
          child: Text(
            'Static mind maps go stale the moment the world moves. Reflica binds '
            'every node to the real-world state behind it, so a new report '
            'propagates through dependencies, impacts become visible, and the '
            'strategy adapts in minutes — not weeks.',
            textAlign: TextAlign.center,
            style: AppText.body(size: 16, color: AppColors.ink2),
          ),
        ),
      ],
    );
  }
}

// -------- the loop visual --------

class _LoopDiagram extends StatelessWidget {
  const _LoopDiagram();

  @override
  Widget build(BuildContext context) {
    final isNarrow = screenSizeOf(context).index < ScreenSize.desktop.index;
    if (isNarrow) return const _LoopList();
    return const _LoopRing();
  }
}

class _LoopStep {
  final String id;
  final String label;
  final String sub;
  final IconData icon;
  final Color color;
  const _LoopStep(this.id, this.label, this.sub, this.icon, this.color);
}

const _steps = <_LoopStep>[
  _LoopStep('obs', 'Observe', 'A new report arrives from a person, a document, or a sensor.',
      Icons.visibility_outlined, AppColors.accent),
  _LoopStep('update', 'Update state', 'The relevant nodes gain new facts, timestamps and confidence.',
      Icons.auto_fix_normal, _brandViolet),
  _LoopStep('impact', 'Trace impact', 'Dependencies propagate — milestones, timelines and risks shift.',
      Icons.alt_route, AppColors.amber),
  _LoopStep('verify', 'Verify', 'Deterministic checks confirm the new state is consistent.',
      Icons.rule, AppColors.sage),
  _LoopStep('adapt', 'Adapt', 'Reflica repairs only the broken parts; the rest is preserved.',
      Icons.sync, _brandBlue),
  _LoopStep('render', 'Render', 'Mind map, dashboards and reports update in real time.',
      Icons.hub_outlined, AppColors.violet),
];

class _LoopRing extends StatelessWidget {
  const _LoopRing();

  @override
  Widget build(BuildContext context) {
    return ConstrainedBox(
      constraints: const BoxConstraints(maxWidth: 980, minHeight: 520),
      child: AspectRatio(
        aspectRatio: 16 / 9,
        child: LayoutBuilder(builder: (ctx, c) {
          final size = Size(c.maxWidth, c.maxHeight);
          final center = Offset(size.width / 2, size.height / 2);
          final radiusX = size.width * 0.38;
          final radiusY = size.height * 0.36;
          return Stack(
            children: [
              Positioned.fill(
                child: CustomPaint(
                  painter: _LoopRingPainter(
                    center: center,
                    radiusX: radiusX,
                    radiusY: radiusY,
                    steps: _steps.length,
                  ),
                ),
              ),
              for (int i = 0; i < _steps.length; i++) ..._place(i, center, radiusX, radiusY),
              Positioned(
                left: center.dx - 140,
                top: center.dy - 60,
                child: SizedBox(
                  width: 280,
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 5),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          border: Border.all(color: AppColors.line),
                          borderRadius: BorderRadius.circular(999),
                        ),
                        child: Text(
                          'THE LIVING LOOP',
                          style: AppText.mono(
                            size: 10,
                            color: AppColors.muted,
                          ).copyWith(letterSpacing: 1.2),
                        ),
                      ),
                      const SizedBox(height: 10),
                      Text(
                        'Reality changes.\nThe plan keeps up.',
                        textAlign: TextAlign.center,
                        style: AppText.serif(
                          size: 22,
                          weight: FontWeight.w500,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          );
        }),
      ),
    );
  }

  List<Widget> _place(int i, Offset center, double rx, double ry) {
    final n = _steps.length;
    // Start at the top (angle = -pi/2) and go clockwise.
    final angle = -math.pi / 2 + i * (2 * math.pi / n);
    final pos = Offset(
      center.dx + rx * math.cos(angle),
      center.dy + ry * math.sin(angle),
    );
    final step = _steps[i];
    return [
      Positioned(
        left: pos.dx - 110,
        top: pos.dy - 48,
        child: SizedBox(
          width: 220,
          child: _StepBubble(step: step, number: i + 1),
        ),
      ),
    ];
  }
}

class _LoopRingPainter extends CustomPainter {
  final Offset center;
  final double radiusX;
  final double radiusY;
  final int steps;
  _LoopRingPainter({
    required this.center,
    required this.radiusX,
    required this.radiusY,
    required this.steps,
  });

  @override
  void paint(Canvas canvas, Size size) {
    // Soft ambient halo behind the ring
    final halo = Paint()
      ..shader = RadialGradient(
        colors: [
          _brandBlue.withValues(alpha: 0.06),
          Colors.white.withValues(alpha: 0),
        ],
      ).createShader(Rect.fromCircle(center: center, radius: radiusX * 1.1));
    canvas.drawCircle(center, radiusX * 1.1, halo);

    // Dashed ellipse
    final paint = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1.2
      ..color = AppColors.lineStrong.withValues(alpha: 0.55);
    final rect = Rect.fromCenter(
      center: center,
      width: radiusX * 2,
      height: radiusY * 2,
    );
    final path = Path()..addOval(rect);
    for (final metric in path.computeMetrics()) {
      double d = 0;
      while (d < metric.length) {
        final next = (d + 6).clamp(0.0, metric.length);
        canvas.drawPath(metric.extractPath(d, next), paint);
        d = next + 6;
      }
    }

    // Six arrowheads around the ring to show flow direction
    for (int i = 0; i < steps; i++) {
      final a = -math.pi / 2 + (i + 0.5) * (2 * math.pi / steps);
      final tip = Offset(
        center.dx + radiusX * math.cos(a),
        center.dy + radiusY * math.sin(a),
      );
      final tangent = Offset(-math.sin(a) * radiusX, math.cos(a) * radiusY);
      final tLen = tangent.distance;
      final tn = tangent / tLen;
      final perp = Offset(-tn.dy, tn.dx);
      final back = tip - tn * 10;
      final head = Path()
        ..moveTo(tip.dx + tn.dx * 2, tip.dy + tn.dy * 2)
        ..lineTo(back.dx + perp.dx * 4, back.dy + perp.dy * 4)
        ..lineTo(back.dx - perp.dx * 4, back.dy - perp.dy * 4)
        ..close();
      canvas.drawPath(head, Paint()..color = _brandBlue.withValues(alpha: 0.5));
    }
  }

  @override
  bool shouldRepaint(covariant _LoopRingPainter old) =>
      old.center != center || old.radiusX != radiusX || old.radiusY != radiusY;
}

class _StepBubble extends StatefulWidget {
  final _LoopStep step;
  final int number;
  const _StepBubble({required this.step, required this.number});

  @override
  State<_StepBubble> createState() => _StepBubbleState();
}

class _StepBubbleState extends State<_StepBubble> {
  bool _hover = false;

  @override
  Widget build(BuildContext context) {
    final s = widget.step;
    return MouseRegion(
      cursor: SystemMouseCursors.help,
      onEnter: (_) => setState(() => _hover = true),
      onExit: (_) => setState(() => _hover = false),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 180),
        transform: Matrix4.translationValues(0, _hover ? -3 : 0, 0),
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: Colors.white,
          border: Border.all(
            color: _hover ? s.color : AppColors.line,
            width: _hover ? 1.5 : 1,
          ),
          borderRadius: BorderRadius.circular(14),
          boxShadow: [
            BoxShadow(
              color: _hover
                  ? s.color.withValues(alpha: 0.18)
                  : AppColors.ink.withValues(alpha: 0.05),
              blurRadius: _hover ? 20 : 10,
              offset: const Offset(0, 6),
              spreadRadius: -6,
            ),
          ],
        ),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              width: 36,
              height: 36,
              decoration: BoxDecoration(
                color: s.color.withValues(alpha: 0.12),
                shape: BoxShape.circle,
              ),
              alignment: Alignment.center,
              child: Icon(s.icon, color: s.color, size: 18),
            ),
            const SizedBox(width: 10),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: [
                  Row(
                    children: [
                      Text(
                        '0${widget.number}',
                        style: AppText.mono(
                          size: 10,
                          color: AppColors.muted,
                        ).copyWith(fontWeight: FontWeight.w600),
                      ),
                      const SizedBox(width: 6),
                      Flexible(
                        child: Text(
                          s.label,
                          style: AppText.serif(
                              size: 15, weight: FontWeight.w600),
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 2),
                  Text(
                    s.sub,
                    style: AppText.body(size: 11.5, color: AppColors.ink2)
                        .copyWith(height: 1.3),
                    maxLines: 3,
                    overflow: TextOverflow.ellipsis,
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _LoopList extends StatelessWidget {
  const _LoopList();

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        for (int i = 0; i < _steps.length; i++) ...[
          _StepBubble(step: _steps[i], number: i + 1),
          if (i < _steps.length - 1)
            Padding(
              padding: const EdgeInsets.symmetric(vertical: 10),
              child: Container(
                width: 2,
                height: 24,
                color: AppColors.lineStrong.withValues(alpha: 0.4),
              ),
            ),
        ],
      ],
    );
  }
}

// -------- supporting value props strip --------

class _ValueProps extends StatelessWidget {
  const _ValueProps();

  @override
  Widget build(BuildContext context) {
    const props = <_Prop>[
      _Prop('5', 'Evidence types tracked', 'Fact · Observation · Prediction · Hypothesis · Assumption',
          AppColors.sage),
      _Prop('6', 'Edge kinds in the graph', 'depends-on · blocks · enables · causes · requires · supports',
          _brandBlue),
      _Prop('100%', 'Audit trail', 'Every write — plan, node, edge, report — fires a notification you can trace',
          _brandViolet),
    ];
    return LayoutBuilder(builder: (ctx, c) {
      final tight = c.maxWidth < 820;
      return tight
          ? Column(children: props.map((p) => _PropTile(prop: p)).toList())
          : Row(
              children: props
                  .map((p) => Expanded(child: _PropTile(prop: p)))
                  .toList(),
            );
    });
  }
}

class _Prop {
  final String number;
  final String title;
  final String sub;
  final Color color;
  const _Prop(this.number, this.title, this.sub, this.color);
}

class _PropTile extends StatelessWidget {
  final _Prop prop;
  const _PropTile({required this.prop});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(10),
      child: Container(
        padding: const EdgeInsets.all(22),
        decoration: BoxDecoration(
          color: Colors.white,
          border: Border.all(color: AppColors.line),
          borderRadius: BorderRadius.circular(14),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              prop.number,
              style: AppText.serif(size: 36, weight: FontWeight.w500)
                  .copyWith(color: prop.color, height: 1),
            ),
            const SizedBox(height: 10),
            Text(prop.title,
                style: AppText.serif(size: 17, weight: FontWeight.w500)),
            const SizedBox(height: 6),
            Text(prop.sub,
                style: AppText.body(size: 13, color: AppColors.ink2)),
          ],
        ),
      ),
    );
  }
}
