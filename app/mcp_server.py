from mcp.server.fastmcp import FastMCP
from app.modules.agent.tools import (
    create_milestone_tool,
    list_milestones_tool,
    update_milestone_tool,
    complete_task_tool,
    start_milestone_tool,
    delete_milestone_tool,
    get_business_summary_tool,
    record_transaction_tool,
    get_financial_report_tool,
    get_transaction_categories_tool,
    update_business_context_tool,
)

# Initialize MCP Server
mcp = FastMCP(
    "Telaten Backend Tools",
    message_path="/messages",
)

mcp.add_tool(create_milestone_tool)
mcp.add_tool(list_milestones_tool)
mcp.add_tool(update_milestone_tool)
mcp.add_tool(complete_task_tool)
mcp.add_tool(start_milestone_tool)
mcp.add_tool(delete_milestone_tool)
mcp.add_tool(get_business_summary_tool)
mcp.add_tool(record_transaction_tool)
mcp.add_tool(get_financial_report_tool)
mcp.add_tool(get_transaction_categories_tool)
mcp.add_tool(update_business_context_tool)
