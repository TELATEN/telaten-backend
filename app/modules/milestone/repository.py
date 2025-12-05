from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import select
from uuid import UUID
from typing import List, Sequence
from app.modules.milestone.models import Milestone, MilestoneTask
from datetime import datetime, timezone


class MilestoneRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_bulk(self, milestones: List[Milestone]) -> Sequence[Milestone]:
        self.session.add_all(milestones)
        await self.session.commit()
        for m in milestones:
            await self.session.refresh(m)
        return milestones

    async def add_task(self, task: MilestoneTask) -> MilestoneTask:
        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def get_by_business_id(
        self,
        business_id: UUID,
        page: int = 1,
        size: int = 100,
        status: str | Sequence[str] | None = None,
    ) -> Sequence[Milestone]:
        offset = (page - 1) * size
        statement = (
            select(Milestone)
            .where(Milestone.business_id == business_id)
            .where(Milestone.deleted_at == None)
        )

        if status:
            if isinstance(status, str):
                statement = statement.where(Milestone.status == status)
            else:
                statement = statement.where(Milestone.status.in_(status))  # type: ignore

        statement = (
            statement.order_by(Milestone.order)  # type: ignore
            .offset(offset)
            .limit(size)
        )
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def get_by_id(self, milestone_id: UUID) -> Milestone | None:
        statement = (
            select(Milestone)
            .where(Milestone.id == milestone_id)
            .where(Milestone.deleted_at == None)
        )
        result = await self.session.execute(statement)
        return result.scalars().first()

    async def get_task_by_id(self, task_id: UUID) -> MilestoneTask | None:
        statement = (
            select(MilestoneTask)
            .where(MilestoneTask.id == task_id)
            .options(selectinload(MilestoneTask.milestone))  # type: ignore
        )
        result = await self.session.execute(statement)
        return result.scalars().first()

    async def update(self, milestone: Milestone) -> Milestone:
        self.session.add(milestone)
        await self.session.commit()
        await self.session.refresh(milestone)
        return milestone

    async def update_task(self, task: MilestoneTask) -> MilestoneTask:
        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def delete(self, milestone: Milestone) -> None:
        milestone.deleted_at = datetime.now(timezone.utc)
        self.session.add(milestone)
        await self.session.commit()
