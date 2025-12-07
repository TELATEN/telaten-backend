from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, desc
from app.core.security import get_password_hash
from app.modules.auth.models import User
from app.modules.business.models import BusinessProfile, BusinessLevel
from app.core.logging import logger


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


async def seed_additional_users(session: AsyncSession):
    """Seed additional dummy users and businesses for leaderboard."""
    users_data = [
        {
            "email": "sari.roti@telaten.com",
            "name": "Sari Roti",
            "business": "Toko Roti Sari",
            "points": 12000,
        },
        {
            "email": "joko.kopi@telaten.com",
            "name": "Joko Kopi",
            "business": "Kopi Joko",
            "points": 8500,
        },
        {
            "email": "lila.laundry@telaten.com",
            "name": "Lila Laundry",
            "business": "Lila Bersih",
            "points": 6200,
        },
        {
            "email": "tina.tailor@telaten.com",
            "name": "Tina Tailor",
            "business": "Tina Modiste",
            "points": 4800,
        },
        {
            "email": "rudi.bengkel@telaten.com",
            "name": "Rudi Bengkel",
            "business": "Bengkel Rudi Jaya",
            "points": 3500,
        },
        {
            "email": "marni.sayur@telaten.com",
            "name": "Marni Sayur",
            "business": "Sayur Segar Marni",
            "points": 2100,
        },
        {
            "email": "anton.gadget@telaten.com",
            "name": "Anton Gadget",
            "business": "Anton Cell",
            "points": 1500,
        },
        {
            "email": "dewi.salon@telaten.com",
            "name": "Dewi Salon",
            "business": "Cantik Salon",
            "points": 900,
        },
        {
            "email": "agus.bakso@telaten.com",
            "name": "Agus Bakso",
            "business": "Bakso Mas Agus",
            "points": 450,
        },
        {
            "email": "siti.jamu@telaten.com",
            "name": "Siti Jamu",
            "business": "Jamu Gendong Siti",
            "points": 150,
        },
        {
            "email": "bambang.nasgor@telaten.com",
            "name": "Bambang Nasgor",
            "business": "Nasi Goreng Bambang",
            "points": 9500,
        },
        {
            "email": "rini.kue@telaten.com",
            "name": "Rini Kue",
            "business": "Rini Cookies",
            "points": 7200,
        },
        {
            "email": "eko.print@telaten.com",
            "name": "Eko Print",
            "business": "Eko Digital Printing",
            "points": 5500,
        },
        {
            "email": "ayu.florist@telaten.com",
            "name": "Ayu Florist",
            "business": "Ayu Bunga Segar",
            "points": 4100,
        },
        {
            "email": "dani.barbershop@telaten.com",
            "name": "Dani Barbershop",
            "business": "Dani Potong Rambut",
            "points": 2800,
        },
        {
            "email": "fajar.snack@telaten.com",
            "name": "Fajar Snack",
            "business": "Aneka Snack Fajar",
            "points": 1800,
        },
        {
            "email": "gita.fashion@telaten.com",
            "name": "Gita Fashion",
            "business": "Gita Boutique",
            "points": 1200,
        },
        {
            "email": "hendra.motor@telaten.com",
            "name": "Hendra Motor",
            "business": "Hendra Service Motor",
            "points": 700,
        },
        {
            "email": "indah.catering@telaten.com",
            "name": "Indah Catering",
            "business": "Dapur Indah",
            "points": 300,
        },
        {
            "email": "jerry.pulsa@telaten.com",
            "name": "Jerry Pulsa",
            "business": "Jerry Cell & PPOB",
            "points": 50,
        },
    ]

    for data in users_data:
        # Check User
        result = await session.execute(select(User).where(User.email == data["email"]))
        user = result.scalars().first()
        if not user:
            user = User(
                email=data["email"],
                name=data["name"],
                hashed_password=get_password_hash("demo123"),
                role="user",
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            logger.info(f"Created User: {data['name']}")

        # Check Business
        result = await session.execute(
            select(BusinessProfile).where(BusinessProfile.user_id == user.id)
        )
        profile = result.scalars().first()
        if not profile:
            profile = BusinessProfile(
                user_id=user.id,
                business_name=data["business"],
                business_category="Retail",
                business_description=f"Usaha {data['business']}",
                business_stage="Operational",
                total_points=data["points"],
            )
            session.add(profile)
            await session.commit()
            await session.refresh(profile)
            logger.info(f"Created Business: {data['business']}")

        # Set Level
        if profile.level_id is None:
            # Find correct level
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
