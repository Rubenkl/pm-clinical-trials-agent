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
│   │   ├── query_analyzer.py       # Clinical data analysis specialist
│   │   ├── data_verifier.py        # Cross-system verification specialist
│   │   ├── query_generator.py      # Clinical query generation specialist
│   │   ├── query_tracker.py        # Query lifecycle tracking specialist
│   │   └── handoff_registry.py     # Agent coordination registry
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
├── tests/               # Comprehensive test suite
│   ├── __init__.py
│   ├── test_sdk_integration.py     # Complete SDK integration tests
│   ├── test_data/                  # Clinical test datasets
│   │   └── clinical_test_datasets.py
│   ├── test_*_sdk.py               # Individual agent tests
│   └── conftest.py                 # Test configuration
├── requirements.txt     # Python dependencies
├── Dockerfile          # Railway deployment
├── railway.toml        # Railway configuration
└── main.py            # Application entry point
```

## Key Components

### Multi-Agent System (OpenAI Agents SDK)
The system uses the Portfolio Manager pattern with 5 specialized agents:

1. **Portfolio Manager**: Central orchestrator coordinating all workflow execution
2. **Query Analyzer**: Clinical data analysis and discrepancy detection with medical terminology
3. **Data Verifier**: Cross-system verification and Source Data Verification (SDV)
4. **Query Generator**: Clinical query generation with regulatory compliance
5. **Query Tracker**: Query lifecycle tracking, SLA monitoring, and escalation management

### Agent Function Tools Summary
- **Portfolio Manager**: 5 tools (workflow orchestration, planning, status tracking)
- **Query Analyzer**: 5 tools (data analysis, medical terminology, batch processing)
- **Data Verifier**: 6 tools (cross-system verification, SDV, audit trails)
- **Query Generator**: 5 tools (query generation, templates, compliance validation)
- **Query Tracker**: 5 tools (lifecycle tracking, SLA monitoring, escalation)

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
python3 -m venv venv
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
from agents import Agent, function_tool, Runner
from app.agents.portfolio_manager import PortfolioManager, WorkflowContext

# Initialize Portfolio Manager
pm = PortfolioManager()

# Example workflow orchestration
workflow_request = {
    "workflow_id": "WF_001",
    "workflow_type": "query_resolution", 
    "description": "Analyze clinical data discrepancies",
    "input_data": {
        "subject_id": "SUBJ001",
        "edc_data": {"hemoglobin": "12.5"},
        "source_data": {"hemoglobin": "11.2"}
    }
}

result = await pm.orchestrate_workflow(workflow_request)
```

### Agent Handoff Registry
```python
from app.agents.handoff_registry import clinical_trials_registry, execute_workflow

# Execute complete workflow with automatic agent handoffs
result = await execute_workflow(
    workflow_type="data_verification",
    input_data=clinical_data
)

# Get specific agents
portfolio_manager = clinical_trials_registry.get_portfolio_manager()
query_analyzer = clinical_trials_registry.get_query_analyzer() 
data_verifier = clinical_trials_registry.get_data_verifier()
```

### Context Management Examples
```python
# Portfolio Manager Context
class WorkflowContext(Context):
    active_workflows: List[Dict[str, Any]] = field(default_factory=list)
    completed_workflows: List[Dict[str, Any]] = field(default_factory=list)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)

# Query Analyzer Context  
class QueryAnalysisContext(Context):
    analysis_history: List[Dict[str, Any]] = field(default_factory=list)
    medical_terminology_cache: Dict[str, str] = field(default_factory=dict)
    confidence_threshold: float = 0.7

# Data Verifier Context
class DataVerificationContext(Context):
    verification_history: List[Dict[str, Any]] = field(default_factory=list)
    audit_trails: List[Dict[str, Any]] = field(default_factory=list)
    critical_findings: List[Dict[str, Any]] = field(default_factory=list)
```

## Dependencies (requirements.txt)
```
# FastAPI and ASGI
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
pydantic>=2.5.0
pydantic-settings>=2.1.0

# OpenAI Agents SDK (CORRECT PACKAGE NAME)
openai>=1.87.0
openai-agents>=0.1.0

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
pytest-mock==3.12.0

# Development Tools
black==23.11.0
isort==5.12.0
mypy==1.7.1

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

## Workflow Types & Agent Handoffs

The system supports three main workflow patterns with automatic agent handoffs:

### 1. Query Resolution Workflow
```
Portfolio Manager → Query Analyzer → Query Generator → Query Tracker
```
- Analyzes clinical data for discrepancies
- Generates appropriate clinical queries
- Tracks query lifecycle and resolution

### 2. Data Verification Workflow  
```
Portfolio Manager → Data Verifier → Query Generator → Query Tracker
```
- Cross-system data verification (EDC vs Source)
- Source Data Verification (SDV) processes
- Audit trail generation for regulatory compliance

### 3. Comprehensive Analysis Workflow
```
Portfolio Manager → Query Analyzer → Data Verifier → Query Generator → Query Tracker
```
- Complete clinical data analysis and verification
- Pattern detection across multiple data sources
- Full audit trail and query generation

### Handoff Rules
- **8 total handoff rules** defined between agents
- **Conditional handoffs** based on context and results
- **Context transfer** of relevant data between agents
- **Validation** of handoff sequences before execution

## Agent Performance Metrics

### Testing & Validation
- **Ground Truth Datasets**: Clinical test data with known expected results
- **Performance Thresholds**: Precision ≥ 0.85, Recall ≥ 0.80, F1-Score ≥ 0.82
- **Integration Tests**: 20+ comprehensive test scenarios
- **Concurrent Operations**: Support for parallel agent execution

### Regulatory Compliance Features
- **GCP Compliance**: Good Clinical Practice validation
- **FDA Readiness**: Audit trail generation
- **Medical Terminology**: Standardized medical term processing
- **Critical Field Detection**: Automatic identification of safety-critical data

## ✅ **WORKING OpenAI Agents SDK Implementation**

### **Correct Import Pattern**
```python
# CORRECT - Use 'agents' package (not 'openai_agents')
from agents import Agent, function_tool, Runner
from pydantic import BaseModel
```

### **Context Classes with Pydantic**
```python
# CORRECT - Use Pydantic BaseModel for context
class WorkflowContext(BaseModel):
    active_workflows: Dict[str, Any] = {}
    agent_states: Dict[str, Any] = {}
    performance_metrics: Dict[str, Any] = {}
```

### **Function Tools with String Signatures**
```python
# CORRECT - Use string inputs/outputs with JSON serialization
@function_tool
def orchestrate_workflow(workflow_request: str) -> str:
    """Orchestrate workflow with JSON string input/output."""
    import json
    try:
        request_data = json.loads(workflow_request)
        # Process request...
        result = {"success": True, "workflow_id": request_data.get("workflow_id")}
        return json.dumps(result)
    except json.JSONDecodeError:
        return json.dumps({"success": False, "error": "Invalid JSON"})
```

### **Complete Working System Statistics**
- ✅ **5 Specialized Agents**: All using real OpenAI Agents SDK
- ✅ **23 Function Tools**: String-based with JSON serialization
- ✅ **Pydantic Context Classes**: No dataclass mock implementations
- ✅ **Real SDK Integration**: No mock classes or fallback implementations
- ✅ **Full Test Coverage**: All agents tested with actual SDK patterns

### **Agent Details**
| Agent | Tools | Status | SDK Compliance |
|-------|-------|--------|----------------|
| Portfolio Manager | 5 | ✅ Working | Full SDK integration |
| Query Analyzer | 5 | ✅ Working | Full SDK integration |
| Data Verifier | 6 | ✅ Working | Full SDK integration |
| Query Generator | 3 | ✅ Working | Full SDK integration |
| Query Tracker | 4 | ✅ Working | Full SDK integration |

### **Key Implementation Insights**
1. **Package Name**: Use `openai-agents` (pip) but import as `agents`
2. **Function Tools**: Must use string signatures, not `Dict[str, Any]`
3. **Context**: Use Pydantic BaseModel, not dataclasses
4. **JSON Serialization**: Required for complex data in function tools
5. **No Mocks**: All agents use real OpenAI Agents SDK

This approach leverages the OpenAI Agents SDK's powerful built-in features while keeping our implementation focused on the actual business requirements rather than infrastructure complexity.