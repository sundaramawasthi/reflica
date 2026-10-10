import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:reflicaa/graph/graph1.dart';
import 'package:reflicaa/widgets/graph/research_graph_panel.dart';

import 'support/fixtures.dart';

final _routes = {
  'POST /v1/impact/preview': (200, fixture('preview_delete_n3.json')),
  'POST /v1/impact/decide': (200, fixture('decide_approve.json')),
};

Future<List<(GraphUpdate, String)>> _pump(WidgetTester tester, FakeBackend b) async {
  tester.view.physicalSize = const Size(1000, 3000);
  tester.view.devicePixelRatio = 1;
  addTearDown(tester.view.reset);
  final updates = <(GraphUpdate, String)>[];
  await tester.pumpWidget(MaterialApp(
    home: Scaffold(
      body: ResearchGraphPanel(
        graph: GraphDoc.fromJson(fixture('accept_response.json')['graph'] as Map<String, dynamic>),
        api: b.api(),
        decidedBy: 'uid-demo',
        onUpdate: (u, type) async => updates.add((u, type)),
      ),
    ),
  ));
  return updates;
}

Future<void> _delete(WidgetTester tester, String id) async {
  await tester.tap(find.byKey(ValueKey('menu-$id')));
  await tester.pumpAndSettle();
  await tester.tap(find.text('Delete…'));
  await tester.pumpAndSettle();
}

void main() {
  testWidgets('delete → impact preview → approve → dependents flagged, event recorded',
      (tester) async {
    final b = FakeBackend(_routes);
    final updates = await _pump(tester, b);
    await _delete(tester, 'n3');
    expect(b.lastBody('POST /v1/impact/preview')!['change'], {'op': 'delete_node', 'node_id': 'n3'});
    expect(find.textContaining('3 items may be affected'), findsOneWidget);
    expect(find.textContaining('flagged for your review — not changed or deleted'), findsOneWidget);
    expect(find.byKey(const ValueKey('impact-n4')), findsOneWidget);
    expect(find.text('confirmed dependency'), findsNWidgets(3));
    expect(updates, isEmpty, reason: 'nothing changes before the decision');
    await tester.tap(find.byKey(const ValueKey('approve-change')));
    await tester.pumpAndSettle();
    final decision = b.lastBody('POST /v1/impact/decide')!['decision'] as Map;
    expect((decision['decision'], decision['decided_by']), ('approve', 'uid-demo'));
    expect(updates.single.$2, 'change_approved');
    expect(updates.single.$1.graph.nodes.where((n) => n.needsReview).map((n) => n.id),
        ['n2', 'n4', 'n6']);
  });

  testWidgets('reject is sent and recorded; closing the dialog records nothing', (tester) async {
    final b = FakeBackend({..._routes, 'POST /v1/impact/decide': (200, fixture('decide_reject.json'))});
    final updates = await _pump(tester, b);
    await _delete(tester, 'n3');
    await tester.tap(find.byKey(const ValueKey('reject-change')));
    await tester.pumpAndSettle();
    expect((b.lastBody('POST /v1/impact/decide')!['decision'] as Map)['decision'], 'reject');
    expect(updates.single.$2, 'change_rejected');
    expect(find.text('Change rejected; nothing was changed.'), findsOneWidget);

    await _delete(tester, 'n3');
    await tester.tapAt(const Offset(5, 5)); // dismiss the dialog without deciding
    await tester.pumpAndSettle();
    expect(updates.length, 1);
    expect(b.requests.where((r) => r.$1 == 'POST /v1/impact/decide').length, 1);
  });

  testWidgets('a stale preview is refused by the service and reported', (tester) async {
    final b = FakeBackend({..._routes,
      'POST /v1/impact/decide': (409, fixture('error_graph_changed.json'))});
    final updates = await _pump(tester, b);
    await _delete(tester, 'n3');
    await tester.tap(find.byKey(const ValueKey('approve-change')));
    await tester.pumpAndSettle();
    expect(updates, isEmpty);
    expect(find.textContaining('graph has changed since the preview'), findsOneWidget);
  });

  testWidgets('edit sends only the fields that changed', (tester) async {
    final b = FakeBackend(_routes);
    await _pump(tester, b);
    await tester.tap(find.byKey(const ValueKey('menu-n2')));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Edit…'));
    await tester.pumpAndSettle();
    expect(find.textContaining('makes it your statement'), findsOneWidget);
    await tester.enterText(find.byKey(const ValueKey('edit-label')), 'Weekly irrigation is associated with yield');
    await tester.tap(find.byKey(const ValueKey('edit-preview')));
    await tester.pumpAndSettle();
    expect(b.lastBody('POST /v1/impact/preview')!['change'], {
      'op': 'edit_node', 'node_id': 'n2', 'label': 'Weekly irrigation is associated with yield'
    });
  });

  testWidgets('shows kind, origin and quotes; flags items needing review', (tester) async {
    final b = FakeBackend(_routes);
    tester.view.physicalSize = const Size(1000, 3000);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.reset);
    await tester.pumpWidget(MaterialApp(home: Scaffold(body: ResearchGraphPanel(
      graph: GraphDoc.fromJson(fixture('decide_approve.json')['graph'] as Map<String, dynamic>),
      api: b.api(), decidedBy: 'u', onUpdate: (_, _) async {}))));
    expect(find.text('3 items need your review'), findsOneWidget);
    expect(find.text('needs review'), findsNWidgets(3));
    expect(find.text('HYPOTHESIS'), findsOneWidget);
    expect(find.textContaining("'n3' was deleted."), findsNWidgets(3));
  });

  testWidgets('an empty graph says so instead of showing template nodes', (tester) async {
    await tester.pumpWidget(MaterialApp(home: Scaffold(body: ResearchGraphPanel(
      graph: GraphDoc.empty(), api: FakeBackend({}).api(), decidedBy: 'u',
      onUpdate: (_, _) async {}))));
    expect(find.byKey(const ValueKey('empty-graph')), findsOneWidget);
  });
}
