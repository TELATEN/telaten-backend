from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.modules.gamification.repository import GamificationRepository


def get_gamification_repo(db: AsyncSession = Depends(get_db)) -> GamificationRepository:
    return GamificationRepository(db)
