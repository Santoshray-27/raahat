import httpx
import time
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.response import success_response, error_response
from app.core.telemetry import get_logs
from app.core.circuit_breaker import google_circuit_breaker
from app.core.database import get_db
from app.repositories.health_repository import HealthRepository

router = APIRouter()

_geoapify_cache = {"status": "NOT_CONFIGURED", "timestamp": 0}

async def _check_geoapify_status():
    if not settings.GEOAPIFY_API_KEY:
        return "NOT_CONFIGURED"
        
    now = time.time()
    if now - _geoapify_cache["timestamp"] < 60:
        return _geoapify_cache["status"]
        
    try:
        url = "https://api.geoapify.com/v2/places"
        params = {"categories": "healthcare.hospital", "filter": "circle:0,0,100", "limit": 1, "apiKey": settings.GEOAPIFY_API_KEY}
        async with httpx.AsyncClient(timeout=5.0) as client:
            res = await client.get(url, params=params)
            if res.status_code == 200:
                _geoapify_cache["status"] = "OPERATIONAL"
            elif res.status_code in [401, 403, 429]:
                _geoapify_cache["status"] = f"ERROR_{res.status_code}"
            else:
                _geoapify_cache["status"] = "ERROR"
    except Exception:
        _geoapify_cache["status"] = "ERROR"
        
    _geoapify_cache["timestamp"] = now
    return _geoapify_cache["status"]

@router.get("/health")
async def get_health(db: AsyncSession = Depends(get_db)):
    health_repo = HealthRepository(db)
    is_db_healthy = await health_repo.check_database_health()

    return success_response(
        data={
            "status": "healthy" if is_db_healthy else "degraded",
            "service": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "mode": "mock" if settings.USE_MOCKS else "live",
            "auth": "disabled" if settings.AUTH_DISABLED else "enabled",
            "database": "connected" if is_db_healthy else "disconnected"
        }
    )

@router.get("/providers/status")
async def get_providers_status():
    geo_status = await _check_geoapify_status()
    from app.services.gemini_service import gemini_enhancer
    gemini_model_name = gemini_enhancer.get_active_model()
    
    data = {
        "active_mode": "MOCK" if settings.USE_MOCKS else "LIVE",
        "primary_places_provider": "GEOAPIFY",
        "primary_routing_provider": "GEOAPIFY",
        "geoapify": {
            "configured": bool(settings.GEOAPIFY_API_KEY),
            "status": geo_status
        },
        "fallback_providers": ["OSM_OVERPASS", "OSRM", "CURATED"],
        "gemini_ai": {
            "configured": bool(settings.GEMINI_API_KEY),
            "model": gemini_model_name
        }
    }
    return success_response(data=data)

@router.get("/diagnostics")
async def get_diagnostics():
    recent = get_logs()
    return success_response(
        data={
            "mode": "MOCK" if settings.USE_MOCKS else "LIVE",
            "total_queries_logged": len(recent),
            "recent_call_history": recent
        }
    )
