from typing import List, Optional
from fastapi import APIRouter, Query
from app.core.response import success_response
from app.providers.manager import provider_manager
from app.services.ranking import service_ranker
from app.schemas.common import GeoPoint
from app.schemas.enums import ServiceType
from app.schemas.services import ServiceSearchRequest, ServicesNearbyResponseData

router = APIRouter()

@router.get("/services/nearby")
async def get_services_nearby(
    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180),
    radius_km: float = Query(10.0, ge=0.1, le=100.0),
    category: Optional[str] = None
):
    loc = GeoPoint(latitude=lat, longitude=lng)
    
    st_list = [ServiceType.MECHANIC, ServiceType.PUNCTURE_REPAIR, ServiceType.TOWING, ServiceType.HOSPITAL]
    if category:
        try:
            st_list = [ServiceType(category.upper())]
        except ValueError:
            pass

    providers, provider_source = await provider_manager.get_nearby_services(
        location=loc,
        service_types=st_list,
        radius_km=radius_km,
        limit=10
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
