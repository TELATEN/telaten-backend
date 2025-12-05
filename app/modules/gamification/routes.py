from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.db.session import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.gamification.models import AchievementRead, LeaderboardEntry
from app.modules.gamification.repository import GamificationRepository
from app.modules.gamification.dependencies import get_gamification_repo
from app.modules.gamification.service import GamificationService
from app.modules.business.repository import BusinessRepository

router = APIRouter()


def get_gamification_service(
    repo: GamificationRepository = Depends(get_gamification_repo),
    session: AsyncSession = Depends(get_db),
) -> GamificationService:
    business_repo = BusinessRepository(session)
    return GamificationService(repo, business_repo)


@router.get("/achievements", response_model=List[AchievementRead])
async def get_achievements_user(
    current_user: User = Depends(get_current_user),
    repo: GamificationRepository = Depends(get_gamification_repo),
):
    """List all available achievements with unlock status for the current user."""
    all_achievements = await repo.get_all_achievements()
    user_achievements = await repo.get_user_achievements(current_user.id)

    # Create map for easy lookup
    unlocked_map = {ua.achievement_id: ua for ua in user_achievements}

    result = []
    for ach in all_achievements:
        # Convert SQLModel to Pydantic model (AchievementRead)
        ach_read = AchievementRead.model_validate(ach)

        if ach.id in unlocked_map:
            ach_read.is_unlocked = True
            ach_read.unlocked_at = unlocked_map[ach.id].unlocked_at
        else:
            ach_read.is_unlocked = False
            ach_read.unlocked_at = None

        result.append(ach_read)

    return result


@router.get("/leaderboard", response_model=List[LeaderboardEntry])
async def get_leaderboard(
    limit: int = 10,
    service: GamificationService = Depends(get_gamification_service),
    current_user: User = Depends(get_current_user),
):
    """Get the top business leaderboard based on total points."""
    return await service.get_leaderboard(limit, current_user)
