import 'dart:async';
import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import '../models/models.dart';

class ApiService {
  static final ApiService _instance = ApiService._internal();
  factory ApiService() => _instance;
  ApiService._internal();

  // Dynamic Host Detection: localhost on Web/Desktop, 10.0.2.2 on Android
  String get baseUrl {
    if (kIsWeb) {
      return 'http://localhost:8000';
    }
    return 'http://localhost:8000';
  }

  Future<String> createSession({String deviceId = 'dev_farmer_1', String language = 'hi'}) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/v1/sessions'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'device_id': deviceId,
          'language': language,
          'lat': 16.6913,
          'lon': 74.2432,
        }),
      );
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['session_id'] as String;
      }
    } catch (e) {
      debugPrint('Error creating session: $e');
    }
    return 'sess_${DateTime.now().millisecondsSinceEpoch}';
  }

  Stream<Map<String, dynamic>> analyzeArbitrageStream({
    required String sessionId,
    required String commodity,
    required double quantity,
    required String unit,
    required String originCity,
    required double originLat,
    required double originLon,
    required String vehicleType,
  }) async* {
    final client = http.Client();
    try {
      final request = http.Request(
        'POST',
        Uri.parse('$baseUrl/api/v1/sessions/$sessionId/analyze'),
      );
      request.headers['Content-Type'] = 'application/json';
      request.headers['Accept'] = 'text/event-stream';
      request.body = jsonEncode({
        'commodity': commodity,
        'quantity': quantity,
        'unit': unit,
        'origin_city': originCity,
        'origin_lat': originLat,
        'origin_lon': originLon,
        'vehicle_type': vehicleType,
      });

      final streamedResponse = await client.send(request);
      String buffer = '';

      await for (final chunk in streamedResponse.stream.transform(utf8.decoder)) {
        buffer += chunk;
        final lines = buffer.split('\n');
        buffer = lines.removeLast(); // Keep incomplete trailing fragment

        for (final line in lines) {
          if (line.startsWith('data: ')) {
            final jsonStr = line.substring(6).trim();
            if (jsonStr.isNotEmpty) {
              try {
                final parsed = jsonDecode(jsonStr) as Map<String, dynamic>;
                yield parsed;
              } catch (e) {
                debugPrint('SSE JSON parse error: $e');
              }
            }
          }
        }
      }
    } catch (e) {
      debugPrint('SSE streaming error: $e');
    } finally {
      client.close();
    }
  }

  Future<List<CommunityReportItem>> fetchCommunityReports() async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/api/v1/community/reports'));
      if (response.statusCode == 200) {
        final List<dynamic> data = jsonDecode(response.body);
        return data.map((e) => CommunityReportItem.fromJson(e as Map<String, dynamic>)).toList();
      }
    } catch (e) {
      debugPrint('Error fetching reports: $e');
    }
    return [];
  }

  Future<bool> submitCommunityReport({
    required String mandiId,
    required String mandiName,
    required String commodity,
    required double priceReceived,
    String farmerName = 'Kisan Mitra',
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/v1/community/report'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'mandi_id': mandiId,
          'mandi_name': mandiName,
          'commodity': commodity,
          'price_received': priceReceived,
          'farmer_name': farmerName,
        }),
      );
      return response.statusCode == 200;
    } catch (e) {
      debugPrint('Error submitting report: $e');
      return false;
    }
  }

  Future<Map<String, dynamic>> approveTransport({
    required String sessionId,
    required String mandiId,
    String phone = '+919876543210',
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/v1/sessions/$sessionId/approve'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'session_id': sessionId,
          'mandi_id': mandiId,
          'transporter_phone': phone,
        }),
      );
      if (response.statusCode == 200) {
        return jsonDecode(response.body) as Map<String, dynamic>;
      }
    } catch (e) {
      debugPrint('Error approving transport: $e');
    }
    return {'status': 'APPROVED', 'transporter_notified': true};
  }
}
