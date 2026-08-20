import httpx
from fastapi import APIRouter
from app.core.config import settings
from app.core.response import success_response
from app.schemas.rag import RAGQueryRequest, RAGQueryResponseData, RAGDocumentChunk

router = APIRouter()

@router.post("/rag/query")
async def query_rag(req: RAGQueryRequest):
    # Satwik Integration Point: If Satwik's AI Service is available at AI_SERVICE_URL, pass-through
    ai_url = getattr(settings, "AI_SERVICE_URL", None)
    if ai_url:
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                resp = await client.post(f"{ai_url}/rag/query", json=req.model_dump())
                if resp.status_code == 200:
                    return resp.json()
        except Exception:
            pass

    # Clean fallback stub when AI service is not running
    chunks = [
        RAGDocumentChunk(
            chunk_id="chk_first_aid_01",
            title="Roadside Emergency First Aid Guidelines (SW-17 Manual)",
            content="In case of vehicle accident with casualties, dial 112 immediately. Apply direct firm pressure over bleeding wounds with clean cloth.",
            score=0.94,
            source="RAAHAT Emergency SOP Manual v1"
        ),
        RAGDocumentChunk(
            chunk_id="chk_puncture_02",
            title="Expressway Vehicle Breakdowns & Safety Protocol",
            content="Pull over to left shoulder, engage hazard lights, remain inside vehicle on expressways, and alert mobile roadside repair units.",
            score=0.88,
            source="National Highway Safety Manual"
        )
    ]
    
    data = RAGQueryResponseData(
        query=req.query,
        answer=f"RAAHAT RAG Assistance: For '{req.query}', follow standard safety protocols. Park safely, activate hazard lights, and contact nearest verified provider.",
        chunks=chunks[:req.top_k],
        source_attribution=["RAAHAT Emergency SOP Manual v1", "National Highway Safety Manual"]
    )
    return success_response(data=data.model_dump())
