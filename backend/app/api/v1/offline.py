import hashlib, json, uuid
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from app.core.response import success_response
from app.providers.manager import provider_manager
from app.schemas.enums import ServiceType
from app.schemas.common import GeoPoint
from app.schemas.offline import (
    OfflinePackCreateRequest, OfflinePackManifest, OfflinePackData
)

router = APIRouter()

# In-memory storage for generated offline packs
_OFFLINE_PACKS_STORE = {}

@router.post("/offline-packs")
async def create_offline_pack(req: OfflinePackCreateRequest):
    pack_id = f"pack_{req.region_name.lower().replace(' ', '_')}_{str(uuid.uuid4())[:6]}"
    
    # Center point of bounding box
    if req.bounding_box and len(req.bounding_box) >= 2:
        center_lat = (req.bounding_box[0].latitude + req.bounding_box[1].latitude) / 2
        center_lon = (req.bounding_box[0].longitude + req.bounding_box[1].longitude) / 2
    else:
        center_lat, center_lon = 22.7196, 75.8577
        
    center_loc = GeoPoint(latitude=center_lat, longitude=center_lon)
    
    st_list = [ServiceType.MECHANIC, ServiceType.PUNCTURE_REPAIR, ServiceType.TOWING, ServiceType.HOSPITAL, ServiceType.AMBULANCE]
    
    providers, _ = await provider_manager.get_nearby_services(
        location=center_loc,
        service_types=st_list,
        radius_km=25.0,
        limit=20
    )
    
    created_at = datetime.now(timezone.utc).isoformat()
    
    pack_content = {
        "pack_id": pack_id,
        "region_name": req.region_name,
        "created_at": created_at,
        "providers": [p.model_dump() for p in providers]
    }
    
    content_json = json.dumps(pack_content, sort_keys=True)
    sha256_hash = hashlib.sha256(content_json.encode("utf-8")).hexdigest()
    
    manifest = OfflinePackManifest(
        pack_id=pack_id,
        region_name=req.region_name,
        version="1.0.0",
        created_at=created_at,
        file_size_bytes=len(content_json.encode("utf-8")),
        sha256_checksum=sha256_hash,
        total_providers=len(providers),
        categories=req.include_categories
    )
    
    offline_pack_data = OfflinePackData(
        manifest=manifest,
        providers=providers
    )
    
    _OFFLINE_PACKS_STORE[pack_id] = offline_pack_data
    
    return success_response(data=offline_pack_data.model_dump())

@router.get("/offline-packs/{pack_id}")
async def get_offline_pack_manifest(pack_id: str):
    if pack_id not in _OFFLINE_PACKS_STORE:
        raise HTTPException(status_code=404, detail=f"Offline pack '{pack_id}' not found")
        
    return success_response(data=_OFFLINE_PACKS_STORE[pack_id].manifest.model_dump())

@router.get("/offline-packs/{pack_id}/download")
async def download_offline_pack(pack_id: str):
    if pack_id not in _OFFLINE_PACKS_STORE:
        raise HTTPException(status_code=404, detail=f"Offline pack '{pack_id}' not found")
        
    return JSONResponse(
        content=_OFFLINE_PACKS_STORE[pack_id].model_dump(),
        headers={
            "Content-Disposition": f"attachment; filename=raahat_offline_{pack_id}.json"
        }
    )
