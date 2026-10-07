import 'package:flutter/material.dart';

enum Audience {
  individual('Individuals', Icons.person_outline),
  organization('Organizations', Icons.business_outlined),
  research('Research & Academia', Icons.science_outlined),
  government('Government', Icons.account_balance_outlined),
  disaster('Disaster & Emergency', Icons.waves_outlined);

  final String label;
  final IconData icon;
  const Audience(this.label, this.icon);
}

enum InputMode {
  text('Free text', Icons.short_text, 'Describe your situation in your own words.'),
  form('Structured form', Icons.view_list_outlined, 'Fill in goal, entities, constraints step by step.'),
  voice('Voice', Icons.mic_none, 'Record a spoken brief.'),
  document('Documents', Icons.description_outlined, 'Upload PDFs, reports, spreadsheets.'),
  image('Images', Icons.image_outlined, 'Upload photos, scans or satellite tiles.'),
  video('Video', Icons.videocam_outlined, 'Upload a video brief or CCTV clip.'),
  camera('Live camera', Icons.photo_camera_outlined, 'Capture directly from your device camera.');

  final String label;
  final IconData icon;
  final String hint;
  const InputMode(this.label, this.icon, this.hint);
}

/// A fact in the cognitive graph. Blueprint §8 — one of five epistemic types.
enum EvidenceType { fact, observation, prediction, hypothesis, assumption }

class PlanNode {
  final String id;
  final String label;
  final String? subLabel;
  final EvidenceType type;
  // Normalized 0..1 position inside the mind-map canvas.
  final double x;
  final double y;
  final double confidence;
  final String? source;

  const PlanNode({
    required this.id,
    required this.label,
    this.subLabel,
    this.type = EvidenceType.observation,
    required this.x,
    required this.y,
    this.confidence = 0.9,
    this.source,
  });

  Map<String, dynamic> toJson() => {
        'id': id,
        'label': label,
        'subLabel': subLabel,
        'type': type.name,
        'x': x,
        'y': y,
        'confidence': confidence,
        'source': source,
      };

  factory PlanNode.fromJson(Map<String, dynamic> j) => PlanNode(
        id: j['id'] as String,
        label: j['label'] as String,
        subLabel: j['subLabel'] as String?,
        type: EvidenceType.values
            .firstWhere((e) => e.name == j['type'], orElse: () => EvidenceType.observation),
        x: (j['x'] as num).toDouble(),
        y: (j['y'] as num).toDouble(),
        confidence: (j['confidence'] as num?)?.toDouble() ?? 0.9,
        source: j['source'] as String?,
      );
}

enum EdgeKind { dependsOn, blocks, enables, causes, requires, supports }

class PlanEdge {
  final String fromId;
  final String toId;
  final EdgeKind kind;
  const PlanEdge({required this.fromId, required this.toId, required this.kind});

  Map<String, dynamic> toJson() => {
        'from': fromId,
        'to': toId,
        'kind': kind.name,
      };

  factory PlanEdge.fromJson(Map<String, dynamic> j) => PlanEdge(
        fromId: j['from'] as String,
        toId: j['to'] as String,
        kind: EdgeKind.values
            .firstWhere((k) => k.name == j['kind'], orElse: () => EdgeKind.dependsOn),
      );
}

/// Where the input artefact lives. For stage 0 we keep file bytes locally and
/// only the metadata in the plan record; later we move to Cloud Storage.
class InputArtefact {
  final String fileName;
  final String mimeType;
  final int bytes;
  const InputArtefact({
    required this.fileName,
    required this.mimeType,
    required this.bytes,
  });

  Map<String, dynamic> toJson() => {
        'fileName': fileName,
        'mimeType': mimeType,
        'bytes': bytes,
      };

  factory InputArtefact.fromJson(Map<String, dynamic> j) => InputArtefact(
        fileName: j['fileName'] as String,
        mimeType: j['mimeType'] as String,
        bytes: j['bytes'] as int,
      );
}

enum PlanStatus { draft, verified, changed, repaired }

class Plan {
  final String id;
  final String ownerId;
  final String title;
  final Audience audience;
  final InputMode inputMode;
  final String? rawText;
  final List<InputArtefact> artefacts;
  final List<PlanNode> nodes;
  final List<PlanEdge> edges;
  final PlanStatus status;
  final DateTime createdAt;
  final DateTime updatedAt;

  const Plan({
    required this.id,
    required this.ownerId,
    required this.title,
    required this.audience,
    required this.inputMode,
    this.rawText,
    this.artefacts = const [],
    this.nodes = const [],
    this.edges = const [],
    this.status = PlanStatus.draft,
    required this.createdAt,
    required this.updatedAt,
  });

  Plan copyWith({
    String? title,
    List<PlanNode>? nodes,
    List<PlanEdge>? edges,
    PlanStatus? status,
    DateTime? updatedAt,
  }) =>
      Plan(
        id: id,
        ownerId: ownerId,
        title: title ?? this.title,
        audience: audience,
        inputMode: inputMode,
        rawText: rawText,
        artefacts: artefacts,
        nodes: nodes ?? this.nodes,
        edges: edges ?? this.edges,
        status: status ?? this.status,
        createdAt: createdAt,
        updatedAt: updatedAt ?? DateTime.now(),
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'ownerId': ownerId,
        'title': title,
        'audience': audience.name,
        'inputMode': inputMode.name,
        'rawText': rawText,
        'artefacts': artefacts.map((a) => a.toJson()).toList(),
        'nodes': nodes.map((n) => n.toJson()).toList(),
        'edges': edges.map((e) => e.toJson()).toList(),
        'status': status.name,
        'createdAt': createdAt.toIso8601String(),
        'updatedAt': updatedAt.toIso8601String(),
      };

  factory Plan.fromJson(Map<String, dynamic> j) => Plan(
        id: j['id'] as String,
        ownerId: j['ownerId'] as String,
        title: j['title'] as String,
        audience: Audience.values
            .firstWhere((a) => a.name == j['audience'], orElse: () => Audience.individual),
        inputMode: InputMode.values
            .firstWhere((m) => m.name == j['inputMode'], orElse: () => InputMode.text),
        rawText: j['rawText'] as String?,
        artefacts: ((j['artefacts'] as List?) ?? [])
            .map((a) => InputArtefact.fromJson(a as Map<String, dynamic>))
            .toList(),
        nodes: ((j['nodes'] as List?) ?? [])
            .map((n) => PlanNode.fromJson(n as Map<String, dynamic>))
            .toList(),
        edges: ((j['edges'] as List?) ?? [])
            .map((e) => PlanEdge.fromJson(e as Map<String, dynamic>))
            .toList(),
        status: PlanStatus.values
            .firstWhere((s) => s.name == j['status'], orElse: () => PlanStatus.draft),
        createdAt: DateTime.parse(j['createdAt'] as String),
        updatedAt: DateTime.parse(j['updatedAt'] as String),
      );
}
