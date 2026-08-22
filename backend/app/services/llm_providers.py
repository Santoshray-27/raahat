import abc
import json
import time
import re
from typing import Optional, Dict, Any, Type
import httpx
import asyncio

from pydantic import BaseModel, ValidationError

# Using the existing schema
from app.schemas.emergency import EmergencyGuidance
from app.core.config import settings
from app.core.logging import logger

# Import specific provider exceptions we want to catch gracefully
try:
    from google.api_core.exceptions import ResourceExhausted, ServiceUnavailable
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    
try:
    from groq import AsyncGroq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False


class GenerationRequest(BaseModel):
    prompt: str
    language: str


class LLMResult(BaseModel):
    guidance: Optional[EmergencyGuidance] = None
    provider_name: str
    latency_ms: int
    success: bool
    error_message: Optional[str] = None


class BaseLLMProvider(abc.ABC):
    @abc.abstractmethod
    async def generate_guidance(self, request: GenerationRequest, timeout: float) -> LLMResult:
        pass

    def _extract_json(self, text: str) -> str:
        """Strips markdown code blocks to safely extract JSON."""
        text = text.strip()
        match = re.search(r'```(?:json)?\s*(.*?)\s*```', text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return text

    def _validate_output(self, text: str) -> EmergencyGuidance:
        """Extracts JSON and strictly validates it against the schema."""
        clean_json = self._extract_json(text)
        try:
            return EmergencyGuidance.model_validate_json(clean_json)
        except ValidationError as e:
            logger.error(f"Failed to validate {self.__class__.__name__} output: {e}")
            raise


class GeminiProvider(BaseLLMProvider):
    _permanently_failed = False
    
    def __init__(self):
        self.provider_name = "gemini"
        self.is_configured = bool(settings.GEMINI_API_KEY) and GEMINI_AVAILABLE
        if self.is_configured:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel("models/gemini-flash-latest")

    async def generate_guidance(self, request: GenerationRequest, timeout: float) -> LLMResult:
        start_time = time.time()
        if not self.is_configured:
            return LLMResult(provider_name=self.provider_name, latency_ms=0, success=False, error_message="Not configured")
            
        if self.__class__._permanently_failed:
            return LLMResult(provider_name=self.provider_name, latency_ms=0, success=False, error_message="Permanently disabled due to 404/400")
            
        try:
            # We can't strictly enforce timeout on the google library natively through an async param,
            # but we assume the orchestration layer handles overarching timeouts if needed.
            response = await self.model.generate_content_async(
                request.prompt,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json"
                )
            )
            guidance = self._validate_output(response.text)
            latency = int((time.time() - start_time) * 1000)
            return LLMResult(guidance=guidance, provider_name=self.provider_name, latency_ms=latency, success=True)
            
        except (ResourceExhausted, ServiceUnavailable) as e:
            logger.warning(f"GeminiProvider 429/503 error: {str(e)}")
            latency = int((time.time() - start_time) * 1000)
            return LLMResult(provider_name=self.provider_name, latency_ms=latency, success=False, error_message="Rate limit or Service Unavailable")
        except Exception as e:
            err_str = str(e)
            if "404" in err_str or "400" in err_str or "not found" in err_str.lower():
                logger.error(f"GeminiProvider permanent error: {err_str}. Disabling for process lifetime.")
                self.__class__._permanently_failed = True
            else:
                logger.warning(f"GeminiProvider unexpected error: {err_str}")
                
            latency = int((time.time() - start_time) * 1000)
            return LLMResult(provider_name=self.provider_name, latency_ms=latency, success=False, error_message=err_str)


class SarvamProvider(BaseLLMProvider):
    _cooldown_until = 0
    
    def __init__(self):
        self.provider_name = "sarvam"
        self.is_configured = bool(settings.SARVAM_API_KEY)
        self.endpoint = "https://api.sarvam.ai/v1/chat/completions"

    async def generate_guidance(self, request: GenerationRequest, timeout: float) -> LLMResult:
        start_time = time.time()
        if not self.is_configured:
            return LLMResult(provider_name=self.provider_name, latency_ms=0, success=False, error_message="Not configured")
            
        if time.time() < self.__class__._cooldown_until:
            return LLMResult(provider_name=self.provider_name, latency_ms=0, success=False, error_message="In cooldown")
            
        headers = {
            "api-subscription-key": settings.SARVAM_API_KEY,
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "sarvam-105b",
            "messages": [
                {"role": "user", "content": request.prompt}
            ],
            "temperature": 0.1
        }
        
        try:
            # Enforce dynamic timeout passed by the orchestrator
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(self.endpoint, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
                
                content = data.get("choices", [{}])[0].get("message", {}).get("content")
                if not content:
                    raise ValueError("Empty or invalid content from Sarvam")
                
                guidance = self._validate_output(content)
                latency = int((time.time() - start_time) * 1000)
                return LLMResult(guidance=guidance, provider_name=self.provider_name, latency_ms=latency, success=True)
                
        except httpx.HTTPStatusError as e:
            logger.warning(f"SarvamProvider HTTP error: {e.response.status_code}")
            latency = int((time.time() - start_time) * 1000)
            return LLMResult(provider_name=self.provider_name, latency_ms=latency, success=False, error_message=f"HTTP {e.response.status_code}")
        except httpx.RequestError as e:
            logger.warning(f"SarvamProvider network error/timeout: {str(e)}")
            self.__class__._cooldown_until = time.time() + 10.0 # 10s cooldown
            latency = int((time.time() - start_time) * 1000)
            return LLMResult(provider_name=self.provider_name, latency_ms=latency, success=False, error_message="Network error/Timeout")
        except Exception as e:
            logger.warning(f"SarvamProvider validation/unexpected error: {str(e)}")
            latency = int((time.time() - start_time) * 1000)
            return LLMResult(provider_name=self.provider_name, latency_ms=latency, success=False, error_message=str(e))


class GroqProvider(BaseLLMProvider):
    _permanently_failed = False
    
    def __init__(self):
        self.provider_name = "groq"
        self.is_configured = bool(settings.GROQ_API_KEY) and GROQ_AVAILABLE
        if self.is_configured:
            self.client = AsyncGroq(api_key=settings.GROQ_API_KEY)

    async def generate_guidance(self, request: GenerationRequest, timeout: float) -> LLMResult:
        start_time = time.time()
        if not self.is_configured:
            return LLMResult(provider_name=self.provider_name, latency_ms=0, success=False, error_message="Not configured")
            
        if self.__class__._permanently_failed:
            return LLMResult(provider_name=self.provider_name, latency_ms=0, success=False, error_message="Permanently disabled")
            
        try:
            # Enforce dynamic timeout passed by the orchestrator
            prompt_with_json = request.prompt + "\nIMPORTANT: You must return the output in JSON format."
            
            response = await asyncio.wait_for(
                self.client.chat.completions.create(
                    messages=[
                        {"role": "user", "content": prompt_with_json}
                    ],
                    model="qwen/qwen3.6-27b",
                    response_format={"type": "json_object"},
                    timeout=timeout
                ),
                timeout=timeout + 0.5
            )
            content = response.choices[0].message.content
            if not content:
                raise ValueError("Empty content from Groq")
            guidance = self._validate_output(content)
            latency = int((time.time() - start_time) * 1000)
            return LLMResult(guidance=guidance, provider_name=self.provider_name, latency_ms=latency, success=True)
            
        except Exception as e:
            err_str = str(e)
            if "model_decommissioned" in err_str or "400" in err_str:
                logger.error(f"GroqProvider permanent error: {err_str}. Disabling for process lifetime.")
                self.__class__._permanently_failed = True
            else:
                logger.warning(f"GroqProvider error: {err_str}")
            latency = int((time.time() - start_time) * 1000)
            return LLMResult(provider_name=self.provider_name, latency_ms=latency, success=False, error_message=str(e))
