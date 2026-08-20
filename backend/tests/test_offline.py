import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
import httpx
from app.main import app

@pytest.mark.asyncio
async def test_offline_pack_creation_and_download():
    payload = {
        "region_name": "Indore Expressway Corridor",
        "bounding_box": [
            {"latitude": 22.70, "longitude": 75.80},
            {"latitude": 22.80, "longitude": 75.90}
        ],
        "include_categories": ["MECHANIC", "HOSPITAL", "AMBULANCE"]
    }
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/v1/offline-packs", json=payload)
        assert response.status_code == 200
        res = response.json()
        assert res["success"] is True
        pack_id = res["data"]["manifest"]["pack_id"]
        checksum = res["data"]["manifest"]["sha256_checksum"]
        assert len(checksum) == 64  # SHA256 hex string length
        
        # Download check
        dl_response = await client.get(f"/api/v1/offline-packs/{pack_id}/download")
        assert dl_response.status_code == 200
        assert dl_response.headers["content-type"].startswith("application/json")

@pytest.mark.asyncio
async def test_offline_pack_schema_variations():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        # 1. Dict format
        payload_dict = {
            "region_name": "Test1",
            "bounding_box": {"min_lat": 22.7, "min_lng": 75.8, "max_lat": 22.8, "max_lng": 75.9}
        }
        res1 = await client.post("/api/v1/offline-packs", json=payload_dict)
        assert res1.status_code == 200
        
        # 2. Omitted bounding box with route_id
        payload_route = {
            "region_name": "Test2",
            "route_id": "demo_route_123"
        }
        res2 = await client.post("/api/v1/offline-packs", json=payload_route)
        assert res2.status_code == 200
        
        # 3. Invalid - neither route_id nor bounding_box
        payload_invalid = {
            "region_name": "Test3"
        }
        res3 = await client.post("/api/v1/offline-packs", json=payload_invalid)
        assert res3.status_code == 422
