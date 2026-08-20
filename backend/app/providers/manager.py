import time
from datetime import datetime, timezone
from typing import List, Tuple, Dict, Any
from fastapi import HTTPException, status
from app.core.config import settings
from app.core.logging import logger
from app.providers.google_places import GooglePlacesProvider
from app.providers.google_routes import GoogleRoutesProvider
from app.providers.osm_overpass import OSMOverpassProvider
from app.providers.osrm import OSRMRoutingProvider
from app.providers.geoapify import GeoapifyPlacesProvider, GeoapifyRoutingProvider, GeoapifyProviderError
from app.providers.mock_provider import MockPlacesProvider, MockRoutingProvider
from app.schemas.common import GeoPoint, ServiceProvider
from app.schemas.enums import ServiceType
from app.schemas.routes import RoutePlanResponseData

# Removed local diagnostic recorder; using centralized telemetry now.


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

        # 2. Live Chain 1: Try Google Places API
        if settings.GOOGLE_PLACES_API_KEY:
            try:
                logger.info("ProviderManager: Querying LIVE Google Places API...")
                res = await self.google_places.search_nearby(location, service_types, radius_km, limit)
                if res:
                    for p in res:
                        p.source = "GOOGLE_PLACES"
                        p.retrieved_at = datetime.now(timezone.utc).isoformat()
                    return res[:limit], "GOOGLE_PLACES"
            except Exception as e:
                logger.warning(f"Google Places API call failed: {e}. Falling back to Geoapify...")

        # 3. Live Chain 2: Fallback to Geoapify API
        if settings.GEOAPIFY_API_KEY:
            try:
                logger.info("ProviderManager: Querying LIVE Geoapify Places API...")
                res = await self.geoapify_places.search_nearby(location, service_types, radius_km, limit)
                if res:
                    for p in res:
                        p.source = "GEOAPIFY"
                        p.retrieved_at = datetime.now(timezone.utc).isoformat()
                    return res[:limit], "GEOAPIFY"
            except GeoapifyProviderError as e:
                logger.warning(f"Geoapify API failed/unauthorized: {e}. Falling back to OpenStreetMap Overpass...")
            except Exception as e:
                logger.warning(f"Geoapify Places API call failed: {e}. Falling back to OpenStreetMap Overpass...")

        # 4. Live Chain 3: Fallback to OpenStreetMap Overpass API
        try:
            logger.info("ProviderManager: Querying LIVE OSM Overpass API...")
            res = await self.osm_overpass.search_nearby(location, service_types, radius_km, limit)
            if res:
                for p in res:
                    p.source = "OSM_OVERPASS"
                    p.retrieved_at = datetime.now(timezone.utc).isoformat()
                return res[:limit], "OSM_OVERPASS"
        except Exception as e:
            logger.error(f"OSM Overpass API call failed: {e}")

        # 4. Fail LOUD in Live Mode — Never fabricate silent mock data!
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="UPSTREAM_PROVIDER_ERROR: Unable to retrieve live emergency providers from Google Places or OpenStreetMap. Please check network connectivity or try again."
        )

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

        # 2. Try Google Routes API
        if settings.GOOGLE_ROUTES_API_KEY:
            try:
                logger.info("ProviderManager: Querying LIVE Google Routes API...")
                res = await self.google_routes.plan_route(origin, destination, avoid_highways, avoid_tolls)
                res.provider_source = "GOOGLE_ROUTES"
                return res
            except Exception as e:
                logger.warning(f"Google Routes API failed: {e}. Falling back to Geoapify...")

        # 3. Fallback to Geoapify Routing
        if settings.GEOAPIFY_API_KEY:
            try:
                logger.info("ProviderManager: Querying LIVE Geoapify Routing API...")
                res = await self.geoapify_routing.plan_route(origin, destination, avoid_highways, avoid_tolls)
                res.provider_source = "GEOAPIFY"
                return res
            except GeoapifyProviderError as e:
                logger.warning(f"Geoapify Routing API failed/unauthorized: {e}. Falling back to OSRM...")
            except Exception as e:
                logger.warning(f"Geoapify Routing failed: {e}. Falling back to OSRM...")

        # 4. Fallback to OSRM
        try:
            logger.info("ProviderManager: Querying LIVE OSRM Routing API...")
            res = await self.osrm_routing.plan_route(origin, destination, avoid_highways, avoid_tolls)
            res.provider_source = "OSRM"
            return res
        except Exception as e:
            logger.error(f"OSRM Routing failed: {e}")

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="UPSTREAM_PROVIDER_ERROR: Unable to compute live navigation route via Google Routes or OSRM."
        )

provider_manager = ProviderManager()
