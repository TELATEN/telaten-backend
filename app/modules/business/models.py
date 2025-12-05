from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import Column, DateTime, JSON

if TYPE_CHECKING:
    from app.modules.milestone.models import Milestone


class BusinessProfileBase(SQLModel):
    business_name: str = Field(index=True)
    business_category: str = Field(index=True)
    business_description: str
    address: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    business_stage: Optional[str] = Field(
        default=None, description="e.g. Idea, Startup, Operational, Expansion"
    )
    target_market: Optional[str] = Field(
        default=None, description="e.g. Students, Professionals, B2B"
    )
    primary_goal: Optional[str] = Field(
        default=None, description="e.g. Increase Sales, Brand Awareness, New Branch"
    )
    total_points: int = Field(default=0, index=True)
    ai_context: Optional[dict] = Field(
        default=None,
        sa_column=Column(JSON, default={}),
        description="Context memory for AI agent (state, focus, risks)",
    )


class BusinessProfile(BusinessProfileBase, table=True):
    __tablename__ = "business_profiles"  # type: ignore

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", unique=True, index=True)

    level_id: Optional[UUID] = Field(default=None, foreign_key="business_levels.id")

    milestones: List["Milestone"] = Relationship(back_populates="business_profile")

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    deleted_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True, index=True),
    )

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None


class BusinessProfileCreate(BusinessProfileBase):
    pass


class BusinessProfileRead(BusinessProfileBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    level_id: Optional[UUID] = None
    level_name: Optional[str] = None
    ai_context: Optional[dict] = Field(default=None, exclude=True)


class BusinessProfileUpdate(SQLModel):
    business_name: Optional[str] = None
    business_category: Optional[str] = None
    business_description: Optional[str] = None
    address: Optional[dict] = None
    business_stage: Optional[str] = None
    target_market: Optional[str] = None
    primary_goal: Optional[str] = None
    total_points: Optional[int] = None


class BusinessLevelBase(SQLModel):
    name: str = Field(index=True)
    required_points: int = Field(index=True)
    order: int = Field(default=0)
    icon: Optional[str] = None


class BusinessLevel(BusinessLevelBase, table=True):
    __tablename__ = "business_levels"  # type: ignore

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )


class BusinessLevelCreate(BusinessLevelBase):
    pass


class BusinessLevelRead(BusinessLevelBase):
    id: UUID
    created_at: datetime


class BusinessLevelUpdate(SQLModel):
    name: Optional[str] = None
    required_points: Optional[int] = None
    order: Optional[int] = None
    icon: Optional[str] = None
