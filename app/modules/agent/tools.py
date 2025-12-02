from uuid import UUID
from app.modules.milestone.models import Milestone
from app.modules.milestone.repository import MilestoneRepository
from app.db.session import AsyncSessionLocal


async def create_milestone_tool(
    business_id: str, title: str, description: str, order: int
) -> str:
    """
    Creates a new milestone for the business in the database.

    Args:
        business_id: The UUID of the business.
        title: The short title of the milestone.
        description: A detailed, actionable description.
        order: The sequence number (1, 2, 3...).
    """
    try:
        async with AsyncSessionLocal() as session:
            repo = MilestoneRepository(session)
            milestone = Milestone(
                business_id=UUID(business_id),
                title=title,
                description=description,
                order=order,
                is_generated=True,
                status="pending",
            )
            await repo.create_bulk([milestone])
        return f"Success: Milestone '{title}' created."
    except Exception as e:
        return f"Error creating milestone: {str(e)}"
