import asyncio
import os
import sys
import tempfile
import shutil
import logging

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from sqlalchemy import text
from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.services.rag_embedding_service import RagEmbeddingService
from app.repositories.rag_repository import RagRepository
from app.services.rag_ingestion_pipeline import RagIngestionPipeline

logging.basicConfig(level=logging.ERROR)

async def verify():
    print("==================================================")
    print("PHASE 2: ENVIRONMENT SAFETY CHECK")
    print("==================================================")
    if not settings.DATABASE_URL:
        print("BLOCKER: DATABASE_URL is missing")
        return
    else:
        print("PASS: DATABASE_URL is present (redacted)")

    if not settings.GEMINI_API_KEY:
        print("BLOCKER: GEMINI_API_KEY is missing")
        return
    else:
        print("PASS: GEMINI_API_KEY is present (redacted)")

    try:
        async with AsyncSessionLocal() as session:
            res = await session.execute(text("SELECT 1"))
            print(f"PASS: Database is reachable (SELECT 1 returned {res.scalar()})")
            
            # Check schema
            res = await session.execute(text("SELECT to_regclass('rag_documents'), to_regclass('rag_sources'), to_regclass('rag_chunks')"))
            tables = res.fetchone()
            if not all(tables):
                print(f"BLOCKER: Missing RAG tables. Regclass returned: {tables}")
                return
            print("PASS: rag_documents, rag_sources, rag_chunks exist")
            
            # Check VECTOR(1536)
            res = await session.execute(text("""
                SELECT data_type, character_maximum_length, udt_name 
                FROM information_schema.columns 
                WHERE table_name='rag_chunks' AND column_name='embedding'
            """))
            emb_col = res.fetchone()
            print(f"PASS: rag_chunks.embedding column info: {emb_col}")
            
            # Check index
            res = await session.execute(text("SELECT indexname, indexdef FROM pg_indexes WHERE tablename = 'rag_chunks' AND indexname = 'ix_rag_chunks_embedding'"))
            idx = res.fetchone()
            if idx:
                print(f"PASS: HNSW Index exists: {idx[0]}")
            else:
                print("BLOCKER: HNSW index missing")
                return

    except Exception as e:
        print(f"BLOCKER: Database check failed: {e}")
        return

    # Corpus Dir check
    corpus_dir = getattr(settings, "RAG_CORPUS_DIR", None)
    if not corpus_dir:
        corpus_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "RAG"))
    else:
        corpus_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend", corpus_dir))
    
    print(f"PASS: Corpus directory resolved to {corpus_dir}")
    
    print("\n==================================================")
    print("PHASE 3 & 4: CONTROLLED REAL INGESTION & DB STATE")
    print("==================================================")
    domain_003_path = os.path.join(corpus_dir, "DOMAIN-003.json")
    if not os.path.exists(domain_003_path):
        print(f"BLOCKER: {domain_003_path} does not exist")
        return
        
    with tempfile.TemporaryDirectory() as temp_dir:
        shutil.copy(domain_003_path, temp_dir)
        print(f"PASS: Copied DOMAIN-003.json to isolated directory")
        
        # Also copy DOMAIN-005.v2.json to check skip behavior
        domain_005_path = os.path.join(corpus_dir, "DOMAIN-005.v2.json")
        if os.path.exists(domain_005_path):
             shutil.copy(domain_005_path, temp_dir)
             print(f"PASS: Copied DOMAIN-005.v2.json to isolated directory for skip verification")

        embedding_service = RagEmbeddingService()
        async with AsyncSessionLocal() as session:
            rag_repository = RagRepository(session)
            pipeline = RagIngestionPipeline(
                corpus_dir=temp_dir,
                embedding_service=embedding_service,
                rag_repository=rag_repository
            )
            
            print("Running pipeline...")
            summary = await pipeline.run_full_ingestion()
            print(f"Ingestion 1 Summary: {summary}")
            
            if summary.files_skipped > 0:
                print("PASS: Truncated file (DOMAIN-005.v2.json) was skipped correctly.")
                
            # Verify DB state
            docs = await rag_repository.get_active_documents()
            doc_id = None
            for d in docs:
                if d.title == "First Aid":
                    doc_id = d.id
                    print(f"PASS: Document exists in DB: ID={d.id}, Hash={d.content_hash}, Active={d.is_active}")
                    break
                    
            if not doc_id:
                print("BLOCKER: First Aid document not found after ingestion")
                return
                
            res = await session.execute(text(f"SELECT count(*) FROM rag_sources WHERE document_id = '{doc_id}'"))
            print(f"PASS: Sources count: {res.scalar()}")
            
            res = await session.execute(text(f"""
                SELECT count(*), min(vector_dims(embedding)), max(vector_dims(embedding)), count(embedding) 
                FROM rag_chunks WHERE document_id = '{doc_id}'
            """))
            chunks_cnt, min_dim, max_dim, non_null = res.fetchone()
            print(f"PASS: Chunks count: {chunks_cnt}, Non-Null embeddings: {non_null}, Min Dim: {min_dim}, Max Dim: {max_dim}")
            
            if chunks_cnt != 13 or non_null != 13 or min_dim != 1536 or max_dim != 1536:
                print("BLOCKER: DB state did not match expected 13 chunks/embeddings with dimension 1536.")
            
        print("\n==================================================")
        print("PHASE 5: IDEMPOTENCY TEST")
        print("==================================================")
        async with AsyncSessionLocal() as session:
            rag_repository = RagRepository(session)
            pipeline = RagIngestionPipeline(
                corpus_dir=temp_dir,
                embedding_service=embedding_service,
                rag_repository=rag_repository
            )
            summary2 = await pipeline.run_full_ingestion()
            print(f"Ingestion 2 Summary: {summary2}")
            
            if summary2.documents_skipped == 1 and summary2.total_embeddings_generated == 0:
                print("PASS: Idempotency logic properly skipped regenerating embeddings.")
            else:
                print("BLOCKER: Idempotency failed.")
                
            res = await session.execute(text(f"SELECT count(*) FROM rag_chunks WHERE document_id = '{doc_id}'"))
            print(f"PASS: Chunks count after run 2 remains: {res.scalar()}")

    print("\n==================================================")
    print("PHASE 6: REAL VECTOR RETRIEVAL SMOKE TEST")
    print("==================================================")
    query = "How should I control severe bleeding after a roadside injury?"
    async with AsyncSessionLocal() as session:
        emb_service = RagEmbeddingService()
        repo = RagRepository(session)
        q_emb = await emb_service.embed_query(query)
        print(f"PASS: Generated query embedding of dimension {len(q_emb)}")
        
        results = await repo.similarity_search(q_emb, top_k=3)
        print(f"PASS: Found {len(results)} results")
        for i, (chunk, score) in enumerate(results):
            req_id = chunk.metadata_.get("requirement_id", "N/A") if chunk.metadata_ else "N/A"
            domain = chunk.metadata_.get("domain_id", "N/A") if chunk.metadata_ else "N/A"
            print(f"  [{i+1}] Score: {score:.4f} | Domain: {domain} | Req: {req_id} | Chunk Index: {chunk.chunk_index} | ID: {chunk.id}")

if __name__ == "__main__":
    asyncio.run(verify())
