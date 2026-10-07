import 'dart:math' as math;

import 'package:flutter/material.dart';

import '../theme/app_theme.dart';

enum GraphPhase { verified, change, repaired }

/// The hero-section mind map. A compact Flood-Response cognitive graph that
/// animates through three states (verified → change → repaired) with:
///   - Soft radial halos on every node for depth.
///   - Curved typed edges with directional arrowheads + midpoint labels.
///   - A pulsing "change" ring when a disruption fires.
///   - A diamond "risk" node and a dashed "alternative" path that lights up on
///     repair.
///   - Subtle idle wobble on nodes so the graph never looks dead.
class SituationGraph extends StatefulWidget {
  final GraphPhase phase;
  const SituationGraph({super.key, required this.phase});

  @override
  State<SituationGraph> createState() => _SituationGraphState();
}

class _SituationGraphState extends State<SituationGraph>
    with TickerProviderStateMixin {
  late final AnimationController _pulse;
  late final AnimationController _wobble;

  @override
  void initState() {
    super.initState();
    _pulse = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1600),
    )..repeat();
    _wobble = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 6),
    )..repeat();
  }

  @override
  void dispose() {
    _pulse.dispose();
    _wobble.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, c) {
        return AnimatedBuilder(
          animation: Listenable.merge([_pulse, _wobble]),
          builder: (_, _) {
            return CustomPaint(
              size: Size(c.maxWidth, c.maxHeight),
              painter: _GraphPainter(
                phase: widget.phase,
                pulse: _pulse.value,
                wobble: _wobble.value,
              ),
            );
          },
        );
      },
    );
  }
}

const _brandBlue = Color(0xFF2E6FEB);

class _GraphPainter extends CustomPainter {
  final GraphPhase phase;
  final double pulse;
  final double wobble;

  _GraphPainter({
    required this.phase,
    required this.pulse,
    required this.wobble,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final w = size.width;
    final h = size.height;

    // Normalised layout — scales with the hero card size.
    final cx = w * 0.5;

    double jitter(double amp, double offset) =>
        math.sin((wobble + offset) * 2 * math.pi) * amp;

    // Node positions
    final nFlood = Offset(cx, h * 0.10);
    final nAlert = Offset(cx * 0.33, h * 0.18 + jitter(1.2, 0.1));
    final nRoadA = Offset(w * 0.25, h * 0.40);
    final nRoadB = Offset(w * 0.75, h * 0.40);
    final nPeople = Offset(w * 0.10, h * 0.70);
    final nShelter = Offset(cx, h * 0.72);
    final nTrucks = Offset(w * 0.90, h * 0.70 + jitter(1.4, 0.2));
    final nSupplies = Offset(cx, h * 0.93);
    final nRisk = Offset(w * 0.78, h * 0.17 + jitter(1.2, 0.3));

    final isChange = phase == GraphPhase.change;
    final isRepaired = phase == GraphPhase.repaired;

    // ---- background grid dots ----
    _grid(canvas, size);

    // ---- edges (drawn under nodes) ----
    _edge(canvas, nFlood, nRoadA,
        color: AppColors.crimson.withValues(alpha: 0.75), width: 1.6);
    _edge(canvas, nFlood, nRoadB,
        color: AppColors.lineStrong, width: 1, dashed: true);

    _edge(canvas, nAlert, nRoadA,
        color: AppColors.crimson.withValues(alpha: 0.4),
        width: 1,
        dashed: true);

    _edge(canvas, nRoadA, nShelter,
        color: isChange
            ? AppColors.amber
            : isRepaired
                ? AppColors.lineStrong.withValues(alpha: 0.6)
                : AppColors.sage,
        width: 2,
        dashed: isChange || isRepaired);
    _edge(canvas, nRoadB, nShelter,
        color: isRepaired
            ? AppColors.sage
            : AppColors.lineStrong.withValues(alpha: 0.6),
        width: isRepaired ? 2 : 1,
        dashed: !isRepaired);

    _edge(canvas, nPeople, nShelter, color: _brandBlue, width: 1.5);
    _edge(canvas, nTrucks, nShelter, color: _brandBlue, width: 1.5);
    _edge(canvas, nShelter, nSupplies,
        color: AppColors.amber.withValues(alpha: 0.8), width: 1.5);

    _edge(canvas, nRisk, nRoadA,
        color: AppColors.amber.withValues(alpha: 0.3),
        width: 1,
        dashed: true);

    // ---- pulse ring on the broken road during the change phase ----
    if (isChange) {
      _pulseRing(canvas, nRoadA, AppColors.amber);
    }
    if (isRepaired) {
      _pulseRing(canvas, nRoadB, AppColors.sage);
    }

    // ---- nodes ----
    _node(canvas, nFlood,
        fill: AppColors.crimson,
        glyph: '!',
        label: 'Flood',
        sub: 'obs · 10:00 · c 0.95',
        labelAbove: true);

    _diamond(canvas, nAlert,
        fill: AppColors.crimson.withValues(alpha: 0.75),
        label: 'Alert',
        sub: 'risk · dispatch');

    _diamond(canvas, nRisk,
        fill: AppColors.amber,
        label: 'Rain risk',
        sub: 'hypothesis · c 0.6');

    final roadAFill = isChange ? AppColors.amber : AppColors.sage;
    _node(canvas, nRoadA,
        fill: roadAFill,
        glyph: isChange ? '✕' : '✓',
        label: 'Road A',
        sub: isChange ? 'blocked · 11:20' : 'open · 09:00',
        labelAbove: true);

    final roadBFill = isRepaired ? AppColors.sage : AppColors.muted;
    final roadBAlpha = isRepaired ? 1.0 : 0.45;
    _node(canvas, nRoadB,
        fill: roadBFill.withValues(alpha: roadBAlpha),
        glyph: isRepaired ? '✓' : '·',
        label: 'Road B',
        sub: isRepaired ? 'open · routed' : 'alt · unverified',
        labelAbove: true,
        labelAlpha: isRepaired ? 1.0 : 0.55);

    _node(canvas, nPeople,
        fill: _brandBlue,
        glyph: '40',
        label: 'People',
        sub: 'need · evac',
        labelAbove: false);

    _rect(canvas, nShelter,
        fill: AppColors.sage,
        glyph: 'S · 50',
        label: 'Shelter A',
        sub: 'fact · 50 beds');

    _node(canvas, nTrucks,
        fill: _brandBlue,
        glyph: 'T1·T2',
        label: 'Trucks',
        sub: '20 ea · avail',
        labelAbove: false);

    _node(canvas, nSupplies,
        fill: AppColors.amber,
        glyph: '▲',
        radius: 11,
        label: 'Supplies',
        sub: 'high priority',
        labelAbove: false);
  }

  // ------- primitives -------

  void _grid(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = AppColors.lineStrong.withValues(alpha: 0.08);
    const spacing = 28.0;
    for (double x = 0; x < size.width; x += spacing) {
      for (double y = 0; y < size.height; y += spacing) {
        canvas.drawCircle(Offset(x, y), 0.8, paint);
      }
    }
  }

  void _edge(
    Canvas canvas,
    Offset a,
    Offset b, {
    required Color color,
    double width = 1.5,
    bool dashed = false,
  }) {
    final paint = Paint()
      ..color = color
      ..strokeWidth = width
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round;

    final midLift = (a - b).distance * 0.08;
    final mid = Offset((a.dx + b.dx) / 2, (a.dy + b.dy) / 2 - midLift);
    final path = Path()
      ..moveTo(a.dx, a.dy)
      ..quadraticBezierTo(mid.dx, mid.dy, b.dx, b.dy);

    if (dashed) {
      for (final metric in path.computeMetrics()) {
        double d = 0;
        while (d < metric.length) {
          final next = (d + 4).clamp(0.0, metric.length);
          canvas.drawPath(metric.extractPath(d, next), paint);
          d = next + 3;
        }
      }
    } else {
      canvas.drawPath(path, paint);
    }

    // Arrowhead at b
    final dir = (b - a);
    final len = dir.distance;
    if (len > 0) {
      final norm = dir / len;
      final tip = b - norm * 14;
      final perp = Offset(-norm.dy, norm.dx);
      final left = tip + perp * 4;
      final right = tip - perp * 4;
      final head = Path()
        ..moveTo(b.dx, b.dy)
        ..lineTo(left.dx, left.dy)
        ..lineTo(right.dx, right.dy)
        ..close();
      canvas.drawPath(head, Paint()..color = color);
    }
  }

  void _pulseRing(Canvas canvas, Offset c, Color color) {
    final r = 20 + pulse * 36;
    final alpha = (0.9 - pulse * 0.9).clamp(0.0, 1.0);
    canvas.drawCircle(
      c,
      r,
      Paint()
        ..style = PaintingStyle.stroke
        ..strokeWidth = 2
        ..color = color.withValues(alpha: alpha),
    );
    canvas.drawCircle(
      c,
      r * 0.55,
      Paint()
        ..style = PaintingStyle.stroke
        ..strokeWidth = 1.4
        ..color = color.withValues(alpha: alpha * 0.6),
    );
  }

  void _node(
    Canvas canvas,
    Offset c, {
    required Color fill,
    required String glyph,
    String label = '',
    String sub = '',
    double radius = 15,
    bool labelAbove = true,
    double labelAlpha = 1.0,
  }) {
    // Soft halo
    canvas.drawCircle(
      c,
      radius + 10,
      Paint()..color = fill.withValues(alpha: 0.14),
    );
    // Inner glow
    canvas.drawCircle(
      c,
      radius + 4,
      Paint()..color = fill.withValues(alpha: 0.18),
    );
    // Body
    canvas.drawCircle(c, radius, Paint()..color = fill);
    // Rim highlight
    canvas.drawCircle(
      c,
      radius,
      Paint()
        ..style = PaintingStyle.stroke
        ..strokeWidth = 1
        ..color = Colors.white.withValues(alpha: 0.4),
    );
    // Glyph
    _text(
      canvas,
      glyph,
      c,
      style: TextStyle(
        fontSize: glyph.length > 2 ? 9 : 11.5,
        color: Colors.white,
        fontWeight: FontWeight.w700,
      ),
      centerVertical: true,
    );
    if (label.isNotEmpty) {
      _text(
        canvas,
        label,
        Offset(c.dx, labelAbove ? c.dy - radius - 18 : c.dy + radius + 12),
        style: TextStyle(
          fontSize: 11.5,
          color: AppColors.ink.withValues(alpha: labelAlpha),
          fontWeight: FontWeight.w600,
        ),
      );
    }
    if (sub.isNotEmpty) {
      _text(
        canvas,
        sub,
        Offset(c.dx, labelAbove ? c.dy - radius - 32 : c.dy + radius + 26),
        style: TextStyle(
          fontSize: 9.5,
          color: AppColors.muted.withValues(alpha: labelAlpha),
          fontWeight: FontWeight.w500,
        ),
      );
    }
  }

  void _rect(
    Canvas canvas,
    Offset c, {
    required Color fill,
    required String glyph,
    required String label,
    required String sub,
  }) {
    final outer = RRect.fromRectAndRadius(
      Rect.fromCenter(center: c, width: 62, height: 38),
      const Radius.circular(8),
    );
    final inner = RRect.fromRectAndRadius(
      Rect.fromCenter(center: c, width: 52, height: 26),
      const Radius.circular(6),
    );
    canvas.drawRRect(outer, Paint()..color = fill.withValues(alpha: 0.18));
    canvas.drawRRect(inner, Paint()..color = fill);
    _text(canvas, glyph, c,
        style: const TextStyle(
          fontSize: 10,
          color: Colors.white,
          fontWeight: FontWeight.w700,
        ),
        centerVertical: true);
    _text(canvas, label, Offset(c.dx, c.dy - 30),
        style: const TextStyle(
          fontSize: 11.5,
          color: AppColors.ink,
          fontWeight: FontWeight.w600,
        ));
    _text(canvas, sub, Offset(c.dx, c.dy - 44),
        style: const TextStyle(
          fontSize: 9.5,
          color: AppColors.muted,
          fontWeight: FontWeight.w500,
        ));
  }

  void _diamond(
    Canvas canvas,
    Offset c, {
    required Color fill,
    required String label,
    required String sub,
  }) {
    const r = 12.0;
    final path = Path()
      ..moveTo(c.dx, c.dy - r)
      ..lineTo(c.dx + r, c.dy)
      ..lineTo(c.dx, c.dy + r)
      ..lineTo(c.dx - r, c.dy)
      ..close();
    // Halo
    final halo = Path()
      ..moveTo(c.dx, c.dy - (r + 6))
      ..lineTo(c.dx + (r + 6), c.dy)
      ..lineTo(c.dx, c.dy + (r + 6))
      ..lineTo(c.dx - (r + 6), c.dy)
      ..close();
    canvas.drawPath(halo, Paint()..color = fill.withValues(alpha: 0.14));
    canvas.drawPath(path, Paint()..color = fill);
    canvas.drawPath(
      path,
      Paint()
        ..style = PaintingStyle.stroke
        ..strokeWidth = 1
        ..color = Colors.white.withValues(alpha: 0.5),
    );
    _text(canvas, label, Offset(c.dx, c.dy + r + 10),
        style: const TextStyle(
          fontSize: 10.5,
          color: AppColors.ink,
          fontWeight: FontWeight.w600,
        ));
    _text(canvas, sub, Offset(c.dx, c.dy + r + 23),
        style: const TextStyle(
          fontSize: 9,
          color: AppColors.muted,
          fontWeight: FontWeight.w500,
        ));
  }

  void _text(
    Canvas canvas,
    String s,
    Offset pos, {
    required TextStyle style,
    bool centerVertical = false,
  }) {
    final tp = TextPainter(
      text: TextSpan(text: s, style: style),
      textAlign: TextAlign.center,
      textDirection: TextDirection.ltr,
    )..layout();
    final dx = pos.dx - tp.width / 2;
    final dy = pos.dy - (centerVertical ? tp.height / 2 : 0);
    tp.paint(canvas, Offset(dx, dy));
  }

  @override
  bool shouldRepaint(covariant _GraphPainter old) =>
      old.phase != phase || old.pulse != pulse || old.wobble != wobble;
}
