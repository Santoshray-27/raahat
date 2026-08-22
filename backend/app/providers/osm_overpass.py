import httpx, uuid
import urllib.parse
from datetime import datetime, timezone
from typing import List, Tuple
from app.core.logging import logger
from app.providers.base import BasePlacesProvider
from app.schemas.common import GeoPoint, ServiceProvider, LocationAddress, ContactInfo
from app.schemas.enums import ServiceType, ProviderSource
from app.services.ranking import calculate_haversine_distance

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
        radius_m = max(int(radius_km * 1000), 15000)
        
        main_type = service_types[0] if service_types else ServiceType.HOSPITAL
        tag_pairs = self._TAG_MAP.get(main_type, [("amenity", "hospital")])
        
        # Build node and way subqueries
        statements = []
        for k, v in tag_pairs:
            statements.append(f'node["{k}"="{v}"](around:{radius_m},{lat},{lon});')
            statements.append(f'way["{k}"="{v}"](around:{radius_m},{lat},{lon});')
        
        query = f"[out:json][timeout:10];({' '.join(statements)});out center tags {max(limit * 2, 15)};"
        encoded_data = urllib.parse.urlencode({"data": query})
        
        headers = {
            "User-Agent": "raahat-hackathon/1.0",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        for endpoint in self.ENDPOINTS:
            try:
                logger.info(f"OSMOverpassProvider: Attempting query for {main_type.value} on endpoint: {endpoint}")
                async with httpx.AsyncClient(timeout=10.0) as client:
                    resp = await client.post(endpoint, content=encoded_data, headers=headers)
                    if resp.status_code != 200:
                        logger.warning(f"OSM Overpass endpoint {endpoint} returned status {resp.status_code}. Trying next endpoint...")
                        continue
                        
                    data = resp.json()
                    elements = data.get("elements", [])
                    if not elements:
                        continue
                        
                    raw_results = []
                    for el in elements:
                        tags = el.get("tags", {})
                        name = tags.get("name") or tags.get("name:en") or f"Local {main_type.value.title()} Service"
                        name_lower = name.lower()

                        if main_type == ServiceType.HOSPITAL and tags.get("hospital:type") == "ayush":
                            continue
                            
                        # Extract coordinates (nodes have lat/lon, ways have center dict)
                        if "lat" in el and "lon" in el:
                            p_lat, p_lon = el["lat"], el["lon"]
                        elif "center" in el:
                            p_lat, p_lon = el["center"].get("lat", lat), el["center"].get("lon", lon)
                        else:
                            p_lat, p_lon = lat, lon
                            
                        loc = GeoPoint(latitude=p_lat, longitude=p_lon)
                        dist_km = round(calculate_haversine_distance(location, loc), 2)
                        phone = tags.get("phone") or tags.get("contact:phone") or None
                        
                        quality_score = 0.0
                        if main_type == ServiceType.HOSPITAL:
                            pos_keywords = ["hospital", "nursing", "care", "superspeciality", "हॉस्पिटल", "अस्पताल"]
                            neg_keywords = ["homeo", "ayush", "ayurved", "dental", "eye", "skin", "clinic", "चिकित्सालय", "होमियो"]
                            
                            if any(w in name_lower for w in pos_keywords):
                                quality_score += 0.5
                            if tags.get("emergency") == "yes":
                                quality_score += 0.5
                            if any(w in name_lower for w in neg_keywords):
                                quality_score -= 0.3
                                
                            if quality_score < 0:
                                continue

                        sp = ServiceProvider(
                            provider_id=f"osm_{el.get('type','n')}_{el.get('id', str(uuid.uuid4())[:8])}",
                            name=name,
                            service_types=[main_type.value],
                            location=loc,
                            address=LocationAddress(formatted_address=tags.get("addr:full") or tags.get("addr:street") or "OpenStreetMap Verified Location"),
                            contact=ContactInfo(phone_primary=phone),
                            distance_km=dist_km,
                            eta_minutes=max(1, int(dist_km * 2)),
                            rating=None,
                            review_count=0,
                            availability_status="UNKNOWN",
                            verification_status="UNVERIFIED",
                            recommendation_score=quality_score if main_type == ServiceType.HOSPITAL else 0.85,
                            recommendation_reason="OpenStreetMap Community Provider",
                            source=ProviderSource.OSM_OVERPASS,
                            is_cached=False,
                            retrieved_at=datetime.now(timezone.utc).isoformat()
                        )
                        raw_results.append((quality_score, sp))
                        
                    if raw_results:
                        if main_type == ServiceType.HOSPITAL:
                            sorted_items = sorted(raw_results, key=lambda x: (-x[0], x[1].distance_km))
                            return [item[1] for item in sorted_items][:limit]
                        else:
                            sorted_items = sorted(raw_results, key=lambda x: x[1].distance_km)
                            return [item[1] for item in sorted_items][:limit]
            except Exception as e:
                logger.warning(f"OSM Overpass endpoint {endpoint} failed: {e}. Trying next...")
                
        logger.error("OSM Overpass: All endpoints failed or returned no data.")
        return []
