import time
import asyncio
from datetime import datetime, timezone
from typing import List, Tuple, Dict, Any
from fastapi import HTTPException, status
from app.core.config import settings
from app.core.logging import logger
from app.core.circuit_breaker import google_circuit_breaker
from app.providers.google_places import GooglePlacesProvider
from app.providers.google_routes import GoogleRoutesProvider
from app.providers.osm_overpass import OSMOverpassProvider
from app.providers.osrm import OSRMRoutingProvider
from app.providers.geoapify import GeoapifyPlacesProvider, GeoapifyRoutingProvider, GeoapifyProviderError
from app.providers.mock_provider import MockPlacesProvider, MockRoutingProvider
from app.schemas.common import GeoPoint, ServiceProvider
from app.schemas.enums import ServiceType, ProviderSource
from app.schemas.routes import RoutePlanResponseData

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

        # Per-Category Preferred Order
        if main_type in [ServiceType.POLICE, ServiceType.FIRE_BRIGADE, ServiceType.AMBULANCE]:
            chain = ["OSM", "GEOAPIFY"]
        else:
            chain = ["GEOAPIFY", "OSM"]

        async def _execute_chain() -> Tuple[List[ServiceProvider], str]:
            last_source_used = "UNKNOWN"
            for provider_name in chain:
                if provider_name == "GEOAPIFY" and settings.GEOAPIFY_API_KEY:
                    try:
                        logger.info("ProviderManager: Querying LIVE Geoapify Places API...")
                        res = await self.geoapify_places.search_nearby(location, service_types, radius_km, limit)
                        if res:
                            for p in res:
                                p.source = ProviderSource.GEOAPIFY
                                p.retrieved_at = datetime.now(timezone.utc).isoformat()
                            return res[:limit], "GEOAPIFY"
                        last_source_used = "GEOAPIFY"
                    except Exception as e:
                        logger.warning(f"Geoapify Places API call failed: {e}.")

                elif provider_name == "OSM":
                    try:
                        logger.info("ProviderManager: Querying LIVE OSM Overpass API...")
                        res = await self.osm_overpass.search_nearby(location, service_types, radius_km, limit)
                        if res:
                            for p in res:
                                p.source = ProviderSource.OSM_OVERPASS
                                p.retrieved_at = datetime.now(timezone.utc).isoformat()
                            return res[:limit], "OSM_OVERPASS"
                        last_source_used = "OSM_OVERPASS"
                    except Exception as e:
                        logger.warning(f"OSM Overpass API call failed: {e}.")

            # If live providers returned 0 items or failed, fall back to CURATED seed data
            from app.services.curated_service import curated_provider_manager
            logger.info(f"ProviderManager: Live providers returned 0 items for {category_name}. Falling back to CURATED seed data.")
            curated_res = curated_provider_manager.get_fallback_providers(location, service_types, limit=limit)
            if curated_res:
                return curated_res, "CURATED"

            return [], last_source_used if last_source_used != "UNKNOWN" else "GEOAPIFY"

        try:
            results, source = await asyncio.wait_for(_execute_chain(), timeout=12.0)
        except asyncio.TimeoutError:
            logger.error("ProviderManager: Global SLA timeout exceeded for get_nearby_services. Returning curated fallback.")
            from app.services.curated_service import curated_provider_manager
            results = curated_provider_manager.get_fallback_providers(location, service_types, limit=limit)
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
