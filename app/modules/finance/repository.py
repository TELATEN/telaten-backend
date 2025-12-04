from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, desc
from uuid import UUID
from typing import Sequence, Optional
from datetime import datetime
from app.modules.finance.models import Transaction


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
    ) -> Sequence[Transaction]:
        statement = (
            select(Transaction)
            .where(Transaction.business_id == business_id)
            .order_by(desc(Transaction.transaction_date))
        )

        if start_date:
            statement = statement.where(Transaction.transaction_date >= start_date)
        if end_date:
            statement = statement.where(Transaction.transaction_date <= end_date)

        result = await self.session.execute(statement)
        return result.scalars().all()

    async def get_by_id(self, transaction_id: UUID) -> Transaction | None:
        result = await self.session.get(Transaction, transaction_id)
        return result

    async def delete(self, transaction: Transaction) -> None:
        await self.session.delete(transaction)
        await self.session.commit()
