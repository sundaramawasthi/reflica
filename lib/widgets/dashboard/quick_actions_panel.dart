import 'package:flutter/material.dart';

import '../../theme/app_theme.dart';

class _Action {
  final String title;
  final String desc;
  final IconData icon;
  final String route;
  const _Action(this.title, this.desc, this.icon, this.route);
}

const _actions = <_Action>[
  _Action('Create New Plan', 'Start planning for a new goal or situation',
      Icons.add_box_outlined, '/new-plan'),
  _Action('Upload Document', 'Add files, reports or data',
      Icons.upload_file_outlined, '/documents'),
  _Action('View Knowledge Graph', 'Explore your current situation graph',
      Icons.hub_outlined, '/graph'),
  _Action('Explore Scenarios', 'Test different what-if scenarios',
      Icons.layers_outlined, '/scenarios'),
];

class QuickActionsPanel extends StatelessWidget {
  const QuickActionsPanel({super.key});

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
              Icon(Icons.flash_on_outlined, size: 18, color: AppColors.amber),
              const SizedBox(width: 10),
              Text('Quick Actions',
                  style: AppText.serif(size: 18, weight: FontWeight.w500)),
            ],
          ),
          const SizedBox(height: 16),
          ..._actions.map((a) => _ActionRow(action: a)),
        ],
      ),
    );
  }
}

class _ActionRow extends StatefulWidget {
  final _Action action;
  const _ActionRow({required this.action});

  @override
  State<_ActionRow> createState() => _ActionRowState();
}

class _ActionRowState extends State<_ActionRow> {
  bool _hover = false;

  @override
  Widget build(BuildContext context) {
    final a = widget.action;
    return MouseRegion(
      cursor: SystemMouseCursors.click,
      onEnter: (_) => setState(() => _hover = true),
      onExit: (_) => setState(() => _hover = false),
      child: GestureDetector(
        onTap: () => Navigator.of(context).pushNamed(a.route),
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 150),
          margin: const EdgeInsets.only(bottom: 8),
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: _hover ? AppColors.surface2 : AppColors.surface,
            border: Border.all(
              color: _hover ? AppColors.lineStrong : AppColors.line,
            ),
            borderRadius: BorderRadius.circular(10),
          ),
          child: Row(
            children: [
              Container(
                width: 40,
                height: 40,
                decoration: BoxDecoration(
                  color: AppColors.accent.withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                alignment: Alignment.center,
                child: Icon(a.icon, color: AppColors.accent, size: 18),
              ),
              const SizedBox(width: 14),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      a.title,
                      style: AppText.body(
                        size: 14,
                        weight: FontWeight.w500,
                        color: AppColors.ink,
                      ),
                    ),
                    Text(
                      a.desc,
                      style: AppText.body(size: 12, color: AppColors.muted),
                    ),
                  ],
                ),
              ),
              Icon(Icons.arrow_forward,
                  size: 16,
                  color: _hover ? AppColors.accent : AppColors.muted),
            ],
          ),
        ),
      ),
    );
  }
}
