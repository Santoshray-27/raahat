import uuid
from typing import List
from app.services.gemini_service import gemini_enhancer
from app.services.guidance import guidance_engine
from app.services.ranking import service_ranker
from app.providers.manager import provider_manager
from app.schemas.enums import SeverityLevel, ServiceType
from app.schemas.emergency import (
    EmergencyRequest, EmergencyResponseData, IncidentDetails, RecommendedAction, AIAnalysisMeta
)

class EmergencyOrchestrator:
    async def process_emergency(self, req: EmergencyRequest) -> EmergencyResponseData:
        # 1. Classify Query (Primary Gemini 1.5 Flash server-side with rule fallback)
        category, severity, confidence, req_services, classifier_model = await gemini_enhancer.analyze_emergency(req.user_query)
        
        # 2. Get Structured Guidance
        guidance = guidance_engine.get_guidance(category, severity)
        
        # 3. Retrieve Nearby Services via ProviderManager (with fallback)
        raw_providers, provider_source = await provider_manager.get_nearby_services(
            location=req.location,
            service_types=req_services,
            radius_km=15.0 if severity == SeverityLevel.CRITICAL else 10.0,
            limit=6
        )
        
        # 4. Rank Services with human-readable rationale
        ranked_services = service_ranker.rank_providers(raw_providers, req.location, category)
        
        # 5. Build Recommended Actions (Dial 112 for critical/accident, call towing/mechanic, navigate)
        actions: List[RecommendedAction] = []
        
        if severity == SeverityLevel.CRITICAL or category.value in ["ACCIDENT", "MEDICAL", "FIRE"]:
            actions.append(
                RecommendedAction(
                    action_id="act_call_112",
                    action_type="CALL_POLICE",
                    label="Emergency Services (112)",
                    target_contact="112",
                    priority=1
                )
            )
            
        if ranked_services:
            top_provider = ranked_services[0]
            if top_provider.contact.phone_primary:
                actions.append(
                    RecommendedAction(
                        action_id="act_call_vendor",
                        action_type="CALL_TOWING" if "TOWING" in top_provider.service_types else "CALL_MECHANIC",
                        label=f"Call {top_provider.name}",
                        target_contact=top_provider.contact.phone_primary,
                        priority=2
                    )
                )
            actions.append(
                RecommendedAction(
                    action_id="act_nav_vendor",
                    action_type="NAVIGATE",
                    label=f"Navigate to {top_provider.name}",
                    target_payload={
                        "latitude": top_provider.location.latitude,
                        "longitude": top_provider.location.longitude,
                        "name": top_provider.name
                    },
                    priority=3
                )
            )
            
        incident = IncidentDetails(
            incident_id=f"inc_{str(uuid.uuid4())[:8]}",
            category=category,
            severity=severity,
            confidence=confidence,
            description_summary=f"Detected {category.value.lower()} emergency ({severity.value} severity)",
            requires_immediate_services=req_services,
            is_life_threatening=(severity == SeverityLevel.CRITICAL)
        )
        
        ai_meta = AIAnalysisMeta(
            classifier_used=classifier_model,
            confidence_score=confidence,
            model_version="v1.0"
        )
        
        limitations = None
        if provider_source != "google_places":
            limitations = [
                f"Service directory served via {provider_source} fallback.",
                "Vendor availability status is UNKNOWN — please call to confirm opening hours."
            ]
            
        return EmergencyResponseData(
            incident=incident,
            guidance=guidance,
            services=ranked_services,
            recommended_actions=actions,
            ai=ai_meta,
            limitations=limitations
        )

orchestrator = EmergencyOrchestrator()
