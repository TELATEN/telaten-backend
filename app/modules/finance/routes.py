from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime
from uuid import UUID
from app.db.session import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.business.repository import BusinessRepository
from app.modules.finance.models import (
    TransactionCreate,
    TransactionRead,
    FinancialSummary,
    TransactionPagination,
)
from app.modules.finance.repository import FinanceRepository
from app.modules.finance.service import FinanceService
from app.modules.gamification.repository import GamificationRepository
from app.modules.gamification.service import GamificationService


router = APIRouter()


def get_service(session: AsyncSession = Depends(get_db)) -> FinanceService:
    repo = FinanceRepository(session)
    business_repo = BusinessRepository(session)
    gamification_repo = GamificationRepository(session)
    gamification_service = GamificationService(gamification_repo, business_repo)
    return FinanceService(repo, business_repo, gamification_service)


@router.post("/transactions", response_model=TransactionRead)
async def create_transaction(
    transaction_in: TransactionCreate,
    service: FinanceService = Depends(get_service),
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

    return await service.create_transaction(business.id, transaction_in)


@router.get("/transactions", response_model=TransactionPagination)
async def get_transactions(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    page: int = 1,
    size: int = 20,
    service: FinanceService = Depends(get_service),
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

    return await service.get_transactions(business.id, start_date, end_date, page, size)


@router.get("/summary", response_model=FinancialSummary)
async def get_financial_summary(
    period: str = "month",
    service: FinanceService = Depends(get_service),
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

    return await service.get_summary(business.id, period)


@router.delete("/transactions/{transaction_id}")
async def delete_transaction(
    transaction_id: UUID,
    service: FinanceService = Depends(get_service),
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

    transaction = await service.repo.get_by_id(transaction_id)
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )

    if transaction.business_id != business.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this transaction",
        )

    await service.repo.delete(transaction)
    return {"message": "Transaction deleted successfully"}
