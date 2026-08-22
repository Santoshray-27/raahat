import uuid
import logging
import asyncio
from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.users import UserProfile
from app.repositories.user_repository import UserRepository
from app.repositories.incident_repository import IncidentRepository
from app.models.incident import Incident, IncidentUpdate
from app.services.gemini_service import gemini_enhancer
from app.services.guidance import guidance_engine
from app.services.ranking import service_ranker
from app.providers.manager import provider_manager
from app.schemas.enums import SeverityLevel, ServiceType
from app.schemas.emergency import (
    EmergencyRequest, EmergencyResponseData, IncidentDetails, RecommendedAction, AIAnalysisMeta
)

logger = logging.getLogger(__name__)


async def _retrieve_rag_context(
    query: str,
    db: Optional[AsyncSession],
    top_k: int = 5,
    min_score: float = 0.5,
) -> Tuple[str, int, Optional[float]]:
    """
    Attempt RAG retrieval and context building.

    Returns:
        (context_text, chunks_used, top_score)

    On any failure (no DB, embedding error, retrieval error, no results):
        returns ("", 0, None) — the caller must not break on this.
    """
    if db is None:
        logger.debug("RAG retrieval skipped: no DB session provided.")
        return "", 0, None

    try:
        # Lazy imports to avoid circular dependency at module load time
        from app.repositories.rag_repository import RagRepository
        from app.services.rag_embedding_service import RagEmbeddingService, RagEmbeddingError
        from app.services.rag_context_builder import rag_context_builder
        from app.core.config import settings

        top_k = getattr(settings, "RAG_RETRIEVAL_TOP_K", top_k)
        min_score = getattr(settings, "RAG_RETRIEVAL_MIN_SCORE", min_score)

        embedding_service = RagEmbeddingService()
        query_embedding = await embedding_service.embed_query(query)

        rag_repo = RagRepository(db)
        results = await rag_repo.similarity_search(
            query_embedding=query_embedding,
            top_k=top_k,
            min_score=min_score,
        )

        if not results:
            logger.debug("RAG retrieval returned 0 results above threshold.")
            return "", 0, None

        # Convert SQLAlchemy RagChunk objects to plain tuples for the context builder
        chunk_tuples = [
            (chunk.content, float(score), chunk.metadata_ or {})
            for chunk, score in results
        ]

        built = rag_context_builder.build(chunk_tuples, query=query)
        logger.info(
            f"RAG retrieval: {built.chunks_used} chunks used, "
            f"top_score={built.top_score:.4f}"
        )
        return built.context_text, built.chunks_used, built.top_score

    except Exception as e:
        # RAG is an enhancement — never let it block emergency response
        logger.warning(f"RAG retrieval failed (falling back): {e}", exc_info=False)
        return "", 0, None


class EmergencyOrchestrator:
    async def process_emergency(
        self, 
        req: EmergencyRequest, 
        db: Optional[AsyncSession] = None, 
        user: Optional[UserProfile] = None
    ) -> EmergencyResponseData:
        import time
        t_start = time.time()
        # 0. Sync User to get DB ID
        db_user = None
        if db and user and not user.is_anonymous:
            try:
                user_repo = UserRepository(db)
                db_user = await user_repo.sync_user(user)
            except Exception as e:
                logger.error(f"User sync error: {e}", exc_info=True)

        # 0.5. Load Conversation History
        history = []
        conversation_id_used = None
        if req.conversation_id and db:
            from app.repositories.conversation_repository import ConversationRepository
            conv_repo = ConversationRepository(db)
            conv = await conv_repo.get_or_create(req.conversation_id, db_user.id if db_user else None)
            history = conv.history
            conversation_id_used = str(conv.id)

        # 1. Classify Query (Primary Gemini 1.5 Flash server-side with rule fallback)
        t_classify_start = time.time()
        category, severity, confidence, req_services, classifier_model = await gemini_enhancer.analyze_emergency(req.user_query, history)
        t_classify_end = time.time()
        
        # Persist Incident (Transaction 1)
        incident_id_str = f"inc_{str(uuid.uuid4())[:8]}"
        persisted_incident = None

        if db and db_user:
            try:
                inc_repo = IncidentRepository(db)
                new_incident = Incident(
                    user_id=db_user.id,
                    incident_type=category.value,
                    severity=severity.value,
                    description=req.user_query or req.message,
                    location=f"SRID=4326;POINT({req.location.longitude} {req.location.latitude})",
                    status="active"
                )
                persisted_incident = await inc_repo.create_incident(new_incident)
                if persisted_incident:
                    incident_id_str = str(persisted_incident.id)
            except Exception as e:
                # Critical resilience: do not block emergency response
                logger.error(f"Persistence error: {e}", exc_info=True)
                pass
        t_db_end = time.time()
        
        # 3. Build RAG Prompt & Generate Structured LLM Guidance
        from app.services.rag_context_builder import rag_context_builder
        from app.services.llm_orchestrator import llm_orchestrator
        
        is_life_threatening = (severity == SeverityLevel.CRITICAL)
        
        async def guidance_pipeline():
            # Attempt RAG retrieval concurrently
            try:
                rag_context, rag_chunks_used, rag_top_score = await _retrieve_rag_context(
                    query=req.user_query,
                    db=db,
                )
            except Exception as e:
                logger.warning(f"RAG context helper raised unexpectedly (falling back): {e}")
                rag_context, rag_chunks_used, rag_top_score = "", 0, None
                
            from app.services.rag_context_builder import BuiltContext
            b_context = BuiltContext(
                context_text=rag_context, 
                chunks_used=rag_chunks_used, 
                top_score=rag_top_score, 
                has_content=bool(rag_context)
            )
            
            generation_prompt = rag_context_builder.build_generation_prompt(
                query=req.user_query,
                category=category.value,
                severity=severity.value,
                life_threatening=is_life_threatening,
                built_context=b_context,
                language=req.language if hasattr(req, 'language') and req.language else "english",
                history=history
            )

            # Generate Guidance
            result = await llm_orchestrator.generate_emergency_guidance(
                prompt=generation_prompt,
                language=req.language if hasattr(req, 'language') and req.language else "english",
                category=category.value,
                severity=severity.value
            )
            # Append RAG metrics to the result for the profiler
            return result, b_context

        # 3. & 4. Run LLM Guidance Generation AND Service Lookup CONCURRENTLY
        async def fetch_providers():
            if not req.location:
                return [], "NONE"
            return await provider_manager.get_nearby_services(
                location=req.location,
                service_types=req_services,
                radius_km=15.0 if severity == SeverityLevel.CRITICAL else 10.0,
                limit=6
            )
            
        provider_coro = fetch_providers()
        
        t_gather_start = time.time()
        guidance_result, (raw_providers, provider_source) = await asyncio.gather(
            guidance_pipeline(), provider_coro
        )
        (guidance, llm_provider_used, llm_latency), b_context = guidance_result
        t_gather_end = time.time()
        
        # 5. Rank Services with human-readable rationale
        ranked_services = service_ranker.rank_providers(raw_providers, req.location, category) if req.location else []
        
        # 6. Build Recommended Actions (Dial 112 for critical/accident, call towing/mechanic, navigate)
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
            incident_id=incident_id_str,
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
            model_version=f"v1.0 (gen: {llm_provider_used})"
        )
        t_end = time.time()
        print(f"PROFILE: Classify: {(t_classify_end - t_classify_start)*1000:.2f}ms, RAG: (Concurrent), DB: {(t_db_end - t_classify_end)*1000:.2f}ms, Gather(LLM+Provider): {(t_gather_end - t_gather_start)*1000:.2f}ms, Assemble: {(t_end - t_gather_end)*1000:.2f}ms, Total: {(t_end - t_start)*1000:.2f}ms")
        
        limitations = []
        if provider_source != "google_places" and provider_source != "NONE":
            limitations.extend([
                f"Service directory served via {provider_source} fallback.",
                "Vendor availability status is UNKNOWN — please call to confirm opening hours."
            ])
        if not req.location:
            limitations.append("Exact location is required to identify nearby services.")
        if not persisted_incident:
            limitations.append("Database is offline. Incident history persistence is unavailable.")
        if severity == SeverityLevel.CRITICAL or category.value in ["ACCIDENT", "MEDICAL", "FIRE"]:
            limitations.append("CRITICAL: Dial 112 (National Emergency Helpline) or 108 (Ambulance) immediately for life-threatening support.")
            
        if not limitations:
            limitations = None
            
        if db:
            try:
                from app.repositories.conversation_repository import ConversationRepository
                conv_repo = ConversationRepository(db)
                if not conversation_id_used:
                    new_conv = await conv_repo.get_or_create(None, db_user.id if db_user else None)
                    conversation_id_used = str(new_conv.id)
                await conv_repo.add_message(
                    conversation_id_used,
                    user_message=req.user_query,
                    detected_category=category.value,
                    severity=severity.value,
                    guidance_summary=guidance.summary,
                    service_ids=[s.provider_id for s in ranked_services],
                    provider_sources=list(set([s.source for s in ranked_services]))
                )
            except Exception as e:
                logger.error(f"Failed to persist conversation: {e}", exc_info=True)
            
            # Transaction 2: Incident Update
            if persisted_incident:
                try:
                    inc_repo = IncidentRepository(db)
                    update = IncidentUpdate(
                        incident_id=persisted_incident.id,
                        status="active",
                        message="Services retrieved and actions recommended."
                    )
                    await inc_repo.create_incident_update(update)
                except Exception:
                    pass
            
        return EmergencyResponseData(
            incident=incident,
            guidance=guidance,
            services=ranked_services,
            recommended_actions=actions,
            ai=ai_meta,
            limitations=limitations,
            conversation_id=conversation_id_used
        )

orchestrator = EmergencyOrchestrator()
