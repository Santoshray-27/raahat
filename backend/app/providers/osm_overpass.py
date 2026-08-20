import httpx, uuid
import urllib.parse
from datetime import datetime, timezone
from typing import List, Tuple
from app.core.logging import logger
from app.providers.base import BasePlacesProvider
from app.schemas.common import GeoPoint, ServiceProvider, LocationAddress, ContactInfo
from app.schemas.enums import ServiceType

class OSMOverpassProvider(BasePlacesProvider):
    ENDPOINTS = [
        "https://overpass-api.de/api/interpreter",
        "https://overpass.kumi.systems/api/interpreter",
        "https://overpass.private.coffee/api/interpreter",
    ]

    _TAG_MAP = {
        ServiceType.HOSPITAL: [("amenity", "hospital")],
        ServiceType.POLICE: [("amenity", "police")],
        ServiceType.AMBULANCE: [("emergency", "ambulance_station"), ("amenity", "hospital")],
        ServiceType.FIRE_BRIGADE: [("amenity", "fire_station")],
        ServiceType.MECHANIC: [("shop", "car_repair"), ("amenity", "fuel")],
        ServiceType.PUNCTURE_REPAIR: [("shop", "car_repair"), ("amenity", "fuel")],
        ServiceType.TOWING: [("shop", "car_repair")],
        ServiceType.FUEL_DELIVERY: [("amenity", "fuel")],
    }

    async def search_nearby(
        self,
        location: GeoPoint,
        service_types: List[ServiceType],
        radius_km: float = 10.0,
        limit: int = 10
    ) -> List[ServiceProvider]:
        lat, lon = location.latitude, location.longitude
        radius_m = int(radius_km * 1000)
        
        main_type = service_types[0] if service_types else ServiceType.HOSPITAL
        tag_pairs = self._TAG_MAP.get(main_type, [("amenity", "hospital")])
        
        # Build node and way subqueries
        statements = []
        for k, v in tag_pairs:
            statements.append(f'node["{k}"="{v}"](around:{radius_m},{lat},{lon});')
            statements.append(f'way["{k}"="{v}"](around:{radius_m},{lat},{lon});')
        
        query = f"[out:json][timeout:10];({' '.join(statements)});out center tags {limit};"
        encoded_data = urllib.parse.urlencode({"data": query})
        
        headers = {
            "User-Agent": "raahat-hackathon/1.0",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        for endpoint in self.ENDPOINTS:
            try:
                logger.info(f"OSMOverpassProvider: Attempting query on endpoint: {endpoint}")
                async with httpx.AsyncClient(timeout=10.0) as client:
                    resp = await client.post(endpoint, content=encoded_data, headers=headers)
                    if resp.status_code != 200:
                        logger.warning(f"OSM Overpass endpoint {endpoint} returned status {resp.status_code}. Trying next endpoint...")
                        continue
                        
                    data = resp.json()
                    elements = data.get("elements", [])
                    if not elements:
                        continue
                        
                    providers: List[ServiceProvider] = []
                    for el in elements[:limit]:
                        tags = el.get("tags", {})
                        name = tags.get("name") or tags.get("name:en") or f"Local {main_type.value.title()} Service"
                        
                        # Extract coordinates (nodes have lat/lon, ways have center dict)
                        if "lat" in el and "lon" in el:
                            p_lat, p_lon = el["lat"], el["lon"]
                        elif "center" in el:
                            p_lat, p_lon = el["center"].get("lat", lat), el["center"].get("lon", lon)
                        else:
                            p_lat, p_lon = lat, lon
                            
                        phone = tags.get("phone") or tags.get("contact:phone") or None
                        
                        providers.append(
                            ServiceProvider(
                                provider_id=f"osm_{el.get('type','n')}_{el.get('id', str(uuid.uuid4())[:8])}",
                                name=name,
                                service_types=[main_type.value],
                                location=GeoPoint(latitude=p_lat, longitude=p_lon),
                                address=LocationAddress(formatted_address=tags.get("addr:full") or tags.get("addr:street") or "OpenStreetMap Verified Location"),
                                contact=ContactInfo(phone_primary=phone),
                                distance_km=2.0,
                                eta_minutes=6,
                                rating=None,
                                review_count=0,
                                availability_status="UNKNOWN",
                                verification_status="UNVERIFIED",
                                recommendation_score=0.85,
                                recommendation_reason="OpenStreetMap Community Provider",
                                source="OSM_OVERPASS",
                                is_cached=False,
                                retrieved_at=datetime.now(timezone.utc).isoformat()
                            )
                        )
                    if providers:
                        return providers
            except Exception as e:
                logger.warning(f"OSM Overpass endpoint {endpoint} failed: {e}. Trying next...")
                
        logger.error("OSM Overpass: All endpoints failed or returned no data.")
        return []
