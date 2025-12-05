import asyncio
import logging
from app.db.session import AsyncSessionLocal
from app.db.seeds.auth_seed import seed_users, seed_additional_users
from app.db.seeds.business_seed import seed_business
from app.db.seeds.gamification_seed import seed_gamification
from app.db.seeds.finance_seed import seed_transaction_categories, seed_finance
from app.db.seeds.milestone_seed import seed_milestones

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    logger.info("Starting seeder...")
    async with AsyncSessionLocal() as session:
        await seed_transaction_categories(session)  # Seed categories first
        await seed_gamification(session)
        demo_user = await seed_users(session)
        if demo_user:
            business = await seed_business(session, demo_user)
            if business:
                await seed_milestones(session, business.id)
                await seed_finance(session, business.id)

        await seed_additional_users(session)  # Add leaderboard data

    logger.info("Seeding completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
