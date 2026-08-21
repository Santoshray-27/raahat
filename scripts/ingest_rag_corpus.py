import sys
import os
import asyncio
import logging

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.core.database import AsyncSessionLocal
from app.core.config import settings
from app.services.rag_embedding_service import RagEmbeddingService
from app.repositories.rag_repository import RagRepository
from app.services.rag_ingestion_pipeline import RagIngestionPipeline

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger("rag_ingestion")

async def main():
    logger.info("Starting RAG Ingestion Pipeline...")
    
    if not settings.GEMINI_API_KEY:
        logger.warning("GEMINI_API_KEY is not set. Ingestion will fail when attempting to generate embeddings.")
        
    corpus_dir = getattr(settings, "RAG_CORPUS_DIR", os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "RAG")))
    if not os.path.isabs(corpus_dir):
        corpus_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend", corpus_dir))
    
    logger.info(f"Using corpus directory: {corpus_dir}")
    
    embedding_service = RagEmbeddingService()
    
    async with AsyncSessionLocal() as session:
        rag_repository = RagRepository(session)
        pipeline = RagIngestionPipeline(
            corpus_dir=corpus_dir,
            embedding_service=embedding_service,
            rag_repository=rag_repository
        )
        
        summary = await pipeline.run_full_ingestion()
        
    logger.info("--- Ingestion Summary ---")
    logger.info(f"Files parsed: {summary.files_parsed}")
    logger.info(f"Files skipped: {summary.files_skipped}")
    logger.info(f"Documents created/updated: {summary.documents_created}")
    logger.info(f"Documents skipped (unchanged): {summary.documents_skipped}")
    logger.info(f"Chunks generated and inserted: {summary.chunks_created}")
    logger.info(f"Embeddings generated: {summary.total_embeddings_generated}")
    if summary.chunks_failed > 0:
        logger.error(f"Failed to process {summary.chunks_failed} chunks.")

if __name__ == "__main__":
    asyncio.run(main())
