from uuid import UUID
from typing import List
from app.modules.gamification.repository import GamificationRepository
from app.modules.business.repository import BusinessRepository



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
