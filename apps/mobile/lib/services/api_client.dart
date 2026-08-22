// ignore_for_file: depend_on_referenced_packages

import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'dart:math';
import 'package:http/http.dart' as http;
import 'package:firebase_auth/firebase_auth.dart';

/// Custom exception thrown by [ApiClient] for API and network failures.
class ApiException implements Exception {
  final String code;
  final String message;
  final int? statusCode;

  ApiException({
    required this.code,
    required this.message,
    this.statusCode,
  });

  @override
  String toString() =>
      'ApiException(code: $code, message: $message, statusCode: $statusCode)';
}

/// Central API client abstraction responsible for HTTP operations in RAAHAT.
class ApiClient {
  static final ApiClient instance = ApiClient._internal();

  /// Base URL for the RAAHAT backend API (defaults to Android emulator routing).
  String baseUrl;

  /// Optional underlying HTTP client instance.
  final http.Client _client;

  ApiClient._internal({
    http.Client? client,
  }) : baseUrl = 'http://10.0.2.2:8000/api/v1',
       _client = client ?? http.Client();

  factory ApiClient() {
    return instance;
  }

  /// Sends a GET request to the specified [path] with optional [queryParams].
  Future<Map<String, dynamic>> get(
    String path, {
    Map<String, String>? queryParams,
  }) async {
    Uri uri = Uri.parse(_buildUrl(path));
    if (queryParams != null && queryParams.isNotEmpty) {
      uri = uri.replace(queryParameters: queryParams);
    }

    final headers = await _buildHeaders();
    return _sendRequest(() => _client.get(uri, headers: headers));
  }

  /// Sends a POST request to the specified [path] with the given [body].
  Future<Map<String, dynamic>> post(
    String path,
    Map<String, dynamic> body,
  ) async {
    final uri = Uri.parse(_buildUrl(path));
    final encodedBody = jsonEncode(body);
    final headers = await _buildHeaders();

    return _sendRequest(
      () => _client.post(
        uri,
        headers: headers,
        body: encodedBody,
      ),
    );
  }

  /// Builds a complete URL string by joining [baseUrl] and [path].
  String _buildUrl(String path) {
    final cleanBase =
        baseUrl.endsWith('/') ? baseUrl.substring(0, baseUrl.length - 1) : baseUrl;
    final cleanPath = path.startsWith('/') ? path : '/$path';
    return '$cleanBase$cleanPath';
  }

  /// Generates mandatory default headers for every API request.
  Future<Map<String, String>> _buildHeaders() async {
    final Map<String, String> headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      'X-Request-ID': _generateRequestId(),
    };

    final user = FirebaseAuth.instance.currentUser;
    if (user != null) {
      try {
        final token = await user.getIdToken();
        if (token != null && token.isNotEmpty) {
          headers['Authorization'] = 'Bearer $token';
        }
      } catch (e) {
        // Ignore token fetch errors here to let the request fail normally 
        // or proceed unauthenticated depending on backend endpoint.
      }
    }

    return headers;
  }

  /// Generates a unique request ID string for debugging and tracing.
  String _generateRequestId() {
    final timestamp = DateTime.now().microsecondsSinceEpoch;
    final randomHex = Random().nextInt(0xFFFFFFFF).toRadixString(16).padLeft(8, '0');
    return 'req-$timestamp-$randomHex';
  }

  /// Sends request with strict 15-second timeout and exception encapsulation.
  Future<Map<String, dynamic>> _sendRequest(
    Future<http.Response> Function() requestAction,
  ) async {
    try {
      final response = await requestAction().timeout(
        const Duration(seconds: 15),
      );

      return _processResponse(response);
    } on TimeoutException {
      throw ApiException(
        code: 'TIMEOUT_ERROR',
        message: 'Request timed out after 15 seconds.',
      );
    } on SocketException catch (e) {
      throw ApiException(
        code: 'NETWORK_ERROR',
        message: 'Network unreachable or connection refused: ${e.message}',
      );
    } on http.ClientException catch (e) {
      throw ApiException(
        code: 'CLIENT_ERROR',
        message: e.message,
      );
    } catch (e) {
      if (e is ApiException) rethrow;
      throw ApiException(
        code: 'UNKNOWN_ERROR',
        message: 'An unexpected error occurred: ${e.toString()}',
      );
    }
  }

  /// Parses server response or throws [ApiException] on non-200 HTTP status.
  Map<String, dynamic> _processResponse(http.Response response) {
    Map<String, dynamic> decodedBody = {};

    if (response.body.isNotEmpty) {
      try {
        final parsed = jsonDecode(response.body);
        if (parsed is Map<String, dynamic>) {
          decodedBody = parsed;
        } else {
          decodedBody = {'data': parsed};
        }
      } catch (_) {
        decodedBody = {'raw': response.body};
      }
    }

    if (response.statusCode >= 200 && response.statusCode < 300) {
      return decodedBody;
    }

    String errorCode = 'HTTP_${response.statusCode}';
    String errorMessage =
        'Server returned HTTP status ${response.statusCode}';

    if (decodedBody.containsKey('error') && decodedBody['error'] is Map) {
      final errorMap = decodedBody['error'] as Map;
      if (errorMap.containsKey('code') && errorMap['code'] != null) {
        errorCode = errorMap['code'].toString();
      }
      if (errorMap.containsKey('message') && errorMap['message'] != null) {
        errorMessage = errorMap['message'].toString();
      }
    } else if (decodedBody.containsKey('message')) {
      errorMessage = decodedBody['message'].toString();
    } else if (decodedBody.containsKey('detail')) {
      errorMessage = decodedBody['detail'].toString();
    }

    throw ApiException(
      code: errorCode,
      message: errorMessage,
      statusCode: response.statusCode,
    );
  }
}
