from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import Column, DateTime, JSON


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


class BusinessProfile(BusinessProfileBase, table=True):
    __tablename__ = "business_profiles"  # type: ignore

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", unique=True, index=True)

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )


class BusinessProfileCreate(BusinessProfileBase):
    pass


class BusinessProfileRead(BusinessProfileBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime


class BusinessProfileUpdate(SQLModel):
    business_name: Optional[str] = None
    business_category: Optional[str] = None
    business_description: Optional[str] = None
    address: Optional[dict] = None
    business_stage: Optional[str] = None
    target_market: Optional[str] = None
    primary_goal: Optional[str] = None
