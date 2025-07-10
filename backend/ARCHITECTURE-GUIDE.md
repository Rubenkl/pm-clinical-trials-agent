# Clinical Trials Automation Platform - Backend Architecture Guide
**Version:** 1.0  
**Date:** January 2025  
**Status:** Single Source of Truth

## 🎯 What We're Building

**THIS IS:** An internal IQVIA enterprise automation platform for clinical trials  
**THIS IS NOT:** A chatbot or conversational AI system

### Core Architecture
```
Frontend Dashboard → Structured API → Portfolio Manager → Agent Workflows → Automated Actions → Dashboard Updates
```

## 📋 API Endpoints (No Chat!)

### Query Management
```python
POST /api/v1/queries/analyze
# Analyzes clinical data and auto-generates queries
# Input: study_id, site_id, subject_id, data_points
# Output: discrepancies, generated_queries, automated_actions, metrics

GET /api/v1/queries/{query_id}/status
# Tracks query lifecycle

POST /api/v1/queries/bulk-analyze
# Bulk operations for multiple subjects

GET /api/v1/queries/metrics
# Dashboard metrics (pending count, avg resolution time, compliance score)
```

### Source Data Verification (SDV)
```python
POST /api/v1/sdv/schedule
# Creates risk-based SDV schedule
# Output: scheduled_verifications, cost_savings, risk_coverage

POST /api/v1/sdv/verify
# Performs automated verification
# Output: match_scores, discrepancies, audit_trail

GET /api/v1/sdv/metrics
# SDV efficiency metrics
```

### Protocol Deviation Detection
```python
POST /api/v1/deviations/monitor
# Real-time monitoring configuration

GET /api/v1/deviations/patterns
# Pattern analysis across sites

POST /api/v1/deviations/report
# Compliance report generation
```

### Dashboard APIs
```python
GET /api/v1/dashboard/overview
# Executive metrics

GET /api/v1/metrics/sites/{site_id}
# Site performance data
```

## 🤖 Agent Architecture (Process Data, Don't Chat!)

### Portfolio Manager - Workflow Orchestrator
```python
class PortfolioManager:
    """Orchestrates workflows, NOT conversations"""
    
    async def orchestrate_query_workflow(self, request: AnalyzeDataRequest):
        # 1. Query Analyzer identifies discrepancies
        # 2. Data Verifier confirms findings
        # 3. Query Generator creates queries
        # 4. Query Tracker monitors lifecycle
        # Returns structured JSON for dashboard
```

### Agent Instructions Template
```python
# CORRECT - Automation focused:
instructions = """You are an automated clinical data processor.
Analyze structured inputs and return JSON with findings, severity, and actions.
Trigger escalations for critical findings. Never engage in conversation."""

# WRONG - Chat focused:
# "You are a helpful assistant..." ❌
```

## 🚀 Automated Workflows

### 1. Data Discrepancy Detection
**Trigger:** EDC data import or manual upload  
**Workflow:**
- Analyze → Classify severity → Generate queries → Set SLAs → Escalate if critical
- **Automatic actions:** Medical monitor alerts, site notifications, dashboard flags

### 2. Risk-Based SDV
**Trigger:** Weekly schedule or quality threshold breach  
**Workflow:**
- Calculate risk scores → Schedule verifications → Process documents → Flag issues
- **Cost savings:** 75% reduction through smart sampling

### 3. Protocol Deviation Prevention
**Trigger:** Continuous monitoring  
**Workflow:**
- Monitor compliance → Predict issues → Alert BEFORE deviation → Generate CAPA
- **Prevention rate:** 60% of deviations avoided

### 4. Safety Signal Detection
**Trigger:** AE report or critical lab value  
**Workflow:**
- Triage severity → Pattern detection → Medical review → Regulatory reporting
- **Timeline:** 24-hour SAE reporting compliance

## 📊 Response Models for Frontend

```python
class QueryAnalysisResponse(BaseModel):
    analysis_id: str
    severity: str  # "critical", "major", "minor"
    findings: List[DiscrepancyFinding]
    generated_queries: List[GeneratedQuery]
    automated_actions: List[str]  # ["medical_monitor_notified", "site_alerted"]
    metrics: DashboardMetrics

class DiscrepancyFinding(BaseModel):
    field_name: str
    severity: str
    edc_value: Optional[str]
    source_value: Optional[str]
    clinical_significance: str
    action_required: str
```

## ✅ Implementation Checklist

### Remove (This Week)
- [ ] `/agents/chat` endpoint
- [ ] Conversation history tracking
- [ ] Message-based agent communication
- [ ] All conversational agent instructions

### Build (Next 2 Weeks)
- [ ] Structured API endpoints
- [ ] Workflow orchestration in Portfolio Manager
- [ ] Automatic action triggers
- [ ] Dashboard response models
- [ ] Continuous monitoring loops

## 🎯 Success Metrics

**Measure These:**
- Query processing: 30 min → 3 min (90% reduction)
- SDV costs: 75% reduction
- Deviation detection: Days → 30 minutes
- Auto-generated queries: 95%
- Critical escalations within SLA: 100%

**NOT These:**
- ❌ Chat quality
- ❌ Conversation completion
- ❌ Natural language understanding

## 🏗️ Corrected Task Priorities

1. **Task A1:** Remove all chat patterns
2. **Task A2:** Update agent instructions for structured output
3. **Task A3:** Portfolio Manager as workflow orchestrator
4. **Task A4:** Implement structured endpoints
5. **Task A5:** Create dashboard response models
6. **Task A6:** Automatic query generation
7. **Task A7:** Continuous monitoring loops
8. **Task A8:** Escalation automation

## 💡 Key Principles

1. **Agents process data, they don't chat**
2. **APIs are structured, not conversational**
3. **Actions are automatic, not prompted**
4. **Output is for dashboards, not dialogue**
5. **System is proactive, not reactive**

## 🚀 What Success Looks Like

- CRA uploads data → System finds issues → Queries appear on dashboard
- No chat windows, no conversations, no "helpful" responses
- Automatic escalation for critical findings
- Real-time dashboard updates
- One-click bulk operations
- Proactive alerts before problems occur

**Remember:** This is enterprise automation using AI agents as processors, not a chatbot. Users interact with dashboards, not agents.