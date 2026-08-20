from sqlalchemy import text
from app.repositories.base import BaseRepository

class HealthRepository(BaseRepository):
    async def check_database_health(self) -> bool:
        """
        Executes a lightweight query to verify the database connection is alive.
        """
        try:
            result = await self.session.execute(text("SELECT 1"))
            return result.scalar() == 1
        except Exception as e:
            # We catch any exception (like connection refused, auth failed, etc.)
            return False
