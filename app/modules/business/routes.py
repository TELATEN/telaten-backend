from fastapi import APIRouter, Depends, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.modules.business.models import (
    BusinessProfileRead,
    BusinessProfileCreate,
    BusinessProfileUpdate,
)
from app.modules.business.repository import BusinessRepository
from app.modules.business.service import BusinessService
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.core.redis import RedisClient
import asyncio

router = APIRouter()


# Dependency to get BusinessService
def get_business_service(db: AsyncSession = Depends(get_db)) -> BusinessService:
    repo = BusinessRepository(db)
    return BusinessService(repo)


@router.post("/profile", response_model=BusinessProfileRead)
async def create_business_profile(
    profile_in: BusinessProfileCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    service: BusinessService = Depends(get_business_service),
):
    """Create a new business profile for the current user and trigger AI milestone generation."""
    profile = await service.create_profile(current_user.id, profile_in)

    # Trigger background task for AI Milestone generation
    background_tasks.add_task(
        service.generate_milestones_background, current_user.id, profile.id
    )

    return profile


@router.get("/events")
async def business_events(current_user: User = Depends(get_current_user)):
    """
    Server-Sent Events (SSE) endpoint for real-time business updates.
    Connect to this endpoint to receive updates about AI generation progress.
    """
    redis = RedisClient.get_instance()
    channel = f"events:{current_user.id}"

    async def event_generator():
        pubsub = redis.pubsub()
        await pubsub.subscribe(channel)
        try:
            async for message in pubsub.listen():
                if await asyncio.to_thread(lambda: message["type"] == "message"):
                    yield f"data: {message['data']}\n\n"
        except asyncio.CancelledError:
            await pubsub.unsubscribe(channel)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.get("/profile", response_model=BusinessProfileRead)
async def get_business_profile(
    current_user: User = Depends(get_current_user),
    service: BusinessService = Depends(get_business_service),
):
    """Get the business profile of the current user."""
    return await service.get_profile(current_user.id)


@router.patch("/profile", response_model=BusinessProfileRead)
async def update_business_profile(
    profile_in: BusinessProfileUpdate,
    current_user: User = Depends(get_current_user),
    service: BusinessService = Depends(get_business_service),
):
    """Update the business profile of the current user."""
    return await service.update_profile(current_user.id, profile_in)
