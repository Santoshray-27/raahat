import json, re
from typing import Tuple, List, Optional
import google.generativeai as genai
from app.core.config import settings
from app.core.logging import logger
from app.schemas.enums import IncidentCategory, SeverityLevel, ServiceType
from app.services.classifier import classifier as fallback_classifier

_gemini_model = None
_active_model_name = "rule-fallback"

def init_gemini():
    global _gemini_model, _active_model_name
    if settings.GEMINI_API_KEY:
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            
            # Model fall-through candidate list
            candidates = [
                getattr(settings, "GEMINI_MODEL", "gemini-flash-latest"),
                "gemini-flash-latest",
                "gemini-2.5-flash",
                "gemini-3.5-flash"
            ]
            
            # Remove duplicates preserving order
            unique_candidates = []
            for c in candidates:
                if c and c not in unique_candidates:
                    unique_candidates.append(c)
            
            for candidate in unique_candidates:
                try:
                    model = genai.GenerativeModel(candidate)
                    _gemini_model = model
                    _active_model_name = candidate
                    logger.info(f"Server-side Gemini AI model initialized successfully with '{candidate}'.")
                    break
                except Exception as ex:
                    logger.info(f"Gemini candidate '{candidate}' failed: {ex}. Trying next candidate...")
            
            if not _gemini_model:
                _active_model_name = "rule-fallback"
                logger.warning("No candidate Gemini model succeeded. Falling back to rule-fallback.")
        except Exception as e:
            _active_model_name = "rule-fallback"
            logger.warning(f"Failed to initialize Gemini AI: {e}")

init_gemini()

class GeminiEnhancer:
    def get_active_model(self) -> str:
        return _active_model_name if _gemini_model else "rule-fallback"

    async def analyze_emergency(
        self, query: str, history: Optional[List[dict]] = None
    ) -> Tuple[IncidentCategory, SeverityLevel, float, List[ServiceType], str]:
        # Always use deterministic classifier as primary or fallback
        det_category, det_severity, det_confidence, det_services = fallback_classifier.classify(query)
        
        if not _gemini_model:
            return det_category, det_severity, det_confidence, det_services, "rule-fallback"

        history_str = ""
        if history:
            history_str = "Prior Conversation History:\n"
            for msg in history[-5:]: # last 5 exchanges
                history_str += f"{msg['role']}: {msg['content']}\n"

        prompt = f"""
        You are RAAHAT emergency triage AI.
        {history_str}
        
        Analyze this roadside emergency query in Hindi/Hinglish/English: "{query}".
        Categorize into one of: ACCIDENT, MEDICAL, PUNCTURE, BREAKDOWN, FUEL_EMPTY, STRANDED, ANIMAL_STRIKE, FIRE, WEATHER_HAZARD, OTHER.
        Determine severity: CRITICAL, HIGH, MEDIUM, LOW.
        Return ONLY valid JSON matching:
        {{"category": "PUNCTURE", "severity": "MEDIUM", "confidence": 0.95}}
        """

        try:
            response = await _gemini_model.generate_content_async(prompt)
            match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if match:
                data = json.loads(match.group(0))
                gem_cat = IncidentCategory(data.get("category", det_category.value))
                gem_sev = SeverityLevel(data.get("severity", det_severity.value))
                gem_conf = float(data.get("confidence", 0.90))
                req_services = fallback_classifier._map_category_to_services(gem_cat, gem_sev)
                return gem_cat, gem_sev, gem_conf, req_services, _active_model_name
        except Exception as e:
            logger.warning(f"Gemini API analysis failed: {e}. Falling back to deterministic classifier.")

        return det_category, det_severity, det_confidence, det_services, "rule-fallback"

gemini_enhancer = GeminiEnhancer()
