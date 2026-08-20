from fastapi import APIRouter
from app.core.response import success_response
from app.schemas.emergency import EmergencyRequest
from app.services.orchestrator import orchestrator

router = APIRouter()

@router.post("/emergency-assistance")
async def process_emergency_assistance(req: EmergencyRequest):
    result = await orchestrator.process_emergency(req)
    return success_response(data=result.model_dump())
