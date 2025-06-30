# Backend - FastAPI with OpenAI Agents SDK

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
The backend leverages the **OpenAI Agents SDK** for multi-agent orchestration with FastAPI as a lightweight API wrapper. The SDK provides built-in agent communication, state management, and orchestration patterns - eliminating the need for complex database models or custom agent frameworks.

## 🧪 Agent Testing & Evaluation Strategy

### Agent Architecture Philosophy
Our agents are **prompt-based LLM systems**, not trained models. This means:
- **Core Logic**: Carefully crafted prompts that define agent behavior
- **Intelligence**: Leveraged from base LLM (GPT-4) capabilities  
- **Specialization**: Domain-specific prompts and response parsing
- **Validation**: Ground truth datasets to measure performance

### Testing Approach
1. **Unit Tests**: Test agent structure, configuration, and non-LLM logic
2. **Integration Tests**: Test agent coordination and handoffs (mocked responses)
3. **Performance Tests**: Test agents against ground truth datasets (requires OpenAI API)
4. **Evaluation Metrics**: Precision, recall, F1-score, accuracy for each agent capability

### Ground Truth Test Datasets
Located in `/tests/test_data/clinical_test_datasets.py`:
- **Discrepancy Detection**: 6 test cases with known EDC vs source document differences
- **Critical Data Identification**: 3 test cases with safety-critical scenarios
- **Pattern Detection**: Site-specific and temporal pattern scenarios
- **Performance Metrics**: Automated calculation of precision/recall/F1/accuracy

### Agent Performance Validation
```python
# Example evaluation approach
test_dataset = get_test_dataset("DISCREPANCY_001")
result = await data_verifier.cross_system_verification(
    test_dataset["edc_data"], 
    test_dataset["source_data"]
)
metrics = calculate_performance_metrics(
    result.discrepancies, 
    test_dataset["expected_discrepancies"]
)
assert metrics["precision"] >= 0.85  # Performance threshold
```

## Architecture

### Tech Stack
- **AI Orchestration**: OpenAI Agents SDK (handles all agent coordination)
- **API Framework**: FastAPI (lightweight wrapper for HTTP endpoints)
- **State Management**: SDK Context objects (in-memory with optional persistence)
- **Storage**: Simple PostgreSQL (only if persistence needed)
- **Server**: Hypercorn (for Railway deployment)
- **Deployment**: Railway with Docker

### OpenAI Agents SDK Features (Built-in)
✅ **Agent-to-Agent Communication**: Via "Handoffs" - agents delegate to specialized sub-agents
✅ **State Management**: Via "Context" objects - dependency injection for shared state
✅ **Multi-Agent Orchestration**: LLM-driven and code-driven patterns
✅ **Portfolio Manager Pattern**: Central agent coordinating specialists
✅ **Built-in Tracing**: Workflow visualization and debugging
✅ **Parallel Execution**: Agents run tools/sub-agents concurrently

### Directory Structure

```
backend/
├── app/
│   ├── agents/          # OpenAI Agents SDK implementation
│   │   ├── __init__.py
│   │   ├── portfolio_manager.py    # Central orchestrator agent
│   │   ├── query_analyzer.py       # Query analysis specialist
│   │   ├── data_verifier.py        # Data verification specialist
│   │   ├── context.py              # Shared context/state management
│   │   └── handoffs.py             # Agent handoff definitions
│   ├── api/             # FastAPI routes (lightweight wrapper)
│   │   ├── __init__.py
│   │   ├── endpoints/
│   │   │   ├── agents.py           # Agent interaction endpoints
│   │   │   └── health.py           # Health check endpoints
│   │   ├── models/                 # Pydantic request/response models
│   │   └── dependencies.py         # API dependencies
│   ├── core/            # Core configurations
│   │   ├── __init__.py
│   │   └── config.py               # Application configuration
│   └── services/        # Optional services (if needed)
├── tests/               # Backend tests
│   ├── __init__.py
│   ├── test_agents.py              # Agent orchestration tests
│   ├── test_api.py                 # FastAPI endpoint tests
│   └── conftest.py
├── requirements.txt     # Python dependencies
├── Dockerfile          # Railway deployment
├── railway.toml        # Railway configuration
└── main.py            # Application entry point
```

## Key Components

### Multi-Agent System (OpenAI Agents SDK)
The system uses the Portfolio Manager pattern with specialized agents:

1. **Portfolio Manager**: Central orchestrator that coordinates all other agents
2. **Query Analyzer**: Analyzes and interprets user queries
3. **Data Verifier**: Validates and verifies data integrity
4. **Additional Specialists**: As needed for specific domains

### SDK-Based Orchestration Patterns
- **Handoffs**: Agents delegate specific tasks to specialized sub-agents
- **Context Sharing**: Shared state flows between agents via Context objects
- **Parallel Execution**: Multiple agents can work concurrently
- **Code-driven Flow**: Deterministic workflows using Python control structures

### FastAPI Wrapper
- **Minimal Endpoints**: Simple HTTP interface to the agent system
- **Pydantic Models**: Request/response validation
- **Health Checks**: System status monitoring
- **No Complex Database**: State managed by SDK Context objects

## Development Setup

### Installation
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Environment Variables
```bash
# Required
OPENAI_API_KEY=your_openai_api_key

# Optional
PORT=8000
DEBUG=true
CORS_ORIGINS=http://localhost:3000
```

### Running Locally
```bash
uvicorn app.main:app --reload --port 8000
```

## API Documentation

### Agent Endpoints
- `POST /api/v1/agents/chat` - Chat with Portfolio Manager (orchestrates other agents)
- `GET /api/v1/agents/status` - Get agent system status
- `POST /api/v1/agents/reset` - Reset agent context/state

### Health Check
- `GET /health` - Application health status

## Agent Implementation Example

### Portfolio Manager Agent
```python
from openai_agents import Agent, Runner
from app.agents.context import WorkflowContext
from app.agents.handoffs import query_analyzer_handoff, data_verifier_handoff

portfolio_manager = Agent(
    name="Portfolio Manager",
    instructions="You coordinate specialized agents to fulfill user requests.",
    handoffs=[query_analyzer_handoff, data_verifier_handoff]
)

# Usage
context = WorkflowContext(user_request="Analyze this data")
result = Runner.run_sync(portfolio_manager, "Analyze user query", context=context)
```

### Context Management
```python
class WorkflowContext:
    def __init__(self):
        self.user_request = ""
        self.analysis_results = {}
        self.verification_status = ""
        self.workflow_state = "pending"
```

## Dependencies (requirements.txt)
```
# FastAPI and ASGI
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
pydantic-settings==2.1.0

# OpenAI Agents SDK
openai>=1.87.0
openai-agents>=0.1.0

# Simple PostgreSQL (only if persistent storage needed)
psycopg2-binary==2.9.9

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0

# Utilities
python-dotenv==1.0.0
```

## Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run agent tests specifically
pytest tests/test_agents.py -v
```

## Key Benefits of This Approach

### ✅ What We Get for Free (SDK Built-in):
- Agent orchestration and communication
- State management via Context objects
- Built-in tracing and debugging
- Parallel agent execution
- Handoff patterns for delegation

### ✅ What We Focus On:
- Business logic in agent instructions
- FastAPI endpoint design
- Request/response models
- Agent specialization and coordination

### ❌ What We DON'T Need:
- Complex database models/ORM
- Custom agent communication protocols
- Manual state management systems
- Custom orchestration frameworks

This approach leverages the OpenAI Agents SDK's powerful built-in features while keeping our implementation focused on the actual business requirements rather than infrastructure complexity.