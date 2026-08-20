from abc import ABC, abstractmethod
from typing import List, Optional
from app.schemas.common import GeoPoint, ServiceProvider
from app.schemas.enums import ServiceType
from app.schemas.routes import RoutePlanResponseData

class BasePlacesProvider(ABC):
    @abstractmethod
    async def search_nearby(
        self,
        location: GeoPoint,
        service_types: List[ServiceType],
        radius_km: float = 10.0,
        limit: int = 10
    ) -> List[ServiceProvider]:
        pass

class BaseRoutingProvider(ABC):
    @abstractmethod
    async def plan_route(
        self,
        origin: GeoPoint,
        destination: GeoPoint,
        avoid_highways: bool = False,
        avoid_tolls: bool = False
    ) -> RoutePlanResponseData:
        pass
