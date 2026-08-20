from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, model_validator
from app.schemas.common import GeoPoint, ServiceProvider

class OfflinePackCreateRequest(BaseModel):
    region_name: str = "Route Corridor"
    bounding_box: Optional[List[GeoPoint]] = None
    route_id: Optional[str] = None
    include_categories: List[str] = ["AMBULANCE", "POLICE", "MECHANIC", "PUNCTURE_REPAIR", "HOSPITAL"]

    @model_validator(mode="before")
    def validate_bounding_box(cls, values):
        bb = values.get("bounding_box")
        route_id = values.get("route_id")
        
        # Scenario C: omitted when route_id is provided
        if not bb and route_id:
            # We'll use dummy coords for the route corridor or default
            values["bounding_box"] = [{"latitude": 22.7196, "longitude": 75.8577}, {"latitude": 23.2599, "longitude": 77.4126}]
            return values
            
        if not bb:
            raise ValueError("bounding_box is required if route_id is not provided")
            
        # Scenario A: dict form
        if isinstance(bb, dict):
            if "min_lat" in bb and "min_lng" in bb and "max_lat" in bb and "max_lng" in bb:
                values["bounding_box"] = [
                    {"latitude": bb["min_lat"], "longitude": bb["min_lng"]},
                    {"latitude": bb["max_lat"], "longitude": bb["max_lng"]}
                ]
            else:
                raise ValueError("bounding_box dict must contain min_lat, min_lng, max_lat, max_lng")
                
        # Scenario B: list form (already validated by Pydantic down the line if it's a list)
        elif isinstance(bb, list):
            if len(bb) < 2:
                raise ValueError("bounding_box list must have at least 2 coordinate objects")
        else:
            raise ValueError("bounding_box must be a dict or a list")
            
        return values

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
