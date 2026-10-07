import 'dart:async';

import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:uuid/uuid.dart';

import '../models/notification.dart';
import 'auth_service.dart';

/// Writes & streams [AppNotification]s. Firestore when signed in, in-memory
/// stream when running in demo mode.
class NotificationService {
  NotificationService._();
  static final instance = NotificationService._();

  static const _uuid = Uuid();

  bool get _hasFirestore => Firebase.apps.isNotEmpty;

  final List<AppNotification> _memory = <AppNotification>[];
  final _memoryController = StreamController<List<AppNotification>>.broadcast();

  CollectionReference<Map<String, dynamic>>? _col(String ownerId) {
    if (!_hasFirestore) return null;
    return FirebaseFirestore.instance
        .collection('users')
        .doc(ownerId)
        .collection('notifications');
  }

  Stream<List<AppNotification>> watchMyNotifications({int limit = 50}) {
    final uid = AuthService.instance.currentUser?.uid;
    if (uid == null) return Stream.value(const []);
    final col = _col(uid);
    if (col == null) {
      Future.microtask(() => _memoryController.add(_sorted(_memory)));
      return _memoryController.stream;
    }
    return col
        .orderBy('createdAt', descending: true)
        .limit(limit)
        .snapshots()
        .map((snap) =>
            snap.docs.map((d) => AppNotification.fromJson(d.data())).toList());
  }

  Stream<int> watchUnreadCount() =>
      watchMyNotifications().map((list) => list.where((n) => !n.read).length);

  Future<void> emit({
    required NotificationKind kind,
    required String title,
    required String body,
    String? planId,
  }) async {
    final uid = AuthService.instance.currentUser?.uid ?? 'demo';
    final n = AppNotification(
      id: _uuid.v4(),
      ownerId: uid,
      kind: kind,
      title: title,
      body: body,
      planId: planId,
      createdAt: DateTime.now(),
    );
    final col = _col(uid);
    if (col == null) {
      _memory.insert(0, n);
      _memoryController.add(_sorted(_memory));
    } else {
      await col.doc(n.id).set(n.toJson());
    }
  }

  Future<void> markRead(String id) async {
    final uid = AuthService.instance.currentUser?.uid ?? 'demo';
    final col = _col(uid);
    if (col == null) {
      final i = _memory.indexWhere((n) => n.id == id);
      if (i >= 0) _memory[i] = _memory[i].copyWith(read: true);
      _memoryController.add(_sorted(_memory));
    } else {
      await col.doc(id).update({'read': true});
    }
  }

  Future<void> markAllRead() async {
    final uid = AuthService.instance.currentUser?.uid ?? 'demo';
    final col = _col(uid);
    if (col == null) {
      for (int i = 0; i < _memory.length; i++) {
        _memory[i] = _memory[i].copyWith(read: true);
      }
      _memoryController.add(_sorted(_memory));
    } else {
      final batch = FirebaseFirestore.instance.batch();
      final snap = await col.where('read', isEqualTo: false).get();
      for (final doc in snap.docs) {
        batch.update(doc.reference, {'read': true});
      }
      await batch.commit();
    }
  }

  Future<void> delete(String id) async {
    final uid = AuthService.instance.currentUser?.uid ?? 'demo';
    final col = _col(uid);
    if (col == null) {
      _memory.removeWhere((n) => n.id == id);
      _memoryController.add(_sorted(_memory));
    } else {
      await col.doc(id).delete();
    }
  }

  List<AppNotification> _sorted(List<AppNotification> list) {
    final sorted = [...list]..sort((a, b) => b.createdAt.compareTo(a.createdAt));
    return sorted;
  }
}
