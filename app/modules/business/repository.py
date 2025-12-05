from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, asc, desc, func
from uuid import UUID
from typing import Sequence
from app.modules.business.models import BusinessProfile, BusinessLevel
from app.modules.auth.models import User


class BusinessRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_user_id(self, user_id: UUID) -> BusinessProfile | None:
        statement = select(BusinessProfile).where(BusinessProfile.user_id == user_id)
        result = await self.session.execute(statement)
        return result.scalars().first()

    async def get_by_id(self, business_id: UUID) -> BusinessProfile | None:
        statement = select(BusinessProfile).where(BusinessProfile.id == business_id)
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

    async def add_points(self, business_id: UUID, points: int) -> int:
        profile = await self.get_by_id(business_id)
        if profile:
            current = profile.total_points or 0
            profile.total_points = current + points
            self.session.add(profile)
            await self.session.commit()
            await self.session.refresh(profile)
            return profile.total_points
        return 0

    # --- Business Level Methods ---

    async def get_levels(self) -> Sequence[BusinessLevel]:
        stmt = select(BusinessLevel).order_by(asc(BusinessLevel.required_points))
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_level(self, level_id: UUID) -> BusinessLevel | None:
        result = await self.session.get(BusinessLevel, level_id)
        return result

    async def create_level(self, level: BusinessLevel) -> BusinessLevel:
        self.session.add(level)
        await self.session.commit()
        await self.session.refresh(level)
        return level

    async def update_level(self, level: BusinessLevel) -> BusinessLevel:
        self.session.add(level)
        await self.session.commit()
        await self.session.refresh(level)
        return level

    async def delete_level(self, level: BusinessLevel) -> None:
        await self.session.delete(level)
        await self.session.commit()

    async def get_level_by_points(self, points: int) -> BusinessLevel | None:
        # Find the highest level where required_points <= points
        stmt = (
            select(BusinessLevel)
            .where(BusinessLevel.required_points <= points)
            .order_by(desc(BusinessLevel.required_points))
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_top_businesses(
        self, limit: int = 10
    ) -> Sequence[tuple[BusinessProfile, User, BusinessLevel | None]]:
        # Join with User to get user details and BusinessLevel for level name
        stmt = (
            select(BusinessProfile, User, BusinessLevel)
            .join(User, BusinessProfile.user_id == User.id)  # type: ignore
            .join(BusinessLevel, BusinessProfile.level_id == BusinessLevel.id, isouter=True)  # type: ignore
            .where(BusinessProfile.deleted_at == None)
            .order_by(desc(BusinessProfile.total_points))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.all()  # type: ignore

    async def calculate_rank(self, points: int) -> int:
        stmt = (
            select(func.count())
            .select_from(BusinessProfile)
            .where(BusinessProfile.deleted_at == None)
            .where(BusinessProfile.total_points > points)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one() + 1
