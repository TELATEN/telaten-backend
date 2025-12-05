# Telaten Backend 🚀

**Telaten** (from Javanese, meaning *“diligent”* or *“patient perseverance”*) is an AI-powered backend system crafted to support Indonesian MSMEs (UMKM) on their business journey. It blends **Gamification**, **Financial Tracking**, and **AI-driven Business Roadmaps** into a unified, empowering business companion.

## 📚 Documentation

* **[Infrastructure & Core](docs/infrastructure.md)** – Database, security layers, and configuration architecture.
* **[Auth & Business](docs/auth_business.md)** – User accounts, business profiles, and onboarding flows.
* **[Finance & Milestones](docs/finance_milestone.md)** – Transaction tracking and actionable business roadmaps.
* **[Gamification & Chat](docs/gamification_chat.md)** – Points, badges, leaderboards, and AI-assisted conversations.
* **[Agent & System Entry](docs/agent_main.md)** – AI workflows, tools, MCP server details, and application entry points.

## 🌟 Key Features

* **🤖 AI Business Advisor**
  A proactive agent (“Telaten Advisor”) functioning like a business GPS—monitoring progress, generating tasks, and guiding owners through each milestone.

* **🗺️ Adaptive Roadmaps**
  Automatically generated milestones that evolve with the business’s development and completion history.

* **💰 Financial Tracking Made Simple**
  Intuitive income/expense recording, automated summaries, and gamified incentives that reward consistency.

* **🏆 Gamification Layer**
  Earn points, unlock achievements, and rise through the leaderboard for staying diligent.

* **🔌 MCP-Powered Integration**
  Built using the **Model Context Protocol (MCP)**, enabling seamless interaction between AI agents, internal tools, and external services.

## 🏗️ Architecture Overview

This project adopts a clean, modular architecture using **FastAPI**, **SQLModel**, and **LlamaIndex**.

### Directory Structure

* **`app/core`** – Configuration, logging, security, and the MCP client.
* **`app/db`** – Database initialization, session handling, and seed logic.
* **`app/modules`** – Domain-specific modules:

  * `agent` – AI workflows & tools
  * `auth` – Authentication & authorization
  * `business` – Business profile management
  * `chat` – History management & SSE/streaming
  * `finance` – Transactions & reports
  * `gamification` – Points, badges, and leaderboards
  * `milestone` – Roadmap tasks and progress tracking
* **`app/main.py`** – Application entry point and router aggregation
* **`app/mcp_server.py`** – Internal MCP server exposing Telaten’s toolset

## 🚀 Getting Started

1. **Install dependencies**

   Make sure you have `uv` installed.
   ```bash
   uv sync
   ```

2. **Set up environment variables**
   Duplicate `.env.example` → `.env`, then configure your database and LLM settings.

3. **Run the server**

   You can run the server using one of the following methods:

   **Option A: Using `uv` directly (Recommended)**
   ```bash
   uv run python run.py
   ```

   **Option B: Activating the virtual environment**
   ```bash
   source .venv/bin/activate
   python run.py
   ```

4. **Open documentation**
   Visit `http://localhost:8000/docs` for the interactive API explorer.

## 🐳 Docker

You can also run the application using Docker Compose:

```bash
docker-compose up --build
```

This will start the backend service and a PostgreSQL database.

---

**Built with ❤️ to help Indonesian MSMEs grow—one diligent step at a time.**

---
