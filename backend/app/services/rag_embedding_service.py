import math
import asyncio
import logging
from typing import List, Optional
import warnings

# Suppress the SDK deprecation warning to keep logs clean
warnings.filterwarnings('ignore', message='.*google.generativeai package has ended.*')

import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted, ServiceUnavailable, GoogleAPICallError
from app.core.config import settings

logger = logging.getLogger(__name__)

class RagEmbeddingError(Exception):
    pass

class RagEmbeddingService:
    """
    RAG Embedding Service.
    Wraps google-generativeai embed_content_async using Matryoshka Representation Learning (MRL).
    Target dimension is 1536 (truncating native 3072 from gemini-embedding-001).
    """
    
    MODEL = getattr(settings, "RAG_EMBEDDING_MODEL", "models/gemini-embedding-001")
    DIMENSION = getattr(settings, "RAG_EMBEDDING_DIMENSION", 1536)
    BATCH_SIZE = 5  # Strict constraint: 5-10 chunks max per batch
    MAX_RETRIES = 3
    RETRY_BASE_DELAY = 2.0  # Backoff: 2s -> 4s -> 8s

    def __init__(self):
        # We rely on gemini_service.py having already called genai.configure() 
        # via the init_gemini() module load if the key was present. 
        # But we can also ensure it here.
        if settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)

    @staticmethod
    def _l2_normalize(vector: List[float]) -> List[float]:
        """
        L2-normalize a vector. 
        Crucial for cosine similarity correctness when using MRL truncated embeddings (dim < 3072).
        """
        norm = math.sqrt(sum(x * x for x in vector))
        if norm == 0.0:
            return vector
        return [x / norm for x in vector]

    async def _call_with_retries(self, func, *args, **kwargs):
        delay = self.RETRY_BASE_DELAY
        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                # Enforce a 30-second timeout at the RPC layer if supported
                if "request_options" not in kwargs:
                    kwargs["request_options"] = {"timeout": 30.0}
                return await func(*args, **kwargs)
            except (ResourceExhausted, ServiceUnavailable) as e:
                if attempt == self.MAX_RETRIES:
                    logger.error(f"Gemini API failed after {self.MAX_RETRIES} attempts: {e}")
                    raise RagEmbeddingError(f"API Error (rate limited or unavailable): {e}")
                logger.warning(f"Gemini API rate limited/unavailable (attempt {attempt}/{self.MAX_RETRIES}), retrying in {delay}s...")
                await asyncio.sleep(delay)
                delay *= 2
            except GoogleAPICallError as e:
                logger.error(f"Gemini API call error: {e}")
                raise RagEmbeddingError(f"API Call Error: {e}")
            except Exception as e:
                logger.error(f"Gemini API unexpected error: {e}")
                raise RagEmbeddingError(f"Unexpected Error: {e}")

    async def embed_document(self, text: str, title: Optional[str] = None) -> List[float]:
        """Embeds a single chunk of knowledge for ingestion."""
        if not settings.GEMINI_API_KEY:
            raise RagEmbeddingError("GEMINI_API_KEY is not configured")

        kwargs = {
            "model": self.MODEL,
            "content": text,
            "task_type": "RETRIEVAL_DOCUMENT",
            "output_dimensionality": self.DIMENSION,
        }
        if title:
            kwargs["title"] = title

        resp = await self._call_with_retries(genai.embed_content_async, **kwargs)
        raw_vector = resp["embedding"]
        return self._l2_normalize(raw_vector)

    async def embed_query(self, text: str) -> List[float]:
        """Embeds a user query at runtime."""
        if not settings.GEMINI_API_KEY:
            raise RagEmbeddingError("GEMINI_API_KEY is not configured")

        resp = await self._call_with_retries(
            genai.embed_content_async,
            model=self.MODEL,
            content=text,
            task_type="RETRIEVAL_QUERY",
            output_dimensionality=self.DIMENSION,
        )
        raw_vector = resp["embedding"]
        return self._l2_normalize(raw_vector)

    async def embed_batch(self, texts: List[str], task_type: str = "RETRIEVAL_DOCUMENT") -> List[List[float]]:
        """
        Embeds a list of texts in batches up to BATCH_SIZE.
        Returns a list of vectors matching the order of input texts.
        """
        if not settings.GEMINI_API_KEY:
            raise RagEmbeddingError("GEMINI_API_KEY is not configured")
            
        if not texts:
            return []

        all_vectors = []
        for i in range(0, len(texts), self.BATCH_SIZE):
            batch = texts[i : i + self.BATCH_SIZE]
            
            resp = await self._call_with_retries(
                genai.embed_content_async,
                model=self.MODEL,
                content=batch,
                task_type=task_type,
                output_dimensionality=self.DIMENSION,
            )
            
            # genai.embed_content_async returns a dictionary where "embedding" is a list of lists 
            # for batch requests if content was an iterable.
            raw_vectors = resp["embedding"]
            for vec in raw_vectors:
                all_vectors.append(self._l2_normalize(vec))
                
        return all_vectors
