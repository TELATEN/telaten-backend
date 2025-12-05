from uuid import UUID
from typing import List
from app.modules.milestone.models import Milestone, MilestoneTask
from app.modules.milestone.repository import MilestoneRepository
from app.modules.business.repository import BusinessRepository
from app.modules.gamification.repository import GamificationRepository
from app.modules.finance.models import TransactionCreate
from app.modules.finance.repository import FinanceRepository
from app.modules.finance.service import FinanceService
from app.modules.gamification.service import GamificationService
from app.db.session import AsyncSessionLocal


async def create_milestone_tool(
    business_id: str,
    title: str,
    description: str,
    order: int,
    tasks: List[str],
    level: int = 1,
    reward_points: int = 0,
) -> str:
    """
    Creates a new milestone for the business in the database with associated tasks.

    Args:
        business_id: The UUID of the business.
        title: The short title of the milestone.
        description: A detailed, actionable description.
        order: The sequence number (1, 2, 3...).
        tasks: A list of actionable tasks (strings) for this milestone.
        level: Difficulty level (default 1).
        reward_points: Points awarded upon completion (default 0).
    """
    try:
        async with AsyncSessionLocal() as session:
            repo = MilestoneRepository(session)

            milestone_tasks = [
                MilestoneTask(title=t, order=i + 1) for i, t in enumerate(tasks)
            ]

            milestone = Milestone(
                business_id=UUID(business_id),
                title=title,
                description=description,
                order=order,
                is_generated=True,
                status="pending",
                level=level,
                reward_points=reward_points,
                tasks=milestone_tasks,
            )
            await repo.create_bulk([milestone])
        return f"Success: Milestone '{title}' created with {len(tasks)} tasks."
    except Exception as e:
        return f"Error creating milestone: {str(e)}"


async def list_milestones_tool(
    business_id: str, page: int = 1, size: int = 8
) -> str:
    """
    Lists all milestones and their tasks for a specific business.

    Args:
        business_id: The UUID of the business.
        page: Page number (default 1).
        size: Number of milestones per page (default 8).
    """
    try:
        async with AsyncSessionLocal() as session:
            repo = MilestoneRepository(session)
            milestones = await repo.get_by_business_id(
                UUID(business_id), page=page, size=size
            )

            if not milestones:
                return "No milestones found."

            result = []
            for m in milestones:
                tasks_str = ""
                if m.tasks:
                    tasks_list = []
                    for t in m.tasks:
                        status_mark = "[x]" if t.is_completed else "[ ]"
                        tasks_list.append(f"    {status_mark} {t.title} (ID: {t.id})")
                    tasks_str = "\n" + "\n".join(tasks_list)

                result.append(
                    f"ID: {m.id} | Order: {m.order} | Title: {m.title} | Status: {m.status} | Level: {m.level} | Points: {m.reward_points}{tasks_str}"
                )

            return "\n".join(result)
    except Exception as e:
        return f"Error listing milestones: {str(e)}"


async def update_milestone_tool(
    milestone_id: str,
    status: str | None = None,
    description: str | None = None,
    reward_points: int | None = None,
) -> str:
    """
    Updates a milestone's status, description, or points.

    Args:
        milestone_id: The UUID of the milestone to update.
        status: New status (pending, in_progress, completed).
        description: New description text.
        reward_points: Update reward points.
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
            if reward_points is not None:
                milestone.reward_points = reward_points

            await repo.update(milestone)
            return f"Success: Milestone updated. New Status: {milestone.status}"
    except Exception as e:
        return f"Error updating milestone: {str(e)}"


async def complete_task_tool(task_id: str) -> str:
    """
    Marks a specific task as completed. This may trigger milestone completion if all tasks are done.

    Args:
        task_id: The UUID of the task to complete.
    """
    try:
        async with AsyncSessionLocal() as session:
            repo = MilestoneRepository(session)
            task = await repo.get_task_by_id(UUID(task_id))

            if not task:
                return "Task not found."

            if not task.is_completed:
                task.is_completed = True
                await repo.update_task(task)

                # Check milestone
                if task.milestone_id:
                    milestone = await repo.get_by_id(task.milestone_id)
                    if milestone and milestone.tasks:
                        all_done = all(t.is_completed for t in milestone.tasks)
                        if all_done:
                            milestone.status = "completed"
                            await repo.update(milestone)
                            return f"Success: Task completed. Milestone '{milestone.title}' is now COMPLETED!"

            return "Success: Task completed."
    except Exception as e:
        return f"Error completing task: {str(e)}"


async def start_milestone_tool(milestone_id: str) -> str:
    """
    Starts a milestone by changing its status from 'pending' to 'in_progress'.

    Args:
        milestone_id: The UUID of the milestone to start.
    """
    try:
        async with AsyncSessionLocal() as session:
            repo = MilestoneRepository(session)
            milestone = await repo.get_by_id(UUID(milestone_id))

            if not milestone:
                return "Milestone not found."

            if milestone.status == "pending":
                milestone.status = "in_progress"
                await repo.update(milestone)
                return f"Success: Milestone '{milestone.title}' started."

            return f"Milestone is already {milestone.status}."
    except Exception as e:
        return f"Error starting milestone: {str(e)}"


async def delete_milestone_tool(milestone_id: str) -> str:
    """
    Deletes a milestone.

    Args:
        milestone_id: The UUID of the milestone to delete.
    """
    try:
        async with AsyncSessionLocal() as session:
            repo = MilestoneRepository(session)
            milestone = await repo.get_by_id(UUID(milestone_id))

            if not milestone:
                return "Milestone not found."

            await repo.delete(milestone)
            return "Success: Milestone deleted."
    except Exception as e:
        return f"Error deleting milestone: {str(e)}"


# --- NEW TOOLS FOR BUSINESS DATA & FINANCE ---


async def get_business_summary_tool(business_id: str) -> str:
    """
    Retrieves a summary of the business profile, including total points, level,
    and unlocked achievements.

    Args:
        business_id: The UUID of the business.
    """
    try:
        async with AsyncSessionLocal() as session:
            business_repo = BusinessRepository(session)
            gamification_repo = GamificationRepository(session)

            business = await business_repo.get_by_id(UUID(business_id))
            if not business:
                return "Business not found."

            unlocked_ids = await gamification_repo.get_unlocked_achievement_ids(
                business.id
            )
            all_achievements = await gamification_repo.get_all_achievements()
            unlocked_count = len(unlocked_ids)
            total_achievements = len(all_achievements)

            # Get recent achievements names
            unlocked_names = [a.title for a in all_achievements if a.id in unlocked_ids]
            recent_achievements = (
                ", ".join(unlocked_names[-5:]) if unlocked_names else "None"
            )

            level_name = "N/A"
            if business.level_id:
                level = await business_repo.get_level(business.level_id)
                if level:
                    level_name = level.name

            return (
                f"Business Summary for '{business.business_name}':\n"
                f"- Level: {level_name}\n"
                f"- Total Points: {business.total_points}\n"
                f"- Business Stage: {business.business_stage or 'N/A'}\n"
                f"- Achievements Unlocked: {unlocked_count}/{total_achievements}\n"
                f"- Recent Achievements: {recent_achievements}"
            )
    except Exception as e:
        return f"Error getting business summary: {str(e)}"


async def record_transaction_tool(
    business_id: str,
    type: str,
    amount: float,
    category_name: str,
    description: str = "",
    category_id: str | None = None,
    payment_method: str = "CASH",
) -> str:
    """
    Records a financial transaction (Income or Expense).

    Args:
        business_id: The UUID of the business.
        type: 'INCOME' or 'EXPENSE'.
        amount: The amount of money.
        category_name: Category name (text fallback).
        description: Brief description.
        category_id: UUID of the category (optional but recommended).
        payment_method: 'CASH', 'TRANSFER', 'QRIS', etc.
    """
    try:
        async with AsyncSessionLocal() as session:
            repo = FinanceRepository(session)
            business_repo = BusinessRepository(session)
            gamification_repo = GamificationRepository(session)
            gamification_service = GamificationService(gamification_repo, business_repo)
            service = FinanceService(repo, business_repo, gamification_service)

            cat_uuid = UUID(category_id) if category_id else None

            transaction_in = TransactionCreate(
                amount=amount,
                type=type.upper(),
                category_name=category_name,
                category_id=cat_uuid,
                description=description,
                payment_method=payment_method,
            )

            transaction = await service.create_transaction(
                UUID(business_id), transaction_in
            )
            return f"Success: Recorded {type} of {amount} for '{category_name}'. ID: {transaction.id}"
    except Exception as e:
        return f"Error recording transaction: {str(e)}"


async def get_financial_report_tool(business_id: str, period: str = "month") -> str:
    """
    Gets a financial summary (Income, Expense, Profit) for a period.

    Args:
        business_id: The UUID of the business.
        period: 'week', 'month', or 'year'.
    """
    try:
        async with AsyncSessionLocal() as session:
            repo = FinanceRepository(session)
            business_repo = BusinessRepository(session)
            service = FinanceService(repo, business_repo)

            summary = await service.get_summary(UUID(business_id), period)

            return (
                f"Financial Report ({period}):\n"
                f"Total Income: {summary.total_income}\n"
                f"Total Expense: {summary.total_expense}\n"
                f"Net Profit: {summary.net_profit}\n"
                f"Period: {summary.period_start} to {summary.period_end}"
            )
    except Exception as e:
        return f"Error getting financial report: {str(e)}"


async def get_transaction_categories_tool(business_id: str) -> str:
    """
    Retrieves the list of available transaction categories for the business.
    This includes system default categories and custom business categories.

    Args:
        business_id: The UUID of the business.
    """
    try:
        async with AsyncSessionLocal() as session:
            repo = FinanceRepository(session)
            categories = await repo.get_categories(UUID(business_id))

            if not categories:
                return "No categories found."

            result = []
            for cat in categories:
                default_tag = "[Default]" if cat.is_default else "[Custom]"
                result.append(
                    f"ID: {cat.id} | Name: {cat.name} | Type: {cat.type} | {default_tag}"
                )

            return "\n".join(result)
    except Exception as e:
        return f"Error listing categories: {str(e)}"


async def update_business_context_tool(
    business_id: str,
    current_focus: str | None = None,
    financial_health: str | None = None,
    user_mood: str | None = None,
    condition_update: str | None = None,
    risk_factor: str | None = None,
    remove_condition_index: int | None = None,
    remove_risk_factor_index: int | None = None,
    update_condition_index: int | None = None,
    update_condition_text: str | None = None,
) -> str:
    """
    Updates the AI's context memory about the business status.
    USE THIS whenever the user reveals important changes or conditions.

    Args:
        business_id: The UUID of the business.
        current_focus: E.g., "Marketing", "Product", "Finance".
        financial_health: E.g., "Critical", "Stable", "Growing".
        user_mood: E.g., "Optimistic", "Frustrated", "Burned out".
        condition_update: A specific fact to ADD to the conditions list.
        risk_factor: A risk to ADD.
        remove_condition_index: Index of the condition to REMOVE (0-based).
        remove_risk_factor_index: Index of the risk factor to REMOVE (0-based).
        update_condition_index: Index of the condition to UPDATE.
        update_condition_text: New text for the condition at that index.
    """
    try:
        async with AsyncSessionLocal() as session:
            repo = BusinessRepository(session)
            business = await repo.get_by_id(UUID(business_id))

            if not business:
                return "Business not found."

            # Initialize if empty
            if not business.ai_context:
                business.ai_context = {
                    "conditions": [],
                    "risk_factors": [],
                }

            context = business.ai_context

            if current_focus:
                context["current_focus"] = current_focus
            if financial_health:
                context["financial_health"] = financial_health
            if user_mood:
                context["user_mood"] = user_mood

            # ADD Logic
            if condition_update:
                if "conditions" not in context:
                    context["conditions"] = []
                if condition_update not in context["conditions"]:
                    context["conditions"].append(condition_update)

            if risk_factor:
                if "risk_factors" not in context:
                    context["risk_factors"] = []
                if risk_factor not in context["risk_factors"]:
                    context["risk_factors"].append(risk_factor)

            # UPDATE Logic for Conditions
            if update_condition_index is not None and update_condition_text and "conditions" in context:
                try:
                    if 0 <= update_condition_index < len(context["conditions"]):
                        context["conditions"][update_condition_index] = update_condition_text
                except IndexError:
                    pass

            # REMOVE Logic (Index Based)
            if remove_condition_index is not None and "conditions" in context:
                try:
                    # Check bounds
                    if 0 <= remove_condition_index < len(context["conditions"]):
                        context["conditions"].pop(remove_condition_index)
                except IndexError:
                    pass # Ignore invalid index

            if remove_risk_factor_index is not None and "risk_factors" in context:
                try:
                    if 0 <= remove_risk_factor_index < len(context["risk_factors"]):
                        context["risk_factors"].pop(remove_risk_factor_index)
                except IndexError:
                    pass

            # Save back
            business.ai_context = context
            await repo.update(business)

            return f"Success: Context updated. Focus: {context.get('current_focus', 'N/A')}"

    except Exception as e:
        return f"Error updating context: {str(e)}"
