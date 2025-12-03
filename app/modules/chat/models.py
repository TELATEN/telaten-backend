from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import Column, DateTime


class ChatSessionBase(SQLModel):
    title: str = Field(default="New Chat")


class ChatSession(ChatSessionBase, table=True):
    __tablename__ = "chat_sessions"  # type: ignore

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    business_id: UUID = Field(foreign_key="business_profiles.id", index=True)
    messages: List["ChatMessage"] = Relationship(back_populates="session")
    created_at: datetime = Field(
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


class ChatMessageBase(SQLModel):
    role: str = Field(index=True)
    content: str


class ChatMessage(ChatMessageBase, table=True):
    __tablename__ = "chat_messages"  # type: ignore

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    session_id: UUID = Field(foreign_key="chat_sessions.id", index=True)
    session: Optional[ChatSession] = Relationship(back_populates="messages")
    created_at: datetime = Field(
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


class ChatMessageCreate(SQLModel):
    content: str
    session_id: Optional[UUID] = None


class ChatSessionRead(ChatSessionBase):
    id: UUID
    business_id: UUID
    created_at: datetime


class ChatMessageRead(ChatMessageBase):
    id: UUID
    created_at: datetime
