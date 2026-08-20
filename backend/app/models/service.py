import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Boolean, DateTime, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from geoalchemy2 import Geography

from app.core.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class ServiceCategory(Base):
    __tablename__ = "service_categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)

    # Relationships
    service_locations = relationship(
        "ServiceLocation",
        secondary="service_location_categories",
        back_populates="categories"
    )

class ServiceLocation(Base):
    __tablename__ = "service_locations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    address = Column(String, nullable=True)
    
    # Location using PostGIS geography point type, stored as SRID 4326
    location = Column(Geography("POINT", srid=4326), nullable=False, index=True)
    
    phone_number = Column(String, nullable=True)
    website_url = Column(String, nullable=True)
    source_provider = Column(String, nullable=True)
    external_place_id = Column(String, nullable=True)
    rating = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    last_verified_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    metadata_ = Column("metadata", JSONB, nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    # Relationships
    categories = relationship(
        "ServiceCategory",
        secondary="service_location_categories",
        back_populates="service_locations"
    )

class ServiceLocationCategory(Base):
    __tablename__ = "service_location_categories"

    service_location_id = Column(UUID(as_uuid=True), ForeignKey("service_locations.id", ondelete="CASCADE"), nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey("service_categories.id", ondelete="CASCADE"), nullable=False)
    
    __table_args__ = (
        PrimaryKeyConstraint("service_location_id", "category_id"),
    )
