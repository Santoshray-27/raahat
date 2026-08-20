import json, re
from typing import Tuple, List, Optional
import google.generativeai as genai
from app.core.config import settings
from app.core.logging import logger
from app.schemas.enums import IncidentCategory, SeverityLevel, ServiceType
from app.services.classifier import classifier as fallback_classifier

_gemini_model = None

def init_gemini():
    global _gemini_model
    if settings.GEMINI_API_KEY:
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            _gemini_model = genai.GenerativeModel("gemini-1.5-flash")
            logger.info("Server-side Gemini AI model initialized successfully.")
        except Exception as e:
            logger.warning(f"Failed to initialize Gemini AI model: {e}")

init_gemini()

class GeminiEnhancer:
    async def analyze_emergency(
        self, query: str
    ) -> Tuple[IncidentCategory, SeverityLevel, float, List[ServiceType], str]:
        # Always use deterministic classifier as primary or fallback
        det_category, det_severity, det_confidence, det_services = fallback_classifier.classify(query)
        
        if not _gemini_model:
            return det_category, det_severity, det_confidence, det_services, "deterministic_keyword"

        prompt = f"""
        You are RAAHAT emergency triage AI. Analyze this roadside emergency query in Hindi/Hinglish/English: "{query}".
        Categorize into one of: ACCIDENT, MEDICAL, PUNCTURE, BREAKDOWN, FUEL_EMPTY, STRANDED, ANIMAL_STRIKE, FIRE, WEATHER_HAZARD, OTHER.
        Determine severity: CRITICAL, HIGH, MEDIUM, LOW.
        Return ONLY valid JSON matching:
        {{"category": "PUNCTURE", "severity": "MEDIUM", "confidence": 0.95}}
        """

        try:
            response = _gemini_model.generate_content(prompt)
            match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if match:
                data = json.loads(match.group(0))
                gem_cat = IncidentCategory(data.get("category", det_category.value))
                gem_sev = SeverityLevel(data.get("severity", det_severity.value))
                gem_conf = float(data.get("confidence", 0.90))
                req_services = fallback_classifier._map_category_to_services(gem_cat, gem_sev)
                return gem_cat, gem_sev, gem_conf, req_services, "gemini_1.5_flash"
        except Exception as e:
            logger.warning(f"Gemini API analysis failed: {e}. Falling back to deterministic classifier.")

        return det_category, det_severity, det_confidence, det_services, "deterministic_keyword_fallback"

gemini_enhancer = GeminiEnhancer()
