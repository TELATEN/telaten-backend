from uuid import UUID
from typing import List, Sequence, Optional
from datetime import datetime, timezone
from app.modules.milestone.repository import MilestoneRepository
from app.modules.milestone.models import Milestone, MilestoneTask
from app.modules.business.repository import BusinessRepository
from app.modules.gamification.service import GamificationService


class MilestoneService:
    def __init__(
        self,
        repo: MilestoneRepository,
        business_repo: BusinessRepository,
        gamification_service: Optional[GamificationService] = None,
    ):
        self.repo = repo
        self.business_repo = business_repo
        self.gamification_service = gamification_service

    async def _award_points(self, business_id: UUID, points: int) -> None:
        if points > 0:
            business = await self.business_repo.get_by_id(business_id)
            if business:
                business.total_points += points
                await self.business_repo.update(business)

                # Check for achievements if gamification service is available
                if self.gamification_service:
                    await self.gamification_service.process_gamification(
                        business.id, business.user_id, business.total_points
                    )

    async def get_business_milestones(self, business_id: UUID) -> Sequence[Milestone]:
        return await self.repo.get_by_business_id(business_id)

    async def create_milestones(
        self, milestones: List[Milestone]
    ) -> Sequence[Milestone]:
        return await self.repo.create_bulk(milestones)

    async def get_milestone(self, milestone_id: UUID) -> Milestone | None:
        return await self.repo.get_by_id(milestone_id)

    async def update_milestone(self, milestone: Milestone) -> Milestone:
        return await self.repo.update(milestone)

    async def start_milestone(self, milestone_id: UUID) -> Milestone:
        milestone = await self.repo.get_by_id(milestone_id)
        if not milestone:
            raise ValueError("Milestone not found")

        if milestone.status == "pending":
            milestone.status = "in_progress"
            milestone.started_at = datetime.now(timezone.utc)
            return await self.repo.update(milestone)
        return milestone

    async def complete_task(self, task_id: UUID) -> MilestoneTask:
        task = await self.repo.get_task_by_id(task_id)
        if not task:
            raise ValueError("Task not found")

        if not task.is_completed:
            task.is_completed = True
            task.completed_at = datetime.now(timezone.utc)
            await self.repo.update_task(task)

            # Get milestone to find business_id
            if task.milestone_id:
                milestone = await self.repo.get_by_id(task.milestone_id)
                if milestone:
                    # Award points for Task Completion
                    await self._award_points(milestone.business_id, task.reward_points)

                    # Auto-check milestone completion
                    if milestone.tasks:
                        all_tasks_done = all(t.is_completed for t in milestone.tasks)
                        if all_tasks_done and milestone.status != "completed":
                            milestone.status = "completed"
                            milestone.completed_at = datetime.now(timezone.utc)
                            await self.repo.update(milestone)

                            # Award Bonus Points for Milestone Completion
                            await self._award_points(
                                milestone.business_id, milestone.reward_points
                            )

        return task
