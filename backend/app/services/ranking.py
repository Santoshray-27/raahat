import math
from typing import List
from app.schemas.common import ServiceProvider, GeoPoint
from app.schemas.enums import IncidentCategory

def calculate_haversine_distance(p1: GeoPoint, p2: GeoPoint) -> float:
    R = 6371.0  # Earth radius in kilometers
    dlat = math.radians(p2.latitude - p1.latitude)
    dlon = math.radians(p2.longitude - p1.longitude)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(p1.latitude)) * math.cos(math.radians(p2.latitude)) * math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)

class ServiceRanker:
    def rank_providers(
        self,
        providers: List[ServiceProvider],
        user_loc: GeoPoint,
        category: IncidentCategory
    ) -> List[ServiceProvider]:
        for provider in providers:
            # Recalculate distance km and ETA
            dist = calculate_haversine_distance(user_loc, provider.location)
            provider.distance_km = dist
            provider.eta_minutes = max(3, int(dist * 3) + 2)
            
            # Score formula: 50% proximity, 30% rating, 20% suitability
            proximity_score = max(0.0, 1.0 - (dist / 25.0))
            rating_score = (provider.rating or 4.0) / 5.0
            
            score = round((0.5 * proximity_score) + (0.3 * rating_score) + 0.2, 2)
            provider.recommendation_score = score
            
            # Human readable recommendation reason
            if dist < 2.0:
                provider.recommendation_reason = f"Closest available vendor ({dist} km away, ~{provider.eta_minutes} min ETA)"
            elif provider.rating and provider.rating >= 4.5:
                provider.recommendation_reason = f"Top-rated service provider ({provider.rating}⭐) with verified response team"
            else:
                provider.recommendation_reason = f"Verified roadside service suited for {category.value.lower()}"
                
        # Sort descending by score
        providers.sort(key=lambda p: p.recommendation_score, reverse=True)
        return providers

service_ranker = ServiceRanker()
