from uuid import UUID

import structlog
from app.core.logging import setup_logging
from app.modules.agent.workflow import get_onboarding_workflow
from app.core.redis import RedisClient
from llama_index.core.agent.workflow import (
    AgentOutput,
    ToolCall,
    ToolCallResult,
)
import json

setup_logging()
logger = structlog.get_logger()


class AgentService:

    async def run_onboarding_workflow(
        self, user_id: UUID, business_id: UUID, business_data: dict
    ):
        """
        Runs the onboarding agent workflow to generate initial milestones.
        Handles SSE streaming for updates.
        """
        redis = RedisClient.get_instance()
        channel = f"events:{user_id}"

        async def publish_event(
            event_type: str, message: str, data: dict | None = None
        ):
            payload = json.dumps({"type": event_type, "message": message, "data": data})
            await redis.publish(channel, payload)

        try:
            await publish_event(
                "progress", "AI Agents initializing...", {"progress": 5}
            )

            workflow = get_onboarding_workflow()

            # Prompt for the agents
            user_msg = f"""
            Please create a roadmap for this new business.
            
            Business ID: {str(business_id)} (IMPORTANT: Use this ID for tools)
            
            Profile:
            - Name: {business_data['name']}
            - Category: {business_data['category']}
            - Description: {business_data['description']}
            - Stage: {business_data.get('stage', 'Unknown')}
            - Target Market: {business_data.get('target_market', 'Unknown')}
            - Goal: {business_data.get('primary_goal', 'Unknown')}
            - Address: {business_data.get('address', {})}
            """

            # Run workflow with streaming
            handler = workflow.run(user_msg=user_msg)

            async for event in handler.stream_events():
                if isinstance(event, AgentOutput):
                    logger.debug(f"\n[AgentOutput] {event.response}")

                elif isinstance(event, ToolCall):
                    tool_name = event.tool_name
                    tool_args = event.tool_kwargs
                    if tool_name == "create_milestone_tool":
                        title = tool_args.get("title", "New Milestone")
                        msg = f"Creating Milestone: {title}"
                        await publish_event("creating", msg, {"title": title})
                        logger.debug(f"\n[ToolCall] {tool_name} args: {tool_args}")
                    else:
                        msg = "Agent is resarching..."
                        await publish_event(
                            "research", msg, {"tool": tool_name, "args": tool_args}
                        )
                        logger.debug(f"\n[ToolCall] {tool_name} args: {tool_args}")

                elif isinstance(event, ToolCallResult):
                    tool_name = event.tool_name
                    tool_output = str(event.tool_output)
                    msg = "Analyzing the results..."
                    await publish_event("analysis", msg)
                    logger.debug(
                        f"\n[ToolResult] {tool_name} output: {tool_output[:100]}..."
                    )

            await publish_event(
                "completed", "Roadmap generated successfully!", {"progress": 100}
            )

        except Exception as e:
            print(f"Agent Workflow Error: {e}")
            await publish_event("error", f"AI Generation failed: {str(e)}")
            raise e
