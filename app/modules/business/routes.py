from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from typing import List
from app.modules.business.models import (
    BusinessProfileRead,
    BusinessProfileCreate,
    BusinessProfileUpdate,
    BusinessLevelRead,
)
from app.modules.business.repository import BusinessRepository
from app.modules.business.service import BusinessService
from app.modules.business.dependencies import get_business_service, get_business_repo
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
import json

router = APIRouter()


@router.post("/profile")
async def create_business_profile(
    profile_in: BusinessProfileCreate,
    current_user: User = Depends(get_current_user),
    service: BusinessService = Depends(get_business_service),
):

    profile = await service.create_profile(current_user.id, profile_in)

    async def combined_generator():
        profile_data = profile.model_dump(mode="json")
        yield f"data: {json.dumps({'type': 'profile_created', 'data': profile_data})}\n\n"

        async for event in service.generate_milestones_stream(
            current_user.id, profile.id
        ):
            yield event

    return StreamingResponse(combined_generator(), media_type="text/event-stream")


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


@router.get("/levels", response_model=List[BusinessLevelRead])
async def get_levels_user(
    repo: BusinessRepository = Depends(get_business_repo),
):
    """List all available business levels (User)."""
    return await repo.get_levels()
