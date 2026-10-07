import 'dart:async';

import 'package:flutter/material.dart';

import '../theme/app_theme.dart';
import 'app_top_bar.dart' show handleGetStarted;
import 'responsive.dart';
import 'situation_graph.dart';

const _brandBlue = Color(0xFF2E6FEB);
const _brandBlueSoft = Color(0xFF4A8EFF);
const _brandViolet = Color(0xFF7A5BE8);
const _brandVioletSoft = Color(0xFF9A7FEF);

class HeroSection extends StatefulWidget {
  const HeroSection({super.key});

  @override
  State<HeroSection> createState() => _HeroSectionState();
}

class _HeroSectionState extends State<HeroSection> {
  int _phase = 0;
  Timer? _timer;

  static const _phases = [
    GraphPhase.verified,
    GraphPhase.change,
    GraphPhase.repaired,
  ];

  @override
  void initState() {
    super.initState();
    _timer = Timer.periodic(const Duration(milliseconds: 4200), (_) {
      if (!mounted) return;
      setState(() => _phase = (_phase + 1) % _phases.length);
    });
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  void _replay() {
    setState(() => _phase = 0);
    _timer?.cancel();
    _timer = Timer.periodic(const Duration(milliseconds: 4200), (_) {
      if (!mounted) return;
      setState(() => _phase = (_phase + 1) % _phases.length);
    });
  }

  @override
  Widget build(BuildContext context) {
    final size = screenSizeOf(context);
    final isStacked = size.index < ScreenSize.desktop.index;

    final leftColumn = _HeroCopy(onReplay: _replay);
    final rightColumn = _HeroDashboard(
      phase: _phases[_phase],
      onReplay: _replay,
    );

    return Container(
      decoration: const BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            Color(0xFFFBFCFF),
            Color(0xFFEEF2FA),
          ],
        ),
      ),
      child: PageWrap(
        child: Padding(
          padding: const EdgeInsets.only(top: 48, bottom: 72),
          child: isStacked
              ? Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    leftColumn,
                    const SizedBox(height: 48),
                    SizedBox(height: 560, child: rightColumn),
                  ],
                )
              : Row(
                  crossAxisAlignment: CrossAxisAlignment.center,
                  children: [
                    Expanded(flex: 100, child: leftColumn),
                    const SizedBox(width: 48),
                    Expanded(
                      flex: 125,
                      child: SizedBox(height: 620, child: rightColumn),
                    ),
                  ],
                ),
        ),
      ),
    );
  }
}

class _HeroCopy extends StatelessWidget {
  final VoidCallback onReplay;
  const _HeroCopy({required this.onReplay});

  @override
  Widget build(BuildContext context) {
    final w = MediaQuery.sizeOf(context).width;
    final heroSize = w < 560 ? 44.0 : (w < 1180 ? 58.0 : 72.0);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Positioning pill — living strategic planning platform.
        // Pill is width-aware: shortens the text on tight widths so it never
        // overflows the hero column.
        LayoutBuilder(builder: (ctx, c) {
          final text = c.maxWidth < 420
              ? 'Living strategic planning'
              : c.maxWidth < 620
                  ? 'Living strategic planning platform'
                  : 'Living strategic planning · for individuals to governments';
          return Align(
            alignment: Alignment.centerLeft,
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
              decoration: BoxDecoration(
                color: _brandBlue.withValues(alpha: 0.08),
                borderRadius: BorderRadius.circular(999),
                border: Border.all(color: _brandBlue.withValues(alpha: 0.15)),
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Container(
                    width: 6,
                    height: 6,
                    decoration: BoxDecoration(
                      color: _brandBlue,
                      shape: BoxShape.circle,
                      boxShadow: [
                        BoxShadow(
                          color: _brandBlue.withValues(alpha: 0.5),
                          blurRadius: 6,
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(width: 10),
                  Flexible(
                    child: Text(
                      text,
                      style: AppText.body(
                        size: 13,
                        weight: FontWeight.w500,
                        color: _brandBlue,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                ],
              ),
            ),
          );
        }),
        const SizedBox(height: 28),

        // Headline with gradient words
        _GradientHeadline(size: heroSize),

        const SizedBox(height: 24),

        ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 560),
          child: Text(
            'Describe a goal in your own words. Reflica turns it into a '
            'structured strategy — objectives, dependencies, resources, risks '
            'and timeline — and keeps the plan alive as reports arrive from the '
            'real world. One general engine for individuals, organisations, '
            'research institutions and government bodies.',
            style: AppText.body(size: 17, color: AppColors.ink2),
          ),
        ),

        const SizedBox(height: 32),

        // Feature pills row
        const _FeaturePillsRow(),

        const SizedBox(height: 36),

        // CTAs
        Builder(
          builder: (ctx) =>
              _StartExploringButton(onTap: () => handleGetStarted(ctx)),
        ),
      ],
    );
  }
}

class _GradientHeadline extends StatelessWidget {
  final double size;
  const _GradientHeadline({required this.size});

  @override
  Widget build(BuildContext context) {
    // Keep "From" / "to" at the base size; make the gradient phrases larger
    // and heavier so they carry the headline.
    final baseStyle = AppText.display(size: size, weight: FontWeight.w500);
    final gradientSize = size * 1.18;
    final gradientStyle =
        AppText.display(size: gradientSize, weight: FontWeight.w700);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        RichText(
          text: TextSpan(
            style: baseStyle,
            children: [
              const TextSpan(text: 'From '),
              WidgetSpan(
                alignment: PlaceholderAlignment.baseline,
                baseline: TextBaseline.alphabetic,
                child: _GradientText(
                  text: 'Complex Situations',
                  style: gradientStyle,
                  colors: const [_brandBlue, _brandBlueSoft],
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 6),
        RichText(
          text: TextSpan(
            style: baseStyle,
            children: [
              const TextSpan(text: 'to '),
              WidgetSpan(
                alignment: PlaceholderAlignment.baseline,
                baseline: TextBaseline.alphabetic,
                child: _GradientText(
                  text: 'Confident Decisions',
                  style: gradientStyle,
                  colors: const [_brandViolet, _brandVioletSoft],
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}

class _GradientText extends StatelessWidget {
  final String text;
  final TextStyle style;
  final List<Color> colors;
  const _GradientText({
    required this.text,
    required this.style,
    required this.colors,
  });

  @override
  Widget build(BuildContext context) {
    return ShaderMask(
      blendMode: BlendMode.srcIn,
      shaderCallback: (bounds) => LinearGradient(
        colors: colors,
        begin: Alignment.topLeft,
        end: Alignment.bottomRight,
      ).createShader(Rect.fromLTWH(0, 0, bounds.width, bounds.height)),
      child: Text(text, style: style),
    );
  }
}

class _FeaturePillsRow extends StatelessWidget {
  const _FeaturePillsRow();

  @override
  Widget build(BuildContext context) {
    const features = [
      _Feature('Dynamic\nCognitive Graph', Icons.hub_outlined, _brandBlue),
      _Feature('Evidence &\nProvenance', Icons.verified_outlined, AppColors.sage),
      _Feature('Reasoning &\nConstraint Checking', Icons.psychology_outlined, _brandViolet),
      _Feature('Adaptive\nReplanning', Icons.sync_outlined, AppColors.sage),
      _Feature('Human-in-the-Loop', Icons.person_outline, AppColors.amber),
    ];
    return Wrap(
      spacing: 24,
      runSpacing: 16,
      children: features.map((f) => _FeaturePill(feature: f)).toList(),
    );
  }
}

class _Feature {
  final String label;
  final IconData icon;
  final Color color;
  const _Feature(this.label, this.icon, this.color);
}

class _FeaturePill extends StatelessWidget {
  final _Feature feature;
  const _FeaturePill({required this.feature});

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: 44,
          height: 44,
          decoration: BoxDecoration(
            color: feature.color.withValues(alpha: 0.12),
            shape: BoxShape.circle,
          ),
          alignment: Alignment.center,
          child: Icon(feature.icon, color: feature.color, size: 20),
        ),
        const SizedBox(height: 10),
        Text(
          feature.label,
          textAlign: TextAlign.center,
          style: AppText.body(
            size: 12,
            weight: FontWeight.w600,
            color: AppColors.ink,
          ).copyWith(height: 1.3),
        ),
      ],
    );
  }
}

class _StartExploringButton extends StatefulWidget {
  final VoidCallback onTap;
  const _StartExploringButton({required this.onTap});

  @override
  State<_StartExploringButton> createState() => _StartExploringButtonState();
}

class _StartExploringButtonState extends State<_StartExploringButton> {
  bool _hover = false;

  @override
  Widget build(BuildContext context) {
    return MouseRegion(
      cursor: SystemMouseCursors.click,
      onEnter: (_) => setState(() => _hover = true),
      onExit: (_) => setState(() => _hover = false),
      child: GestureDetector(
        onTap: widget.onTap,
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 160),
          padding: const EdgeInsets.symmetric(horizontal: 26, vertical: 15),
          decoration: BoxDecoration(
            color: _hover ? const Color(0xFF1E5BC9) : _brandBlue,
            borderRadius: BorderRadius.circular(999),
            boxShadow: [
              BoxShadow(
                color: _brandBlue.withValues(alpha: _hover ? 0.4 : 0.25),
                blurRadius: _hover ? 20 : 12,
                offset: const Offset(0, 6),
              ),
            ],
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Icon(Icons.auto_awesome, color: Colors.white, size: 18),
              const SizedBox(width: 10),
              Text(
                'Start Exploring',
                style: AppText.body(
                  size: 15,
                  weight: FontWeight.w600,
                  color: Colors.white,
                ),
              ),
              const SizedBox(width: 10),
              const Icon(Icons.arrow_forward, color: Colors.white, size: 18),
            ],
          ),
        ),
      ),
    );
  }
}

// ---------- MIND-MAP PREVIEW ----------
// Shown next to the hero copy. Only the cognitive graph: no sidebar, no top
// bar, no assistant panel — the single mind-map a user sees once they query.
class _HeroDashboard extends StatelessWidget {
  final GraphPhase phase;
  final VoidCallback onReplay;
  const _HeroDashboard({required this.phase, required this.onReplay});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onReplay,
      child: Container(
        padding: const EdgeInsets.fromLTRB(20, 20, 20, 44),
        decoration: BoxDecoration(
          color: Colors.white,
          border: Border.all(color: AppColors.line),
          borderRadius: BorderRadius.circular(24),
          boxShadow: [
            BoxShadow(
              color: _brandBlue.withValues(alpha: 0.12),
              blurRadius: 40,
              offset: const Offset(0, 18),
              spreadRadius: -14,
            ),
          ],
        ),
        child: Stack(
          children: [
            Positioned.fill(child: SituationGraph(phase: phase)),
            Positioned(
              left: 0,
              bottom: 0,
              child: _GraphLegend(),
            ),
            Positioned(
              right: 0,
              top: 0,
              child: _PhaseTag(phase: phase),
            ),
          ],
        ),
      ),
    );
  }
}

class _PhaseTag extends StatelessWidget {
  final GraphPhase phase;
  const _PhaseTag({required this.phase});

  @override
  Widget build(BuildContext context) {
    late final String label;
    late final Color color;
    switch (phase) {
      case GraphPhase.verified:
        label = 'VERIFIED';
        color = AppColors.sage;
        break;
      case GraphPhase.change:
        label = 'CHANGE';
        color = AppColors.amber;
        break;
      case GraphPhase.repaired:
        label = 'REPAIRED';
        color = AppColors.sage;
        break;
    }
    return _LiveTag(label: label, color: color);
  }
}

class _LiveTag extends StatefulWidget {
  final String label;
  final Color color;
  const _LiveTag({required this.label, required this.color});

  @override
  State<_LiveTag> createState() => _LiveTagState();
}

class _LiveTagState extends State<_LiveTag>
    with SingleTickerProviderStateMixin {
  late final AnimationController _c;

  @override
  void initState() {
    super.initState();
    _c = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1400),
    )..repeat(reverse: true);
  }

  @override
  void dispose() {
    _c.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
      decoration: BoxDecoration(
        color: widget.color.withValues(alpha: 0.14),
        borderRadius: BorderRadius.circular(999),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          AnimatedBuilder(
            animation: _c,
            builder: (_, _) => Container(
              width: 6,
              height: 6,
              decoration: BoxDecoration(
                color: widget.color.withValues(alpha: 0.4 + _c.value * 0.6),
                shape: BoxShape.circle,
              ),
            ),
          ),
          const SizedBox(width: 6),
          Text(
            widget.label,
            style: AppText.mono(size: 10, color: widget.color),
          ),
        ],
      ),
    );
  }
}

class _GraphLegend extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    const entries = [
      _LegendEntry('Fact', AppColors.sage),
      _LegendEntry('Observation', _brandBlue),
      _LegendEntry('Prediction', _brandViolet),
      _LegendEntry('Change', AppColors.amber),
      _LegendEntry('Risk', AppColors.crimson),
    ];
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.9),
        border: Border.all(color: AppColors.line),
        borderRadius: BorderRadius.circular(999),
      ),
      child: Wrap(
        spacing: 12,
        runSpacing: 4,
        children: entries.map(_dot).toList(),
      ),
    );
  }

  Widget _dot(_LegendEntry e) => Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: 7,
            height: 7,
            decoration: BoxDecoration(color: e.c, shape: BoxShape.circle),
          ),
          const SizedBox(width: 5),
          Text(e.label, style: AppText.mono(size: 10)),
        ],
      );
}

class _LegendEntry {
  final String label;
  final Color c;
  const _LegendEntry(this.label, this.c);
}

