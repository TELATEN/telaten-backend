from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.modules.auth.models import User
from app.core.security import get_password_hash
import logging

logger = logging.getLogger(__name__)


async def init_admin_user(session: AsyncSession):
    """
    Create a default admin user if it doesn't exist.
    """
    try:
        stmt = select(User).where(User.email == "admin@telaten.com")
        result = await session.execute(stmt)
        user = result.scalars().first()

        if not user:
            logger.info("Creating default admin user...")
            admin_user = User(
                email="admin@telaten.com",
                name="Super Admin",
                hashed_password=get_password_hash("admin123"),
                role="admin",
            )
            session.add(admin_user)
            await session.commit()
            logger.info("Admin user created: admin@telaten.com / admin123")
        else:
            logger.info("Admin user already exists.")
    except Exception as e:
        logger.error(f"Error creating admin user: {e}")
