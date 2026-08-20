from fastapi import APIRouter
from app.core.config import settings
from app.core.response import success_response

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
