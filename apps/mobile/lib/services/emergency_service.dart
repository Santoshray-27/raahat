import 'package:raahat/core/constants/enums.dart';
import 'package:raahat/core/location/location_service.dart';
import 'package:raahat/services/api_client.dart';

/// Exception thrown by [EmergencyService] for application-level emergency processing failures.
class EmergencyServiceException implements Exception {
  final String message;

  EmergencyServiceException(this.message);

  @override
  String toString() => 'EmergencyServiceException: $message';
}

/// Production Emergency Assistance API Service for submitting emergency reports.
class EmergencyService {
  final ApiClient apiClient;
  final LocationService locationService;

  EmergencyService({
    required this.apiClient,
    required this.locationService,
  });

  /// Submits an emergency message to the RAAHAT backend API.
  ///
  /// Obtains current GPS coordinates via [LocationService] and sends a structured
  /// request payload to `/emergency-assistance` via [ApiClient].
  ///
  /// Returns the parsed `data` map payload upon success.
  ///
  /// Throws [EmergencyServiceException] if input validation fails, location is unavailable,
  /// or if response payload is missing the expected `data` field.
  /// Throws [ApiException] if backend returns an API error or network failure occurs.
  Future<Map<String, dynamic>> submitEmergency(
    String userMessage,
    NetworkMode mode,
  ) async {
    final trimmedMessage = userMessage.trim();
    if (trimmedMessage.isEmpty) {
      throw EmergencyServiceException(
        'Emergency message cannot be empty or contain only whitespace.',
      );
    }

    final Map<String, dynamic>? locationMap =
        await locationService.getCurrentLocation();

    if (locationMap == null) {
      throw EmergencyServiceException(
        'Unable to obtain current device location. Please ensure location services and permissions are enabled.',
      );
    }

    final Map<String, dynamic> requestBody = {
      'message': trimmedMessage,
      'language': 'en',
      'location': {
        'latitude': locationMap['latitude'],
        'longitude': locationMap['longitude'],
        'accuracy_meters': locationMap['accuracy_meters'],
        'timestamp': locationMap['timestamp'],
      },
      'network_mode': mode == NetworkMode.ONLINE ? 'ONLINE' : 'OFFLINE',
      'include_services': true,
    };

    final Map<String, dynamic> response = await apiClient.post(
      '/emergency-assistance',
      requestBody,
    );

    if (!response.containsKey('data') || response['data'] == null) {
      throw EmergencyServiceException(
        'Malformed API response: Missing expected "data" field.',
      );
    }

    final dataPayload = response['data'];
    if (dataPayload is! Map<String, dynamic>) {
      throw EmergencyServiceException(
        'Malformed API response: Expected "data" field to be a JSON object.',
      );
    }

    return dataPayload;
  }
}
