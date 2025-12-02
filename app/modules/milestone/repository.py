from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from uuid import UUID
from typing import List, Sequence
from app.modules.milestone.models import Milestone


class MilestoneRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_bulk(self, milestones: List[Milestone]) -> Sequence[Milestone]:
        self.session.add_all(milestones)
        await self.session.commit()
        for m in milestones:
            await self.session.refresh(m)
        return milestones

    async def get_by_business_id(self, business_id: UUID) -> Sequence[Milestone]:
        statement = (
            select(Milestone)
            .where(Milestone.business_id == business_id)
            .order_by(Milestone.order)  # type: ignore
        )
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def get_by_id(self, milestone_id: UUID) -> Milestone | None:
        statement = select(Milestone).where(Milestone.id == milestone_id)
        result = await self.session.execute(statement)
        return result.scalars().first()

    async def update(self, milestone: Milestone) -> Milestone:
        self.session.add(milestone)
        await self.session.commit()
        await self.session.refresh(milestone)
        return milestone
