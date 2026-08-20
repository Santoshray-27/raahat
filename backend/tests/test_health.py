import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
import httpx
from app.main import app

@pytest.mark.asyncio
async def test_health_endpoint():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["status"] == "healthy"
        assert "request_id" in data

@pytest.mark.asyncio
async def test_diagnostics_logging():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        # 1. Trigger an emergency assistance call
        payload = {
            "user_query": "Tyre puncture",
            "location": {"latitude": 22.7196, "longitude": 75.8577}
        }
        await client.post("/api/v1/emergency-assistance", json=payload)
        
        # 2. Check diagnostics
        response = await client.get("/api/v1/diagnostics")
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["total_queries_logged"] >= 1
        history = data["data"]["recent_call_history"]
        assert any(entry["endpoint"] == "/api/v1/emergency-assistance" for entry in history)
