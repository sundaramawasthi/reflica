import 'package:flutter/material.dart';

import '../../theme/app_theme.dart';

class _Step {
  final String name;
  final String sub;
  final IconData icon;
  final Color color;
  const _Step(this.name, this.sub, this.icon, this.color);
}

const _steps = <_Step>[
  _Step('Understand', '(AI)', Icons.search_outlined, AppColors.accent),
  _Step('Represent', '(Graph)', Icons.hub_outlined, AppColors.sage),
  _Step('Plan', '(LLM)', Icons.edit_outlined, AppColors.violet),
  _Step('Verify', '(Rules)', Icons.verified_outlined, AppColors.amber),
  _Step('Adapt', '(Replan)', Icons.sync_outlined, AppColors.crimson),
];

class HowItWorksStrip extends StatelessWidget {
  const HowItWorksStrip({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: AppColors.surface,
        border: Border.all(color: AppColors.line),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            children: [
              Icon(Icons.lightbulb_outline,
                  size: 18, color: AppColors.amber),
              const SizedBox(width: 10),
              Text('How It Works',
                  style: AppText.serif(size: 18, weight: FontWeight.w500)),
            ],
          ),
          const SizedBox(height: 20),
          LayoutBuilder(builder: (context, c) {
            final isTight = c.maxWidth < 420;
            return isTight
                ? Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      for (int i = 0; i < _steps.length; i++) ...[
                        _StepItem(step: _steps[i], tight: true),
                        if (i < _steps.length - 1)
                          Padding(
                            padding: const EdgeInsets.only(left: 20),
                            child: Container(
                              width: 2,
                              height: 20,
                              color: AppColors.line,
                            ),
                          ),
                      ],
                    ],
                  )
                : Row(
                    children: [
                      for (int i = 0; i < _steps.length; i++) ...[
                        Expanded(child: _StepItem(step: _steps[i])),
                        if (i < _steps.length - 1)
                          Padding(
                            padding: const EdgeInsets.symmetric(horizontal: 2),
                            child: Icon(Icons.arrow_forward,
                                size: 14, color: AppColors.muted),
                          ),
                      ],
                    ],
                  );
          }),
        ],
      ),
    );
  }
}

class _StepItem extends StatelessWidget {
  final _Step step;
  final bool tight;
  const _StepItem({required this.step, this.tight = false});

  @override
  Widget build(BuildContext context) {
    if (tight) {
      return Row(
        children: [
          Container(
            width: 42,
            height: 42,
            decoration: BoxDecoration(
              color: step.color.withValues(alpha: 0.12),
              shape: BoxShape.circle,
            ),
            alignment: Alignment.center,
            child: Icon(step.icon, color: step.color, size: 20),
          ),
          const SizedBox(width: 12),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                step.name,
                style: AppText.body(
                  size: 13,
                  weight: FontWeight.w500,
                  color: AppColors.ink,
                ),
              ),
              Text(step.sub, style: AppText.mono(size: 11)),
            ],
          ),
        ],
      );
    }
    return Column(
      children: [
        Container(
          width: 42,
          height: 42,
          decoration: BoxDecoration(
            color: step.color.withValues(alpha: 0.12),
            shape: BoxShape.circle,
          ),
          alignment: Alignment.center,
          child: Icon(step.icon, color: step.color, size: 20),
        ),
        const SizedBox(height: 8),
        Text(
          step.name,
          style: AppText.body(
            size: 12,
            weight: FontWeight.w500,
            color: AppColors.ink,
          ),
        ),
        Text(step.sub, style: AppText.mono(size: 10)),
      ],
    );
  }
}
