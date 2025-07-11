# Endpoint Analysis: AI vs Mock Data

## Current Endpoint Architecture

### 1. Production Endpoints (`/api/v1/clinical/*`)
**Location**: `app/api/endpoints/clinical_workflows.py`
**Status**: ✅ **USING REAL AI**

These endpoints correctly use `Runner.run()` to execute agents with real AI:
- `/analyze-query` - Uses query_analyzer_agent with Runner.run()
- `/verify-data` - Uses data_verifier_agent with Runner.run()
- `/detect-deviations` - Uses deviation_detector_agent with Runner.run()
- `/execute-workflow` - Uses portfolio_manager_agent with Runner.run()

**Example**:
```python
result = await Runner.run(query_analyzer_agent, message, context)
```

### 2. Test Data Endpoints (`/api/v1/test-data/*`)
**Location**: `app/api/endpoints/test_data.py`
**Status**: ✅ **CORRECTLY USING MOCK DATA**

These endpoints use `TestDataService` directly (no agents):
- `/status` - Returns test data statistics
- `/subjects/{id}` - Returns mock subject data
- `/queries` - Returns mock queries
- `/sdv/sessions` - Returns mock SDV sessions
- etc.

**This is correct because**:
- Frontend needs predictable data for development
- Test endpoints should NOT use expensive AI calls
- Mock data helps with UI testing and demos

### 3. Dashboard Endpoints (`/api/v1/dashboard/*`)
**Location**: `app/api/endpoints/dashboard.py`
**Status**: ✅ **CORRECTLY USING ANALYTICS**

These endpoints use analytics services for metrics and visualization data.

## The Real Problem

The issue is NOT with the endpoints - they're correctly architected. The problem is with the **function tools inside agents**:

### Mock Function Tools (TO BE REMOVED)
These function tools return fake medical judgments instead of using AI:

1. **portfolio_manager.py**:
   - `analyze_clinical_values()` - Returns mock severity assessments
   - `orchestrate_workflow()` - Returns mock workflow templates
   - `execute_workflow_step()` - Fake execution status
   - `get_workflow_status()` - Mock status data
   - `coordinate_agent_handoff()` - Fake coordination
   - `monitor_workflow_performance()` - Mock metrics

2. **deviation_detector.py**:
   - `classify_deviation_severity()` - Mock severity classification
   - `assess_compliance_impact()` - Fake compliance assessment

### Good Function Tools (TO BE KEPT)
1. **calculation_tools.py** - All 7 tools are pure calculations ✅
2. **Test data retrieval** - `get_test_subject_data()`, `get_subject_discrepancies()` ✅

## Conclusion

**Endpoints are fine!** The architecture correctly separates:
- Production endpoints → Use AI via Runner.run()
- Test endpoints → Use mock data for frontend
- Dashboard endpoints → Use analytics

**The cleanup needed is**:
- Remove mock medical judgment function tools from agents
- Keep calculation tools and test data retrieval
- Ensure agents rely on their AI intelligence, not mock functions