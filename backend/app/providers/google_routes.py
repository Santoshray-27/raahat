import httpx, uuid
from app.core.config import settings
from app.core.logging import logger
from app.core.circuit_breaker import google_circuit_breaker
from app.providers.base import BaseRoutingProvider
from app.schemas.common import GeoPoint
from app.schemas.enums import RouteSafetyTier
from app.schemas.routes import RoutePlanResponseData, RouteSegment, RouteWaypoint

class GoogleRoutesProvider(BaseRoutingProvider):
    async def plan_route(
        self,
        origin: GeoPoint,
        destination: GeoPoint,
        avoid_highways: bool = False,
        avoid_tolls: bool = False
    ) -> RoutePlanResponseData:
        if not settings.GOOGLE_ROUTES_API_KEY:
            raise ValueError("GOOGLE_ROUTES_API_KEY is not configured")
            
        exhausted, until_time = google_circuit_breaker.is_exhausted()
        if exhausted:
            logger.warning(f"GoogleRoutesProvider: Skipping call due to active circuit breaker (exhausted until {until_time}).")
            raise RuntimeError(f"Google Routes quota exhausted (skipping until {until_time})")
            
        url = "https://routes.googleapis.com/directions/v2:computeRoutes"
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": settings.GOOGLE_ROUTES_API_KEY,
            "X-Goog-FieldMask": "routes.duration,routes.distanceMeters,routes.polyline.encodedPolyline"
        }
        
        payload = {
            "origin": {"location": {"latLng": {"latitude": origin.latitude, "longitude": origin.longitude}}},
            "destination": {"location": {"latLng": {"latitude": destination.latitude, "longitude": destination.longitude}}},
            "travelMode": "DRIVE",
            "routeModifiers": {
                "avoidTolls": avoid_tolls,
                "avoidHighways": avoid_highways
            }
        }
        
        async with httpx.AsyncClient(timeout=6.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            if resp.status_code == 429:
                google_circuit_breaker.record_429("google_routes")
                logger.warning(f"Google Routes API error status 429: {resp.text}")
                raise RuntimeError("Google Routes API quota limit 429 exceeded")
            elif resp.status_code != 200:
                logger.warning(f"Google Routes API error status {resp.status_code}: {resp.text}")
                raise RuntimeError(f"Google Routes API request failed with status {resp.status_code}")
                
            google_circuit_breaker.record_success("google_routes")
            data = resp.json()
            routes = data.get("routes", [])
            if not routes:
                raise RuntimeError("No route found from Google Routes API")
                
            r = routes[0]
            dist_km = round(r.get("distanceMeters", 10000) / 1000.0, 2)
            duration_sec = int(r.get("duration", "600s").replace("s", ""))
            
            return RoutePlanResponseData(
                route_id=f"groute_{str(uuid.uuid4())[:8]}",
                origin=origin,
                destination=destination,
                total_distance_km=dist_km,
                total_duration_minutes=round(duration_sec / 60.0, 1),
                safety_tier=RouteSafetyTier.RECOMMENDED_SAFE,
                polyline_encoded=r.get("polyline", {}).get("encodedPolyline"),
                waypoints=[
                    RouteWaypoint(latitude=origin.latitude, longitude=origin.longitude, name="Origin"),
                    RouteWaypoint(latitude=destination.latitude, longitude=destination.longitude, name="Destination")
                ],
                segments=[
                    RouteSegment(
                        summary="Google Navigation Optimized Emergency Route",
                        distance_km=dist_km,
                        duration_minutes=round(duration_sec / 60.0, 1),
                        safety_tier=RouteSafetyTier.RECOMMENDED_SAFE
                    )
                ],
                provider_source="google_routes"
            )
