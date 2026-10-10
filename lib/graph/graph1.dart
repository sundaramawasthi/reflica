// Dart views of the graph@1 contract served by reflica_service.
//
// The Python service owns the contract (research/reflica_service/graph/
// contract.py and graph@1.schema.json). These classes only READ it: each keeps
// the exact JSON it was parsed from in [raw], and that JSON — never a
// re-serialisation — is what goes back to the service. Previews and proposals
// are fingerprinted server-side, so sending them back unchanged matters.
//
// `kind` says what an item is; `basis` says where it came from. Neither says
// it is true.

/// Where an item came from (graph@1 `basis`).
enum Basis { userStated, sourceQuoted, llmInferred, computed, legacyUnverified }

const _basisNames = {
  'user_stated': Basis.userStated,
  'source_quoted': Basis.sourceQuoted,
  'llm_inferred': Basis.llmInferred,
  'computed': Basis.computed,
  'legacy_unverified': Basis.legacyUnverified,
};

Basis parseBasis(String s) {
  final b = _basisNames[s];
  if (b == null) throw FormatException('unknown basis "$s"');
  return b;
}

/// Plain-language label shown next to every item.
String basisLabel(Basis b) => switch (b) {
      Basis.userStated => 'Stated by you',
      Basis.sourceQuoted => 'Quoted from your text',
      Basis.llmInferred => 'Suggested by AI — not in your text',
      Basis.computed => 'Computed by an analysis',
      Basis.legacyUnverified => 'Imported — origin unknown',
    };

class SourceSpan {
  final String sourceId;
  final int start;
  final int end;
  final String quote;
  const SourceSpan(this.sourceId, this.start, this.end, this.quote);

  factory SourceSpan.fromJson(Map<String, dynamic> j) => SourceSpan(
      j['source_id'] as String, j['start'] as int, j['end'] as int, j['quote'] as String);
}

class ReviewNote {
  final String changeSha256;
  final String reason;
  const ReviewNote(this.changeSha256, this.reason);

  factory ReviewNote.fromJson(Map<String, dynamic> j) =>
      ReviewNote(j['change_sha256'] as String, j['reason'] as String);
}

List<SourceSpan> _spans(Object? v) => [
      for (final s in (v as List? ?? const [])) SourceSpan.fromJson(s as Map<String, dynamic>)
    ];

class GNode {
  final String id;
  final String kind;
  final String label;
  final String? detail;
  final Basis basis;
  final List<SourceSpan> spans;
  final List<ReviewNote> reviews;
  final String? legacyType;

  const GNode({
    required this.id,
    required this.kind,
    required this.label,
    this.detail,
    required this.basis,
    this.spans = const [],
    this.reviews = const [],
    this.legacyType,
  });

  bool get needsReview => reviews.isNotEmpty;

  factory GNode.fromJson(Map<String, dynamic> j) => GNode(
        id: j['id'] as String,
        kind: j['kind'] as String,
        label: j['label'] as String,
        detail: j['detail'] as String?,
        basis: parseBasis(j['basis'] as String),
        spans: _spans(j['spans']),
        reviews: [
          for (final r in (j['reviews'] as List? ?? const []))
            ReviewNote.fromJson(r as Map<String, dynamic>)
        ],
        legacyType: (j['legacy'] as Map<String, dynamic>?)?['type'] as String?,
      );
}

class GEdge {
  final String id;
  final String source;
  final String target;
  final String type;
  final bool confirmed;
  final Basis basis;
  final List<SourceSpan> spans;

  const GEdge({
    required this.id,
    required this.source,
    required this.target,
    required this.type,
    required this.confirmed,
    required this.basis,
    this.spans = const [],
  });

  factory GEdge.fromJson(Map<String, dynamic> j) {
    final certainty = j['certainty'] as String;
    if (certainty != 'confirmed' && certainty != 'inferred') {
      throw FormatException('unknown certainty "$certainty"');
    }
    return GEdge(
      id: j['id'] as String,
      source: j['source'] as String,
      target: j['target'] as String,
      type: j['type'] as String,
      confirmed: certainty == 'confirmed',
      basis: parseBasis(j['basis'] as String),
      spans: _spans(j['spans']),
    );
  }
}

/// How to read a link in words; edges point from influencing to influenced.
String edgeSentence(GEdge e, String Function(String id) label) {
  final s = label(e.source), t = label(e.target);
  return switch (e.type) {
    'requires' => '$t requires $s',
    'derived_from' => '$t is derived from $s',
    _ => '$s ${e.type.replaceAll('_', ' ')} $t',
  };
}

class GraphDoc {
  static const version = 'graph@1';
  final Map<String, dynamic> raw;
  final List<GNode> nodes;
  final List<GEdge> edges;

  GraphDoc._(this.raw, this.nodes, this.edges);

  factory GraphDoc.fromJson(Map<String, dynamic> j) {
    if (j['version'] != version) {
      throw FormatException('expected $version, got ${j['version']}');
    }
    return GraphDoc._(
      j,
      [for (final n in (j['nodes'] as List? ?? const [])) GNode.fromJson(n as Map<String, dynamic>)],
      [for (final e in (j['edges'] as List? ?? const [])) GEdge.fromJson(e as Map<String, dynamic>)],
    );
  }

  /// A graph with no items (used when automatic extraction is unavailable).
  factory GraphDoc.empty() => GraphDoc.fromJson(
      {'version': version, 'sources': <dynamic>[], 'nodes': <dynamic>[], 'edges': <dynamic>[]});

  GNode? node(String id) {
    for (final n in nodes) {
      if (n.id == id) return n;
    }
    return null;
  }

  String labelOf(String id) => node(id)?.label ?? id;
}

class ImpactItem {
  final String nodeId;
  final String relation; // changed | direct | downstream
  final bool confirmed; // false = uncertain (path runs through an inferred link)
  final List<String> path;
  final String explanation;

  const ImpactItem(this.nodeId, this.relation, this.confirmed, this.path, this.explanation);

  factory ImpactItem.fromJson(Map<String, dynamic> j) => ImpactItem(
        j['node_id'] as String,
        j['relation'] as String,
        j['certainty'] == 'confirmed',
        [for (final p in j['path'] as List) p as String],
        j['explanation'] as String,
      );
}

class ProposedUpdate {
  final String action;
  final String target;
  final String description;
  const ProposedUpdate(this.action, this.target, this.description);

  factory ProposedUpdate.fromJson(Map<String, dynamic> j) =>
      ProposedUpdate(j['action'] as String, j['target'] as String, j['description'] as String);
}

class ImpactPreviewView {
  final Map<String, dynamic> raw;
  final String sha256;
  final String analyzer;
  final List<ImpactItem> items;
  final List<String> unaffected;
  final List<String> relatedUnaffected;
  final List<ProposedUpdate> proposedUpdates;
  final List<String> limitations;

  ImpactPreviewView._(this.raw, this.sha256, this.analyzer, this.items, this.unaffected,
      this.relatedUnaffected, this.proposedUpdates, this.limitations);

  factory ImpactPreviewView.fromJson(Map<String, dynamic> j) => ImpactPreviewView._(
        j,
        j['preview_sha256'] as String,
        j['analyzer'] as String,
        [for (final i in j['items'] as List) ImpactItem.fromJson(i as Map<String, dynamic>)],
        [for (final u in j['unaffected'] as List) u as String],
        [for (final u in j['related_unaffected'] as List) u as String],
        [for (final u in j['proposed_updates'] as List)
          ProposedUpdate.fromJson(u as Map<String, dynamic>)],
        [for (final l in j['limitations'] as List) l as String],
      );

  /// Items other than the changed node itself: what would be flagged for review.
  List<ImpactItem> get affected => [for (final i in items) if (i.relation != 'changed') i];
}

class ExtractionIssue {
  final String code;
  final bool warning;
  final String message;
  final String? ref;
  const ExtractionIssue(this.code, this.warning, this.message, this.ref);

  factory ExtractionIssue.fromJson(Map<String, dynamic> j) => ExtractionIssue(
      j['code'] as String, j['severity'] == 'warning', j['message'] as String, j['ref'] as String?);
}

class ExtractionProposalView {
  final Map<String, dynamic> raw;
  final String sha256;
  final String restatement;
  final List<String> clarifyingQuestions;
  final GraphDoc graph;
  final List<ExtractionIssue> issues;
  final String provider;
  final String model;

  ExtractionProposalView._(this.raw, this.sha256, this.restatement, this.clarifyingQuestions,
      this.graph, this.issues, this.provider, this.model);

  factory ExtractionProposalView.fromJson(Map<String, dynamic> j) {
    final m = j['model'] as Map<String, dynamic>;
    return ExtractionProposalView._(
      j,
      j['proposal_sha256'] as String,
      j['restatement'] as String,
      [for (final q in j['clarifying_questions'] as List) q as String],
      GraphDoc.fromJson(j['graph'] as Map<String, dynamic>),
      [for (final i in j['issues'] as List) ExtractionIssue.fromJson(i as Map<String, dynamic>)],
      m['provider'] as String,
      m['model'] as String,
    );
  }

  /// Issues about one item or link (by the model's ref), for display beside it.
  Map<String, String> get nodeIdByRef =>
      {for (final e in (raw['refs'] as Map<String, dynamic>).entries) e.key: e.value as String};
}

/// Result of accept / decide: the new graph plus the record to store as an event.
class GraphUpdate {
  final GraphDoc graph;
  final Map<String, dynamic> record;
  const GraphUpdate(this.graph, this.record);
}
