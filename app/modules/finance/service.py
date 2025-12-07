from uuid import UUID
from typing import Optional, Sequence
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from app.modules.business.repository import BusinessRepository
from app.modules.finance.repository import FinanceRepository
from app.modules.finance.models import (
    Transaction,
    TransactionCreate,
    TransactionRead,
    FinancialSummary,
    TransactionPagination,
    CategoryBreakdown,
    TransactionCategory,
    TransactionCategoryCreate,
)
from collections import defaultdict
from app.modules.gamification.service import GamificationService
import math


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
        cat = await self.repo.get_category_by_id(transaction_in.category_id)
        if not cat:
            raise ValueError(f"Category with ID {transaction_in.category_id} not found")
        final_category_name = cat.name
        data = transaction_in.model_dump()

        # Ensure transaction_date is not None if not provided
        if data.get("transaction_date") is None:
            del data["transaction_date"]

        data["category"] = final_category_name
        data["category_name"] = final_category_name

        transaction = Transaction(**data, business_id=business_id)
        transaction = await self.repo.create(transaction)

        if self.gamification_service:
            # Simple logic: 5 points per transaction for being diligent ("Telaten")
            points_to_award = 5
            new_total = await self.business_repo.add_points(
                business_id, points_to_award
            )

            business = await self.business_repo.get_by_id(business_id)
            if business:
                await self.gamification_service.process_gamification(
                    business.id, business.user_id, new_total
                )

        return transaction

    async def get_transactions(
        self,
        business_id: UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        page: int = 1,
        size: int = 20,
    ) -> TransactionPagination:
        skip = (page - 1) * size
        items, total = await self.repo.get_by_business_id(
            business_id, start_date, end_date, skip, size
        )

        pages = math.ceil(total / size) if size > 0 else 0

        return TransactionPagination(
            items=[TransactionRead.model_validate(t) for t in items],
            total=total,
            page=page,
            size=size,
            pages=pages,
        )

    async def get_summary(
        self,
        business_id: UUID,
        period: str = "month",  # "day", "week", "month", "year", "all"
    ) -> FinancialSummary:
        now = datetime.now()
        start_date = None
        end_date = now

        if period == "day":
            start_date = now - timedelta(days=1)
        elif period == "week":
            start_date = now - timedelta(days=7)
        elif period == "month":
            start_date = now - relativedelta(months=1)
        elif period == "year":
            start_date = now - relativedelta(years=1)

        # For summary we need all transactions within period, so using large limit
        transactions, _ = await self.repo.get_by_business_id(
            business_id, start_date, end_date, skip=0, limit=10000
        )

        total_income = 0.0
        total_expense = 0.0
        income_categories = defaultdict(float)
        expense_categories = defaultdict(float)

        for t in transactions:
            amount = float(t.amount)
            cat_label = t.category_name

            if t.type == "INCOME":
                total_income += amount
                income_categories[cat_label] += amount
            elif t.type == "EXPENSE":
                total_expense += amount
                expense_categories[cat_label] += amount

        net_profit = total_income - total_expense

        # Helper to create breakdown list
        def create_breakdown(categories: dict, total: float) -> list[CategoryBreakdown]:
            if total == 0:
                return []
            return [
                CategoryBreakdown(
                    category=cat,
                    amount=amt,
                    percentage=round((amt / total) * 100, 2),
                )
                for cat, amt in categories.items()
            ]

        return FinancialSummary(
            total_income=total_income,
            total_expense=total_expense,
            net_profit=net_profit,
            period_start=start_date,
            period_end=end_date,
            income_breakdown=create_breakdown(income_categories, total_income),
            expense_breakdown=create_breakdown(expense_categories, total_expense),
        )

    # --- Category Management ---

    async def create_category(
        self, business_id: UUID, category_in: TransactionCategoryCreate
    ) -> TransactionCategory:
        category = TransactionCategory(
            **category_in.model_dump(), business_id=business_id
        )
        return await self.repo.create_category(category)

    async def get_categories(self, business_id: UUID) -> Sequence[TransactionCategory]:
        return await self.repo.get_categories(business_id)

    async def delete_category(self, business_id: UUID, category_id: UUID) -> None:
        category = await self.repo.get_category_by_id(category_id)
        if not category:
            raise ValueError("Category not found")

        # Only allow deleting own categories
        if category.business_id != business_id:
            raise ValueError("Not authorized to delete this category")

        await self.repo.delete_category(category)
