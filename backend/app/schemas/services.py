from typing import Optional, List
from pydantic import BaseModel, Field
from app.schemas.common import GeoPoint, ServiceProvider
from app.schemas.enums import ServiceType

class ServiceSearchRequest(BaseModel):
    location: GeoPoint
    service_types: List[ServiceType]
    radius_km: float = Field(10.0, ge=0.1, le=100.0)
    limit: int = Field(10, ge=1, le=50)

class ServicesNearbyResponseData(BaseModel):
    center_location: GeoPoint
    radius_km: float
    total_found: int
    services: List[ServiceProvider]
    provider_source: str = "mock"  # google_places | osm_overpass | mock
