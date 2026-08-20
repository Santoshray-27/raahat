from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from app.schemas.enums import IncidentCategory, SeverityLevel, ServiceType
from app.schemas.common import GeoPoint, ServiceProvider

class VehicleInfo(BaseModel):
    vehicle_type: Optional[str] = "FOUR_WHEELER"
    make: Optional[str] = None
    model: Optional[str] = None
    fuel_type: Optional[str] = None

class EmergencyRequest(BaseModel):
    user_query: str = Field(..., min_length=2, description="Natural language description of emergency in English, Hindi, or Hinglish")
    location: GeoPoint
    user_id: Optional[str] = "anonymous"
    language: Optional[str] = "en"
    vehicle_info: Optional[VehicleInfo] = None

class IncidentDetails(BaseModel):
    incident_id: str
    category: IncidentCategory
    severity: SeverityLevel
    confidence: float
    description_summary: str
    requires_immediate_services: List[ServiceType]
    is_life_threatening: bool = False

class GuidanceStep(BaseModel):
    step_number: int
    title: str
    instruction: str
    caution: Optional[str] = None
    is_critical: bool = False

class EmergencyGuidance(BaseModel):
    summary: str
    immediate_do_not_do: List[str]
    steps: List[GuidanceStep]
    first_aid_included: bool = False

class RecommendedAction(BaseModel):
    action_id: str
    action_type: str  # CALL_POLICE, CALL_AMBULANCE, CALL_TOWING, NAVIGATE, SELF_REPAIR
    label: str
    target_contact: Optional[str] = None
    target_payload: Optional[Dict[str, Any]] = None
    priority: int = 1

class AIAnalysisMeta(BaseModel):
    classifier_used: str = "deterministic_keyword"
    confidence_score: float = 0.95
    model_version: str = "v1.0"

class EmergencyResponseData(BaseModel):
    incident: IncidentDetails
    guidance: EmergencyGuidance
    services: List[ServiceProvider]
    recommended_actions: List[RecommendedAction]
    ai: AIAnalysisMeta
    limitations: Optional[List[str]] = None
