# 🏗️ Infrastructure Documentation

The infrastructure layer defines Telaten Backend’s **core configuration**, **security**, **MCP integration**, and **database foundation**.
Everything in this section supports the higher-level business logic.

---

## ⚙️ Core Configuration

The `app/core` directory contains the essential building blocks for application setup, security, and AI integrations.

---

### 📄 Config (`config.py`)

Centralized application settings powered by **pydantic-settings**, ensuring clean environment variable management across environments.

**Key Settings Include:**

* `PROJECT_NAME`: Telaten Backend
* `API_V1_STR`: Base path for API v1 (default: `/api/v1`)
* `DATABASE_URL`: PostgreSQL DSN using the `asyncpg` driver
* `SECRET_KEY`: JWT signing key
* `ACCESS_TOKEN_EXPIRE_MINUTES`: Default access token TTL (60 minutes)
* `REFRESH_TOKEN_EXPIRE_DAYS`: Refresh token validity (7 days)
* `LLM_API_KEY`, `LLM_BASE_URL`, `LLM_MODEL_NAME`: AI provider configuration

**Environment Variables (`.env`):**

Make sure to configure the following in your `.env` file (see `.env.example`):

```ini
PROJECT_NAME="Telaten Backend"
API_V1_STR="/api/v1"
PORT=8000
DATABASE_URL="postgresql+asyncpg://user:password@host:5432/dbname"
SECRET_KEY="your_secret_key_here"
LLM_API_KEY="your_llm_api_key"
LLM_BASE_URL="https://api.provider.com"
LLM_MODEL_NAME="model-name"
```

---

### 🔐 Security (`security.py`)

Handles password encryption, token encoding, and authentication utilities.

**Features:**

* **Password Hashing:** Uses `bcrypt` via `passlib`
* **JWT Generation:** Access + Refresh tokens using `python-jose`
* **Algorithm:** HS256
* **Utilities:** Token verification + payload decoding

---

### 🧠 MCP Client (`mcp_client.py`)

Provides connectivity to external **Model Context Protocol (MCP)** servers, enabling the AI agent to use third-party tools and contextual data sources.

**Capabilities:**

* Supports **Stdio** and **SSE** transport modes
* Automatically discovers and loads tools from configured MCP endpoints
* Wraps MCP tools into `llama_index` **FunctionTool** objects
* Fully configurable through `mcp.json`

---

## 🗄️ Database Layer

The `app/db` directory maintains database connectivity, schema initialization, and session lifecycle using **SQLModel** + **SQLAlchemy Async**.

---

### 🔌 Session (`session.py`)

* **Engine:** Async SQLAlchemy engine using `asyncpg`
* **Session Provider:** `get_db` dependency that yields an `AsyncSession`
* **Initialization:** `init_db` creates all tables registered in SQLModel metadata

---

### 🌱 Initialization (`init_data.py`)

* Creates a **default Admin User** (`admin@telaten.com`) on first startup
* Ensures secure bootstrapping of the application

---

## 📜 Logging & AI

### **Logging (`logging.py`)**

* Uses **structlog** for structured, JSON-friendly logs.
* Configurable log levels via `LOG_LEVEL` environment variable.

### **LLM Factory (`llm.py`)**

* Centralized factory pattern to instantiate Large Language Models.
* Supports generic OpenAI-compatible providers (Groq, Together AI, DeepSeek, etc.) based on `.env` configuration.

---
