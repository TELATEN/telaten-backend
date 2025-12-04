from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime
from typing import Optional
from app.modules.business.models import BusinessProfileRead


class UserBase(SQLModel):
    email: str = Field(unique=True, index=True)
    name: Optional[str] = None
    role: str = Field(default="user")


class User(UserBase, table=True):
    __tablename__ = "users"  # type: ignore

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    hashed_password: str
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


class UserCreate(UserBase):
    password: str


class UserLogin(SQLModel):
    email: str
    password: str


class UserRead(UserBase):
    id: UUID
    created_at: datetime


class UserWithBusinessRead(UserRead):
    business: Optional[BusinessProfileRead] = None
