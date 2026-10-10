// The saved graph@1 graph of a plan, with researcher-controlled changes.
//
// Every edit, deletion or review resolution goes through the service:
// preview → impact dialog → approve or reject → [onUpdate] saves the new graph
// and the decision record. Nothing changes locally without the service.

import 'package:flutter/material.dart';

import '../../graph/graph1.dart';
import '../../services/reflica_api.dart';
import '../../theme/app_theme.dart';
import 'graph_badges.dart';
import 'impact_preview_dialog.dart';

const nodeKinds = [
  'goal', 'question', 'hypothesis', 'assumption', 'claim', 'method', 'evidence', 'result',
  'limitation', 'task'
];

typedef GraphUpdateHandler = Future<void> Function(GraphUpdate update, String eventType);

class ResearchGraphPanel extends StatefulWidget {
  final GraphDoc graph;
  final ReflicaApi api;
  final String decidedBy;
  final GraphUpdateHandler onUpdate;
  const ResearchGraphPanel(
      {super.key,
      required this.graph,
      required this.api,
      required this.decidedBy,
      required this.onUpdate});

  @override
  State<ResearchGraphPanel> createState() => _ResearchGraphPanelState();
}

class _ResearchGraphPanelState extends State<ResearchGraphPanel> {
  bool _busy = false;

  GraphDoc get g => widget.graph;

  void _snack(String text) =>
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(text)));

  Future<void> _change(Map<String, dynamic> change, String title) async {
    setState(() => _busy = true);
    try {
      final preview = await widget.api.preview(g, change);
      if (!mounted) return;
      final ok = await showImpactPreviewDialog(context, preview: preview, graph: g, title: title);
      if (ok == null) return; // closed without deciding: nothing recorded
      final up = await widget.api.decide(g, preview, approve: ok, decidedBy: widget.decidedBy);
      await widget.onUpdate(up, ok ? 'change_approved' : 'change_rejected');
      if (mounted) _snack(ok ? 'Change applied. Affected items are flagged for review.' : 'Change rejected; nothing was changed.');
    } on ReflicaApiException catch (e) {
      if (mounted) _snack(e.message);
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  Future<void> _edit(GNode n) async {
    final labelCtrl = TextEditingController(text: n.label);
    var kind = n.kind;
    final result = await showDialog<(String, String)>(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setLocal) => AlertDialog(
          title: const Text('Edit item'),
          content: Column(mainAxisSize: MainAxisSize.min, children: [
            TextField(
                key: const ValueKey('edit-label'),
                controller: labelCtrl,
                maxLength: 300,
                decoration: const InputDecoration(labelText: 'Statement')),
            DropdownButtonFormField<String>(
              key: const ValueKey('edit-kind'),
              initialValue: kind,
              decoration: const InputDecoration(labelText: 'Kind'),
              items: [for (final k in nodeKinds) DropdownMenuItem(value: k, child: Text(k))],
              onChanged: (v) => setLocal(() => kind = v ?? kind),
            ),
            if (n.basis != Basis.userStated)
              Padding(
                padding: const EdgeInsets.only(top: 8),
                child: Text('Changing the wording makes it your statement; the original source '
                    'quote is kept for reference.', style: AppText.body(size: 12)),
              ),
          ]),
          actions: [
            TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancel')),
            FilledButton(
                key: const ValueKey('edit-preview'),
                onPressed: () => Navigator.pop(ctx, (labelCtrl.text.trim(), kind)),
                child: const Text('Preview impact')),
          ],
        ),
      ),
    );
    if (result == null) return;
    final (label, newKind) = result;
    final change = <String, dynamic>{'op': 'edit_node', 'node_id': n.id};
    if (label.isNotEmpty && label != n.label) change['label'] = label;
    if (newKind != n.kind) change['kind'] = newKind;
    if (change.length == 2) return _snack('Nothing was changed.');
    await _change(change, 'Edit “${n.label}”?');
  }

  @override
  Widget build(BuildContext context) {
    if (g.nodes.isEmpty) {
      return Center(
        child: Text('This graph has no items yet.', key: const ValueKey('empty-graph'),
            style: AppText.body(color: AppColors.muted)),
      );
    }
    final flagged = g.nodes.where((n) => n.needsReview).length;
    return AbsorbPointer(
      absorbing: _busy,
      child: ListView(
        children: [
          if (flagged > 0)
            Padding(
              padding: const EdgeInsets.only(bottom: 10),
              child: GraphChip('$flagged item${flagged == 1 ? '' : 's'} need your review',
                  color: AppColors.amber, icon: Icons.flag_outlined),
            ),
          for (final n in g.nodes) _nodeCard(n),
          const SizedBox(height: 8),
          Text('LINKS', style: AppText.eyebrow()),
          for (final e in g.edges)
            Padding(
              padding: const EdgeInsets.only(top: 6),
              child: Row(children: [
                Expanded(child: Text(edgeSentence(e, g.labelOf), style: AppText.body(size: 13))),
                CertaintyChip(e.confirmed, uncertainText: 'inferred'),
              ]),
            ),
        ],
      ),
    );
  }

  Widget _nodeCard(GNode n) => Container(
        key: ValueKey('node-${n.id}'),
        margin: const EdgeInsets.only(bottom: 10),
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: AppColors.surface,
          border: Border.all(color: n.needsReview ? AppColors.amber : AppColors.line),
          borderRadius: BorderRadius.circular(12),
        ),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Row(children: [
            Expanded(
              child: Wrap(spacing: 6, runSpacing: 4, children: [
                KindChip(n.kind),
                BasisChip(n.basis),
                if (n.needsReview)
                  const GraphChip('needs review', color: AppColors.amber, icon: Icons.flag),
              ]),
            ),
            PopupMenuButton<String>(
              key: ValueKey('menu-${n.id}'),
              onSelected: (v) => switch (v) {
                'edit' => _edit(n),
                'delete' => _change({'op': 'delete_node', 'node_id': n.id}, 'Delete “${n.label}”?'),
                _ => _change({'op': 'resolve_review', 'node_id': n.id}, 'Mark “${n.label}” as reviewed?'),
              },
              itemBuilder: (_) => [
                const PopupMenuItem(value: 'edit', child: Text('Edit…')),
                const PopupMenuItem(value: 'delete', child: Text('Delete…')),
                if (n.needsReview) const PopupMenuItem(value: 'resolve', child: Text('Mark reviewed…')),
              ],
            ),
          ]),
          const SizedBox(height: 6),
          Text(n.label, style: AppText.body(weight: FontWeight.w600, color: AppColors.ink)),
          for (final s in n.spans) QuoteBlock(s.quote),
          for (final r in n.reviews)
            Padding(
              padding: const EdgeInsets.only(top: 6),
              child: Text(r.reason, style: AppText.body(size: 12, color: AppColors.amber)),
            ),
        ]),
      );
}
