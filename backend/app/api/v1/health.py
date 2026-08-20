import httpx
import time
from fastapi import APIRouter
from app.core.config import settings
from app.core.response import success_response
from app.core.telemetry import get_logs
from app.core.circuit_breaker import google_circuit_breaker

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
async def get_health():
    return success_response(
        data={
            "status": "healthy",
            "service": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "mode": "mock" if settings.USE_MOCKS else "live",
            "auth_disabled": settings.AUTH_DISABLED
        }
    )

@router.get("/providers/status")
async def get_providers_status():
    exhausted, expiry_time = google_circuit_breaker.is_exhausted()
    if exhausted:
        gp_status = f"QUOTA_EXHAUSTED (skipping until {expiry_time})"
        gr_status = f"QUOTA_EXHAUSTED (skipping until {expiry_time})"
    else:
        gp_status = "OPERATIONAL" if settings.GOOGLE_PLACES_API_KEY else "DISABLED"
        gr_status = "OPERATIONAL" if settings.GOOGLE_ROUTES_API_KEY else "DISABLED"

    return success_response(
        data={
            "active_mode": "MOCK" if settings.USE_MOCKS else "LIVE",
            "google_places": {
                "configured": bool(settings.GOOGLE_PLACES_API_KEY),
                "status": gp_status
            },
            "google_routes": {
                "configured": bool(settings.GOOGLE_ROUTES_API_KEY),
                "status": gr_status
            },
            "geoapify": {
                "configured": bool(settings.GEOAPIFY_API_KEY),
                "status": await _check_geoapify_status()
            },
            "fallback_providers": ["OSM_OVERPASS", "OSRM"],
            "gemini_ai": {
                "configured": bool(settings.GEMINI_API_KEY),
                "model": "gemini-1.5-flash" if settings.GEMINI_API_KEY else "rule-fallback"
            }
        }
    )

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
