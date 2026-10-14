import 'package:flutter/material.dart';

import '../services/auth_service.dart';
import '../theme/app_theme.dart';
import 'brand_mark.dart';
import 'responsive.dart';

Future<void> handleGetStarted(BuildContext context) async {
  try {
    await AuthService.instance.signInWithGoogle();
  } on SignInException catch (e) {
    if (e.isCancelled) return; // Silent: user chose to abort.
    if (!context.mounted) return;
    await showSignInErrorDialog(context, e);
  } catch (e) {
    if (!context.mounted) return;
    await showSignInErrorDialog(
      context,
      SignInException('Sign-in failed: $e'),
    );
  }
}

/// Branded popup for sign-in errors. Shows a specific hint when the problem
/// is a missing network connection.
Future<void> showSignInErrorDialog(
    BuildContext context, SignInException e) {
  final isNet = e.isNetwork;
  return showDialog<void>(
    context: context,
    barrierColor: Colors.black.withValues(alpha: 0.4),
    builder: (ctx) => Dialog(
      backgroundColor: AppColors.surface,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
      ),
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 420),
        child: Padding(
          padding: const EdgeInsets.fromLTRB(24, 24, 24, 20),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Container(
                    width: 44,
                    height: 44,
                    decoration: BoxDecoration(
                      color: (isNet ? AppColors.amber : AppColors.crimson)
                          .withValues(alpha: 0.12),
                      shape: BoxShape.circle,
                    ),
                    alignment: Alignment.center,
                    child: Icon(
                      isNet
                          ? Icons.wifi_off_outlined
                          : Icons.error_outline,
                      color: isNet ? AppColors.amber : AppColors.crimson,
                      size: 22,
                    ),
                  ),
                  const SizedBox(width: 14),
                  Expanded(
                    child: Text(
                      isNet ? 'No internet connection' : 'Sign-in failed',
                      style: AppText.serif(
                          size: 18, weight: FontWeight.w600),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              Text(
                e.message,
                style: AppText.body(size: 14, color: AppColors.ink2),
              ),
              if (isNet) ...[
                const SizedBox(height: 16),
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: AppColors.amber.withValues(alpha: 0.08),
                    border: Border.all(
                      color: AppColors.amber.withValues(alpha: 0.3),
                    ),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('HINTS',
                          style: AppText.eyebrow().copyWith(
                              color: AppColors.amber,
                              fontWeight: FontWeight.w600)),
                      const SizedBox(height: 8),
                      _hint('Switch on Wi-Fi or mobile data'),
                      _hint('Open any website first to confirm you\'re online'),
                      _hint('Disable VPN / airplane mode if it\'s on'),
                    ],
                  ),
                ),
              ],
              const SizedBox(height: 20),
              Row(
                mainAxisAlignment: MainAxisAlignment.end,
                children: [
                  TextButton(
                    onPressed: () => Navigator.of(ctx).pop(),
                    child: Text(
                      'Close',
                      style: AppText.body(
                          size: 14,
                          weight: FontWeight.w500,
                          color: AppColors.ink2),
                    ),
                  ),
                  const SizedBox(width: 6),
                  ElevatedButton.icon(
                    onPressed: () async {
                      Navigator.of(ctx).pop();
                      await handleGetStarted(context);
                    },
                    icon: const Icon(Icons.refresh,
                        size: 16, color: Colors.white),
                    label: Text(
                      'Try again',
                      style: AppText.body(
                          size: 13.5,
                          weight: FontWeight.w600,
                          color: Colors.white),
                    ),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: AppColors.accent,
                      padding: const EdgeInsets.symmetric(
                          horizontal: 18, vertical: 12),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(10),
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    ),
  );
}

Widget _hint(String text) {
  return Padding(
    padding: const EdgeInsets.only(bottom: 4),
    child: Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Icon(Icons.circle, size: 4, color: AppColors.ink2),
        const SizedBox(width: 10),
        Expanded(
          child: Text(text,
              style: AppText.body(size: 12.5, color: AppColors.ink2)),
        ),
      ],
    ),
  );
}

/// Centralised sign-out handler. Confirms, signs out, pops to the landing
/// route, and shows an error dialog if anything fails.
Future<void> handleSignOut(BuildContext context) async {
  final confirmed = await showDialog<bool>(
    context: context,
    builder: (ctx) => Dialog(
      backgroundColor: AppColors.surface,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(14),
      ),
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 380),
        child: Padding(
          padding: const EdgeInsets.fromLTRB(20, 20, 20, 16),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Container(
                    width: 36,
                    height: 36,
                    decoration: BoxDecoration(
                      color: AppColors.crimson.withValues(alpha: 0.12),
                      shape: BoxShape.circle,
                    ),
                    alignment: Alignment.center,
                    child: Icon(Icons.logout,
                        color: AppColors.crimson, size: 18),
                  ),
                  const SizedBox(width: 12),
                  Text('Sign out of Reflica?',
                      style: AppText.serif(
                          size: 16, weight: FontWeight.w600)),
                ],
              ),
              const SizedBox(height: 12),
              Text(
                'You\'ll need to sign in again to open the dashboard.',
                style: AppText.body(size: 13.5, color: AppColors.ink2),
              ),
              const SizedBox(height: 18),
              Row(
                mainAxisAlignment: MainAxisAlignment.end,
                children: [
                  TextButton(
                    onPressed: () => Navigator.of(ctx).pop(false),
                    child: Text('Cancel',
                        style: AppText.body(
                            size: 14,
                            weight: FontWeight.w500,
                            color: AppColors.ink2)),
                  ),
                  const SizedBox(width: 6),
                  ElevatedButton.icon(
                    onPressed: () => Navigator.of(ctx).pop(true),
                    icon: const Icon(Icons.logout,
                        size: 16, color: Colors.white),
                    label: Text('Sign out',
                        style: AppText.body(
                            size: 13.5,
                            weight: FontWeight.w600,
                            color: Colors.white)),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: AppColors.crimson,
                      padding: const EdgeInsets.symmetric(
                          horizontal: 16, vertical: 10),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(8),
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    ),
  );
  if (confirmed != true) return;
  if (!context.mounted) return;

  // Flash a brief in-progress indicator — Firestore + native Google can take
  // a moment to tear down, especially on a slow network.
  final messenger = ScaffoldMessenger.maybeOf(context);
  messenger?.showSnackBar(
    const SnackBar(
      content: Text('Signing out…'),
      duration: Duration(seconds: 2),
    ),
  );

  try {
    await AuthService.instance.signOut();
  } catch (e) {
    if (!context.mounted) return;
    messenger?.hideCurrentSnackBar();
    messenger?.showSnackBar(
      SnackBar(content: Text('Sign-out failed: $e')),
    );
    return;
  }

  if (!context.mounted) return;
  messenger?.hideCurrentSnackBar();
  // Nuke the whole navigation stack and go back to the AuthGate at `/`.
  // AuthGate will see the null user and render HomeScreen.
  Navigator.of(context).pushNamedAndRemoveUntil('/', (_) => false);
}

/// Homepage navigation colours (match the homepage in home_screen.dart).
const _navy = Color(0xFF0F1B3D);
const _muted = Color(0xFF5B6B85);
const _blue = Color(0xFF2563EB);
const _border = Color(0xFFE3E9F3);

/// Top bar of the public homepage. Links only do real things: scroll on the
/// page, or say honestly that a forecasting page is not built yet.
class AppTopBar extends StatelessWidget {
  final bool elevated;
  final VoidCallback? onHome;
  final VoidCallback? onAbout;
  final ValueChanged<String>? onComingSoon;

  const AppTopBar({
    super.key,
    this.elevated = false,
    this.onHome,
    this.onAbout,
    this.onComingSoon,
  });

  void _select(String item) {
    switch (item) {
      case 'Home':
        onHome?.call();
      case 'About':
        onAbout?.call();
      default:
        onComingSoon?.call(item);
    }
  }

  @override
  Widget build(BuildContext context) {
    final size = screenSizeOf(context);
    final showLinks = MediaQuery.sizeOf(context).width >= 900;
    const items = ['Home', 'Question Bank', 'Forecasts', 'About'];

    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        border: Border(
          bottom: BorderSide(
            color: elevated ? _border : Colors.transparent,
          ),
        ),
      ),
      child: SafeArea(
        bottom: false,
        child: PageWrap(
          padding: const EdgeInsets.symmetric(
            horizontal: Breakpoints.pageGutter,
            vertical: 14,
          ),
          child: Row(
            children: [
              Flexible(
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const BrandMark(size: 32),
                    const SizedBox(width: 10),
                    Flexible(
                      child: Text(
                        'Reflica',
                        style: TextStyle(
                          color: _navy,
                          fontSize: size == ScreenSize.phone ? 20 : 22,
                          fontWeight: FontWeight.w800,
                        ),
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                  ],
                ),
              ),
              const Spacer(),
              if (showLinks) ...[
                for (final item in items)
                  _NavLink(
                    item,
                    active: item == 'Home',
                    onTap: () => _select(item),
                  ),
                const SizedBox(width: 24),
              ],
              if (AuthService.instance.isDemoMode) ...[
                Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(
                    color: AppColors.amber.withValues(alpha: 0.12),
                    borderRadius: BorderRadius.circular(999),
                  ),
                  child: Text(
                    'demo mode',
                    style: AppText.mono(size: 10, color: AppColors.amber),
                  ),
                ),
                const SizedBox(width: 10),
              ],
              FilledButton(
                onPressed: () => handleGetStarted(context),
                style: FilledButton.styleFrom(
                  backgroundColor: _blue,
                  foregroundColor: Colors.white,
                  padding:
                      const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
                  shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(10)),
                  textStyle: const TextStyle(
                      fontSize: 14, fontWeight: FontWeight.w600),
                ),
                child: const Text('Sign In'),
              ),
              if (!showLinks) ...[
                const SizedBox(width: 4),
                PopupMenuButton<String>(
                  tooltip: 'Menu',
                  icon: const Icon(Icons.menu, color: _navy),
                  onSelected: _select,
                  itemBuilder: (_) => [
                    for (final item in items)
                      PopupMenuItem<String>(value: item, child: Text(item)),
                  ],
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}

class _NavLink extends StatelessWidget {
  final String label;
  final bool active;
  final VoidCallback onTap;
  const _NavLink(this.label, {this.active = false, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 4),
      child: TextButton(
        onPressed: onTap,
        style: TextButton.styleFrom(
          foregroundColor: active ? _blue : _muted,
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
          textStyle: TextStyle(
            fontSize: 15,
            fontWeight: active ? FontWeight.w700 : FontWeight.w500,
          ),
        ),
        child: Text(label),
      ),
    );
  }
}
