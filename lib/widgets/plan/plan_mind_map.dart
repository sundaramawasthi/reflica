import 'dart:math' as math;

import 'package:flutter/material.dart';

import '../../models/plan.dart';
import '../../theme/app_theme.dart';

/// Reflica's mind-map view of a Plan's cognitive graph.
/// Pan + pinch-zoom; nodes colored by evidence type.
class PlanMindMap extends StatefulWidget {
  final Plan plan;
  final EdgeInsets padding;
  const PlanMindMap({
    super.key,
    required this.plan,
    this.padding = const EdgeInsets.all(24),
  });

  @override
  State<PlanMindMap> createState() => _PlanMindMapState();
}

class _PlanMindMapState extends State<PlanMindMap> {
  final _tc = TransformationController();

  @override
  void dispose() {
    _tc.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(builder: (context, c) {
      return ClipRRect(
        borderRadius: BorderRadius.circular(16),
        child: Container(
          decoration: BoxDecoration(
            color: const Color(0xFFF6F8FC),
            border: Border.all(color: AppColors.line),
            borderRadius: BorderRadius.circular(16),
          ),
          child: Stack(
            children: [
              Positioned.fill(
                child: InteractiveViewer(
                  transformationController: _tc,
                  minScale: 0.4,
                  maxScale: 3.0,
                  boundaryMargin: const EdgeInsets.all(120),
                  child: Padding(
                    padding: widget.padding,
                    child: CustomPaint(
                      size: Size(c.maxWidth, c.maxHeight),
                      painter: _MindMapPainter(plan: widget.plan),
                    ),
                  ),
                ),
              ),
              Positioned(
                right: 12,
                bottom: 12,
                child: _Legend(),
              ),
              Positioned(
                right: 12,
                top: 12,
                child: _ZoomControls(controller: _tc),
              ),
            ],
          ),
        ),
      );
    });
  }
}

class _MindMapPainter extends CustomPainter {
  final Plan plan;
  _MindMapPainter({required this.plan});

  // Scale knobs computed per paint so the map stays readable on both a 320 px
  // phone and a 1600 px desktop.
  late double _scale;
  late bool _tight;

  @override
  void paint(Canvas canvas, Size size) {
    // Reference width ≈ 640 px. Below that, shrink linearly; above, cap at 1.
    _scale = (size.width / 640).clamp(0.55, 1.0);
    _tight = size.width < 420;

    // Map normalised 0..1 positions into the canvas.
    Offset posOf(PlanNode n) =>
        Offset(n.x * size.width, n.y * size.height);

    // Edges first so they sit under the nodes.
    for (final e in plan.edges) {
      final a = plan.nodes.firstWhere((n) => n.id == e.fromId,
          orElse: () => plan.nodes.first);
      final b = plan.nodes.firstWhere((n) => n.id == e.toId,
          orElse: () => plan.nodes.first);
      _drawEdge(canvas, posOf(a), posOf(b), e.kind);
    }

    for (final n in plan.nodes) {
      _drawNode(canvas, posOf(n), n);
    }
  }

  void _drawEdge(Canvas canvas, Offset a, Offset b, EdgeKind kind) {
    final color = _edgeColor(kind);
    final paint = Paint()
      ..color = color.withValues(alpha: 0.55)
      ..strokeWidth = 1.4
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round;

    final mid = Offset((a.dx + b.dx) / 2, (a.dy + b.dy) / 2 - 24);
    final path = Path()
      ..moveTo(a.dx, a.dy)
      ..quadraticBezierTo(mid.dx, mid.dy, b.dx, b.dy);
    canvas.drawPath(path, paint);

    // Arrow head
    final dir = b - a;
    final len = dir.distance;
    if (len > 0) {
      final norm = dir / len;
      final tip = b - norm * 22;
      final perp = Offset(-norm.dy, norm.dx);
      final left = tip + perp * 5;
      final right = tip - perp * 5;
      final head = Path()
        ..moveTo(b.dx - norm.dx * 10, b.dy - norm.dy * 10)
        ..lineTo(left.dx, left.dy)
        ..lineTo(right.dx, right.dy)
        ..close();
      canvas.drawPath(head, Paint()..color = color);
    }

    // Edge-kind label midway — only on roomier canvases. On narrow screens
    // these collide with the node labels and look like noise.
    if (!_tight) {
      _drawLabel(
        canvas,
        _edgeLabel(kind),
        Offset(mid.dx, mid.dy - 2),
        style: TextStyle(
          fontSize: 9 * _scale.clamp(0.75, 1.0),
          color: color,
          fontWeight: FontWeight.w500,
          letterSpacing: 0.5,
        ),
        backgroundColor: Colors.white.withValues(alpha: 0.92),
      );
    }
  }

  void _drawNode(Canvas canvas, Offset pos, PlanNode n) {
    final color = _nodeColor(n.type);
    final baseRadius = (n.id == 'goal' ? 36.0 : 28.0) * _scale;
    final radius = baseRadius.clamp(16.0, 36.0);

    // Soft halo
    canvas.drawCircle(
      pos,
      radius + 10,
      Paint()..color = color.withValues(alpha: 0.12),
    );
    // Node body
    canvas.drawCircle(pos, radius, Paint()..color = Colors.white);
    canvas.drawCircle(
      pos,
      radius,
      Paint()
        ..style = PaintingStyle.stroke
        ..strokeWidth = 2.2
        ..color = color,
    );

    // Label inside / around. Tighter line length + smaller font on narrow
    // canvases so a goal like "I am doing M.Tech in Computer Science" doesn't
    // smear across the whole map.
    final maxChars = _tight ? 10 : 14;
    final maxLines = _tight ? 2 : 2;
    final labelLines =
        _wrapLabel(n.label, maxCharsPerLine: maxChars, maxLines: maxLines);
    final labelFontSize =
        ((n.id == 'goal' ? 12.0 : 11.0) * _scale).clamp(9.5, 12.0);
    _drawMultilineText(
      canvas,
      labelLines,
      pos,
      style: TextStyle(
        fontSize: labelFontSize,
        color: AppColors.ink,
        fontWeight: FontWeight.w600,
        height: 1.15,
      ),
    );

    if (n.subLabel != null && n.subLabel!.isNotEmpty && !_tight) {
      _drawLabel(
        canvas,
        n.subLabel!,
        Offset(pos.dx, pos.dy + radius + 14),
        style: TextStyle(
          fontSize: (9.5 * _scale).clamp(8.5, 9.5),
          color: color,
          fontWeight: FontWeight.w500,
          letterSpacing: 0.4,
        ),
      );
    }

    // Confidence pip — skip on very narrow canvases, saves clutter.
    if (n.confidence < 1.0 && !_tight) {
      _drawLabel(
        canvas,
        'c ${n.confidence.toStringAsFixed(2)}',
        Offset(pos.dx + radius + 2, pos.dy - radius + 4),
        style: TextStyle(
          fontSize: 8.5,
          color: AppColors.muted,
          fontWeight: FontWeight.w500,
        ),
        align: TextAlign.left,
      );
    }
  }

  Color _nodeColor(EvidenceType t) {
    switch (t) {
      case EvidenceType.fact:
        return AppColors.sage;
      case EvidenceType.observation:
        return AppColors.accent;
      case EvidenceType.prediction:
        return AppColors.violet;
      case EvidenceType.hypothesis:
        return AppColors.amber;
      case EvidenceType.assumption:
        return AppColors.crimson;
    }
  }

  Color _edgeColor(EdgeKind k) {
    switch (k) {
      case EdgeKind.dependsOn:
      case EdgeKind.requires:
        return AppColors.accent;
      case EdgeKind.blocks:
        return AppColors.crimson;
      case EdgeKind.enables:
      case EdgeKind.supports:
        return AppColors.sage;
      case EdgeKind.causes:
        return AppColors.violet;
    }
  }

  String _edgeLabel(EdgeKind k) {
    switch (k) {
      case EdgeKind.dependsOn:
        return 'depends on';
      case EdgeKind.blocks:
        return 'blocks';
      case EdgeKind.enables:
        return 'enables';
      case EdgeKind.causes:
        return 'causes';
      case EdgeKind.requires:
        return 'requires';
      case EdgeKind.supports:
        return 'supports';
    }
  }

  // ---- text helpers ----
  List<String> _wrapLabel(String text,
      {required int maxCharsPerLine, required int maxLines}) {
    final words = text.split(RegExp(r'\s+')).where((w) => w.isNotEmpty).toList();
    final lines = <String>[];
    var current = '';
    for (final w in words) {
      if ((current + (current.isEmpty ? '' : ' ') + w).length > maxCharsPerLine) {
        if (current.isNotEmpty) lines.add(current);
        current = w;
      } else {
        current = current.isEmpty ? w : '$current $w';
      }
      if (lines.length >= maxLines) break;
    }
    if (current.isNotEmpty && lines.length < maxLines) lines.add(current);
    if (lines.isEmpty) lines.add(text);
    if (lines.length == maxLines && words.length > lines.join(' ').split(' ').length) {
      final last = lines.last;
      lines[lines.length - 1] = last.length > 2
          ? '${last.substring(0, math.min(last.length, maxCharsPerLine - 1))}…'
          : '$last…';
    }
    return lines;
  }

  void _drawMultilineText(
    Canvas canvas,
    List<String> lines,
    Offset center, {
    required TextStyle style,
  }) {
    final painters = lines
        .map((l) => TextPainter(
              text: TextSpan(text: l, style: style),
              textAlign: TextAlign.center,
              textDirection: TextDirection.ltr,
            )..layout())
        .toList();
    final totalHeight = painters.fold<double>(0, (s, p) => s + p.height);
    double y = center.dy - totalHeight / 2;
    for (final p in painters) {
      p.paint(canvas, Offset(center.dx - p.width / 2, y));
      y += p.height;
    }
  }

  void _drawLabel(
    Canvas canvas,
    String text,
    Offset pos, {
    required TextStyle style,
    TextAlign align = TextAlign.center,
    Color? backgroundColor,
  }) {
    final tp = TextPainter(
      text: TextSpan(text: text, style: style),
      textAlign: align,
      textDirection: TextDirection.ltr,
    )..layout();
    final offset = Offset(
      align == TextAlign.center ? pos.dx - tp.width / 2 : pos.dx,
      pos.dy - tp.height / 2,
    );
    if (backgroundColor != null) {
      final rect = Rect.fromCenter(
        center: pos,
        width: tp.width + 10,
        height: tp.height + 2,
      );
      canvas.drawRRect(
        RRect.fromRectAndRadius(rect, const Radius.circular(999)),
        Paint()..color = backgroundColor,
      );
    }
    tp.paint(canvas, offset);
  }

  @override
  bool shouldRepaint(covariant _MindMapPainter old) =>
      old.plan.updatedAt != plan.updatedAt ||
      old.plan.nodes.length != plan.nodes.length ||
      old.plan.edges.length != plan.edges.length;
}

class _Legend extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    const entries = [
      ('Fact', AppColors.sage),
      ('Observation', AppColors.accent),
      ('Prediction', AppColors.violet),
      ('Hypothesis', AppColors.amber),
      ('Assumption', AppColors.crimson),
    ];
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.94),
        border: Border.all(color: AppColors.line),
        borderRadius: BorderRadius.circular(999),
      ),
      child: Wrap(
        spacing: 12,
        runSpacing: 4,
        children: entries
            .map((e) => Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Container(
                      width: 7,
                      height: 7,
                      decoration:
                          BoxDecoration(color: e.$2, shape: BoxShape.circle),
                    ),
                    const SizedBox(width: 5),
                    Text(e.$1, style: AppText.mono(size: 10)),
                  ],
                ))
            .toList(),
      ),
    );
  }
}

class _ZoomControls extends StatelessWidget {
  final TransformationController controller;
  const _ZoomControls({required this.controller});

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.94),
        border: Border.all(color: AppColors.line),
        borderRadius: BorderRadius.circular(10),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          _ZoomBtn(
            icon: Icons.add,
            onTap: () {
              final scaled = controller.value.clone()..scaleByDouble(1.2, 1.2, 1.2, 1.0);
              controller.value = scaled;
            },
          ),
          Container(width: 1, height: 20, color: AppColors.line),
          _ZoomBtn(
            icon: Icons.remove,
            onTap: () {
              final s = 1 / 1.2;
              final scaled = controller.value.clone()..scaleByDouble(s, s, s, 1.0);
              controller.value = scaled;
            },
          ),
          Container(width: 1, height: 20, color: AppColors.line),
          _ZoomBtn(
            icon: Icons.center_focus_strong_outlined,
            onTap: () => controller.value = Matrix4.identity(),
          ),
        ],
      ),
    );
  }
}

class _ZoomBtn extends StatelessWidget {
  final IconData icon;
  final VoidCallback onTap;
  const _ZoomBtn({required this.icon, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      child: Padding(
        padding: const EdgeInsets.all(8),
        child: Icon(icon, size: 16, color: AppColors.ink2),
      ),
    );
  }
}
