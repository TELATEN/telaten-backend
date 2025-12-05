from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, func
from uuid import UUID
from typing import Sequence
from app.modules.gamification.models import Achievement, UserAchievement


class GamificationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_achievements(self) -> Sequence[Achievement]:
        result = await self.session.execute(select(Achievement))
        return result.scalars().all()

    async def get_unlocked_achievement_ids(self, user_id: UUID) -> Sequence[UUID]:
        stmt = select(UserAchievement.achievement_id).where(
            UserAchievement.user_id == user_id
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_user_achievements(
        self, user_id: UUID
    ) -> Sequence[UserAchievement]:
        stmt = select(UserAchievement).where(
            UserAchievement.user_id == user_id
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_user_achievements(self, user_id: UUID) -> int:
        stmt = select(func.count()).select_from(UserAchievement).where(
            UserAchievement.user_id == user_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def unlock_achievement(self, user_id: UUID, achievement_id: UUID):
        ua = UserAchievement(user_id=user_id, achievement_id=achievement_id)
        self.session.add(ua)
        await self.session.commit()

    async def create_achievement(self, achievement: Achievement) -> Achievement:
        self.session.add(achievement)
        await self.session.commit()
        await self.session.refresh(achievement)
        return achievement

    async def get_achievement(self, achievement_id: UUID) -> Achievement | None:
        stmt = select(Achievement).where(Achievement.id == achievement_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def update_achievement(self, achievement: Achievement) -> Achievement:
        self.session.add(achievement)
        await self.session.commit()
        await self.session.refresh(achievement)
        return achievement

    async def delete_achievement(self, achievement: Achievement) -> None:
        await self.session.delete(achievement)
        await self.session.commit()
