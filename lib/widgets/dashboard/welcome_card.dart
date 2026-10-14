import 'dart:math' as math;

import 'package:flutter/material.dart';

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
          'AI Forecasting\nfor India',
          style: AppText.serif(size: 36, weight: FontWeight.w400),
        ),
        const SizedBox(height: 14),
        Text(
          'Explore upcoming events, inspect model predictions, and evaluate '
          'forecasts against real-world outcomes.',
          style: AppText.body(size: 15, color: AppColors.ink2),
        ),
      ],
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
