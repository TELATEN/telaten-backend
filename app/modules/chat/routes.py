from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.db.session import get_db
from app.modules.chat.models import (
    ChatMessageCreate,
    ChatSessionRead,
    ChatMessageRead,
)
from app.modules.chat.repository import ChatRepository
from app.modules.chat.service import ChatService
from app.modules.business.repository import BusinessRepository
from app.modules.auth.dependencies import get_current_user, get_current_business
from app.modules.auth.models import User
from app.modules.business.models import BusinessProfile
from uuid import UUID

router = APIRouter()


def get_chat_service(db: AsyncSession = Depends(get_db)) -> ChatService:
    chat_repo = ChatRepository(db)
    business_repo = BusinessRepository(db)
    return ChatService(chat_repo, business_repo)


@router.get("/sessions", response_model=List[ChatSessionRead])
async def get_chat_sessions(
    current_user: User = Depends(get_current_user),
    current_business: BusinessProfile = Depends(get_current_business),
    service: ChatService = Depends(get_chat_service),
):
    """List all chat sessions for the current user's business."""
    return await service.get_business_sessions(current_user.id, current_business.id)


@router.get("/sessions/{session_id}", response_model=List[ChatMessageRead])
async def get_chat_messages(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    service: ChatService = Depends(get_chat_service),
):
    """Get all messages for a specific chat session."""
    return await service.get_session_messages(current_user.id, session_id)


@router.delete("/sessions/{session_id}")
async def delete_chat_session(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    service: ChatService = Depends(get_chat_service),
):
    """Delete a chat session."""
    await service.delete_session(current_user.id, session_id)
    return {"message": "Session deleted successfully"}


@router.post("/completion")
async def chat_completion(
    message: ChatMessageCreate,
    current_user: User = Depends(get_current_user),
    current_business: BusinessProfile = Depends(get_current_business),
    service: ChatService = Depends(get_chat_service),
):
    return StreamingResponse(
        service.stream_chat_completion(current_user.id, current_business.id, message),
        media_type="text/event-stream",
    )
