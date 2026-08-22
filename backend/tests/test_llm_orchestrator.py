import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.llm_orchestrator import LLMOrchestrator
from app.services.llm_providers import (
    GenerationRequest, 
    LLMResult, 
    BaseLLMProvider
)
from app.schemas.emergency import EmergencyGuidance, GuidanceStep

@pytest.fixture
def mock_guidance():
    return EmergencyGuidance(
        summary="Test summary",
        immediate_do_not_do=["Do not panic"],
        steps=[GuidanceStep(step_number=1, title="Step 1", instruction="Stay calm", is_critical=True)],
        first_aid_included=False
    )

class MockSuccessProvider(BaseLLMProvider):
    def __init__(self, name, guidance):
        self.provider_name = name
        self.is_configured = True
        self.guidance = guidance
        
    async def generate_guidance(self, request, timeout):
        return LLMResult(
            guidance=self.guidance,
            provider_name=self.provider_name,
            latency_ms=100,
            success=True
        )

class MockFailProvider(BaseLLMProvider):
    def __init__(self, name):
        self.provider_name = name
        self.is_configured = True
        
    async def generate_guidance(self, request, timeout):
        return LLMResult(
            provider_name=self.provider_name,
            latency_ms=100,
            success=False,
            error_message="Simulated failure"
        )

class MockUnconfiguredProvider(BaseLLMProvider):
    def __init__(self, name):
        self.provider_name = name
        self.is_configured = False
        
    async def generate_guidance(self, request, timeout):
        return LLMResult(
            provider_name=self.provider_name,
            latency_ms=0,
            success=False,
            error_message="Not configured"
        )


@pytest.mark.asyncio
async def test_orchestrator_gemini_success(mock_guidance):
    orchestrator = LLMOrchestrator()
    orchestrator.providers = [
        MockSuccessProvider("gemini", mock_guidance),
        MockFailProvider("sarvam"),
        MockFailProvider("groq")
    ]
    
    guidance, provider, latency = await orchestrator.generate_emergency_guidance("prompt", "english", "ACCIDENT", "HIGH")
    
    assert guidance.summary == "Test summary"
    assert provider == "gemini"

@pytest.mark.asyncio
async def test_orchestrator_gemini_fail_sarvam_success(mock_guidance):
    orchestrator = LLMOrchestrator()
    orchestrator.providers = [
        MockFailProvider("gemini"),
        MockSuccessProvider("sarvam", mock_guidance),
        MockFailProvider("groq")
    ]
    
    guidance, provider, latency = await orchestrator.generate_emergency_guidance("prompt", "english", "ACCIDENT", "HIGH")
    
    assert guidance.summary == "Test summary"
    assert provider == "sarvam"

@pytest.mark.asyncio
async def test_orchestrator_all_fail_fallback_to_deterministic():
    orchestrator = LLMOrchestrator()
    orchestrator.providers = [
        MockFailProvider("gemini"),
        MockFailProvider("sarvam"),
        MockUnconfiguredProvider("groq")
    ]
    
    # ACCIDENT should have deterministic fallback
    guidance, provider, latency = await orchestrator.generate_emergency_guidance("prompt", "english", "ACCIDENT", "HIGH")
    
    assert provider == "deterministic_keyword_fallback"
    assert len(guidance.summary) > 0

@pytest.mark.asyncio
async def test_orchestrator_skips_unconfigured(mock_guidance):
    orchestrator = LLMOrchestrator()
    orchestrator.providers = [
        MockUnconfiguredProvider("gemini"),
        MockUnconfiguredProvider("sarvam"),
        MockSuccessProvider("groq", mock_guidance)
    ]
    
    guidance, provider, latency = await orchestrator.generate_emergency_guidance("prompt", "english", "ACCIDENT", "HIGH")
    
    assert provider == "groq"
