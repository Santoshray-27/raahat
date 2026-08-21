import 'package:raahat/core/location/location_service.dart';
import 'package:raahat/services/api_client.dart';

/// Exception thrown by [ServicesService] for application-level service query failures.
class ServicesServiceException implements Exception {
  final String message;

  ServicesServiceException(this.message);

  @override
  String toString() => 'ServicesServiceException: $message';
}

/// Production service responsible for fetching nearby emergency services from backend API.
class ServicesService {
  final ApiClient apiClient;
  final LocationService locationService;

  ServicesService({
    required this.apiClient,
    required this.locationService,
  });

  /// Fetches a list of nearby emergency services matching [serviceCategoryFilter].
  ///
  /// Obtains current device GPS coordinates via [locationService] and queries
  /// the `/services/nearby` endpoint via [apiClient].
  ///
  /// Returns a [List] of parsed service maps. Returns an empty list if no services are found.
  /// Throws [ServicesServiceException] if location is unavailable or if response payload is malformed.
  /// Throws [ApiException] if network or API error occurs.
  Future<List<Map<String, dynamic>>> fetchNearbyServices(
    String serviceCategoryFilter,
  ) async {
    final Map<String, dynamic>? locationMap =
        await locationService.getCurrentLocation();

    if (locationMap == null) {
      throw ServicesServiceException(
        'Unable to obtain current device location. Please ensure location services and permissions are enabled.',
      );
    }

    final String latitudeStr = locationMap['latitude'].toString();
    final String longitudeStr = locationMap['longitude'].toString();

    final Map<String, String> queryParams = {
      'lat': latitudeStr,
      'lng': longitudeStr,
      'category': serviceCategoryFilter,
      'radius_km': '5.0',
      'limit': '10',
    };

    final Map<String, dynamic> response = await apiClient.get(
      '/services/nearby',
      queryParams: queryParams,
    );

    if (!response.containsKey('data') || response['data'] == null) {
      throw ServicesServiceException(
        'Malformed API response: Missing expected "data" field.',
      );
    }

    final rawData = response['data'];
    List<dynamic> servicesList;

    if (rawData is List) {
      servicesList = rawData;
    } else if (rawData is Map &&
        rawData.containsKey('services') &&
        rawData['services'] is List) {
      servicesList = rawData['services'] as List<dynamic>;
    } else {
      throw ServicesServiceException(
        'Malformed API response: Expected "data" field to contain a list of service entries.',
      );
    }

    final List<Map<String, dynamic>> result = [];
    for (final item in servicesList) {
      if (item is Map) {
        result.add(Map<String, dynamic>.from(item));
      }
    }

    return result;
  }
}
