import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.modules.gamification.models import Achievement
from app.modules.business.models import BusinessLevel

logger = logging.getLogger(__name__)

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
