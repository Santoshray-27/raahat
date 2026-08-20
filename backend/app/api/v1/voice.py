from fastapi import APIRouter
from app.core.response import success_response
from app.schemas.voice import VoiceAssistRequest, VoiceAssistResponseData
from app.schemas.emergency import EmergencyRequest
from app.services.orchestrator import orchestrator

router = APIRouter()

@router.post("/voice/assist")
async def voice_assist(req: VoiceAssistRequest):
    # Sarvam / Voice processing hook
    transcript = req.transcript_text or "Puncture ho gaya hai, tyre badalna hai urgent"
    
    emergency_req = EmergencyRequest(
        user_query=transcript,
        location=req.location,
        language=req.language
    )
    
    triage_result = await orchestrator.process_emergency(emergency_req)
    
    data = VoiceAssistResponseData(
        transcript_recognized=transcript,
        language_detected=req.language,
        triage_result=triage_result,
        response_audio_base64=None
    )
    return success_response(data=data.model_dump())
