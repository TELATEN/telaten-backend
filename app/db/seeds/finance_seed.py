from datetime import datetime, timedelta, timezone
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.modules.finance.models import Transaction, TransactionCategory
from app.core.logging import logger


async def seed_finance(session: AsyncSession, business_id: UUID):
    """Seed Transactions."""
    result = await session.execute(
        select(Transaction).where(Transaction.business_id == business_id)
    )
    existing = result.scalars().all()

    # Check if this business already has categories (it should, from creation)
    stmt_cat = select(TransactionCategory).where(
        TransactionCategory.business_id == business_id
    )
    cats_result = await session.execute(stmt_cat)
    business_cats = {c.name: c.id for c in cats_result.scalars().all()}

    # If no categories found (e.g. old business profile), create them now
    if not business_cats:
        from app.modules.finance.repository import FinanceRepository

        repo = FinanceRepository(session)
        await repo.create_default_categories(business_id)

        # Refresh
        cats_result = await session.execute(stmt_cat)
        business_cats = {c.name: c.id for c in cats_result.scalars().all()}

    if not existing:
        transactions = []
        base_date = datetime.now(timezone.utc)

        # Income
        penjualan_id = business_cats.get("Penjualan")
        if penjualan_id:
            transactions.append(
                Transaction(
                    business_id=business_id,
                    amount=50000,
                    type="INCOME",
                    category_id=penjualan_id,
                    category_name="Penjualan",
                    description="Penjualan Paket Nasi Ayam",
                    transaction_date=base_date - timedelta(days=1),
                )
            )
            transactions.append(
                Transaction(
                    business_id=business_id,
                    amount=75000,
                    type="INCOME",
                    category_id=penjualan_id,
                    category_name="Penjualan",
                    description="Penjualan Minuman Dingin",
                    transaction_date=base_date - timedelta(days=2),
                )
            )

        # Expense
        bahan_baku_id = business_cats.get("Bahan Baku")
        if bahan_baku_id:
            transactions.append(
                Transaction(
                    business_id=business_id,
                    amount=20000,
                    type="EXPENSE",
                    category_id=bahan_baku_id,
                    category_name="Bahan Baku",
                    description="Beli Beras",
                    transaction_date=base_date - timedelta(days=1),
                )
            )

        if transactions:
            session.add_all(transactions)
            await session.commit()
            logger.info(f"Created {len(transactions)} transactions")
    else:
        logger.info(f"Transactions exist ({len(existing)} records)")
