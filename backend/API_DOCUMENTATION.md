# Clinical Trials Agent API Documentation

## Overview
The Clinical Trials Agent API provides AI-powered clinical data analysis through a clean set of workflow-focused endpoints. All agent interactions use the OpenAI Agents SDK with direct `Runner.run()` invocation.

## ⭐ **Agent Output Schemas**
For complete standardized output documentation for all agents, see:
**[Agent Output Schemas Reference](./AGENT_OUTPUT_SCHEMAS.md)**

This comprehensive document contains:
- Exact JSON schemas for all 7 agents
- TypeScript interface definitions  
- Realistic example responses
- Field types and constraints
- Error handling patterns

## Base URL
```
http://localhost:8000/api/v1
```

## Authentication
Currently no authentication required (development mode). Production will require API keys.

## Endpoints

### 1. Clinical Workflows

#### Analyze Clinical Query
Analyzes clinical queries to determine severity and required actions.

```
POST /clinical/analyze-query
```

**Request Body:**
```json
{
  "query_id": "QUERY-001",
  "subject_id": "CARD001",
  "query_text": "Hemoglobin 8.5 g/dL needs review",
  "data_points": [
    {
      "field": "hemoglobin",
      "value": "8.5",
      "unit": "g/dL"
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "query_id": "QUERY-001",
  "analysis": {
    "success": true,
    "analysis_type": "clinical_data_analysis",
    "findings": [
      "Hemoglobin 8.5 g/dL - moderate anemia requiring clinical evaluation"
    ],
    "severity": "major",
    "clinical_significance": "Hemoglobin below normal range requires assessment for causes",
    "recommended_queries": [
      "Verify hemoglobin reading and recent transfusions",
      "Assess for bleeding or other causes of anemia"
    ],
    "priority": "high",
    "medical_assessment": "Moderate anemia requiring prompt clinical evaluation"
  },
  "execution_time": 7.8
}
```

#### Verify Source Data
Compares EDC data against source documents to identify discrepancies.

```
POST /clinical/verify-data
```

**Request Body:**
```json
{
  "subject_id": "CARD001",
  "visit": "Week 4",
  "edc_data": {
    "hemoglobin": {"value": "12.5", "unit": "g/dL"},
    "systolic_bp": {"value": "147", "unit": "mmHg"}
  },
  "source_data": {
    "hemoglobin": {"value": "11.2", "unit": "g/dL"},
    "systolic_bp": {"value": "145", "unit": "mmHg"}
  }
}
```

**Response:**
```json
{
  "success": true,
  "subject_id": "CARD001",
  "verification": {
    "success": true,
    "verification_type": "edc_vs_source_verification",
    "discrepancies": [
      "Hemoglobin: EDC shows 12.5 g/dL, source document shows 11.2 g/dL"
    ],
    "critical_findings": [
      "1.3 g/dL hemoglobin difference requires source verification"
    ],
    "audit_trail": [
      "Verification initiated: 2024-07-11T10:30:00Z",
      "Source documents reviewed: CRF page 2"
    ],
    "verification_status": "discrepancies_found",
    "confidence_score": "0.92",
    "recommendations": [
      "Contact site to verify hemoglobin value",
      "Request source document clarification"
    ]
  },
  "execution_time": 5.2
}
```

#### Detect Protocol Deviations
Identifies protocol compliance issues and suggests corrective actions.

```
POST /clinical/detect-deviations
```

**Request Body:**
```json
{
  "subject_id": "CARD001",
  "visit_data": {
    "visit_date": "2025-01-10",
    "scheduled_date": "2025-01-05",
    "procedures_completed": ["ECG", "Blood Draw"],
    "medications": ["Aspirin"]
  },
  "protocol_requirements": {
    "visit_window_days": 3,
    "required_procedures": ["ECG", "Blood Draw", "ECHO"],
    "prohibited_medications": ["Aspirin"]
  }
}
```

**Response:**
```json
{
  "success": true,
  "subject_id": "CARD001",
  "compliance": {
    "deviations": [
      {
        "type": "visit_window",
        "description": "Visit outside allowed window",
        "severity": "major"
      },
      {
        "type": "prohibited_medication",
        "description": "Subject taking Aspirin",
        "severity": "critical"
      }
    ],
    "compliance_score": 0.6,
    "corrective_actions": ["Document deviation", "Discontinue Aspirin"]
  },
  "execution_time": 4.1
}
```

#### Execute Clinical Workflow
Runs multi-agent workflows for comprehensive analysis.

```
POST /clinical/execute-workflow
```

**Request Body:**
```json
{
  "workflow_type": "comprehensive_analysis",
  "subject_id": "CARD001",
  "input_data": {
    "clinical_concern": "Low hemoglobin with hypertension",
    "data_points": [
      {"field": "hemoglobin", "value": "8.5"},
      {"field": "blood_pressure", "value": "180/95"}
    ]
  }
}
```

**Response:**
```json
{
  "success": true,
  "workflow_type": "comprehensive_analysis",
  "results": {
    "query_analysis": {
      "severity": "critical",
      "findings": ["Severe anemia", "Stage 2 hypertension"]
    },
    "data_verification": {
      "verified": true,
      "confidence": 0.92
    },
    "protocol_compliance": {
      "compliant": false,
      "issues": ["Safety criteria exceeded"]
    },
    "generated_queries": [
      {
        "query_text": "Please confirm Hgb 8.5 and assess for SAE",
        "priority": "urgent"
      }
    ]
  },
  "execution_time": 12.5
}
```

### 2. Test Data Endpoints

#### Get Study Status
```
GET /test-data/status
```

#### Get Subject Data
```
GET /test-data/subjects/{subject_id}
```

#### Get Subject Discrepancies
```
GET /test-data/subjects/{subject_id}/discrepancies
```

#### Get All Queries
```
GET /test-data/queries
```

#### Resolve Query
```
PUT /test-data/queries/{query_id}/resolve
```

#### Get SDV Sessions
```
GET /test-data/sdv/sessions
```

#### Create SDV Session
```
POST /test-data/sdv/sessions
```

#### Get Protocol Deviations
```
GET /test-data/protocol/deviations
```

#### Get Monitoring Schedule
```
GET /test-data/protocol/monitoring
```

#### Get Analytics Dashboard
```
GET /test-data/analytics/dashboard
```

### 3. Dashboard Metrics

#### Get Overall Metrics
```
GET /dashboard/metrics
```

#### Get Query Metrics
```
GET /dashboard/metrics/queries
```

#### Get SDV Metrics
```
GET /dashboard/metrics/sdv
```

#### Get Compliance Metrics
```
GET /dashboard/metrics/compliance
```

### 4. Health Checks

#### API Health
```
GET /health
```

#### Clinical Workflow Health
```
GET /clinical/health
```

## Response Codes

- `200` - Success
- `400` - Bad Request (invalid input)
- `422` - Validation Error
- `500` - Internal Server Error

## Error Format

```json
{
  "error": "Error Type",
  "message": "Detailed error message",
  "details": "Additional context",
  "request_id": "unique-request-id"
}
```

## Rate Limits

Development mode has no rate limits. Production will implement:
- 100 requests/minute per IP
- 1000 requests/hour per API key

## Workflow Types

Available workflow types for `/clinical/execute-workflow`:

1. **comprehensive_analysis** - Full clinical data analysis with all agents
2. **query_resolution** - Analyze and resolve clinical queries
3. **data_verification** - Verify all data points and generate queries

## Agent Capabilities

The system uses 7 specialized AI agents (agents_v2 clean implementation):

1. **Portfolio Manager** - Orchestrates multi-agent workflows
2. **Query Analyzer** - Clinical data analysis and severity assessment  
3. **Data Verifier** - EDC vs source document verification
4. **Query Generator** - Professional query creation with medical language expertise
5. **Query Tracker** - Query lifecycle management and intelligent escalation
6. **Deviation Detector** - Protocol compliance monitoring with regulatory knowledge
7. **Analytics Agent** - Performance analytics and operational insights

## Example Usage

### Python
```python
import httpx
import asyncio

async def analyze_clinical_data():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/v1/clinical/analyze-query",
            json={
                "query_id": "TEST-001",
                "subject_id": "CARD001",
                "query_text": "Hemoglobin 8.5 g/dL",
                "data_points": [{"field": "hemoglobin", "value": "8.5", "unit": "g/dL"}]
            }
        )
        return response.json()

result = asyncio.run(analyze_clinical_data())
print(result)
```

### JavaScript
```javascript
const response = await fetch('http://localhost:8000/api/v1/clinical/analyze-query', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    query_id: 'TEST-001',
    subject_id: 'CARD001',
    query_text: 'Hemoglobin 8.5 g/dL',
    data_points: [{field: 'hemoglobin', value: '8.5', unit: 'g/dL'}]
  })
});
const result = await response.json();
console.log(result);
```

## Notes

- All clinical endpoints use AI/LLM for intelligent analysis
- Function tools execute via OpenAI Agents SDK
- Response times vary based on complexity (2-20 seconds)
- Test data includes 50 cardiology subjects across 3 sites