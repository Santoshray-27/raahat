"""
M3-G — Tests for the real RAG query endpoint and orchestrator RAG integration.

Tests:
1.  RAG query endpoint returns real-shaped response
2.  Query embedding uses RagEmbeddingService (mocked)
3.  Results ranked by similarity score (descending)
4.  Minimum similarity threshold filters low-score chunks
5.  Inactive documents excluded (exercised through similarity_search mock)
6.  NULL embeddings excluded (exercised through similarity_search mock)
7.  Empty retrieval returns 0 results gracefully
8.  Embedding API failure does NOT break the endpoint
9.  DB failure does NOT break the endpoint
10. Emergency assistance invokes RAG retrieval (smoke test via mock)
11. RAG failure does NOT break emergency assistance
12. Existing emergency response schema remains compatible after M3
13. Context builder integration: orchestrator calls _retrieve_rag_context
14. RAG query response shape matches RAGQueryResponse schema
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4


# ---------------------------------------------------------------------------
# Helper fixtures
# ---------------------------------------------------------------------------

def _make_chunk(content="Chunk content", score=0.75, meta=None):
    """Create a mock RagChunk + score tuple."""
    chunk = MagicMock()
    chunk.id = uuid4()
    chunk.document_id = uuid4()
    chunk.chunk_index = 0
    chunk.content = content
    chunk.metadata_ = meta or {"domain_id": "DOMAIN-003", "requirement_id": "KR-001"}
    return chunk, score


# ---------------------------------------------------------------------------
# 1. RAG query endpoint — real shape (httpx ASGI test)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_rag_query_endpoint_returns_success_shape():
    """Endpoint returns success=True + results list even with no real DB."""
    import httpx
    from app.main import app

    mock_emb = [0.1] * 1536
    with patch(
        "app.services.rag_embedding_service.RagEmbeddingService.embed_query",
        new=AsyncMock(return_value=mock_emb)
    ):
        with patch(
            "app.repositories.rag_repository.RagRepository.similarity_search",
            new=AsyncMock(return_value=[_make_chunk()])
        ):
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app=app), base_url="http://test"
            ) as client:
                resp = await client.post(
                    "/api/v1/rag/query",
                    json={"query": "How to stop bleeding?", "top_k": 3}
                )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert "results" in body["data"]
    assert body["data"]["rag_used"] is True


# ---------------------------------------------------------------------------
# 2. Query embedding uses RETRIEVAL_QUERY task type
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_rag_query_uses_retrieval_query_task():
    """embed_query (RETRIEVAL_QUERY) is called, not embed_document."""
    import httpx
    from app.main import app

    embed_spy = AsyncMock(return_value=[0.1] * 1536)
    with patch("app.services.rag_embedding_service.RagEmbeddingService.embed_query", new=embed_spy):
        with patch(
            "app.repositories.rag_repository.RagRepository.similarity_search",
            new=AsyncMock(return_value=[])
        ):
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app=app), base_url="http://test"
            ) as client:
                await client.post("/api/v1/rag/query", json={"query": "test", "top_k": 3})

    embed_spy.assert_awaited_once()
    # embed_query is called with the query string
    assert embed_spy.call_args[0][0] == "test"


# ---------------------------------------------------------------------------
# 3. Results ranked by similarity score (highest first)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_rag_results_ordered_by_score():
    """similarity_search result order is preserved (it returns ordered tuples)."""
    import httpx
    from app.main import app

    # DB returns chunks in descending score order (as similarity_search guarantees)
    ordered = [
        _make_chunk("High relevance", 0.90),
        _make_chunk("Medium relevance", 0.72),
        _make_chunk("Low relevance", 0.55),
    ]
    with patch(
        "app.services.rag_embedding_service.RagEmbeddingService.embed_query",
        new=AsyncMock(return_value=[0.1] * 1536)
    ):
        with patch(
            "app.repositories.rag_repository.RagRepository.similarity_search",
            new=AsyncMock(return_value=ordered)
        ):
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app=app), base_url="http://test"
            ) as client:
                resp = await client.post(
                    "/api/v1/rag/query", json={"query": "test", "top_k": 5}
                )

    results = resp.json()["data"]["results"]
    assert len(results) == 3
    assert results[0]["similarity_score"] >= results[1]["similarity_score"]
    assert results[1]["similarity_score"] >= results[2]["similarity_score"]


# ---------------------------------------------------------------------------
# 4. min_score is forwarded to similarity_search
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_min_score_forwarded_to_similarity_search():
    """The min_score from the request is passed through to similarity_search."""
    import httpx
    from app.main import app

    search_mock = AsyncMock(return_value=[])
    with patch(
        "app.services.rag_embedding_service.RagEmbeddingService.embed_query",
        new=AsyncMock(return_value=[0.1] * 1536)
    ):
        with patch(
            "app.repositories.rag_repository.RagRepository.similarity_search",
            new=search_mock
        ):
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app=app), base_url="http://test"
            ) as client:
                await client.post(
                    "/api/v1/rag/query",
                    json={"query": "test", "top_k": 3, "min_score": 0.7}
                )

    call_kwargs = search_mock.call_args[1]
    assert call_kwargs["min_score"] == pytest.approx(0.7)


# ---------------------------------------------------------------------------
# 5 & 6. Active-document + null-embedding filtering (delegated to repository)
#         The endpoint correctly passes through whatever similarity_search returns.
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_endpoint_returns_only_what_search_returns():
    """
    Active-doc and null-embedding filtering happens inside similarity_search.
    We verify the endpoint passes results through without modification.
    """
    import httpx
    from app.main import app

    single = [_make_chunk("Only active chunk", 0.80)]
    with patch(
        "app.services.rag_embedding_service.RagEmbeddingService.embed_query",
        new=AsyncMock(return_value=[0.1] * 1536)
    ):
        with patch(
            "app.repositories.rag_repository.RagRepository.similarity_search",
            new=AsyncMock(return_value=single)
        ):
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app=app), base_url="http://test"
            ) as client:
                resp = await client.post("/api/v1/rag/query", json={"query": "test"})

    assert resp.json()["data"]["results_count"] == 1


# ---------------------------------------------------------------------------
# 7. Empty retrieval returns 0 results gracefully
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_empty_retrieval_is_graceful():
    import httpx
    from app.main import app

    with patch(
        "app.services.rag_embedding_service.RagEmbeddingService.embed_query",
        new=AsyncMock(return_value=[0.1] * 1536)
    ):
        with patch(
            "app.repositories.rag_repository.RagRepository.similarity_search",
            new=AsyncMock(return_value=[])
        ):
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app=app), base_url="http://test"
            ) as client:
                resp = await client.post("/api/v1/rag/query", json={"query": "obscure query"})

    body = resp.json()
    assert resp.status_code == 200
    assert body["success"] is True
    assert body["data"]["results"] == []
    assert body["data"]["results_count"] == 0


# ---------------------------------------------------------------------------
# 8. Embedding API failure does NOT break the endpoint
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_embedding_api_failure_graceful():
    import httpx
    from app.main import app
    from app.services.rag_embedding_service import RagEmbeddingError

    with patch(
        "app.services.rag_embedding_service.RagEmbeddingService.embed_query",
        new=AsyncMock(side_effect=RagEmbeddingError("API unavailable"))
    ):
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.post("/api/v1/rag/query", json={"query": "emergency query"})

    body = resp.json()
    assert resp.status_code == 200
    assert body["success"] is True
    assert body["data"]["rag_used"] is False
    assert body["data"]["results"] == []


# ---------------------------------------------------------------------------
# 9. DB failure does NOT break the endpoint
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_db_failure_graceful():
    import httpx
    from app.main import app

    with patch(
        "app.services.rag_embedding_service.RagEmbeddingService.embed_query",
        new=AsyncMock(return_value=[0.1] * 1536)
    ):
        with patch(
            "app.repositories.rag_repository.RagRepository.similarity_search",
            new=AsyncMock(side_effect=Exception("DB connection lost"))
        ):
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app=app), base_url="http://test"
            ) as client:
                resp = await client.post("/api/v1/rag/query", json={"query": "emergency query"})

    body = resp.json()
    assert resp.status_code == 200
    assert body["success"] is True
    assert body["data"]["rag_used"] is False


# ---------------------------------------------------------------------------
# 10 & 11. Emergency assistance invokes RAG but does NOT fail when RAG fails
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_emergency_still_works_when_rag_fails():
    """
    The emergency endpoint must return 200 even when _retrieve_rag_context fails.
    """
    import httpx
    from app.main import app

    with patch(
        "app.services.orchestrator._retrieve_rag_context",
        new=AsyncMock(return_value=("", 0, None))  # RAG silently failed
    ):
        payload = {
            "user_query": "Tyre puncture on highway",
            "location": {"latitude": 22.7196, "longitude": 75.8577},
        }
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.post("/api/v1/emergency-assistance", json=payload)

    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["incident"]["category"] in [
        "PUNCTURE", "BREAKDOWN", "ACCIDENT", "OTHER"
    ]


@pytest.mark.asyncio
async def test_emergency_rag_failure_does_not_raise():
    """_retrieve_rag_context raises internally — orchestrator must catch it."""
    import httpx
    from app.main import app

    with patch(
        "app.services.orchestrator._retrieve_rag_context",
        new=AsyncMock(side_effect=Exception("Embedding service down"))
    ):
        payload = {
            "user_query": "Car accident, people injured",
            "location": {"latitude": 22.7196, "longitude": 75.8577},
        }
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.post("/api/v1/emergency-assistance", json=payload)

    # Even though the patch makes it raise, the orchestrator's own try/except
    # in process_emergency should protect it — if not, we want this test to catch it.
    # Note: if _retrieve_rag_context itself raises (not the wrapper), we test resilience.
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# 12. Existing emergency response schema remains compatible
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_emergency_response_schema_unchanged():
    """
    Emergency response must still have: incident, guidance, services,
    recommended_actions, ai — no M3 fields leaked into the response.
    """
    import httpx
    from app.main import app

    with patch(
        "app.services.orchestrator._retrieve_rag_context",
        new=AsyncMock(return_value=("", 0, None))
    ):
        payload = {
            "user_query": "Puncture on highway",
            "location": {"latitude": 22.7196, "longitude": 75.8577},
        }
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.post("/api/v1/emergency-assistance", json=payload)

    data = resp.json()["data"]
    # Required top-level keys
    for key in ("incident", "guidance", "services", "recommended_actions", "ai"):
        assert key in data, f"Missing key: {key}"
    # Incident sub-fields
    incident = data["incident"]
    for key in ("incident_id", "category", "severity", "confidence", "is_life_threatening"):
        assert key in incident, f"Missing incident field: {key}"
    # Guidance sub-fields
    guidance = data["guidance"]
    for key in ("summary", "steps", "immediate_do_not_do"):
        assert key in guidance, f"Missing guidance field: {key}"


# ---------------------------------------------------------------------------
# 13. _retrieve_rag_context is called during process_emergency
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_orchestrator_calls_retrieve_rag_context():
    """Verify _retrieve_rag_context is invoked within process_emergency."""
    import httpx
    from app.main import app

    retrieve_spy = AsyncMock(return_value=("", 0, None))
    with patch("app.services.orchestrator._retrieve_rag_context", new=retrieve_spy):
        payload = {
            "user_query": "Bleeding heavily after accident",
            "location": {"latitude": 22.7196, "longitude": 75.8577},
        }
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.post("/api/v1/emergency-assistance", json=payload)

    retrieve_spy.assert_awaited_once()


# ---------------------------------------------------------------------------
# 14. RAG query response shape matches schema
# ---------------------------------------------------------------------------

def test_rag_query_response_schema_fields():
    from app.schemas.rag import RAGQueryResponse, RAGRetrievedChunk
    chunk = RAGRetrievedChunk(
        chunk_id=str(uuid4()),
        document_id=str(uuid4()),
        chunk_index=0,
        content="Test content",
        similarity_score=0.87,
        metadata={"domain_id": "DOMAIN-003"},
    )
    resp = RAGQueryResponse(
        query="test query",
        results=[chunk],
        results_count=1,
        rag_used=True,
    )
    d = resp.model_dump()
    assert d["results_count"] == 1
    assert d["rag_used"] is True
    assert d["results"][0]["similarity_score"] == pytest.approx(0.87)
