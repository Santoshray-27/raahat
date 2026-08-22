from typing import Optional, Dict
from datetime import datetime, timezone
from app.schemas.common import GeoPoint

class LocationUpdate:
    def __init__(self, location: GeoPoint, updated_at: datetime):
        self.location = location
        self.updated_at = updated_at

class LocationService:
    def __init__(self):
        # In-memory store mapping user_id -> LocationUpdate
        # For a production system, this would be Redis with a TTL
        self._store: Dict[str, LocationUpdate] = {}
        
    def update_location(self, user_id: str, location: GeoPoint):
        self._store[user_id] = LocationUpdate(location, datetime.now(timezone.utc))
        
    def get_latest_location(self, user_id: str) -> Optional[GeoPoint]:
        update = self._store.get(user_id)
        if not update:
            return None
            
        # Optional: Check if location is stale (e.g., older than 1 hour)
        age = (datetime.now(timezone.utc) - update.updated_at).total_seconds()
        if age > 3600:
            return None
            
        return update.location

location_service = LocationService()

