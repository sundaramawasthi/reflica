import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:reflicaa/graph/graph1.dart';
import 'package:reflicaa/screens/proposal_review_screen.dart';

import 'support/fixtures.dart';

Future<GraphUpdate?> _open(WidgetTester tester, FakeBackend b) async {
  tester.view.physicalSize = const Size(900, 3000);
  tester.view.devicePixelRatio = 1;
  addTearDown(tester.view.reset);
  GraphUpdate? result;
  await tester.pumpWidget(MaterialApp(
    home: Builder(
      builder: (ctx) => TextButton(
        onPressed: () async {
          result = await Navigator.of(ctx).push<GraphUpdate>(MaterialPageRoute(
            builder: (_) => ProposalReviewScreen(
                proposal: ExtractionProposalView.fromJson(fixture('proposal.json')),
                api: b.api(),
                decidedBy: 'uid-demo'),
          ));
        },
        child: const Text('open'),
      ),
    ),
  ));
  await tester.tap(find.text('open'));
  await tester.pumpAndSettle();
  return result;
}

void main() {
  testWidgets('shows what was understood, where each item came from, and saves nothing yet',
      (tester) async {
    final b = FakeBackend({'POST /v1/extract/accept': (200, fixture('accept_response.json'))});
    await _open(tester, b);
    expect(find.text('NOTHING IS SAVED UNTIL YOU ACCEPT'), findsOneWidget);
    expect(find.textContaining('soil moisture, through weekly irrigation'), findsOneWidget);
    expect(find.text('• Were plots assigned to irrigation at random?'), findsOneWidget);
    expect(find.text('Quoted from your text'), findsNWidgets(6));
    expect(find.text('Suggested by AI — not in your text'), findsOneWidget); // the limitation
    expect(find.text('suggested — unconfirmed'), findsNWidgets(4));
    expect(find.text('stated in your text'), findsNWidgets(2));
    expect(find.textContaining('scripted/scripted-v1'), findsOneWidget);
    expect(b.requests, isEmpty);
  });

  testWidgets('accept sends exactly the researcher\'s choices', (tester) async {
    final b = FakeBackend({'POST /v1/extract/accept': (200, fixture('accept_response.json'))});
    await _open(tester, b);
    await tester.tap(find.byKey(const ValueKey('keep-n7')));   // drop the AI-suggested limitation
    await tester.tap(find.byKey(const ValueKey('confirm-x2'))); // vouch for an inferred link
    await tester.pump();
    expect(find.text('Accept 6 items'), findsOneWidget);
    await tester.tap(find.byKey(const ValueKey('accept-proposal')));
    await tester.pumpAndSettle();
    expect(b.lastBody('POST /v1/extract/accept'), fixture('accept_request.json'));
    expect(find.byType(ProposalReviewScreen), findsNothing); // popped with the result
  });

  testWidgets('links of a removed item cannot be confirmed or kept', (tester) async {
    final b = FakeBackend({});
    await _open(tester, b);
    await tester.tap(find.byKey(const ValueKey('keep-n7')));
    await tester.pump();
    final cb = tester.widget<Checkbox>(find.byKey(const ValueKey('keep-x6')));
    expect((cb.value, cb.onChanged), (false, null));
    expect(find.byKey(const ValueKey('confirm-x6')), findsNothing);
  });

  testWidgets('a service error is shown and nothing is popped', (tester) async {
    final b = FakeBackend({'POST /v1/extract/accept': (409, {
      'error': {'code': 'proposal_modified', 'message': 'The proposal was changed.', 'detail': {}}
    })});
    await _open(tester, b);
    await tester.tap(find.byKey(const ValueKey('accept-proposal')));
    await tester.pumpAndSettle();
    expect(find.text('The proposal was changed.'), findsOneWidget);
    expect(find.byType(ProposalReviewScreen), findsOneWidget);
  });
}
