# Clinical Trials Management API Documentation

## Overview

The Clinical Trials Management API provides comprehensive clinical trials management capabilities through **two complementary interfaces**:

1. **Structured Workflow Endpoints** (NEW) - Direct access to clinical workflows with frontend-optimized responses
2. **Agent System Interface** - Multi-agent orchestration powered by OpenAI Agents SDK

### **System Architecture**
- ✅ **Real OpenAI Agents SDK**: Using `agents` package (openai-agents==0.1.0)
- ✅ **26 Function Tools**: All using string-based signatures with JSON serialization
- ✅ **5 Specialized Agents**: Portfolio Manager, Query Analyzer, Data Verifier, Query Generator, Query Tracker
- ✅ **Structured Endpoints**: Frontend-optimized REST API for Query Management, SDV, and Deviation Detection
- ✅ **Pydantic Context Classes**: No dataclass or mock implementations
- ✅ **Full SDK Integration**: Agent coordination, handoffs, and state management

## Base URL
- **Development**: `http://localhost:8000`
- **Production**: `https://your-railway-app.railway.app`

---

# 🆕 Structured Workflow Endpoints

## Overview

The new structured endpoints provide direct access to clinical trial workflows with responses optimized for frontend consumption. These endpoints return consistent JSON structures for data tables, charts, and dashboard components.

### Available Workflows

1. **Query Management** (`/api/v1/queries/`) - Clinical data analysis and query generation
2. **Source Data Verification** (`/api/v1/sdv/`) - Cross-system data verification and audit trails
3. **Protocol Deviation Detection** (`/api/v1/deviations/`) - Automated compliance monitoring

### Response Format

All structured endpoints follow a consistent format:

```json
{
  "success": boolean,
  "response_type": "string", // workflow identifier
  "execution_time": number,  // seconds
  "agent_id": "string",     // responsible agent
  "raw_response": "string", // original agent output
  // ... workflow-specific fields
}
```

## Query Management Endpoints

### POST /api/v1/queries/analyze

Analyze clinical data for discrepancies and generate queries with medical intelligence.

**Request Body**:
```json
{
  "subject_id": "SUBJ001",
  "site_id": "SITE01", 
  "visit": "Week 12",
  "field_name": "hemoglobin",
  "field_value": "8.5",
  "expected_value": "12.0", // optional
  "form_name": "Laboratory Results",
  "page_number": 1, // optional
  "context": {
    "initials": "JD",
    "site_name": "Boston General"
  }
}
```

**Response**:
```json
{
  "success": true,
  "response_type": "clinical_analysis",
  "query_id": "Q-20250109-120000-SUBJ001",
  "created_date": "2025-01-09T12:00:00Z",
  "status": "pending",
  "severity": "critical",
  "category": "laboratory_value",
  "subject": {
    "id": "SUBJ001",
    "initials": "JD",
    "site": "Boston General",
    "site_id": "SITE01"
  },
  "clinical_context": {
    "visit": "Week 12",
    "field": "hemoglobin",
    "value": "8.5",
    "expected_value": "12.0",
    "form_name": "Laboratory Results"
  },
  "clinical_findings": [
    {
      "parameter": "hemoglobin",
      "value": "8.5",
      "interpretation": "Severe anemia",
      "normal_range": "12-16 g/dL",
      "severity": "critical",
      "clinical_significance": "Risk of tissue hypoxia"
    }
  ],
  "ai_analysis": {
    "interpretation": "Critical finding: Hemoglobin 8.5 g/dL indicates severe anemia",
    "clinical_significance": "high",
    "confidence_score": 0.95,
    "suggested_query": "URGENT: Please confirm hemoglobin value and evaluate for bleeding source",
    "recommendations": [
      "Immediate medical review",
      "Check for GI bleeding", 
      "Consider transfusion"
    ]
  },
  "execution_time": 1.2,
  "confidence_score": 0.95
}
```

### GET /api/v1/queries/

List queries with filtering and pagination.

**Query Parameters**:
- `skip` (integer, default: 0) - Pagination offset
- `limit` (integer, default: 100, max: 1000) - Number of records
- `severity` (array) - Filter by severity levels
- `status` (array) - Filter by query status
- `site_id` (string) - Filter by site
- `subject_id` (string) - Filter by subject
- `date_from` (ISO date) - Filter from date
- `date_to` (ISO date) - Filter to date

### GET /api/v1/queries/stats/dashboard

Get query statistics for dashboard display.

**Response**:
```json
{
  "total_queries": 234,
  "open_queries": 45,
  "critical_queries": 5,
  "major_queries": 23,
  "minor_queries": 17,
  "resolved_today": 12,
  "resolved_this_week": 78,
  "average_resolution_time": 24.5,
  "queries_by_site": {
    "SITE01": 15,
    "SITE02": 12,
    "SITE03": 8
  },
  "queries_by_category": {
    "laboratory_value": 20,
    "vital_signs": 15,
    "adverse_event": 8
  },
  "trend_data": [
    {"date": "2025-01-01", "queries": 8},
    {"date": "2025-01-02", "queries": 12}
  ]
}
```

## Source Data Verification (SDV) Endpoints

### POST /api/v1/sdv/verify

Verify source data against EDC data with discrepancy detection.

**Request Body**:
```json
{
  "subject_id": "SUBJ001",
  "site_id": "SITE01",
  "visit": "Week 12",
  "edc_data": {
    "hemoglobin": "12.5",
    "systolic_bp": "120",
    "diastolic_bp": "80"
  },
  "source_data": {
    "hemoglobin": "12.3",
    "systolic_bp": "125",
    "diastolic_bp": "80"
  },
  "monitor_id": "MON001",
  "context": {
    "initials": "JD",
    "site_name": "Boston General"
  }
}
```

**Response**:
```json
{
  "success": true,
  "response_type": "data_verification",
  "verification_id": "SDV-20250109-120000-SUBJ001",
  "site": "SITE01",
  "monitor": "MON001",
  "verification_date": "2025-01-09T12:00:00Z",
  "subject": {
    "id": "SUBJ001",
    "initials": "JD",
    "site": "Boston General",
    "site_id": "SITE01"
  },
  "visit": "Week 12",
  "match_score": 0.75,
  "matching_fields": ["diastolic_bp"],
  "discrepancies": [
    {
      "field": "hemoglobin",
      "field_label": "Hemoglobin",
      "edc_value": "12.5",
      "source_value": "12.3",
      "severity": "minor",
      "discrepancy_type": "value_mismatch",
      "confidence": 0.9
    }
  ],
  "total_fields_compared": 3,
  "progress": {
    "total_fields": 3,
    "verified": 1,
    "discrepancies": 2,
    "completion_rate": 0.75
  },
  "recommendations": [
    "Review hemoglobin discrepancy with medical monitor"
  ],
  "execution_time": 1.8
}
```

### GET /api/v1/sdv/stats/dashboard

Get SDV statistics for dashboard display.

**Response**:
```json
{
  "total_subjects": 75,
  "verified_subjects": 60,
  "total_data_points": 2250,
  "verified_data_points": 1800,
  "overall_completion": 0.8,
  "discrepancy_rate": 0.05,
  "sites_summary": [
    {
      "site_id": "SITE01",
      "completion_rate": 0.72,
      "discrepancy_rate": 0.06,
      "monitor": "Monitor A"
    }
  ],
  "high_risk_sites": ["SITE01"],
  "resource_utilization": {
    "monitor_a": 0.85,
    "monitor_b": 0.75
  }
}
```

## Protocol Deviation Detection Endpoints

### POST /api/v1/deviations/detect

Detect protocol deviations by comparing requirements to actual data.

**Request Body**:
```json
{
  "subject_id": "SUBJ001",
  "site_id": "SITE01",
  "visit": "Week 12",
  "protocol_data": {
    "required_visit_window": "±3 days",
    "required_fasting": "12 hours",
    "prohibited_medications": ["aspirin", "warfarin"]
  },
  "actual_data": {
    "visit_date": "2025-01-15",
    "scheduled_date": "2025-01-09",
    "fasting_hours": "8",
    "concomitant_medications": ["aspirin", "metformin"]
  },
  "monitor_id": "MON001",
  "context": {
    "initials": "JD",
    "site_name": "Boston General"
  }
}
```

**Response**:
```json
{
  "success": true,
  "response_type": "deviation_detection",
  "deviation_id": "DEV-20250109-120000-SUBJ001",
  "subject": {
    "id": "SUBJ001",
    "initials": "JD",
    "site": "Boston General",
    "site_id": "SITE01"
  },
  "site": "SITE01",
  "visit": "Week 12",
  "monitor": "MON001",
  "detection_date": "2025-01-09T12:00:00Z",
  "deviations": [
    {
      "category": "visit_window",
      "severity": "major",
      "protocol_requirement": "Visit within ±3 days",
      "actual_value": "6 days outside window",
      "impact_level": "medium",
      "corrective_action_required": true,
      "deviation_description": "Visit occurred 6 days outside protocol window",
      "confidence": 0.95
    },
    {
      "category": "prohibited_medication",
      "severity": "critical",
      "protocol_requirement": "No prohibited medications allowed",
      "actual_value": "Taking aspirin",
      "impact_level": "critical",
      "corrective_action_required": true,
      "deviation_description": "Subject taking prohibited medication: aspirin",
      "confidence": 0.98
    }
  ],
  "total_deviations_found": 2,
  "impact_assessment": "Critical impact: 1 critical deviation(s) detected",
  "recommendations": [
    "Immediate medical monitor notification required",
    "Consider subject discontinuation assessment"
  ],
  "corrective_actions_required": [
    "Review and update visit scheduling procedures",
    "Immediate medication review and discontinuation if necessary"
  ],
  "execution_time": 1.5
}
```

### GET /api/v1/deviations/stats/dashboard

Get deviation statistics for dashboard display.

**Response**:
```json
{
  "total_deviations": 42,
  "critical_deviations": 3,
  "major_deviations": 15,
  "minor_deviations": 24,
  "resolved_deviations": 35,
  "pending_deviations": 7,
  "deviations_by_site": {
    "SITE01": 18,
    "SITE02": 14,
    "SITE03": 10
  },
  "deviations_by_category": {
    "visit_window": 20,
    "fasting_requirement": 12,
    "prohibited_medication": 6
  },
  "deviation_trends": [
    {"date": "2025-01-01", "deviations": 5},
    {"date": "2025-01-02", "deviations": 8}
  ],
  "resolution_rate": 0.83,
  "average_resolution_time": 72.5
}
```

### Severity Classification

All endpoints use consistent severity levels:
- `critical` - Life-threatening findings, protocol violations (Hgb < 8.0, prohibited medications)
- `major` - Significant clinical concerns, major deviations (Hgb < 10.0, visit windows > 2x limit)
- `minor` - Minor deviations from normal, small discrepancies
- `info` - Informational findings, no action required

### Frontend Integration

Responses are optimized for common frontend components:

**Data Tables**: All list endpoints return arrays with consistent field structures
**Dashboard Widgets**: Statistics endpoints provide ready-to-use metrics
**Progress Bars**: Completion rates as 0-1 decimals for easy percentage calculation
**Charts**: Trend data with date/value pairs for direct chart library integration
**Notifications**: Critical findings include urgency indicators and recommendations

---

# 🤖 Multi-Agent System Interface

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