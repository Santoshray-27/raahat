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
from app.schemas.enums import ServiceType
from app.schemas.routes import RoutePlanResponseData

class ProviderManager:
    def __init__(self):
        self.google_places = GooglePlacesProvider()
        self.google_routes = GoogleRoutesProvider()
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
        start_time = time.time()
        category_name = service_types[0].value if service_types else "GENERAL"

        # 1. Check if USE_MOCKS is explicitly enabled for offline dev
        if settings.USE_MOCKS:
            logger.info("ProviderManager: Using MockPlacesProvider (USE_MOCKS=True)")
            res = await self.mock_places.search_nearby(location, service_types, radius_km, limit)
            for p in res:
                p.source = "MOCK"
                p.retrieved_at = datetime.now(timezone.utc).isoformat()
            return res[:limit], "MOCK"

        # Check circuit breaker status
        google_exhausted, expiry_time = google_circuit_breaker.is_exhausted()

        # Build live chain order based on circuit breaker state
        # If Google quota is exhausted, reorder live chain to Geoapify FIRST, then OSM, then Google.
        if google_exhausted:
            logger.info(f"ProviderManager: Google quota exhausted (until {expiry_time}). Reordering chain: [Geoapify, OSM, Google].")
            chain = ["GEOAPIFY", "OSM", "GOOGLE"]
        else:
            chain = ["GOOGLE", "GEOAPIFY", "OSM"]

        async def _execute_chain() -> Tuple[List[ServiceProvider], str]:
            last_source_used = "UNKNOWN"
            for provider_name in chain:
                if provider_name == "GOOGLE" and settings.GOOGLE_PLACES_API_KEY:
                    # Double check exhaustion before trying Google
                    is_ex, _ = google_circuit_breaker.is_exhausted()
                    if is_ex:
                        continue
                    try:
                        logger.info("ProviderManager: Querying LIVE Google Places API...")
                        res = await self.google_places.search_nearby(location, service_types, radius_km, limit)
                        if res:
                            for p in res:
                                p.source = "GOOGLE_PLACES"
                                p.retrieved_at = datetime.now(timezone.utc).isoformat()
                            return res[:limit], "GOOGLE_PLACES"
                        last_source_used = "GOOGLE_PLACES"
                    except Exception as e:
                        logger.warning(f"Google Places API call failed/skipped: {e}.")
    
                elif provider_name == "GEOAPIFY" and settings.GEOAPIFY_API_KEY:
                    try:
                        logger.info("ProviderManager: Querying LIVE Geoapify Places API...")
                        res = await self.geoapify_places.search_nearby(location, service_types, radius_km, limit)
                        if res:
                            for p in res:
                                p.source = "GEOAPIFY"
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
                                p.source = "OSM_OVERPASS"
                                p.retrieved_at = datetime.now(timezone.utc).isoformat()
                            return res[:limit], "OSM_OVERPASS"
                        last_source_used = "OSM_OVERPASS"
                    except Exception as e:
                        logger.warning(f"OSM Overpass API call failed: {e}.")
    
            # If live queries completed without exception but returned 0 items, return empty list gracefully
            logger.info(f"ProviderManager: All live providers queried. Zero results found for category {category_name}.")
            return [], last_source_used if last_source_used != "UNKNOWN" else "GEOAPIFY"

        try:
            # 12.0 seconds global SLA for provider search
            return await asyncio.wait_for(_execute_chain(), timeout=12.0)
        except asyncio.TimeoutError:
            logger.error("ProviderManager: Global SLA timeout exceeded for get_nearby_services. Returning gracefully.")
            return [], "TIMEOUT_FALLBACK"

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

        google_exhausted, expiry_time = google_circuit_breaker.is_exhausted()

        if google_exhausted:
            chain = ["GEOAPIFY", "OSRM", "GOOGLE"]
        else:
            chain = ["GOOGLE", "GEOAPIFY", "OSRM"]

        async def _execute_route_chain() -> RoutePlanResponseData:
            for provider_name in chain:
                if provider_name == "GOOGLE" and settings.GOOGLE_ROUTES_API_KEY:
                    is_ex, _ = google_circuit_breaker.is_exhausted()
                    if is_ex:
                        continue
                    try:
                        logger.info("ProviderManager: Querying LIVE Google Routes API...")
                        res = await self.google_routes.plan_route(origin, destination, avoid_highways, avoid_tolls)
                        res.provider_source = "GOOGLE_ROUTES"
                        return res
                    except Exception as e:
                        logger.warning(f"Google Routes API failed: {e}.")
    
                elif provider_name == "GEOAPIFY" and settings.GEOAPIFY_API_KEY:
                    try:
                        logger.info("ProviderManager: Querying LIVE Geoapify Routing API...")
                        res = await self.geoapify_routing.plan_route(origin, destination, avoid_highways, avoid_tolls)
                        res.provider_source = "GEOAPIFY"
                        return res
                    except Exception as e:
                        logger.warning(f"Geoapify Routing failed: {e}.")
    
                elif provider_name == "OSRM":
                    try:
                        logger.info("ProviderManager: Querying LIVE OSRM Routing API...")
                        res = await self.osrm_routing.plan_route(origin, destination, avoid_highways, avoid_tolls)
                        res.provider_source = "OSRM"
                        return res
                    except Exception as e:
                        logger.warning(f"OSRM Routing failed: {e}.")
    
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="UPSTREAM_PROVIDER_ERROR: Unable to compute live navigation route via Google Routes, Geoapify, or OSRM."
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
