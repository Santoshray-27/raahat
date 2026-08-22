import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
import asyncio
import httpx
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.common import GeoPoint
from app.schemas.enums import ServiceType
from app.providers.manager import provider_manager
from unittest.mock import patch, AsyncMock

# client = TestClient(app)

from app.main import generic_exception_handler
import json

@pytest.mark.asyncio
async def test_generic_exception_handler_does_not_leak_details():
    """
    Test that an unhandled exception returns a 500 error without exposing
    the raw exception string to the client.
    """
    class MockRequest:
        def __init__(self):
            self.url = type("URL", (), {"path": "/test/crash"})()
            self.state = type("State", (), {"request_id": "1234"})()
            
    req = MockRequest()
    exc = RuntimeError("SENSITIVE_DATABASE_URL=postgres://user:pass@localhost:5432/db")
    
    response = await generic_exception_handler(req, exc)
    
    assert response.status_code == 500
    data = json.loads(response.body)
    
    assert data["error"]["code"] == "INTERNAL_SERVER_ERROR"
    assert "SENSITIVE" not in str(data)
    assert data["error"]["details"]["error"] == "A server error was recorded and will be investigated."


@pytest.mark.asyncio
async def test_provider_manager_global_timeout():
    """
    Test that the provider manager global timeout works and returns gracefully.
    """
    location = GeoPoint(latitude=22.7196, longitude=75.8577)
    service_types = [ServiceType.HOSPITAL]
    
    async def slow_mock_provider(*args, **kwargs):
        # Sleep for longer than the global SLA timeout (12 seconds)
        await asyncio.sleep(13.0)
        return []

    # Mock all providers to take 13 seconds (exceeding SLA)
    with patch.object(provider_manager.geoapify_places, "search_nearby", side_effect=slow_mock_provider), \
         patch.object(provider_manager.osm_overpass, "search_nearby", side_effect=slow_mock_provider):
        
        # This should hit the asyncio.TimeoutError and return gracefully (curated fallback)
        results, source = await provider_manager.get_nearby_services(location, service_types)
        
        assert source == "CURATED"

@pytest.mark.asyncio
async def test_provider_manager_first_timeout_fallback_works():
    """
    Test that if Geoapify fails, fallback to OSM Overpass happens.
    """
    location = GeoPoint(latitude=22.7196, longitude=75.8577)
    service_types = [ServiceType.HOSPITAL]
    
    async def geoapify_fail(*args, **kwargs):
        raise Exception("Geoapify failed")
        
    async def osm_success(*args, **kwargs):
        from app.schemas.common import ServiceProvider, LocationAddress, ContactInfo
        from datetime import datetime, timezone
        return [
            ServiceProvider(
                provider_id="fake_1",
                name="Fake OSM",
                service_types=[ServiceType.HOSPITAL.value],
                location=location,
                address=LocationAddress(formatted_address="Fake Address"),
                contact=ContactInfo(phone_primary="1234567890"),
                distance_km=1.0,
                eta_minutes=2,
                availability_status="UNKNOWN",
                source="OSM_OVERPASS",
                is_cached=False,
                retrieved_at=datetime.now(timezone.utc).isoformat()
            )
        ]

    with patch.object(provider_manager.geoapify_places, "search_nearby", side_effect=geoapify_fail), \
         patch.object(provider_manager.osm_overpass, "search_nearby", side_effect=osm_success):
        
        results, source = await provider_manager.get_nearby_services(location, service_types)
        
        assert len(results) == 1
        assert source == "OSM_OVERPASS"
