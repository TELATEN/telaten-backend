from uuid import UUID
from fastapi import HTTPException, status
from app.modules.business.models import (
    BusinessProfile,
    BusinessProfileCreate,
    BusinessProfileUpdate,
)
from app.modules.business.repository import BusinessRepository
from app.modules.agent.service import AgentService
from app.db.session import AsyncSessionLocal
from app.core.redis import RedisClient
import json


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

    async def generate_milestones_background(self, user_id: UUID, business_id: UUID):
        """
        Background task delegates to AgentService.
        """
        redis = RedisClient.get_instance()
        channel = f"events:{user_id}"

        # Helper to publish event
        async def publish_event(
            event_type: str, message: str, data: dict | None = None
        ):
            payload = json.dumps({"type": event_type, "message": message, "data": data})
            await redis.publish(channel, payload)

        try:
            async with AsyncSessionLocal() as session:
                repo = BusinessRepository(session)
                profile = await repo.get_by_id(business_id)
                if not profile:
                    await publish_event("error", "Business profile not found.")
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

            # 2. Call Agent Service
            agent_service = AgentService()
            await agent_service.run_onboarding_workflow(
                user_id, business_id, business_data
            )

        except Exception as e:
            print(f"Error in background task: {e}")
            await publish_event("error", f"Background task failed: {str(e)}")
