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
    SARVAM_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    LLM_PROVIDER_ORDER: str = "gemini,sarvam,groq"
    LLM_PROVIDER_TIMEOUT: float = 8.0
    FIREBASE_CREDENTIALS_PATH: str = "./firebase-key.json"
    ENVIRONMENT: str = "development"
    AUTH_DISABLED: bool = True
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/raahat"
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    # RAG configuration
    RAG_CORPUS_DIR: str = "../RAG"
    RAG_EMBEDDING_MODEL: str = "models/gemini-embedding-001"
    RAG_EMBEDDING_DIMENSION: int = 1536
    RAG_RETRIEVAL_TOP_K: int = 5
    RAG_RETRIEVAL_MIN_SCORE: float = 0.5

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def cors_origins_list(self) -> List[str]:
        if isinstance(self.CORS_ORIGINS, str):
            return [
                origin.strip()
                for origin in self.CORS_ORIGINS.split(",")
                if origin.strip()
            ]
        return ["*"]


settings = Settings()