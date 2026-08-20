from app.core.database import Base

from app.models.user import User, UserPreference, AuditLog
from app.models.incident import Incident, IncidentUpdate
from app.models.route import Route, OfflinePackage, OfflinePackageItem
from app.models.service import ServiceCategory, ServiceLocation, ServiceLocationCategory
from app.models.rag import RagDocument, RagSource, RagChunk, EmergencyContact
from app.models.agent import AgentSession, AgentAction, AgentCallRecord

# Export all models and the Base to make it easier for Alembic to import
__all__ = [
    "Base",
    "User",
    "UserPreference",
    "AuditLog",
    "Incident",
    "IncidentUpdate",
    "Route",
    "OfflinePackage",
    "OfflinePackageItem",
    "ServiceCategory",
    "ServiceLocation",
    "ServiceLocationCategory",
    "RagDocument",
    "RagSource",
    "RagChunk",
    "EmergencyContact",
    "AgentSession",
    "AgentAction",
    "AgentCallRecord",
]
