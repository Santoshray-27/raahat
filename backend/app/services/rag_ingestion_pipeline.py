import logging
from typing import Optional, List
from pathlib import Path
from dataclasses import dataclass

from app.services.rag_parser import parse_corpus_directory, ParsedDomainFile
from app.services.rag_normalizer import normalize_domain, NormalizedDomain
from app.services.rag_chunker import chunk_normalized_domain, EmbeddingReadyChunk
from app.services.rag_embedding_service import RagEmbeddingService
from app.repositories.rag_repository import RagRepository

logger = logging.getLogger(__name__)

@dataclass
class IngestionSummary:
    files_parsed: int = 0
    files_skipped: int = 0
    documents_created: int = 0
    documents_skipped: int = 0
    chunks_created: int = 0
    chunks_failed: int = 0
    total_embeddings_generated: int = 0

class RagIngestionPipeline:
    def __init__(
        self,
        corpus_dir: str,
        embedding_service: RagEmbeddingService,
        rag_repository: RagRepository
    ):
        self.corpus_dir = corpus_dir
        self.embedding_service = embedding_service
        self.rag_repository = rag_repository

    async def run_full_ingestion(self) -> IngestionSummary:
        summary = IngestionSummary()
        
        # 1. Parse corpus directory
        parsed_files = parse_corpus_directory(self.corpus_dir)
        for parsed in parsed_files:
            if parsed.status != "parsed":
                summary.files_skipped += 1
                import os
                logger.info(f"Skipping {os.path.basename(parsed.filepath)} (reason: {parsed.reason})")
                continue
            
            summary.files_parsed += 1
            
            # 2. Normalize
            normalized = normalize_domain(parsed)
            if not normalized:
                summary.documents_skipped += 1
                continue
                
            # 3. Idempotency Check
            existing_doc = await self.rag_repository.get_document_by_content_hash(normalized.file_hash)
            if existing_doc:
                logger.info(f"Document {normalized.domain_id} ({normalized.file_hash}) already ingested. Skipping embedding.")
                summary.documents_skipped += 1
                continue
                
            # 4. Upsert Document and Sources
            try:
                doc = await self.rag_repository.upsert_document(normalized)
                summary.documents_created += 1
                
                await self.rag_repository.upsert_sources(doc.id, normalized.sources)
                
                # 5. Chunk
                chunks = chunk_normalized_domain(normalized)
                if not chunks:
                    await self.rag_repository.session.commit()
                    continue
                    
                # 6. Embed in batch
                texts_to_embed = [c.embedding_text for c in chunks]
                embeddings = await self.embedding_service.embed_batch(texts_to_embed, task_type="RETRIEVAL_DOCUMENT")
                summary.total_embeddings_generated += len(embeddings)
                
                # 7. Persist chunks
                chunks_with_embeddings = list(zip(chunks, embeddings))
                inserted = await self.rag_repository.bulk_upsert_chunks(doc.id, chunks_with_embeddings)
                summary.chunks_created += inserted
                
                await self.rag_repository.session.commit()
                logger.info(f"Successfully ingested {normalized.domain_id}: {inserted} chunks.")
            except Exception as e:
                logger.error(f"Failed to ingest document {normalized.domain_id}: {e}", exc_info=True)
                summary.chunks_failed += len(chunks) if 'chunks' in locals() else 0
                await self.rag_repository.session.rollback()
                
        return summary
