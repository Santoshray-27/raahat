import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
import httpx
from app.main import app

@pytest.mark.asyncio
async def test_emergency_puncture():
    payload = {
        "user_query": "Tyre puncture ho gaya hai highway par, urgent repair chahiye",
        "location": {"latitude": 22.7196, "longitude": 75.8577},
        "language": "hi"
    }
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/v1/emergency-assistance", json=payload)
        assert response.status_code == 200
        res = response.json()
        assert res["success"] is True
        data = res["data"]
        assert data["incident"]["category"] == "PUNCTURE"
        assert data["incident"]["severity"] in ["LOW", "MEDIUM"]
        assert len(data["guidance"]["steps"]) > 0
        assert len(data["services"]) > 0
        assert data["services"][0]["availability_status"] == "UNKNOWN"
        assert data["services"][0]["source"] in ["GOOGLE_PLACES", "GEOAPIFY", "OSM_OVERPASS"]
        assert data["services"][0]["source"] != "MOCK"
        
        # Extra Check: Ensure relevant categories for Puncture (Not Hospital first)
        first_service_types = data["services"][0]["service_types"]
        assert "HOSPITAL" not in first_service_types, "Hospital should not be the top service for a puncture"
        assert any(t in first_service_types for t in ["PUNCTURE_REPAIR", "MECHANIC", "TOWING"])

@pytest.mark.asyncio
async def test_emergency_accident_critical():
    payload = {
        "user_query": "Heavy car accident near bypass, bleeding profusely and unconscious victim",
        "location": {"latitude": 22.7196, "longitude": 75.8577}
    }
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/v1/emergency-assistance", json=payload)
        assert response.status_code == 200
        res = response.json()
        data = res["data"]
        assert data["incident"]["category"] in ["ACCIDENT", "MEDICAL"]
        assert data["incident"]["severity"] == "CRITICAL"
        assert data["incident"]["is_life_threatening"] is True
        assert any(a["target_contact"] == "112" for a in data["recommended_actions"])

@pytest.mark.asyncio
async def test_emergency_validation_error():
    payload = {
        "user_query": "a",  # min length 2 required
        "location": {"latitude": 999.0, "longitude": 75.8577}  # Invalid latitude > 90
    }
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/v1/emergency-assistance", json=payload)
        assert response.status_code == 422
        res = response.json()
        assert res["success"] is False
        assert res["error"]["code"] == "VALIDATION_ERROR"
