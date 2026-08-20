from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from app.schemas.common import GeoPoint, ServiceProvider

class OfflinePackCreateRequest(BaseModel):
    region_name: str
    bounding_box: List[GeoPoint]  # [south_west, north_east]
    include_categories: List[str] = ["AMBULANCE", "POLICE", "MECHANIC", "PUNCTURE_REPAIR", "HOSPITAL"]

class OfflinePackManifest(BaseModel):
    pack_id: str
    region_name: str
    version: str
    created_at: str
    file_size_bytes: int
    sha256_checksum: str
    total_providers: int
    categories: List[str]

class OfflinePackData(BaseModel):
    manifest: OfflinePackManifest
    providers: List[ServiceProvider]
    emergency_contacts: Dict[str, str] = {
        "NATIONAL_EMERGENCY": "112",
        "POLICE": "100",
        "AMBULANCE": "102",
        "FIRE": "101",
        "ROAD_ACCIDENT_HELPLINE": "1033"
    }
