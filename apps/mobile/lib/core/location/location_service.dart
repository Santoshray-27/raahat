import 'package:flutter/foundation.dart';
import 'package:geolocator/geolocator.dart';

/// LocationService is the single abstraction responsible for obtaining
/// the device's current GPS coordinates.
class LocationService {
  /// Obtains the current GPS position of the device if location services
  /// are enabled and permissions are granted.
  ///
  /// Returns a JSON-compatible [Map] with location details, or `null` if
  /// location services are disabled or permission is not granted.
  Future<Map<String, dynamic>?> getCurrentLocation() async {
    debugPrint('Checking location services');
    final bool serviceEnabled = await Geolocator.isLocationServiceEnabled();
    if (!serviceEnabled) {
      debugPrint('Location service disabled');
      return null;
    }

    debugPrint('Checking location permission');
    LocationPermission permission = await Geolocator.checkPermission();

    if (permission == LocationPermission.denied) {
      debugPrint('Requesting location permission');
      permission = await Geolocator.requestPermission();
      if (permission == LocationPermission.denied) {
        debugPrint('Permission denied');
        return null;
      }
    }

    if (permission == LocationPermission.deniedForever) {
      debugPrint('Permission permanently denied');
      return null;
    }

    final Position position = await Geolocator.getCurrentPosition();
    debugPrint('Location successfully obtained');

    return {
      'latitude': position.latitude,
      'longitude': position.longitude,
      'accuracy_meters': position.accuracy,
      'timestamp': DateTime.now().toUtc().toIso8601String(),
    };
  }
}
