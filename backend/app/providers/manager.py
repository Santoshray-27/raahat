import time
import asyncio
from datetime import datetime, timezone
from typing import List, Tuple, Dict, Any
from fastapi import HTTPException, status
from app.core.config import settings
from app.core.logging import logger
from app.providers.osm_overpass import OSMOverpassProvider
from app.providers.osrm import OSRMRoutingProvider
from app.providers.geoapify import GeoapifyPlacesProvider, GeoapifyRoutingProvider, GeoapifyProviderError
from app.providers.mock_provider import MockPlacesProvider, MockRoutingProvider
from app.schemas.common import GeoPoint, ServiceProvider
from app.schemas.enums import ServiceType, ProviderSource
from app.schemas.routes import RoutePlanResponseData


def _is_usable_coordinate(lat: float, lon: float) -> bool:
    """
    Return False for coordinates that are technically valid range-wise but are
    clearly placeholder / degenerate values:
      - (0.0, 0.0)     null island
      - (-90.0, -180.0) Swagger/OpenAPI default example placeholder
    Both would cause a "nearby services" search in the middle of an ocean.
    """
    if lat == 0.0 and lon == 0.0:
        return False
    if lat == -90.0 and lon == -180.0:
        return False
    return True


class ProviderManager:
    def __init__(self):
        self.geoapify_places = GeoapifyPlacesProvider()
        self.geoapify_routing = GeoapifyRoutingProvider()
        self.osm_overpass = OSMOverpassProvider()
        self.osrm_routing = OSRMRoutingProvider()
        self.mock_places = MockPlacesProvider()
        self.mock_routing = MockRoutingProvider()

    async def get_nearby_services(
        self,
        location: GeoPoint,
        service_types: List[ServiceType],
        radius_km: float = 10.0,
        limit: int = 10
    ) -> Tuple[List[ServiceProvider], str]:
        main_type = service_types[0] if service_types else ServiceType.HOSPITAL
        category_name = main_type.value

        # 1. Check if USE_MOCKS is explicitly enabled for offline dev
        if settings.USE_MOCKS:
            logger.info("ProviderManager: Using MockPlacesProvider (USE_MOCKS=True)")
            res = await self.mock_places.search_nearby(location, service_types, radius_km, limit)
            for p in res:
                p.source = "MOCK"
                p.retrieved_at = datetime.now(timezone.utc).isoformat()
            return res[:limit], "MOCK"

        # 2. Coordinate usability guard — reject null-island and Swagger placeholders
        if not _is_usable_coordinate(location.latitude, location.longitude):
            logger.warning(
                f"ProviderManager: Degenerate coordinates ({location.latitude},{location.longitude}). "
                "Falling back to curated data with CURATED_LOCATION_UNAVAILABLE flag."
            )
            from app.services.curated_service import curated_provider_manager
            curated_res = curated_provider_manager.get_fallback_providers(
                location, service_types, limit=limit
            )
            return curated_res, "CURATED_LOCATION_UNAVAILABLE"

        chain = ["GEOAPIFY", "OSM"]

        async def _execute_chain() -> Tuple[List[ServiceProvider], str]:
            last_source_used = "UNKNOWN"
            for provider_name in chain:
                if provider_name == "GEOAPIFY" and settings.GEOAPIFY_API_KEY:
                    try:
                        logger.info("ProviderManager: Querying LIVE Geoapify Places API...")
                        t0 = time.time()
                        # Geoapify latency typically 1-5s; allow 14s
                        res = await asyncio.wait_for(
                            self.geoapify_places.search_nearby(location, service_types, radius_km, limit),
                            timeout=14.0
                        )
                        latency = int((time.time() - t0) * 1000)
                        if res:
                            logger.info(f"Provider GEOAPIFY returned {len(res)} results in {latency}ms.")
                            for p in res:
                                p.source = ProviderSource.GEOAPIFY
                                p.retrieved_at = datetime.now(timezone.utc).isoformat()
                            return res[:limit], "GEOAPIFY"
                        logger.info(f"Provider GEOAPIFY returned 0 results in {latency}ms.")
                        last_source_used = "GEOAPIFY"
                    except asyncio.TimeoutError:
                        logger.warning("Provider GEOAPIFY timed out after 14.0s.")
                    except Exception as e:
                        logger.warning(f"Provider GEOAPIFY error: {e}")

                elif provider_name == "OSM":
                    try:
                        logger.info("ProviderManager: Querying LIVE OSM Overpass API...")
                        t0 = time.time()
                        # OSM Overpass latency can be 10-20s; allow 22s
                        res = await asyncio.wait_for(
                            self.osm_overpass.search_nearby(location, service_types, radius_km, limit),
                            timeout=22.0
                        )
                        latency = int((time.time() - t0) * 1000)
                        if res:
                            logger.info(f"Provider OSM returned {len(res)} results in {latency}ms.")
                            for p in res:
                                p.source = ProviderSource.OSM_OVERPASS
                                p.retrieved_at = datetime.now(timezone.utc).isoformat()
                            return res[:limit], "OSM_OVERPASS"
                        logger.info(f"Provider OSM returned 0 results in {latency}ms.")
                        last_source_used = "OSM_OVERPASS"
                    except asyncio.TimeoutError:
                        logger.warning("Provider OSM timed out after 22.0s.")
                    except Exception as e:
                        logger.warning(f"Provider OSM error: {e}")

            # If live providers returned 0 items or all failed → CURATED fallback
            from app.services.curated_service import curated_provider_manager
            logger.info(
                f"ProviderManager: Live providers returned 0 items for {category_name}. "
                "Falling back to CURATED seed data."
            )
            curated_res = curated_provider_manager.get_fallback_providers(
                location, service_types, limit=limit
            )
            if curated_res:
                return curated_res, "CURATED"

            return [], last_source_used if last_source_used != "UNKNOWN" else "GEOAPIFY"

        try:
            # Global SLA: Geoapify 14s + OSM 22s + buffer = 35s
            results, source = await asyncio.wait_for(_execute_chain(), timeout=35.0)
        except asyncio.TimeoutError:
            logger.error(
                "ProviderManager: Global SLA timeout exceeded for get_nearby_services. "
                "Returning curated fallback."
            )
            from app.services.curated_service import curated_provider_manager
            results = curated_provider_manager.get_fallback_providers(
                location, service_types, limit=limit
            )
            source = "CURATED"

        # Guarantee nearest-first sorting and non-null distance / ETA properties
        from app.services.ranking import calculate_haversine_distance
        for p in results:
            p.distance_km = round(calculate_haversine_distance(location, p.location), 2)
            p.eta_minutes = max(1, int(p.distance_km * 2))

        sorted_results = sorted(results, key=lambda x: x.distance_km)
        return sorted_results[:limit], source

    async def plan_route(
        self,
        origin: GeoPoint,
        destination: GeoPoint,
        avoid_highways: bool = False,
        avoid_tolls: bool = False
    ) -> RoutePlanResponseData:
        # 1. Check if USE_MOCKS is explicitly enabled
        if settings.USE_MOCKS:
            logger.info("ProviderManager: Using MockRoutingProvider (USE_MOCKS=True)")
            return await self.mock_routing.plan_route(origin, destination, avoid_highways, avoid_tolls)

        chain = ["GEOAPIFY", "OSRM"]

        async def _execute_route_chain() -> RoutePlanResponseData:
            for provider_name in chain:
                if provider_name == "GEOAPIFY" and settings.GEOAPIFY_API_KEY:
                    try:
                        logger.info("ProviderManager: Querying LIVE Geoapify Routing API...")
                        res = await self.geoapify_routing.plan_route(origin, destination, avoid_highways, avoid_tolls)
                        res.provider_source = ProviderSource.GEOAPIFY
                        return res
                    except Exception as e:
                        logger.warning(f"Geoapify Routing failed: {e}.")

                elif provider_name == "OSRM":
                    try:
                        logger.info("ProviderManager: Querying LIVE OSRM Routing API...")
                        res = await self.osrm_routing.plan_route(origin, destination, avoid_highways, avoid_tolls)
                        res.provider_source = ProviderSource.OSRM
                        return res
                    except Exception as e:
                        logger.warning(f"OSRM Routing failed: {e}.")

            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="UPSTREAM_PROVIDER_ERROR: Unable to compute live navigation route via Geoapify or OSRM."
            )

        try:
            return await asyncio.wait_for(_execute_route_chain(), timeout=12.0)
        except asyncio.TimeoutError:
            logger.error("ProviderManager: Global SLA timeout exceeded for plan_route.")
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="GLOBAL_SLA_TIMEOUT: Route planning exceeded maximum allowed time."
            )

provider_manager = ProviderManager()
