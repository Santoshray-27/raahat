import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, Integer, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.core.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class AgentSession(Base):
    __tablename__ = "agent_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    incident_id = Column(UUID(as_uuid=True), ForeignKey("incidents.id", ondelete="SET NULL"), nullable=True)
    
    session_type = Column(String, nullable=False)
    status = Column(String, nullable=False, default="active")
    
    started_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    ended_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="agent_sessions")
    incident = relationship("Incident", back_populates="agent_sessions")
    actions = relationship("AgentAction", back_populates="session", cascade="all, delete-orphan")

class AgentAction(Base):
    __tablename__ = "agent_actions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("agent_sessions.id", ondelete="CASCADE"), nullable=False)
    
    action_type = Column(String, nullable=False)
    target_service_id = Column(UUID(as_uuid=True), ForeignKey("service_locations.id", ondelete="SET NULL"), nullable=True)
    
    requires_user_consent = Column(Boolean, default=False, nullable=False)
    user_consented_at = Column(DateTime(timezone=True), nullable=True)
    
    status = Column(String, nullable=False)
    
    input_data = Column(JSONB, nullable=True)
    output_data = Column(JSONB, nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    # Relationships
    session = relationship("AgentSession", back_populates="actions")
    call_records = relationship("AgentCallRecord", back_populates="action", cascade="all, delete-orphan")

class AgentCallRecord(Base):
    __tablename__ = "agent_call_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_action_id = Column(UUID(as_uuid=True), ForeignKey("agent_actions.id", ondelete="CASCADE"), nullable=False)
    
    phone_number = Column(String, nullable=False)
    provider = Column(String, nullable=True)
    external_call_id = Column(String, nullable=True)
    status = Column(String, nullable=False)
    
    started_at = Column(DateTime(timezone=True), nullable=True)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    
    transcript = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    
    metadata_ = Column("metadata", JSONB, nullable=True)

    # Relationships
    action = relationship("AgentAction", back_populates="call_records")
