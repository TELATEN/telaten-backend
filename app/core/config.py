from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    PROJECT_NAME: str = "Telaten Backend"
    API_V1_STR: str = "/api/v1"
    PORT: int = 8000

    DATABASE_URL: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/telaten_db"
    )

    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # AI Providers
    LLM_API_KEY: Optional[str] = None
    LLM_BASE_URL: Optional[str] = None
    LLM_MODEL_NAME: str

    # Logging
    LOG_LEVEL: str = "INFO"
    ENV: str = "development"

    # CORS
    FRONTEND_URL: str = "http://localhost:3000"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
