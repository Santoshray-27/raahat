from fastapi import APIRouter, Depends
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import get_optional_current_user
from app.schemas.users import UserProfile
from app.core.response import success_response
from app.schemas.emergency import EmergencyRequest
from app.services.orchestrator import orchestrator
import time
from app.core.config import settings
from app.core.telemetry import log_request

router = APIRouter()

@router.post("/emergency-assistance")
async def process_emergency_assistance(
    req: EmergencyRequest,
    db: AsyncSession = Depends(get_db),
    user: Optional[UserProfile] = Depends(get_optional_current_user)
):
    start_time = time.time()
    result = await orchestrator.process_emergency(req, db, user)
    latency = (time.time() - start_time) * 1000
    
    # Extract provider source from the first service if available, else fallback
    provider_source = "UNKNOWN"
    if result.services and len(result.services) > 0:
        provider_source = result.services[0].source
        
    log_request(
        endpoint="/api/v1/emergency-assistance",
        provider_source=provider_source,
        latency_ms=latency,
        results_count=len(result.services),
        mode="MOCK" if settings.USE_MOCKS else "LIVE"
    )
    
    return success_response(data=result.model_dump())
