from typing import Optional, List
from pydantic import BaseModel, Field

class GeoPoint(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    accuracy_meters: Optional[float] = None
    altitude_meters: Optional[float] = None
    heading_degrees: Optional[float] = None
    speed_mps: Optional[float] = None

class ContactInfo(BaseModel):
    phone_primary: Optional[str] = None
    phone_secondary: Optional[str] = None
    whatsapp: Optional[str] = None
    emergency_shortcode: Optional[str] = None
    is_phone_verified: bool = False

class LocationAddress(BaseModel):
    formatted_address: Optional[str] = None
    street_name: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: str = "India"
    landmark: Optional[str] = None

class ServiceProvider(BaseModel):
    provider_id: str
    name: str
    service_types: List[str]
    location: GeoPoint
    address: LocationAddress
    contact: ContactInfo
    distance_km: float
    eta_minutes: int
    rating: Optional[float] = 4.5
    review_count: int = 12
    availability_status: str = "UNKNOWN"  # UNKNOWN unless explicitly verified!
    verification_status: str = "VERIFIED"
    recommendation_score: float = 0.95
    recommendation_reason: str = "Nearest verified provider suited for puncture repair"
    source: str = "GOOGLE_PLACES"
    is_cached: bool = False
    retrieved_at: Optional[str] = None
