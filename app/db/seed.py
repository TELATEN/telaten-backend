import asyncio
import logging
from datetime import datetime, timedelta, timezone
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, desc
from app.db.session import AsyncSessionLocal
from app.core.security import get_password_hash

# Import Models
from app.modules.auth.models import User
from app.modules.business.models import BusinessLevel, BusinessProfile
from app.modules.gamification.models import Achievement
from app.modules.milestone.models import Milestone, MilestoneTask
from app.modules.finance.models import Transaction, TransactionCategory

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def seed_users(session: AsyncSession) -> User:
    """Seed Admin and Demo User."""
    # Admin
    result = await session.execute(
        select(User).where(User.email == "admin@telaten.com")
    )
    admin = result.scalars().first()
    if not admin:
        admin = User(
            email="admin@telaten.com",
            name="Super Admin",
            hashed_password=get_password_hash("admin123"),
            role="admin",
        )
        session.add(admin)
        logger.info("Created Admin User")
    else:
        logger.info("Admin User exists")

    # Demo User
    result = await session.execute(select(User).where(User.email == "demo@telaten.com"))
    demo = result.scalars().first()
    if not demo:
        demo = User(
            email="demo@telaten.com",
            name="Budi Telaten",
            hashed_password=get_password_hash("demo123"),
            role="user",
        )
        session.add(demo)
        await session.commit()
        await session.refresh(demo)
        logger.info("Created Demo User")
    else:
        logger.info("Demo User exists")

    return demo


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


async def seed_gamification(session: AsyncSession):
    """Seed Business Levels and Achievements."""
    # Levels
    levels_data = [
        {"name": "Pemula", "required_points": 0, "order": 1, "icon": "🌱"},
        {"name": "Perintis", "required_points": 100, "order": 2, "icon": "🚀"},
        {"name": "Penggerak", "required_points": 500, "order": 3, "icon": "⚙️"},
        {"name": "Pelopor", "required_points": 1000, "order": 4, "icon": "🏆"},
        {"name": "Pengusaha Mapan", "required_points": 2500, "order": 5, "icon": "🏢"},
        {"name": "Maestro Bisnis", "required_points": 5000, "order": 6, "icon": "🎩"},
        {"name": "Puncak Pewaris", "required_points": 10000, "order": 7, "icon": "👑"},
    ]

    for data in levels_data:
        result = await session.execute(
            select(BusinessLevel).where(
                BusinessLevel.required_points == data["required_points"]
            )
        )
        level = result.scalars().first()
        if not level:
            level = BusinessLevel(**data)
            session.add(level)
            logger.info(f"Created Level: {data['name']}")
        else:
            # Update fields if needed
            level.name = data["name"]
            level.order = data["order"]
            level.icon = data["icon"]
            session.add(level)
            logger.info(f"Updated Level: {data['name']}")

    # Achievements
    achievements_data = [
        {
            "title": "Langkah Awal",
            "description": "Catat transaksi pertamamu",
            "required_points": 10,
            "badge_icon": "📝",
        },
        {
            "title": "Bisnis Produktif",
            "description": "Capai 100 poin aktivitas",
            "required_points": 100,
            "badge_icon": "📈",
        },
        {
            "title": "Sultan Lokal",
            "description": "Capai 1000 poin aktivitas",
            "required_points": 1000,
            "badge_icon": "💰",
        },
        {
            "title": "Master Telaten",
            "description": "Capai 5000 poin aktivitas",
            "required_points": 5000,
            "badge_icon": "⭐",
        },
    ]

    for data in achievements_data:
        result = await session.execute(
            select(Achievement).where(Achievement.title == data["title"])
        )
        ach = result.scalars().first()
        if not ach:
            ach = Achievement(**data)
            session.add(ach)
            logger.info(f"Created Achievement: {data['title']}")
        else:
            ach.description = data["description"]
            ach.required_points = data["required_points"]
            ach.badge_icon = data["badge_icon"]
            session.add(ach)
            logger.info(f"Updated Achievement: {data['title']}")

    await session.commit()


async def seed_business(session: AsyncSession, user: User) -> BusinessProfile | None:
    """Seed Business Profile for User."""
    result = await session.execute(
        select(BusinessProfile).where(BusinessProfile.user_id == user.id)
    )
    profile = result.scalars().first()

    if not profile:
        profile = BusinessProfile(
            user_id=user.id,
            business_name="Warung Budi Sejahtera",
            business_category="F&B",
            business_description="Warung makan dengan cita rasa nusantara yang khas dan harga terjangkau.",
            business_stage="Operational",
            target_market="Warga Sekitar",
            primary_goal="Increase Sales",
            total_points=50,  # Start with some points
            address={"street": "Jl. Mawar No. 10", "city": "Jakarta"},
        )
        session.add(profile)
        await session.commit()
        await session.refresh(profile)
        logger.info("Created Business Profile")
    else:
        logger.info("Business Profile exists")

    # Ensure level is set (simple check)
    if profile.level_id is None:
        # Find Pemula level
        result = await session.execute(
            select(BusinessLevel)
            .where(BusinessLevel.required_points <= profile.total_points)
            .order_by(desc(BusinessLevel.required_points))
        )
        level = result.scalars().first()
        if level:
            profile.level_id = level.id
            session.add(profile)
            await session.commit()
            logger.info(f"Set Business Level to {level.name}")

    return profile


async def seed_milestones(session: AsyncSession, business_id: UUID):
    """Seed Milestones and Tasks."""
    result = await session.execute(
        select(Milestone).where(Milestone.business_id == business_id)
    )
    existing = result.scalars().first()

    if not existing:
        # Milestone 1
        m1 = Milestone(
            business_id=business_id,
            title="Persiapan Digitalisasi",
            description="Langkah awal mendigitalkan operasional warung",
            status="in_progress",
            started_at=datetime.now(timezone.utc),
            reward_points=50,
            order=1,
            is_generated=False,
        )
        session.add(m1)
        await session.commit()
        await session.refresh(m1)

        tasks1 = [
            MilestoneTask(
                milestone_id=m1.id,
                title="Buat akun Telaten",
                is_completed=True,
                completed_at=datetime.now(timezone.utc),
                reward_points=10,
            ),
            MilestoneTask(
                milestone_id=m1.id,
                title="Lengkapi Profil Bisnis",
                is_completed=True,
                completed_at=datetime.now(timezone.utc),
                reward_points=20,
            ),
            MilestoneTask(
                milestone_id=m1.id,
                title="Catat Transaksi Pertama",
                is_completed=False,
                reward_points=20,
            ),
        ]
        session.add_all(tasks1)
        logger.info("Created Milestone 1")

        # Milestone 2
        m2 = Milestone(
            business_id=business_id,
            title="Ekspansi Menu",
            description="Menambah variasi menu untuk menarik pelanggan",
            status="pending",
            reward_points=100,
            order=2,
            is_generated=False,
        )
        session.add(m2)
        await session.commit()
        await session.refresh(m2)

        tasks2 = [
            MilestoneTask(
                milestone_id=m2.id,
                title="Riset Menu Baru",
                is_completed=False,
                reward_points=30,
            ),
            MilestoneTask(
                milestone_id=m2.id,
                title="Uji Coba Resep",
                is_completed=False,
                reward_points=30,
            ),
            MilestoneTask(
                milestone_id=m2.id,
                title="Launching Menu",
                is_completed=False,
                reward_points=40,
            ),
        ]
        session.add_all(tasks2)
        logger.info("Created Milestone 2")

        await session.commit()
    else:
        logger.info("Milestones exist")


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


async def main():
    logger.info("Starting seeder...")
    async with AsyncSessionLocal() as session:
        await seed_transaction_categories(session) # Seed categories first
        await seed_gamification(session)
        demo_user = await seed_users(session)
        if demo_user:
            business = await seed_business(session, demo_user)
            if business:
                await seed_milestones(session, business.id)
                await seed_finance(session, business.id)
    logger.info("Seeding completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
