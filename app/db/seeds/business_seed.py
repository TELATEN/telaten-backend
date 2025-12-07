from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, desc
from app.modules.auth.models import User
from app.modules.business.models import BusinessProfile, BusinessLevel
from app.core.logging import logger
from app.modules.finance.repository import FinanceRepository


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

        finance_repo = FinanceRepository(session)
        await finance_repo.create_default_categories(profile.id)

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
