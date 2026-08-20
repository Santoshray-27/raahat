from typing import Optional, List, Dict, Any
from pydantic import BaseModel

class RAGQueryRequest(BaseModel):
    query: str
    context_filters: Optional[Dict[str, Any]] = None
    top_k: int = 3

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
