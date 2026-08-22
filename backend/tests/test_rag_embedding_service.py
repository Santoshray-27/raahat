import pytest
import math
from unittest.mock import patch, AsyncMock
from app.services.rag_embedding_service import RagEmbeddingService, RagEmbeddingError
from google.api_core.exceptions import ResourceExhausted, ServiceUnavailable, GoogleAPICallError

@pytest.fixture
def mock_genai_config(monkeypatch):
    monkeypatch.setattr("app.core.config.settings.GEMINI_API_KEY", "test-key")

@pytest.fixture
def embedding_service(mock_genai_config):
    return RagEmbeddingService()

def test_l2_normalize():
    vec = [1.0, 1.0, 1.0, 1.0]
    normalized = RagEmbeddingService._l2_normalize(vec)
    # length should be 2.0. Each item 0.5.
    assert math.isclose(sum(x*x for x in normalized), 1.0, rel_tol=1e-5)
    assert all(math.isclose(x, 0.5, rel_tol=1e-5) for x in normalized)

@pytest.mark.asyncio
async def test_embed_document_success(embedding_service):
    mock_resp = {"embedding": [0.1] * 1536}
    with patch("google.generativeai.embed_content_async", new_callable=AsyncMock) as mock_embed:
        mock_embed.return_value = mock_resp
        vec = await embedding_service.embed_document("Test document text")
        
        mock_embed.assert_called_once()
        kwargs = mock_embed.call_args.kwargs
        assert kwargs["task_type"] == "RETRIEVAL_DOCUMENT"
        assert kwargs["output_dimensionality"] == 1536
        assert len(vec) == 1536
        assert math.isclose(sum(x*x for x in vec), 1.0, rel_tol=1e-5)

@pytest.mark.asyncio
async def test_embed_batch_success(embedding_service):
    # simulate 3 vectors returned
    mock_resp = {"embedding": [[0.1] * 1536, [0.2] * 1536, [0.3] * 1536]}
    with patch("google.generativeai.embed_content_async", new_callable=AsyncMock) as mock_embed:
        mock_embed.return_value = mock_resp
        vecs = await embedding_service.embed_batch(["t1", "t2", "t3"])
        
        mock_embed.assert_called_once()
        assert len(vecs) == 3
        for v in vecs:
            assert math.isclose(sum(x*x for x in v), 1.0, rel_tol=1e-5)

@pytest.mark.asyncio
async def test_embed_retries_on_resource_exhausted(embedding_service):
    embedding_service.RETRY_BASE_DELAY = 0.01  # speed up test
    mock_resp = {"embedding": [0.1] * 1536}
    
    with patch("google.generativeai.embed_content_async", new_callable=AsyncMock) as mock_embed:
        # Fail twice, succeed on third
        mock_embed.side_effect = [
            ResourceExhausted("Rate limited"),
            ServiceUnavailable("Unavailable"),
            mock_resp
        ]
        
        vec = await embedding_service.embed_document("Retry test")
        assert mock_embed.call_count == 3
        assert len(vec) == 1536

@pytest.mark.asyncio
async def test_embed_fails_after_max_retries(embedding_service):
    embedding_service.RETRY_BASE_DELAY = 0.01
    
    with patch("google.generativeai.embed_content_async", new_callable=AsyncMock) as mock_embed:
        mock_embed.side_effect = ResourceExhausted("Rate limited always")
        
        with pytest.raises(RagEmbeddingError) as exc:
            await embedding_service.embed_document("Fail test")
            
        assert mock_embed.call_count == 3
        assert "rate limited or unavailable" in str(exc.value)

@pytest.mark.asyncio
async def test_embed_fails_fast_on_call_error(embedding_service):
    with patch("google.generativeai.embed_content_async", new_callable=AsyncMock) as mock_embed:
        mock_embed.side_effect = GoogleAPICallError("Bad request")
        
        with pytest.raises(RagEmbeddingError) as exc:
            await embedding_service.embed_document("Fast fail test")
            
        # Should not retry for standard call errors
        assert mock_embed.call_count == 1
        assert "API Call Error" in str(exc.value)

@pytest.mark.asyncio
async def test_missing_api_key(monkeypatch):
    monkeypatch.setattr("app.core.config.settings.GEMINI_API_KEY", "")
    service = RagEmbeddingService()
    with pytest.raises(RagEmbeddingError):
        await service.embed_document("text")
