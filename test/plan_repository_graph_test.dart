// Runs without Firebase, so PlanRepository uses its in-memory store.
import 'dart:async';

import 'package:flutter_test/flutter_test.dart';
import 'package:reflicaa/graph/graph1.dart';
import 'package:reflicaa/models/plan.dart';
import 'package:reflicaa/services/plan_repository.dart';

import 'support/fixtures.dart';

void main() {
  final repo = PlanRepository.instance;
  setUp(repo.resetMemoryForTests);

  GraphUpdate accepted() {
    final j = fixture('accept_response.json');
    return GraphUpdate(GraphDoc.fromJson(j['graph'] as Map<String, dynamic>),
        j['record'] as Map<String, dynamic>);
  }

  test('a plan is created from the accepted graph, not from template nodes', () async {
    final plan = await repo.createPlan(
        title: 'Irrigation', audience: Audience.individual, inputMode: InputMode.text,
        rawText: 'text', accepted: accepted());
    expect(plan.nodes, isEmpty);
    expect(plan.edges, isEmpty);
    expect(GraphDoc.fromJson(plan.graph!).nodes.length, 6);
    final events = repo.memoryEvents(plan.id);
    expect(events.single['type'], 'proposal_accepted');
    expect(events.single['actor_uid'], repo.actorId);
    expect(events.single['graph_after_sha256'], accepted().record['graph_sha256']);
    expect(events.single['created_at'], isNotNull);
  });

  test('without an extraction the plan starts with an empty graph', () async {
    final plan = await repo.createPlan(
        title: 'Voice note', audience: Audience.individual, inputMode: InputMode.voice);
    expect(GraphDoc.fromJson(plan.graph!).nodes, isEmpty);
    expect(plan.nodes, isEmpty);
    expect(repo.memoryEvents(plan.id), isEmpty);
  });

  test('approved and rejected decisions are both appended to the history', () async {
    var plan = await repo.createPlan(
        title: 'Irrigation', audience: Audience.individual, inputMode: InputMode.text,
        accepted: accepted());
    for (final (name, type) in [
      ('decide_approve.json', 'change_approved'),
      ('decide_reject.json', 'change_rejected')
    ]) {
      final j = fixture(name);
      plan = await repo.applyGraphUpdate(
          plan,
          GraphUpdate(GraphDoc.fromJson(j['graph'] as Map<String, dynamic>),
              j['record'] as Map<String, dynamic>),
          eventType: type);
    }
    final events = repo.memoryEvents(plan.id);
    expect(events.map((e) => e['type']), ['proposal_accepted', 'change_approved', 'change_rejected']);
    final rejected = events.last;
    expect(rejected['graph_before_sha256'], rejected['graph_after_sha256']);
    expect(Plan.fromJson(plan.toJson()).graph, plan.graph);
  });

  test('background saves never block, and failures are reported, not silent', () async {
    final errors = <String>[];
    final sub = repo.writeErrors.listen(errors.add);
    final never = Completer<void>(); // a server that never confirms
    final sw = Stopwatch()..start();
    repo.trackWrite(never.future, 'plan "stuck"', warnAfter: const Duration(milliseconds: 10));
    repo.trackWrite(Future<void>.value(), 'plan "ok"');
    repo.trackWrite(Future<void>.error(StateError('permission-denied')), 'history entry "x"');
    expect(sw.elapsedMilliseconds, lessThan(50), reason: 'trackWrite returns immediately');
    await Future<void>.delayed(const Duration(milliseconds: 30));
    expect(errors, ['Could not save history entry "x": Bad state: permission-denied']);
    await sub.cancel();
  });
}
