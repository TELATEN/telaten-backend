from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from uuid import UUID
from typing import Sequence
from app.modules.chat.models import ChatMessage, ChatSession


class ChatRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_session(self, session_data: ChatSession) -> ChatSession:
        self.session.add(session_data)
        await self.session.commit()
        await self.session.refresh(session_data)
        return session_data

    async def get_session(self, session_id: UUID) -> ChatSession | None:
        statement = select(ChatSession).where(ChatSession.id == session_id)
        result = await self.session.execute(statement)
        return result.scalars().first()

    async def get_sessions_by_business(self, business_id: UUID) -> Sequence[ChatSession]:
        statement = (
            select(ChatSession)
            .where(ChatSession.business_id == business_id)
            .order_by(ChatSession.created_at.desc()) # type: ignore
        )
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def create_message(self, message: ChatMessage) -> ChatMessage:
        self.session.add(message)
        await self.session.commit()
        await self.session.refresh(message)
        return message

    async def get_history(
        self, session_id: UUID, limit: int = 50
    ) -> Sequence[ChatMessage]:
        statement = (
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.asc())  # type: ignore
            .limit(limit)
        )
        result = await self.session.execute(statement)
        return result.scalars().all()
