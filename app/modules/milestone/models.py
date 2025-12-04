from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import Column, DateTime
from app.modules.business.models import BusinessProfile


class MilestoneTaskBase(SQLModel):
    title: str
    is_completed: bool = Field(default=False)
    order: int = Field(default=0)
    reward_points: int = Field(default=10)


class MilestoneTask(MilestoneTaskBase, table=True):
    __tablename__ = "milestone_tasks"  # type: ignore

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    milestone_id: Optional[UUID] = Field(
        default=None, foreign_key="milestones.id", index=True
    )
    milestone: Optional["Milestone"] = Relationship(back_populates="tasks")

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    completed_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )


class MilestoneBase(SQLModel):
    title: str
    description: str
    status: str = Field(default="pending")
    order: int
    is_generated: bool = Field(default=False)
    level: int = Field(default=1)
    reward_points: int = Field(default=0)


class Milestone(MilestoneBase, table=True):
    __tablename__ = "milestones"  # type: ignore

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    business_id: UUID = Field(foreign_key="business_profiles.id", index=True)
    business_profile: Optional[BusinessProfile] = Relationship(
        back_populates="milestones"
    )
    tasks: List[MilestoneTask] = Relationship(
        back_populates="milestone",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"},
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    started_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )
    completed_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )
    deleted_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True, index=True),
    )

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None


class MilestoneCreate(MilestoneBase):
    tasks: List[MilestoneTaskBase] = []


class MilestoneTaskRead(MilestoneTaskBase):
    id: UUID
    milestone_id: UUID
    completed_at: Optional[datetime] = None


class MilestoneRead(MilestoneBase):
    id: UUID
    business_id: UUID
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    tasks: List[MilestoneTaskRead] = []


class MilestoneListRead(MilestoneBase):
    id: UUID
    business_id: UUID
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None




class MilestoneUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    order: Optional[int] = None
    level: Optional[int] = None
    reward_points: Optional[int] = None


class MilestoneTaskUpdate(SQLModel):
    title: Optional[str] = None
    is_completed: Optional[bool] = None
    reward_points: Optional[int] = None
