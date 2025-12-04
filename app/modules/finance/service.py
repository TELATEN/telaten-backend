from uuid import UUID
from typing import Sequence, Optional
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from app.modules.finance.repository import FinanceRepository
from app.modules.finance.models import Transaction, TransactionCreate, FinancialSummary
from app.modules.business.repository import BusinessRepository
from app.modules.gamification.service import GamificationService


class FinanceService:
    def __init__(
        self,
        repo: FinanceRepository,
        business_repo: BusinessRepository,
        gamification_service: Optional[GamificationService] = None,
    ):
        self.repo = repo
        self.business_repo = business_repo
        self.gamification_service = gamification_service

    async def create_transaction(
        self, business_id: UUID, transaction_in: TransactionCreate
    ) -> Transaction:
        transaction = Transaction(
            **transaction_in.model_dump(), business_id=business_id
        )
        transaction = await self.repo.create(transaction)

        if self.gamification_service:
            # Simple logic: 5 points per transaction for being diligent ("Telaten")
            business = await self.business_repo.get_by_id(business_id)
            if business:
                points_to_award = 5
                business.total_points += points_to_award
                await self.business_repo.update(business)
                await self.gamification_service.process_gamification(
                    business.id, business.user_id, business.total_points
                )

        return transaction

    async def get_transactions(
        self,
        business_id: UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Sequence[Transaction]:
        return await self.repo.get_by_business_id(business_id, start_date, end_date)

    async def get_summary(
        self, business_id: UUID, period: str = "month"  # "week", "month", "year", "all"
    ) -> FinancialSummary:
        now = datetime.now()
        start_date = None
        end_date = now

        if period == "week":
            start_date = now - timedelta(days=7)
        elif period == "month":
            start_date = now - relativedelta(months=1)
        elif period == "year":
            start_date = now - relativedelta(years=1)

        transactions = await self.repo.get_by_business_id(
            business_id, start_date, end_date
        )

        total_income = sum(t.amount for t in transactions if t.type == "INCOME")
        total_expense = sum(t.amount for t in transactions if t.type == "EXPENSE")
        net_profit = total_income - total_expense

        return FinancialSummary(
            total_income=total_income,
            total_expense=total_expense,
            net_profit=net_profit,
            period_start=start_date,
            period_end=end_date,
        )
