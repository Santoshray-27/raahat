import httpx
from datetime import datetime, timezone
import uuid
from typing import List, Optional, Tuple
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

    # Category map: (geoapify_api_category, [local_filter_keywords])
    # ONLY pass 200-returning categories to the API!
    _CATEGORY_MAP: dict[ServiceType, Tuple[str, List[str]]] = {
        ServiceType.HOSPITAL: ("healthcare.hospital", []),
        ServiceType.AMBULANCE: ("healthcare", ["ambulance"]),
        ServiceType.POLICE: ("amenity", ["police"]),
        ServiceType.FIRE_BRIGADE: ("amenity", ["fire", "fire_station"]),
        ServiceType.PUNCTURE_REPAIR: ("service.vehicle", []),
        ServiceType.MECHANIC: ("service.vehicle.repair", []),
        ServiceType.TOWING: ("service.vehicle", ["towing"]),
        ServiceType.FUEL_DELIVERY: ("commercial", ["fuel", "gas"]),
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
        api_category, filter_keywords = self._CATEGORY_MAP.get(main_type, ("amenity", []))

        url = "https://api.geoapify.com/v2/places"
        params = {
            "categories": api_category,
            "filter": f"circle:{location.longitude},{location.latitude},{int(radius_km * 1000)}",
            "limit": max(limit * 3, 20) if filter_keywords else limit,  # Fetch more if doing local filtering
            "apiKey": settings.GEOAPIFY_API_KEY,
            "lang": "en"
        }
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(url, params=params)
                if response.status_code in [401, 403, 429]:
                    raise GeoapifyProviderError(f"Geoapify authentication/rate limit error: {response.status_code}")
                if response.status_code != 200:
                    logger.warning(f"Geoapify category {api_category} returned {response.status_code}.")
                    raise GeoapifyProviderError(f"Geoapify returned {response.status_code}")

                data = response.json()
                features = data.get("features", [])
                
                # Apply local keyword filtering if filter_keywords specified
                if filter_keywords and features:
                    filtered_features = []
                    for f in features:
                        props = f.get("properties", {})
                        item_cats = [c.lower() for c in props.get("categories", [])]
                        item_name = props.get("name", "").lower()
                        
                        # Match if any keyword is in item categories or name
                        matched = any(
                            kw.lower() in cat_str or kw.lower() in item_name
                            for kw in filter_keywords
                            for cat_str in item_cats + [item_name]
                        )
                        if matched:
                            filtered_features.append(f)
                    
                    # If local filter yielded matching features, use them; else fallback to raw features
                    if filtered_features:
                        features = filtered_features

                if features:
                    results = []
                    for f in features[:limit]:
                        props = f.get("properties", {})
                        place_id = props.get("place_id", str(uuid.uuid4()))
                        
                        dist = props.get("distance")
                        loc = GeoPoint(latitude=props.get("lat", 0), longitude=props.get("lon", 0))
                        if dist is None:
                            dist = calculate_haversine_distance(location, loc) * 1000.0

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
                            distance_km=round(dist / 1000.0, 2),
                            eta_minutes=max(1, int(dist / 1000.0 * 2)),
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
            total_distance_km=round(dist_m / 1000.0, 2),
            total_duration_minutes=round(dur_s / 60.0, 1),
            provider_source=ProviderSource.GEOAPIFY
        )
