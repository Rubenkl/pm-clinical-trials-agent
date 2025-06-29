# Backend - FastAPI with OpenAI Multi-Agent Orchestrator

## ⚠️ IMPORTANT: Before Starting Backend Work
1. **Review Project Plans**: Check `/product-management/roadmaps/` for:
   - `backend-development-tasks.md` - Comprehensive task list with priorities
   - `sprint-execution-plan.md` - Current sprint goals and what to work on
   - `master-implementation-plan-2025.md` - Overall timeline and dependencies

2. **Current Sprint Focus**: Always align work with the current sprint objectives

3. **Task Priority**: Follow the priority matrix:
   - Critical Path (Must Complete First)
   - High Priority (Core Functionality)
   - Medium Priority (Enhanced Features)
   - Lower Priority (Nice to Have)

## Overview
The backend is built with FastAPI and implements an OpenAI multi-agent orchestrator system for clinical trials management. It provides a RESTful API wrapper around the agent system.

## Architecture

### Tech Stack
- **Framework**: FastAPI
- **AI Agents**: OpenAI SDK with multi-agent orchestrator
- **Server**: Hypercorn (for Railway deployment)
- **Database**: PostgreSQL (Railway managed)
- **Deployment**: Railway with Docker

### Directory Structure

```
backend/
├── app/
│   ├── agents/          # OpenAI multi-agent orchestrator
│   │   ├── __init__.py
│   │   ├── orchestrator.py    # Main orchestrator logic
│   │   ├── clinical_agent.py  # Clinical trials specialist
│   │   ├── data_agent.py      # Data analysis agent
│   │   └── workflow_agent.py  # Workflow management agent
│   ├── api/             # FastAPI routes
│   │   ├── __init__.py
│   │   ├── endpoints/
│   │   │   ├── agents.py      # Agent interaction endpoints
│   │   │   ├── trials.py      # Clinical trial endpoints
│   │   │   └── health.py      # Health check endpoints
│   │   └── dependencies.py    # API dependencies
│   ├── core/            # Core configurations
│   │   ├── __init__.py
│   │   ├── config.py          # Application configuration
│   │   ├── security.py        # Authentication/authorization
│   │   └── database.py        # Database connection
│   └── models/          # Data models
│       ├── __init__.py
│       ├── agent_models.py    # Agent request/response models
│       └── trial_models.py    # Clinical trial models
├── tests/               # Backend tests
│   ├── __init__.py
│   ├── test_agents.py
│   ├── test_api.py
│   └── conftest.py
├── requirements.txt     # Python dependencies
├── Dockerfile          # Railway deployment
├── railway.toml        # Railway configuration
└── main.py            # Application entry point
```

## Key Components

### Multi-Agent Orchestrator
The system uses multiple specialized AI agents:

1. **Clinical Agent**: Handles clinical trial protocols, regulations, and medical terminology
2. **Data Agent**: Manages data analysis, statistics, and reporting
3. **Workflow Agent**: Coordinates project management and task orchestration

### FastAPI Structure
- **Endpoints**: RESTful API routes for agent interactions
- **Models**: Pydantic models for request/response validation
- **Dependencies**: Shared dependencies like database connections
- **Middleware**: CORS, authentication, logging

## Development Setup

### Local Development
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Environment Variables
```bash
# Required
OPENAI_API_KEY=your_openai_api_key
DATABASE_URL=postgresql://user:pass@localhost/dbname

# Optional
PORT=8000
DEBUG=true
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
```

## API Documentation

### Agent Endpoints
- `POST /api/v1/agents/chat` - Chat with agent orchestrator
- `GET /api/v1/agents/status` - Get agent system status
- `POST /api/v1/agents/reset` - Reset agent conversation

### Trial Management
- `GET /api/v1/trials/` - List clinical trials
- `POST /api/v1/trials/` - Create new trial
- `GET /api/v1/trials/{id}` - Get trial details
- `PUT /api/v1/trials/{id}` - Update trial
- `DELETE /api/v1/trials/{id}` - Delete trial

### Health Check
- `GET /health` - Application health status
- `GET /health/db` - Database connection status

## Railway Deployment

### Dockerfile Configuration
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE $PORT
CMD ["hypercorn", "app.main:app", "--bind", "0.0.0.0:$PORT"]
```

### Railway Configuration (railway.toml)
```toml
[build]
builder = "DOCKERFILE"

[deploy]
startCommand = "hypercorn app.main:app --bind 0.0.0.0:$PORT"
healthcheckPath = "/health"
healthcheckTimeout = 100
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10
```

## Dependencies (requirements.txt)
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
hypercorn==0.15.0
openai==1.3.5
pydantic==2.5.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
python-dotenv==1.0.0
python-multipart==0.0.6
```

## Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_agents.py -v
```

## Agent Integration Patterns

### Request/Response Flow
1. Frontend sends request to FastAPI endpoint
2. API validates request using Pydantic models
3. Request routed to appropriate agent via orchestrator
4. Agent processes request using OpenAI API
5. Response formatted and returned to frontend

### Error Handling
- Comprehensive error handling for API failures
- Graceful degradation when agents are unavailable
- Proper HTTP status codes and error messages
- Logging for debugging and monitoring