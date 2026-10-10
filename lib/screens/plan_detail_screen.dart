import 'package:flutter/material.dart';

import '../graph/graph1.dart';
import '../models/plan.dart';
import '../services/plan_repository.dart';
import '../services/reflica_api.dart';
import '../theme/app_theme.dart';
import '../widgets/dashboard/dashboard_sidebar.dart';
import '../widgets/graph/research_graph_panel.dart';
import '../widgets/plan/node_editor_dialog.dart';
import '../widgets/plan/plan_mind_map.dart';
import '../widgets/responsive.dart';

class PlanDetailScreen extends StatelessWidget {
  final String planId;
  const PlanDetailScreen({super.key, required this.planId});

  @override
  Widget build(BuildContext context) {
    final showSidebar =
        screenSizeOf(context).index >= ScreenSize.desktop.index;
    return Scaffold(
      backgroundColor: AppColors.bg,
      drawer: showSidebar
          ? null
          : Drawer(
              backgroundColor: AppColors.surface,
              child: DashboardSidebar(
                selected: 2,
                onSelect: (i) {
                  Navigator.of(context).maybePop();
                  if (i == 0) {
                    Navigator.of(context)
                        .pushNamedAndRemoveUntil('/', (r) => false);
                  } else {
                    Navigator.of(context)
                        .pushReplacementNamed(sidebarItems[i].route);
                  }
                },
              ),
            ),
      body: SafeArea(
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (showSidebar)
              SizedBox(
                width: 240,
                child: DashboardSidebar(
                  selected: 2,
                  onSelect: (i) {
                    if (i == 0) {
                      Navigator.of(context)
                          .pushNamedAndRemoveUntil('/', (r) => false);
                    } else {
                      Navigator.of(context)
                          .pushReplacementNamed(sidebarItems[i].route);
                    }
                  },
                ),
              ),
            Expanded(
              child: Container(
                decoration: const BoxDecoration(
                  border: Border(left: BorderSide(color: AppColors.line)),
                ),
                child: StreamBuilder<Plan?>(
                  stream: PlanRepository.instance.watchPlan(planId),
                  builder: (context, snap) {
                    if (snap.connectionState == ConnectionState.waiting) {
                      return const Center(
                        child: SizedBox(
                          width: 24,
                          height: 24,
                          child: CircularProgressIndicator(
                            strokeWidth: 2,
                            valueColor:
                                AlwaysStoppedAnimation(AppColors.accent),
                          ),
                        ),
                      );
                    }
                    final plan = snap.data;
                    if (plan == null) return _NotFound();
                    return _DetailBody(plan: plan, showMenu: !showSidebar);
                  },
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _DetailBody extends StatefulWidget {
  final Plan plan;
  final bool showMenu;
  const _DetailBody({required this.plan, required this.showMenu});

  @override
  State<_DetailBody> createState() => _DetailBodyState();
}

class _DetailBodyState extends State<_DetailBody> {
  bool _editMode = false;

  @override
  Widget build(BuildContext context) {
    if (widget.plan.hasGraph) return _graphBody(context);
    return Column(
      children: [
        _TopBar(
          plan: widget.plan,
          showMenu: widget.showMenu,
          editMode: _editMode,
          onToggleEdit: () => setState(() => _editMode = !_editMode),
        ),
        if (_editMode)
          _EditToolbar(plan: widget.plan),
        Expanded(
          child: Padding(
            padding: const EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                _PlanMeta(plan: widget.plan),
                const SizedBox(height: 16),
                Expanded(
                  child: _editMode
                      ? _EditableNodeList(plan: widget.plan)
                      : PlanMindMap(plan: widget.plan),
                ),
                const SizedBox(height: 12),
                _RawInputBlock(
                  plan: widget.plan,
                  editMode: _editMode,
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }
}

extension on _DetailBodyState {
  // graph@1 plans: the researcher-reviewed graph; changes go through the
  // impact preview and are recorded in the plan's event history.
  Widget _graphBody(BuildContext context) {
    final repo = PlanRepository.instance;
    return Column(
      children: [
        _TopBar(
          plan: widget.plan,
          showMenu: widget.showMenu,
          editMode: false,
          showEditToggle: false,
          onToggleEdit: () {},
        ),
        Expanded(
          child: Padding(
            padding: const EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                _PlanMeta(plan: widget.plan),
                const SizedBox(height: 16),
                Expanded(
                  child: ResearchGraphPanel(
                    graph: GraphDoc.fromJson(widget.plan.graph!),
                    api: ReflicaApi.instance,
                    decidedBy: repo.actorId,
                    onUpdate: (up, type) async {
                      await repo.applyGraphUpdate(widget.plan, up, eventType: type);
                    },
                  ),
                ),
                const SizedBox(height: 12),
                _RawInputBlock(plan: widget.plan, editMode: false),
              ],
            ),
          ),
        ),
      ],
    );
  }
}

// ---------- top bar with inline title edit ----------

class _TopBar extends StatefulWidget {
  final Plan plan;
  final bool showMenu;
  final bool editMode;
  final bool showEditToggle;
  final VoidCallback onToggleEdit;
  const _TopBar({
    required this.plan,
    required this.showMenu,
    required this.editMode,
    required this.onToggleEdit,
    this.showEditToggle = true,
  });

  @override
  State<_TopBar> createState() => _TopBarState();
}

class _TopBarState extends State<_TopBar> {
  bool _editing = false;
  late final TextEditingController _ctrl;

  @override
  void initState() {
    super.initState();
    _ctrl = TextEditingController(text: widget.plan.title);
  }

  @override
  void didUpdateWidget(covariant _TopBar oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (!_editing && oldWidget.plan.title != widget.plan.title) {
      _ctrl.text = widget.plan.title;
    }
  }

  @override
  void dispose() {
    _ctrl.dispose();
    super.dispose();
  }

  Future<void> _commit() async {
    final newTitle = _ctrl.text.trim();
    setState(() => _editing = false);
    if (newTitle.isNotEmpty && newTitle != widget.plan.title) {
      await PlanRepository.instance.renameTitle(widget.plan, newTitle);
    }
  }

  @override
  Widget build(BuildContext context) {
    final isNarrow = MediaQuery.sizeOf(context).width < 560;
    return Container(
      constraints: BoxConstraints(minHeight: isNarrow ? 84 : 72),
      padding: EdgeInsets.symmetric(
          horizontal: isNarrow ? 8 : 20, vertical: 10),
      decoration: const BoxDecoration(
        border: Border(bottom: BorderSide(color: AppColors.line)),
      ),
      child: Row(
        children: [
          if (widget.showMenu)
            Builder(
              builder: (ctx) => IconButton(
                icon: const Icon(Icons.menu),
                color: AppColors.ink2,
                onPressed: () => Scaffold.of(ctx).openDrawer(),
              ),
            ),
          IconButton(
            icon: const Icon(Icons.arrow_back),
            color: AppColors.ink2,
            onPressed: () =>
                Navigator.of(context).pushReplacementNamed('/plans'),
          ),
          const SizedBox(width: 4),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisAlignment: MainAxisAlignment.center,
              mainAxisSize: MainAxisSize.min,
              children: [
                _editing
                    ? Row(
                        children: [
                          Expanded(
                            child: TextField(
                              controller: _ctrl,
                              autofocus: true,
                              onSubmitted: (_) => _commit(),
                              style: AppText.serif(
                                  size: 18, weight: FontWeight.w500),
                              decoration: const InputDecoration(
                                border: InputBorder.none,
                                isCollapsed: true,
                              ),
                            ),
                          ),
                          IconButton(
                            icon: Icon(Icons.check,
                                color: AppColors.sage, size: 20),
                            onPressed: _commit,
                          ),
                        ],
                      )
                    : GestureDetector(
                        onTap: widget.editMode
                            ? () => setState(() => _editing = true)
                            : null,
                        child: Row(
                          children: [
                            Flexible(
                              child: Text(
                                widget.plan.title,
                                style: AppText.serif(
                                    size: 17, weight: FontWeight.w500),
                                maxLines: 1,
                                overflow: TextOverflow.ellipsis,
                              ),
                            ),
                            if (widget.editMode) ...[
                              const SizedBox(width: 6),
                              Icon(Icons.edit_outlined,
                                  size: 14, color: AppColors.muted),
                            ],
                          ],
                        ),
                      ),
                Text(
                  '${widget.plan.audience.label} · ${widget.plan.inputMode.label} · ${widget.plan.status.name}',
                  style: AppText.mono(size: 11),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
              ],
            ),
          ),
          if (widget.showEditToggle)
            _EditToggle(active: widget.editMode, onTap: widget.onToggleEdit),
          const SizedBox(width: 8),
          IconButton(
            tooltip: 'Delete plan',
            icon: const Icon(Icons.delete_outline),
            color: AppColors.crimson,
            onPressed: () async {
              final confirmed = await showDialog<bool>(
                context: context,
                builder: (ctx) => AlertDialog(
                  backgroundColor: AppColors.surface,
                  title: const Text('Delete this plan?'),
                  content: Text(
                    'This removes the plan and its graph. You cannot undo this.',
                    style: AppText.body(size: 14, color: AppColors.ink2),
                  ),
                  actions: [
                    TextButton(
                      onPressed: () => Navigator.of(ctx).pop(false),
                      child: const Text('Cancel'),
                    ),
                    TextButton(
                      onPressed: () => Navigator.of(ctx).pop(true),
                      child: Text(
                        'Delete',
                        style: TextStyle(color: AppColors.crimson),
                      ),
                    ),
                  ],
                ),
              );
              if (confirmed != true) return;
              await PlanRepository.instance
                  .delete(widget.plan.id, plan: widget.plan);
              if (context.mounted) {
                Navigator.of(context).pushReplacementNamed('/plans');
              }
            },
          ),
        ],
      ),
    );
  }
}

class _EditToggle extends StatelessWidget {
  final bool active;
  final VoidCallback onTap;
  const _EditToggle({required this.active, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 150),
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
        decoration: BoxDecoration(
          color: active ? AppColors.accent : Colors.transparent,
          border: Border.all(
            color: active ? AppColors.accent : AppColors.lineStrong,
          ),
          borderRadius: BorderRadius.circular(999),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              active ? Icons.check : Icons.edit_outlined,
              size: 15,
              color: active ? Colors.white : AppColors.ink2,
            ),
            const SizedBox(width: 8),
            Text(
              active ? 'Done' : 'Edit',
              style: AppText.body(
                size: 13,
                weight: FontWeight.w600,
                color: active ? Colors.white : AppColors.ink,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// ---------- edit toolbar ----------

class _EditToolbar extends StatelessWidget {
  final Plan plan;
  const _EditToolbar({required this.plan});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
      decoration: BoxDecoration(
        color: AppColors.accent.withValues(alpha: 0.06),
        border: const Border(
          bottom: BorderSide(color: AppColors.line),
        ),
      ),
      child: Row(
        children: [
          Icon(Icons.edit_note, size: 18, color: AppColors.accent),
          const SizedBox(width: 10),
          Text(
            'Edit mode · changes save in real time',
            style: AppText.body(
              size: 13,
              weight: FontWeight.w500,
              color: AppColors.accent,
            ),
          ),
          const Spacer(),
          ElevatedButton.icon(
            onPressed: () async {
              final node = await NodeEditorDialog.show(context);
              if (node != null) {
                await PlanRepository.instance.upsertNode(plan, node);
              }
            },
            icon: const Icon(Icons.add, size: 16, color: Colors.white),
            label: Text(
              'Add node',
              style: AppText.body(
                  size: 13,
                  weight: FontWeight.w600,
                  color: Colors.white),
            ),
            style: ElevatedButton.styleFrom(
              backgroundColor: AppColors.accent,
              padding:
                  const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(10),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

// ---------- editable node list (replaces the mind map in edit mode) ----------

class _EditableNodeList extends StatelessWidget {
  final Plan plan;
  const _EditableNodeList({required this.plan});

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: AppColors.surface,
        border: Border.all(color: AppColors.line),
        borderRadius: BorderRadius.circular(14),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Container(
            padding:
                const EdgeInsets.symmetric(horizontal: 18, vertical: 14),
            decoration: const BoxDecoration(
              border: Border(bottom: BorderSide(color: AppColors.line)),
            ),
            child: Row(
              children: [
                Icon(Icons.layers_outlined, size: 18, color: AppColors.ink2),
                const SizedBox(width: 10),
                Text('Nodes',
                    style: AppText.serif(
                        size: 16, weight: FontWeight.w500)),
                const Spacer(),
                Text('${plan.nodes.length} total',
                    style: AppText.mono(size: 12)),
              ],
            ),
          ),
          Expanded(
            child: plan.nodes.isEmpty
                ? Center(
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(Icons.hub_outlined,
                            size: 28, color: AppColors.muted),
                        const SizedBox(height: 10),
                        Text(
                          'No nodes yet',
                          style: AppText.body(
                              size: 14,
                              weight: FontWeight.w500,
                              color: AppColors.ink2),
                        ),
                        const SizedBox(height: 4),
                        Text('Use "Add node" above.',
                            style: AppText.body(
                                size: 12, color: AppColors.muted)),
                      ],
                    ),
                  )
                : ListView.separated(
                    itemCount: plan.nodes.length,
                    separatorBuilder: (_, _) =>
                        const Divider(color: AppColors.line, height: 1),
                    itemBuilder: (ctx, i) {
                      final n = plan.nodes[i];
                      return _NodeRow(plan: plan, node: n);
                    },
                  ),
          ),
        ],
      ),
    );
  }
}

class _NodeRow extends StatefulWidget {
  final Plan plan;
  final PlanNode node;
  const _NodeRow({required this.plan, required this.node});

  @override
  State<_NodeRow> createState() => _NodeRowState();
}

class _NodeRowState extends State<_NodeRow> {
  bool _hover = false;

  Color _color() {
    switch (widget.node.type) {
      case EvidenceType.fact:
        return AppColors.sage;
      case EvidenceType.observation:
        return AppColors.accent;
      case EvidenceType.prediction:
        return AppColors.violet;
      case EvidenceType.hypothesis:
        return AppColors.amber;
      case EvidenceType.assumption:
        return AppColors.crimson;
    }
  }

  @override
  Widget build(BuildContext context) {
    final n = widget.node;
    final color = _color();
    return MouseRegion(
      onEnter: (_) => setState(() => _hover = true),
      onExit: (_) => setState(() => _hover = false),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 12),
        color: _hover ? AppColors.surface2 : Colors.transparent,
        child: Row(
          children: [
            Container(
              width: 10,
              height: 10,
              decoration: BoxDecoration(color: color, shape: BoxShape.circle),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    n.label,
                    style: AppText.body(
                      size: 14,
                      weight: FontWeight.w500,
                      color: AppColors.ink,
                    ),
                  ),
                  Text(
                    '${n.type.name} · c ${n.confidence.toStringAsFixed(2)}'
                    '${n.subLabel != null ? ' · ${n.subLabel}' : ''}'
                    '${n.source != null ? ' · src: ${n.source}' : ''}',
                    style: AppText.mono(size: 11),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                ],
              ),
            ),
            IconButton(
              tooltip: 'Edit node',
              icon: Icon(Icons.edit_outlined,
                  size: 18, color: AppColors.ink2),
              onPressed: () async {
                final updated =
                    await NodeEditorDialog.show(context, existing: n);
                if (updated != null) {
                  await PlanRepository.instance.upsertNode(widget.plan, updated);
                }
              },
            ),
            IconButton(
              tooltip: 'Delete node',
              icon: Icon(Icons.delete_outline,
                  size: 18, color: AppColors.crimson),
              onPressed: () async {
                await PlanRepository.instance
                    .removeNode(widget.plan, n.id);
              },
            ),
          ],
        ),
      ),
    );
  }
}

// ---------- plan meta ----------

class _PlanMeta extends StatelessWidget {
  final Plan plan;
  const _PlanMeta({required this.plan});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.surface,
        border: Border.all(color: AppColors.line),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Wrap(
        spacing: 24,
        runSpacing: 10,
        children: [
          _MetaItem(
              icon: plan.audience.icon,
              label: 'For',
              value: plan.audience.label),
          _MetaItem(
              icon: plan.inputMode.icon,
              label: 'Input',
              value: plan.inputMode.label),
          _MetaItem(
              icon: Icons.layers_outlined,
              label: plan.hasGraph ? 'Items' : 'Nodes',
              value: '${plan.hasGraph ? (plan.graph!['nodes'] as List).length : plan.nodes.length}'),
          _MetaItem(
              icon: Icons.alt_route_outlined,
              label: plan.hasGraph ? 'Links' : 'Edges',
              value: '${plan.hasGraph ? (plan.graph!['edges'] as List).length : plan.edges.length}'),
          _MetaItem(
              icon: Icons.schedule,
              label: 'Updated',
              value: _relative(plan.updatedAt)),
          if (plan.artefacts.isNotEmpty)
            _MetaItem(
                icon: Icons.attachment,
                label: 'Attachments',
                value: '${plan.artefacts.length}'),
        ],
      ),
    );
  }

  String _relative(DateTime t) {
    final diff = DateTime.now().difference(t);
    if (diff.inSeconds < 60) return 'just now';
    if (diff.inMinutes < 60) return '${diff.inMinutes}m ago';
    if (diff.inHours < 24) return '${diff.inHours}h ago';
    return '${diff.inDays}d ago';
  }
}

class _MetaItem extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;
  const _MetaItem({
    required this.icon,
    required this.label,
    required this.value,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(icon, size: 16, color: AppColors.muted),
        const SizedBox(width: 8),
        Text('$label: ',
            style: AppText.mono(size: 11, color: AppColors.muted)),
        Text(value,
            style: AppText.body(
              size: 13,
              color: AppColors.ink,
              weight: FontWeight.w500,
            )),
      ],
    );
  }
}

// ---------- raw input (editable in edit mode) ----------

class _RawInputBlock extends StatefulWidget {
  final Plan plan;
  final bool editMode;
  const _RawInputBlock({required this.plan, required this.editMode});

  @override
  State<_RawInputBlock> createState() => _RawInputBlockState();
}

class _RawInputBlockState extends State<_RawInputBlock> {
  late final TextEditingController _ctrl;
  bool _editing = false;

  @override
  void initState() {
    super.initState();
    _ctrl = TextEditingController(text: widget.plan.rawText ?? '');
  }

  @override
  void didUpdateWidget(covariant _RawInputBlock old) {
    super.didUpdateWidget(old);
    if (!_editing && old.plan.rawText != widget.plan.rawText) {
      _ctrl.text = widget.plan.rawText ?? '';
    }
  }

  @override
  void dispose() {
    _ctrl.dispose();
    super.dispose();
  }

  Future<void> _commit() async {
    final text = _ctrl.text.trim();
    setState(() => _editing = false);
    if (text == (widget.plan.rawText ?? '')) return;
    final updated = Plan(
      id: widget.plan.id,
      ownerId: widget.plan.ownerId,
      title: widget.plan.title,
      audience: widget.plan.audience,
      inputMode: widget.plan.inputMode,
      rawText: text,
      artefacts: widget.plan.artefacts,
      nodes: widget.plan.nodes,
      edges: widget.plan.edges,
      status: widget.plan.status,
      createdAt: widget.plan.createdAt,
      updatedAt: DateTime.now(),
    );
    await PlanRepository.instance.save(updated, reason: 'Original input edited');
  }

  @override
  Widget build(BuildContext context) {
    if ((widget.plan.rawText == null || widget.plan.rawText!.trim().isEmpty) &&
        !widget.editMode) {
      return const SizedBox.shrink();
    }
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: AppColors.surface,
        border: Border.all(color: AppColors.line),
        borderRadius: BorderRadius.circular(10),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Text('ORIGINAL INPUT', style: AppText.eyebrow()),
              const Spacer(),
              if (widget.editMode)
                _editing
                    ? TextButton.icon(
                        onPressed: _commit,
                        icon: Icon(Icons.check,
                            size: 14, color: AppColors.sage),
                        label: Text(
                          'Save',
                          style: AppText.body(
                              size: 12,
                              weight: FontWeight.w600,
                              color: AppColors.sage),
                        ),
                      )
                    : TextButton.icon(
                        onPressed: () => setState(() => _editing = true),
                        icon: Icon(Icons.edit_outlined,
                            size: 14, color: AppColors.ink2),
                        label: Text(
                          'Edit',
                          style: AppText.body(
                              size: 12,
                              weight: FontWeight.w600,
                              color: AppColors.ink2),
                        ),
                      ),
            ],
          ),
          const SizedBox(height: 6),
          _editing
              ? TextField(
                  controller: _ctrl,
                  autofocus: true,
                  minLines: 3,
                  maxLines: 10,
                  decoration: InputDecoration(
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(8),
                      borderSide:
                          const BorderSide(color: AppColors.line),
                    ),
                    isDense: true,
                  ),
                  style: AppText.body(size: 14, color: AppColors.ink2),
                )
              : Text(
                  widget.plan.rawText ?? '',
                  style: AppText.body(size: 14, color: AppColors.ink2),
                  maxLines: 6,
                  overflow: TextOverflow.ellipsis,
                ),
        ],
      ),
    );
  }
}

class _NotFound extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(Icons.cloud_off_outlined, size: 36, color: AppColors.muted),
          const SizedBox(height: 12),
          Text(
            'Plan not found',
            style: AppText.serif(size: 20, weight: FontWeight.w500),
          ),
          const SizedBox(height: 16),
          TextButton(
            onPressed: () =>
                Navigator.of(context).pushReplacementNamed('/plans'),
            child: const Text('Back to My Plans'),
          ),
        ],
      ),
    );
  }
}
