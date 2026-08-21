import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.rag_ingestion_pipeline import RagIngestionPipeline
from app.services.rag_parser import ParsedDomainFile
from app.services.rag_normalizer import NormalizedDomain
from app.services.rag_chunker import EmbeddingReadyChunk
from uuid import uuid4

@pytest.fixture
def mock_embedding_service():
    return AsyncMock()

@pytest.fixture
def mock_rag_repository():
    repo = AsyncMock()
    repo.session = AsyncMock()
    return repo

@pytest.fixture
def pipeline(mock_embedding_service, mock_rag_repository):
    return RagIngestionPipeline(
        corpus_dir="fake_dir",
        embedding_service=mock_embedding_service,
        rag_repository=mock_rag_repository
    )

@pytest.mark.asyncio
async def test_pipeline_skips_failed_parse(pipeline):
    mock_parsed = MagicMock(spec=ParsedDomainFile)
    mock_parsed.status = "skipped"
    mock_parsed.reason = "empty_file"
    mock_parsed.filepath = "test.json"
    
    with patch("app.services.rag_ingestion_pipeline.parse_corpus_directory", return_value=[mock_parsed]):
        summary = await pipeline.run_full_ingestion()
        
        assert summary.files_skipped == 1
        assert summary.files_parsed == 0

@pytest.mark.asyncio
async def test_pipeline_skips_existing_hash(pipeline):
    mock_parsed = MagicMock(spec=ParsedDomainFile)
    mock_parsed.status = "parsed"
    mock_parsed.filepath = "test.json"
    mock_parsed.file_hash = "hash123"
    mock_norm = NormalizedDomain(
        domain_id="DOMAIN-001", version="v1", domain_name="Test", filepath=mock_parsed.filepath,
        file_hash="hash123", records=[], sources=[], knowledge_requirements=[], knowledge_gaps=[], research_summary=""
    )
    
    with patch("app.services.rag_ingestion_pipeline.parse_corpus_directory", return_value=[mock_parsed]):
        with patch("app.services.rag_ingestion_pipeline.normalize_domain", return_value=mock_norm):
            # Repository says hash exists
            pipeline.rag_repository.get_document_by_content_hash.return_value = MagicMock()
            
            summary = await pipeline.run_full_ingestion()
            
            assert summary.files_parsed == 1
            assert summary.documents_skipped == 1
            assert summary.documents_created == 0

@pytest.mark.asyncio
async def test_pipeline_full_ingestion_success(pipeline):
    mock_parsed = MagicMock(spec=ParsedDomainFile)
    mock_parsed.status = "parsed"
    mock_parsed.filepath = "test.json"
    mock_parsed.file_hash = "hash123"
    mock_norm = NormalizedDomain(
        domain_id="DOMAIN-001", version="v1", domain_name="Test", filepath=mock_parsed.filepath,
        file_hash="hash123", records=["rec1"], sources=["src1"], knowledge_requirements=[], knowledge_gaps=[], research_summary=""
    )
    mock_chunk = EmbeddingReadyChunk(domain_id="D1", version="v1", record_id="R1", requirement_id="KR1", chunk_index=0, embedding_text="text1", chunk_metadata={}, estimated_tokens=10)
    
    with patch("app.services.rag_ingestion_pipeline.parse_corpus_directory", return_value=[mock_parsed]):
        with patch("app.services.rag_ingestion_pipeline.normalize_domain", return_value=mock_norm):
            with patch("app.services.rag_ingestion_pipeline.chunk_normalized_domain", return_value=[mock_chunk]):
                
                pipeline.rag_repository.get_document_by_content_hash.return_value = None
                mock_doc = MagicMock()
                mock_doc.id = uuid4()
                pipeline.rag_repository.upsert_document.return_value = mock_doc
                pipeline.rag_repository.bulk_upsert_chunks.return_value = 1
                pipeline.embedding_service.embed_batch.return_value = [[0.1]*1536]
                
                summary = await pipeline.run_full_ingestion()
                
                assert summary.files_parsed == 1
                assert summary.documents_created == 1
                assert summary.chunks_created == 1
                assert summary.total_embeddings_generated == 1
                
                pipeline.embedding_service.embed_batch.assert_called_once_with(["text1"], task_type="RETRIEVAL_DOCUMENT")
                pipeline.rag_repository.session.commit.assert_called_once()
