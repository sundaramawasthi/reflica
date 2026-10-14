import 'dart:math' as math;

import 'package:flutter/material.dart';

import '../widgets/app_top_bar.dart';
import '../widgets/cta_footer.dart';
import '../widgets/responsive.dart';

/// Homepage colours (white, royal blue, navy). Kept local so the signed-in
/// dashboard keeps the shared [AppColors] theme until it is redesigned.
class HomeColors {
  static const background = Colors.white;
  static const section = Color(0xFFF3F7FD);
  static const navy = Color(0xFF0F1B3D);
  static const muted = Color(0xFF5B6B85);
  static const border = Color(0xFFE3E9F3);
  static const blue = Color(0xFF2563EB);
  static const blueDark = Color(0xFF1D4ED8);
  static const green = Color(0xFF16A34A);
  static const purple = Color(0xFF7C3AED);
  static const orange = Color(0xFFEA580C);
}

/// Forecasting pages are not built yet. Say so honestly instead of opening
/// an empty or fake page.
Future<void> showComingSoon(BuildContext context, String what) {
  return showDialog<void>(
    context: context,
    builder: (ctx) => AlertDialog(
      backgroundColor: Colors.white,
      title: Text('$what: coming soon',
          style: const TextStyle(
              color: HomeColors.navy, fontWeight: FontWeight.w700)),
      content: const Text(
        'Reflica is an M.Tech research project. The first forecasting '
        'questions are being prepared, and the first forecasts will be '
        'recorded from December 2026. No forecasts are published yet.',
        style: TextStyle(color: HomeColors.muted, height: 1.5),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(ctx).pop(),
          child: const Text('OK'),
        ),
      ],
    ),
  );
}

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final _scroll = ScrollController();
  final _howItWorksKey = GlobalKey();
  bool _scrolled = false;

  @override
  void initState() {
    super.initState();
    _scroll.addListener(() {
      final s = _scroll.offset > 8;
      if (s != _scrolled) setState(() => _scrolled = s);
    });
  }

  @override
  void dispose() {
    _scroll.dispose();
    super.dispose();
  }

  void _scrollToTop() {
    _scroll.animateTo(0,
        duration: const Duration(milliseconds: 400), curve: Curves.easeOut);
  }

  void _scrollToHowItWorks() {
    final ctx = _howItWorksKey.currentContext;
    if (ctx == null) return;
    Scrollable.ensureVisible(ctx,
        duration: const Duration(milliseconds: 500), curve: Curves.easeOut);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: HomeColors.background,
      body: Stack(
        children: [
          Positioned.fill(
            child: SingleChildScrollView(
              controller: _scroll,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  const SizedBox(height: 72),
                  _Hero(
                    onExplore: () => showComingSoon(context, 'Forecasts'),
                  ),
                  const _FeatureCards(),
                  _HowItWorks(key: _howItWorksKey),
                  const CtaFooter(),
                ],
              ),
            ),
          ),
          Positioned(
            top: 0,
            left: 0,
            right: 0,
            child: AppTopBar(
              elevated: _scrolled,
              onHome: _scrollToTop,
              onAbout: _scrollToHowItWorks,
              onComingSoon: (what) => showComingSoon(context, what),
            ),
          ),
        ],
      ),
    );
  }
}

// ---------------------------------------------------------------- Hero ----

class _Hero extends StatelessWidget {
  final VoidCallback onExplore;
  const _Hero({required this.onExplore});

  @override
  Widget build(BuildContext context) {
    final size = screenSizeOf(context);
    final stacked = size == ScreenSize.phone || size == ScreenSize.tablet;
    final copy = _HeroCopy(onExplore: onExplore, compact: stacked);

    if (stacked) {
      return PageWrap(
        padding: const EdgeInsets.fromLTRB(
            Breakpoints.pageGutter, 32, Breakpoints.pageGutter, 24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            copy,
            const SizedBox(height: 28),
            ClipRRect(
              borderRadius: BorderRadius.circular(20),
              child: const SizedBox(height: 240, child: _HeroImage()),
            ),
          ],
        ),
      );
    }

    // Image and text widths scale with the screen so the headline never
    // sits on the solid (unfaded) part of the picture.
    final screenWidth = MediaQuery.sizeOf(context).width;
    final imageWidth = math.min(760.0, screenWidth * 0.58);
    final copyWidth = math.min(560.0, screenWidth * 0.46);

    return SizedBox(
      height: 520,
      child: Stack(
        children: [
          // Decorative image on the right, fading into white on the left.
          Positioned(
            top: 0,
            bottom: 0,
            right: 0,
            width: imageWidth,
            child: const _HeroImage(fadeLeft: true),
          ),
          Positioned.fill(
            child: PageWrap(
              child: Align(
                alignment: Alignment.centerLeft,
                child: ConstrainedBox(
                  constraints: BoxConstraints(maxWidth: copyWidth),
                  child: copy,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _HeroCopy extends StatelessWidget {
  final VoidCallback onExplore;
  final bool compact;
  const _HeroCopy({required this.onExplore, required this.compact});

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'AI FORECASTING FOR INDIA',
          style: TextStyle(
            color: HomeColors.blue,
            fontSize: 13,
            fontWeight: FontWeight.w700,
            letterSpacing: 1.6,
          ),
        ),
        const SizedBox(height: 16),
        Semantics(
          header: true,
          child: Text(
            'Better forecasts.\nA clearer tomorrow.',
            style: TextStyle(
              color: HomeColors.navy,
              fontSize: compact ? 38 : 56,
              height: 1.1,
              fontWeight: FontWeight.w800,
              letterSpacing: -0.5,
            ),
          ),
        ),
        const SizedBox(height: 20),
        const Text(
          'Reflica uses AI to predict important events affecting India, with '
          'honest probabilities, clear evidence and a focus on real-world '
          'impact.',
          style: TextStyle(color: HomeColors.muted, fontSize: 17, height: 1.6),
        ),
        const SizedBox(height: 28),
        FilledButton(
          onPressed: onExplore,
          style: FilledButton.styleFrom(
            backgroundColor: HomeColors.blue,
            foregroundColor: Colors.white,
            padding: const EdgeInsets.symmetric(horizontal: 26, vertical: 18),
            shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12)),
            textStyle:
                const TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
          ),
          child: const Text('Explore Forecasts →'),
        ),
        const SizedBox(height: 14),
        const Text(
          'Research preview · first forecasts from December 2026',
          style: TextStyle(color: HomeColors.muted, fontSize: 13),
        ),
      ],
    );
  }
}

/// Decorative India Gate at sunrise, drawn in code (no image download).
/// A licensed photo can replace it later without changing the layout.
class _HeroImage extends StatelessWidget {
  final bool fadeLeft;
  const _HeroImage({this.fadeLeft = false});

  @override
  Widget build(BuildContext context) {
    return ExcludeSemantics(
      child: Stack(
        fit: StackFit.expand,
        children: [
          const CustomPaint(painter: _IndiaGatePainter()),
          if (fadeLeft)
            const DecoratedBox(
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.centerLeft,
                  end: Alignment.centerRight,
                  colors: [Colors.white, Color(0x00FFFFFF)],
                  stops: [0.0, 0.45],
                ),
              ),
            ),
        ],
      ),
    );
  }
}

class _IndiaGatePainter extends CustomPainter {
  const _IndiaGatePainter();

  @override
  void paint(Canvas canvas, Size size) {
    final w = size.width;
    final h = size.height;
    final rect = Offset.zero & size;

    // Sky: warm sunrise near the horizon, pale blue at the top.
    canvas.drawRect(
      rect,
      Paint()
        ..shader = const LinearGradient(
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
          colors: [Color(0xFFE8F0FB), Color(0xFFFDE7C8), Color(0xFFF9C88F)],
          stops: [0.0, 0.6, 1.0],
        ).createShader(rect),
    );

    // Sun behind the monument.
    final groundY = h * 0.86;
    final cx = w * 0.62;
    canvas.drawCircle(
      Offset(cx, groundY - h * 0.38),
      h * 0.16,
      Paint()..color = const Color(0xFFFFD79A).withValues(alpha: 0.9),
    );

    final stone = Paint()..color = const Color(0xFFB9744A);
    final shade = Paint()..color = const Color(0xFF9A5A36);

    // Monument proportions, scaled to the available height.
    final gw = math.min(w * 0.36, h * 0.62); // total width
    final gh = gw * 1.18; // height up to the cornice
    final left = cx - gw / 2;
    final top = groundY - gh;

    // Steps.
    canvas.drawRect(
        Rect.fromLTWH(left - gw * 0.08, groundY - gh * 0.04, gw * 1.16,
            gh * 0.04),
        shade);

    // Main body with the arched opening cut out.
    final body = Path()
      ..addRect(Rect.fromLTWH(left, top, gw, gh * 0.96));
    final archW = gw * 0.42;
    final archLeft = cx - archW / 2;
    final archTop = top + gh * 0.34;
    final arch = Path()
      ..moveTo(archLeft, groundY - gh * 0.04)
      ..lineTo(archLeft, archTop + archW / 2)
      ..arcToPoint(Offset(archLeft + archW, archTop + archW / 2),
          radius: Radius.circular(archW / 2))
      ..lineTo(archLeft + archW, groundY - gh * 0.04)
      ..close();
    canvas.drawPath(
        Path.combine(PathOperation.difference, body, arch), stone);

    // Cornice bands and the attic block on top.
    canvas.drawRect(
        Rect.fromLTWH(left - gw * 0.04, top + gh * 0.16, gw * 1.08, gh * 0.04),
        shade);
    canvas.drawRect(
        Rect.fromLTWH(left - gw * 0.03, top - gh * 0.02, gw * 1.06, gh * 0.05),
        shade);
    canvas.drawRect(
        Rect.fromLTWH(left + gw * 0.18, top - gh * 0.14, gw * 0.64, gh * 0.12),
        stone);
    canvas.drawRect(
        Rect.fromLTWH(left + gw * 0.36, top - gh * 0.2, gw * 0.28, gh * 0.06),
        stone);

    // Ground and soft tree lines on both sides.
    canvas.drawRect(Rect.fromLTWH(0, groundY, w, h - groundY),
        Paint()..color = const Color(0xFFD9B98C));
    final trees = Paint()..color = const Color(0xFF7D8F6A).withValues(alpha: 0.55);
    for (var i = 0; i < 14; i++) {
      final x = w * (i / 13);
      if ((x - cx).abs() < gw * 0.75) continue;
      canvas.drawCircle(Offset(x, groundY - 6), 16 + (i % 3) * 5.0, trees);
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}

// ------------------------------------------------------- Feature cards ----

class _FeatureCards extends StatelessWidget {
  const _FeatureCards();

  static const _cards = [
    _Feature(
      icon: Icons.trending_up,
      color: HomeColors.blue,
      title: 'Probability Forecasts',
      text: 'Get clear percentage forecasts for important events, from '
          'economy to weather.',
    ),
    _Feature(
      icon: Icons.description_outlined,
      color: HomeColors.green,
      title: 'Evidence Grounded',
      text: 'Every forecast is backed by relevant evidence and clear '
          'reasoning.',
    ),
    _Feature(
      icon: Icons.shield_outlined,
      color: HomeColors.purple,
      title: 'Honest Uncertainty',
      text: 'When evidence is weak, Reflica says “I don\'t know” instead of '
          'guessing.',
    ),
    _Feature(
      icon: Icons.place_outlined,
      color: HomeColors.orange,
      title: 'Real-World Impact',
      text: 'See how events could affect people, regions and more.',
    ),
  ];

  @override
  Widget build(BuildContext context) {
    final size = screenSizeOf(context);
    final perRow = switch (size) {
      ScreenSize.phone => 1,
      ScreenSize.tablet => 2,
      _ => 4,
    };
    const gap = 20.0;

    return PageWrap(
      padding: const EdgeInsets.fromLTRB(
          Breakpoints.pageGutter, 24, Breakpoints.pageGutter, 64),
      child: LayoutBuilder(
        builder: (context, c) {
          final cardWidth = (c.maxWidth - gap * (perRow - 1)) / perRow;
          return Wrap(
            spacing: gap,
            runSpacing: gap,
            children: [
              for (final f in _cards)
                SizedBox(width: cardWidth, child: _FeatureCard(feature: f)),
            ],
          );
        },
      ),
    );
  }
}

class _Feature {
  final IconData icon;
  final Color color;
  final String title;
  final String text;
  const _Feature({
    required this.icon,
    required this.color,
    required this.title,
    required this.text,
  });
}

class _FeatureCard extends StatelessWidget {
  final _Feature feature;
  const _FeatureCard({required this.feature});

  @override
  Widget build(BuildContext context) {
    return Container(
      constraints: const BoxConstraints(minHeight: 200),
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: HomeColors.border),
        boxShadow: [
          BoxShadow(
            color: HomeColors.navy.withValues(alpha: 0.04),
            blurRadius: 16,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 48,
            height: 48,
            decoration: BoxDecoration(
              color: feature.color.withValues(alpha: 0.12),
              shape: BoxShape.circle,
            ),
            child: Icon(feature.icon, color: feature.color, size: 24),
          ),
          const SizedBox(height: 18),
          Text(
            feature.title,
            style: const TextStyle(
              color: HomeColors.navy,
              fontSize: 18,
              fontWeight: FontWeight.w700,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            feature.text,
            style: const TextStyle(
                color: HomeColors.muted, fontSize: 15, height: 1.55),
          ),
        ],
      ),
    );
  }
}

// -------------------------------------------------------- How it works ----

class _HowItWorks extends StatelessWidget {
  const _HowItWorks({super.key});

  static const _steps = [
    _Step(
      icon: Icons.help_outline,
      title: 'Ask a Question',
      text: 'We define clear, testable questions about important events in '
          'India.',
    ),
    _Step(
      icon: Icons.psychology_outlined,
      title: 'Get a Forecast',
      text: 'AI models provide probabilities with evidence and uncertainty '
          'levels.',
    ),
    _Step(
      icon: Icons.event_available_outlined,
      title: 'Track the Outcome',
      text: 'We record the real result when it becomes available.',
    ),
    _Step(
      icon: Icons.track_changes,
      title: 'Measure Accuracy',
      text: 'We score the forecasts and learn for better predictions in the '
          'future.',
    ),
  ];

  @override
  Widget build(BuildContext context) {
    final size = screenSizeOf(context);
    final horizontal = size == ScreenSize.desktop || size == ScreenSize.wide;

    return Container(
      color: HomeColors.section,
      padding: const EdgeInsets.symmetric(vertical: 72),
      child: PageWrap(
        child: Column(
          children: [
            const Semantics(
              header: true,
              child: Text(
                'How It Works',
                textAlign: TextAlign.center,
                style: TextStyle(
                  color: HomeColors.navy,
                  fontSize: 34,
                  fontWeight: FontWeight.w800,
                ),
              ),
            ),
            const SizedBox(height: 12),
            ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 620),
              child: const Text(
                'We combine the best of AI and human insight to forecast what '
                'matters — before it happens.',
                textAlign: TextAlign.center,
                style: TextStyle(
                    color: HomeColors.muted, fontSize: 17, height: 1.6),
              ),
            ),
            const SizedBox(height: 48),
            if (horizontal)
              Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  for (var i = 0; i < _steps.length; i++) ...[
                    Expanded(child: _StepTile(step: _steps[i], number: i + 1)),
                    if (i < _steps.length - 1)
                      const Padding(
                        padding: EdgeInsets.only(top: 22),
                        child: Icon(Icons.arrow_forward,
                            color: HomeColors.blue, size: 22),
                      ),
                  ],
                ],
              )
            else
              Column(
                children: [
                  for (var i = 0; i < _steps.length; i++) ...[
                    _StepTile(step: _steps[i], number: i + 1),
                    if (i < _steps.length - 1)
                      const Padding(
                        padding: EdgeInsets.symmetric(vertical: 12),
                        child: Icon(Icons.arrow_downward,
                            color: HomeColors.blue, size: 22),
                      ),
                  ],
                ],
              ),
          ],
        ),
      ),
    );
  }
}

class _Step {
  final IconData icon;
  final String title;
  final String text;
  const _Step({required this.icon, required this.title, required this.text});
}

class _StepTile extends StatelessWidget {
  final _Step step;
  final int number;
  const _StepTile({required this.step, required this.number});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 12),
      child: Column(
        children: [
          Container(
            width: 64,
            height: 64,
            decoration: BoxDecoration(
              color: Colors.white,
              shape: BoxShape.circle,
              border: Border.all(color: HomeColors.border),
            ),
            child: Icon(step.icon, color: HomeColors.blue, size: 28),
          ),
          const SizedBox(height: 16),
          Text(
            '$number. ${step.title}',
            textAlign: TextAlign.center,
            style: const TextStyle(
              color: HomeColors.navy,
              fontSize: 17,
              fontWeight: FontWeight.w700,
            ),
          ),
          const SizedBox(height: 8),
          ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 280),
            child: Text(
              step.text,
              textAlign: TextAlign.center,
              style: const TextStyle(
                  color: HomeColors.muted, fontSize: 15, height: 1.55),
            ),
          ),
        ],
      ),
    );
  }
}
