import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from app.repositories.base import BaseRepository
from app.models.incident import Incident, IncidentUpdate
from typing import Optional
from uuid import UUID

logger = logging.getLogger(__name__)

class IncidentRepository(BaseRepository[Incident]):
    async def create_incident(self, incident: Incident) -> Optional[Incident]:
        """
        Persists an Incident to the database.
        Returns the Incident on success, or None on database failure to avoid blocking emergencies.
        """
        try:
            self.session.add(incident)
            await self.session.commit()
            await self.session.refresh(incident)
            return incident
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Failed to persist Incident: {e}")
            return None

    async def create_incident_update(self, update: IncidentUpdate) -> Optional[IncidentUpdate]:
        """
        Persists an IncidentUpdate to the database.
        Returns the IncidentUpdate on success, or None on database failure.
        """
        try:
            self.session.add(update)
            await self.session.commit()
            await self.session.refresh(update)
            return update
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Failed to persist IncidentUpdate: {e}")
            return None
