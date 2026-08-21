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
    repo = UserRepository(db)
    # Synchronize Firebase identity with PostgreSQL
    db_user = await repo.sync_user(user)
    
    # We do not expose the internal UUID in the response currently, keeping the contract unchanged
    data = UserMeResponseData(user=user, auth_provider="firebase")
    return success_response(data=data.model_dump())
