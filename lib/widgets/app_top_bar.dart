import 'dart:ui';

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
                'Your plans stay saved. You\'ll need to sign in again to '
                'open the dashboard.',
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

class AppTopBar extends StatelessWidget {
  final bool elevated;
  const AppTopBar({super.key, this.elevated = false});

  @override
  Widget build(BuildContext context) {
    final size = screenSizeOf(context);
    final width = MediaQuery.sizeOf(context).width;
    final showLinks = width >= 980;
    // Nav + chip + button + brand all compete. Tagline is ~290 px wide and
    // must share Flexible space with the brand mark — we need enough free
    // width even AFTER nav links eat their share. 1480 is empirically safe.
    final showTagline = width >= 1480;

    return ClipRRect(
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
        child: Container(
          decoration: BoxDecoration(
            color: AppColors.bg.withValues(alpha: 0.85),
            border: Border(
              bottom: BorderSide(
                color: elevated ? AppColors.line : Colors.transparent,
                width: 1,
              ),
            ),
          ),
          child: SafeArea(
            bottom: false,
            child: PageWrap(
              padding: const EdgeInsets.symmetric(
                horizontal: Breakpoints.pageGutter,
                vertical: 16,
              ),
              child: Row(
                children: [
                  Flexible(
                    child: ClipRect(
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          const BrandMark(size: 32),
                          const SizedBox(width: 10),
                          Flexible(
                            child: Text(
                              'Reflica',
                              style: AppText.serif(
                                  size: size == ScreenSize.phone ? 20 : 24,
                                  weight: FontWeight.w600),
                              overflow: TextOverflow.ellipsis,
                            ),
                          ),
                          if (showTagline) ...[
                            const SizedBox(width: 20),
                            Flexible(child: _TaglineBar()),
                          ],
                        ],
                      ),
                    ),
                  ),
                  const Spacer(),
                  if (showLinks) ...[
                    const _NavLink('Home', active: true),
                    const _NavLink('Solutions'),
                    const _NavLink('Features'),
                    const _NavLink('Use Cases'),
                    const _NavLink('About'),
                    const SizedBox(width: 32),
                  ],
                  if (AuthService.instance.isDemoMode) ...[
                    Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 10, vertical: 4),
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
                  _PrimaryButton(
                    label: size == ScreenSize.phone ? 'Start' : 'Get Started',
                    onTap: () => handleGetStarted(context),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class _TaglineBar extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    const words = ['Understand', 'Reason', 'Plan', 'Adapt'];
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        for (int i = 0; i < words.length; i++) ...[
          Text(
            words[i],
            style: AppText.body(
              size: 14,
              weight: FontWeight.w500,
              color: AppColors.ink2,
            ),
          ),
          if (i < words.length - 1) ...[
            const SizedBox(width: 10),
            Container(
              width: 3,
              height: 3,
              decoration: const BoxDecoration(
                color: AppColors.muted,
                shape: BoxShape.circle,
              ),
            ),
            const SizedBox(width: 10),
          ],
        ],
      ],
    );
  }
}

class _NavLink extends StatefulWidget {
  final String label;
  final bool active;
  const _NavLink(this.label, {this.active = false});

  @override
  State<_NavLink> createState() => _NavLinkState();
}

class _NavLinkState extends State<_NavLink> {
  bool _hover = false;

  @override
  Widget build(BuildContext context) {
    final isActive = widget.active;
    final color = isActive
        ? AppColors.accent
        : _hover
            ? AppColors.ink
            : AppColors.ink2;

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: MouseRegion(
        cursor: SystemMouseCursors.click,
        onEnter: (_) => setState(() => _hover = true),
        onExit: (_) => setState(() => _hover = false),
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 6),
          decoration: BoxDecoration(
            border: Border(
              bottom: BorderSide(
                color: isActive
                    ? AppColors.accent
                    : _hover
                        ? AppColors.accent.withValues(alpha: 0.4)
                        : Colors.transparent,
                width: 2,
              ),
            ),
          ),
          child: Text(
            widget.label,
            style: AppText.body(
              size: 15,
              weight: isActive ? FontWeight.w600 : FontWeight.w500,
              color: color,
            ),
          ),
        ),
      ),
    );
  }
}

class _PrimaryButton extends StatefulWidget {
  final String label;
  final VoidCallback onTap;
  const _PrimaryButton({required this.label, required this.onTap});

  @override
  State<_PrimaryButton> createState() => _PrimaryButtonState();
}

class _PrimaryButtonState extends State<_PrimaryButton> {
  bool _hover = false;

  @override
  Widget build(BuildContext context) {
    return MouseRegion(
      cursor: SystemMouseCursors.click,
      onEnter: (_) => setState(() => _hover = true),
      onExit: (_) => setState(() => _hover = false),
      child: GestureDetector(
        onTap: widget.onTap,
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 150),
          padding: const EdgeInsets.symmetric(horizontal: 22, vertical: 12),
          decoration: BoxDecoration(
            color: _hover
                ? const Color(0xFF1E5BC9)
                : const Color(0xFF2E6FEB),
            borderRadius: BorderRadius.circular(999),
            boxShadow: _hover
                ? [
                    BoxShadow(
                      color: const Color(0xFF2E6FEB).withValues(alpha: 0.4),
                      blurRadius: 16,
                      offset: const Offset(0, 4),
                    ),
                  ]
                : [],
          ),
          child: Text(
            widget.label,
            style: AppText.body(
              size: 14,
              weight: FontWeight.w600,
              color: Colors.white,
            ),
          ),
        ),
      ),
    );
  }
}
