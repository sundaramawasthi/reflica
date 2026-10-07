import 'package:flutter/material.dart';

import '../theme/app_theme.dart';
import 'responsive.dart';

const _brandBlue = Color(0xFF2E6FEB);
const _brandViolet = Color(0xFF7A5BE8);

class InputModesSection extends StatelessWidget {
  const InputModesSection({super.key});

  @override
  Widget build(BuildContext context) {
    const modes = <_Mode>[
      _Mode('01', 'Free text', 'Describe your situation in your own words.',
          Icons.short_text, _brandBlue),
      _Mode('02', 'Structured form', 'Fill goal, entities, constraints step by step.',
          Icons.view_list_outlined, AppColors.sage),
      _Mode('03', 'Voice', 'Record a spoken brief or upload audio.',
          Icons.mic_none, _brandViolet),
      _Mode('04', 'Documents', 'PDFs, reports, spreadsheets — multi-file.',
          Icons.description_outlined, AppColors.amber),
      _Mode('05', 'Images', 'Photos, scans, satellite tiles.',
          Icons.image_outlined, AppColors.crimson),
      _Mode('06', 'Video', 'Brief clips of the situation or CCTV.',
          Icons.videocam_outlined, AppColors.accent),
      _Mode('07', 'Live camera', 'Capture directly from device camera.',
          Icons.photo_camera_outlined, _brandBlue),
    ];

    return Container(
      color: Colors.white,
      padding: const EdgeInsets.symmetric(vertical: 96),
      child: PageWrap(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _Header(),
            const SizedBox(height: 40),
            LayoutBuilder(builder: (ctx, c) {
              final cols = c.maxWidth < 560
                  ? 1
                  : c.maxWidth < 820
                      ? 2
                      : c.maxWidth < 1180
                          ? 3
                          : 4;
              const gap = 16.0;
              final cardWidth =
                  ((c.maxWidth - (cols - 1) * gap) / cols).floorToDouble();
              return Wrap(
                spacing: gap,
                runSpacing: gap,
                children: modes
                    .map((m) => SizedBox(
                          width: cardWidth,
                          child: _ModeCard(mode: m),
                        ))
                    .toList(),
              );
            }),
            const SizedBox(height: 32),
            const _TypedOutput(),
          ],
        ),
      ),
    );
  }
}

class _Header extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
          decoration: BoxDecoration(
            color: _brandBlue.withValues(alpha: 0.08),
            borderRadius: BorderRadius.circular(999),
          ),
          child: Text(
            'SEVEN WAYS TO GIVE INPUT',
            style: AppText.mono(
              size: 10,
              color: _brandBlue,
            ).copyWith(letterSpacing: 1.5, fontWeight: FontWeight.w600),
          ),
        ),
        const SizedBox(height: 20),
        Text(
          'Whatever the medium, one shared graph.',
          style: AppText.serif(size: 42, weight: FontWeight.w600),
        ),
        const SizedBox(height: 16),
        ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 680),
          child: Text(
            'Reflica takes seven kinds of input and resolves every one into the '
            'same typed cognitive graph. Mix and match as the situation evolves — '
            'the structure stays coherent, the audit trail stays intact.',
            style: AppText.body(size: 16, color: AppColors.ink2),
          ),
        ),
      ],
    );
  }
}

class _Mode {
  final String number;
  final String title;
  final String sub;
  final IconData icon;
  final Color color;
  const _Mode(this.number, this.title, this.sub, this.icon, this.color);
}

class _ModeCard extends StatefulWidget {
  final _Mode mode;
  const _ModeCard({required this.mode});

  @override
  State<_ModeCard> createState() => _ModeCardState();
}

class _ModeCardState extends State<_ModeCard> {
  bool _hover = false;

  @override
  Widget build(BuildContext context) {
    final m = widget.mode;
    return MouseRegion(
      cursor: SystemMouseCursors.click,
      onEnter: (_) => setState(() => _hover = true),
      onExit: (_) => setState(() => _hover = false),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 180),
        transform: Matrix4.translationValues(0, _hover ? -3 : 0, 0),
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: Colors.white,
          border: Border.all(
            color: _hover ? m.color.withValues(alpha: 0.6) : AppColors.line,
            width: _hover ? 1.5 : 1,
          ),
          borderRadius: BorderRadius.circular(14),
          boxShadow: _hover
              ? [
                  BoxShadow(
                    color: m.color.withValues(alpha: 0.14),
                    blurRadius: 24,
                    offset: const Offset(0, 10),
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
              children: [
                Container(
                  width: 44,
                  height: 44,
                  decoration: BoxDecoration(
                    color: m.color.withValues(alpha: 0.12),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  alignment: Alignment.center,
                  child: Icon(m.icon, color: m.color, size: 22),
                ),
                const Spacer(),
                Text(
                  m.number,
                  style: AppText.mono(
                    size: 11,
                    color: AppColors.muted,
                  ).copyWith(letterSpacing: 1.2),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Text(
              m.title,
              style: AppText.serif(size: 18, weight: FontWeight.w600),
            ),
            const SizedBox(height: 6),
            Text(
              m.sub,
              style: AppText.body(size: 13, color: AppColors.ink2),
              maxLines: 3,
              overflow: TextOverflow.ellipsis,
            ),
          ],
        ),
      ),
    );
  }
}

class _TypedOutput extends StatelessWidget {
  const _TypedOutput();

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: const Color(0xFFF6F8FC),
        border: Border.all(color: AppColors.line),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          Icon(Icons.lock_outline, size: 18, color: _brandViolet),
          const SizedBox(width: 12),
          Expanded(
            child: RichText(
              text: TextSpan(
                style: AppText.body(size: 13.5, color: AppColors.ink2),
                children: [
                  TextSpan(
                    text: 'One typed output. ',
                    style: AppText.body(
                      size: 13.5,
                      weight: FontWeight.w600,
                      color: AppColors.ink,
                    ),
                  ),
                  const TextSpan(
                    text: 'Every input mode produces the same JSON shape — nodes with '
                        'evidence type, source, timestamp and confidence, plus typed '
                        'edges. The graph never cares which modality the fact came '
                        'from, which is exactly what makes revision tractable.',
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
