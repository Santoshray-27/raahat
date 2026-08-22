import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest

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

import httpx
from sqlalchemy import text
from app.main import app
from app.core.database import AsyncSessionLocal

@pytest.mark.asyncio
async def test_user_sync_first_time(monkeypatch):
    async with AsyncSessionLocal() as session:
        await session.execute(text("DELETE FROM users WHERE firebase_uid = 'dev_user_999'"))
        await session.commit()
        
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/users/me")
        assert response.status_code == 200
        
    async with AsyncSessionLocal() as session:
        result = await session.execute(text("SELECT id, firebase_uid, email, display_name FROM users WHERE firebase_uid = 'dev_user_999'"))
        user = result.fetchone()
        assert user is not None
        assert user.firebase_uid == "dev_user_999"
        assert user.email == "santosh.dev@raahat.app"
        assert user.display_name == "Santosh Ray (Dev Mode)"
        
        pref_result = await session.execute(text(f"SELECT * FROM user_preferences WHERE user_id = '{user.id}'"))
        pref = pref_result.fetchone()
        assert pref is not None

@pytest.mark.asyncio
async def test_user_sync_existing_user():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        # First ensure the user exists
        await client.get("/api/v1/users/me")

    async with AsyncSessionLocal() as session:
        result = await session.execute(text("SELECT id FROM users WHERE firebase_uid = 'dev_user_999'"))
        first_id = result.scalar_one_or_none()
        assert first_id is not None

    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/users/me")
        assert response.status_code == 200
        
    async with AsyncSessionLocal() as session:
        result = await session.execute(text("SELECT id FROM users WHERE firebase_uid = 'dev_user_999'"))
        second_id = result.scalar_one_or_none()
        assert first_id == second_id
        
        pref_result = await session.execute(text(f"SELECT count(*) FROM user_preferences WHERE user_id = '{first_id}'"))
        pref_count = pref_result.scalar_one_or_none()
        assert pref_count == 1

@pytest.mark.asyncio
async def test_missing_optional_claims(monkeypatch):
    from app.schemas.users import UserProfile
    from app.core.security import get_current_user
    
    async def override_get_current_user():
        return UserProfile(uid="missing_claims_user", email=None, phone_number=None, display_name=None)
        
    app.dependency_overrides[get_current_user] = override_get_current_user
    
    try:
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/v1/users/me")
            assert response.status_code == 200
            
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("SELECT email, phone_number FROM users WHERE firebase_uid = 'missing_claims_user'"))
            user = result.fetchone()
            assert user is not None
            assert user.email is None
            assert user.phone_number is None
            
            await session.execute(text("DELETE FROM users WHERE firebase_uid = 'missing_claims_user'"))
            await session.commit()
    finally:
        app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_authentication_failure():
    from app.core.config import settings
    original_auth = settings.AUTH_DISABLED
    settings.AUTH_DISABLED = False
    
    try:
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/v1/users/me")
            assert response.status_code == 401
    finally:
        settings.AUTH_DISABLED = original_auth
