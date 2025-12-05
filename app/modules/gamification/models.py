from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime
from typing import Optional


class AchievementBase(SQLModel):
    title: str = Field(index=True)
    description: str
    required_points: int
    badge_icon: Optional[str] = None


class Achievement(AchievementBase, table=True):
    __tablename__ = "achievements"  # type: ignore

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )


class UserAchievement(SQLModel, table=True):
    __tablename__ = "user_achievements"  # type: ignore

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    achievement_id: UUID = Field(foreign_key="achievements.id", index=True)
    unlocked_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )


class AchievementRead(AchievementBase):
    id: UUID
    created_at: datetime
    is_unlocked: bool = Field(default=False)
    unlocked_at: Optional[datetime] = None


class AchievementCreate(AchievementBase):
    pass


class AchievementUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    required_points: Optional[int] = None
    badge_icon: Optional[str] = None


class LeaderboardEntry(SQLModel):
    rank: int
    business_id: UUID
    business_name: str
    total_points: int
    level_name: Optional[str] = None
    achievements_count: int = 0
    user_id: UUID
    user_name: str
    is_current_user: bool = False
