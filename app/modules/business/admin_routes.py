from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Sequence
from uuid import UUID
from app.db.session import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.business.models import (
    BusinessLevel,
    BusinessLevelCreate,
    BusinessLevelRead,
    BusinessLevelUpdate,
)
from app.modules.business.repository import BusinessRepository
from app.modules.business.dependencies import get_business_repo

router = APIRouter()


@router.post("/levels", response_model=BusinessLevelRead)
async def create_level(
    level_in: BusinessLevelCreate,
    current_user: User = Depends(get_current_user),
    repo: BusinessRepository = Depends(get_business_repo),
):
    """Create a new business level (Admin only)."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    level = BusinessLevel(**level_in.model_dump())
    return await repo.create_level(level)


@router.get("/levels", response_model=Sequence[BusinessLevelRead])
async def get_levels_admin(
    current_user: User = Depends(get_current_user),
    repo: BusinessRepository = Depends(get_business_repo),
):
    """List all available business levels (Admin)."""
    if current_user.role != "admin":
         raise HTTPException(status_code=403, detail="Not authorized")
    return await repo.get_levels()


@router.put("/levels/{level_id}", response_model=BusinessLevelRead)
async def update_level(
    level_id: UUID,
    level_in: BusinessLevelUpdate,
    current_user: User = Depends(get_current_user),
    repo: BusinessRepository = Depends(get_business_repo),
):
    """Update a business level (Admin only)."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    level = await repo.get_level(level_id)
    if not level:
        raise HTTPException(status_code=404, detail="Level not found")

    update_data = level_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(level, key, value)

    return await repo.update_level(level)


@router.delete("/levels/{level_id}")
async def delete_level(
    level_id: UUID,
    current_user: User = Depends(get_current_user),
    repo: BusinessRepository = Depends(get_business_repo),
):
    """Delete a business level (Admin only)."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    level = await repo.get_level(level_id)
    if not level:
        raise HTTPException(status_code=404, detail="Level not found")

    await repo.delete_level(level)
    return {"message": "Level deleted successfully"}
