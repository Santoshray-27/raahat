import abc
import json
import time
import re
from typing import Optional, Dict, Any, Type
import httpx

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
    def __init__(self):
        self.provider_name = "gemini"
        self.is_configured = bool(settings.GEMINI_API_KEY) and GEMINI_AVAILABLE
        if self.is_configured:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            # Using flash for generation tasks as requested
            self.model = genai.GenerativeModel("models/gemini-1.5-flash")

    async def generate_guidance(self, request: GenerationRequest, timeout: float) -> LLMResult:
        start_time = time.time()
        if not self.is_configured:
            return LLMResult(provider_name=self.provider_name, latency_ms=0, success=False, error_message="Not configured")
            
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
            logger.warning(f"GeminiProvider unexpected error: {str(e)}")
            latency = int((time.time() - start_time) * 1000)
            return LLMResult(provider_name=self.provider_name, latency_ms=latency, success=False, error_message=str(e))


class SarvamProvider(BaseLLMProvider):
    def __init__(self):
        self.provider_name = "sarvam"
        self.is_configured = bool(settings.SARVAM_API_KEY)
        self.endpoint = "https://api.sarvam.ai/v1/chat/completions"

    async def generate_guidance(self, request: GenerationRequest, timeout: float) -> LLMResult:
        start_time = time.time()
        if not self.is_configured:
            return LLMResult(provider_name=self.provider_name, latency_ms=0, success=False, error_message="Not configured")
            
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
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(self.endpoint, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
                
                content = data["choices"][0]["message"]["content"]
                guidance = self._validate_output(content)
                latency = int((time.time() - start_time) * 1000)
                return LLMResult(guidance=guidance, provider_name=self.provider_name, latency_ms=latency, success=True)
                
        except httpx.HTTPStatusError as e:
            logger.warning(f"SarvamProvider HTTP error: {e.response.status_code}")
            latency = int((time.time() - start_time) * 1000)
            return LLMResult(provider_name=self.provider_name, latency_ms=latency, success=False, error_message=f"HTTP {e.response.status_code}")
        except httpx.RequestError as e:
            logger.warning(f"SarvamProvider network error: {str(e)}")
            latency = int((time.time() - start_time) * 1000)
            return LLMResult(provider_name=self.provider_name, latency_ms=latency, success=False, error_message="Network error/Timeout")
        except Exception as e:
            logger.warning(f"SarvamProvider validation/unexpected error: {str(e)}")
            latency = int((time.time() - start_time) * 1000)
            return LLMResult(provider_name=self.provider_name, latency_ms=latency, success=False, error_message=str(e))


class GroqProvider(BaseLLMProvider):
    def __init__(self):
        self.provider_name = "groq"
        self.is_configured = bool(settings.GROQ_API_KEY) and GROQ_AVAILABLE
        if self.is_configured:
            self.client = AsyncGroq(api_key=settings.GROQ_API_KEY)

    async def generate_guidance(self, request: GenerationRequest, timeout: float) -> LLMResult:
        start_time = time.time()
        if not self.is_configured:
            return LLMResult(provider_name=self.provider_name, latency_ms=0, success=False, error_message="Not configured")
            
        try:
            response = await self.client.chat.completions.create(
                messages=[
                    {"role": "user", "content": request.prompt}
                ],
                model="llama3-8b-8192",
                response_format={"type": "json_object"},
                timeout=timeout
            )
            content = response.choices[0].message.content
            guidance = self._validate_output(content)
            latency = int((time.time() - start_time) * 1000)
            return LLMResult(guidance=guidance, provider_name=self.provider_name, latency_ms=latency, success=True)
            
        except Exception as e:
            logger.warning(f"GroqProvider error: {str(e)}")
            latency = int((time.time() - start_time) * 1000)
            return LLMResult(provider_name=self.provider_name, latency_ms=latency, success=False, error_message=str(e))
