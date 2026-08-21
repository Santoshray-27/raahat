import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, patch, MagicMock
from app.repositories.rag_repository import RagRepository
from app.models.rag import RagDocument, RagSource, RagChunk
from app.services.rag_normalizer import NormalizedDomain
from app.services.rag_chunker import EmbeddingReadyChunk

@pytest.fixture
def mock_session():
    session = AsyncMock()
    session.add = MagicMock()
    return session

@pytest.fixture
def rag_repo(mock_session):
    return RagRepository(mock_session)

@pytest.mark.asyncio
async def test_upsert_document_existing_hash(rag_repo):
    mock_doc = RagDocument(id=uuid4(), title="Existing", content_hash="hash123")
    
    with patch.object(rag_repo, "get_document_by_content_hash", return_value=mock_doc):
        domain = NormalizedDomain(
            domain_id="DOMAIN-003", version="v1", domain_name="First Aid",
            filepath=None, file_hash="hash123", records=[], sources=[],
            knowledge_requirements=[], knowledge_gaps=[], research_summary=""
        )
        
        result = await rag_repo.upsert_document(domain)
        assert result == mock_doc
        rag_repo.session.add.assert_not_called()

@pytest.mark.asyncio
async def test_upsert_document_new_deactivates_old(rag_repo):
    old_doc = RagDocument(id=uuid4(), title="Old", content_hash="hash_old", is_active=True)
    
    with patch.object(rag_repo, "get_document_by_content_hash", return_value=None):
        with patch.object(rag_repo, "get_document_by_domain_version", return_value=old_doc):
            domain = NormalizedDomain(
                domain_id="DOMAIN-003", version="v1", domain_name="First Aid",
                filepath=None, file_hash="hash_new", records=[], sources=[],
                knowledge_requirements=[], knowledge_gaps=[], research_summary=""
            )
            
            result = await rag_repo.upsert_document(domain)
            
            assert old_doc.is_active is False
            assert rag_repo.session.add.call_count == 2
            assert result.content_hash == "hash_new"
            assert result.is_active is True
            rag_repo.session.flush.assert_called_once()

@pytest.mark.asyncio
async def test_upsert_sources(rag_repo):
    doc_id = uuid4()
    sources = [
        {"source_id": "SRC-01", "name": "Test Source", "url": "http://test.com"},
        {"name": "No ID Source"}
    ]
    
    db_sources = await rag_repo.upsert_sources(doc_id, sources)
    
    assert len(db_sources) == 2
    assert db_sources[0].source_name == "SRC-01"
    assert db_sources[1].source_name == "No ID Source"
    assert rag_repo.session.add.call_count == 2
    rag_repo.session.flush.assert_called_once()

@pytest.mark.asyncio
async def test_bulk_upsert_chunks(rag_repo):
    doc_id = uuid4()
    chunk1 = EmbeddingReadyChunk(
        domain_id="D1", version="v1", record_id="R1", requirement_id="KR1",
        chunk_index=0, embedding_text="t1", chunk_metadata={}, estimated_tokens=10
    )
    chunk2 = EmbeddingReadyChunk(
        domain_id="D1", version="v1", record_id="R2", requirement_id="KR1",
        chunk_index=1, embedding_text="t2", chunk_metadata={}, estimated_tokens=20
    )
    
    chunks_with_embeds = [
        (chunk1, [0.1]*1536),
        (chunk2, [0.2]*1536)
    ]
    
    mock_result = MagicMock()
    mock_result.rowcount = 2
    rag_repo.session.execute.return_value = mock_result
    
    inserted = await rag_repo.bulk_upsert_chunks(doc_id, chunks_with_embeds)
    
    assert inserted == 2
    rag_repo.session.execute.assert_called_once()
