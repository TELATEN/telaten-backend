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


async def list_milestones_tool(business_id: str) -> str:
    """
    Lists all milestones for a specific business.

    Args:
        business_id: The UUID of the business.
    """
    try:
        async with AsyncSessionLocal() as session:
            repo = MilestoneRepository(session)
            milestones = await repo.get_by_business_id(UUID(business_id))

            if not milestones:
                return "No milestones found."

            result = []
            for m in milestones:
                result.append(
                    f"ID: {m.id} | Order: {m.order} | Title: {m.title} | Status: {m.status}"
                )

            return "\n".join(result)
    except Exception as e:
        return f"Error listing milestones: {str(e)}"


async def update_milestone_tool(
    milestone_id: str, status: str | None = None, description: str | None = None
) -> str:
    """
    Updates a milestone's status or description.

    Args:
        milestone_id: The UUID of the milestone to update.
        status: New status (pending, in_progress, completed).
        description: New description text.
    """
    try:
        async with AsyncSessionLocal() as session:
            repo = MilestoneRepository(session)
            milestone = await repo.get_by_id(UUID(milestone_id))

            if not milestone:
                return "Milestone not found."

            if status:
                milestone.status = status
            if description:
                milestone.description = description

            await repo.update(milestone)
            return f"Success: Milestone updated. New Status: {milestone.status}"
    except Exception as e:
        return f"Error updating milestone: {str(e)}"


async def delete_milestone_tool(milestone_id: str) -> str:
    """
    Deletes a milestone.

    Args:
        milestone_id: The UUID of the milestone to delete.
    """
    # Note: We haven't implemented delete in repo yet, let's assume update status to 'deleted' or implement delete
    # For now, return mock or implement delete in repo.
    return "Error: Delete function not implemented in repository yet."
