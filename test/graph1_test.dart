import 'dart:convert';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:reflicaa/graph/graph1.dart';
import 'package:reflicaa/models/plan.dart';

import 'support/fixtures.dart';

void main() {
  test('parses the shared graph@1 example used by the Python tests', () {
    final j = jsonDecode(File('research/tests/service/data/graph/research_example.json')
        .readAsStringSync()) as Map<String, dynamic>;
    final g = GraphDoc.fromJson(j);
    expect(g.nodes.map((n) => n.id), ['h1', 'm1', 'r1', 'a1', 't1', 'l1']);
    final h1 = g.node('h1')!;
    expect((h1.kind, h1.basis), ('hypothesis', Basis.sourceQuoted));
    expect(h1.spans.single.quote, 'higher soil moisture increases wheat yield in semi-arid plots');
    expect(g.node('l1')!.basis, Basis.llmInferred);
    expect(identical(g.raw, j), isTrue, reason: 'raw JSON is kept, not re-serialised');
  });

  test('edge direction reads as the contract defines', () {
    final g = GraphDoc.fromJson(fixture('accept_response.json')['graph'] as Map<String, dynamic>);
    String sentence(String id) => edgeSentence(g.edges.firstWhere((e) => e.id == id), g.labelOf);
    expect(sentence('x2'), "Weekly irrigated plots yielded 18% more grain is derived from "
        "2024 field trial measuring grain yield in 40 plots");
    expect(sentence('x4'), 'Weekly irrigated plots yielded 18% more grain requires '
        'Soil type is similar across plots');
  });

  test('confirmed vs inferred links come from the service, not the client', () {
    final p = ExtractionProposalView.fromJson(fixture('proposal.json'));
    final byId = {for (final e in p.graph.edges) e.id: e};
    expect(byId['x3']!.confirmed, isTrue);  // quote found in the text
    expect(byId['x2']!.confirmed, isFalse); // no quote: inferred
    expect(byId['x2']!.basis, Basis.llmInferred);
    expect(p.clarifyingQuestions, isNotEmpty);
    expect(p.provider, 'scripted');
  });

  test('impact preview view', () {
    final pv = ImpactPreviewView.fromJson(fixture('preview_delete_n3.json'));
    expect(pv.items.firstWhere((i) => i.relation == 'changed').nodeId, 'n3');
    expect({for (final i in pv.affected) i.nodeId: (i.relation, i.confirmed)}, {
      'n2': ('downstream', true),
      'n4': ('direct', true),
      'n6': ('downstream', true),
    });
    expect(pv.proposedUpdates.first.action, 'delete_node');
    expect(pv.limitations, isNotEmpty);
  });

  test('rejects other contract versions and unknown values', () {
    expect(() => GraphDoc.fromJson({'version': 'graph@2', 'nodes': [], 'edges': []}),
        throwsFormatException);
    expect(() => parseBasis('fact'), throwsFormatException);
  });

  test('every basis has a plain-language label', () {
    for (final b in Basis.values) {
      expect(basisLabel(b), isNotEmpty);
    }
    expect(basisLabel(Basis.llmInferred), contains('not in your text'));
  });

  group('Plan storage', () {
    final legacy = {
      'id': 'p', 'ownerId': 'u', 'title': 't', 'audience': 'individual', 'inputMode': 'text',
      'nodes': [], 'edges': [], 'status': 'draft',
      'createdAt': '2026-10-01T00:00:00.000', 'updatedAt': '2026-10-01T00:00:00.000',
    };

    test('plans saved before graph@1 still load, without a graph', () {
      final p = Plan.fromJson(legacy);
      expect(p.hasGraph, isFalse);
      expect(p.toJson().containsKey('graph'), isFalse);
    });

    test('graph round-trips, including loosely typed nested maps from Firestore', () {
      final graph = fixture('accept_response.json')['graph'] as Map<String, dynamic>;
      Object? loosen(Object? v) => switch (v) {
            Map() => <Object?, Object?>{for (final e in v.entries) e.key: loosen(e.value)},
            List() => [for (final x in v) loosen(x)],
            _ => v,
          };
      final p = Plan.fromJson({...legacy, 'graph': loosen(graph)});
      expect(p.hasGraph, isTrue);
      expect(jsonEncode(p.graph), jsonEncode(graph));
      expect(GraphDoc.fromJson(p.graph!).nodes.length, 6);
    });
  });
}
