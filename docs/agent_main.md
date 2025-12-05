## 🚀 Workflows (`workflow.py`)

### **`auto_generate_workflow`**

Handles onboarding and automatic milestone refilling.

* **Agent**: `OnboardingAgent`
* **Role (System Prompt)**: Senior Business Strategist
* **Responsibilities**:

  * Analyze the user’s business context.
  * Generate:

    * **4 initial milestones** for new users, or
    * **3 future milestones** when refilling.
  * Ensure milestones follow a logical, actionable progression.

---

### **`get_chat_workflow`**

Powers the interactive advisor experience.

* **Agent**: `AdvisorAgent` (Telaten Advisor)
* **Role (System Prompt)**: GPS Navigator & Business Manager
* **Capabilities**:

  * **Roadmap Management**: view, update, and modify milestones.
  * **Financial Assistant**: record transactions and generate reports.
  * **Gamification**: access points, level, and achievements.
  * **Long-Term Memory**: store user facts/constraints in `business_profile.ai_context` via `update_business_context_tool`.
* **Rules & Behavior**:

  * **No Overload**: cannot create new milestones if active ones exist (unless explicitly instructed to replace).
  * **Re-Routing**: suggests alternative plans when obstacles arise.
  * **Language Mode**: defaults to Indonesian but can switch to English on request.

---

## 🛠 Tools (`tools.py`)

A collection of async functions exposed to the AI agent as operational tools.

### **📌 Milestone Management**

* `create_milestone_tool`
* `list_milestones_tool`
* `update_milestone_tool`
* `complete_task_tool`
* `start_milestone_tool`
* `delete_milestone_tool`

### **💰 Business & Finance**

* `get_business_summary_tool` — returns gamification stats (points, level, achievements)
* `record_transaction_tool`
* `get_financial_report_tool`
* `get_transaction_categories_tool`

### **🧠 Context Management**

* `update_business_context_tool` — updates persistent AI memory (focus, mood, risks, conditions)

---

# 🏁 Application Entry Points

## **Main App (`main.py`)**

* **Framework**: FastAPI
* **Lifespan Events**:

  * Initialize database and admin user
  * Initialize the **MCP Client** (connecting to external tools)
  * Clean up resources on shutdown
* **Routers Included**: Auth, Business, Milestone, Chat, Gamification, Finance
* **MCP Server Integration**: mounts internal MCP server at `/mcp`

---

## **MCP Server (`mcp_server.py`)**

* **Library**: `mcp[fastmcp]`
* **Purpose**: Exposes internal logic as an MCP-compliant server
* **Endpoints**:

  * SSE endpoint available via `/mcp/sse`
* **Registered Tools**:

  * All tools from `app.modules.agent.tools` are exposed, allowing access from any MCP-compatible client — such as Claude Desktop or the internal MCP Client.

## **External MCP Configuration (`mcp.json`)**

The application uses `mcp.json` to configure connections to external MCP servers. This allows the AI agent to use tools provided by other services.

**Example Configuration (`mcp.json.example`):**

```json
{
  "mcpServers": {
    "sequential-thinking": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
    }
  }
}
```

The `MCPToolClient` in `app/core/mcp_client.py` reads this configuration and automatically loads the tools, making them available to the `AdvisorAgent`.

---

