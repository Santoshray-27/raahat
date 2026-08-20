import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "RAAHAT Core API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    USE_MOCKS: bool = False
    GOOGLE_PLACES_API_KEY: str = ""
    GOOGLE_ROUTES_API_KEY: str = ""
    GEOAPIFY_API_KEY: str = ""
    GOOGLE_MAPS_JS_KEY: str = ""
    GEMINI_API_KEY: str = ""
    FIREBASE_CREDENTIALS_PATH: str = "./firebase-key.json"
    AUTH_DISABLED: bool = True
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/raahat"
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def cors_origins_list(self) -> List[str]:
        if isinstance(self.CORS_ORIGINS, str):
            return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
        return ["*"]

settings = Settings()
