from uuid import UUID
from typing import AsyncGenerator
from fastapi import HTTPException, status
from app.modules.business.models import (
    BusinessProfile,
    BusinessProfileCreate,
    BusinessProfileUpdate,
)
from app.modules.business.repository import BusinessRepository
from app.modules.agent.service import AgentService
from app.db.session import AsyncSessionLocal
import structlog
from app.core.utils import format_sse

logger = structlog.get_logger()


class BusinessService:
    def __init__(self, repo: BusinessRepository):
        self.repo = repo

    async def get_profile(self, user_id: UUID) -> BusinessProfile:
        profile = await self.repo.get_by_user_id(user_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Business profile not found",
            )
        return profile

    async def create_profile(
        self, user_id: UUID, profile_in: BusinessProfileCreate
    ) -> BusinessProfile:
        # Check if profile already exists
        existing_profile = await self.repo.get_by_user_id(user_id)
        if existing_profile:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Business profile already exists for this user",
            )

        profile = BusinessProfile(user_id=user_id, **profile_in.model_dump())
        return await self.repo.create(profile)

    async def update_profile(
        self, user_id: UUID, profile_in: BusinessProfileUpdate
    ) -> BusinessProfile:
        profile = await self.get_profile(user_id)

        update_data = profile_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(profile, key, value)

        return await self.repo.update(profile)

    async def add_points(self, business_id: UUID, points: int) -> int:
        return await self.repo.add_points(business_id, points)

    async def generate_milestones_stream(
        self, user_id: UUID, business_id: UUID
    ) -> AsyncGenerator[str, None]:
        """
        Generator that yields SSE events for milestone generation.
        """

        try:
            async with AsyncSessionLocal() as session:
                repo = BusinessRepository(session)
                profile = await repo.get_by_id(business_id)
                if not profile:
                    yield format_sse("error", "Business profile not found.")
                    return

                if profile.user_id != user_id:
                    yield format_sse("error", "Not authorized to access this business.")
                    return

                business_data = {
                    "name": profile.business_name,
                    "category": profile.business_category,
                    "description": profile.business_description,
                    "stage": profile.business_stage,
                    "target_market": profile.target_market,
                    "primary_goal": profile.primary_goal,
                    "address": profile.address,
                }

            agent_service = AgentService()
            async for event in agent_service.run_onboarding_workflow(
                business_id, business_data
            ):
                yield event

        except Exception as e:
            logger.error(f"Error in streaming task: {e}")
            yield format_sse("error", f"Streaming task failed: {str(e)}")
