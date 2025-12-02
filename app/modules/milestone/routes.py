from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Sequence
from app.db.session import get_db
from app.modules.milestone.models import MilestoneRead
from app.modules.milestone.repository import MilestoneRepository
from app.modules.milestone.service import MilestoneService
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.business.service import BusinessService
from app.modules.business.repository import BusinessRepository

router = APIRouter()


def get_milestone_service(db: AsyncSession = Depends(get_db)) -> MilestoneService:
    repo = MilestoneRepository(db)
    return MilestoneService(repo)


def get_business_service(db: AsyncSession = Depends(get_db)) -> BusinessService:
    repo = BusinessRepository(db)
    return BusinessService(repo)


@router.get("/", response_model=Sequence[MilestoneRead])
async def get_my_business_milestones(
    current_user: User = Depends(get_current_user),
    milestone_service: MilestoneService = Depends(get_milestone_service),
    business_service: BusinessService = Depends(get_business_service),
):
    """Get all milestones for the current user's business."""
    business_profile = await business_service.get_profile(current_user.id)
    return await milestone_service.get_business_milestones(business_profile.id)
