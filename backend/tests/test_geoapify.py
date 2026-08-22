import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from app.providers.geoapify import GeoapifyPlacesProvider, GeoapifyRoutingProvider, GeoapifyProviderError
from app.providers.manager import provider_manager
from app.schemas.common import GeoPoint
from app.schemas.enums import ServiceType, ProviderSource
from app.core.config import settings

@pytest.fixture
def mock_places_response():
    return {
        "features": [
            {
                "properties": {
                    "place_id": "test_id_123",
                    "name": "Test Hospital",
                    "distance": 1500,
                    "lat": 22.7,
                    "lon": 75.8,
                    "address_line1": "123 Test St",
                    "city": "Indore"
                }
            }
        ]
    }

@pytest.fixture
def mock_routing_response():
    return {
        "features": [
            {
                "properties": {
                    "distance": 5000,
                    "time": 600
                },
                "geometry": {
                    "coordinates": [[[75.8, 22.7], [75.9, 22.8]]]
                }
            }
        ]
    }

@pytest.mark.asyncio
async def test_geoapify_places_normalization(mock_places_response):
    provider = GeoapifyPlacesProvider()
    location = GeoPoint(latitude=22.7196, longitude=75.8577)
    
    with patch("app.providers.geoapify.settings.GEOAPIFY_API_KEY", "dummy_key"):
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_resp = MagicMock(status_code=200)
            mock_resp.json.return_value = mock_places_response
            mock_get.return_value = mock_resp
            
            res = await provider.search_nearby(location, [ServiceType.HOSPITAL])
            assert len(res) == 1
            assert res[0].name == "Test Hospital"
            assert res[0].source == ProviderSource.GEOAPIFY
            assert res[0].distance_km == 1.5
            assert res[0].availability_status == "UNKNOWN"

@pytest.mark.asyncio
async def test_geoapify_places_error():
    provider = GeoapifyPlacesProvider()
    location = GeoPoint(latitude=22.7196, longitude=75.8577)
    
    with patch("app.providers.geoapify.settings.GEOAPIFY_API_KEY", "dummy_key"):
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_resp = MagicMock(status_code=401)
            mock_get.return_value = mock_resp
            
            with pytest.raises(GeoapifyProviderError):
                await provider.search_nearby(location, [ServiceType.HOSPITAL])

@pytest.mark.asyncio
async def test_geoapify_routing_normalization(mock_routing_response):
    provider = GeoapifyRoutingProvider()
    origin = GeoPoint(latitude=22.7196, longitude=75.8577)
    dest = GeoPoint(latitude=22.8, longitude=75.9)
    
    with patch("app.providers.geoapify.settings.GEOAPIFY_API_KEY", "dummy_key"):
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_resp = MagicMock(status_code=200)
            mock_resp.json.return_value = mock_routing_response
            mock_get.return_value = mock_resp
            
            res = await provider.plan_route(origin, dest)
            assert res.provider_source == ProviderSource.GEOAPIFY
            assert res.total_distance_km == 5.0
            assert res.total_duration_minutes == 10.0

@pytest.mark.asyncio
async def test_manager_chain_order():
    location = GeoPoint(latitude=22.7196, longitude=75.8577)
    
    # Test with Geoapify key present
    with patch("app.providers.manager.settings.USE_MOCKS", False), \
         patch("app.providers.manager.settings.GEOAPIFY_API_KEY", "dummy"):
        
        # Geoapify succeeds
        with patch.object(provider_manager.geoapify_places, "search_nearby", return_value=[MagicMock(source="GEOAPIFY", location=location)]) as mock_geo, \
             patch.object(provider_manager.osm_overpass, "search_nearby") as mock_osm:
            
            res, src = await provider_manager.get_nearby_services(location, [ServiceType.HOSPITAL])
            assert src == "GEOAPIFY"
            mock_geo.assert_called_once()
            mock_osm.assert_not_called()

    # Test with Geoapify key absent
    with patch("app.providers.manager.settings.USE_MOCKS", False), \
         patch("app.providers.manager.settings.GEOAPIFY_API_KEY", ""):
        
        # Geoapify is skipped, OSM succeeds
        with patch.object(provider_manager.geoapify_places, "search_nearby") as mock_geo, \
             patch.object(provider_manager.osm_overpass, "search_nearby", return_value=[MagicMock(source="OSM_OVERPASS", location=location)]) as mock_osm:
            
            res, src = await provider_manager.get_nearby_services(location, [ServiceType.HOSPITAL])
            assert src == "OSM_OVERPASS"
            mock_geo.assert_not_called()
            mock_osm.assert_called_once()
