from uuid import UUID
from datetime import datetime
from typing import AsyncGenerator, Sequence
from fastapi import HTTPException, status
from app.core.utils import format_sse
from app.core.logging import logger
from app.modules.chat.repository import ChatRepository
from app.modules.chat.models import ChatMessage, ChatMessageCreate, ChatSession
from app.modules.business.repository import BusinessRepository
from app.modules.agent.workflow import get_chat_workflow
from app.modules.auth.models import User
from llama_index.core.llms import ChatMessage as LLChatMessage, MessageRole
from llama_index.core.agent.workflow import (
    ToolCall,
    ToolCallResult,
    AgentStream,
)


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
                status_code=status.HTTP_404_NOT_FOUND, detail="Session Id not found"
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

    async def delete_session(self, user_id: UUID, session_id: UUID) -> None:
        # 1. Verify Session
        session = await self.repo.get_session(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
            )

        # 2. Verify Ownership
        profile = await self.business_repo.get_by_id(session.business_id)
        if not profile or profile.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this session",
            )
        # 3. Delete
        await self.repo.delete_session(session)

    async def stream_chat_completion(
        self, user_id: UUID, business_id: UUID, message_in: ChatMessageCreate
    ) -> AsyncGenerator[str, None]:

        session_id = message_in.session_id

        profile = await self.business_repo.get_by_id(business_id)
        if not profile:
            yield format_sse("error", "Business profile not found")
            return

        if profile.user_id != user_id:
            yield format_sse("error", "Not authorized to access this business")
            return

        # Handle Session Creation
        if not session_id:
            session_title = " ".join(message_in.content.split(" ")[:4])
            new_session = ChatSession(business_id=business_id, title=session_title)
            session = await self.repo.create_session(new_session)
            session_id = session.id
            yield format_sse(
                "session_created",
                session_title,
                str(session_id),
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
        ai_memory = profile.ai_context or {}

        # Fetch User to get name
        user_obj = await self.business_repo.session.get(User, user_id)
        user_name = user_obj.name if user_obj else "N/A"
        current_date = datetime.now().strftime("%A, %d %B %Y")

        context_str = f"""
            CONTEXT:
            Business Name: {profile.business_name}
            Category: {profile.business_category}
            Stage: {profile.business_stage}
            ID: {str(business_id)}

            User Name: {user_name}
            Current Date: {current_date}
            """

        workflow = get_chat_workflow(system_prompt=context_str, initial_state=ai_memory)
        logger.debug(f"Starting Chat Workflow for session {session_id}")
        logger.debug(f"User Message: {message_in.content}")
        try:
            handler = workflow.run(
                user_msg=message_in.content, chat_history=chat_history[:-1]
            )

            full_response_text = ""

            async for event in handler.stream_events():
                if isinstance(event, AgentStream):
                    delta = event.delta
                    full_response_text += delta
                    yield format_sse("token", None, {"text": delta})

                elif isinstance(event, ToolCall):
                    logger.debug(
                        f"Tool Call: {event.tool_name} with args {event.tool_kwargs}"
                    )
                    yield format_sse(
                        "tool_start",
                        f"Calling tool: {event.tool_name}",
                        {"tool": event.tool_name, "args": event.tool_kwargs},
                    )

                elif isinstance(event, ToolCallResult):
                    logger.debug(
                        f"Tool Result: {event.tool_name} output {event.tool_output}"
                    )
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

        except Exception as e:
            logger.error(f"Chat Error: {e}")
            yield format_sse("error", str(e))
