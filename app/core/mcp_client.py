import json
from typing import List, Dict, Any
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.sse import sse_client
from llama_index.core.tools import FunctionTool
from app.core.logging import logger


class MCPToolClient:
    """
    Manages connections to MCP servers defined in a configuration file
    and exposes their tools as LlamaIndex FunctionTools.
    """

    def __init__(self, config_path: str = "mcp.json"):
        self.config_path = config_path
        self.exit_stack = AsyncExitStack()
        self.sessions: List[ClientSession] = []
        self.tools: List[FunctionTool] = []

    async def initialize(self):
        """
        Reads config, connects to servers, and loads tools.
        Returns a list of LlamaIndex FunctionTool objects.
        """
        try:
            with open(self.config_path, "r") as f:
                config = json.load(f)
        except FileNotFoundError:
            logger.warning(f"MCP config file not found at {self.config_path}")
            return []

        servers = config.get("mcpServers", {})

        for name, server_config in servers.items():
            try:
                await self._connect_and_load_tools(name, server_config)
            except Exception as e:
                logger.error(f"Failed to connect to MCP server '{name}': {e}")

        return self.tools

    async def _connect_and_load_tools(self, name: str, config: Dict[str, Any]):
        if "url" in config:
            # SSE Connection
            url = config["url"]
            logger.info(f"Connecting to MCP SSE server '{name}' at {url}")
            # Note: sse_client context manager yields (read, write) streams
            # We need to keep the connection open, so we enter the context and keep it in exit_stack
            read_stream, write_stream = await self.exit_stack.enter_async_context(
                sse_client(url)
            )
            session = await self.exit_stack.enter_async_context(
                ClientSession(read_stream, write_stream)
            )
        elif "command" in config:
            # Stdio Connection
            command = config["command"]
            args = config.get("args", [])
            env = config.get("env", None)

            params = StdioServerParameters(command=command, args=args, env=env)
            logger.info(f"Connecting to MCP Stdio server '{name}': {command} {args}")

            read_stream, write_stream = await self.exit_stack.enter_async_context(
                stdio_client(params)
            )
            session = await self.exit_stack.enter_async_context(
                ClientSession(read_stream, write_stream)
            )
        else:
            logger.warning(
                f"Skipping invalid MCP server config '{name}': missing 'url' or 'command'"
            )
            return

        await session.initialize()
        self.sessions.append(session)

        # List tools
        mcp_tools_result = await session.list_tools()

        for tool in mcp_tools_result.tools:
            logger.info(f"Loaded tool '{tool.name}' from server '{name}'")

            # Create a dynamic function that calls this tool
            async def dynamic_tool_func(**kwargs) -> str:
                # Handle LlamaIndex/LLM wrapping arguments in 'kwargs' key
                if (
                    "kwargs" in kwargs
                    and len(kwargs) == 1
                    and isinstance(kwargs["kwargs"], dict)
                ):
                    kwargs = kwargs["kwargs"]

                # Filter out None values for optional parameters
                kwargs = {k: v for k, v in kwargs.items() if v is not None}

                try:
                    result = await session.call_tool(tool.name, arguments=kwargs)
                    # MCP CallToolResult has content list. We usually just want the text.
                    output = []
                    if result.content:
                        for item in result.content:
                            if item.type == "text":
                                output.append(item.text)
                            else:
                                output.append(f"[{item.type} content]")
                    return "\n".join(output)
                except Exception as call_err:
                    return f"Error calling tool {tool.name}: {str(call_err)}"

            llama_tool = FunctionTool.from_defaults(
                fn=dynamic_tool_func,
                name=tool.name,
                description=tool.description or f"Tool {tool.name} from {name}",
            )
            self.tools.append(llama_tool)

    async def cleanup(self):
        """Close all connections."""
        await self.exit_stack.aclose()


# Global instance
mcp_client = MCPToolClient()
mcp_tools: List[FunctionTool] = []


async def init_mcp_tools():
    global mcp_tools
    tools = await mcp_client.initialize()
    mcp_tools.clear()
    mcp_tools.extend(tools)
    logger.info(f"Initialized {len(mcp_tools)} MCP tools.")


async def cleanup_mcp_tools():
    await mcp_client.cleanup()
