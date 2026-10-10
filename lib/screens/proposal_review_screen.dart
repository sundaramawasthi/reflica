// Review an extraction proposal before anything is saved.
//
// The researcher sees what Reflica understood (restatement, clarifying
// questions), every proposed item with where it came from, every proposed
// link with its certainty, and every issue the service corrected. They choose
// what to keep and which suggested links to confirm. Pops with the accepted
// [GraphUpdate], or null if cancelled.

import 'package:flutter/material.dart';

import '../graph/graph1.dart';
import '../services/reflica_api.dart';
import '../theme/app_theme.dart';
import '../widgets/graph/graph_badges.dart';

class ProposalReviewScreen extends StatefulWidget {
  final ExtractionProposalView proposal;
  final ReflicaApi api;
  final String decidedBy;
  const ProposalReviewScreen(
      {super.key, required this.proposal, required this.api, required this.decidedBy});

  @override
  State<ProposalReviewScreen> createState() => _ProposalReviewScreenState();
}

class _ProposalReviewScreenState extends State<ProposalReviewScreen> {
  final _removedNodes = <String>{};
  final _removedEdges = <String>{};
  final _confirmedEdges = <String>{};
  bool _saving = false;
  String? _error;

  GraphDoc get g => widget.proposal.graph;

  bool _edgeGone(GEdge e) =>
      _removedEdges.contains(e.id) ||
      _removedNodes.contains(e.source) ||
      _removedNodes.contains(e.target);

  Future<void> _save() async {
    setState(() {
      _saving = true;
      _error = null;
    });
    try {
      final liveConfirm = [
        for (final e in g.edges)
          if (_confirmedEdges.contains(e.id) && !_edgeGone(e)) e.id
      ];
      final up = await widget.api.accept(widget.proposal,
          decidedBy: widget.decidedBy,
          removeNodes: _removedNodes.toList()..sort(),
          removeEdges: [
            for (final e in g.edges)
              if (_removedEdges.contains(e.id) &&
                  !_removedNodes.contains(e.source) &&
                  !_removedNodes.contains(e.target))
                e.id
          ],
          confirmEdges: liveConfirm);
      if (mounted) Navigator.of(context).pop(up);
    } on ReflicaApiException catch (e) {
      setState(() {
        _saving = false;
        _error = e.message;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final p = widget.proposal;
    final warnings = [for (final i in p.issues) if (i.warning) i];
    final kept = g.nodes.length - _removedNodes.length;
    return Scaffold(
      backgroundColor: AppColors.bg,
      appBar: AppBar(
        backgroundColor: AppColors.surface,
        title: Text('Review the proposed graph', style: AppText.serif(size: 20)),
      ),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(16, 16, 16, 120),
        children: [
          Text('NOTHING IS SAVED UNTIL YOU ACCEPT', style: AppText.eyebrow()),
          const SizedBox(height: 8),
          _Section(title: 'What Reflica understood', children: [
            Text(p.restatement, style: AppText.body()),
            if (p.clarifyingQuestions.isNotEmpty) ...[
              const SizedBox(height: 10),
              Text('Questions for you', style: AppText.body(weight: FontWeight.w600)),
              for (final q in p.clarifyingQuestions)
                Padding(
                    padding: const EdgeInsets.only(top: 4),
                    child: Text('• $q', style: AppText.body(size: 14))),
            ],
            const SizedBox(height: 8),
            Text('Proposed by ${p.provider}/${p.model}. AI suggestions can be wrong.',
                style: AppText.mono()),
          ]),
          if (warnings.isNotEmpty)
            _Section(title: 'Corrected by Reflica (${warnings.length})', children: [
              for (final w in warnings)
                Padding(
                  padding: const EdgeInsets.only(bottom: 6),
                  child: Text('${w.ref == null ? '' : '[${w.ref}] '}${w.message}',
                      key: ValueKey('issue-${w.code}-${w.ref}'),
                      style: AppText.body(size: 13, color: AppColors.amber)),
                ),
            ]),
          _Section(title: 'Items ($kept of ${g.nodes.length} kept)', children: [
            for (final n in g.nodes) _itemTile(n),
          ]),
          _Section(title: 'Links', children: [
            if (g.edges.isEmpty) Text('No links proposed.', style: AppText.body(size: 14)),
            for (final e in g.edges) _edgeTile(e),
          ]),
          if (_error != null)
            Text(_error!, key: const ValueKey('review-error'),
                style: AppText.body(color: AppColors.crimson)),
        ],
      ),
      bottomNavigationBar: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(children: [
            TextButton(
                onPressed: _saving ? null : () => Navigator.of(context).pop(),
                child: const Text('Cancel')),
            const Spacer(),
            FilledButton.icon(
              key: const ValueKey('accept-proposal'),
              style: FilledButton.styleFrom(backgroundColor: AppColors.accent),
              onPressed: _saving || kept == 0 ? null : _save,
              icon: _saving
                  ? const SizedBox(
                      width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2))
                  : const Icon(Icons.check),
              label: Text('Accept $kept items'),
            ),
          ]),
        ),
      ),
    );
  }

  Widget _itemTile(GNode n) {
    final removed = _removedNodes.contains(n.id);
    return Opacity(
      opacity: removed ? 0.45 : 1,
      child: CheckboxListTile(
        key: ValueKey('keep-${n.id}'),
        contentPadding: EdgeInsets.zero,
        controlAffinity: ListTileControlAffinity.leading,
        value: !removed,
        onChanged: (v) => setState(() => v == true ? _removedNodes.remove(n.id) : _removedNodes.add(n.id)),
        title: Wrap(spacing: 6, runSpacing: 4, children: [KindChip(n.kind), BasisChip(n.basis)]),
        subtitle: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          const SizedBox(height: 6),
          Text(n.label, style: AppText.body(weight: FontWeight.w600, color: AppColors.ink)),
          for (final s in n.spans) QuoteBlock(s.quote),
        ]),
      ),
    );
  }

  Widget _edgeTile(GEdge e) {
    final gone = _edgeGone(e);
    final byNode = _removedNodes.contains(e.source) || _removedNodes.contains(e.target);
    return Opacity(
      opacity: gone ? 0.45 : 1,
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 6),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Row(children: [
            Checkbox(
              key: ValueKey('keep-${e.id}'),
              value: !gone,
              onChanged: byNode
                  ? null
                  : (v) => setState(
                      () => v == true ? _removedEdges.remove(e.id) : _removedEdges.add(e.id)),
            ),
            Expanded(child: Text(edgeSentence(e, g.labelOf), style: AppText.body(size: 14))),
          ]),
          Padding(
            padding: const EdgeInsets.only(left: 48),
            child: Wrap(spacing: 8, runSpacing: 4, crossAxisAlignment: WrapCrossAlignment.center, children: [
              CertaintyChip(e.confirmed || _confirmedEdges.contains(e.id),
                  confirmedText: e.confirmed ? 'stated in your text' : 'confirmed by you',
                  uncertainText: 'suggested — unconfirmed'),
              if (!e.confirmed && !gone)
                FilterChip(
                  key: ValueKey('confirm-${e.id}'),
                  label: const Text('I confirm this link'),
                  selected: _confirmedEdges.contains(e.id),
                  onSelected: (v) => setState(
                      () => v ? _confirmedEdges.add(e.id) : _confirmedEdges.remove(e.id)),
                ),
            ]),
          ),
          for (final s in e.spans) Padding(padding: const EdgeInsets.only(left: 48), child: QuoteBlock(s.quote)),
        ]),
      ),
    );
  }
}

class _Section extends StatelessWidget {
  final String title;
  final List<Widget> children;
  const _Section({required this.title, required this.children});

  @override
  Widget build(BuildContext context) => Padding(
        padding: const EdgeInsets.only(bottom: 14),
        // A Material (not a decorated box) so list tiles inside show their ink.
        child: Material(
          color: AppColors.surface,
          shape: RoundedRectangleBorder(
            side: const BorderSide(color: AppColors.line),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Padding(
            padding: const EdgeInsets.all(14),
            child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Text(title, style: AppText.serif(size: 17)),
              const SizedBox(height: 10),
              ...children,
            ]),
          ),
        ),
      );
}
