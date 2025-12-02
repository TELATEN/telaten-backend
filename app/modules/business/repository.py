from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from uuid import UUID
from app.modules.business.models import BusinessProfile

class BusinessRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_user_id(self, user_id: UUID) -> BusinessProfile | None:
        statement = select(BusinessProfile).where(BusinessProfile.user_id == user_id)
        result = await self.session.execute(statement)
        return result.scalars().first()

    async def create(self, profile: BusinessProfile) -> BusinessProfile:
        self.session.add(profile)
        await self.session.commit()
        await self.session.refresh(profile)
        return profile

    async def update(self, profile: BusinessProfile) -> BusinessProfile:
        self.session.add(profile)
        await self.session.commit()
        await self.session.refresh(profile)
        return profile
