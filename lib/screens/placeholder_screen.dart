import 'package:flutter/material.dart';

import '../theme/app_theme.dart';
import '../widgets/dashboard/dashboard_sidebar.dart';
import '../widgets/responsive.dart';

/// Reusable "coming soon" scaffold for the sidebar routes we haven't built yet.
/// Keeps the dashboard shell (sidebar + back) so navigation stays consistent.
class PlaceholderScreen extends StatelessWidget {
  final String title;
  final String description;
  final IconData icon;
  final int sidebarIndex;

  const PlaceholderScreen({
    super.key,
    required this.title,
    required this.description,
    required this.icon,
    required this.sidebarIndex,
  });

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
                selected: sidebarIndex,
                onSelect: (i) {
                  Navigator.of(context).maybePop();
                  if (i == 0) {
                    Navigator.of(context)
                        .pushNamedAndRemoveUntil('/', (r) => false);
                  } else {
                    Navigator.of(context).pushReplacementNamed(
                      sidebarItems[i].route,
                    );
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
                  selected: sidebarIndex,
                  onSelect: (i) {
                    if (i == 0) {
                      Navigator.of(context)
                          .pushNamedAndRemoveUntil('/', (r) => false);
                    } else if (sidebarItems[i].route !=
                        ModalRoute.of(context)?.settings.name) {
                      Navigator.of(context).pushReplacementNamed(
                        sidebarItems[i].route,
                      );
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
                    Container(
                      height: 72,
                      padding: const EdgeInsets.symmetric(horizontal: 20),
                      decoration: const BoxDecoration(
                        border: Border(
                          bottom: BorderSide(color: AppColors.line),
                        ),
                      ),
                      child: Row(
                        children: [
                          if (!showSidebar)
                            Builder(
                              builder: (ctx) => IconButton(
                                icon: const Icon(Icons.menu),
                                color: AppColors.ink2,
                                onPressed: () =>
                                    Scaffold.of(ctx).openDrawer(),
                              ),
                            ),
                          Builder(
                            builder: (ctx) => IconButton(
                              icon: const Icon(Icons.arrow_back),
                              color: AppColors.ink2,
                              onPressed: () => Navigator.of(ctx)
                                  .pushNamedAndRemoveUntil('/', (r) => false),
                            ),
                          ),
                          const SizedBox(width: 6),
                          Expanded(
                            child: Text(
                              title,
                              style: AppText.serif(
                                  size: 18, weight: FontWeight.w500),
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                            ),
                          ),
                        ],
                      ),
                    ),
                    Expanded(
                      child: Center(
                        child: ConstrainedBox(
                          constraints: const BoxConstraints(maxWidth: 480),
                          child: Column(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Container(
                                width: 72,
                                height: 72,
                                decoration: BoxDecoration(
                                  color: AppColors.accent
                                      .withValues(alpha: 0.1),
                                  shape: BoxShape.circle,
                                ),
                                alignment: Alignment.center,
                                child: Icon(icon,
                                    size: 32, color: AppColors.accent),
                              ),
                              const SizedBox(height: 24),
                              Text(
                                title,
                                style: AppText.serif(
                                    size: 32, weight: FontWeight.w400),
                                textAlign: TextAlign.center,
                              ),
                              const SizedBox(height: 10),
                              Text(
                                description,
                                style: AppText.body(
                                    size: 15, color: AppColors.ink2),
                                textAlign: TextAlign.center,
                              ),
                              const SizedBox(height: 20),
                              Container(
                                padding: const EdgeInsets.symmetric(
                                    horizontal: 14, vertical: 6),
                                decoration: BoxDecoration(
                                  color:
                                      AppColors.amber.withValues(alpha: 0.12),
                                  borderRadius: BorderRadius.circular(999),
                                ),
                                child: Text(
                                  'IN DEVELOPMENT',
                                  style: AppText.mono(
                                      size: 11, color: AppColors.amber),
                                ),
                              ),
                            ],
                          ),
                        ),
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
