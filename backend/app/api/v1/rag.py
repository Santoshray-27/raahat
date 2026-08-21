import time
import logging
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.response import success_response
from app.schemas.rag import RAGQueryRequest, RAGQueryResponse, RAGRetrievedChunk

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/rag/query")
async def query_rag(
    req: RAGQueryRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    M3-A: Real RAG query endpoint using pgvector cosine similarity.

    Embeds the query via RagEmbeddingService (RETRIEVAL_QUERY task type),
    runs similarity search through RagRepository, and returns structured chunks.

    Graceful fallback: returns empty results if embedding or DB fails.
    """
    start = time.time()

    try:
        from app.services.rag_embedding_service import RagEmbeddingService, RagEmbeddingError
        from app.repositories.rag_repository import RagRepository

        embedding_service = RagEmbeddingService()
        query_embedding = await embedding_service.embed_query(req.query)

        # Optionally build a metadata filter from the request
        metadata_filter = None
        filter_parts = {}
        if req.domain_id:
            filter_parts["domain_id"] = req.domain_id
        if req.india_specific is not None:
            filter_parts["india_specific"] = req.india_specific
        if filter_parts:
            metadata_filter = filter_parts

        rag_repo = RagRepository(db)
        raw_results = await rag_repo.similarity_search(
            query_embedding=query_embedding,
            top_k=req.top_k,
            min_score=req.min_score,
            metadata_filter=metadata_filter,
        )

        results = [
            RAGRetrievedChunk(
                chunk_id=str(chunk.id),
                document_id=str(chunk.document_id),
                chunk_index=chunk.chunk_index,
                content=chunk.content,
                similarity_score=round(float(score), 6),
                metadata=chunk.metadata_ or {},
            )
            for chunk, score in raw_results
        ]

        elapsed_ms = round((time.time() - start) * 1000, 2)
        logger.info(
            f"RAG query: '{req.query[:60]}...' → {len(results)} results "
            f"in {elapsed_ms}ms"
        )

        response = RAGQueryResponse(
            query=req.query,
            results=results,
            results_count=len(results),
            rag_used=True,
        )
        return success_response(data=response.model_dump())

    except Exception as e:
        # Graceful degradation: log and return empty results
        logger.warning(f"RAG query failed, returning empty results: {e}", exc_info=False)
        response = RAGQueryResponse(
            query=req.query,
            results=[],
            results_count=0,
            rag_used=False,
        )
        return success_response(data=response.model_dump())
