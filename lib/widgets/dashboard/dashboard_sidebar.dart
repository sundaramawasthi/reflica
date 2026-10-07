import 'package:flutter/material.dart';

import '../../models/plan.dart';
import '../../services/plan_repository.dart';
import '../../theme/app_theme.dart';
import '../brand_mark.dart';

class SidebarItem {
  final String label;
  final IconData icon;
  final String route;
  const SidebarItem(this.label, this.icon, this.route);
}

const sidebarItems = <SidebarItem>[
  SidebarItem('Home', Icons.home_outlined, '/dashboard'),
  SidebarItem('New Plan', Icons.add_box_outlined, '/new-plan'),
  SidebarItem('My Plans', Icons.folder_outlined, '/plans'),
  SidebarItem('Knowledge Graph', Icons.hub_outlined, '/graph'),
  SidebarItem('Scenarios', Icons.layers_outlined, '/scenarios'),
  SidebarItem('Documents', Icons.description_outlined, '/documents'),
  SidebarItem('Settings', Icons.settings_outlined, '/settings'),
];


class DashboardSidebar extends StatelessWidget {
  final int selected;
  final ValueChanged<int> onSelect;
  const DashboardSidebar({
    super.key,
    required this.selected,
    required this.onSelect,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      color: AppColors.surface,
      padding: const EdgeInsets.symmetric(vertical: 20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(20, 4, 20, 24),
            child: Row(
              children: [
                const BrandMark(size: 30),
                const SizedBox(width: 12),
                Text('Reflica',
                    style: AppText.serif(size: 22, weight: FontWeight.w500)),
              ],
            ),
          ),
          ...List.generate(sidebarItems.length, (i) {
            final item = sidebarItems[i];
            final isActive = i == selected;
            return _NavItem(
              item: item,
              active: isActive,
              onTap: () {
                onSelect(i);
                if (item.route != '/dashboard' &&
                    ModalRoute.of(context)?.settings.name != item.route) {
                  Navigator.of(context).pushNamed(item.route);
                }
              },
            );
          }),
          const SizedBox(height: 24),
          const Divider(color: AppColors.line, height: 1),
          const SizedBox(height: 20),
          const Padding(
            padding: EdgeInsets.symmetric(horizontal: 20),
            child: _RecentSection(),
          ),
          const Spacer(),
          const Padding(
            padding: EdgeInsets.fromLTRB(16, 16, 16, 8),
            child: _HelpCard(),
          ),
        ],
      ),
    );
  }
}

class _NavItem extends StatefulWidget {
  final SidebarItem item;
  final bool active;
  final VoidCallback onTap;
  const _NavItem({
    required this.item,
    required this.active,
    required this.onTap,
  });

  @override
  State<_NavItem> createState() => _NavItemState();
}

class _NavItemState extends State<_NavItem> {
  bool _hover = false;

  @override
  Widget build(BuildContext context) {
    final color = widget.active
        ? AppColors.accent
        : _hover
            ? AppColors.ink
            : AppColors.ink2;
    final bg = widget.active
        ? AppColors.accent.withValues(alpha: 0.08)
        : _hover
            ? AppColors.surface2
            : Colors.transparent;
    final weight = widget.active ? FontWeight.w600 : FontWeight.w500;

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 2),
      child: MouseRegion(
        cursor: SystemMouseCursors.click,
        onEnter: (_) => setState(() => _hover = true),
        onExit: (_) => setState(() => _hover = false),
        child: GestureDetector(
          onTap: widget.onTap,
          child: AnimatedContainer(
            duration: const Duration(milliseconds: 150),
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 11),
            decoration: BoxDecoration(
              color: bg,
              borderRadius: BorderRadius.circular(10),
            ),
            child: Row(
              children: [
                Icon(widget.item.icon, size: 20, color: color),
                const SizedBox(width: 12),
                Text(
                  widget.item.label,
                  style: AppText.body(size: 14, weight: weight, color: color),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _RecentSection extends StatelessWidget {
  const _RecentSection();

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Icon(Icons.schedule, size: 14, color: AppColors.muted),
            const SizedBox(width: 6),
            Text('RECENT PROJECTS', style: AppText.eyebrow()),
          ],
        ),
        const SizedBox(height: 14),
        StreamBuilder<List<Plan>>(
          stream: PlanRepository.instance.watchMyPlans(),
          builder: (context, snap) {
            final plans = (snap.data ?? const []).take(4).toList();
            if (plans.isEmpty) {
              return Text(
                'Your recent plans will show here.',
                style: AppText.body(size: 12, color: AppColors.muted),
              );
            }
            return Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: plans
                  .map((p) => Padding(
                        padding: const EdgeInsets.only(bottom: 14),
                        child: _RecentRow(plan: p),
                      ))
                  .toList(),
            );
          },
        ),
      ],
    );
  }
}

class _RecentRow extends StatefulWidget {
  final Plan plan;
  const _RecentRow({required this.plan});

  @override
  State<_RecentRow> createState() => _RecentRowState();
}

class _RecentRowState extends State<_RecentRow> {
  bool _hover = false;

  @override
  Widget build(BuildContext context) {
    return MouseRegion(
      cursor: SystemMouseCursors.click,
      onEnter: (_) => setState(() => _hover = true),
      onExit: (_) => setState(() => _hover = false),
      child: GestureDetector(
        onTap: () =>
            Navigator.of(context).pushNamed('/plan', arguments: widget.plan.id),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              widget.plan.title,
              style: AppText.body(
                size: 13,
                weight: FontWeight.w500,
                color: _hover ? AppColors.ink : AppColors.ink2,
              ),
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
            ),
            const SizedBox(height: 2),
            Text(_relative(widget.plan.updatedAt),
                style: AppText.mono(size: 11)),
          ],
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

class _HelpCard extends StatelessWidget {
  const _HelpCard();

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(14),
        gradient: const LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [Color(0xFFD6E6EC), Color(0xFF95B5BE)],
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Need help?',
            style: AppText.serif(
              size: 15,
              weight: FontWeight.w500,
              color: AppColors.ink,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            'View tutorials & guides',
            style: AppText.body(size: 12, color: AppColors.ink2),
          ),
          const SizedBox(height: 20),
          Container(
            height: 44,
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(8),
              color: Colors.white.withValues(alpha: 0.35),
            ),
            child: CustomPaint(painter: _MountainPainter()),
          ),
        ],
      ),
    );
  }
}

class _MountainPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final darkBlue = Paint()..color = AppColors.accent.withValues(alpha: 0.6);
    final midBlue = Paint()..color = AppColors.accent.withValues(alpha: 0.3);
    final path1 = Path()
      ..moveTo(0, size.height)
      ..lineTo(size.width * 0.3, size.height * 0.3)
      ..lineTo(size.width * 0.55, size.height * 0.7)
      ..lineTo(size.width * 0.75, size.height * 0.4)
      ..lineTo(size.width, size.height * 0.85)
      ..lineTo(size.width, size.height)
      ..close();
    canvas.drawPath(path1, midBlue);
    final path2 = Path()
      ..moveTo(0, size.height)
      ..lineTo(size.width * 0.2, size.height * 0.6)
      ..lineTo(size.width * 0.5, size.height * 0.9)
      ..lineTo(size.width * 0.8, size.height * 0.65)
      ..lineTo(size.width, size.height)
      ..close();
    canvas.drawPath(path2, darkBlue);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
