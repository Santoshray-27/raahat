import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
import httpx
from app.main import app

@pytest.mark.asyncio
async def test_services_nearby():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/services/nearby?lat=22.7196&lng=75.8577&radius_km=10")
        assert response.status_code == 200
        res = response.json()
        assert res["success"] is True
        assert res["data"]["total_found"] > 0
        assert len(res["data"]["services"]) > 0

@pytest.mark.asyncio
async def test_services_search_post():
    payload = {
        "location": {"latitude": 22.7196, "longitude": 75.8577},
        "service_types": ["MECHANIC", "PUNCTURE_REPAIR"],
        "radius_km": 15.0,
        "limit": 5
    }
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/v1/services/search", json=payload)
        assert response.status_code == 200
        res = response.json()
        assert res["success"] is True
        assert res["data"]["total_found"] > 0
