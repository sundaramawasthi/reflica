import 'package:flutter/material.dart';

import '../../models/plan.dart';
import '../../screens/new_plan_flow.dart';
import '../../theme/app_theme.dart';

const _brandBlue = Color(0xFF2E6FEB);
const _brandViolet = Color(0xFF7A5BE8);

class QuickInputStrip extends StatelessWidget {
  const QuickInputStrip({super.key});

  @override
  Widget build(BuildContext context) {
    const items = <_InputItem>[
      _InputItem(InputMode.text, _brandBlue),
      _InputItem(InputMode.form, AppColors.sage),
      _InputItem(InputMode.voice, _brandViolet),
      _InputItem(InputMode.document, AppColors.amber),
      _InputItem(InputMode.image, AppColors.crimson),
      _InputItem(InputMode.video, AppColors.accent),
      _InputItem(InputMode.camera, _brandBlue),
    ];

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: AppColors.surface,
        border: Border.all(color: AppColors.line),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.flash_on_outlined, size: 18, color: _brandBlue),
              const SizedBox(width: 10),
              Text(
                'Quick capture',
                style: AppText.serif(size: 18, weight: FontWeight.w500),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: Text(
                  '· pick an input mode and jump straight in',
                  style: AppText.body(size: 13, color: AppColors.muted),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          LayoutBuilder(builder: (ctx, c) {
            final cols = c.maxWidth < 480
                ? 2
                : c.maxWidth < 760
                    ? 3
                    : c.maxWidth < 1080
                        ? 4
                        : 7;
            const gap = 10.0;
            final cardWidth =
                ((c.maxWidth - (cols - 1) * gap) / cols).floorToDouble();
            return Wrap(
              spacing: gap,
              runSpacing: gap,
              children: items
                  .map((item) => SizedBox(
                        width: cardWidth,
                        child: _InputCard(item: item),
                      ))
                  .toList(),
            );
          }),
        ],
      ),
    );
  }
}

class _InputItem {
  final InputMode mode;
  final Color color;
  const _InputItem(this.mode, this.color);
}

class _InputCard extends StatefulWidget {
  final _InputItem item;
  const _InputCard({required this.item});

  @override
  State<_InputCard> createState() => _InputCardState();
}

class _InputCardState extends State<_InputCard> {
  bool _hover = false;

  @override
  Widget build(BuildContext context) {
    final mode = widget.item.mode;
    final color = widget.item.color;
    return MouseRegion(
      cursor: SystemMouseCursors.click,
      onEnter: (_) => setState(() => _hover = true),
      onExit: (_) => setState(() => _hover = false),
      child: GestureDetector(
        onTap: () => Navigator.of(context).pushNamed(
          '/new-plan',
          arguments: NewPlanArgs(mode: mode),
        ),
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 150),
          transform: Matrix4.translationValues(0, _hover ? -2 : 0, 0),
          padding: const EdgeInsets.symmetric(vertical: 14, horizontal: 10),
          decoration: BoxDecoration(
            color: _hover
                ? color.withValues(alpha: 0.08)
                : Colors.white,
            border: Border.all(
              color: _hover ? color : AppColors.line,
              width: _hover ? 1.2 : 1,
            ),
            borderRadius: BorderRadius.circular(10),
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                width: 36,
                height: 36,
                decoration: BoxDecoration(
                  color: color.withValues(alpha: 0.12),
                  shape: BoxShape.circle,
                ),
                alignment: Alignment.center,
                child: Icon(mode.icon, color: color, size: 18),
              ),
              const SizedBox(height: 8),
              Text(
                mode.label,
                textAlign: TextAlign.center,
                style: AppText.body(
                  size: 12,
                  weight: FontWeight.w600,
                  color: AppColors.ink,
                ),
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
              ),
            ],
          ),
        ),
      ),
    );
  }
}
