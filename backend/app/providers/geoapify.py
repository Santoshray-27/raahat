import httpx
from datetime import datetime, timezone
import uuid
from typing import List, Optional
from app.providers.base import BasePlacesProvider, BaseRoutingProvider
from app.core.config import settings
from app.core.logging import logger
from app.schemas.common import GeoPoint, ServiceProvider, LocationAddress, ContactInfo
from app.schemas.enums import ServiceType, ProviderSource
from app.schemas.routes import RoutePlanResponseData, RouteSegment, RouteWaypoint
from app.services.ranking import calculate_haversine_distance

class GeoapifyProviderError(Exception):
    pass

class GeoapifyPlacesProvider(BasePlacesProvider):
    name = "geoapify"

    _CATEGORY_MAP = {
        ServiceType.HOSPITAL: ["healthcare.hospital"],
        ServiceType.AMBULANCE: ["healthcare.ambulance", "healthcare.hospital"],
        ServiceType.POLICE: ["amenity.police"],
        ServiceType.FIRE_BRIGADE: ["amenity.fire_station"],
        ServiceType.PUNCTURE_REPAIR: ["service.vehicle", "commercial.vehicle"],
        ServiceType.MECHANIC: ["service.vehicle.repair", "service.vehicle"],
        ServiceType.TOWING: ["service.vehicle.towing", "service.vehicle"],
        ServiceType.FUEL_DELIVERY: ["service.fuel"],
    }

    async def search_nearby(
        self,
        location: GeoPoint,
        service_types: List[ServiceType],
        radius_km: float = 10.0,
        limit: int = 10
    ) -> List[ServiceProvider]:
        if not settings.GEOAPIFY_API_KEY:
            logger.warning("Geoapify key not configured. Skipping.")
            raise GeoapifyProviderError("Key not configured")

        main_type = service_types[0] if service_types else ServiceType.HOSPITAL
        categories = self._CATEGORY_MAP.get(main_type, ["amenity.other"])

        for category in categories:
            url = "https://api.geoapify.com/v2/places"
            params = {
                "categories": category,
                "filter": f"circle:{location.longitude},{location.latitude},{int(radius_km * 1000)}",
                "limit": limit,
                "apiKey": settings.GEOAPIFY_API_KEY,
                "lang": "en"
            }
            try:
                async with httpx.AsyncClient(timeout=15.0) as client:
                    response = await client.get(url, params=params)
                    if response.status_code in [401, 403, 429]:
                        raise GeoapifyProviderError(f"Geoapify authentication/rate limit error: {response.status_code}")
                    if response.status_code != 200:
                        logger.warning(f"Geoapify category {category} returned {response.status_code}. Trying fallback...")
                        continue

                    data = response.json()
                    features = data.get("features", [])
                    if features:
                        results = []
                        for f in features:
                            props = f.get("properties", {})
                            place_id = props.get("place_id", str(uuid.uuid4()))
                            
                            # Calculate distance
                            dist = props.get("distance")
                            loc = GeoPoint(latitude=props.get("lat", 0), longitude=props.get("lon", 0))
                            if dist is None:
                                dist = calculate_haversine_distance(location, loc) * 1000.0

                            # Parse address
                            address_line = props.get("address_line1", "")
                            if props.get("address_line2"):
                                address_line += ", " + props.get("address_line2")

                            sp = ServiceProvider(
                                provider_id=f"geoapify_{place_id}",
                                name=props.get("name") or props.get("address_line1", "Unknown Service"),
                                service_types=[main_type.value],
                                location=loc,
                                address=LocationAddress(
                                    formatted_address=address_line or None,
                                    city=props.get("city"),
                                    state=props.get("state"),
                                    country=props.get("country", "India"),
                                    postal_code=props.get("postcode")
                                ),
                                contact=ContactInfo(
                                    phone_primary=str(props.get("contact", {}).get("phone")) if props.get("contact", {}).get("phone") else None
                                ),
                                distance_km=dist / 1000.0,
                                eta_minutes=int(dist / 1000.0 * 2), # rough estimate
                                rating=None,
                                review_count=0,
                                availability_status="UNKNOWN",
                                source=ProviderSource.GEOAPIFY,
                                is_cached=False,
                                retrieved_at=datetime.now(timezone.utc).isoformat()
                            )
                            results.append(sp)
                        return sorted(results, key=lambda x: x.distance_km)[:limit]
            except GeoapifyProviderError:
                raise
            except Exception as e:
                logger.error(f"Geoapify request failed: {e}")
                
        raise GeoapifyProviderError("No results found in any categories or request failed completely.")

class GeoapifyRoutingProvider(BaseRoutingProvider):
    name = "geoapify_routing"

    async def plan_route(
        self,
        origin: GeoPoint,
        destination: GeoPoint,
        avoid_highways: bool = False,
        avoid_tolls: bool = False
    ) -> RoutePlanResponseData:
        if not settings.GEOAPIFY_API_KEY:
            raise GeoapifyProviderError("Geoapify key not configured")
            
        url = "https://api.geoapify.com/v1/routing"
        params = {
            "waypoints": f"{origin.latitude},{origin.longitude}|{destination.latitude},{destination.longitude}",
            "mode": "drive",
            "apiKey": settings.GEOAPIFY_API_KEY
        }
            
        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                response = await client.get(url, params=params)
                if response.status_code in [401, 403, 429]:
                    raise GeoapifyProviderError(f"Geoapify error {response.status_code}")
                response.raise_for_status()
                data = response.json()
            except Exception as e:
                raise GeoapifyProviderError(f"Routing request failed: {e}")

        features = data.get("features", [])
        if not features:
            raise GeoapifyProviderError("No route found")

        feature = features[0]
        props = feature.get("properties", {})
        
        dist_m = props.get("distance", 0)
        dur_s = props.get("time", 0)
        
        return RoutePlanResponseData(
            route_id=f"rt_geoapify_{uuid.uuid4().hex[:8]}",
            origin=origin,
            destination=destination,
            total_distance_km=dist_m / 1000.0,
            total_duration_minutes=dur_s / 60.0,
            provider_source=ProviderSource.GEOAPIFY
        )
