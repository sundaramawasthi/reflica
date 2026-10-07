import 'package:flutter/material.dart';

import '../theme/app_theme.dart';

class BrandMark extends StatelessWidget {
  final double size;
  const BrandMark({super.key, this.size = 28});

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: size,
      height: size,
      child: CustomPaint(painter: _BrandPainter()),
    );
  }
}

class _BrandPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final c = Offset(size.width / 2, size.height / 2);
    final r = size.width / 2;

    final ring = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1.5
      ..color = AppColors.ink.withValues(alpha: 0.3);
    canvas.drawCircle(c, r - 1, ring);

    final a = Offset(size.width * 0.25, size.height * 0.31);
    final b = Offset(size.width * 0.75, size.height * 0.31);
    final cN = Offset(size.width * 0.5, size.height * 0.69);

    final line = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1.2
      ..color = AppColors.ink.withValues(alpha: 0.5);
    canvas.drawLine(a, cN, line);
    canvas.drawLine(b, cN, line);
    canvas.drawLine(a, b, line);

    final dot = Paint()..color = AppColors.accent;
    canvas.drawCircle(a, size.width * 0.095, dot);
    canvas.drawCircle(
      b,
      size.width * 0.095,
      Paint()..color = AppColors.accent.withValues(alpha: 0.4),
    );
    canvas.drawCircle(cN, size.width * 0.095, Paint()..color = AppColors.amber);
  }

  @override
  bool shouldRepaint(covariant _BrandPainter oldDelegate) => false;
}
