import 'dart:async';
import 'dart:math' as math;

import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:flutter/foundation.dart';
import 'package:uuid/uuid.dart';

import '../graph/graph1.dart';
import '../models/notification.dart';
import '../models/plan.dart';
import 'auth_service.dart';
import 'notification_service.dart';

/// Writes & streams [Plan]s. Uses Cloud Firestore when Firebase is initialised,
/// otherwise falls back to an in-memory store so demo mode still works.
class PlanRepository {
  PlanRepository._();
  static final instance = PlanRepository._();

  static const _uuid = Uuid();

  bool get _hasFirestore => Firebase.apps.isNotEmpty;

  /// Return the uid for the current write/read.
  ///
  /// When Firebase is initialised we REQUIRE a real signed-in user — never
  /// fall back to the 'demo' sentinel, because that silently writes plans
  /// into `users/demo/plans/*` which won't appear when the user later signs
  /// in on another device with their real account. The AuthGate shouldn't
  /// allow a signed-out user to reach any screen that calls these methods;
  /// if it ever does, we want a loud error rather than silent data loss.
  ///
  /// When Firebase is NOT initialised (demo mode), 'demo' is a valid tag for
  /// the in-memory store.
  String _requireOwnerId() {
    if (_hasFirestore) {
      final uid = AuthService.instance.currentUser?.uid;
      if (uid == null || uid.isEmpty) {
        throw StateError(
          'PlanRepository: Firestore is initialised but no user is signed '
          'in. Writes under a placeholder uid would cause cross-device sync '
          'to break. Make sure the UI waits for AuthGate before calling '
          'repository methods.',
        );
      }
      return uid;
    }
    return 'demo';
  }

  // -------- in-memory fallback (demo mode) --------
  final List<Plan> _memory = <Plan>[];
  final _memoryController = StreamController<List<Plan>>.broadcast();

  // -------- Firestore --------
  CollectionReference<Map<String, dynamic>>? _col(String ownerId) {
    if (!_hasFirestore) return null;
    return FirebaseFirestore.instance
        .collection('users')
        .doc(ownerId)
        .collection('plans');
  }

  /// Live stream of the current user's plans, newest first.
  Stream<List<Plan>> watchMyPlans() {
    final uid = AuthService.instance.currentUser?.uid;
    if (uid == null) return Stream.value(const []);
    final col = _col(uid);
    if (col == null) {
      // Memory stream — seed with current snapshot immediately.
      Future.microtask(() => _memoryController.add(_sortByUpdated(_memory)));
      return _memoryController.stream;
    }
    return col
        .orderBy('updatedAt', descending: true)
        .snapshots()
        .map((snap) => snap.docs.map((d) => Plan.fromJson(d.data())).toList());
  }

  Stream<Plan?> watchPlan(String id) {
    final uid = AuthService.instance.currentUser?.uid;
    if (uid == null) return Stream.value(null);
    final col = _col(uid);
    if (col == null) {
      return _memoryController.stream.map(
        (list) => list.where((p) => p.id == id).firstOrNull,
      ).distinct();
    }
    return col.doc(id).snapshots().map(
          (d) => d.data() == null ? null : Plan.fromJson(d.data()!),
        );
  }

  Future<Plan> createPlan({
    required String title,
    required Audience audience,
    required InputMode inputMode,
    String? rawText,
    List<InputArtefact> artefacts = const [],
    GraphUpdate? accepted,
  }) async {
    // New plans hold a graph@1 graph: the researcher-reviewed extraction
    // ([accepted]) or, when none is available, an empty graph. The fixed
    // starter nodes used before graph@1 are no longer created.
    final uid = _requireOwnerId();
    final now = DateTime.now();
    final id = _uuid.v4();
    final graph = accepted?.graph ?? GraphDoc.empty();
    final plan = Plan(
      id: id,
      ownerId: uid,
      title: title.trim().isEmpty ? _derivedTitle(audience, rawText) : title,
      audience: audience,
      inputMode: inputMode,
      rawText: rawText,
      artefacts: artefacts,
      status: PlanStatus.draft,
      createdAt: now,
      updatedAt: now,
      graph: graph.raw,
    );

    final col = _col(uid);
    if (col == null) {
      _memory.insert(0, plan);
      _memoryController.add(_sortByUpdated(_memory));
    } else {
      trackWrite(col.doc(id).set(plan.toJson()), 'plan "${plan.title}"');
    }
    if (accepted != null) {
      _appendEvent(uid, plan.id, 'proposal_accepted', accepted.record,
          before: null, after: accepted.record['graph_sha256'] as String?);
    }
    trackWrite(
        NotificationService.instance.emit(
          kind: NotificationKind.planCreated,
          title: 'Plan created',
          body: plan.title,
          planId: plan.id,
        ),
        'notification');
    return plan;
  }

  // Full-record save after edits. [reason] appears in the notification body.
  Future<void> save(Plan plan, {String reason = 'Plan updated'}) async {
    final uid = _requireOwnerId();
    final updated = plan.copyWith(updatedAt: DateTime.now());
    final col = _col(uid);
    if (col == null) {
      final i = _memory.indexWhere((p) => p.id == updated.id);
      if (i >= 0) {
        _memory[i] = updated;
      } else {
        _memory.insert(0, updated);
      }
      _memoryController.add(_sortByUpdated(_memory));
    } else {
      await col.doc(updated.id).set(updated.toJson());
    }
    await NotificationService.instance.emit(
      kind: NotificationKind.planUpdated,
      title: reason,
      body: updated.title,
      planId: updated.id,
    );
  }

  Future<void> renameTitle(Plan plan, String newTitle) async {
    if (newTitle.trim().isEmpty || newTitle.trim() == plan.title) return;
    await save(plan.copyWith(title: newTitle.trim()),
        reason: 'Plan renamed to “${newTitle.trim()}”');
  }

  Future<void> upsertNode(Plan plan, PlanNode node) async {
    final existing = plan.nodes.indexWhere((n) => n.id == node.id);
    final nodes = [...plan.nodes];
    final isNew = existing < 0;
    if (isNew) {
      nodes.add(node);
    } else {
      nodes[existing] = node;
    }
    final updated = plan.copyWith(nodes: nodes);
    final uid = _requireOwnerId();
    final col = _col(uid);
    if (col == null) {
      final i = _memory.indexWhere((p) => p.id == updated.id);
      if (i >= 0) _memory[i] = updated;
      _memoryController.add(_sortByUpdated(_memory));
    } else {
      await col.doc(updated.id).set(updated.toJson());
    }
    await NotificationService.instance.emit(
      kind: isNew ? NotificationKind.nodeAdded : NotificationKind.nodeUpdated,
      title: isNew ? 'Node added' : 'Node updated',
      body: '${node.label} · ${plan.title}',
      planId: plan.id,
    );
  }

  Future<void> removeNode(Plan plan, String nodeId) async {
    final node = plan.nodes.firstWhere((n) => n.id == nodeId,
        orElse: () => plan.nodes.first);
    final nodes = plan.nodes.where((n) => n.id != nodeId).toList();
    final edges = plan.edges
        .where((e) => e.fromId != nodeId && e.toId != nodeId)
        .toList();
    final updated = plan.copyWith(nodes: nodes, edges: edges);
    final uid = _requireOwnerId();
    final col = _col(uid);
    if (col == null) {
      final i = _memory.indexWhere((p) => p.id == updated.id);
      if (i >= 0) _memory[i] = updated;
      _memoryController.add(_sortByUpdated(_memory));
    } else {
      await col.doc(updated.id).set(updated.toJson());
    }
    await NotificationService.instance.emit(
      kind: NotificationKind.nodeRemoved,
      title: 'Node removed',
      body: '${node.label} · ${plan.title}',
      planId: plan.id,
    );
  }

  Future<void> addEdge(Plan plan, PlanEdge edge) async {
    final edges = [...plan.edges, edge];
    final updated = plan.copyWith(edges: edges);
    final uid = _requireOwnerId();
    final col = _col(uid);
    if (col == null) {
      final i = _memory.indexWhere((p) => p.id == updated.id);
      if (i >= 0) _memory[i] = updated;
      _memoryController.add(_sortByUpdated(_memory));
    } else {
      await col.doc(updated.id).set(updated.toJson());
    }
    await NotificationService.instance.emit(
      kind: NotificationKind.edgeAdded,
      title: 'Dependency added',
      body: '${edge.fromId} → ${edge.toId} (${edge.kind.name})',
      planId: plan.id,
    );
  }

  Future<void> removeEdge(Plan plan, PlanEdge edge) async {
    final edges = plan.edges
        .where((e) =>
            !(e.fromId == edge.fromId &&
                e.toId == edge.toId &&
                e.kind == edge.kind))
        .toList();
    final updated = plan.copyWith(edges: edges);
    final uid = _requireOwnerId();
    final col = _col(uid);
    if (col == null) {
      final i = _memory.indexWhere((p) => p.id == updated.id);
      if (i >= 0) _memory[i] = updated;
      _memoryController.add(_sortByUpdated(_memory));
    } else {
      await col.doc(updated.id).set(updated.toJson());
    }
    await NotificationService.instance.emit(
      kind: NotificationKind.edgeRemoved,
      title: 'Dependency removed',
      body: '${edge.fromId} → ${edge.toId}',
      planId: plan.id,
    );
  }

  /// Delete a plan. Pass the full [plan] when you have it (the detail page
  /// does) so the notification can carry its title. The returned future
  /// resolves once the UI has been updated — on Firestore the actual server
  /// write may still be in flight (offline persistence will sync it as soon
  /// as the device reaches the network).
  Future<void> delete(String id, {Plan? plan}) async {
    final uid = _requireOwnerId();
    final title = plan?.title ??
        (_memory.where((p) => p.id == id).firstOrNull)?.title ??
        id;

    final col = _col(uid);
    if (col == null) {
      // Demo mode / in-memory fallback.
      _memory.removeWhere((p) => p.id == id);
      _memoryController.add(_sortByUpdated(_memory));
    } else {
      // Issue the Firestore delete. We DO await it so that any immediate
      // network failure surfaces to the UI as an error (vs. silently
      // disappearing). With offline persistence on (enabled by default on
      // mobile and web), this completes instantly offline too — the write
      // joins the local queue and will push to the server when the device
      // next connects.
      try {
        await col.doc(id).delete();
      } catch (_) {
        // Offline queue may raise `UNAVAILABLE` on some SDK versions even
        // though the write WAS queued. Swallow — the queued write survives
        // app restart and syncs when the device reconnects.
      }
    }

    await NotificationService.instance.emit(
      kind: NotificationKind.planDeleted,
      title: 'Plan deleted',
      body: title,
      planId: id,
    );
  }

  List<Plan> _sortByUpdated(List<Plan> list) {
    final sorted = [...list]..sort((a, b) => b.updatedAt.compareTo(a.updatedAt));
    return sorted;
  }

  // ----- graph@1 updates and the event history -----

  /// Save the graph returned by an approved (or rejected) impact decision and
  /// append the decision record to the plan's history. Rejections are recorded
  /// too; the graph is then unchanged.
  Future<Plan> applyGraphUpdate(Plan plan, GraphUpdate update,
      {required String eventType}) async {
    final uid = _requireOwnerId();
    final updated = plan.copyWith(graph: update.graph.raw);
    final col = _col(uid);
    if (col == null) {
      final i = _memory.indexWhere((p) => p.id == updated.id);
      if (i >= 0) _memory[i] = updated;
      _memoryController.add(_sortByUpdated(_memory));
    } else {
      trackWrite(col.doc(updated.id).set(updated.toJson()), 'graph of "${plan.title}"');
    }
    _appendEvent(uid, plan.id, eventType, update.record,
        before: update.record['graph_before_sha256'] as String?,
        after: update.record['graph_after_sha256'] as String?);
    return updated;
  }

  // Append-only history: users/{uid}/plans/{planId}/events/{eventId}.
  // Timestamps and the actor live here, outside the fingerprinted records.
  final Map<String, List<Map<String, dynamic>>> _memoryEvents = {};

  void _appendEvent(String uid, String planId, String type,
      Map<String, dynamic> record, {String? before, String? after}) {
    final event = <String, dynamic>{
      'id': _uuid.v4(),
      'type': type,
      'actor_uid': uid,
      'graph_before_sha256': before,
      'graph_after_sha256': after,
      'record': record,
    };
    final col = _col(uid);
    if (col == null) {
      event['created_at'] = DateTime.now().toUtc().toIso8601String();
      (_memoryEvents[planId] ??= []).add(event);
    } else {
      event['created_at'] = FieldValue.serverTimestamp();
      trackWrite(col.doc(planId).collection('events').doc(event['id'] as String).set(event),
          'history entry "$type"');
    }
  }

  /// The plan's recorded decisions, oldest first (in-memory mode only; used by tests).
  List<Map<String, dynamic>> memoryEvents(String planId) =>
      List.unmodifiable(_memoryEvents[planId] ?? const []);

  // ----- background writes -----
  //
  // On Firestore a write's Future completes only when the server confirms it,
  // which can take long or not happen at all (offline, stalled connection),
  // while the data is already visible locally. graph@1 saves therefore do not
  // block the UI: each is tracked here, logged when confirmed, and reported on
  // [writeErrors] if it fails, so a failure is never silent.

  final _writeErrors = StreamController<String>.broadcast();

  /// Human-readable messages for saves that failed.
  Stream<String> get writeErrors => _writeErrors.stream;

  /// Track a save without waiting for it. Returns immediately.
  void trackWrite(Future<void> write, String what,
      {Duration warnAfter = const Duration(seconds: 20)}) {
    var done = false;
    Timer(warnAfter, () {
      if (!done) debugPrint('[Reflica] $what: not yet confirmed by the server (still queued)');
    });
    write.then((_) {
      done = true;
      debugPrint('[Reflica] $what: saved');
    }, onError: (Object e) {
      done = true;
      debugPrint('[Reflica] $what: FAILED: $e');
      _writeErrors.add('Could not save $what: $e');
    });
  }

  /// The signed-in account's stable id, recorded as `decided_by`.
  String get actorId => _requireOwnerId();

  void resetMemoryForTests() {
    _memory.clear();
    _memoryEvents.clear();
  }

  String _derivedTitle(Audience audience, String? text) {
    if (text != null && text.trim().isNotEmpty) {
      final line = text.trim().split('\n').first;
      final cut = line.length > 60 ? '${line.substring(0, 57)}…' : line;
      return cut;
    }
    const words = ['Plan', 'Scenario', 'Situation', 'Brief'];
    final w = words[math.Random().nextInt(words.length)];
    return 'New $w · ${audience.label}';
  }
}
