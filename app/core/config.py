from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    PROJECT_NAME: str = "Telaten Backend"
    API_V1_STR: str = "/api/v1"
    PORT: int = 8000

    DATABASE_URL: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/telaten_db"
    )
    REDIS_URL: str = "redis://localhost:6379/0"

    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # AI Providers
    LLM_API_KEY: Optional[str] = None
    LLM_BASE_URL: Optional[str] = None

    # Storage (Cloudflare R2)
    R2_ACCOUNT_ID: Optional[str] = None
    R2_ACCESS_KEY_ID: str
    R2_SECRET_ACCESS_KEY: str
    R2_BUCKET_NAME: str
    R2_ENDPOINT_URL: str

    # Logging
    LOG_LEVEL: str = "INFO"
    ENV: str = "development"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
