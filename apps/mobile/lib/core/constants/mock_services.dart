// lib/core/constants/mock_services.dart

final List<Map<String, dynamic>> mockServicesData = [
  {
    "provider_id": "google_place_abc",
    "name": "SAGE Emergency Hospital",
    "service_types": ["HOSPITAL"],
    "location": {
      "latitude": 22.7196,
      "longitude": 75.8577,
      "accuracy_meters": null,
      "timestamp": "2026-08-20T12:30:45Z"
    },
    "address": {"formatted_address": "SAGE University Campus, Indore"},
    "contact": {"phone_primary": "+91 99999 88888"},
    "distance_km": 1.2,
    "eta_minutes": 6,
    "rating": 4.8,
    "availability_status": "OPEN",
    "source": "GOOGLE_PLACES",
    "retrieved_at": "2026-08-20T12:30:45Z",
    "is_cached": false
  },
  {
    "provider_id": "google_place_xyz",
    "name": "Highway Quick Mechanic & Towing",
    "service_types": ["MECHANIC"],
    "location": {
      "latitude": 22.7300,
      "longitude": 75.8600,
      "accuracy_meters": null,
      "timestamp": "2026-08-20T12:31:00Z"
    },
    "address": {"formatted_address": "Bypass Highway Road, Indore"},
    "contact": {"phone_primary": "+91 88888 77777"},
    "distance_km": 2.4,
    "eta_minutes": 10,
    "rating": 4.2,
    "availability_status": "UNKNOWN",
    "source": "GOOGLE_PLACES",
    "retrieved_at": "2026-08-20T12:30:45Z",
    "is_cached": false
  }
];
