import sys, os
import pytest
import httpx
from unittest.mock import patch
from sqlalchemy.future import select
from uuid import UUID

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def is_db_unreachable() -> bool:
    from app.core.config import settings
    if not settings.DATABASE_URL or ("postgres://" not in settings.DATABASE_URL and "postgresql://" not in settings.DATABASE_URL):
        return True
    import socket
    from urllib.parse import urlparse
    try:
        url = urlparse(settings.DATABASE_URL)
        host = url.hostname or "localhost"
        port = url.port or 5432
        with socket.create_connection((host, port), timeout=1.0):
            return False
    except Exception:
        return True

pytestmark = pytest.mark.skipif(
    is_db_unreachable(),
    reason="DATABASE_URL not configured"
)

from app.main import app
from app.core.security import get_optional_current_user
from app.schemas.users import UserProfile
from app.core.database import get_engine, get_session_factory, get_db
from app.models.incident import Incident, IncidentUpdate
from app.models.user import User
from sqlalchemy.exc import SQLAlchemyError

def override_get_optional_current_user():
    return UserProfile(
        uid="test_user_persistence",
        email="test@raahat.app",
        display_name="Test User",
        is_anonymous=False
    )

@pytest.mark.asyncio
async def test_emergency_authenticated_persistence():
    app.dependency_overrides[get_optional_current_user] = override_get_optional_current_user
    
    payload = {
        "user_query": "Persistent emergency test",
        "location": {"latitude": 22.7, "longitude": 75.8}
    }
    
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/v1/emergency-assistance", json=payload)
        
    app.dependency_overrides = {}
    
    assert response.status_code == 200
    res = response.json()
    assert res["success"] is True
    incident_id_str = res["data"]["incident"]["incident_id"]
    
    # Verify in DB
    try:
        incident_id = UUID(incident_id_str)
    except ValueError:
        pytest.fail(f"Returned incident_id {incident_id_str} is not a valid UUID")
        
    async_session_factory = get_session_factory()
    async with async_session_factory() as session:
        # Check incident
        result = await session.execute(select(Incident).where(Incident.id == incident_id))
        incident = result.scalar_one_or_none()
        assert incident is not None
        assert incident.description == "Persistent emergency test"
        
        # Check user
        user_result = await session.execute(select(User).where(User.id == incident.user_id))
        user = user_result.scalar_one_or_none()
        assert user is not None
        assert user.firebase_uid == "test_user_persistence"
        
        # Check update
        update_result = await session.execute(select(IncidentUpdate).where(IncidentUpdate.incident_id == incident_id))
        updates = update_result.scalars().all()
        assert len(updates) > 0
        assert updates[-1].message == "Services retrieved and actions recommended."


def override_get_none_user():
    return None

@pytest.mark.asyncio
async def test_emergency_anonymous_persistence():
    # Ensure anonymous user override
    app.dependency_overrides[get_optional_current_user] = override_get_none_user
    
    payload = {
        "user_query": "Anonymous emergency test",
        "location": {"latitude": 22.7, "longitude": 75.8}
    }
    
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/v1/emergency-assistance", json=payload)
    
    app.dependency_overrides = {}
        
    assert response.status_code == 200
    res = response.json()
    assert res["success"] is True
    incident_id_str = res["data"]["incident"]["incident_id"]
    
    assert incident_id_str.startswith("inc_")
    
@pytest.mark.asyncio
async def test_emergency_db_failure_fallback():
    app.dependency_overrides[get_optional_current_user] = override_get_optional_current_user
    
    payload = {
        "user_query": "DB failure emergency test",
        "location": {"latitude": 22.7, "longitude": 75.8}
    }
    
    with patch("app.repositories.incident_repository.IncidentRepository.create_incident") as mock_create:
        mock_create.side_effect = SQLAlchemyError("Simulated DB failure")
        
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/v1/emergency-assistance", json=payload)
            
    app.dependency_overrides = {}
    
    assert response.status_code == 200
    res = response.json()
    assert res["success"] is True
    # Verify fallback to transient ID
    incident_id_str = res["data"]["incident"]["incident_id"]
    assert incident_id_str.startswith("inc_")
