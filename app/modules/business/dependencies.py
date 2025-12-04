from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.modules.business.repository import BusinessRepository
from app.modules.business.service import BusinessService


def get_business_repo(db: AsyncSession = Depends(get_db)) -> BusinessRepository:
    return BusinessRepository(db)


def get_business_service(db: AsyncSession = Depends(get_db)) -> BusinessService:
    repo = BusinessRepository(db)
    return BusinessService(repo)
