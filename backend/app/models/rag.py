import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector

from app.core.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class EmergencyContact(Base):
    __tablename__ = "emergency_contacts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    country_code = Column(String, nullable=False)
    region_code = Column(String, nullable=True)
    service_type = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    description = Column(String, nullable=True)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    source_document_id = Column(UUID(as_uuid=True), ForeignKey("rag_documents.id", ondelete="SET NULL"), nullable=True)
    last_verified_at = Column(DateTime(timezone=True), nullable=True)

class RagDocument(Base):
    __tablename__ = "rag_documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    source_type = Column(String, nullable=False)
    source_url = Column(String, nullable=True)
    language = Column(String, nullable=False, default="en")
    country_code = Column(String, nullable=True)
    region_code = Column(String, nullable=True)
    version = Column(String, nullable=True)
    content_hash = Column(String, nullable=True)
    
    metadata_ = Column("metadata", JSONB, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    # Relationships
    sources = relationship("RagSource", back_populates="document", cascade="all, delete-orphan")
    chunks = relationship("RagChunk", back_populates="document", cascade="all, delete-orphan")

class RagSource(Base):
    __tablename__ = "rag_sources"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("rag_documents.id", ondelete="CASCADE"), nullable=False)
    
    source_name = Column(String, nullable=False)
    source_url = Column(String, nullable=True)
    retrieved_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    source_type = Column(String, nullable=True)
    
    metadata_ = Column("metadata", JSONB, nullable=True)

    # Relationships
    document = relationship("RagDocument", back_populates="sources")

class RagChunk(Base):
    __tablename__ = "rag_chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("rag_documents.id", ondelete="CASCADE"), nullable=False)
    
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    
    # 1536 is explicitly locked by requirements
    embedding = Column(Vector(1536), nullable=True) 
    
    token_count = Column(Integer, nullable=True)
    metadata_ = Column("metadata", JSONB, nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    __table_args__ = (
        UniqueConstraint('document_id', 'chunk_index', name='uq_rag_chunks_document_index'),
        Index('ix_rag_chunks_embedding', 'embedding', postgresql_using='hnsw', postgresql_with={'m': 16, 'ef_construction': 64}, postgresql_ops={'embedding': 'vector_cosine_ops'}),
    )

    # Relationships
    document = relationship("RagDocument", back_populates="chunks")
