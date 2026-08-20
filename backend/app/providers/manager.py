from typing import List, Tuple
from app.core.config import settings
from app.core.logging import logger
from app.providers.google_places import GooglePlacesProvider
from app.providers.google_routes import GoogleRoutesProvider
from app.providers.osm_overpass import OSMOverpassProvider
from app.providers.osrm import OSRMRoutingProvider
from app.providers.mock_provider import MockPlacesProvider, MockRoutingProvider
from app.schemas.common import GeoPoint, ServiceProvider
from app.schemas.enums import ServiceType
from app.schemas.routes import RoutePlanResponseData

class ProviderManager:
    def __init__(self):
        self.google_places = GooglePlacesProvider()
        self.google_routes = GoogleRoutesProvider()
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
        # 1. Check if USE_MOCKS is explicitly enabled
        if settings.USE_MOCKS:
            logger.info("ProviderManager: Using MockPlacesProvider (USE_MOCKS=True)")
            res = await self.mock_places.search_nearby(location, service_types, radius_km, limit)
            return res, "mock"

        # 2. Try Google Places
        if settings.GOOGLE_PLACES_API_KEY:
            try:
                logger.info("ProviderManager: Attempting Google Places API...")
                res = await self.google_places.search_nearby(location, service_types, radius_km, limit)
                if res:
                    return res, "google_places"
            except Exception as e:
                logger.warning(f"Google Places API failed: {e}. Falling back to OSM Overpass...")

        # 3. Fallback to OpenStreetMap Overpass
        try:
            logger.info("ProviderManager: Attempting OSM Overpass API...")
            res = await self.osm_overpass.search_nearby(location, service_types, radius_km, limit)
            if res:
                return res, "osm_overpass"
        except Exception as e:
            logger.warning(f"OSM Overpass API failed: {e}. Falling back to Mock Provider...")

        # 4. Final Fallback to Mock
        res = await self.mock_places.search_nearby(location, service_types, radius_km, limit)
        return res, "mock_fallback"

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

        # 2. Try Google Routes
        if settings.GOOGLE_ROUTES_API_KEY:
            try:
                logger.info("ProviderManager: Attempting Google Routes API...")
                return await self.google_routes.plan_route(origin, destination, avoid_highways, avoid_tolls)
            except Exception as e:
                logger.warning(f"Google Routes API failed: {e}. Falling back to OSRM...")

        # 3. Fallback to OSRM
        try:
            logger.info("ProviderManager: Attempting OSRM Routing API...")
            return await self.osrm_routing.plan_route(origin, destination, avoid_highways, avoid_tolls)
        except Exception as e:
            logger.warning(f"OSRM Routing failed: {e}. Falling back to Mock Routing...")

        # 4. Final Fallback to Mock
        return await self.mock_routing.plan_route(origin, destination, avoid_highways, avoid_tolls)

provider_manager = ProviderManager()
