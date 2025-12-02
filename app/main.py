from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.config import settings
from app.modules.auth.routes import router as auth_router
from app.db.session import init_db
from app.core.logging import setup_logging
import structlog

# Setup logging as early as possible
setup_logging()
logger = structlog.get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Initializing database...")
    await init_db()
    logger.info("Database initialized successfully")
    yield
    # Shutdown
    logger.info("Shutting down application...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

@app.get("/")
async def root():
    return {"message": "Welcome to Telaten API", "docs": "/docs"}

app.include_router(auth_router, prefix=f"{settings.API_V1_STR}/auth", tags=["Auth"])
