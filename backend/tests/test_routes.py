import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
import httpx
from app.main import app

@pytest.mark.asyncio
async def test_routes_plan():
    payload = {
        "origin": {"latitude": 22.7196, "longitude": 75.8577},
        "destination": {"latitude": 22.9734, "longitude": 76.0508},
        "prefer_safe_corridors": True
    }
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/v1/routes/plan", json=payload)
        assert response.status_code == 200
        res = response.json()
        assert res["success"] is True
        assert res["data"]["total_distance_km"] > 0
        assert "route_id" in res["data"]
