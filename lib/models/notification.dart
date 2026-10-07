import 'package:flutter/material.dart';

enum NotificationKind {
  planCreated,
  planUpdated,
  planDeleted,
  nodeAdded,
  nodeUpdated,
  nodeRemoved,
  edgeAdded,
  edgeRemoved,
}

extension NotificationKindX on NotificationKind {
  IconData get icon {
    switch (this) {
      case NotificationKind.planCreated:
        return Icons.auto_awesome;
      case NotificationKind.planUpdated:
        return Icons.edit_note;
      case NotificationKind.planDeleted:
        return Icons.delete_outline;
      case NotificationKind.nodeAdded:
        return Icons.add_circle_outline;
      case NotificationKind.nodeUpdated:
        return Icons.edit_outlined;
      case NotificationKind.nodeRemoved:
        return Icons.remove_circle_outline;
      case NotificationKind.edgeAdded:
        return Icons.alt_route;
      case NotificationKind.edgeRemoved:
        return Icons.link_off;
    }
  }
}

class AppNotification {
  final String id;
  final String ownerId;
  final NotificationKind kind;
  final String title;
  final String body;
  final String? planId;
  final bool read;
  final DateTime createdAt;

  const AppNotification({
    required this.id,
    required this.ownerId,
    required this.kind,
    required this.title,
    required this.body,
    this.planId,
    this.read = false,
    required this.createdAt,
  });

  AppNotification copyWith({bool? read}) => AppNotification(
        id: id,
        ownerId: ownerId,
        kind: kind,
        title: title,
        body: body,
        planId: planId,
        read: read ?? this.read,
        createdAt: createdAt,
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'ownerId': ownerId,
        'kind': kind.name,
        'title': title,
        'body': body,
        'planId': planId,
        'read': read,
        'createdAt': createdAt.toIso8601String(),
      };

  factory AppNotification.fromJson(Map<String, dynamic> j) => AppNotification(
        id: j['id'] as String,
        ownerId: j['ownerId'] as String,
        kind: NotificationKind.values
            .firstWhere((k) => k.name == j['kind'], orElse: () => NotificationKind.planUpdated),
        title: j['title'] as String,
        body: j['body'] as String,
        planId: j['planId'] as String?,
        read: j['read'] as bool? ?? false,
        createdAt: DateTime.parse(j['createdAt'] as String),
      );
}
