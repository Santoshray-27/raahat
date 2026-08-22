from typing import List, Optional
from fastapi import APIRouter, Query
from app.core.response import success_response
from app.providers.manager import provider_manager
from app.services.ranking import service_ranker
from app.schemas.common import GeoPoint
from app.schemas.enums import ServiceType
from app.schemas.services import ServiceSearchRequest, ServicesNearbyResponseData
import time
from app.core.config import settings
from app.core.telemetry import log_request

router = APIRouter()

@router.get("/services/nearby")
async def get_services_nearby(
    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180),
    radius_km: float = Query(10.0, ge=0.1, le=100.0),
    category: Optional[str] = None,
    limit: int = Query(10, ge=1, le=50)
):
    start_time = time.time()
    loc = GeoPoint(latitude=lat, longitude=lng)
    
    st_list = [ServiceType.MECHANIC, ServiceType.PUNCTURE_REPAIR, ServiceType.TOWING, ServiceType.HOSPITAL]
    if category:
        cat_str = category.upper()
        alias_map = {
            "FUEL": ServiceType.FUEL_DELIVERY,
            "FUEL_STATION": ServiceType.FUEL_DELIVERY,
            "FUEL_DELIVERY": ServiceType.FUEL_DELIVERY,
            "FIRE": ServiceType.FIRE_BRIGADE,
            "FIRE_STATION": ServiceType.FIRE_BRIGADE,
            "FIRE_BRIGADE": ServiceType.FIRE_BRIGADE,
            "PUNCTURE": ServiceType.PUNCTURE_REPAIR,
            "PUNCTURE_REPAIR": ServiceType.PUNCTURE_REPAIR,
            "POLICE": ServiceType.POLICE,
            "AMBULANCE": ServiceType.AMBULANCE,
            "HOSPITAL": ServiceType.HOSPITAL,
            "TOWING": ServiceType.TOWING,
            "MECHANIC": ServiceType.MECHANIC,
        }
        if cat_str in alias_map:
            st_list = [alias_map[cat_str]]
        else:
            try:
                st_list = [ServiceType(cat_str)]
            except ValueError:
                pass

    providers, provider_source = await provider_manager.get_nearby_services(
        location=loc,
        service_types=st_list,
        radius_km=radius_km,
        limit=limit
    )
    
    latency = (time.time() - start_time) * 1000
    log_request(
        endpoint="/api/v1/services/nearby", 
        provider_source=provider_source, 
        latency_ms=latency, 
        results_count=len(providers), 
        mode="MOCK" if settings.USE_MOCKS else "LIVE"
    )

    data = ServicesNearbyResponseData(
        center_location=loc,
        radius_km=radius_km,
        total_found=len(providers),
        services=providers,
        provider_source=provider_source
    )
    return success_response(data=data.model_dump())

@router.post("/services/search")
async def search_services(req: ServiceSearchRequest):
    providers, provider_source = await provider_manager.get_nearby_services(
        location=req.location,
        service_types=req.service_types,
        radius_km=req.radius_km,
        limit=req.limit
    )
    
    data = ServicesNearbyResponseData(
        center_location=req.location,
        radius_km=req.radius_km,
        total_found=len(providers),
        services=providers,
        provider_source=provider_source
    )
    return success_response(data=data.model_dump())
