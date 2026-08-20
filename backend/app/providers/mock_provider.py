import uuid
from typing import List
from app.providers.base import BasePlacesProvider, BaseRoutingProvider
from app.schemas.common import GeoPoint, ServiceProvider, LocationAddress, ContactInfo
from app.schemas.enums import ServiceType, RouteSafetyTier
from app.schemas.routes import RoutePlanResponseData, RouteSegment, RouteWaypoint

class MockPlacesProvider(BasePlacesProvider):
    async def search_nearby(
        self,
        location: GeoPoint,
        service_types: List[ServiceType],
        radius_km: float = 10.0,
        limit: int = 10
    ) -> List[ServiceProvider]:
        providers: List[ServiceProvider] = []
        
        # Generator relative to user location
        lat, lon = location.latitude, location.longitude
        
        mock_templates = [
            {
                "name": "Indore Express Puncture & Mobile Repair",
                "types": ["PUNCTURE_REPAIR", "MECHANIC"],
                "lat_offset": 0.012, "lon_offset": 0.008,
                "phone": "+91 98260 11223", "rating": 4.7
            },
            {
                "name": "Apollo Emergency Trauma & Hospital",
                "types": ["HOSPITAL", "AMBULANCE"],
                "lat_offset": -0.018, "lon_offset": 0.015,
                "phone": "+91 731 4455667", "rating": 4.9
            },
            {
                "name": "National Highway Towing & Crane Service",
                "types": ["TOWING", "CRANE"],
                "lat_offset": 0.025, "lon_offset": -0.021,
                "phone": "+91 94250 88990", "rating": 4.6
            },
            {
                "name": "24/7 Highway Fuel Delivery & Assistance",
                "types": ["FUEL_DELIVERY", "MECHANIC"],
                "lat_offset": -0.009, "lon_offset": -0.011,
                "phone": "+91 91110 44332", "rating": 4.4
            }
        ]
        
        for idx, tmpl in enumerate(mock_templates[:limit]):
            p_lat = lat + tmpl["lat_offset"]
            p_lon = lon + tmpl["lon_offset"]
            
            providers.append(
                ServiceProvider(
                    provider_id=f"prov_mock_{idx+1}_{str(uuid.uuid4())[:6]}",
                    name=tmpl["name"],
                    service_types=tmpl["types"],
                    location=GeoPoint(latitude=p_lat, longitude=p_lon),
                    address=LocationAddress(
                        formatted_address=f"Near Highway Kilometer 14{idx}, Indore",
                        city="Indore", state="Madhya Pradesh", country="India"
                    ),
                    contact=ContactInfo(phone_primary=tmpl["phone"], is_phone_verified=True),
                    distance_km=round(abs(tmpl["lat_offset"] * 111), 2),
                    eta_minutes=max(4, int(abs(tmpl["lat_offset"] * 111) * 3)),
                    rating=tmpl["rating"],
                    review_count=35 + (idx * 12),
                    availability_status="UNKNOWN",  # NON-NEGOTIABLE RULE: UNKNOWN unless verified
                    verification_status="VERIFIED",
                    recommendation_score=0.92,
                    recommendation_reason="Mock local verified roadside vendor",
                    is_cached=False
                )
            )
            
        return providers

class MockRoutingProvider(BaseRoutingProvider):
    async def plan_route(
        self,
        origin: GeoPoint,
        destination: GeoPoint,
        avoid_highways: bool = False,
        avoid_tolls: bool = False
    ) -> RoutePlanResponseData:
        return RoutePlanResponseData(
            route_id=f"route_mock_{str(uuid.uuid4())[:8]}",
            origin=origin,
            destination=destination,
            total_distance_km=14.5,
            total_duration_minutes=22.0,
            safety_tier=RouteSafetyTier.RECOMMENDED_SAFE,
            waypoints=[
                RouteWaypoint(latitude=origin.latitude, longitude=origin.longitude, name="Start Position"),
                RouteWaypoint(
                    latitude=(origin.latitude + destination.latitude) / 2,
                    longitude=(origin.longitude + destination.longitude) / 2,
                    name="Safe Highway Bypass"
                ),
                RouteWaypoint(latitude=destination.latitude, longitude=destination.longitude, name="Destination")
            ],
            segments=[
                RouteSegment(
                    summary="Main Bypass Highway",
                    distance_km=14.5,
                    duration_minutes=22.0,
                    safety_tier=RouteSafetyTier.RECOMMENDED_SAFE,
                    hazard_warnings=[]
                )
            ],
            provider_source="mock"
        )
