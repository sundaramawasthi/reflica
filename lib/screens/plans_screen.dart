import 'package:flutter/material.dart';

import '../models/plan.dart';
import '../services/plan_repository.dart';
import '../theme/app_theme.dart';
import '../widgets/dashboard/dashboard_sidebar.dart';
import '../widgets/responsive.dart';

class PlansScreen extends StatelessWidget {
  const PlansScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final showSidebar =
        screenSizeOf(context).index >= ScreenSize.desktop.index;
    return Scaffold(
      backgroundColor: AppColors.bg,
      drawer: showSidebar
          ? null
          : Drawer(
              backgroundColor: AppColors.surface,
              child: DashboardSidebar(
                selected: 2,
                onSelect: (i) {
                  Navigator.of(context).maybePop();
                  if (i == 0) {
                    Navigator.of(context)
                        .pushNamedAndRemoveUntil('/', (r) => false);
                  } else if (sidebarItems[i].route != '/plans') {
                    Navigator.of(context)
                        .pushReplacementNamed(sidebarItems[i].route);
                  }
                },
              ),
            ),
      body: SafeArea(
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (showSidebar)
              SizedBox(
                width: 240,
                child: DashboardSidebar(
                  selected: 2,
                  onSelect: (i) {
                    if (i == 0) {
                      Navigator.of(context)
                          .pushNamedAndRemoveUntil('/', (r) => false);
                    } else if (sidebarItems[i].route != '/plans') {
                      Navigator.of(context)
                          .pushReplacementNamed(sidebarItems[i].route);
                    }
                  },
                ),
              ),
            Expanded(
              child: Container(
                decoration: const BoxDecoration(
                  border: Border(left: BorderSide(color: AppColors.line)),
                ),
                child: Column(
                  children: [
                    _TopBar(showMenu: !showSidebar),
                    Expanded(
                      child: StreamBuilder<List<Plan>>(
                        stream: PlanRepository.instance.watchMyPlans(),
                        builder: (context, snap) {
                          if (snap.connectionState == ConnectionState.waiting &&
                              !snap.hasData) {
                            return const Center(
                              child: SizedBox(
                                width: 24,
                                height: 24,
                                child: CircularProgressIndicator(
                                  strokeWidth: 2,
                                  valueColor:
                                      AlwaysStoppedAnimation(AppColors.accent),
                                ),
                              ),
                            );
                          }
                          final plans = snap.data ?? const [];
                          if (plans.isEmpty) return const _EmptyState();
                          return _PlansGrid(plans: plans);
                        },
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _TopBar extends StatelessWidget {
  final bool showMenu;
  const _TopBar({required this.showMenu});

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 72,
      padding: const EdgeInsets.symmetric(horizontal: 20),
      decoration: const BoxDecoration(
        border: Border(bottom: BorderSide(color: AppColors.line)),
      ),
      child: Row(
        children: [
          if (showMenu)
            Builder(
              builder: (ctx) => IconButton(
                icon: const Icon(Icons.menu),
                color: AppColors.ink2,
                onPressed: () => Scaffold.of(ctx).openDrawer(),
              ),
            ),
          Icon(Icons.folder_outlined, color: AppColors.accent, size: 20),
          const SizedBox(width: 10),
          Text('My Plans',
              style: AppText.serif(size: 20, weight: FontWeight.w500)),
          const Spacer(),
          ElevatedButton.icon(
            onPressed: () => Navigator.of(context).pushNamed('/new-plan'),
            icon: const Icon(Icons.add, color: Colors.white, size: 18),
            label: Text(
              'New Plan',
              style: AppText.body(
                  size: 14, weight: FontWeight.w600, color: Colors.white),
            ),
            style: ElevatedButton.styleFrom(
              backgroundColor: AppColors.accent,
              padding:
                  const EdgeInsets.symmetric(horizontal: 18, vertical: 12),
              shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(999)),
            ),
          ),
        ],
      ),
    );
  }
}

class _EmptyState extends StatelessWidget {
  const _EmptyState();

  @override
  Widget build(BuildContext context) {
    return Center(
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 420),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 72,
              height: 72,
              decoration: BoxDecoration(
                color: AppColors.accent.withValues(alpha: 0.1),
                shape: BoxShape.circle,
              ),
              child: Icon(Icons.folder_outlined,
                  size: 32, color: AppColors.accent),
            ),
            const SizedBox(height: 20),
            Text('No plans yet',
                style: AppText.serif(size: 24, weight: FontWeight.w500)),
            const SizedBox(height: 8),
            Text(
              'Describe a goal, upload a document, or capture a situation. '
              'Reflica turns it into a living strategic mind-map that updates '
              'as reality changes.',
              textAlign: TextAlign.center,
              style: AppText.body(size: 14, color: AppColors.ink2),
            ),
            const SizedBox(height: 20),
            ElevatedButton.icon(
              onPressed: () => Navigator.of(context).pushNamed('/new-plan'),
              icon: const Icon(Icons.auto_awesome,
                  color: Colors.white, size: 18),
              label: Text(
                'Create your first plan',
                style: AppText.body(
                    size: 14,
                    weight: FontWeight.w600,
                    color: Colors.white),
              ),
              style: ElevatedButton.styleFrom(
                backgroundColor: AppColors.accent,
                padding: const EdgeInsets.symmetric(
                    horizontal: 24, vertical: 14),
                shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(999)),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _PlansGrid extends StatelessWidget {
  final List<Plan> plans;
  const _PlansGrid({required this.plans});

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(builder: (context, c) {
      final cols = c.maxWidth < 640
          ? 1
          : c.maxWidth < 980
              ? 2
              : c.maxWidth < 1400
                  ? 3
                  : 4;
      const gap = 16.0;
      final cardWidth =
          ((c.maxWidth - 40 - (cols - 1) * gap) / cols).floorToDouble();
      return SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Wrap(
          spacing: gap,
          runSpacing: gap,
          children: plans
              .map((p) => SizedBox(
                    width: cardWidth,
                    child: _PlanCard(plan: p),
                  ))
              .toList(),
        ),
      );
    });
  }
}

class _PlanCard extends StatefulWidget {
  final Plan plan;
  const _PlanCard({required this.plan});

  @override
  State<_PlanCard> createState() => _PlanCardState();
}

class _PlanCardState extends State<_PlanCard> {
  bool _hover = false;

  @override
  Widget build(BuildContext context) {
    final p = widget.plan;
    return MouseRegion(
      cursor: SystemMouseCursors.click,
      onEnter: (_) => setState(() => _hover = true),
      onExit: (_) => setState(() => _hover = false),
      child: GestureDetector(
        onTap: () => Navigator.of(context).pushNamed('/plan', arguments: p.id),
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 180),
          transform: Matrix4.translationValues(0, _hover ? -3 : 0, 0),
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
            color: AppColors.surface,
            border: Border.all(
              color: _hover ? AppColors.accent : AppColors.line,
            ),
            borderRadius: BorderRadius.circular(14),
            boxShadow: _hover
                ? [
                    BoxShadow(
                      color: AppColors.ink.withValues(alpha: 0.06),
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
                    width: 36,
                    height: 36,
                    decoration: BoxDecoration(
                      color: AppColors.accent.withValues(alpha: 0.12),
                      borderRadius: BorderRadius.circular(10),
                    ),
                    alignment: Alignment.center,
                    child: Icon(p.audience.icon,
                        color: AppColors.accent, size: 18),
                  ),
                  const Spacer(),
                  _StatusChip(status: p.status),
                ],
              ),
              const SizedBox(height: 14),
              Text(
                p.title,
                style: AppText.serif(size: 18, weight: FontWeight.w500),
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
              const SizedBox(height: 8),
              Text(
                '${p.audience.label} · ${p.inputMode.label}',
                style: AppText.mono(size: 11),
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  Icon(Icons.layers_outlined, size: 14, color: AppColors.muted),
                  const SizedBox(width: 4),
                  Text('${p.nodes.length} nodes',
                      style: AppText.body(size: 12, color: AppColors.muted)),
                  const SizedBox(width: 14),
                  Icon(Icons.alt_route_outlined,
                      size: 14, color: AppColors.muted),
                  const SizedBox(width: 4),
                  Text('${p.edges.length} edges',
                      style: AppText.body(size: 12, color: AppColors.muted)),
                ],
              ),
              const SizedBox(height: 12),
              const Divider(color: AppColors.line, height: 1),
              const SizedBox(height: 12),
              Row(
                children: [
                  Icon(Icons.schedule, size: 14, color: AppColors.muted),
                  const SizedBox(width: 6),
                  Text(_relative(p.updatedAt),
                      style: AppText.mono(size: 11)),
                  const Spacer(),
                  Icon(Icons.arrow_forward,
                      size: 16, color: AppColors.accent),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  String _relative(DateTime t) {
    final diff = DateTime.now().difference(t);
    if (diff.inSeconds < 60) return 'just now';
    if (diff.inMinutes < 60) return '${diff.inMinutes}m ago';
    if (diff.inHours < 24) return '${diff.inHours}h ago';
    return '${diff.inDays}d ago';
  }
}

class _StatusChip extends StatelessWidget {
  final PlanStatus status;
  const _StatusChip({required this.status});

  @override
  Widget build(BuildContext context) {
    final (label, color) = switch (status) {
      PlanStatus.draft => ('Draft', AppColors.muted),
      PlanStatus.verified => ('Verified', AppColors.sage),
      PlanStatus.changed => ('Change', AppColors.amber),
      PlanStatus.repaired => ('Repaired', AppColors.sage),
    };
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.12),
        borderRadius: BorderRadius.circular(999),
      ),
      child: Text(
        label,
        style: AppText.body(
            size: 11, weight: FontWeight.w600, color: color),
      ),
    );
  }
}
