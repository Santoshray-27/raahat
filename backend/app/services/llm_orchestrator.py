import time
from typing import Optional, List, Tuple

from app.core.config import settings
from app.core.logging import logger
from app.schemas.emergency import EmergencyGuidance
from app.services.llm_providers import (
    GenerationRequest, 
    LLMResult, 
    GeminiProvider, 
    SarvamProvider, 
    GroqProvider,
    BaseLLMProvider
)
# Retain the deterministic fallback
from app.services.guidance import guidance_engine


class LLMOrchestrator:
    def __init__(self):
        self.providers: List[BaseLLMProvider] = []
        self.provider_timeout = settings.LLM_PROVIDER_TIMEOUT
        
        # Build the chain dynamically based on configured order
        order = [p.strip().lower() for p in settings.LLM_PROVIDER_ORDER.split(",")]
        
        for p in order:
            if p == "gemini":
                self.providers.append(GeminiProvider())
            elif p == "sarvam":
                self.providers.append(SarvamProvider())
            elif p == "groq":
                self.providers.append(GroqProvider())
                
    async def generate_emergency_guidance(self, prompt: str, language: str, category: str, severity: str) -> Tuple[EmergencyGuidance, str, int]:
        """
        Attempts to generate guidance through the LLM chain. 
        Falls back to deterministic engine if all fail.
        Returns: (EmergencyGuidance, provider_used_name, total_latency_ms)
        """
        start_time = time.time()
        request = GenerationRequest(prompt=prompt, language=language)
        
        for provider in self.providers:
            if not getattr(provider, 'is_configured', False):
                continue
                
            result = await provider.generate_guidance(request, timeout=self.provider_timeout)
            if result.success and result.guidance:
                total_latency = int((time.time() - start_time) * 1000)
                logger.info(f"LLMOrchestrator: Generated guidance via {result.provider_name} in {total_latency}ms")
                return result.guidance, result.provider_name, total_latency
            else:
                logger.info(f"LLMOrchestrator: {provider.provider_name} failed or unavailable. Moving to next.")
        
        # If all LLMs fail, use the deterministic fallback
        total_latency = int((time.time() - start_time) * 1000)
        logger.warning(f"LLMOrchestrator: All LLMs failed. Falling back to deterministic guidance.")
        
        from app.schemas.emergency import IncidentCategory, SeverityLevel
        try:
            cat_enum = IncidentCategory(category)
        except ValueError:
            cat_enum = IncidentCategory.OTHER
            
        try:
            sev_enum = SeverityLevel(severity)
        except ValueError:
            sev_enum = SeverityLevel.LOW
            
        deterministic_guidance = guidance_engine.get_guidance(cat_enum, sev_enum)
        return deterministic_guidance, "deterministic_keyword_fallback", total_latency

llm_orchestrator = LLMOrchestrator()
