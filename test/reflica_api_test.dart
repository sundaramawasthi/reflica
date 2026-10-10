import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:reflicaa/graph/graph1.dart';
import 'package:reflicaa/services/reflica_api.dart';

import 'support/fixtures.dart';

void main() {
  test('accept sends the proposal unchanged plus the review', () async {
    final b = FakeBackend({'POST /v1/extract/accept': (200, fixture('accept_response.json'))});
    final proposal = ExtractionProposalView.fromJson(fixture('proposal.json'));
    final up = await b.api().accept(proposal,
        decidedBy: 'uid-demo', removeNodes: ['n7'], confirmEdges: ['x2']);
    final body = b.lastBody('POST /v1/extract/accept')!;
    expect(body, fixture('accept_request.json'));
    expect(up.graph.nodes.length, 6);
    expect(up.record['confirmed_edges'], ['x2']);
  });

  test('preview and decide round-trip the preview exactly', () async {
    final graph = GraphDoc.fromJson(fixture('accept_response.json')['graph'] as Map<String, dynamic>);
    final b = FakeBackend({
      'POST /v1/impact/preview': (200, fixture('preview_delete_n3.json')),
      'POST /v1/impact/decide': (200, fixture('decide_approve.json')),
    });
    final api = b.api();
    final pv = await api.preview(graph, {'op': 'delete_node', 'node_id': 'n3'});
    expect(b.lastBody('POST /v1/impact/preview'),
        {'graph': graph.raw, 'change': {'op': 'delete_node', 'node_id': 'n3'}});
    final up = await api.decide(graph, pv, approve: true, decidedBy: 'uid-demo');
    final body = b.lastBody('POST /v1/impact/decide')!;
    expect(body['preview'], fixture('preview_delete_n3.json'));
    expect(body['decision'], {
      'preview_sha256': pv.sha256, 'decision': 'approve', 'decided_by': 'uid-demo', 'note': null
    });
    expect(up.graph.nodes.where((n) => n.needsReview).map((n) => n.id), ['n2', 'n4', 'n6']);
  });

  test('service errors keep their stable code and status', () async {
    final b = FakeBackend({'POST /v1/impact/decide': (409, fixture('error_graph_changed.json'))});
    final graph = GraphDoc.fromJson(fixture('accept_response.json')['graph'] as Map<String, dynamic>);
    final pv = ImpactPreviewView.fromJson(fixture('preview_delete_n3.json'));
    await expectLater(
      b.api().decide(graph, pv, approve: true, decidedBy: 'u'),
      throwsA(isA<ReflicaApiException>()
          .having((e) => e.code, 'code', 'graph_changed')
          .having((e) => e.status, 'status', 409)),
    );
  });

  test('unreachable service and non-JSON replies have their own codes', () async {
    final down = ReflicaApi(
        baseUrl: 'http://reflica.test',
        client: MockClient((_) async => throw http.ClientException('connection refused')));
    await expectLater(down.health(),
        throwsA(isA<ReflicaApiException>().having((e) => e.code, 'code', 'service_unreachable')));
    final html = ReflicaApi(
        baseUrl: 'http://reflica.test', client: MockClient((_) async => http.Response('<html>', 502)));
    await expectLater(html.health(),
        throwsA(isA<ReflicaApiException>().having((e) => e.code, 'code', 'bad_response')));
  });

  test('health reports whether extraction uses a scripted model', () async {
    final b = FakeBackend({'GET /v1/health': (200, {
      'status': 'ok', 'service_version': '0.0.1', 'graph_version': 'graph@1',
      'llm': 'scripted/fixture-demo'
    })});
    final h = await b.api().health();
    expect((h.graphVersion, h.scripted), ('graph@1', true));
  });
}
