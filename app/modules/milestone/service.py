import asyncio
from uuid import UUID
from typing import List, Sequence, Optional
from datetime import datetime, timezone

from llama_index.core.agent.workflow import AgentOutput, ToolCall, ToolCallResult
from app.modules.agent.workflow import auto_generate_workflow
from app.modules.milestone.repository import MilestoneRepository
from app.modules.milestone.models import Milestone, MilestoneTask
from app.modules.business.repository import BusinessRepository
from app.modules.gamification.service import GamificationService
from app.modules.chat.repository import ChatRepository
from app.db.session import AsyncSessionLocal
from app.core.logging import logger


class MilestoneService:
    def __init__(
        self,
        repo: MilestoneRepository,
        business_repo: BusinessRepository,
        gamification_service: Optional[GamificationService] = None,
        chat_repo: Optional[ChatRepository] = None,
    ):
        self.repo = repo
        self.business_repo = business_repo
        self.gamification_service = gamification_service
        self.chat_repo = chat_repo

    async def _award_points(self, business_id: UUID, points: int) -> None:
        if points > 0:
            new_total = await self.business_repo.add_points(business_id, points)

            # Check for achievements if gamification service is available
            if self.gamification_service and new_total > 0:
                business = await self.business_repo.get_by_id(business_id)
                if business:
                    await self.gamification_service.process_gamification(
                        business.id, business.user_id, new_total
                    )

    async def get_business_milestones(
        self, business_id: UUID, page: int = 1, size: int = 100
    ) -> Sequence[Milestone]:
        return await self.repo.get_by_business_id(business_id, page=page, size=size)

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

                            # Run background check for milestone generation
                            asyncio.create_task(
                                self._check_and_trigger_generation(
                                    milestone.business_id, milestone
                                )
                            )

        return task

    async def _check_and_trigger_generation(
        self, business_id: UUID, completed_milestone: Milestone
    ):
        """
        Checks if ALL milestones are completed. If so, triggers auto-generation.
        Running this in a separate async task prevents blocking the main response.
        Uses a fresh session to avoid 'garbage collector' issues with pool connections.
        """
        try:
            logger.debug("triggering background milestone generation check")
            async with AsyncSessionLocal() as session:
                # Re-initialize repos with fresh session
                repo = MilestoneRepository(session)
                business_repo = BusinessRepository(session)
                chat_repo = ChatRepository(session) if self.chat_repo else None

                # Use local method but with fresh repos
                await self._trigger_logic_with_session(
                    repo,
                    business_repo,
                    chat_repo,
                    business_id,
                    completed_milestone,
                )

        except Exception as e:
            logger.error(f"Background check failed: {e}")

    async def _trigger_logic_with_session(
        self, repo, business_repo, chat_repo, business_id, completed_milestone
    ):
        all_milestones = await repo.get_by_business_id(business_id)
        active_count = sum(
            1 for m in all_milestones if m.status in ["pending", "in_progress"]
        )
        logger.debug(f"Active milestones count: {active_count}")

        if active_count == 0:
            await self._trigger_auto_generation_internal(
                business_repo, chat_repo, business_id, completed_milestone
            )

    async def _trigger_auto_generation_internal(
        self, business_repo, chat_repo, business_id, completed_milestone
    ):
        try:
            # 1. Fetch Business Profile & Context
            profile = await business_repo.get_by_id(business_id)
            if not profile:
                return

            ai_memory = profile.ai_context or {}
            logger.debug(f"AI Memory: {ai_memory}")

            # 2. Fetch Last Chat Context
            chat_history_str = ""
            if chat_repo:
                sessions = await chat_repo.get_sessions_by_business(business_id)
                if sessions:
                    last_session = sessions[0]
                    history = await chat_repo.get_history(last_session.id, limit=5)
                    chat_history_str = "\n".join(
                        [f"{msg.role.upper()}: {msg.content}" for msg in history]
                    )

            # 3. Construct Trigger Context
            system_context = f"""
            **TRIGGER EVENT:**
            The user has just COMPLETED their LAST active Milestone: "{completed_milestone.title}".
            They now have ZERO active milestones.
            
            **BUSINESS PROFILE:**
            ID Business ID: {str(business_id)}
            Name: {profile.business_name}
            Stage: {profile.business_stage}
            Category: {profile.business_category}
            """

            # 4. Execute Agent
            workflow = auto_generate_workflow(
                system_prompt=system_context, initial_state=ai_memory
            )
            trigger_msg = f"""
            SYSTEM ALERT: ALL Milestones Completed.
            
            RECENT CHAT HISTORY:
            {chat_history_str}
            
            ACTION REQUIRED:
            Based on the persistent memory and recent chat, create a NEW BATCH of 3 milestones immediately.
            Make sure they follow a logical progression from the last one.
            """
            logger.debug(f"Trigger Message: {trigger_msg}")
            logger.debug("Starting auto-generation workflow for new milestones")

            handler = workflow.run(user_msg=trigger_msg)
            async for event in handler.stream_events():
                if isinstance(event, AgentOutput):
                    logger.debug(f"Agent Output: {event.response}")

                elif isinstance(event, ToolCall):
                    logger.debug(
                        f"Tool Call: {event.tool_name} with args {event.tool_kwargs}"
                    )

                elif isinstance(event, ToolCallResult):
                    logger.debug(
                        f"Tool Result: {event.tool_name} output {event.tool_output}"
                    )

        except Exception as e:
            logger.error(f"Auto-generation internal failed: {e}")
