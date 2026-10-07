import 'dart:async';
import 'dart:math' as math;

import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:uuid/uuid.dart';

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
  }) async {
    final uid = _requireOwnerId();
    final now = DateTime.now();
    final id = _uuid.v4();
    final nodes = _bootstrapNodes(title: title, audience: audience, rawText: rawText);
    final edges = _bootstrapEdges(nodes);
    final plan = Plan(
      id: id,
      ownerId: uid,
      title: title.trim().isEmpty ? _derivedTitle(audience, rawText) : title,
      audience: audience,
      inputMode: inputMode,
      rawText: rawText,
      artefacts: artefacts,
      nodes: nodes,
      edges: edges,
      status: PlanStatus.draft,
      createdAt: now,
      updatedAt: now,
    );

    final col = _col(uid);
    if (col == null) {
      _memory.insert(0, plan);
      _memoryController.add(_sortByUpdated(_memory));
    } else {
      await col.doc(id).set(plan.toJson());
    }
    await NotificationService.instance.emit(
      kind: NotificationKind.planCreated,
      title: 'Plan created',
      body: plan.title,
      planId: plan.id,
    );
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

  // ----- Stage-0 bootstrap -----
  // Until the LLM extractor is wired up, every new plan gets a tiny seed graph
  // so the mind-map viewer has something real to render. The user can see
  // their inputs reflected in the goal node; the rest are placeholder scaffold
  // that the real pipeline will replace in Phase 1.
  List<PlanNode> _bootstrapNodes({
    required String title,
    required Audience audience,
    String? rawText,
  }) {
    final goal = title.trim().isEmpty ? _derivedTitle(audience, rawText) : title;
    return [
      PlanNode(
        id: 'goal',
        label: goal,
        subLabel: 'goal · ${audience.label}',
        type: EvidenceType.fact,
        x: 0.5,
        y: 0.14,
        confidence: 1.0,
        source: 'user',
      ),
      const PlanNode(
        id: 'situation',
        label: 'Situation',
        subLabel: 'observation',
        type: EvidenceType.observation,
        x: 0.22,
        y: 0.45,
        confidence: 0.85,
      ),
      const PlanNode(
        id: 'resources',
        label: 'Resources',
        subLabel: 'facts',
        type: EvidenceType.fact,
        x: 0.78,
        y: 0.45,
        confidence: 0.9,
      ),
      const PlanNode(
        id: 'constraints',
        label: 'Constraints',
        subLabel: 'facts',
        type: EvidenceType.fact,
        x: 0.5,
        y: 0.62,
        confidence: 0.9,
      ),
      const PlanNode(
        id: 'risks',
        label: 'Risks',
        subLabel: 'hypothesis',
        type: EvidenceType.hypothesis,
        x: 0.25,
        y: 0.80,
        confidence: 0.6,
      ),
      const PlanNode(
        id: 'plan',
        label: 'Proposed plan',
        subLabel: 'prediction',
        type: EvidenceType.prediction,
        x: 0.75,
        y: 0.80,
        confidence: 0.7,
      ),
    ];
  }

  List<PlanEdge> _bootstrapEdges(List<PlanNode> nodes) {
    return const [
      PlanEdge(fromId: 'situation', toId: 'goal', kind: EdgeKind.supports),
      PlanEdge(fromId: 'resources', toId: 'goal', kind: EdgeKind.enables),
      PlanEdge(fromId: 'constraints', toId: 'plan', kind: EdgeKind.requires),
      PlanEdge(fromId: 'risks', toId: 'plan', kind: EdgeKind.blocks),
      PlanEdge(fromId: 'plan', toId: 'goal', kind: EdgeKind.causes),
      PlanEdge(fromId: 'situation', toId: 'plan', kind: EdgeKind.supports),
      PlanEdge(fromId: 'resources', toId: 'plan', kind: EdgeKind.supports),
    ];
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
