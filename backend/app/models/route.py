import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from geoalchemy2 import Geography

from app.core.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class Route(Base):
    __tablename__ = "routes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    origin = Column(Geography("POINT", srid=4326), nullable=False)
    destination = Column(Geography("POINT", srid=4326), nullable=False)
    route_geometry = Column(Geography("LINESTRING", srid=4326), nullable=False, index=True)
    
    distance_m = Column(Float, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    
    provider = Column(String, nullable=True)
    external_route_id = Column(String, nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="routes")
    offline_packages = relationship("OfflinePackage", back_populates="route", cascade="all, delete-orphan")

class OfflinePackage(Base):
    __tablename__ = "offline_packages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    route_id = Column(UUID(as_uuid=True), ForeignKey("routes.id", ondelete="CASCADE"), nullable=False)
    
    version = Column(Integer, nullable=False, default=1)
    package_size_bytes = Column(Integer, nullable=True)
    content_hash = Column(String, nullable=True)
    
    expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    # Relationships
    route = relationship("Route", back_populates="offline_packages")
    items = relationship("OfflinePackageItem", back_populates="package", cascade="all, delete-orphan")

class OfflinePackageItem(Base):
    __tablename__ = "offline_package_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    package_id = Column(UUID(as_uuid=True), ForeignKey("offline_packages.id", ondelete="CASCADE"), nullable=False)
    
    item_type = Column(String, nullable=False)
    reference_id = Column(String, nullable=True)
    data = Column(JSONB, nullable=False)
    
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    # Relationships
    package = relationship("OfflinePackage", back_populates="items")
