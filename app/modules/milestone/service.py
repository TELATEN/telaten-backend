from uuid import UUID
from typing import List, Sequence
from app.modules.milestone.repository import MilestoneRepository
from app.modules.milestone.models import Milestone


class MilestoneService:
    def __init__(self, repo: MilestoneRepository):
        self.repo = repo

    async def get_business_milestones(self, business_id: UUID) -> Sequence[Milestone]:
        return await self.repo.get_by_business_id(business_id)

    async def create_milestones(self, milestones: List[Milestone]) -> Sequence[Milestone]:
        return await self.repo.create_bulk(milestones)
