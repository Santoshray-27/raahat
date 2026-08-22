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

    # Mapping: ServiceType -> (geoapify_categories_csv, accept_fn)
    #
    # Rules derived from live Geoapify category taxonomy for India:
    #   service.vehicle.repair  → car/motorcycle repair workshops
    #   service.vehicle.fuel    → petrol/diesel stations (use for FUEL_DELIVERY)
    #   healthcare.hospital     → hospitals
    #   healthcare              → broad health (filter to ambulance)
    #   amenity.police          → police stations
    #   amenity.fire_brigade    → fire stations
    #
    # For PUNCTURE_REPAIR and TOWING, Geoapify has no dedicated leaf category in
    # Indian OSM data.  Query service.vehicle.repair (repair shops) and accept all
    # of them — they universally handle tyre/puncture work.  Towing is similar:
    # query the same repair shops and flag as TOWING-capable.
    #
    # For FUEL_DELIVERY, Geoapify puts petrol stations under service.vehicle.fuel
    # (NOT under amenity), so we must use that category.

    _CATEGORY_MAP: dict = {
        ServiceType.HOSPITAL: (
            "healthcare.hospital",
            lambda cats, name, tags: True,          # accept all hospitals
        ),
        ServiceType.AMBULANCE: (
            "healthcare",
            lambda cats, name, tags: (
                "ambulance" in name
                or any("hospital" in c for c in cats)
                or any("hospital" in c for c in cats)
            ),
        ),
        ServiceType.POLICE: (
            "amenity.police",
            lambda cats, name, tags: True,          # category is already specific
        ),
        ServiceType.FIRE_BRIGADE: (
            "amenity.fire_brigade",
            lambda cats, name, tags: True,
        ),
        # MECHANIC: repair workshops (service.vehicle.repair) — accept if named
        ServiceType.MECHANIC: (
            "service.vehicle.repair",
            lambda cats, name, tags: bool(name),
        ),
        # PUNCTURE_REPAIR: same repair shops — they do tyre/puncture work.
        # Accept all named repair/service workshops.
        ServiceType.PUNCTURE_REPAIR: (
            "service.vehicle.repair",
            lambda cats, name, tags: bool(name),
        ),
        # TOWING: repair workshops are the closest proxy (towing trucks often
        # operate from them).  Accept all named entries.
        ServiceType.TOWING: (
            "service.vehicle.repair",
            lambda cats, name, tags: bool(name),
        ),
        # FUEL_DELIVERY: petrol stations
        ServiceType.FUEL_DELIVERY: (
            "service.vehicle.fuel",
            lambda cats, name, tags: True,
        ),
    }

    async def search_nearby(
        self,
        location: GeoPoint,
        service_types: List[ServiceType],
        radius_km: float = 10.0,
        limit: int = 10,
    ) -> List[ServiceProvider]:
        if not settings.GEOAPIFY_API_KEY:
            logger.warning("Geoapify key not configured. Skipping.")
            raise GeoapifyProviderError("Key not configured")

        main_type = service_types[0] if service_types else ServiceType.HOSPITAL
        mapping = self._CATEGORY_MAP.get(main_type)
        if not mapping:
            logger.warning(f"Geoapify: no category mapping for {main_type.value}. Skipping.")
            raise GeoapifyProviderError(f"No mapping for {main_type.value}")

        api_category, accept_fn = mapping
        # Fetch generously — we filter in Python afterward
        api_limit = max(limit * 3, 20)

        url = "https://api.geoapify.com/v2/places"
        params = {
            "categories": api_category,
            "filter": f"circle:{location.longitude},{location.latitude},{int(radius_km * 1000)}",
            "bias": f"proximity:{location.longitude},{location.latitude}",
            "rank.distance": "asc",
            "limit": api_limit,
            "apiKey": settings.GEOAPIFY_API_KEY,
            "lang": "en",
        }

        try:
            async with httpx.AsyncClient(timeout=12.0) as client:
                response = await client.get(url, params=params)

            if response.status_code in [401, 403]:
                raise GeoapifyProviderError(
                    f"Geoapify auth error: {response.status_code}"
                )
            if response.status_code == 429:
                raise GeoapifyProviderError("Geoapify rate-limit exceeded")
            if response.status_code != 200:
                logger.warning(
                    f"Geoapify category {api_category} returned HTTP {response.status_code}."
                )
                raise GeoapifyProviderError(
                    f"Geoapify returned HTTP {response.status_code}"
                )

            data = response.json()
            features = data.get("features", [])
            logger.info(
                f"Geoapify: {len(features)} raw features for {main_type.value} "
                f"(category={api_category})"
            )

            results = []
            for feat in features:
                props = feat.get("properties", {})
                cats = [c.lower() for c in props.get("categories", [])]
                raw_tags = props.get("tags", [])
                tags = (
                    [t.lower() for t in raw_tags]
                    if isinstance(raw_tags, list)
                    else (list(raw_tags.keys()) if isinstance(raw_tags, dict) else [])
                )
                name_val = props.get("name", "") or ""
                name_lower = name_val.lower()

                # Apply the per-service-type acceptance function
                if not accept_fn(cats, name_lower, tags):
                    logger.debug(
                        f"Geoapify: rejected '{name_val}' for {main_type.value}"
                    )
                    continue

                # Skip unnamed entries for non-hospital types
                if not name_val and main_type != ServiceType.HOSPITAL:
                    continue
                if not name_val:
                    name_val = props.get("address_line1", "Unknown Service")

                # Hospital quality scoring (unchanged)
                quality_score = 0.0
                if main_type == ServiceType.HOSPITAL:
                    pos_kw = ["hospital", "nursing", "care", "superspeciality",
                              "हॉस्पिटल", "अस्पताल"]
                    neg_kw = ["homeo", "ayush", "ayurved", "dental", "eye",
                              "skin", "clinic", "चिकित्सालय", "होमियो"]
                    if any(w in name_lower for w in pos_kw):
                        quality_score += 0.5
                    if any(w in name_lower for w in neg_kw):
                        quality_score -= 0.3
                    if quality_score < 0:
                        continue

                # Distance: use Geoapify's pre-computed value if present
                dist_raw = props.get("distance")
                loc = GeoPoint(
                    latitude=props.get("lat", 0.0),
                    longitude=props.get("lon", 0.0),
                )
                if dist_raw is not None:
                    dist_m = float(dist_raw)
                else:
                    dist_m = calculate_haversine_distance(location, loc) * 1000.0

                address_parts = [
                    p for p in [
                        props.get("address_line1", ""),
                        props.get("address_line2", ""),
                    ] if p
                ]
                address_line = ", ".join(address_parts) or None

                contact_raw = props.get("contact", {}) or {}
                phone = None
                if contact_raw.get("phone"):
                    phone = str(contact_raw["phone"])

                sp = ServiceProvider(
                    provider_id=f"geoapify_{props.get('place_id', str(uuid.uuid4()))}",
                    name=name_val,
                    service_types=[main_type.value],
                    location=loc,
                    address=LocationAddress(
                        formatted_address=address_line,
                        city=props.get("city"),
                        state=props.get("state"),
                        country=props.get("country", "India"),
                        postal_code=props.get("postcode"),
                    ),
                    contact=ContactInfo(phone_primary=phone),
                    distance_km=round(dist_m / 1000.0, 2),
                    eta_minutes=max(1, int(dist_m / 1000.0 * 2)),
                    rating=None,
                    review_count=0,
                    availability_status="UNKNOWN",
                    recommendation_score=(
                        quality_score if main_type == ServiceType.HOSPITAL else 0.85
                    ),
                    source=ProviderSource.GEOAPIFY,
                    is_cached=False,
                    retrieved_at=datetime.now(timezone.utc).isoformat(),
                )
                results.append((quality_score, sp))

            if not results:
                logger.warning(
                    f"Geoapify: 0 providers accepted after filtering for {main_type.value}."
                )
                raise GeoapifyProviderError(
                    f"0 accepted results for {main_type.value}"
                )

            # Sort: hospitals by quality+distance, others by distance
            if main_type == ServiceType.HOSPITAL:
                results.sort(key=lambda x: (-x[0], x[1].distance_km))
            else:
                results.sort(key=lambda x: x[1].distance_km)

            final = [item[1] for item in results][:limit]
            logger.info(
                f"Geoapify: returning {len(final)} providers for {main_type.value}"
            )
            return final

        except GeoapifyProviderError:
            raise
        except Exception as e:
            logger.error(f"Geoapify request failed unexpectedly: {e}", exc_info=True)
            raise GeoapifyProviderError(f"Unexpected error: {e}")


class GeoapifyRoutingProvider(BaseRoutingProvider):
    name = "geoapify_routing"

    async def plan_route(
        self,
        origin: GeoPoint,
        destination: GeoPoint,
        avoid_highways: bool = False,
        avoid_tolls: bool = False,
    ) -> RoutePlanResponseData:
        if not settings.GEOAPIFY_API_KEY:
            raise GeoapifyProviderError("Geoapify key not configured")

        url = "https://api.geoapify.com/v1/routing"
        params = {
            "waypoints": (
                f"{origin.latitude},{origin.longitude}"
                f"|{destination.latitude},{destination.longitude}"
            ),
            "mode": "drive",
            "apiKey": settings.GEOAPIFY_API_KEY,
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                response = await client.get(url, params=params)
                if response.status_code in [401, 403, 429]:
                    raise GeoapifyProviderError(
                        f"Geoapify routing error {response.status_code}"
                    )
                response.raise_for_status()
                data = response.json()
            except GeoapifyProviderError:
                raise
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
            provider_source=ProviderSource.GEOAPIFY,
        )
