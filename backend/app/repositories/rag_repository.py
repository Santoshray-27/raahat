import logging
from typing import List, Tuple, Dict, Any, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert

from app.repositories.base import BaseRepository
from app.models.rag import RagDocument, RagSource, RagChunk
from app.services.rag_normalizer import NormalizedDomain
from app.services.rag_chunker import EmbeddingReadyChunk

logger = logging.getLogger(__name__)

class RagRepository(BaseRepository[RagDocument]):

    async def get_document_by_content_hash(self, content_hash: str) -> Optional[RagDocument]:
        result = await self.session.execute(select(RagDocument).where(RagDocument.content_hash == content_hash))
        return result.scalar_one_or_none()

    async def get_document_by_domain_version(self, domain_id: str, version: str) -> Optional[RagDocument]:
        result = await self.session.execute(
            select(RagDocument)
            .where(RagDocument.metadata_['domain_id'].astext == domain_id)
            .where(RagDocument.version == version)
            .where(RagDocument.is_active == True)
        )
        return result.scalar_one_or_none()

    async def upsert_document(self, domain: NormalizedDomain) -> RagDocument:
        """Upsert a document. Returns the created/found document."""
        # Check if identical hash exists
        existing_doc = await self.get_document_by_content_hash(domain.file_hash)
        if existing_doc:
            return existing_doc
            
        # Check if old version exists, deactivate if hash changed
        old_doc = await self.get_document_by_domain_version(domain.domain_id, domain.version)
        if old_doc:
            old_doc.is_active = False
            self.session.add(old_doc)
            
        # Create new
        new_doc = RagDocument(
            title=domain.domain_name,
            source_type="corpus",
            version=domain.version,
            content_hash=domain.file_hash,
            metadata_={"domain_id": domain.domain_id},
            is_active=True
        )
        self.session.add(new_doc)
        await self.session.flush() # To get ID
        return new_doc

    async def upsert_sources(self, document_id: UUID, sources: List[Dict]) -> List[RagSource]:
        db_sources = []
        for src in sources:
            source_id = src.get('source_id') or src.get('name', 'Unknown')
            new_source = RagSource(
                document_id=document_id,
                source_name=source_id,
                source_url=src.get('url'),
                metadata_=src
            )
            self.session.add(new_source)
            db_sources.append(new_source)
            
        await self.session.flush()
        return db_sources

    async def upsert_chunk(self, document_id: UUID, chunk: EmbeddingReadyChunk, embedding: List[float]) -> RagChunk:
        stmt = insert(RagChunk).values(
            document_id=document_id,
            chunk_index=chunk.chunk_index,
            content=chunk.embedding_text,
            embedding=embedding,
            token_count=chunk.estimated_tokens,
            metadata_=chunk.chunk_metadata
        )
        stmt = stmt.on_conflict_do_update(
            index_elements=['document_id', 'chunk_index'],
            set_=dict(
                content=stmt.excluded.content,
                embedding=stmt.excluded.embedding,
                token_count=stmt.excluded.token_count,
                metadata=stmt.excluded.metadata
            )
        ).returning(RagChunk)
        
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def bulk_upsert_chunks(self, document_id: UUID, chunks_with_embeddings: List[Tuple[EmbeddingReadyChunk, List[float]]]) -> int:
        if not chunks_with_embeddings:
            return 0
            
        values = []
        for chunk, emb in chunks_with_embeddings:
            values.append({
                "document_id": document_id,
                "chunk_index": chunk.chunk_index,
                "content": chunk.embedding_text,
                "embedding": emb,
                "token_count": chunk.estimated_tokens,
                "metadata_": chunk.chunk_metadata
            })
            
        stmt = insert(RagChunk).values(values)
        stmt = stmt.on_conflict_do_update(
            index_elements=['document_id', 'chunk_index'],
            set_=dict(
                content=stmt.excluded.content,
                embedding=stmt.excluded.embedding,
                token_count=stmt.excluded.token_count,
                metadata=stmt.excluded.metadata
            )
        )
        
        result = await self.session.execute(stmt)
        return result.rowcount

    async def deactivate_document(self, document_id: UUID) -> None:
        await self.session.execute(
            update(RagDocument).where(RagDocument.id == document_id).values(is_active=False)
        )

    async def get_active_documents(self) -> List[RagDocument]:
        result = await self.session.execute(select(RagDocument).where(RagDocument.is_active == True))
        return result.scalars().all()

    async def similarity_search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        min_score: float = 0.0,
        metadata_filter: Optional[Dict[str, Any]] = None,
    ) -> List[Tuple[RagChunk, float]]:
        
        # pgvector cosine distance: embedding <=> query_embedding
        # Cosine similarity = 1 - distance
        cosine_distance = RagChunk.embedding.cosine_distance(query_embedding)
        similarity_score = (1 - cosine_distance).label("similarity_score")
        
        query = (
            select(RagChunk, similarity_score)
            .join(RagDocument, RagChunk.document_id == RagDocument.id)
            .where(RagDocument.is_active == True)
            .where(RagChunk.embedding.is_not(None))
        )
        
        if metadata_filter:
            query = query.where(RagChunk.metadata_.contains(metadata_filter))
            
        query = query.order_by(cosine_distance).limit(top_k)
        
        result = await self.session.execute(query)
        rows = result.all()
        
        filtered_rows = [(chunk, float(score)) for chunk, score in rows if float(score) >= min_score]
        return filtered_rows
