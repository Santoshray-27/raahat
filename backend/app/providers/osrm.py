import httpx, uuid
from app.core.logging import logger
from app.providers.base import BaseRoutingProvider
from app.schemas.common import GeoPoint
from app.schemas.enums import RouteSafetyTier
from app.schemas.routes import RoutePlanResponseData, RouteSegment, RouteWaypoint

class OSRMRoutingProvider(BaseRoutingProvider):
    async def plan_route(
        self,
        origin: GeoPoint,
        destination: GeoPoint,
        avoid_highways: bool = False,
        avoid_tolls: bool = False
    ) -> RoutePlanResponseData:
        url = f"http://router.project-osrm.org/route/v1/driving/{origin.longitude},{origin.latitude};{destination.longitude},{destination.latitude}?overview=simplified&geometries=polyline"
        
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(url)
                if resp.status_code != 200:
                    raise RuntimeError(f"OSRM router returned status {resp.status_code}")
                    
                data = resp.json()
                routes = data.get("routes", [])
                if not routes:
                    raise RuntimeError("No route found from OSRM router")
                    
                r = routes[0]
                dist_km = round(r.get("distance", 10000) / 1000.0, 2)
                duration_min = round(r.get("duration", 600) / 60.0, 1)
                
                return RoutePlanResponseData(
                    route_id=f"osrm_{str(uuid.uuid4())[:8]}",
                    origin=origin,
                    destination=destination,
                    total_distance_km=dist_km,
                    total_duration_minutes=duration_min,
                    safety_tier=RouteSafetyTier.RECOMMENDED_SAFE,
                    polyline_encoded=r.get("geometry"),
                    waypoints=[
                        RouteWaypoint(latitude=origin.latitude, longitude=origin.longitude, name="Origin"),
                        RouteWaypoint(latitude=destination.latitude, longitude=destination.longitude, name="Destination")
                    ],
                    segments=[
                        RouteSegment(
                            summary="OSRM Open Driving Corridor",
                            distance_km=dist_km,
                            duration_minutes=duration_min,
                            safety_tier=RouteSafetyTier.RECOMMENDED_SAFE
                        )
                    ],
                    provider_source="osrm"
                )
        except Exception as e:
            logger.warning(f"OSRM Routing Fallback error: {e}")
            raise RuntimeError(f"OSRM route planning failed: {e}")
