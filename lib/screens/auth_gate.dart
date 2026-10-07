import 'package:flutter/material.dart';

import '../services/auth_service.dart';
import '../theme/app_theme.dart';
import '../widgets/brand_mark.dart';
import 'dashboard_screen.dart';
import 'home_screen.dart';

class AuthGate extends StatelessWidget {
  const AuthGate({super.key});

  @override
  Widget build(BuildContext context) {
    return StreamBuilder<AppUser?>(
      stream: AuthService.instance.authState,
      initialData: AuthService.instance.currentUser,
      builder: (context, snap) {
        if (snap.connectionState == ConnectionState.waiting &&
            !snap.hasData) {
          return const _AuthLoading();
        }
        if (snap.data != null) {
          return const DashboardScreen();
        }
        return const HomeScreen();
      },
    );
  }
}

class _AuthLoading extends StatelessWidget {
  const _AuthLoading();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.bg,
      body: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const BrandMark(size: 48),
            const SizedBox(height: 20),
            SizedBox(
              width: 24,
              height: 24,
              child: CircularProgressIndicator(
                strokeWidth: 2,
                valueColor: AlwaysStoppedAnimation(AppColors.accent),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
