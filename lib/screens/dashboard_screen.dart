import 'package:flutter/material.dart';

import '../theme/app_theme.dart';
import '../widgets/dashboard/dashboard_sidebar.dart';
import '../widgets/dashboard/dashboard_top_bar.dart';
import '../widgets/dashboard/welcome_card.dart';
import '../widgets/responsive.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  final bool _sidebarOpen = true;
  int _selectedNav = 0;

  @override
  Widget build(BuildContext context) {
    final size = screenSizeOf(context);
    final showSidebar = size.index >= ScreenSize.desktop.index && _sidebarOpen;

    return Scaffold(
      backgroundColor: AppColors.bg,
      drawer: size.index < ScreenSize.desktop.index
          ? Drawer(
              backgroundColor: AppColors.surface,
              child: DashboardSidebar(
                selected: _selectedNav,
                onSelect: (i) {
                  setState(() => _selectedNav = i);
                  Navigator.of(context).maybePop();
                },
              ),
            )
          : null,
      body: SafeArea(
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (showSidebar)
              SizedBox(
                width: 240,
                child: DashboardSidebar(
                  selected: _selectedNav,
                  onSelect: (i) => setState(() => _selectedNav = i),
                ),
              ),
            Expanded(child: _MainArea()),
          ],
        ),
      ),
    );
  }
}

class _MainArea extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final size = screenSizeOf(context);
    final isNarrow = size.index < ScreenSize.desktop.index;

    return Container(
      decoration: const BoxDecoration(
        color: AppColors.bg,
        border: Border(left: BorderSide(color: AppColors.line)),
      ),
      child: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            DashboardTopBar(showMenu: isNarrow),
            Padding(
              padding: EdgeInsets.all(isNarrow ? 20 : 28),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const WelcomeCard(),
                  const SizedBox(height: 32),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
