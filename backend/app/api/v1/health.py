from fastapi import APIRouter
from app.core.config import settings
from app.core.response import success_response
from app.core.telemetry import get_logs

router = APIRouter()

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
    return success_response(
        data={
            "active_mode": "MOCK" if settings.USE_MOCKS else "LIVE",
            "google_places": {
                "configured": bool(settings.GOOGLE_PLACES_API_KEY),
                "status": "OPERATIONAL" if settings.GOOGLE_PLACES_API_KEY else "DISABLED"
            },
            "google_routes": {
                "configured": bool(settings.GOOGLE_ROUTES_API_KEY),
                "status": "OPERATIONAL" if settings.GOOGLE_ROUTES_API_KEY else "DISABLED"
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
