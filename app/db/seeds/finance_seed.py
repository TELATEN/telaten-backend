import logging
from datetime import datetime, timedelta, timezone
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.modules.finance.models import Transaction, TransactionCategory

logger = logging.getLogger(__name__)

async def seed_transaction_categories(session: AsyncSession):
    """Seed Default Transaction Categories."""
    # These categories have business_id = None (Global System Defaults)
    categories_data = [
        # EXPENSE
        {"name": "Bahan Baku", "type": "EXPENSE", "icon": "shopping-cart", "is_default": True},
        {"name": "Gaji Karyawan", "type": "EXPENSE", "icon": "users", "is_default": True},
        {"name": "Sewa Tempat", "type": "EXPENSE", "icon": "home", "is_default": True},
        {"name": "Listrik & Air", "type": "EXPENSE", "icon": "zap", "is_default": True},
        {"name": "Transportasi", "type": "EXPENSE", "icon": "truck", "is_default": True},
        {"name": "Pemasaran", "type": "EXPENSE", "icon": "megaphone", "is_default": True},
        {"name": "Lainnya", "type": "EXPENSE", "icon": "more-horizontal", "is_default": True},

        # INCOME
        {"name": "Penjualan", "type": "INCOME", "icon": "tag", "is_default": True},
        {"name": "Investasi", "type": "INCOME", "icon": "trending-up", "is_default": True},
        {"name": "Bonus", "type": "INCOME", "icon": "gift", "is_default": True},
        {"name": "Lainnya", "type": "INCOME", "icon": "more-horizontal", "is_default": True},
    ]

    for data in categories_data:
        # Check if exists (Global)
        result = await session.execute(
            select(TransactionCategory).where(
                TransactionCategory.name == data["name"],
                TransactionCategory.type == data["type"],
                TransactionCategory.business_id == None
            )
        )
        cat = result.scalars().first()
        if not cat:
            cat = TransactionCategory(**data)
            session.add(cat)
            logger.info(f"Created Category: {data['name']} ({data['type']})")
        else:
            # Optional: Update if needed
            pass
    
    await session.commit()

async def seed_finance(session: AsyncSession, business_id: UUID):
    """Seed Transactions."""
    result = await session.execute(
        select(Transaction).where(Transaction.business_id == business_id)
    )
    existing = result.scalars().all()
    
    # Find some default category IDs
    stmt_cat = select(TransactionCategory).where(TransactionCategory.business_id == None)
    cats_result = await session.execute(stmt_cat)
    default_cats = {c.name: c.id for c in cats_result.scalars().all()}

    if not existing:
        transactions = []
        base_date = datetime.now(timezone.utc)

        # Income
        transactions.append(
            Transaction(
                business_id=business_id,
                amount=50000,
                type="INCOME",
                category="Penjualan",
                category_id=default_cats.get("Penjualan"),
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
                category="Penjualan",
                category_id=default_cats.get("Penjualan"),
                category_name="Penjualan",
                description="Penjualan Minuman Dingin",
                transaction_date=base_date - timedelta(days=2),
            )
        )

        # Expense
        transactions.append(
            Transaction(
                business_id=business_id,
                amount=20000,
                type="EXPENSE",
                category="Bahan Baku",
                category_id=default_cats.get("Bahan Baku"),
                category_name="Bahan Baku",
                description="Beli Beras",
                transaction_date=base_date - timedelta(days=1),
            )
        )

        session.add_all(transactions)
        await session.commit()
        logger.info(f"Created {len(transactions)} transactions")
    else:
        logger.info(f"Transactions exist ({len(existing)} records)")
