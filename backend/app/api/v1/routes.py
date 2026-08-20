from fastapi import APIRouter
from app.core.response import success_response
from app.providers.manager import provider_manager
from app.schemas.routes import RoutePlanRequest
from app.schemas.enums import ServiceType

router = APIRouter()

@router.post("/routes/plan")
async def plan_route(req: RoutePlanRequest):
    route_data = await provider_manager.plan_route(
        origin=req.origin,
        destination=req.destination,
        avoid_highways=req.avoid_highways,
        avoid_tolls=req.avoid_tolls
    )
    
    # Query emergency services along route corridor
    corridor_services, _ = await provider_manager.get_nearby_services(
        location=req.origin,
        service_types=[ServiceType.HOSPITAL, ServiceType.TOWING, ServiceType.PUNCTURE_REPAIR],
        radius_km=15.0,
        limit=4
    )
    route_data.nearby_emergency_services = corridor_services
    
    return success_response(data=route_data.model_dump())
