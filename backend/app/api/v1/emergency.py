from fastapi import APIRouter
from app.core.response import success_response
from app.schemas.emergency import EmergencyRequest
from app.services.orchestrator import orchestrator
import time
from app.core.config import settings
from app.core.telemetry import log_request

router = APIRouter()

@router.post("/emergency-assistance")
async def process_emergency_assistance(req: EmergencyRequest):
    start_time = time.time()
    result = await orchestrator.process_emergency(req)
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
