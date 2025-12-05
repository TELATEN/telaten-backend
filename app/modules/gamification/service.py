from uuid import UUID
from typing import List, Optional
from app.modules.gamification.repository import GamificationRepository
from app.modules.gamification.models import LeaderboardEntry
from app.modules.business.repository import BusinessRepository
from app.modules.auth.models import User


class GamificationService:
    def __init__(self, repo: GamificationRepository, business_repo: BusinessRepository):
        self.repo = repo
        self.business_repo = business_repo

    async def process_gamification(
        self, business_id: UUID, user_id: UUID, current_points: int
    ) -> List[str]:
        """
        Process all gamification logic: level updates and achievements.
        Returns list of newly unlocked achievement titles.
        """
        await self.check_and_update_level(business_id, current_points)
        return await self.check_and_unlock(user_id, current_points)

    async def check_and_update_level(self, business_id: UUID, current_points: int):
        """
        Checks if the business qualifies for a new level and updates it.
        """
        new_level = await self.business_repo.get_level_by_points(current_points)
        if new_level:
            business = await self.business_repo.get_by_id(business_id)
            if business and business.level_id != new_level.id:
                business.level_id = new_level.id
                await self.business_repo.update(business)

    async def check_and_unlock(self, user_id: UUID, current_points: int) -> List[str]:
        """
        Checks for eligible achievements based on current points and unlocks them.
        Returns a list of titles of newly unlocked achievements.
        """
        all_achievements = await self.repo.get_all_achievements()
        unlocked_ids = await self.repo.get_unlocked_achievement_ids(user_id)
        unlocked_set = set(unlocked_ids)

        newly_unlocked = []
        for ach in all_achievements:
            if ach.id not in unlocked_set and current_points >= ach.required_points:
                await self.repo.unlock_achievement(user_id, ach.id)
                newly_unlocked.append(ach.title)

        return newly_unlocked

    async def get_leaderboard(
        self, limit: int = 10, current_user: Optional[User] = None
    ) -> List[LeaderboardEntry]:
        """
        Retrieves the leaderboard of top businesses.
        """
        top_businesses = await self.business_repo.get_top_businesses(limit)

        leaderboard = []
        for rank, (business, user) in enumerate(top_businesses, start=1):
            # Fetch level name
            level_name = None
            if business.level_id:
                level = await self.business_repo.get_level(business.level_id)
                if level:
                    level_name = level.name

            unlocked_ids = await self.repo.get_unlocked_achievement_ids(
                business.user_id
            )
            achievements_count = len(unlocked_ids)

            leaderboard.append(
                LeaderboardEntry(
                    rank=rank,
                    business_id=business.id,
                    business_name=business.business_name,
                    total_points=business.total_points,
                    level_name=level_name,
                    achievements_count=achievements_count,
                    user_id=user.id,
                    user_name=user.name or "Unknown",
                    is_current_user=(current_user is not None and user.id == current_user.id),
                )
            )

        if current_user:
            # Check if current user is already in leaderboard
            if not any(entry.user_id == current_user.id for entry in leaderboard):
                business = await self.business_repo.get_by_user_id(current_user.id)
                if business and not business.deleted_at:
                    rank = await self.business_repo.calculate_rank(
                        business.total_points or 0
                    )

                    level_name = None
                    if business.level_id:
                        level = await self.business_repo.get_level(business.level_id)
                        if level:
                            level_name = level.name

                    unlocked_ids = await self.repo.get_unlocked_achievement_ids(
                        current_user.id
                    )
                    achievements_count = len(unlocked_ids)

                    leaderboard.append(
                        LeaderboardEntry(
                            rank=rank,
                            business_id=business.id,
                            business_name=business.business_name,
                            total_points=business.total_points or 0,
                            level_name=level_name,
                            achievements_count=achievements_count,
                            user_id=current_user.id,
                            user_name=current_user.name or "Unknown",
                            is_current_user=True,
                        )
                    )

        return leaderboard
