import 'package:flutter/material.dart';

import '../theme/app_theme.dart';
import 'responsive.dart';

class FeaturesBar extends StatelessWidget {
  const FeaturesBar({super.key});

  @override
  Widget build(BuildContext context) {
    final size = screenSizeOf(context);
    final isStacked = size == ScreenSize.phone;
    const features = [
      _Feature('Dynamic cognitive graph', Icons.hub_outlined),
      _Feature('Evidence & provenance', Icons.verified_outlined),
      _Feature('Reasoning & constraints', Icons.psychology_outlined),
      _Feature('Adaptive replanning', Icons.sync_outlined),
      _Feature('Human-in-the-loop', Icons.person_outline),
    ];

    return PageWrap(
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 24),
        child: isStacked
            ? Column(
                children: features
                    .map((f) => Padding(
                          padding: const EdgeInsets.only(bottom: 10),
                          child: _FeaturePill(feature: f),
                        ))
                    .toList(),
              )
            : Wrap(
                spacing: 16,
                runSpacing: 12,
                alignment: WrapAlignment.center,
                children: features.map((f) => _FeaturePill(feature: f)).toList(),
              ),
      ),
    );
  }
}

class _Feature {
  final String label;
  final IconData icon;
  const _Feature(this.label, this.icon);
}

class _FeaturePill extends StatefulWidget {
  final _Feature feature;
  const _FeaturePill({required this.feature});

  @override
  State<_FeaturePill> createState() => _FeaturePillState();
}

class _FeaturePillState extends State<_FeaturePill> {
  bool _hover = false;

  @override
  Widget build(BuildContext context) {
    return MouseRegion(
      cursor: SystemMouseCursors.click,
      onEnter: (_) => setState(() => _hover = true),
      onExit: (_) => setState(() => _hover = false),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 150),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        decoration: BoxDecoration(
          color: AppColors.surface,
          border: Border.all(
            color: _hover ? AppColors.accent : AppColors.line,
          ),
          borderRadius: BorderRadius.circular(999),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 28,
              height: 28,
              decoration: BoxDecoration(
                color: AppColors.accent.withValues(alpha: 0.12),
                shape: BoxShape.circle,
              ),
              alignment: Alignment.center,
              child: Icon(
                widget.feature.icon,
                size: 16,
                color: AppColors.accent,
              ),
            ),
            const SizedBox(width: 10),
            Text(
              widget.feature.label,
              style: AppText.body(
                size: 13.5,
                weight: FontWeight.w500,
                color: AppColors.ink,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
