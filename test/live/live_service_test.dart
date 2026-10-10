// Live check against a running reflica_service (real HTTP, no mocks).
// Skipped unless run with --dart-define=REFLICA_LIVE=true, e.g.:
//   (cd research && python -m reflica_service.demo \
//        --response tests/service/data/extraction/good_response.json) &
//   flutter test test/live --dart-define=REFLICA_LIVE=true
// The demo service uses a scripted model; no real LLM is called.

import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:reflicaa/services/reflica_api.dart';

const live = bool.fromEnvironment('REFLICA_LIVE');

void main() {
  test('text → proposal → review → preview → approve over real HTTP', () async {
    final api = ReflicaApi();
    final health = await api.health();
    expect((health.graphVersion, health.scripted), ('graph@1', true));

    final text = File('research/tests/service/data/extraction/input.txt').readAsStringSync();
    final proposal = await api.extract(text, title: 'Irrigation');
    expect(proposal.graph.nodes.length, 7);
    final accepted = await api.accept(proposal,
        decidedBy: 'live-test', removeNodes: ['n7'], confirmEdges: ['x2']);
    expect(accepted.graph.nodes.length, 6);

    final preview = await api.preview(accepted.graph, {'op': 'delete_node', 'node_id': 'n3'});
    expect(preview.affected.map((i) => i.nodeId), ['n2', 'n4', 'n6']);
    final done = await api.decide(accepted.graph, preview, approve: true, decidedBy: 'live-test');
    expect(done.graph.nodes.where((n) => n.needsReview).length, 3);
    expect(done.record['graph_before_sha256'], isNot(done.record['graph_after_sha256']));

    // the same preview cannot be applied to the changed graph
    await expectLater(api.decide(done.graph, preview, approve: true, decidedBy: 'live-test'),
        throwsA(isA<ReflicaApiException>().having((e) => e.code, 'code', 'graph_changed')));
  }, skip: live ? false : 'set --dart-define=REFLICA_LIVE=true with the demo service running');
}
