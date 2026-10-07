import 'package:flutter/material.dart';

import '../../models/plan.dart';
import '../../services/plan_repository.dart';
import '../../theme/app_theme.dart';

class ActivityTable extends StatelessWidget {
  const ActivityTable({super.key});

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
              Icon(Icons.schedule, size: 18, color: AppColors.accent),
              const SizedBox(width: 10),
              Expanded(
                child: Text('Recent Activity',
                    style: AppText.serif(size: 18, weight: FontWeight.w500),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis),
              ),
              GestureDetector(
                onTap: () => Navigator.of(context).pushNamed('/plans'),
                child: Text(
                  'View all →',
                  style: AppText.body(
                    size: 13,
                    color: AppColors.accent,
                    weight: FontWeight.w500,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 18),
          StreamBuilder<List<Plan>>(
            stream: PlanRepository.instance.watchMyPlans(),
            builder: (context, snap) {
              if (snap.connectionState == ConnectionState.waiting &&
                  !snap.hasData) {
                return const Padding(
                  padding: EdgeInsets.symmetric(vertical: 24),
                  child: Center(
                    child: SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        valueColor:
                            AlwaysStoppedAnimation(AppColors.accent),
                      ),
                    ),
                  ),
                );
              }
              final plans = snap.data ?? const [];
              if (plans.isEmpty) return const _EmptyRow();

              // Responsive: on wide screens render the 5-column table, on
              // narrow phones (<760px) render stacked cards instead.
              return LayoutBuilder(builder: (ctx, c) {
                final isNarrow = c.maxWidth < 760;
                if (isNarrow) {
                  return Column(
                    children: plans.take(6)
                        .map((p) => _ActivityCard(plan: p))
                        .toList(),
                  );
                }
                return Column(
                  children: [
                    _TableHeader(),
                    const SizedBox(height: 8),
                    ...plans.take(6).map((p) => _PlanRow(plan: p)),
                  ],
                );
              });
            },
          ),
        ],
      ),
    );
  }
}

// -------- mobile card layout --------

class _ActivityCard extends StatefulWidget {
  final Plan plan;
  const _ActivityCard({required this.plan});

  @override
  State<_ActivityCard> createState() => _ActivityCardState();
}

class _ActivityCardState extends State<_ActivityCard> {
  bool _pressed = false;

  @override
  Widget build(BuildContext context) {
    final p = widget.plan;
    final audienceColor = _audienceColor(p.audience);
    return GestureDetector(
      onTap: () => Navigator.of(context).pushNamed('/plan', arguments: p.id),
      onTapDown: (_) => setState(() => _pressed = true),
      onTapUp: (_) => setState(() => _pressed = false),
      onTapCancel: () => setState(() => _pressed = false),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 120),
        margin: const EdgeInsets.only(bottom: 10),
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: _pressed ? AppColors.surface2 : AppColors.surface,
          border: Border.all(color: AppColors.line),
          borderRadius: BorderRadius.circular(12),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  width: 36,
                  height: 36,
                  decoration: BoxDecoration(
                    color: audienceColor.withValues(alpha: 0.12),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  alignment: Alignment.center,
                  child: Icon(p.audience.icon, size: 18, color: audienceColor),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        p.title,
                        style: AppText.body(
                          size: 14.5,
                          weight: FontWeight.w600,
                          color: AppColors.ink,
                        ),
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                      ),
                      const SizedBox(height: 2),
                      Text(
                        _relative(p.updatedAt),
                        style: AppText.mono(size: 11),
                      ),
                    ],
                  ),
                ),
                _StatusPill(status: p.status),
              ],
            ),
            const SizedBox(height: 12),
            Wrap(
              spacing: 8,
              runSpacing: 6,
              children: [
                _MetaChip(
                  icon: p.audience.icon,
                  label: p.audience.label,
                  color: audienceColor,
                ),
                _MetaChip(
                  icon: p.inputMode.icon,
                  label: p.inputMode.label,
                  color: AppColors.accent,
                ),
                _MetaChip(
                  icon: Icons.layers_outlined,
                  label: '${p.nodes.length} nodes',
                  color: AppColors.muted,
                ),
                _MetaChip(
                  icon: Icons.alt_route_outlined,
                  label: '${p.edges.length} edges',
                  color: AppColors.muted,
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _MetaChip extends StatelessWidget {
  final IconData icon;
  final String label;
  final Color color;
  const _MetaChip({
    required this.icon,
    required this.label,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(999),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 12, color: color),
          const SizedBox(width: 5),
          Text(
            label,
            style: AppText.body(
              size: 11.5,
              weight: FontWeight.w500,
              color: color,
            ),
          ),
        ],
      ),
    );
  }
}

// -------- desktop table layout --------

class _TableHeader extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 6),
      child: Row(
        children: [
          Expanded(flex: 5, child: Text('PLAN', style: AppText.eyebrow())),
          Expanded(flex: 2, child: Text('AUDIENCE', style: AppText.eyebrow())),
          Expanded(flex: 2, child: Text('INPUT', style: AppText.eyebrow())),
          Expanded(flex: 2, child: Text('UPDATED', style: AppText.eyebrow())),
          Expanded(flex: 2, child: Text('STATUS', style: AppText.eyebrow())),
          const SizedBox(width: 24),
        ],
      ),
    );
  }
}

class _PlanRow extends StatefulWidget {
  final Plan plan;
  const _PlanRow({required this.plan});

  @override
  State<_PlanRow> createState() => _PlanRowState();
}

class _PlanRowState extends State<_PlanRow> {
  bool _hover = false;

  @override
  Widget build(BuildContext context) {
    final p = widget.plan;
    final audienceColor = _audienceColor(p.audience);
    return MouseRegion(
      cursor: SystemMouseCursors.click,
      onEnter: (_) => setState(() => _hover = true),
      onExit: (_) => setState(() => _hover = false),
      child: GestureDetector(
        onTap: () =>
            Navigator.of(context).pushNamed('/plan', arguments: p.id),
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 120),
          padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 12),
          decoration: BoxDecoration(
            color: _hover ? AppColors.surface2 : Colors.transparent,
            borderRadius: BorderRadius.circular(10),
            border: const Border(top: BorderSide(color: AppColors.line)),
          ),
          child: Row(
            children: [
              Expanded(
                flex: 5,
                child: Row(
                  children: [
                    Container(
                      width: 36,
                      height: 36,
                      decoration: BoxDecoration(
                        color: audienceColor.withValues(alpha: 0.12),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      alignment: Alignment.center,
                      child: Icon(p.audience.icon,
                          size: 18, color: audienceColor),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            p.title,
                            style: AppText.body(
                              size: 14,
                              weight: FontWeight.w500,
                              color: AppColors.ink,
                            ),
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                          Text(
                            '${p.nodes.length} nodes · ${p.edges.length} edges',
                            style: AppText.mono(size: 11),
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
              Expanded(
                flex: 2,
                child: _Pill(label: p.audience.label, color: audienceColor),
              ),
              Expanded(
                flex: 2,
                child: Row(
                  children: [
                    Icon(p.inputMode.icon, size: 14, color: AppColors.muted),
                    const SizedBox(width: 6),
                    Flexible(
                      child: Text(
                        p.inputMode.label,
                        style: AppText.mono(size: 12),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                  ],
                ),
              ),
              Expanded(
                flex: 2,
                child: Text(_relative(p.updatedAt),
                    style: AppText.mono(size: 12),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis),
              ),
              Expanded(flex: 2, child: _StatusPill(status: p.status)),
              SizedBox(
                width: 24,
                child: Icon(Icons.arrow_forward,
                    size: 16,
                    color: _hover ? AppColors.accent : AppColors.muted),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// -------- shared --------

Color _audienceColor(Audience a) {
  switch (a) {
    case Audience.individual:
      return AppColors.accent;
    case Audience.organization:
      return AppColors.sage;
    case Audience.research:
      return AppColors.amber;
    case Audience.government:
      return AppColors.violet;
    case Audience.disaster:
      return AppColors.crimson;
  }
}

String _relative(DateTime t) {
  final diff = DateTime.now().difference(t);
  if (diff.inSeconds < 60) return 'just now';
  if (diff.inMinutes < 60) return '${diff.inMinutes}m ago';
  if (diff.inHours < 24) return '${diff.inHours}h ago';
  return '${diff.inDays}d ago';
}

class _Pill extends StatelessWidget {
  final String label;
  final Color color;
  const _Pill({required this.label, required this.color});

  @override
  Widget build(BuildContext context) {
    return Align(
      alignment: Alignment.centerLeft,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
        decoration: BoxDecoration(
          color: color.withValues(alpha: 0.12),
          borderRadius: BorderRadius.circular(999),
        ),
        child: Text(
          label,
          style: AppText.body(
            size: 12,
            weight: FontWeight.w500,
            color: color,
          ),
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
        ),
      ),
    );
  }
}

class _StatusPill extends StatelessWidget {
  final PlanStatus status;
  const _StatusPill({required this.status});

  @override
  Widget build(BuildContext context) {
    final (label, color) = switch (status) {
      PlanStatus.draft => ('Draft', AppColors.muted),
      PlanStatus.verified => ('Verified', AppColors.sage),
      PlanStatus.changed => ('Change', AppColors.amber),
      PlanStatus.repaired => ('Repaired', AppColors.sage),
    };
    return _Pill(label: label, color: color);
  }
}

class _EmptyRow extends StatelessWidget {
  const _EmptyRow();

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 24),
      decoration: const BoxDecoration(
        border: Border(top: BorderSide(color: AppColors.line)),
      ),
      child: Column(
        children: [
          Icon(Icons.inbox_outlined, size: 24, color: AppColors.muted),
          const SizedBox(height: 8),
          Text(
            'No plans yet',
            style: AppText.body(
              size: 14,
              weight: FontWeight.w500,
              color: AppColors.ink2,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            'Click "Start Planning" above to create your first one.',
            style: AppText.body(size: 12, color: AppColors.muted),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }
}
