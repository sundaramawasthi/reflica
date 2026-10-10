// HTTP client for reflica_service (API v1). All graph reasoning happens in the
// service; this class only sends requests and parses responses.
//
// Base URL: --dart-define=REFLICA_API=http://127.0.0.1:8765 (the default).

import 'dart:async';
import 'dart:convert';

import 'package:http/http.dart' as http;

import '../graph/graph1.dart';

/// A failure with a stable code. Service errors carry the service's code;
/// connection problems use `service_unreachable`, bad replies `bad_response`.
class ReflicaApiException implements Exception {
  final String code;
  final String message;
  final int? status;
  final Map<String, dynamic> detail;
  const ReflicaApiException(this.code, this.message, {this.status, this.detail = const {}});

  @override
  String toString() => 'ReflicaApiException($code): $message';
}

class ServiceHealth {
  final String serviceVersion;
  final String graphVersion;
  final String? llm; // "provider/model", or null when extraction is not configured
  const ServiceHealth(this.serviceVersion, this.graphVersion, this.llm);

  bool get scripted => llm?.startsWith('scripted/') ?? false;
}

class ReflicaApi {
  static const defaultBaseUrl =
      String.fromEnvironment('REFLICA_API', defaultValue: 'http://127.0.0.1:8765');

  final Uri base;
  final http.Client _client;
  final Duration timeout;

  ReflicaApi({String baseUrl = defaultBaseUrl, http.Client? client,
      this.timeout = const Duration(seconds: 120)})
      : base = Uri.parse(baseUrl),
        _client = client ?? http.Client();

  static ReflicaApi instance = ReflicaApi();

  Future<Map<String, dynamic>> _send(String method, String path, [Object? body]) async {
    final uri = base.resolve(path);
    http.Response r;
    try {
      final f = method == 'GET'
          ? _client.get(uri)
          : _client.post(uri,
              headers: {'Content-Type': 'application/json'}, body: jsonEncode(body));
      r = await f.timeout(timeout);
    } on TimeoutException {
      throw const ReflicaApiException(
          'service_unreachable', 'The Reflica service did not answer in time.');
    } catch (e) {
      throw ReflicaApiException('service_unreachable',
          'Could not reach the Reflica service at ${base.origin}. Is it running?');
    }
    Object? decoded;
    try {
      decoded = jsonDecode(utf8.decode(r.bodyBytes));
    } on FormatException {
      throw ReflicaApiException('bad_response', 'The service sent a reply that is not JSON.',
          status: r.statusCode);
    }
    if (decoded is! Map<String, dynamic>) {
      throw ReflicaApiException('bad_response', 'Unexpected reply from the service.',
          status: r.statusCode);
    }
    if (r.statusCode >= 400) {
      final err = decoded['error'];
      if (err is Map<String, dynamic>) {
        throw ReflicaApiException(err['code'] as String? ?? 'error',
            err['message'] as String? ?? 'The service reported an error.',
            status: r.statusCode,
            detail: (err['detail'] as Map<String, dynamic>?) ?? const {});
      }
      throw ReflicaApiException('http_${r.statusCode}', 'The service reported an error.',
          status: r.statusCode);
    }
    return decoded;
  }

  Future<ServiceHealth> health() async {
    final j = await _send('GET', '/v1/health');
    return ServiceHealth(j['service_version'] as String, j['graph_version'] as String,
        j['llm'] as String?);
  }

  Future<ExtractionProposalView> extract(String text, {String title = 'Research problem'}) async =>
      ExtractionProposalView.fromJson(
          await _send('POST', '/v1/extract', {'text': text, 'title': title}));

  Future<GraphUpdate> accept(ExtractionProposalView proposal,
      {required String decidedBy,
      List<String> removeNodes = const [],
      List<String> removeEdges = const [],
      List<String> confirmEdges = const []}) async {
    final j = await _send('POST', '/v1/extract/accept', {
      'proposal': proposal.raw,
      'review': {
        'proposal_sha256': proposal.sha256,
        'decided_by': decidedBy,
        'remove_nodes': removeNodes,
        'remove_edges': removeEdges,
        'confirm_edges': confirmEdges,
      },
    });
    return GraphUpdate(GraphDoc.fromJson(j['graph'] as Map<String, dynamic>),
        j['record'] as Map<String, dynamic>);
  }

  /// [change] is a graph@1 Change, e.g. {'op': 'delete_node', 'node_id': 'n3'}.
  Future<ImpactPreviewView> preview(GraphDoc graph, Map<String, dynamic> change) async =>
      ImpactPreviewView.fromJson(
          await _send('POST', '/v1/impact/preview', {'graph': graph.raw, 'change': change}));

  Future<GraphUpdate> decide(GraphDoc graph, ImpactPreviewView preview,
      {required bool approve, required String decidedBy, String? note}) async {
    final j = await _send('POST', '/v1/impact/decide', {
      'graph': graph.raw,
      'preview': preview.raw,
      'decision': {
        'preview_sha256': preview.sha256,
        'decision': approve ? 'approve' : 'reject',
        'decided_by': decidedBy,
        'note': note,
      },
    });
    return GraphUpdate(GraphDoc.fromJson(j['graph'] as Map<String, dynamic>),
        j['record'] as Map<String, dynamic>);
  }
}
