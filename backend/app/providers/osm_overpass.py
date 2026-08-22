import httpx
import uuid
import urllib.parse
from datetime import datetime, timezone
from typing import List
from app.core.logging import logger
from app.providers.base import BasePlacesProvider
from app.schemas.common import GeoPoint, ServiceProvider, LocationAddress, ContactInfo
from app.schemas.enums import ServiceType, ProviderSource
from app.services.ranking import calculate_haversine_distance


class OSMOverpassProvider(BasePlacesProvider):
    """
    OpenStreetMap Overpass fallback provider.

    Tag mapping based on real OSM tagging conventions for India:
      shop=car_repair       → mechanics, puncture repair, towing depots
      shop=tyres            → dedicated tyre shops
      craft=car_repair      → smaller independent garages
      amenity=fuel          → petrol stations (carry puncture kits)
      amenity=hospital      → hospitals
      amenity=police        → police stations
      amenity=fire_station  → fire stations
      emergency=ambulance_station → ambulance depots

    Endpoints are tried in order; the first successful response wins.
    The primary Overpass endpoint is fast; kumi/private.coffee are community mirrors.
    """

    ENDPOINTS = [
        "https://lz4.overpass-api.de/api/interpreter",
        "https://z.overpass-api.de/api/interpreter",
        "https://overpass-api.de/api/interpreter",
        "https://overpass.kumi.systems/api/interpreter",
    ]

    # OSM tag map: ServiceType -> list of (key, value) tuples
    # Multiple pairs produce a UNION query (all results for all pairs).
    _TAG_MAP: dict = {
        ServiceType.HOSPITAL: [
            ("amenity", "hospital"),
        ],
        ServiceType.POLICE: [
            ("amenity", "police"),
        ],
        ServiceType.AMBULANCE: [
            ("emergency", "ambulance_station"),
            ("amenity", "hospital"),
        ],
        ServiceType.FIRE_BRIGADE: [
            ("amenity", "fire_station"),
        ],
        # MECHANIC: car_repair shops and garages are the primary source
        ServiceType.MECHANIC: [
            ("shop", "car_repair"),
            ("craft", "car_repair"),
        ],
        # PUNCTURE_REPAIR: tyre shops + general car_repair (they universally
        # do puncture work in India)
        ServiceType.PUNCTURE_REPAIR: [
            ("shop", "tyres"),
            ("shop", "car_repair"),
            ("craft", "car_repair"),
        ],
        # TOWING: same depots that handle car repair also tow
        ServiceType.TOWING: [
            ("shop", "car_repair"),
            ("craft", "car_repair"),
        ],
        ServiceType.FUEL_DELIVERY: [
            ("amenity", "fuel"),
        ],
    }

    # Per-type name/tag fallback labels when the OSM name tag is absent
    _DEFAULT_NAME: dict = {
        ServiceType.HOSPITAL: "Local Hospital",
        ServiceType.POLICE: "Police Station",
        ServiceType.AMBULANCE: "Ambulance Station",
        ServiceType.FIRE_BRIGADE: "Fire Station",
        ServiceType.MECHANIC: "Auto Workshop",
        ServiceType.PUNCTURE_REPAIR: "Tyre & Puncture Shop",
        ServiceType.TOWING: "Towing Service",
        ServiceType.FUEL_DELIVERY: "Petrol Station",
    }

    def _build_query(
        self,
        tag_pairs: List[tuple],
        lat: float,
        lon: float,
        radius_m: int,
        result_limit: int,
    ) -> str:
        """Build an Overpass QL union query for node+way with center coords."""
        parts = []
        for k, v in tag_pairs:
            parts.append(f'node["{k}"="{v}"](around:{radius_m},{lat},{lon});')
            parts.append(f'way["{k}"="{v}"](around:{radius_m},{lat},{lon});')
        inner = " ".join(parts)
        # 'out center' makes way centroids available as lat/lon
        return f"[out:json][timeout:20];({inner});out center tags {result_limit};"

    async def search_nearby(
        self,
        location: GeoPoint,
        service_types: List[ServiceType],
        radius_km: float = 10.0,
        limit: int = 10,
    ) -> List[ServiceProvider]:
        lat, lon = location.latitude, location.longitude
        # Minimum 15 km radius to find sparse services in Indian cities
        radius_m = max(int(radius_km * 1000), 15000)
        result_limit = max(limit * 2, 20)

        main_type = service_types[0] if service_types else ServiceType.HOSPITAL
        tag_pairs = self._TAG_MAP.get(main_type, [("amenity", "hospital")])
        default_name = self._DEFAULT_NAME.get(main_type, "Local Service")

        query = self._build_query(tag_pairs, lat, lon, radius_m, result_limit)
        encoded_data = urllib.parse.urlencode({"data": query})
        headers = {
            "User-Agent": "raahat-hackathon/1.0",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        for endpoint in self.ENDPOINTS:
            try:
                logger.info(
                    f"OSMOverpass: querying {main_type.value} via {endpoint}"
                )
                async with httpx.AsyncClient(timeout=20.0) as client:
                    resp = await client.post(
                        endpoint, content=encoded_data, headers=headers
                    )

                if resp.status_code != 200:
                    logger.warning(
                        f"OSMOverpass: endpoint {endpoint} returned HTTP "
                        f"{resp.status_code}. Trying next…"
                    )
                    continue

                data = resp.json()
                elements = data.get("elements", [])
                if not elements:
                    logger.info(
                        f"OSMOverpass: {endpoint} returned 0 elements for "
                        f"{main_type.value}. Trying next…"
                    )
                    continue

                raw_results = []
                for el in elements:
                    tags = el.get("tags", {})

                    # Skip AYUSH/homeopathy hospitals
                    if (
                        main_type == ServiceType.HOSPITAL
                        and tags.get("hospital:type") == "ayush"
                    ):
                        continue

                    # Resolve coordinates: nodes have lat/lon; ways have center
                    if "lat" in el and "lon" in el:
                        p_lat, p_lon = float(el["lat"]), float(el["lon"])
                    elif "center" in el and "lat" in el["center"]:
                        p_lat = float(el["center"]["lat"])
                        p_lon = float(el["center"]["lon"])
                    else:
                        # Cannot determine position — skip
                        continue

                    loc = GeoPoint(latitude=p_lat, longitude=p_lon)
                    dist_km = round(calculate_haversine_distance(location, loc), 2)

                    name = (
                        tags.get("name")
                        or tags.get("name:en")
                        or tags.get("operator")
                        or default_name
                    )
                    name_lower = name.lower()

                    phone = tags.get("phone") or tags.get("contact:phone") or None

                    # Hospital quality scoring
                    quality_score = 0.0
                    if main_type == ServiceType.HOSPITAL:
                        pos_kw = ["hospital", "nursing", "care", "superspeciality",
                                  "हॉस्पिटल", "अस्पताल"]
                        neg_kw = ["homeo", "ayush", "ayurved", "dental", "eye",
                                  "skin", "clinic", "चिकित्सालय", "होमियो"]
                        if any(w in name_lower for w in pos_kw):
                            quality_score += 0.5
                        if tags.get("emergency") == "yes":
                            quality_score += 0.5
                        if any(w in name_lower for w in neg_kw):
                            quality_score -= 0.3
                        if quality_score < 0:
                            continue

                    street = tags.get("addr:street") or tags.get("addr:full") or None
                    city = tags.get("addr:city") or None
                    postcode = tags.get("addr:postcode") or None

                    sp = ServiceProvider(
                        provider_id=(
                            f"osm_{el.get('type', 'n')}_{el.get('id', uuid.uuid4().hex[:8])}"
                        ),
                        name=name,
                        service_types=[main_type.value],
                        location=loc,
                        address=LocationAddress(
                            formatted_address=street,
                            street_name=street,
                            city=city,
                            postal_code=postcode,
                            country="India",
                        ),
                        contact=ContactInfo(phone_primary=phone),
                        distance_km=dist_km,
                        eta_minutes=max(1, int(dist_km * 2)),
                        rating=None,
                        review_count=0,
                        availability_status="UNKNOWN",
                        verification_status="UNVERIFIED",
                        recommendation_score=(
                            quality_score if main_type == ServiceType.HOSPITAL else 0.80
                        ),
                        recommendation_reason="OpenStreetMap Community Provider",
                        source=ProviderSource.OSM_OVERPASS,
                        is_cached=False,
                        retrieved_at=datetime.now(timezone.utc).isoformat(),
                    )
                    raw_results.append((quality_score, sp))

                if not raw_results:
                    logger.info(
                        f"OSMOverpass: all elements filtered out for {main_type.value} "
                        f"on {endpoint}. Trying next…"
                    )
                    continue

                # Sort
                if main_type == ServiceType.HOSPITAL:
                    raw_results.sort(key=lambda x: (-x[0], x[1].distance_km))
                else:
                    raw_results.sort(key=lambda x: x[1].distance_km)

                providers = [item[1] for item in raw_results][:limit]
                logger.info(
                    f"OSMOverpass: returning {len(providers)} providers for "
                    f"{main_type.value} via {endpoint}"
                )
                return providers

            except httpx.TimeoutException:
                logger.warning(
                    f"OSMOverpass: timeout on {endpoint} for {main_type.value}. "
                    "Trying next endpoint…"
                )
            except Exception as e:
                logger.warning(
                    f"OSMOverpass: endpoint {endpoint} failed: {e}. Trying next…"
                )

        logger.warning(
            f"OSMOverpass: all endpoints exhausted for {main_type.value}. "
            "Returning empty list — curated fallback will be used."
        )
        return []
