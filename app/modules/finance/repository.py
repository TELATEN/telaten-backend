from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import select, desc, func
from uuid import UUID
from typing import Sequence, Optional
from datetime import datetime
from app.modules.finance.models import Transaction, TransactionCategory


class FinanceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, transaction: Transaction) -> Transaction:
        self.session.add(transaction)
        await self.session.commit()
        await self.session.refresh(transaction)
        return transaction

    async def get_by_business_id(
        self,
        business_id: UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[Sequence[Transaction], int]:
        statement = (
            select(Transaction)
            .where(Transaction.business_id == business_id)
            .order_by(desc(Transaction.transaction_date))
            .options(selectinload(Transaction.category))  # type: ignore
        )

        if start_date:
            statement = statement.where(Transaction.transaction_date >= start_date)
        if end_date:
            statement = statement.where(Transaction.transaction_date <= end_date)

        # Get total count
        count_statement = select(func.count()).select_from(statement.subquery())
        count_result = await self.session.execute(count_statement)
        total = count_result.scalar_one()

        # Apply pagination
        statement = statement.offset(skip).limit(limit)
        result = await self.session.execute(statement)

        return result.scalars().all(), total

    async def get_summary_stats(
        self,
        business_id: UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> tuple[float, float, dict, dict]:
        """
        Calculates total income, total expense, and category breakdowns using SQL aggregation.
        """
        # Base filter
        filters = [Transaction.business_id == business_id]
        if start_date:
            filters.append(Transaction.transaction_date >= start_date)
        if end_date:
            filters.append(Transaction.transaction_date <= end_date)

        # Query 1: Total Income & Expense
        stmt_totals = (
            select(Transaction.type, func.sum(Transaction.amount).label("total_amount"))
            .where(*filters)
            .group_by(Transaction.type)
        )

        result_totals = await self.session.execute(stmt_totals)
        totals = result_totals.all()

        total_income = 0.0
        total_expense = 0.0

        for type_, amount in totals:
            if type_ == "INCOME":
                total_income = float(amount or 0)
            elif type_ == "EXPENSE":
                total_expense = float(amount or 0)

        # Query 2: Breakdown by Category
        stmt_breakdown = (
            select(
                Transaction.type,
                Transaction.category_name,
                func.sum(Transaction.amount).label("total_amount"),
            )
            .where(*filters)
            .group_by(Transaction.type, Transaction.category_name)
        )

        result_breakdown = await self.session.execute(stmt_breakdown)
        breakdowns = result_breakdown.all()

        income_categories = {}
        expense_categories = {}

        for type_, cat_name, amount in breakdowns:
            if type_ == "INCOME":
                income_categories[cat_name] = float(amount or 0)
            elif type_ == "EXPENSE":
                expense_categories[cat_name] = float(amount or 0)

        return total_income, total_expense, income_categories, expense_categories

    async def get_by_id(self, transaction_id: UUID) -> Transaction | None:
        result = await self.session.get(Transaction, transaction_id)
        return result

    async def delete(self, transaction: Transaction) -> None:
        await self.session.delete(transaction)
        await self.session.commit()

    # --- Category Methods ---

    async def create_category(
        self, category: TransactionCategory
    ) -> TransactionCategory:
        self.session.add(category)
        await self.session.commit()
        await self.session.refresh(category)
        return category

    async def get_categories(self, business_id: UUID) -> Sequence[TransactionCategory]:
        statement = (
            select(TransactionCategory)
            .where(TransactionCategory.business_id == business_id)
            .order_by(TransactionCategory.type, TransactionCategory.name)
        )

        result = await self.session.execute(statement)
        return result.scalars().all()

    async def create_default_categories(self, business_id: UUID) -> None:
        """Creates default transaction categories for a new business."""
        default_categories = [
            # EXPENSE
            {"name": "Bahan Baku", "type": "EXPENSE", "icon": "🛒"},
            {"name": "Gaji Karyawan", "type": "EXPENSE", "icon": "👤"},
            {"name": "Sewa Tempat", "type": "EXPENSE", "icon": "🏠"},
            {"name": "Listrik & Air", "type": "EXPENSE", "icon": "⛏️"},
            {"name": "Transportasi", "type": "EXPENSE", "icon": "🚚"},
            {"name": "Pemasaran", "type": "EXPENSE", "icon": "📢"},
            {"name": "Lainnya", "type": "EXPENSE", "icon": "♾️"},
            # INCOME
            {"name": "Penjualan", "type": "INCOME", "icon": "💲"},
            {"name": "Investasi", "type": "INCOME", "icon": "📈"},
            {"name": "Bonus", "type": "INCOME", "icon": "🤑"},
            {"name": "Lainnya", "type": "INCOME", "icon": "🧲"},
        ]

        for data in default_categories:
            category = TransactionCategory(
                name=data["name"],
                type=data["type"],
                icon=data["icon"],
                business_id=business_id,
            )
            self.session.add(category)

        await self.session.commit()

    async def get_category_by_id(self, category_id: UUID) -> TransactionCategory | None:
        return await self.session.get(TransactionCategory, category_id)

    async def delete_category(self, category: TransactionCategory) -> None:
        await self.session.delete(category)
        await self.session.commit()
