// Shows what a proposed change may affect and asks the researcher to approve
// or reject it. Returns true (approve), false (reject) or null (closed).

import 'package:flutter/material.dart';

import '../../graph/graph1.dart';
import '../../theme/app_theme.dart';
import 'graph_badges.dart';

Future<bool?> showImpactPreviewDialog(BuildContext context,
        {required ImpactPreviewView preview, required GraphDoc graph, required String title}) =>
    showDialog<bool>(
      context: context,
      builder: (_) => ImpactPreviewDialog(preview: preview, graph: graph, title: title),
    );

class ImpactPreviewDialog extends StatelessWidget {
  final ImpactPreviewView preview;
  final GraphDoc graph;
  final String title;
  const ImpactPreviewDialog(
      {super.key, required this.preview, required this.graph, required this.title});

  @override
  Widget build(BuildContext context) {
    final affected = preview.affected;
    final uncertain = affected.where((i) => !i.confirmed).length;
    return AlertDialog(
      backgroundColor: AppColors.surface,
      title: Text(title, style: AppText.serif(size: 20)),
      content: SizedBox(
        width: 560,
        child: ListView(shrinkWrap: true, children: [
          Text(
            affected.isEmpty
                ? 'Nothing else in the graph depends on this.'
                : '${affected.length} item${affected.length == 1 ? '' : 's'} may be affected'
                    '${uncertain > 0 ? ' ($uncertain uncertain)' : ''}. '
                    'They will be flagged for your review — not changed or deleted.',
            key: const ValueKey('impact-summary'),
            style: AppText.body(weight: FontWeight.w600, color: AppColors.ink),
          ),
          const SizedBox(height: 12),
          for (final i in affected)
            Container(
              key: ValueKey('impact-${i.nodeId}'),
              margin: const EdgeInsets.only(bottom: 10),
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                border: Border.all(color: AppColors.line),
                borderRadius: BorderRadius.circular(10),
              ),
              child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                Wrap(spacing: 6, runSpacing: 4, children: [
                  GraphChip(i.relation, color: AppColors.ink2),
                  CertaintyChip(i.confirmed, confirmedText: 'confirmed dependency',
                      uncertainText: 'uncertain dependency'),
                ]),
                const SizedBox(height: 6),
                Text(graph.labelOf(i.nodeId),
                    style: AppText.body(weight: FontWeight.w600, color: AppColors.ink)),
                Text(i.explanation, style: AppText.body(size: 13)),
              ]),
            ),
          if (preview.unaffected.isNotEmpty)
            Text('${preview.unaffected.length} other item(s) are not reached by any dependency link.',
                style: AppText.body(size: 13)),
          if (preview.relatedUnaffected.isNotEmpty)
            Text(
                'Related but not expected to change: '
                '${preview.relatedUnaffected.map(graph.labelOf).join(', ')}.',
                style: AppText.body(size: 13)),
          const SizedBox(height: 12),
          Text('PROPOSED UPDATES', style: AppText.eyebrow()),
          for (final u in preview.proposedUpdates)
            Text('• ${u.description}', style: AppText.body(size: 13)),
          const SizedBox(height: 12),
          ExpansionTile(
            tilePadding: EdgeInsets.zero,
            title: Text('How this was worked out (${preview.analyzer})', style: AppText.mono()),
            children: [
              for (final l in preview.limitations) Text('• $l', style: AppText.body(size: 12)),
            ],
          ),
        ]),
      ),
      actions: [
        TextButton(
          key: const ValueKey('reject-change'),
          onPressed: () => Navigator.of(context).pop(false),
          child: const Text('Reject'),
        ),
        FilledButton(
          key: const ValueKey('approve-change'),
          style: FilledButton.styleFrom(backgroundColor: AppColors.accent),
          onPressed: () => Navigator.of(context).pop(true),
          child: const Text('Approve change'),
        ),
      ],
    );
  }
}
