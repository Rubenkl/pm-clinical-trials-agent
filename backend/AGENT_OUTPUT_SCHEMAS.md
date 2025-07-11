# Agent Output Schemas Documentation

This document provides comprehensive standardized output schemas for all agents in the `agents_v2` directory. Each agent returns structured JSON responses that the frontend can rely on for consistent data handling.

## Overview

All agents use Pydantic models with `strict: True` configuration to ensure consistent JSON output. Each agent has a dedicated output model that defines the exact structure and field types for responses.

---

## 1. Portfolio Manager Agent

**File**: `/backend/app/agents_v2/portfolio_manager.py`

### Output Schema: `PortfolioManagerOutput`

```typescript
interface PortfolioManagerOutput {
  success: boolean;
  workflow_type: string;
  clinical_assessment?: string;
  findings: string[];
  severity?: string;
  safety_implications?: string;
  recommended_actions: string[];
  workflow_next_steps: string[];
  priority?: string;
  execution_time?: string;
}
```

### Example JSON Response

```json
{
  "success": true,
  "workflow_type": "comprehensive_clinical_analysis",
  "clinical_assessment": "Patient showing elevated BP readings requiring immediate clinical attention. BNP levels within normal range for age group.",
  "findings": [
    "Systolic BP 185 mmHg exceeds safety threshold",
    "Patient age 67 years with history of hypertension",
    "Current antihypertensive medication may need adjustment"
  ],
  "severity": "critical",
  "safety_implications": "Risk of cardiovascular events including stroke or MI if BP remains uncontrolled",
  "recommended_actions": [
    "Immediate investigator notification",
    "Blood pressure recheck within 24 hours",
    "Consider study drug interruption",
    "Evaluate antihypertensive therapy"
  ],
  "workflow_next_steps": [
    "Hand off to Query Generator for investigator communication",
    "Hand off to Data Verifier for source document verification",
    "Schedule safety follow-up assessment"
  ],
  "priority": "urgent",
  "execution_time": "2024-07-11T10:30:15Z"
}
```

---

## 2. Query Analyzer Agent

**File**: `/backend/app/agents_v2/query_analyzer.py`

### Output Schema: `QueryAnalyzerOutput`

```typescript
interface QueryAnalyzerOutput {
  success: boolean;
  analysis_type: string;
  findings: string[];
  severity?: string;
  clinical_significance?: string;
  recommended_queries: string[];
  priority?: string;
  medical_assessment?: string;
}
```

### Example JSON Response

```json
{
  "success": true,
  "analysis_type": "clinical_data_analysis",
  "findings": [
    "Hemoglobin 6.2 g/dL - critically low, requires immediate attention",
    "Platelet count 450,000 - elevated but not immediately dangerous",
    "Creatinine 2.8 mg/dL - significant renal impairment"
  ],
  "severity": "critical",
  "clinical_significance": "Multiple safety parameters outside normal ranges with potential for immediate patient harm",
  "recommended_queries": [
    "Please verify hemoglobin result and confirm if patient received transfusion",
    "Provide details on renal function monitoring and dose adjustments",
    "Clarify timing of last complete blood count"
  ],
  "priority": "immediate",
  "medical_assessment": "Critical safety findings requiring immediate investigator contact and potential study drug interruption pending medical evaluation"
}
```

---

## 3. Data Verifier Agent

**File**: `/backend/app/agents_v2/data_verifier.py`

### Output Schema: `DataVerifierOutput`

```typescript
interface DataVerifierOutput {
  success: boolean;
  verification_type: string;
  discrepancies: string[];
  critical_findings: string[];
  audit_trail: string[];
  verification_status: string;
  confidence_score?: string;
  recommendations: string[];
}
```

### Example JSON Response

```json
{
  "success": true,
  "verification_type": "edc_vs_source_verification",
  "discrepancies": [
    "Systolic BP: EDC shows 120 mmHg, source document shows 180 mmHg",
    "Visit date: EDC shows 2024-07-10, source shows 2024-07-11",
    "Hemoglobin units: EDC in g/dL, source in g/L - conversion needed"
  ],
  "critical_findings": [
    "60 mmHg difference in systolic BP represents major safety discrepancy",
    "BP value of 180 mmHg requires immediate safety review"
  ],
  "audit_trail": [
    "Verification initiated: 2024-07-11T10:30:00Z",
    "Source documents reviewed: Case Report Form pages 1-3",
    "Critical discrepancy identified in vital signs section",
    "Immediate escalation triggered for safety review"
  ],
  "verification_status": "critical_discrepancies_found",
  "confidence_score": "0.95",
  "recommendations": [
    "Immediate investigator contact required for BP discrepancy",
    "Source document re-verification needed",
    "Safety assessment prior to next dose",
    "Enhanced monitoring for remaining visits"
  ]
}
```

---

## 4. Query Generator Agent

**File**: `/backend/app/agents_v2/query_generator.py`

### Output Schema: `QueryGeneratorOutput`

```typescript
interface QueryGeneratorOutput {
  success: boolean;
  query_type: string;
  generated_query: string;
  query_priority: string;
  regulatory_compliance: string;
  recommended_timeline: string;
  follow_up_actions: string[];
}
```

### Example JSON Response

```json
{
  "success": true,
  "query_type": "source_verification",
  "generated_query": "Please clarify the systolic blood pressure reading recorded on Day 15 Visit. The EDC shows 120 mmHg, however the source document indicates 180 mmHg. Please verify which value is correct and provide the source document page reference. If 180 mmHg is correct, please confirm what immediate actions were taken given this represents Stage 2 Hypertension per AHA guidelines.",
  "query_priority": "urgent",
  "regulatory_compliance": "ICH-GCP compliant - addresses data integrity requirement for safety parameter",
  "recommended_timeline": "72 hours",
  "follow_up_actions": [
    "Schedule follow-up reminder if no response in 48 hours",
    "Escalate to site management if critical safety issue confirmed",
    "Document resolution in study files",
    "Update safety database if needed"
  ]
}
```

---

## 5. Query Tracker Agent

**File**: `/backend/app/agents_v2/query_tracker.py`

### Output Schema: `QueryTrackerOutput`

```typescript
interface QueryTrackerOutput {
  success: boolean;
  tracking_type: string;
  query_status: string;
  escalation_level: string;
  timeline_status: string;
  sla_compliance: string;
  next_actions: string[];
  performance_metrics: string;
}
```

### Example JSON Response

```json
{
  "success": true,
  "tracking_type": "query_lifecycle_monitoring",
  "query_status": "overdue",
  "escalation_level": "cra_follow_up",
  "timeline_status": "3_days_overdue",
  "sla_compliance": "non_compliant",
  "next_actions": [
    "CRA to contact site principal investigator",
    "Review site workload and capacity",
    "Schedule follow-up call within 24 hours",
    "Document escalation in tracking system"
  ],
  "performance_metrics": "Site average response time: 4.2 days, Current query load: 12 open queries, Site compliance rate: 85%"
}
```

---

## 6. Deviation Detector Agent

**File**: `/backend/app/agents_v2/deviation_detector.py`

### Output Schema: `DeviationDetectorOutput`

```typescript
interface DeviationDetectorOutput {
  success: boolean;
  detection_type: string;
  deviations: string[];
  severity_assessment: string;
  compliance_status: string;
  regulatory_risk: string;
  corrective_actions: string[];
  preventive_measures: string[];
}
```

### Example JSON Response

```json
{
  "success": true,
  "detection_type": "protocol_compliance_monitoring",
  "deviations": [
    "Patient enrolled at age 17.8 years (protocol requires ≥18 years)",
    "Visit 2 occurred 12 days after Visit 1 (protocol window: 7±2 days)",
    "Safety labs missing at Day 15 visit (protocol-required assessment)"
  ],
  "severity_assessment": "critical",
  "compliance_status": "major_protocol_violations",
  "regulatory_risk": "high",
  "corrective_actions": [
    "Remove ineligible patient from study immediately",
    "Notify IRB/EC within 24 hours",
    "Report to regulatory authorities",
    "Conduct root cause analysis",
    "Retrain site staff on eligibility criteria"
  ],
  "preventive_measures": [
    "Implement enhanced eligibility verification checklist",
    "Add automated age calculation to EDC system",
    "Increase CRA monitoring frequency",
    "Provide additional site training on protocol requirements"
  ]
}
```

---

## 7. Analytics Agent

**File**: `/backend/app/agents_v2/analytics_agent.py`

### Output Schema: `AnalyticsAgentOutput`

```typescript
interface AnalyticsAgentOutput {
  success: boolean;
  analysis_type: string;
  key_insights: string[];
  performance_trends: string[];
  risk_indicators: string[];
  recommendations: string[];
  metrics_summary: string;
  predictive_insights: string;
}
```

### Example JSON Response

```json
{
  "success": true,
  "analysis_type": "study_performance_analysis",
  "key_insights": [
    "Site 001 showing 15% higher enrollment rate than study average",
    "Data quality scores improved 8% over last quarter",
    "Query resolution times decreased by 1.2 days on average",
    "Protocol deviation rate stable at 2.1% across all sites"
  ],
  "performance_trends": [
    "Enrollment rate: increasing (+12% vs previous quarter)",
    "Data quality: improving (94.2% vs 87.1% baseline)",
    "Query response time: improving (4.2 days vs 5.4 days)",
    "Site activation: on track (85% of planned sites active)"
  ],
  "risk_indicators": [
    "Site 003 enrollment rate 40% below target",
    "Increased safety query volume at Site 007",
    "Winter holiday period may impact enrollment December-January"
  ],
  "recommendations": [
    "Share Site 001 best practices with underperforming sites",
    "Consider additional CRA support for Site 003",
    "Implement weekly safety reviews for Site 007",
    "Plan enrollment push before holiday season"
  ],
  "metrics_summary": "Overall study health: Good. Enrollment 85% of target, data quality above benchmark, timeline on track for completion Q4 2024.",
  "predictive_insights": "Current trends suggest study completion by December 15, 2024 (±2 weeks). Risk level: Low. Primary endpoint enrollment likely achieved by October 2024."
}
```

---

## Response Wrapper Format

All agent responses are wrapped in a common format from the API endpoints:

```typescript
interface AgentResponse<T> {
  success: boolean;
  [agent_specific_data]: T;  // The agent's output model
  timestamp: string;
  error?: string;  // Only present if success is false
}
```

### Example Wrapped Response

```json
{
  "success": true,
  "analysis": {
    "success": true,
    "analysis_type": "clinical_data_analysis",
    "findings": ["..."],
    "severity": "critical",
    // ... rest of QueryAnalyzerOutput
  },
  "timestamp": "2024-07-11T10:30:15Z"
}
```

### Error Response Format

```json
{
  "success": false,
  "error": "Clinical data analysis failed: Invalid input format",
  "timestamp": "2024-07-11T10:30:15Z"
}
```

---

## Field Types Reference

### Common Field Types

- **boolean**: `true`/`false`
- **string**: Text values, ISO timestamps for dates
- **string[]**: Array of text values
- **Optional fields**: May be `null` or omitted from response

### Severity Values
- `"critical"` - Immediate attention required
- `"major"` - Significant but not immediate
- `"minor"` - Administrative or low impact
- `"normal"` - No issues found

### Priority Values
- `"immediate"` - Within 24 hours
- `"urgent"` - Within 72 hours  
- `"high"` - Within 1 week
- `"medium"` - Standard timeline
- `"low"` - When convenient

### Status Values
- `"completed"` - Successfully finished
- `"in_progress"` - Currently processing
- `"pending"` - Waiting to start
- `"failed"` - Error occurred
- `"overdue"` - Past expected completion

---

## Usage Notes for Frontend Development

1. **Type Safety**: All responses follow the Pydantic models exactly - use TypeScript interfaces above for type checking

2. **Optional Fields**: Fields marked with `?` may be `null` or absent - always check existence before use

3. **Arrays**: All array fields are guaranteed to be arrays (may be empty `[]`)

4. **Timestamps**: All timestamps use ISO 8601 format (`YYYY-MM-DDTHH:mm:ssZ`)

5. **Error Handling**: Always check the `success` field first, then handle the `error` field if `success` is `false`

6. **Nested Objects**: Some responses contain nested analysis objects - refer to the example JSON for exact structure

This documentation ensures consistent frontend integration with predictable, type-safe responses from all clinical trial agents.