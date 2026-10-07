import 'package:flutter/material.dart';

import '../theme/app_theme.dart';
import 'responsive.dart';

class EvidenceSection extends StatelessWidget {
  const EvidenceSection({super.key});

  @override
  Widget build(BuildContext context) {
    const items = [
      _Evidence(
        n: '01',
        name: 'Fact',
        chip: 'source',
        desc: 'Established by a trusted record. Treated as ground until retracted.',
        example: 'University exam starts 10:00 AM',
        exampleMeta: 'src · university notice · reliability high',
        color: AppColors.sage,
      ),
      _Evidence(
        n: '02',
        name: 'Observation',
        chip: 'sensor',
        desc: 'Something the system directly perceived — camera, report, message.',
        example: 'Road A appears blocked',
        exampleMeta: 'src · field report 17 · 11:20 · c 0.87',
        color: AppColors.accent,
      ),
      _Evidence(
        n: '03',
        name: 'Prediction',
        chip: 'derived',
        desc: 'Something expected to happen. Carries uncertainty; verified only after.',
        example: 'T1 reaches Shelter A at 14:30',
        exampleMeta: 'src · planner · c 0.82',
        color: AppColors.violet,
      ),
      _Evidence(
        n: '04',
        name: 'Hypothesis',
        chip: 'why',
        desc: 'A possible explanation. Shapes options, never confused with reality.',
        example: 'Blockage caused by landslide',
        exampleMeta: 'src · inference · competing · c 0.6',
        color: AppColors.amber,
      ),
      _Evidence(
        n: '05',
        name: 'Assumption',
        chip: 'flagged',
        desc: 'A planning premise. Explicitly flagged so you know the plan rests on it.',
        example: 'Road B stays open all day',
        exampleMeta: 'src · none · marked for review',
        color: AppColors.crimson,
      ),
    ];

    return Container(
      color: AppColors.surface2,
      padding: const EdgeInsets.symmetric(vertical: 96),
      child: PageWrap(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('02 · EVIDENCE', style: AppText.eyebrow()),
            const SizedBox(height: 16),
            ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 760),
              child: Text(
                'Five kinds of information. Reflica never confuses them.',
                style: AppText.serif(size: 40, weight: FontWeight.w400),
              ),
            ),
            const SizedBox(height: 18),
            ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 760),
              child: Text(
                'An LLM-generated prediction is not a fact. A field officer’s camera '
                'report is not a planning assumption. Reflica tags every claim so the '
                'planner, the verifier, and you can tell them apart.',
                style: AppText.body(size: 17),
              ),
            ),
            const SizedBox(height: 48),
            LayoutBuilder(builder: (context, c) {
              final cols = c.maxWidth < 560
                  ? 1
                  : c.maxWidth < 980
                      ? 2
                      : 5;
              const gap = 14.0;
              final cardWidth =
                  ((c.maxWidth - (cols - 1) * gap) / cols).floorToDouble();
              return Wrap(
                spacing: gap,
                runSpacing: gap,
                children: items
                    .map((e) => SizedBox(
                          width: cardWidth,
                          child: _EvidenceCard(ev: e),
                        ))
                    .toList(),
              );
            }),
          ],
        ),
      ),
    );
  }
}

class _Evidence {
  final String n;
  final String name;
  final String chip;
  final String desc;
  final String example;
  final String exampleMeta;
  final Color color;
  const _Evidence({
    required this.n,
    required this.name,
    required this.chip,
    required this.desc,
    required this.example,
    required this.exampleMeta,
    required this.color,
  });
}

class _EvidenceCard extends StatefulWidget {
  final _Evidence ev;
  const _EvidenceCard({required this.ev});

  @override
  State<_EvidenceCard> createState() => _EvidenceCardState();
}

class _EvidenceCardState extends State<_EvidenceCard> {
  bool _hover = false;

  @override
  Widget build(BuildContext context) {
    final e = widget.ev;
    return MouseRegion(
      onEnter: (_) => setState(() => _hover = true),
      onExit: (_) => setState(() => _hover = false),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 180),
        transform: Matrix4.translationValues(0, _hover ? -3 : 0, 0),
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: AppColors.surface,
          border: Border.all(
            color: _hover ? AppColors.lineStrong : AppColors.line,
          ),
          borderRadius: BorderRadius.circular(12),
          boxShadow: _hover
              ? [
                  BoxShadow(
                    color: AppColors.ink.withValues(alpha: 0.06),
                    blurRadius: 24,
                    offset: const Offset(0, 8),
                    spreadRadius: -8,
                  ),
                ]
              : [],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              crossAxisAlignment: CrossAxisAlignment.center,
              children: [
                Text(
                  e.n,
                  style: AppText.serif(size: 36, weight: FontWeight.w400)
                      .copyWith(color: e.color, height: 1),
                ),
                Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                  decoration: BoxDecoration(
                    color: AppColors.surface2,
                    border: Border.all(color: AppColors.line),
                    borderRadius: BorderRadius.circular(999),
                  ),
                  child: Text(
                    e.chip.toUpperCase(),
                    style: AppText.mono(size: 10, color: AppColors.muted),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 14),
            Text(e.name,
                style: AppText.serif(size: 18, weight: FontWeight.w500),
                maxLines: 1,
                overflow: TextOverflow.ellipsis),
            const SizedBox(height: 8),
            Text(
              e.desc,
              style: AppText.body(size: 13.5, color: AppColors.ink2),
              maxLines: 3,
              overflow: TextOverflow.ellipsis,
            ),
            const SizedBox(height: 14),
            Container(
              padding: const EdgeInsets.only(top: 12),
              decoration: const BoxDecoration(
                border: Border(top: BorderSide(color: AppColors.line)),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    e.example,
                    style: AppText.mono(
                      size: 12.5,
                      color: AppColors.ink2,
                      weight: FontWeight.w500,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    e.exampleMeta,
                    style: AppText.mono(size: 11),
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
