from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.milestone.models import (
    Milestone,
    MilestoneCreate,
    MilestoneRead,
    MilestoneListRead,
    MilestoneUpdate,
    MilestoneTask,
    MilestoneTaskRead,
)
from app.modules.milestone.repository import MilestoneRepository
from app.modules.milestone.service import MilestoneService
from app.modules.business.repository import BusinessRepository
from app.modules.gamification.repository import GamificationRepository
from app.modules.gamification.service import GamificationService
from app.modules.chat.repository import ChatRepository

router = APIRouter()


def get_service(session: AsyncSession = Depends(get_db)) -> MilestoneService:
    repo = MilestoneRepository(session)
    business_repo = BusinessRepository(session)
    gamification_repo = GamificationRepository(session)
    chat_repo = ChatRepository(session)
    gamification_service = GamificationService(gamification_repo, business_repo)
    return MilestoneService(repo, business_repo, gamification_service, chat_repo)


@router.get("/", response_model=List[MilestoneListRead])
async def get_milestones(
    service: MilestoneService = Depends(get_service),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
    page: int = 1,
    size: int = 100,
):
    business_repo = BusinessRepository(session)
    business = await business_repo.get_by_user_id(current_user.id)
    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business profile not found",
        )
    return await service.get_business_milestones(
        business.id, page=page, size=size
    )


@router.post("/", response_model=List[MilestoneRead])
async def create_milestones(
    milestones_in: List[MilestoneCreate],
    service: MilestoneService = Depends(get_service),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    business_repo = BusinessRepository(session)
    business = await business_repo.get_by_user_id(current_user.id)
    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business profile not found",
        )

    milestones = []
    for m_in in milestones_in:
        milestone_data = m_in.model_dump(exclude={"tasks"})
        milestone = Milestone(
            **milestone_data, business_id=business.id, is_generated=False
        )

        # Create Task objects from input
        tasks = [MilestoneTask(**t.model_dump()) for t in m_in.tasks]
        milestone.tasks = tasks

        milestones.append(milestone)

    return await service.create_milestones(milestones)


@router.get("/{milestone_id}", response_model=MilestoneRead)
async def get_milestone(
    milestone_id: UUID,
    service: MilestoneService = Depends(get_service),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    # Ownership check
    business_repo = BusinessRepository(session)
    business = await business_repo.get_by_user_id(current_user.id)
    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business profile not found",
        )

    milestone = await service.get_milestone(milestone_id)
    if not milestone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Milestone not found"
        )

    # Verify the milestone belongs to the user's business
    if milestone.business_id != business.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this milestone",
        )

    return milestone


@router.put("/{milestone_id}", response_model=MilestoneRead)
async def update_milestone(
    milestone_id: UUID,
    milestone_in: MilestoneUpdate,
    service: MilestoneService = Depends(get_service),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    # Ownership check
    business_repo = BusinessRepository(session)
    business = await business_repo.get_by_user_id(current_user.id)
    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business profile not found",
        )

    milestone = await service.get_milestone(milestone_id)
    if not milestone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Milestone not found"
        )

    # Verify the milestone belongs to the user's business
    if milestone.business_id != business.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this milestone",
        )

    update_data = milestone_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(milestone, key, value)

    return await service.update_milestone(milestone)


@router.post("/{milestone_id}/start", response_model=MilestoneRead)
async def start_milestone(
    milestone_id: UUID,
    service: MilestoneService = Depends(get_service),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    # Ownership check
    business_repo = BusinessRepository(session)
    business = await business_repo.get_by_user_id(current_user.id)
    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business profile not found",
        )

    # Verify existence and ownership
    milestone = await service.get_milestone(milestone_id)
    if not milestone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Milestone not found"
        )

    if milestone.business_id != business.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to start this milestone",
        )

    try:
        return await service.start_milestone(milestone_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/tasks/{task_id}/complete", response_model=MilestoneTaskRead)
async def complete_task(
    task_id: UUID,
    service: MilestoneService = Depends(get_service),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):

    business_repo = BusinessRepository(session)
    business = await business_repo.get_by_user_id(current_user.id)
    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business profile not found",
        )

    milestone_repo = MilestoneRepository(session)
    task = await milestone_repo.get_task_by_id(task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if not task.milestone:
        # Should not happen for a valid task in this context, but handle safely
        raise HTTPException(status_code=404, detail="Task milestone not found")

    if task.milestone.business_id != business.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to complete this task",
        )

    try:
        return await service.complete_task(task_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
