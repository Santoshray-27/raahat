from typing import Optional, List
from pydantic import BaseModel
from app.schemas.common import GeoPoint, ServiceProvider
from app.schemas.enums import RouteSafetyTier

class RouteWaypoint(BaseModel):
    latitude: float
    longitude: float
    name: Optional[str] = None

class RoutePlanRequest(BaseModel):
    origin: GeoPoint
    destination: GeoPoint
    avoid_highways: bool = False
    avoid_tolls: bool = False
    prefer_safe_corridors: bool = True

class RouteSegment(BaseModel):
    summary: str
    distance_km: float
    duration_minutes: float
    safety_tier: RouteSafetyTier = RouteSafetyTier.RECOMMENDED_SAFE
    hazard_warnings: List[str] = []

class RoutePlanResponseData(BaseModel):
    route_id: str
    origin: GeoPoint
    destination: GeoPoint
    total_distance_km: float
    total_duration_minutes: float
    safety_tier: RouteSafetyTier = RouteSafetyTier.RECOMMENDED_SAFE
    polyline_encoded: Optional[str] = None
    waypoints: List[RouteWaypoint] = []
    segments: List[RouteSegment] = []
    nearby_emergency_services: List[ServiceProvider] = []
    provider_source: str = "mock"  # google_routes | osrm | mock
