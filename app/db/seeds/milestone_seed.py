from datetime import datetime, timezone
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.modules.milestone.models import Milestone, MilestoneTask
from app.core.logging import logger


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
