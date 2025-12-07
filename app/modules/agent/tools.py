from uuid import UUID
from datetime import datetime
from typing import List
from app.modules.milestone.models import Milestone, MilestoneTask
from app.modules.milestone.repository import MilestoneRepository
from app.modules.business.repository import BusinessRepository
from app.modules.gamification.repository import GamificationRepository
from app.modules.finance.models import TransactionCreate, TransactionCategoryCreate
from app.modules.finance.repository import FinanceRepository
from app.modules.finance.service import FinanceService
from app.modules.gamification.service import GamificationService
from app.db.session import AsyncSessionLocal
from sqlalchemy.orm.attributes import flag_modified


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
    business_id: str, page: int = 1, size: int = 8, status: str = "in_progress"
) -> str:
    """
    Lists all milestones and their tasks for a specific business.

    Args:
        business_id: The UUID of the business.
        page: Page number (default 1).
        size: Number of milestones per page (default 8).
        status: Filter by status. Default is 'in_progress'. Use 'active' for (pending + in_progress), or 'all' for everything.
    """
    try:
        async with AsyncSessionLocal() as session:
            repo = MilestoneRepository(session)

            status_filter = None
            if status == "active":
                status_filter = ["pending", "in_progress"]
            elif status and status.lower() != "all":
                status_filter = status

            milestones = await repo.get_by_business_id(
                UUID(business_id), page=page, size=size, status=status_filter
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


async def create_transaction_category_tool(
    business_id: str, name: str, type: str
) -> str:
    """
    Creates a new CUSTOM transaction category for the business.
    Use this when the user needs a category that doesn't exist in the default list.

    Args:
        business_id: The UUID of the business.
        name: The name of the new category (e.g., "Endorsements", "Software Subscriptions").
        type: 'INCOME' or 'EXPENSE'.
    """
    try:
        async with AsyncSessionLocal() as session:
            repo = FinanceRepository(session)
            business_repo = BusinessRepository(session)
            service = FinanceService(repo, business_repo)

            category_in = TransactionCategoryCreate(name=name, type=type.upper())

            category = await service.create_category(UUID(business_id), category_in)
            return (
                f"Success: Created new category '{category.name}' (ID: {category.id})"
            )
    except Exception as e:
        return f"Error creating category: {str(e)}"


async def list_recent_transactions_tool(business_id: str, limit: int = 5) -> str:
    """
    Lists the most recent transactions for the business.
    Use this to see details of expenses or income sources.

    Args:
        business_id: The UUID of the business.
        limit: Number of transactions to return (default 5).
    """
    try:
        async with AsyncSessionLocal() as session:
            repo = FinanceRepository(session)
            # unpack the tuple (transactions, count)
            transactions, _ = await repo.get_by_business_id(
                UUID(business_id), skip=0, limit=limit
            )

            if not transactions:
                return "No recent transactions found."

            result = ["Recent Transactions:"]
            for t in transactions:
                t_date = (
                    t.transaction_date.strftime("%Y-%m-%d")
                    if t.transaction_date
                    else "N/A"
                )
                result.append(
                    f"- {t_date} | {t.type} | {t.category_name} | Amount: {t.amount} | Desc: {t.description or '-'}"
                )

            return "\n".join(result)
    except Exception as e:
        return f"Error listing transactions: {str(e)}"


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
    category_id: str,
    category_name: str,
    description: str = "",
    payment_method: str = "CASH",
    transaction_date: str | None = None,
) -> str:
    """
    Records a financial transaction (Income or Expense).
    CRITICAL: You MUST provide a valid 'category_id'. call 'get_transaction_categories_tool' first if needed.

    Args:
        business_id: The UUID of the business.
        type: 'INCOME' or 'EXPENSE'.
        amount: The amount of money.
        category_id: UUID of the category. REQUIRED.
        category_name: Category name (for display/snapshot). REQUIRED.
        description: Brief description.
        payment_method: 'CASH', 'TRANSFER', 'QRIS', etc.
        transaction_date: ISO date string (e.g., '2023-12-25'). Defaults to now.
    """
    try:
        if not category_id:
            return "Error: 'category_id' is required. Please check available categories first."

        async with AsyncSessionLocal() as session:
            repo = FinanceRepository(session)
            business_repo = BusinessRepository(session)
            gamification_repo = GamificationRepository(session)
            gamification_service = GamificationService(gamification_repo, business_repo)
            service = FinanceService(repo, business_repo, gamification_service)

            cat_uuid = UUID(category_id)

            t_date = None
            if transaction_date:
                try:
                    t_date = datetime.fromisoformat(transaction_date)
                except ValueError:
                    return "Error: Invalid date format. Use ISO format (YYYY-MM-DD)."

            transaction_in = TransactionCreate(
                amount=amount,
                type=type.upper(),
                category_name=category_name,
                category_id=cat_uuid,
                description=description,
                payment_method=payment_method,
                transaction_date=t_date,
            )

            transaction = await service.create_transaction(
                UUID(business_id), transaction_in
            )
            return f"Success: Recorded {type} of {amount} for category ID '{category_id}' (Name: {category_name}). ID: {transaction.id}"
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
                result.append(f"ID: {cat.id} | Name: {cat.name} | Type: {cat.type}")

            return "\n".join(result)
    except Exception as e:
        return f"Error listing categories: {str(e)}"


async def update_business_context_tool(
    business_id: str,
    current_focus: str | None = None,
    financial_health: str | None = None,
    business_scale: str | None = None,
    sales_channel: str | None = None,
    operational_type: str | None = None,
    condition_update: str | None = None,
    risk_factor: str | None = None,
    personal_memory: str | None = None,
    remove_condition_index: int | None = None,
    remove_risk_factor_index: int | None = None,
    remove_personal_memory_index: int | None = None,
    update_condition_index: int | None = None,
    update_condition_text: str | None = None,
) -> str:
    """
    Updates the AI's context memory about the business status and user.
    USE THIS whenever the user reveals important changes, conditions, or personal details.

    Args:
        business_id: The UUID of the business.
        current_focus: E.g., "Marketing", "Product", "Finance".
        financial_health: E.g., "Critical", "Stable", "Growing".
        business_scale: E.g., "Micro" (Home-based), "Small" (Has staff), "Medium" (Multiple branches).
        sales_channel: E.g., "Online", "Offline", "Hybrid".
        operational_type: E.g., "Producer" (Makes product), "Reseller" (Sells others'), "Service".
        condition_update: A specific business fact to ADD (e.g., "Menu favorite: Bakso").
        risk_factor: A business risk to ADD.
        personal_memory: A personal detail about the user to ADD (e.g., "Nama panggilan: Budi", "Suka dipuji", "Punya anak 2").
        remove_condition_index: Index of the condition to REMOVE.
        remove_risk_factor_index: Index of the risk factor to REMOVE.
        remove_personal_memory_index: Index of the personal memory to REMOVE.
        update_condition_index: Index of the condition to UPDATE.
        update_condition_text: New text for the condition at that index.
    """
    try:
        async with AsyncSessionLocal() as session:
            repo = BusinessRepository(session)
            business = await repo.get_by_id(UUID(business_id))

            if not business:
                return "Business not found."

            if not business.ai_context:
                business.ai_context = {
                    "current_focus": "N/A",
                    "financial_health": "N/A",
                    "business_scale": "Micro",
                    "sales_channel": "N/A",
                    "operational_type": "N/A",
                    "conditions": [],
                    "risk_factors": [],
                    "personal_memory": [],
                }

            context = business.ai_context
            context.setdefault("current_focus", "N/A")
            context.setdefault("financial_health", "N/A")
            context.setdefault("business_scale", "Micro")
            context.setdefault("sales_channel", "N/A")
            context.setdefault("operational_type", "N/A")
            context.setdefault("conditions", [])
            context.setdefault("risk_factors", [])
            context.setdefault("personal_memory", [])

            # Update Single Fields
            if current_focus and current_focus.lower() != "none":
                context["current_focus"] = current_focus
            if financial_health and financial_health.lower() != "none":
                context["financial_health"] = financial_health
            if business_scale and business_scale.lower() != "none":
                context["business_scale"] = business_scale
            if sales_channel and sales_channel.lower() != "none":
                context["sales_channel"] = sales_channel
            if operational_type and operational_type.lower() != "none":
                context["operational_type"] = operational_type

            # ADD Logic
            if condition_update and condition_update.lower() != "none":
                if condition_update not in context["conditions"]:
                    context["conditions"].append(condition_update)

            if risk_factor and risk_factor.lower() != "none":
                if risk_factor not in context["risk_factors"]:
                    context["risk_factors"].append(risk_factor)

            if personal_memory and personal_memory.lower() != "none":
                if personal_memory not in context["personal_memory"]:
                    context["personal_memory"].append(personal_memory)

            # UPDATE Logic for Conditions
            if (
                update_condition_index is not None
                and update_condition_text
                and update_condition_text.lower() != "none"
            ):
                try:
                    if 0 <= update_condition_index < len(context["conditions"]):
                        context["conditions"][
                            update_condition_index
                        ] = update_condition_text
                except IndexError:
                    pass

            if remove_condition_index is not None:
                try:
                    if 0 <= remove_condition_index < len(context["conditions"]):
                        context["conditions"].pop(remove_condition_index)
                except IndexError:
                    pass

            if remove_risk_factor_index is not None:
                try:
                    if 0 <= remove_risk_factor_index < len(context["risk_factors"]):
                        context["risk_factors"].pop(remove_risk_factor_index)
                except IndexError:
                    pass

            if remove_personal_memory_index is not None:
                try:
                    if (
                        0
                        <= remove_personal_memory_index
                        < len(context["personal_memory"])
                    ):
                        context["personal_memory"].pop(remove_personal_memory_index)
                except IndexError:
                    pass

            # Save back
            flag_modified(business, "ai_context")
            business.ai_context = context
            await repo.update(business)

            return f"Success: Context updated : {context}"

    except Exception as e:
        return f"Error updating context: {str(e)}"
