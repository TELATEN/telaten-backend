<div align="center">
  <h1>🏗️ Infrastructure Documentation</h1>
  <p><em>Core configuration, security, MCP integration, and database foundation</em></p>
</div>

---

## 📋 Overview

The infrastructure layer defines Telaten Backend's **core configuration**, **security**, **MCP integration**, and **database foundation**. Everything in this section supports the higher-level business logic.

---

## 📚 Table of Contents

- [⚙️ Core Configuration](#️-core-configuration)
  - [📄 Config](#-config-configpy)
  - [🔐 Security](#-security-securitypy)
  - [🧠 MCP Client](#-mcp-client-mcp_clientpy)
- [🗄️ Database Layer](#️-database-layer)
  - [🔌 Session](#-session-sessionpy)
  - [🌱 Initialization](#-initialization-init_datapy)
- [📜 Logging & AI](#-logging--ai)

---

## ⚙️ Core Configuration

> 🏠 **Location**: `app/core/`  
> 🎯 **Purpose**: Essential building blocks for application setup, security, and AI integrations

### 📄 Config (`config.py`)

Centralized application settings powered by **pydantic-settings**, ensuring clean environment variable management across environments.

#### 🔧 Key Configuration Settings

| **Setting** | **Default** | **Description** |
|-------------|-------------|-----------------|
| `PROJECT_NAME` | `"Telaten Backend"` | Application name |
| `API_V1_STR` | `"/api/v1"` | Base path for API v1 |
| `DATABASE_URL` | - | PostgreSQL DSN using `asyncpg` driver |
| `SECRET_KEY` | - | JWT signing key (required) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | Access token TTL |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Refresh token validity |
| `LLM_API_KEY` | - | AI provider API key |
| `LLM_BASE_URL` | - | AI provider base URL |
| `LLM_MODEL_NAME` | - | AI model identifier |

#### 🌍 Environment Variables

> **⚠️ Important**: Configure the following in your `.env` file (see `.env.example` for reference)

```ini
PROJECT_NAME="Telaten Backend"
API_V1_STR="/api/v1"
PORT=8000

# Database
DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/telaten_db"

# Security
SECRET_KEY="your-secret-key-here"
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# AI Providers (Choose one)
LLM_API_KEY="your-api-key-here"
LLM_BASE_URL="https://api.groq.com/openai/v1"  # or OpenAI, Together AI, etc.
LLM_MODEL_NAME="llama-3.1-70b-versatile"

# Logging
LOG_LEVEL="INFO"
ENV="development"

# CORS
FRONTEND_URL="http://localhost:3000"
```

---

### 🔐 Security (`security.py`)

> 🛡️ **Purpose**: Password encryption, token encoding, and authentication utilities

#### 🔑 Security Features

| **Feature** | **Technology** | **Description** |
|-------------|----------------|-----------------|
| **Password Hashing** | `bcrypt` via `passlib` | Secure password storage |
| **JWT Generation** | `python-jose` | Access + Refresh tokens |
| **Algorithm** | `HS256` | JWT signing algorithm |
| **Token Utilities** | Custom functions | Verification & payload decoding |

#### 🔒 Security Flow

```mermaid
sequenceDiagram
    participant User
    participant API
    participant Security
    participant DB
    
    User->>API: Login Request
    API->>Security: Verify Password
    Security->>DB: Check Hash
    DB-->>Security: Hash Match
    Security-->>API: Generate JWT
    API-->>User: Access + Refresh Tokens
```

---

### 🧠 MCP Client (`mcp_client.py`)

> 🔗 **Purpose**: Connectivity to external **Model Context Protocol (MCP)** servers

#### 🚀 MCP Capabilities

| **Capability** | **Description** |
|----------------|-----------------|
| **Transport Modes** | Supports **Stdio** and **SSE** transport |
| **Auto Discovery** | Automatically discovers and loads tools from configured endpoints |
| **Tool Wrapping** | Wraps MCP tools into `llama_index` **FunctionTool** objects |
| **Configuration** | Fully configurable through `mcp.json` |

---

## 🗄️ Database Layer

> 🏠 **Location**: `app/db/`  
> 🎯 **Purpose**: Database connectivity, schema initialization, and session lifecycle using **SQLModel** + **SQLAlchemy Async**

### 🔌 Session (`session.py`)

#### 🔧 Database Components

| **Component** | **Technology** | **Purpose** |
|---------------|----------------|-------------|
| **Engine** | Async SQLAlchemy + `asyncpg` | High-performance async database connections |
| **Session Provider** | `get_db` dependency | Yields `AsyncSession` for request lifecycle |
| **Initialization** | `init_db` function | Creates all tables from SQLModel metadata |

#### 🔄 Connection Flow

```mermaid
graph LR
    A[FastAPI Request] --> B[get_db Dependency]
    B --> C[AsyncSession]
    C --> D[Database Operations]
    D --> E[Auto Cleanup]
```

---

### 🌱 Initialization (`init_data.py`)

#### 🚀 Bootstrap Process

| **Step** | **Action** | **Purpose** |
|----------|------------|-------------|
| **1** | Create Admin User | Default: `admin@telaten.com` |
| **2** | Set Secure Password | Auto-generated on first startup |
| **3** | Initialize System Data | Seed business levels, categories, etc. |

> **🔐 Security Note**: Admin credentials are auto-generated and logged securely during first startup

---

## 📜 Logging & AI

### 📊 Logging (`logging.py`)

> **🎯 Features**: Structured, JSON-friendly logging with **structlog**

#### 🔧 Configuration Options

```python
# Environment Variables
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT=JSON # JSON or CONSOLE
```

---

### 🤖 LLM Factory (`llm.py`)

> **🎯 Purpose**: Centralized factory pattern for Large Language Model instantiation

#### 🔗 Supported Providers

| **Provider** | **Base URL Example** | **Notes** |
|--------------|---------------------|-----------|
| **OpenAI** | `https://api.openai.com/v1` | Official OpenAI API |
| **Groq** | `https://api.groq.com/openai/v1` | High-speed inference |
| **Together AI** | `https://api.together.xyz/v1` | Open-source models |
| **DeepSeek** | `https://api.deepseek.com/v1` | Cost-effective option |

#### ⚙️ Configuration Examples

**Groq (Recommended for Development):**
```ini
LLM_API_KEY="gsk_your_groq_api_key_here"
LLM_BASE_URL="https://api.groq.com/openai/v1"
LLM_MODEL_NAME="llama-3.1-70b-versatile"
```

**OpenAI:**
```ini
LLM_API_KEY="sk-your_openai_api_key_here"
LLM_BASE_URL="https://api.openai.com/v1"
LLM_MODEL_NAME="gpt-4"
```

**Together AI:**
```ini
LLM_API_KEY="your_together_api_key_here"
LLM_BASE_URL="https://api.together.xyz/v1"
LLM_MODEL_NAME="meta-llama/Llama-2-70b-chat-hf"
```

---

<div align="center">
  <p><em>🏗️ Infrastructure documentation complete - Ready for production!</em></p>
</div>
