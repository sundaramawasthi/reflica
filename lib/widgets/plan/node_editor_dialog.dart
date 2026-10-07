import 'package:flutter/material.dart';
import 'package:uuid/uuid.dart';

import '../../models/plan.dart';
import '../../theme/app_theme.dart';

/// Dialog to add or edit a [PlanNode]. Returns the new/edited node, or null if
/// the user cancelled. If [existing] is null, the dialog is in "add" mode and
/// generates a fresh id.
class NodeEditorDialog extends StatefulWidget {
  final PlanNode? existing;
  const NodeEditorDialog({super.key, this.existing});

  static Future<PlanNode?> show(BuildContext context, {PlanNode? existing}) =>
      showDialog<PlanNode?>(
        context: context,
        builder: (_) => NodeEditorDialog(existing: existing),
      );

  @override
  State<NodeEditorDialog> createState() => _NodeEditorDialogState();
}

class _NodeEditorDialogState extends State<NodeEditorDialog> {
  late final TextEditingController _label;
  late final TextEditingController _subLabel;
  late final TextEditingController _source;
  late EvidenceType _type;
  late double _confidence;

  @override
  void initState() {
    super.initState();
    final e = widget.existing;
    _label = TextEditingController(text: e?.label ?? '');
    _subLabel = TextEditingController(text: e?.subLabel ?? '');
    _source = TextEditingController(text: e?.source ?? '');
    _type = e?.type ?? EvidenceType.observation;
    _confidence = e?.confidence ?? 0.8;
  }

  @override
  void dispose() {
    _label.dispose();
    _subLabel.dispose();
    _source.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final isEdit = widget.existing != null;
    return Dialog(
      backgroundColor: AppColors.surface,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 480),
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            mainAxisSize: MainAxisSize.min,
            children: [
              Row(
                children: [
                  Icon(isEdit ? Icons.edit_outlined : Icons.add_circle_outline,
                      color: AppColors.accent, size: 20),
                  const SizedBox(width: 10),
                  Text(isEdit ? 'Edit node' : 'Add node',
                      style:
                          AppText.serif(size: 18, weight: FontWeight.w500)),
                  const Spacer(),
                  IconButton(
                    icon: const Icon(Icons.close),
                    color: AppColors.muted,
                    onPressed: () => Navigator.of(context).pop(),
                  ),
                ],
              ),
              const SizedBox(height: 14),
              _field('Label', _label, hint: 'e.g. Road A, Shelter capacity'),
              const SizedBox(height: 14),
              _field('Short description', _subLabel,
                  hint: 'optional (shown under the node)'),
              const SizedBox(height: 14),
              _field('Source', _source,
                  hint: 'where did this fact come from?'),
              const SizedBox(height: 18),
              Text('EVIDENCE TYPE', style: AppText.eyebrow()),
              const SizedBox(height: 8),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: EvidenceType.values
                    .map((t) => ChoiceChip(
                          label: Text(t.name),
                          selected: _type == t,
                          onSelected: (_) => setState(() => _type = t),
                          selectedColor:
                              AppColors.accent.withValues(alpha: 0.18),
                          backgroundColor: AppColors.surface2,
                          side: BorderSide(
                            color: _type == t
                                ? AppColors.accent
                                : AppColors.line,
                          ),
                          labelStyle: AppText.body(
                            size: 12,
                            weight: FontWeight.w500,
                            color: _type == t
                                ? AppColors.accent
                                : AppColors.ink2,
                          ),
                        ))
                    .toList(),
              ),
              const SizedBox(height: 20),
              Row(
                children: [
                  Text('CONFIDENCE', style: AppText.eyebrow()),
                  const Spacer(),
                  Text(_confidence.toStringAsFixed(2),
                      style: AppText.mono(size: 12, color: AppColors.ink2)),
                ],
              ),
              Slider(
                value: _confidence,
                onChanged: (v) => setState(() => _confidence = v),
                activeColor: AppColors.accent,
                inactiveColor: AppColors.surface2,
              ),
              const SizedBox(height: 10),
              Row(
                mainAxisAlignment: MainAxisAlignment.end,
                children: [
                  TextButton(
                    onPressed: () => Navigator.of(context).pop(),
                    child: Text(
                      'Cancel',
                      style: AppText.body(
                          size: 14,
                          color: AppColors.ink2,
                          weight: FontWeight.w500),
                    ),
                  ),
                  const SizedBox(width: 8),
                  ElevatedButton.icon(
                    onPressed: _canSave ? _save : null,
                    icon: Icon(isEdit ? Icons.check : Icons.add,
                        size: 16, color: Colors.white),
                    label: Text(
                      isEdit ? 'Save' : 'Add node',
                      style: AppText.body(
                          size: 13.5,
                          weight: FontWeight.w600,
                          color: Colors.white),
                    ),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: AppColors.accent,
                      padding: const EdgeInsets.symmetric(
                          horizontal: 18, vertical: 12),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(10),
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  bool get _canSave => _label.text.trim().isNotEmpty;

  void _save() {
    final e = widget.existing;
    final node = PlanNode(
      id: e?.id ?? const Uuid().v4(),
      label: _label.text.trim(),
      subLabel: _subLabel.text.trim().isEmpty ? null : _subLabel.text.trim(),
      type: _type,
      x: e?.x ?? 0.5,
      y: e?.y ?? 0.5,
      confidence: _confidence,
      source: _source.text.trim().isEmpty ? null : _source.text.trim(),
    );
    Navigator.of(context).pop(node);
  }

  Widget _field(String label, TextEditingController ctrl,
      {String? hint, int maxLines = 1}) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label.toUpperCase(), style: AppText.eyebrow()),
        const SizedBox(height: 6),
        Container(
          decoration: BoxDecoration(
            color: Colors.white,
            border: Border.all(color: AppColors.line),
            borderRadius: BorderRadius.circular(8),
          ),
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
          child: TextField(
            controller: ctrl,
            maxLines: maxLines,
            onChanged: (_) => setState(() {}),
            decoration: InputDecoration(
              border: InputBorder.none,
              hintText: hint,
              hintStyle: AppText.body(size: 13, color: AppColors.muted),
              isCollapsed: true,
            ),
            style: AppText.body(size: 14, color: AppColors.ink),
          ),
        ),
      ],
    );
  }
}
