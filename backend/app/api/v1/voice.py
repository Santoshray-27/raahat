from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from app.core.response import success_response
from app.schemas.voice import VoiceAssistRequest, VoiceAssistResponseData
from app.schemas.emergency import EmergencyRequest
from app.schemas.common import GeoPoint
from app.services.orchestrator import orchestrator
from app.services.location_service import location_service

router = APIRouter()

class LocationUpdateRequest(BaseModel):
    user_id: str
    latitude: float
    longitude: float
    accuracy_meters: Optional[float] = None

@router.post("/location/update")
async def update_location(req: LocationUpdateRequest):
    location_service.update_location(
        req.user_id, 
        GeoPoint(latitude=req.latitude, longitude=req.longitude)
    )
    return success_response(data={"status": "Location updated successfully"})

@router.post("/voice/assist")
async def voice_assist(req: VoiceAssistRequest):
    # Sarvam / Voice processing hook
    transcript = req.transcript_text or "Puncture ho gaya hai, tyre badalna hai urgent"
    
    # Resolve location from request or fallback to LocationService via user_id
    resolved_location = req.location
    if not resolved_location and req.user_id:
        resolved_location = location_service.get_latest_location(req.user_id)
        
    emergency_req = EmergencyRequest(
        user_query=transcript,
        location=resolved_location,
        language=req.language,
        user_id=req.user_id or "anonymous"
    )
    
    triage_result = await orchestrator.process_emergency(emergency_req)
    
    data = VoiceAssistResponseData(
        transcript_recognized=transcript,
        language_detected=req.language,
        triage_result=triage_result,
        response_audio_base64=None
    )
    return success_response(data=data.model_dump())
