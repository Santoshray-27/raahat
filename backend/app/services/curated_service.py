import json
import pathlib
from typing import List
from datetime import datetime, timezone
from app.core.logging import logger
from app.schemas.common import GeoPoint, ServiceProvider, LocationAddress, ContactInfo
from app.schemas.enums import ServiceType, ProviderSource, AvailabilityStatus, VerificationStatus
from app.services.ranking import calculate_haversine_distance

_CURATED_FILE = pathlib.Path(__file__).parent.parent.parent / "data" / "curated_providers.json"

class CuratedProviderManager:
    def __init__(self):
        self._providers = []
        self._load()

    def _load(self):
        if not _CURATED_FILE.exists():
            logger.warning(f"Curated file not found at {_CURATED_FILE}")
            return
        try:
            with open(_CURATED_FILE, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
                self._providers = raw_data
        except Exception as e:
            logger.error(f"Failed to load curated providers: {e}")

    def get_fallback_providers(
        self,
        location: GeoPoint,
        service_types: List[ServiceType],
        limit: int = 5
    ) -> List[ServiceProvider]:
        if not self._providers:
            self._load()
            
        requested_type_strings = [st.value for st in service_types] if service_types else []
        matches = []
        
        for item in self._providers:
            item_types = item.get("service_types", [])
            # Check match or general emergency
            if not requested_type_strings or any(t in item_types for t in requested_type_strings):
                loc = GeoPoint(
                    latitude=item["location"]["latitude"],
                    longitude=item["location"]["longitude"]
                )
                dist_km = calculate_haversine_distance(location, loc)
                
                sp = ServiceProvider(
                    provider_id=item["provider_id"],
                    name=item["name"],
                    service_types=item["service_types"],
                    location=loc,
                    address=LocationAddress(
                        formatted_address=item["address"].get("formatted_address"),
                        city=item["address"].get("city"),
                        state=item["address"].get("state"),
                        country=item["address"].get("country", "India")
                    ),
                    contact=ContactInfo(
                        phone_primary=item["contact"].get("phone_primary"),
                        emergency_shortcode=item["contact"].get("emergency_shortcode")
                    ),
                    distance_km=dist_km,
                    eta_minutes=max(2, int(dist_km * 2)),
                    rating=item.get("rating"),
                    review_count=item.get("review_count", 0),
                    availability_status=AvailabilityStatus.UNKNOWN,
                    verification_status=VerificationStatus.VERIFIED,
                    recommendation_score=item.get("recommendation_score", 0.90),
                    recommendation_reason=item.get("recommendation_reason", "Verified Indore Emergency Service"),
                    source=ProviderSource.CURATED,
                    is_cached=False,
                    retrieved_at=datetime.now(timezone.utc).isoformat()
                )
                matches.append(sp)
                
        # Sort ascending by distance
        matches.sort(key=lambda p: p.distance_km)
        return matches[:limit]

curated_provider_manager = CuratedProviderManager()
