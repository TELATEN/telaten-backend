from sqlalchemy.ext.asyncio import AsyncSession
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
