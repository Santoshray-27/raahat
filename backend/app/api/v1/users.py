from fastapi import APIRouter, Depends
from app.core.security import get_current_user
from app.core.response import success_response
from app.schemas.users import UserProfile, UserMeResponseData

router = APIRouter()

@router.get("/users/me")
async def get_me(user: UserProfile = Depends(get_current_user)):
    data = UserMeResponseData(user=user, auth_provider="firebase")
    return success_response(data=data.model_dump())
