from uuid import UUID
from typing import AsyncGenerator, Sequence
import structlog
from fastapi import HTTPException, status
from app.core.utils import format_sse
from app.modules.chat.repository import ChatRepository
from app.modules.chat.models import ChatMessage, ChatMessageCreate, ChatSession
from app.modules.business.repository import BusinessRepository
from app.modules.agent.workflow import get_chat_workflow
from llama_index.core.llms import ChatMessage as LLChatMessage, MessageRole
from llama_index.core.agent.workflow import (
    ToolCall,
    ToolCallResult,
    AgentStream,
)

logger = structlog.get_logger()


class ChatService:
    def __init__(self, repo: ChatRepository, business_repo: BusinessRepository):
        self.repo = repo
        self.business_repo = business_repo

    async def get_business_sessions(
        self, user_id: UUID, business_id: UUID
    ) -> Sequence[ChatSession]:
        # 1. Verify Ownership
        profile = await self.business_repo.get_by_id(business_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Business not found"
            )

        if profile.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this business",
            )

        # 2. Fetch Sessions
        return await self.repo.get_sessions_by_business(business_id)

    async def get_session_messages(
        self, user_id: UUID, session_id: UUID
    ) -> Sequence[ChatMessage]:
        # 1. Verify Session & Ownership
        session = await self.repo.get_session(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
            )

        # 2. Verify Business Ownership (indirectly verifies session ownership)
        profile = await self.business_repo.get_by_id(session.business_id)
        if not profile or profile.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this session",
            )

        # 3. Fetch Messages
        return await self.repo.get_history(session_id, limit=100)

    async def stream_chat_completion(
        self, user_id: UUID, business_id: UUID, message_in: ChatMessageCreate
    ) -> AsyncGenerator[str, None]:

        session_id = message_in.session_id

        # 0. Verify Business Ownership (Double check, though route already checked business ownership via dependency if injected,
        # but here we receive business_id explicitly so we should re-verify or assume caller verified).
        # Since we updated route to use `get_current_business`, business_id passed here IS the user's business.
        # But let's keep it safe.
        
        profile = await self.business_repo.get_by_id(business_id)
        if not profile:
            yield format_sse("error", "Business profile not found")
            return

        if profile.user_id != user_id:
            yield format_sse("error", "Not authorized to access this business")
            return

        # Handle Session Creation
        if not session_id:
            new_session = ChatSession(business_id=business_id, title="New Conversation")
            session = await self.repo.create_session(new_session)
            session_id = session.id
            yield format_sse(
                "session_created",
                "New chat session created",
                {"session_id": str(session_id)},
            )
        else:
            session = await self.repo.get_session(session_id)
            if not session:
                yield format_sse("error", "Session not found")
                return

            # Verify session belongs to this business (security check)
            if session.business_id != business_id:
                yield format_sse("error", "Session does not belong to this business")
                return

        # Save User Message
        user_msg = ChatMessage(
            session_id=session_id,
            role="user",
            content=message_in.content,
        )
        await self.repo.create_message(user_msg)

        history_msgs = await self.repo.get_history(session_id, limit=10)
        chat_history = [
            LLChatMessage(
                role=MessageRole.USER if m.role == "user" else MessageRole.ASSISTANT,
                content=m.content,
            )
            for m in history_msgs
        ]

        workflow = get_chat_workflow()

        try:
            context_str = f"""
            CONTEXT:
            Business Name: {profile.business_name}
            Category: {profile.business_category}
            Stage: {profile.business_stage}
            ID: {str(business_id)}
            """

            final_user_msg = f"{context_str}\n\nUser Query: {message_in.content}"

            handler = workflow.run(
                user_msg=final_user_msg, chat_history=chat_history[:-1]
            )

            full_response_text = ""

            async for event in handler.stream_events():
                if isinstance(event, AgentStream):
                    delta = event.delta
                    full_response_text += delta
                    yield format_sse("token", None, {"text": delta})

                elif isinstance(event, ToolCall):
                    yield format_sse(
                        "tool_start",
                        f"Calling tool: {event.tool_name}",
                        {"tool": event.tool_name, "args": event.tool_kwargs},
                    )

                elif isinstance(event, ToolCallResult):
                    yield format_sse(
                        "tool_end",
                        f"Tool {event.tool_name} completed",
                        {
                            "tool": event.tool_name,
                            "output": str(event.tool_output)[:100],
                        },
                    )

            assistant_msg = ChatMessage(
                session_id=session_id,
                role="assistant",
                content=full_response_text,
            )
            await self.repo.create_message(assistant_msg)

            yield format_sse(
                "done",
                None,
                {"full_text": full_response_text, "session_id": str(session_id)},
            )

        except Exception as e:
            logger.error(f"Chat Error: {e}")
            yield format_sse("error", str(e))
