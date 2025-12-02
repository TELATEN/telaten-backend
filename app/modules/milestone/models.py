from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING
from sqlalchemy import Column, DateTime

if TYPE_CHECKING:
    from app.modules.business.models import BusinessProfile


class MilestoneBase(SQLModel):
    title: str
    description: str
    status: str = Field(default="pending")  # pending, in_progress, completed
    order: int
    is_generated: bool = Field(default=False)


class Milestone(MilestoneBase, table=True):
    __tablename__ = "milestones"  # type: ignore

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    business_id: UUID = Field(foreign_key="business_profiles.id", index=True)

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    business_profile: Optional["BusinessProfile"] = Relationship(
        back_populates="milestones"
    )


class MilestoneCreate(MilestoneBase):
    pass


class MilestoneRead(MilestoneBase):
    id: UUID
    business_id: UUID
    created_at: datetime
    updated_at: datetime
