from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# M3 RAG Query Schemas
# ---------------------------------------------------------------------------

class RAGQueryRequest(BaseModel):
    query: str
    top_k: int = Field(default=5, ge=1, le=20)
    min_score: float = Field(default=0.5, ge=0.0, le=1.0)
    # Emergency metadata filters (optional, must exist in corpus)
    domain_id: Optional[str] = None
    india_specific: Optional[bool] = None


class RAGRetrievedChunk(BaseModel):
    """A single chunk returned from pgvector similarity search."""
    chunk_id: str
    document_id: str
    chunk_index: int
    content: str
    similarity_score: float
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RAGQueryResponse(BaseModel):
    query: str
    results: List[RAGRetrievedChunk]
    results_count: int
    rag_used: bool = True


# ---------------------------------------------------------------------------
# Legacy schemas — kept for backward compatibility with any clients using
# the old /rag/query stub. New clients should use RAGQueryResponse.
# ---------------------------------------------------------------------------

class RAGDocumentChunk(BaseModel):
    chunk_id: str
    title: str
    content: str
    score: float
    source: str


class RAGQueryResponseData(BaseModel):
    query: str
    answer: str
    chunks: List[RAGDocumentChunk]
    source_attribution: List[str]
    processing_time_ms: float = 45.0
