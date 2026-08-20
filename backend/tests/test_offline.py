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
