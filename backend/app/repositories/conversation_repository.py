import json
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc
from app.repositories.base import BaseRepository
from app.models.conversation import Conversation, ConversationMessage

from uuid import UUID

class ConversationRepository(BaseRepository[Conversation]):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_or_create(self, conversation_id: Optional[str], user_id: Optional[UUID]) -> Conversation:
        if conversation_id:
            stmt = select(Conversation).where(Conversation.id == conversation_id)
            result = await self.session.execute(stmt)
            conv = result.scalar_one_or_none()
            if conv:
                return conv
                
        # Create new if none provided or not found
        conv = Conversation(user_id=user_id)
        self.session.add(conv)
        await self.session.flush()
        return conv

    async def add_message(self, conversation_id: str, user_message: str, 
                         detected_category: str, severity: str, 
                         guidance_summary: str, service_ids: List[str], 
                         provider_sources: List[str]):
        msg = ConversationMessage(
            conversation_id=conversation_id,
            user_message=user_message,
            detected_category=detected_category,
            severity=severity,
            guidance_summary=guidance_summary,
            service_ids_returned=service_ids,
            provider_sources=provider_sources
        )
        self.session.add(msg)
        
        # Also update conversation history for LLM context
        stmt = select(Conversation).where(Conversation.id == conversation_id)
        result = await self.session.execute(stmt)
        conv = result.scalar_one_or_none()
        if conv:
            history = conv.history or []
            history.append({
                "role": "user",
                "content": user_message
            })
            history.append({
                "role": "assistant",
                "content": guidance_summary
            })
            conv.history = history
            
        await self.session.commit()
        return msg

    async def get_recent_for_user(self, user_id: str, limit: int = 10) -> List[Conversation]:
        stmt = select(Conversation).where(Conversation.user_id == user_id).order_by(desc(Conversation.updated_at)).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
