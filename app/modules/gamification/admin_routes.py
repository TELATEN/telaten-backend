from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.db.session import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.gamification.models import (
    Achievement,
    AchievementCreate,
    AchievementRead,
    AchievementUpdate,
)
from app.modules.gamification.repository import GamificationRepository
from app.modules.gamification.dependencies import get_gamification_repo

router = APIRouter()


@router.post("/achievements", response_model=AchievementRead)
async def create_achievement(
    achievement_in: AchievementCreate,
    current_user: User = Depends(get_current_user),
    repo: GamificationRepository = Depends(get_gamification_repo),
):
    """Create a new achievement (Admin only)."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    achievement = Achievement(**achievement_in.model_dump())
    return await repo.create_achievement(achievement)


@router.put("/achievements/{achievement_id}", response_model=AchievementRead)
async def update_achievement(
    achievement_id: UUID,
    achievement_in: AchievementUpdate,
    current_user: User = Depends(get_current_user),
    repo: GamificationRepository = Depends(get_gamification_repo),
):
    """Update an achievement (Admin only)."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    achievement = await repo.get_achievement(achievement_id)
    if not achievement:
        raise HTTPException(status_code=404, detail="Achievement not found")

    update_data = achievement_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(achievement, key, value)

    return await repo.update_achievement(achievement)


@router.delete("/achievements/{achievement_id}")
async def delete_achievement(
    achievement_id: UUID,
    current_user: User = Depends(get_current_user),
    repo: GamificationRepository = Depends(get_gamification_repo),
):
    """Delete an achievement (Admin only)."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    achievement = await repo.get_achievement(achievement_id)
    if not achievement:
        raise HTTPException(status_code=404, detail="Achievement not found")

    await repo.delete_achievement(achievement)
    return {"message": "Achievement deleted successfully"}
