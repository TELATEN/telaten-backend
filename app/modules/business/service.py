from uuid import UUID
from fastapi import HTTPException, status
from app.modules.business.models import BusinessProfile, BusinessProfileCreate, BusinessProfileUpdate
from app.modules.business.repository import BusinessRepository

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

    async def create_profile(self, user_id: UUID, profile_in: BusinessProfileCreate) -> BusinessProfile:
        # Check if profile already exists
        existing_profile = await self.repo.get_by_user_id(user_id)
        if existing_profile:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Business profile already exists for this user",
            )
        
        profile = BusinessProfile(
            user_id=user_id,
            **profile_in.model_dump()
        )
        return await self.repo.create(profile)

    async def update_profile(self, user_id: UUID, profile_in: BusinessProfileUpdate) -> BusinessProfile:
        profile = await self.get_profile(user_id)
        
        update_data = profile_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(profile, key, value)
            
        return await self.repo.update(profile)
