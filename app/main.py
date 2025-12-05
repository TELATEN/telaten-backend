from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.modules.auth.routes import router as auth_router
from app.modules.business.routes import router as business_router
from app.modules.business.admin_routes import router as business_admin_router
from app.modules.milestone.routes import router as milestone_router
from app.modules.chat.routes import router as chat_router
from app.modules.gamification.routes import router as gamification_router
from app.modules.gamification.admin_routes import router as gamification_admin_router
from app.modules.finance.routes import router as finance_router
from app.db.session import init_db, AsyncSessionLocal
from app.core.logging import logger
from app.db.init_data import init_admin_user


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing database...")
    await init_db()

    # Seed initial data
    async with AsyncSessionLocal() as session:
        await init_admin_user(session)

    logger.info("Database initialized successfully")
    yield
    logger.info("Shutting down application...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

origins = settings.FRONTEND_URL.split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Welcome to Telaten API", "docs": "/docs"}


app.include_router(auth_router, prefix=f"{settings.API_V1_STR}/auth", tags=["Auth"])
app.include_router(
    business_router, prefix=f"{settings.API_V1_STR}/business", tags=["Business"]
)
app.include_router(
    business_admin_router,
    prefix=f"{settings.API_V1_STR}/admin/business",
    tags=["Business (Admin)"],
)
app.include_router(
    milestone_router, prefix=f"{settings.API_V1_STR}/milestones", tags=["Milestones"]
)
app.include_router(chat_router, prefix=f"{settings.API_V1_STR}/chat", tags=["Chat"])
app.include_router(
    gamification_router,
    prefix=f"{settings.API_V1_STR}/gamification",
    tags=["Gamification"],
)
app.include_router(
    gamification_admin_router,
    prefix=f"{settings.API_V1_STR}/admin/gamification",
    tags=["Gamification (Admin)"],
)
app.include_router(
    finance_router, prefix=f"{settings.API_V1_STR}/finance", tags=["Finance"]
)
