from fastapi import APIRouter, Depends
from app.core.security import get_current_user
from app.core.response import success_response
from app.schemas.users import UserProfile, UserMeResponseData

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.repositories.user_repository import UserRepository

router = APIRouter()

@router.get("/users/me")
async def get_me(
    user: UserProfile = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        if db:
            repo = UserRepository(db)
            await repo.sync_user(user)
    except Exception as e:
        from app.core.logging import logger
        logger.warning(f"Database sync skipped for /users/me: {e}")
    
    # We do not expose the internal UUID in the response currently, keeping the contract unchanged
    data = UserMeResponseData(user=user, auth_provider="firebase")
    return success_response(data=data.model_dump())

@router.get("/users/me/conversations")
async def get_my_conversations(
    user: UserProfile = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if not db:
        return success_response(data=[])
        
    try:
        from app.repositories.user_repository import UserRepository
        from app.repositories.conversation_repository import ConversationRepository
        repo = UserRepository(db)
        db_user = await repo.sync_user(user)
        
        conv_repo = ConversationRepository(db)
        convs = await conv_repo.get_recent_for_user(db_user.id, limit=20)
        
        result = []
        for c in convs:
            result.append({
                "conversation_id": c.id,
                "created_at": c.created_at.isoformat(),
                "updated_at": c.updated_at.isoformat(),
                "history": c.history
            })
            
        return success_response(data=result)
    except Exception as e:
        from app.core.logging import logger
        logger.error(f"Failed to fetch conversations for {user.uid}: {e}")
        return success_response(data=[])
