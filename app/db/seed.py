import asyncio
from app.db.session import AsyncSessionLocal
from app.db.seeds.auth_seed import seed_users, seed_additional_users
from app.db.seeds.business_seed import seed_business
from app.db.seeds.gamification_seed import seed_gamification
from app.db.seeds.finance_seed import seed_finance
from app.db.seeds.milestone_seed import seed_milestones
from app.core.logging import logger


async def main():
    logger.info("Starting seeder...")
    async with AsyncSessionLocal() as session:
        await seed_gamification(session)
        demo_user = await seed_users(session)
        if demo_user:
            business = await seed_business(session, demo_user)
            if business:
                await seed_milestones(session, business.id)
                await seed_finance(session, business.id)

        await seed_additional_users(session)

    logger.info("Seeding completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
