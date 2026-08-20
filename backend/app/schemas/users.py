from typing import Optional
from pydantic import BaseModel, EmailStr

class UserProfile(BaseModel):
    uid: str
    email: Optional[EmailStr] = None
    display_name: Optional[str] = "Emergency User"
    phone_number: Optional[str] = None
    photo_url: Optional[str] = None
    is_anonymous: bool = False

class UserMeResponseData(BaseModel):
    user: UserProfile
    auth_provider: str = "firebase"
