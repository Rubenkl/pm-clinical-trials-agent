# Clinical Trials Agent API Documentation

## Overview

The Clinical Trials Agent API provides a lightweight FastAPI wrapper around the **OpenAI Agents SDK** multi-agent system. The API enables interaction with **5 specialized clinical trials agents** powered by the real OpenAI Agents SDK (not mock implementations).

### **System Architecture**
- ✅ **Real OpenAI Agents SDK**: Using `agents` package (openai-agents==0.1.0)
- ✅ **23 Function Tools**: All using string-based signatures with JSON serialization
- ✅ **5 Specialized Agents**: Portfolio Manager, Query Analyzer, Data Verifier, Query Generator, Query Tracker
- ✅ **Pydantic Context Classes**: No dataclass or mock implementations
- ✅ **Full SDK Integration**: Agent coordination, handoffs, and state management

## Base URL
- **Development**: `http://localhost:8000`
- **Production**: `https://your-railway-app.railway.app`

## Authentication

Currently, the API uses API key authentication:

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     https://your-api-endpoint.com/api/v1/agents/chat
```

## Core Endpoints

### 1. Agent Chat Interface

Execute workflows through the Portfolio Manager agent which orchestrates all other specialized agents.

**Endpoint**: `POST /api/v1/agents/chat`

**Request Body**:
```json
{
  "message": "Analyze this clinical data for discrepancies",
  "workflow_type": "query_resolution", 
  "input_data": {
    "subject_id": "SUBJ001",
    "visit": "Week 4",
    "site_name": "Memorial Hospital",
    "edc_data": {
      "hemoglobin": "12.5",
      "weight": "75.0",
      "blood_pressure_systolic": "140",
      "adverse_events": [
        {
          "term": "Headache",
          "severity": "mild", 
          "start_date": "2024-12-15"
        }
      ]
    },
    "source_data": {
      "hemoglobin": "11.2",
      "weight": "75.0",
      "blood_pressure_systolic": "135",
      "adverse_events": [
        {
          "term": "Headache",
          "severity": "mild",
          "start_date": "2024-12-15"
        }
      ]
    }
  }
}
```

**Response**:
```json
{
  "success": true,
  "workflow_id": "WF_20241215_001",
  "status": "completed",
  "execution_plan": {
    "total_steps": 4,
    "completed_steps": 4,
    "current_agent": "Portfolio Manager",
    "next_steps": []
  },
  "results": {
    "discrepancies_found": 1,
    "queries_generated": 1,
    "critical_findings": 0,
    "analysis_summary": "Found 1 discrepancy in hemoglobin values requiring clinical review"
  },
  "handoff_history": [
    {
      "from_agent": "portfolio_manager",
      "to_agent": "query_analyzer", 
      "timestamp": "2024-12-15T10:30:00Z",
      "context_transferred": ["data_points", "trial_metadata"]
    },
    {
      "from_agent": "query_analyzer",
      "to_agent": "query_generator",
      "timestamp": "2024-12-15T10:30:15Z", 
      "context_transferred": ["analysis_results", "discrepancy_details"]
    }
  ],
  "processing_time_ms": 2340
}
```

**Workflow Types**:
- `query_resolution`: Analyze data → Generate queries → Track lifecycle
- `data_verification`: Verify data cross-system → Generate queries → Track
- `comprehensive_analysis`: Full analysis + verification + query generation

### 2. Agent System Status

Get current status of all agents in the system.

**Endpoint**: `GET /api/v1/agents/status`

**Response**:
```json
{
  "system_status": "healthy",
  "agents": {
    "portfolio_manager": {
      "status": "active",
      "active_workflows": 2,
      "completed_workflows": 15,
      "performance_metrics": {
        "avg_execution_time_ms": 1240,
        "success_rate": 0.98
      }
    },
    "query_analyzer": {
      "status": "active", 
      "analysis_performed": 45,
      "confidence_threshold": 0.7,
      "medical_terminology_cache_size": 120
    },
    "data_verifier": {
      "status": "active",
      "verifications_completed": 32,
      "critical_findings": 3,
      "audit_trails_generated": 28
    },
    "query_generator": {
      "status": "active",
      "queries_generated": 18,
      "templates_used": 5,
      "compliance_checks_passed": 18
    },
    "query_tracker": {
      "status": "active",
      "active_queries": 8,
      "completed_queries": 12,
      "escalations": 1
    }
  },
  "handoff_registry": {
    "total_handoff_rules": 8,
    "successful_handoffs": 42,
    "failed_handoffs": 0
  }
}
```

### 3. Reset Agent Context

Reset all agent contexts and clear accumulated state.

**Endpoint**: `POST /api/v1/agents/reset`

**Request Body**:
```json
{
  "reset_type": "soft", // "soft" | "hard" | "selective"
  "agents": ["portfolio_manager", "query_analyzer"], // Optional: specific agents
  "preserve_metrics": true // Optional: keep performance metrics
}
```

**Response**:
```json
{
  "success": true,
  "reset_agents": [
    "portfolio_manager",
    "query_analyzer", 
    "data_verifier",
    "query_generator",
    "query_tracker"
  ],
  "contexts_cleared": 5,
  "metrics_preserved": true,
  "timestamp": "2024-12-15T10:45:00Z"
}
```

### 4. Workflow Execution

Execute specific workflows with detailed control.

**Endpoint**: `POST /api/v1/workflows/execute`

**Request Body**:
```json
{
  "workflow_id": "WF_CUSTOM_001",
  "workflow_type": "data_verification",
  "description": "Custom verification workflow",
  "input_data": {
    "subjects": ["SUBJ001", "SUBJ002"],
    "verification_scope": "critical_fields_only",
    "edc_data": { /* ... */ },
    "source_data": { /* ... */ }
  },
  "execution_options": {
    "parallel_processing": true,
    "generate_audit_trail": true,
    "confidence_threshold": 0.85
  }
}
```

**Response**:
```json
{
  "workflow_id": "WF_CUSTOM_001",
  "status": "in_progress",
  "estimated_completion": "2024-12-15T10:50:00Z",
  "progress": {
    "current_step": 2,
    "total_steps": 4,
    "current_agent": "data_verifier",
    "completion_percentage": 50
  },
  "intermediate_results": {
    "subjects_processed": 1,
    "discrepancies_found": 2,
    "critical_findings": 0
  }
}
```

### 5. Query Management

Manage generated clinical queries through their lifecycle.

**Endpoint**: `GET /api/v1/queries`

**Query Parameters**:
- `status`: `open` | `resolved` | `escalated` | `all`
- `priority`: `critical` | `major` | `minor` | `info`
- `site`: Site identifier
- `subject`: Subject identifier

**Response**:
```json
{
  "queries": [
    {
      "query_id": "Q_20241215_001",
      "subject_id": "SUBJ001",
      "site_name": "Memorial Hospital",
      "status": "open",
      "priority": "major",
      "query_type": "data_discrepancy",
      "description": "Hemoglobin value discrepancy between EDC (12.5) and source (11.2)",
      "generated_timestamp": "2024-12-15T10:30:00Z",
      "due_date": "2024-12-18T10:30:00Z",
      "assigned_to": "site_coordinator",
      "escalation_level": 0,
      "resolution_required": true
    }
  ],
  "total_count": 1,
  "pagination": {
    "page": 1,
    "limit": 50,
    "total_pages": 1
  }
}
```

**Endpoint**: `PUT /api/v1/queries/{query_id}`

Update query status and resolution:

```json
{
  "status": "resolved",
  "resolution": "Source document updated to match EDC value",
  "resolved_by": "site_coordinator",
  "resolution_timestamp": "2024-12-15T14:30:00Z"
}
```

## Health Check

**Endpoint**: `GET /health`

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2024-12-15T10:45:00Z",
  "version": "1.0.0",
  "uptime_seconds": 3600,
  "agents_initialized": 5,
  "openai_sdk_version": "0.1.0"
}
```

## Error Responses

All endpoints return consistent error responses:

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid workflow type specified",
    "details": {
      "field": "workflow_type",
      "allowed_values": ["query_resolution", "data_verification", "comprehensive_analysis"]
    }
  },
  "timestamp": "2024-12-15T10:45:00Z"
}
```

**Common Error Codes**:
- `VALIDATION_ERROR`: Request validation failed
- `AGENT_ERROR`: Agent processing error
- `WORKFLOW_ERROR`: Workflow execution error
- `TIMEOUT_ERROR`: Request timeout exceeded
- `RATE_LIMIT_ERROR`: Rate limit exceeded

## Rate Limits

- **Chat Endpoint**: 60 requests per minute
- **Status Endpoint**: 120 requests per minute  
- **Reset Endpoint**: 10 requests per minute
- **Query Endpoints**: 100 requests per minute

## SDK Integration Examples

### Python Client
```python
import httpx
import asyncio

# Example: Using the real OpenAI Agents SDK through the API
async def analyze_clinical_data():
    clinical_data = {
        "subject_id": "SUBJ001",
        "edc_data": {"hemoglobin": "12.5", "weight": "75.0"},
        "source_data": {"hemoglobin": "11.2", "weight": "75.0"}
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/v1/agents/chat",
            json={
                "message": "Analyze clinical data for discrepancies",
                "workflow_type": "comprehensive_analysis",  # Uses all 5 agents
                "input_data": clinical_data
            },
            headers={"Authorization": "Bearer YOUR_API_KEY"}
        )
        return response.json()

# This executes through the real OpenAI Agents SDK with:
# Portfolio Manager (5 tools) → Query Analyzer (5 tools) → 
# Data Verifier (6 tools) → Query Generator (3 tools) → Query Tracker (4 tools)
result = asyncio.run(analyze_clinical_data())
```

### JavaScript Client
```javascript
const response = await fetch('/api/v1/agents/chat', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer YOUR_API_KEY'
  },
  body: JSON.stringify({
    message: 'Analyze clinical data',
    workflow_type: 'query_resolution',
    input_data: clinicalData
  })
});

const result = await response.json();
```

## OpenAPI/Swagger Documentation

Interactive API documentation is available at:
- **Development**: `http://localhost:8000/docs`
- **Production**: `https://your-railway-app.railway.app/docs`

## Support

For API support, integration questions, or bug reports:
1. Check the interactive documentation at `/docs`
2. Review agent-specific documentation in `backend/CLAUDE.md`
3. Create an issue in the project repository