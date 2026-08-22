from typing import Optional
from pydantic import BaseModel
from app.schemas.common import GeoPoint
from app.schemas.emergency import EmergencyResponseData

class VoiceAssistRequest(BaseModel):
    audio_base64: Optional[str] = None
    transcript_text: Optional[str] = None
    location: Optional[GeoPoint] = None
    user_id: Optional[str] = None
    language: str = "hi-IN"

class VoiceAssistResponseData(BaseModel):
    transcript_recognized: str
    language_detected: str
    triage_result: EmergencyResponseData
    response_audio_base64: Optional[str] = None
