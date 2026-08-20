// ignore_for_file: constant_identifier_names

enum IncidentType {
  ACCIDENT,
  TYRE_PUNCTURE,
  VEHICLE_BREAKDOWN,
  VEHICLE_FIRE,
  MEDICAL_EMERGENCY,
  STRANDED,
  FUEL_EMERGENCY,
  OTHER,
}

enum ServiceCategory {
  HOSPITAL,
  POLICE,
  AMBULANCE,
  FIRE_STATION,
  TOWING,
  PUNCTURE_REPAIR,
  MECHANIC,
  VEHICLE_SERVICE,
  FUEL_STATION,
  OTHER,
}

enum Severity {
  LOW,
  MEDIUM,
  HIGH,
  CRITICAL,
  UNKNOWN,
}

enum NetworkMode {
  ONLINE,
  LIMITED,
  OFFLINE,
}

enum AIResponseMode {
  ONLINE,
  OFFLINE,
  FALLBACK,
}
