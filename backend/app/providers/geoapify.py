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
        ServiceType.FIRE_BRIGADE: ("amenity", ["fire"]),
        ServiceType.PUNCTURE_REPAIR: ("service.vehicle", ["tire", "tyre", "puncture"]),
        ServiceType.MECHANIC: ("service.vehicle.repair", []),
        ServiceType.TOWING: ("service.vehicle", ["tow", "towing", "crane", "recovery"]),
        ServiceType.FUEL_DELIVERY: ("amenity", ["fuel", "petrol", "gas"]),
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

        is_parent_cat = main_type in [
            ServiceType.POLICE, ServiceType.FIRE_BRIGADE, ServiceType.AMBULANCE,
            ServiceType.FUEL_DELIVERY, ServiceType.TOWING, ServiceType.PUNCTURE_REPAIR
        ]
        api_limit = 30 if is_parent_cat else max(limit * 3, 20)

        url = "https://api.geoapify.com/v2/places"
        params = {
            "categories": api_category,
            "filter": f"circle:{location.longitude},{location.latitude},{int(radius_km * 1000)}",
            "bias": f"proximity:{location.longitude},{location.latitude}",
            "rank.distance": "asc",
            "limit": api_limit,
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
                
                # Apply strict category and tag filtering
                filtered_features = []
                for f in features:
                    props = f.get("properties", {})
                    cats = [c.lower() for c in props.get("categories", [])]
                    raw_tags = props.get("tags", [])
                    tags = [t.lower() for t in raw_tags] if isinstance(raw_tags, list) else (list(raw_tags.keys()) if isinstance(raw_tags, dict) else [])
                    name_val = props.get("name", "")
                    name_lower = name_val.lower()
                    address_line = (props.get("address_line1", "") + " " + props.get("address_line2", "")).lower()

                    corpus_str = " ".join(cats + tags + [name_lower, address_line])

                    if main_type == ServiceType.POLICE:
                        if "police" in corpus_str:
                            filtered_features.append(f)
                    elif main_type == ServiceType.FIRE_BRIGADE:
                        if "fire" in corpus_str:
                            filtered_features.append(f)
                    elif main_type == ServiceType.FUEL_DELIVERY:
                        if any(k in corpus_str for k in ["fuel", "petrol", "gas_station"]):
                            filtered_features.append(f)
                    elif main_type == ServiceType.AMBULANCE:
                        if "ambulance" in corpus_str or ("hospital" in corpus_str and "emergency" in corpus_str):
                            filtered_features.append(f)
                    elif main_type == ServiceType.TOWING:
                        if "tow" in corpus_str:
                            filtered_features.append(f)
                    elif main_type == ServiceType.PUNCTURE_REPAIR:
                        if any(k in name_lower for k in ["tire", "tyre", "puncture"]) or any("tire" in c for c in cats):
                            filtered_features.append(f)
                    elif main_type == ServiceType.MECHANIC:
                        if any("service.vehicle.repair" in c or "car_repair" in c for c in cats) or any(k in name_lower for k in ["repair", "mechanic", "garage", "auto", "motors", "service"]):
                            if name_val:
                                filtered_features.append(f)
                    elif main_type == ServiceType.HOSPITAL:
                        filtered_features.append(f)
                    else:
                        filtered_features.append(f)

                features = filtered_features

                if not features:
                    logger.warning(f"Geoapify: 0 features remaining after strict filtering for {main_type.value}.")
                    raise GeoapifyProviderError(f"0 features found after strict filtering for {main_type.value}")

                results = []
                for f in features:
                    props = f.get("properties", {})
                    place_id = props.get("place_id", str(uuid.uuid4()))
                    
                    dist = props.get("distance")
                    loc = GeoPoint(latitude=props.get("lat", 0), longitude=props.get("lon", 0))
                    if dist is None:
                        dist = calculate_haversine_distance(location, loc) * 1000.0

                    address_line = props.get("address_line1", "")
                    if props.get("address_line2"):
                        address_line += ", " + props.get("address_line2")

                    name_val = props.get("name")
                    if not name_val and main_type != ServiceType.HOSPITAL:
                        continue
                    if not name_val:
                        name_val = props.get("address_line1", "Unknown Service")
                    
                    # Hospital Quality Scoring
                    quality_score = 0.0
                    if main_type == ServiceType.HOSPITAL:
                        name_lower = name_val.lower()
                        pos_keywords = ["hospital", "nursing", "care", "superspeciality", "हॉस्पिटल", "अस्पताल"]
                        neg_keywords = ["homeo", "ayush", "ayurved", "dental", "eye", "skin", "clinic", "चिकित्सालय", "होमियो"]
                        
                        if any(w in name_lower for w in pos_keywords):
                            quality_score += 0.5
                        if any(w in name_lower for w in neg_keywords):
                            quality_score -= 0.3
                            
                        if quality_score < 0:
                            continue

                    sp = ServiceProvider(
                        provider_id=f"geoapify_{place_id}",
                        name=name_val,
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
                        recommendation_score=quality_score if main_type == ServiceType.HOSPITAL else 0.85,
                        source=ProviderSource.GEOAPIFY,
                        is_cached=False,
                        retrieved_at=datetime.now(timezone.utc).isoformat()
                    )
                    results.append((quality_score, sp))
                
                if results:
                    if main_type == ServiceType.HOSPITAL:
                        sorted_items = sorted(results, key=lambda x: (-x[0], x[1].distance_km))
                        return [item[1] for item in sorted_items][:limit]
                    else:
                        sorted_items = sorted(results, key=lambda x: x[1].distance_km)
                        return [item[1] for item in sorted_items][:limit]
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
