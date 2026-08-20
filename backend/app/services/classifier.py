import re
from typing import Tuple, List
from app.schemas.enums import IncidentCategory, SeverityLevel, ServiceType

# Keyword mappings for English, Hindi, and Hinglish
KEYWORDS_MAP = {
    IncidentCategory.PUNCTURE: [
        "puncture", "puncutre", "puncher", "flat tire", "flat tyre", "wheel burst", "tyre burst",
        "tyre kharab", "hawa nikal gayi", "tyre puncture", "puncutar", "puncature"
    ],
    IncidentCategory.ACCIDENT: [
        "accident", "crash", "collision", "hit", "thok diya", "gaadi takrai", "accident ho gaya",
        "takkar", "injured", "injury", "bleeding", "khoon", "fracture", "chot lag gayi"
    ],
    IncidentCategory.MEDICAL: [
        "medical", "doctor", "ambulance", "hospital", "patient", "chest pain", "unconscious",
        "bimar", "tabiyat kharab", "heart attack", "breathless", "sans nahi aa rahi"
    ],
    IncidentCategory.BREAKDOWN: [
        "breakdown", "engine fail", "gaadi band", "smoke", "starter motor", "clutch wire",
        "engine overheat", "gaadi start nahi ho rahi", "sound from engine", "towing"
    ],
    IncidentCategory.FUEL_EMPTY: [
        "fuel", "petrol", "diesel", "empty tank", "petrol khatam", "diesel khatam", "tel khatam",
        "no fuel", "gas station"
    ],
    IncidentCategory.STRANDED: [
        "stranded", "stuck", "isolated", "jungle", "highway late night", "akela", "fasa hua",
        " सुनसान", "raat ko fasa"
    ],
    IncidentCategory.FIRE: [
        "fire", "smoke from engine", "aag", "gaadi me aag", "burning smell", "fire brigade"
    ]
}

CRITICAL_TRIGGER_WORDS = [
    "bleeding", "khoon", "unconscious", "head injury", "headache severe", "fire", "aag",
    "heart attack", "chest pain", "sans nahi", "severe accident", "multiple vehicles"
]

HIGH_TRIGGER_WORDS = [
    "accident", "fracture", "chot", "smoke", "stranded late night", "highway emergency"
]

class IncidentClassifier:
    def classify(self, query: str) -> Tuple[IncidentCategory, SeverityLevel, float, List[ServiceType]]:
        query_lower = query.lower()
        
        # 1. Determine Category
        detected_category = IncidentCategory.OTHER
        max_matches = 0
        
        for category, keywords in KEYWORDS_MAP.items():
            matches = sum(1 for kw in keywords if re.search(r'\b' + re.escape(kw) + r'\b', query_lower) or kw in query_lower)
            if matches > max_matches:
                max_matches = matches
                detected_category = category
                
        # Default fallback if no match found
        if detected_category == IncidentCategory.OTHER:
            if "help" in query_lower or "madad" in query_lower or "emergency" in query_lower:
                detected_category = IncidentCategory.BREAKDOWN

        # 2. Determine Severity
        severity = SeverityLevel.MEDIUM
        
        if any(kw in query_lower for kw in CRITICAL_TRIGGER_WORDS):
            severity = SeverityLevel.CRITICAL
        elif any(kw in query_lower for kw in HIGH_TRIGGER_WORDS):
            severity = SeverityLevel.HIGH
        elif detected_category == IncidentCategory.PUNCTURE or detected_category == IncidentCategory.FUEL_EMPTY:
            severity = SeverityLevel.LOW

        # 3. Map to Required Service Types
        required_services = self._map_category_to_services(detected_category, severity)
        
        confidence = 0.95 if max_matches > 0 else 0.70
        
        return detected_category, severity, confidence, required_services

    def _map_category_to_services(self, category: IncidentCategory, severity: SeverityLevel) -> List[ServiceType]:
        if severity == SeverityLevel.CRITICAL or category == IncidentCategory.MEDICAL:
            return [ServiceType.AMBULANCE, ServiceType.HOSPITAL, ServiceType.POLICE]
            
        if category == IncidentCategory.ACCIDENT:
            return [ServiceType.AMBULANCE, ServiceType.POLICE, ServiceType.TOWING]
            
        if category == IncidentCategory.PUNCTURE:
            return [ServiceType.PUNCTURE_REPAIR, ServiceType.MECHANIC, ServiceType.TOWING]
            
        if category == IncidentCategory.BREAKDOWN:
            return [ServiceType.MECHANIC, ServiceType.TOWING, ServiceType.REST_STOP]
            
        if category == IncidentCategory.FUEL_EMPTY:
            return [ServiceType.FUEL_DELIVERY, ServiceType.REST_STOP]
            
        if category == IncidentCategory.FIRE:
            return [ServiceType.FIRE_BRIGADE, ServiceType.POLICE, ServiceType.AMBULANCE]
            
        return [ServiceType.MECHANIC, ServiceType.TOWING]

classifier = IncidentClassifier()
