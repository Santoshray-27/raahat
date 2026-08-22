import os
from typing import Optional
import firebase_admin
from firebase_admin import credentials, auth
from fastapi import HTTPException, Security, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import settings
from app.core.logging import logger
from app.schemas.users import UserProfile

security_scheme = HTTPBearer(auto_error=False)

def init_firebase():
    if firebase_admin._apps:
        return
    
    if os.path.exists(settings.FIREBASE_CREDENTIALS_PATH):
        try:
            cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
            firebase_admin.initialize_app(cred)
            logger.info(f"Firebase Admin SDK initialized successfully from {settings.FIREBASE_CREDENTIALS_PATH}")
        except Exception as e:
            logger.warning(f"Failed to initialize Firebase Admin SDK: {e}. Auth will fall back to dev mode.")
    else:
        logger.info(f"Firebase credentials file not found at {settings.FIREBASE_CREDENTIALS_PATH}. Running in auth-disabled mode.")

init_firebase()

async def get_current_user(
    auth_credentials: Optional[HTTPAuthorizationCredentials] = Security(security_scheme)
) -> UserProfile:
    if settings.AUTH_DISABLED:
        return UserProfile(
            uid="dev_user_999",
            email="santosh.dev@raahat.app",
            display_name="Santosh Ray (Dev Mode)",
            is_anonymous=False
        )
    
    if not auth_credentials or not auth_credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization Header Bearer Token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    token = auth_credentials.credentials
    
    try:
        decoded_token = auth.verify_id_token(token, clock_skew_seconds=10)
        return UserProfile(
            uid=decoded_token.get("uid", "user_unknown"),
            email=decoded_token.get("email"),
            display_name=decoded_token.get("name", "RAAHAT User"),
            phone_number=decoded_token.get("phone_number"),
            photo_url=decoded_token.get("picture"),
            is_anonymous=False
        )
    except Exception as e:
        logger.error(f"Firebase Token Verification Failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired Firebase authentication token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"}
        )

async def get_optional_current_user(
    auth_credentials: Optional[HTTPAuthorizationCredentials] = Security(security_scheme)
) -> Optional[UserProfile]:
    """
    Returns the UserProfile if a valid token is provided.
    Returns None if no token is provided.
    Throws 401 if a token is provided but invalid.
    """
    if settings.AUTH_DISABLED:
        return UserProfile(
            uid="dev_user_999",
            email="santosh.dev@raahat.app",
            display_name="Santosh Ray (Dev Mode)",
            is_anonymous=False
        )
        
    if not auth_credentials or not auth_credentials.credentials:
        return None
        
    token = auth_credentials.credentials
    
    try:
        decoded_token = auth.verify_id_token(token, clock_skew_seconds=10)
        return UserProfile(
            uid=decoded_token.get("uid", "user_unknown"),
            email=decoded_token.get("email"),
            display_name=decoded_token.get("name", "RAAHAT User"),
            phone_number=decoded_token.get("phone_number"),
            photo_url=decoded_token.get("picture"),
            is_anonymous=False
        )
    except Exception as e:
        logger.error(f"Optional Firebase Token Verification Failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired Firebase authentication token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"}
        )
