from uuid import UUID
from typing import AsyncGenerator
import structlog
from app.core.utils import format_sse
from app.modules.agent.workflow import auto_generate_workflow
from llama_index.core.agent.workflow import (
    AgentOutput,
    ToolCall,
    ToolCallResult,
)

logger = structlog.get_logger()


class AgentService:

    async def run_onboarding_workflow(
        self, business_id: UUID, business_data: dict
    ) -> AsyncGenerator[str, None]:

        try:
            yield format_sse("progress", "AI Agents initializing...", {"progress": 5})
            system_prompt = f"""Business ID: {str(business_id)} (IMPORTANT: Use this ID for tools)
            
            Profile:
            - Name: {business_data['name']}
            - Category: {business_data['category']}
            - Description: {business_data['description']}
            - Stage: {business_data.get('stage', 'Unknown')}
            - Target Market: {business_data.get('target_market', 'Unknown')}
            - Goal: {business_data.get('primary_goal', 'Unknown')}
            - Address: {business_data.get('address', {})}
              """

            workflow = auto_generate_workflow(system_prompt)

            user_msg = """Please create a roadmap for this new business."""

            handler = workflow.run(user_msg=user_msg)
            logger.debug("[Onboarding Workflow] Agent Workflow started.")

            async for event in handler.stream_events():
                if isinstance(event, AgentOutput):
                    logger.debug(f"\n[AgentOutput] {event.response}")

                elif isinstance(event, ToolCall):
                    tool_name = event.tool_name
                    tool_args = event.tool_kwargs
                    if tool_name == "create_milestone_tool":
                        title = tool_args.get("title", "New Milestone")
                        msg = f"Creating Milestone: {title}"
                        yield format_sse("creating", msg, {"title": title})
                        logger.debug(f"\n[ToolCall] {tool_name} args: {tool_args}")
                    else:
                        msg = "Agent is researching..."
                        yield format_sse("research", msg, {"tool": tool_name})
                        logger.debug(f"\n[ToolCall] {tool_name} args: {tool_args}")

                elif isinstance(event, ToolCallResult):
                    tool_name = event.tool_name
                    tool_output = str(event.tool_output)
                    msg = "Analyzing the results..."
                    yield format_sse("analysis", msg)
                    logger.debug(
                        f"\n[ToolResult] {tool_name} output: {tool_output[:100]}..."
                    )

            yield format_sse(
                "completed", "Roadmap generated successfully!", {"progress": 100}
            )

        except ValueError as e:
            logger.error(f"Validation Error: {e}")
            yield format_sse("error", f"Validation Error: {str(e)}")
        except RuntimeError as e:
            logger.error(f"Runtime Error: {e}")
            yield format_sse("error", f"System Error: {str(e)}")
        except Exception as e:
            logger.error(f"Agent Workflow Error: {e}")
            yield format_sse("error", f"AI Generation failed: {str(e)}")
