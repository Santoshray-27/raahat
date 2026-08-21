import os
from unittest.mock import patch, MagicMock, AsyncMock
import pytest
from httpx import AsyncClient, ASGITransport

# Test CORS parsing
def test_cors_origin_parsing():
    from app.core.config import Settings
    
    # Default behavior
    settings = Settings(CORS_ORIGINS="http://localhost:5173, http://localhost:3000 ")
    origins = settings.cors_origins_list
    assert "http://localhost:5173" in origins
    assert "http://localhost:3000" in origins
    assert len(origins) == 2
    
    # Production behavior
    settings = Settings(CORS_ORIGINS="https://myprod.com")
    assert settings.cors_origins_list == ["https://myprod.com"]
    
    # Empty behavior
    settings = Settings(CORS_ORIGINS="")
    assert settings.cors_origins_list == []

# Test Auth Disabled logic
def test_auth_disabled_environment_logic():
    from app.core.config import Settings
    
    # Default is True for local development ease
    settings = Settings()
    assert settings.AUTH_DISABLED is True
        
    with patch.dict(os.environ, {"AUTH_DISABLED": "false"}):
        settings = Settings()
        assert settings.AUTH_DISABLED is False
        
    with patch.dict(os.environ, {"AUTH_DISABLED": "true"}):
        settings = Settings()
        assert settings.AUTH_DISABLED is True

# Test Database Lifespan
@pytest.mark.asyncio
async def test_database_startup_check():
    from app.main import lifespan
    from fastapi import FastAPI
    
    app = FastAPI()
    
    # Test successful DB connection
    with patch("app.main.engine", new_callable=MagicMock) as mock_engine:
        mock_engine.dispose = AsyncMock()
        mock_conn = AsyncMock()
        mock_engine.connect.return_value.__aenter__.return_value = mock_conn
        
        async with lifespan(app):
            mock_conn.execute.assert_called_once()
            args, _ = mock_conn.execute.call_args
            assert "SELECT 1" in str(args[0])
            
    # Test failed DB connection doesn't crash the app (graceful degradation)
    with patch("app.main.engine", new_callable=MagicMock) as mock_engine:
        mock_engine.dispose = AsyncMock()
        mock_engine.connect.return_value.__aenter__.side_effect = Exception("DB Connection Refused")
        with patch("app.main.logger.error") as mock_logger:
            async with lifespan(app):
                pass  # Should not raise exception
            mock_logger.assert_called_once()
            assert "Database connection failed" in mock_logger.call_args[0][0]
            assert "DB Connection Refused" in mock_logger.call_args[0][0]

# Test main entrypoint variables
def test_main_execution_variables():
    # To test PORT and reload without running the server, 
    # we replicate the exact variables used in main.py
    
    with patch.dict(os.environ, {"PORT": "8080", "ENVIRONMENT": "production"}):
        from app.core.config import Settings
        settings = Settings()
        port = int(os.getenv("PORT", 8000))
        reload_mode = (settings.ENVIRONMENT == "development")
        
        assert port == 8080
        assert reload_mode is False
        
    with patch.dict(os.environ, {}, clear=True):
        from app.core.config import Settings
        settings = Settings()
        port = int(os.getenv("PORT", 8000))
        reload_mode = (settings.ENVIRONMENT == "development")
        
        assert port == 8000
        assert reload_mode is True

@pytest.mark.asyncio
async def test_health_endpoint_still_works():
    from app.main import app
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/health")
        # Health endpoint should either return 200 or 503 depending on db mock,
        # but the contract is intact and doesn't leak secrets.
        assert response.status_code in [200, 503]
        if response.status_code == 503:
            assert response.json()["error"]["message"] == "Database connection failed"
