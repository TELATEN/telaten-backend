<div align="center">
  <h1>🚀 Telaten Backend</h1>
  <p><strong>AI-Powered Business Growth Platform Backend</strong></p>
  <p><em>Diligent perseverance through intelligent automation</em></p>

  <!-- Tech Stack Badges -->
  <p>
    <img src="https://img.shields.io/badge/Python-3.12+-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
    <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI"/>
    <img src="https://img.shields.io/badge/PostgreSQL-336791?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL"/>
    <img src="https://img.shields.io/badge/LlamaIndex-FF6B35?style=for-the-badge" alt="LlamaIndex"/>
  </p>

  <!-- Status Badges -->
  <p>
    <img src="https://img.shields.io/badge/Status-Production%20Ready-success?style=for-the-badge" alt="Status"/>
    <img src="https://img.shields.io/badge/API%20Docs-Swagger-85EA2D?style=for-the-badge&logo=swagger&logoColor=white" alt="API Docs"/>
    <img src="https://img.shields.io/badge/Real--time-SSE-FF4081?style=for-the-badge" alt="Real-time"/>
  </p>
</div>

---

## 🌟 About Telaten

**Telaten** (from Javanese, meaning *"diligent"* or *"patient perseverance"*) is an AI-powered backend system crafted to support Indonesian MSMEs (UMKM) on their business journey. It blends **Gamification**, **Financial Tracking**, and **AI-driven Business Roadmaps** into a unified, empowering business companion.

---

## 📚 Documentation Hub

| 📂 **Category** | 📄 **Document** | 🎯 **Purpose** |
|----------------|-----------------|----------------|
| 🏗️ **Architecture** | [Infrastructure](docs/INFRASTRUCTURE.md) | Core configuration, security, MCP integration |
| 🤖 **AI & Workflows** | [Agent & Main](docs/AGENT_MAIN.md) | AI workflows, tools, and MCP server setup |
| 👤 **User Management** | [Auth & Business](docs/AUTH_BUSINESS.md) | Authentication, business profiles, levels |
| 💰 **Business Logic** | [Finance & Milestone](docs/FINANCE_MILESTONE.md) | Financial tracking and milestone management |
| 🎮 **Engagement** | [Gamification & Chat](docs/GAMIFICATION_CHAT.md) | Achievements, leaderboard, AI chat system |
| 🌐 **API Reference** | [Bruno Collection](../telaten-docs-api/) | Interactive API testing and documentation |
| 🗄️ **Database** | [ERD Diagram](docs/ERD.md) | Complete database schema and relationships |

## 🌟 Key Features

### 🤖 **AI Business Advisor**
- **Context-Aware Intelligence**: Proactive agent ("Telaten Advisor") functioning like a business GPS
- **Smart Guidance**: Monitors progress, generates tasks, and guides owners through each milestone
- **Real-time Support**: Live chat with business intelligence and tool integration

### 🗺️ **Adaptive Roadmaps** 
- **AI-Generated Milestones**: Automatically created business goals tailored to your industry and stage
- **Dynamic Evolution**: Roadmaps that adapt based on completion history and business growth
- **Progressive Difficulty**: Task complexity scales with business maturity

### 💰 **Financial Tracking Made Simple**
- **Intuitive Recording**: Easy income/expense tracking with smart categorization
- **Automated Analytics**: Real-time summaries and insights for better decision making
- **Gamified Rewards**: Earn points for consistent financial tracking (+5 points per transaction)

### 🏆 **Gamification Layer**
- **Progress System**: Earn points, unlock achievements, and advance through business levels
- **Competitive Element**: Rise through leaderboards by staying diligent and consistent
- **Achievement Badges**: Visual recognition for reaching milestones and maintaining habits

### 🔌 **MCP-Powered Integration**
- **Protocol Standard**: Built using **Model Context Protocol (MCP)** for extensibility
- **Tool Ecosystem**: Seamless interaction between AI agents, internal tools, and external services
- **Future-Ready**: Easy integration with new AI tools and services

---

## 🏗️ System Architecture

```mermaid
graph TB
    subgraph "🎯 API Layer"
        API[FastAPI Application]
        MCP[MCP Server]
    end
    
    subgraph "🧠 AI Layer"
        AGENT[AI Agents]
        TOOLS[Agent Tools]
        WORKFLOWS[LlamaIndex Workflows]
    end
    
    subgraph "💼 Business Layer"
        AUTH[Authentication]
        BIZ[Business Logic]
        GAMIFY[Gamification]
    end
    
    subgraph "🗄️ Data Layer"
        DB[(PostgreSQL)]
        MODELS[SQLModel ORM]
    end
    
    API --> AUTH
    API --> BIZ
    API --> GAMIFY
    API --> MCP
    MCP --> AGENT
    AGENT --> WORKFLOWS
    WORKFLOWS --> TOOLS
    TOOLS --> BIZ
    BIZ --> MODELS
    MODELS --> DB
```

### 🗂️ Project Structure

| **Directory** | **Purpose** | **Key Components** |
|---------------|-------------|-------------------|
| `app/core/` | Core infrastructure | Configuration, security, MCP client |
| `app/db/` | Database layer | Initialization, sessions, seeding |
| `app/modules/` | Business domains | Modular feature implementation |
| `app/main.py` | Application entry | Router aggregation, lifespan events |
| `app/mcp_server.py` | MCP integration | Tool exposure for external access |

#### 🧩 **Module Breakdown**

| **Module** | **Responsibility** | **Key Features** |
|------------|-------------------|------------------|
| `agent/` | AI workflows & tools | Milestone generation, business advisory |
| `auth/` | Authentication & authorization | JWT tokens, user management |
| `business/` | Business profile management | Company data, levels, AI context |
| `chat/` | Conversational AI | Session management, SSE streaming |
| `finance/` | Financial operations | Transaction tracking, analytics |
| `gamification/` | Engagement system | Points, achievements, leaderboards |
| `milestone/` | Goal management | Task tracking, progress monitoring |

### 🛠️ **Technology Stack**

| **Layer** | **Technology** | **Purpose** | **Version** |
|-----------|----------------|-------------|-------------|
| **Framework** | FastAPI | High-performance async API | Latest |
| **Database** | PostgreSQL + SQLModel | Type-safe ORM with async support | 14+ |
| **AI/ML** | LlamaIndex + MCP | Agent workflows and tool integration | Latest |
| **Authentication** | JWT + bcrypt | Secure user management | - |
| **Real-time** | Server-Sent Events | Live updates and streaming | - |
| **Deployment** | Docker + uv | Containerization and dependency management | - |

---

## 🚀 Getting Started

### 📋 Prerequisites

| **Component** | **Version** | **Installation** |
|---------------|-------------|------------------|
| **Python** | ≥ 3.12 | [Download Python](https://python.org/downloads/) |
| **PostgreSQL** | ≥ 14.0 | [Download PostgreSQL](https://postgresql.org/download/) |
| **uv** | Latest | `pip install uv` |

### ⚙️ Environment Setup

**1️⃣ Clone and Navigate**
```bash
git clone <repository-url>
cd telaten-backend
```

**2️⃣ Environment Configuration**
```bash
# Copy environment template
cp .env.example .env
```

**📝 Configure Environment Variables:**
```ini
# Database Configuration
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/telaten_db

# Security
SECRET_KEY=your-super-secret-jwt-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# AI Provider (Choose one)
LLM_API_KEY=your-api-key-here
LLM_BASE_URL=https://api.groq.com/openai/v1
LLM_MODEL_NAME=llama-3.1-70b-versatile

# Application
LOG_LEVEL=INFO
ENV=development
FRONTEND_URL=http://localhost:3000
```

### 🔧 Installation & Running

**3️⃣ Install Dependencies**

| **Method** | **Command** | **Recommended For** |
|------------|-------------|---------------------|
| **uv** ⭐ | `uv sync` | Development (fastest) |
| **pip** | `pip install -e .` | Production/traditional |

**4️⃣ Database Setup**
```bash
# Ensure PostgreSQL is running
# The app will automatically create tables on first run
# Default admin user will be created: admin@telaten.com
```

**5️⃣ Start Development Server**

| **Method** | **Command** | **URL** |
|------------|-------------|---------|
| **uv** ⭐ | `uv run python run.py` | http://localhost:8000 |
| **python** | `python run.py` | http://localhost:8000 |

### 🌐 Access Points

| **Service** | **URL** | **Description** |
|-------------|---------|-----------------|
| **API Docs** | http://localhost:8000/docs | Interactive Swagger UI |
| **ReDoc** | http://localhost:8000/redoc | Alternative API documentation |
| **MCP Server** | http://localhost:8000/mcp/sse | MCP tool access endpoint |
| **Health Check** | http://localhost:8000/health | Service status endpoint |

---

## 🐳 Docker Deployment

### 🚀 Quick Start with Docker

```bash
# Start with Docker Compose
docker-compose up --build

# Or run in background
docker-compose up -d --build
```

### 🔧 Docker Services

| **Service** | **Port** | **Description** |
|-------------|----------|-----------------|
| **Backend** | `8000` | FastAPI application |
| **PostgreSQL** | `5432` | Database service |
| **Adminer** | `8080` | Database admin interface |

### 🐳 Manual Docker Commands

```bash
# Build image
docker build -t telaten-backend .

# Run with environment file
docker run --env-file .env -p 8000:8000 telaten-backend

# Run with database
docker run -d --name postgres-db \
  -e POSTGRES_DB=telaten_db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 postgres:15
```

---

## 🧪 Development

### 🔍 **Code Quality**
```bash
# Type checking
mypy .

# Linting
ruff check .

# Formatting
ruff format .
```

### 🧪 **Testing**
```bash
# Run tests
pytest

# Coverage report
pytest --cov=app tests/
```

### 📊 **Monitoring**
```bash
# View logs
docker-compose logs -f backend

# Database logs
docker-compose logs -f postgres
```

---

## 🤝 Contributing

### 🔄 **Development Workflow**

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/amazing-feature`
3. **Make changes** with proper documentation
4. **Run tests**: `pytest`
5. **Submit pull request**

### 📝 **Code Standards**

- **Type Hints**: Use Python type hints for all functions
- **Docstrings**: Document all public functions and classes
- **Testing**: Write tests for new features
- **Commit Style**: Use conventional commits (`feat:`, `fix:`, `docs:`)

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

<div align="center">
  <h3>🌟 Built with ❤️ for Indonesian MSMEs</h3>
  <p><strong>Empowering businesses through diligent perseverance and intelligent automation</strong></p>
  
  <p>
    <strong>🚀 One step at a time • 🎯 One milestone at a time • 💪 One success at a time</strong>
  </p>
</div>
