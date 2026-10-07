import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../../models/notification.dart';
import '../../services/auth_service.dart';
import '../../services/notification_service.dart';
import '../../theme/app_theme.dart';
import '../app_top_bar.dart' show handleSignOut;

class DashboardTopBar extends StatelessWidget {
  final bool showMenu;
  const DashboardTopBar({super.key, this.showMenu = false});

  @override
  Widget build(BuildContext context) {
    return StreamBuilder<AppUser?>(
      stream: AuthService.instance.authState,
      initialData: AuthService.instance.currentUser,
      builder: (context, snap) {
        final user = snap.data;
        final name = user?.displayName ?? 'Explorer';
        final initials = _initials(name);
        return _build(context, user, name, initials);
      },
    );
  }

  Widget _build(
      BuildContext context, AppUser? user, String name, String initials) {
    return LayoutBuilder(builder: (context, c) {
      final showPipeline = c.maxWidth >= 820;
      final showSearch = c.maxWidth >= 560;
      final compactUser = c.maxWidth < 720;

      return Container(
        height: 72,
        padding: const EdgeInsets.symmetric(horizontal: 20),
        decoration: const BoxDecoration(
          color: AppColors.bg,
          border: Border(bottom: BorderSide(color: AppColors.line)),
        ),
        child: Row(
          children: [
            if (showMenu)
              Padding(
                padding: const EdgeInsets.only(right: 8),
                child: IconButton(
                  icon: const Icon(Icons.menu),
                  color: AppColors.ink2,
                  onPressed: () => Scaffold.of(context).openDrawer(),
                ),
              ),
            if (showPipeline)
              Row(
                children: [
                  _Pipeline('Understand'),
                  _Dot(),
                  _Pipeline('Reason'),
                  _Dot(),
                  _Pipeline('Plan'),
                  _Dot(),
                  _Pipeline('Adapt'),
                ],
              ),
            if (!showSearch) const Spacer(),
            if (showSearch) ...[
              const Spacer(),
              Expanded(
                flex: 2,
                child: ConstrainedBox(
                  constraints: const BoxConstraints(maxWidth: 420),
                  child: _SearchField(),
                ),
              ),
              const SizedBox(width: 16),
            ],
            _NotificationButton(),
            const SizedBox(width: 10),
            _UserMenu(
              name: name,
              initials: initials,
              photoUrl: user?.photoURL,
              compact: compactUser,
            ),
          ],
        ),
      );
    });
  }

  String _initials(String name) {
    final parts = name.trim().split(RegExp(r'\s+')).where((p) => p.isNotEmpty);
    if (parts.isEmpty) return 'R';
    if (parts.length == 1) return parts.first.substring(0, 1).toUpperCase();
    return (parts.first.substring(0, 1) + parts.last.substring(0, 1))
        .toUpperCase();
  }
}

class _Pipeline extends StatelessWidget {
  final String label;
  const _Pipeline(this.label);

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 4),
      child: Text(
        label,
        style: AppText.body(
          size: 13,
          weight: FontWeight.w500,
          color: AppColors.ink2,
        ),
      ),
    );
  }
}

class _Dot extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return const Padding(
      padding: EdgeInsets.symmetric(horizontal: 2),
      child: Text('·', style: TextStyle(color: AppColors.muted)),
    );
  }
}

class _SearchField extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(
      height: 42,
      padding: const EdgeInsets.symmetric(horizontal: 14),
      decoration: BoxDecoration(
        color: AppColors.surface,
        border: Border.all(color: AppColors.line),
        borderRadius: BorderRadius.circular(10),
      ),
      child: Row(
        children: [
          Icon(Icons.search, size: 18, color: AppColors.muted),
          const SizedBox(width: 10),
          Expanded(
            child: TextField(
              decoration: InputDecoration(
                border: InputBorder.none,
                hintText: 'Search plans, scenarios, documents...',
                hintStyle: AppText.body(size: 14, color: AppColors.muted),
                isCollapsed: true,
              ),
              style: AppText.body(size: 14, color: AppColors.ink),
            ),
          ),
        ],
      ),
    );
  }
}

class _NotificationButton extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return StreamBuilder<int>(
      stream: NotificationService.instance.watchUnreadCount(),
      initialData: 0,
      builder: (context, snap) {
        final unread = snap.data ?? 0;
        return SizedBox(
          width: 40,
          height: 40,
          child: Stack(
            children: [
              Positioned.fill(
                child: IconButton(
                  tooltip: 'Notifications',
                  icon: Icon(Icons.notifications_none, color: AppColors.ink2),
                  onPressed: () => _openPanel(context),
                ),
              ),
              if (unread > 0)
                Positioned(
                  right: 4,
                  top: 6,
                  child: Container(
                    constraints: const BoxConstraints(minWidth: 16, minHeight: 16),
                    padding:
                        const EdgeInsets.symmetric(horizontal: 4, vertical: 1),
                    decoration: BoxDecoration(
                      color: AppColors.crimson,
                      borderRadius: BorderRadius.circular(999),
                      border: Border.all(color: AppColors.bg, width: 1.5),
                    ),
                    alignment: Alignment.center,
                    child: Text(
                      unread > 99 ? '99+' : '$unread',
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 9,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                  ),
                ),
            ],
          ),
        );
      },
    );
  }

  void _openPanel(BuildContext context) {
    showDialog(
      context: context,
      barrierColor: Colors.black.withValues(alpha: 0.1),
      builder: (ctx) => Align(
        alignment: Alignment.topRight,
        child: Padding(
          padding: const EdgeInsets.only(top: 72, right: 20),
          child: Material(
            color: Colors.transparent,
            child: NotificationsPanel(),
          ),
        ),
      ),
    );
  }
}

class NotificationsPanel extends StatelessWidget {
  const NotificationsPanel({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 380,
      constraints: const BoxConstraints(maxHeight: 520),
      decoration: BoxDecoration(
        color: AppColors.surface,
        border: Border.all(color: AppColors.line),
        borderRadius: BorderRadius.circular(14),
        boxShadow: [
          BoxShadow(
            color: AppColors.ink.withValues(alpha: 0.1),
            blurRadius: 32,
            offset: const Offset(0, 12),
            spreadRadius: -8,
          ),
        ],
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 14, 10, 10),
            child: Row(
              children: [
                Icon(Icons.notifications_none,
                    size: 18, color: AppColors.accent),
                const SizedBox(width: 10),
                Text('Notifications',
                    style: AppText.serif(
                        size: 16, weight: FontWeight.w500)),
                const Spacer(),
                TextButton(
                  onPressed: () async {
                    await NotificationService.instance.markAllRead();
                  },
                  child: Text(
                    'Mark all read',
                    style: AppText.body(
                      size: 12,
                      color: AppColors.accent,
                      weight: FontWeight.w500,
                    ),
                  ),
                ),
              ],
            ),
          ),
          const Divider(color: AppColors.line, height: 1),
          Flexible(
            child: StreamBuilder<List<AppNotification>>(
              stream: NotificationService.instance.watchMyNotifications(),
              builder: (context, snap) {
                final list = snap.data ?? const [];
                if (list.isEmpty) {
                  return Padding(
                    padding: const EdgeInsets.all(32),
                    child: Column(
                      children: [
                        Icon(Icons.notifications_off_outlined,
                            size: 28, color: AppColors.muted),
                        const SizedBox(height: 10),
                        Text(
                          'No notifications yet',
                          style: AppText.body(
                            size: 13,
                            weight: FontWeight.w500,
                            color: AppColors.ink2,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          'Create or edit a plan — you’ll see activity here.',
                          textAlign: TextAlign.center,
                          style: AppText.body(size: 12, color: AppColors.muted),
                        ),
                      ],
                    ),
                  );
                }
                return ListView.separated(
                  shrinkWrap: true,
                  padding: EdgeInsets.zero,
                  itemCount: list.length,
                  separatorBuilder: (_, _) =>
                      const Divider(color: AppColors.line, height: 1),
                  itemBuilder: (ctx, i) =>
                      _NotificationTile(notification: list[i]),
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}

class _NotificationTile extends StatelessWidget {
  final AppNotification notification;
  const _NotificationTile({required this.notification});

  @override
  Widget build(BuildContext context) {
    final n = notification;
    return InkWell(
      onTap: () async {
        await NotificationService.instance.markRead(n.id);
        if (!context.mounted) return;
        Navigator.of(context).maybePop();
        if (n.planId != null) {
          Navigator.of(context).pushNamed('/plan', arguments: n.planId);
        }
      },
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
        color: n.read ? Colors.transparent : AppColors.accent.withValues(alpha: 0.04),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              width: 32,
              height: 32,
              decoration: BoxDecoration(
                color: AppColors.accent.withValues(alpha: 0.12),
                borderRadius: BorderRadius.circular(8),
              ),
              alignment: Alignment.center,
              child: Icon(n.kind.icon, size: 16, color: AppColors.accent),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    n.title,
                    style: AppText.body(
                      size: 13.5,
                      weight: FontWeight.w600,
                      color: AppColors.ink,
                    ),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    n.body,
                    style: AppText.body(size: 12.5, color: AppColors.ink2),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                  const SizedBox(height: 4),
                  Text(_relative(n.createdAt),
                      style: AppText.mono(size: 10)),
                ],
              ),
            ),
            if (!n.read)
              Container(
                width: 8,
                height: 8,
                margin: const EdgeInsets.only(top: 6, left: 6),
                decoration: const BoxDecoration(
                  color: AppColors.accent,
                  shape: BoxShape.circle,
                ),
              ),
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

class _Avatar extends StatelessWidget {
  final String? photoUrl;
  final String initials;
  const _Avatar({required this.photoUrl, required this.initials});

  @override
  Widget build(BuildContext context) {
    final initialsFallback = Container(
      width: 36,
      height: 36,
      decoration: BoxDecoration(
        color: AppColors.violet.withValues(alpha: 0.2),
        shape: BoxShape.circle,
      ),
      alignment: Alignment.center,
      child: Text(
        initials,
        style: AppText.body(
          size: 13,
          weight: FontWeight.w600,
          color: AppColors.violet,
        ),
      ),
    );
    if (photoUrl == null) return initialsFallback;
    return ClipOval(
      child: SizedBox(
        width: 36,
        height: 36,
        child: Image.network(
          photoUrl!,
          fit: BoxFit.cover,
          // Google avatars rate-limit (HTTP 429) on repeat hits; show the
          // initials fallback instead of propagating a render exception.
          errorBuilder: (_, _, _) => initialsFallback,
          loadingBuilder: (ctx, child, progress) {
            if (progress == null) return child;
            return initialsFallback;
          },
        ),
      ),
    );
  }
}

class _UserMenu extends StatelessWidget {
  final String name;
  final String initials;
  final String? photoUrl;
  final bool compact;
  const _UserMenu({
    required this.name,
    required this.initials,
    this.photoUrl,
    this.compact = false,
  });

  @override
  Widget build(BuildContext context) {
    return PopupMenuButton<String>(
      tooltip: 'Account',
      offset: const Offset(0, 48),
      color: AppColors.surface,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(10),
        side: const BorderSide(color: AppColors.line),
      ),
      onSelected: (v) async {
        if (v == 'logout') {
          await handleSignOut(context);
        }
      },
      itemBuilder: (context) {
        final user = AuthService.instance.currentUser;
        final uid = user?.uid ?? '';
        final shortUid = uid.length > 10 ? '${uid.substring(0, 10)}…' : uid;
        return [
        PopupMenuItem(
          enabled: false,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(name,
                  style: AppText.body(
                      size: 14,
                      weight: FontWeight.w600,
                      color: AppColors.ink)),
              const SizedBox(height: 2),
              Text(
                user?.email ?? '',
                style: AppText.mono(size: 11),
              ),
              if (uid.isNotEmpty) ...[
                const SizedBox(height: 4),
                // Diagnostic: Firebase uid is what plans are keyed by.
                // Compare this across devices — if it differs for the same
                // email, cross-device sync won't work and the sign-in flow
                // needs attention.
                InkWell(
                  onTap: () async {
                    await Clipboard.setData(ClipboardData(text: uid));
                    if (!context.mounted) return;
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(content: Text('uid copied: $uid')),
                    );
                  },
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(Icons.fingerprint,
                          size: 11, color: AppColors.muted),
                      const SizedBox(width: 4),
                      Text(
                        'uid: $shortUid',
                        style: AppText.mono(size: 10),
                      ),
                      const SizedBox(width: 4),
                      Icon(Icons.content_copy,
                          size: 10, color: AppColors.muted),
                    ],
                  ),
                ),
              ],
            ],
          ),
        ),
        const PopupMenuDivider(),
        PopupMenuItem(
          value: 'settings',
          child: Row(
            children: [
              Icon(Icons.settings_outlined, size: 16, color: AppColors.ink2),
              const SizedBox(width: 10),
              Text('Settings', style: AppText.body(size: 14)),
            ],
          ),
        ),
        PopupMenuItem(
          value: 'logout',
          child: Row(
            children: [
              Icon(Icons.logout, size: 16, color: AppColors.crimson),
              const SizedBox(width: 10),
              Text(
                'Sign out',
                style: AppText.body(size: 14, color: AppColors.crimson),
              ),
            ],
          ),
        ),
      ];
      },
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 6),
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(999),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            _Avatar(photoUrl: photoUrl, initials: initials),
            if (!compact) ...[
              const SizedBox(width: 10),
              Text(
                name,
                style: AppText.body(
                  size: 14,
                  weight: FontWeight.w500,
                  color: AppColors.ink,
                ),
              ),
              Icon(Icons.keyboard_arrow_down,
                  size: 16, color: AppColors.muted),
              const SizedBox(width: 4),
            ],
          ],
        ),
      ),
    );
  }
}
