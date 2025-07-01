# Test Data Strategy for Clinical Trials Agent System

## Overview

This document outlines the comprehensive test data strategy for the Clinical Trials Agent System, enabling full end-to-end testing without requiring access to real clinical trial data.

## 🎯 System Architecture & Data Flow

### Multi-Agent Workflow
```
Portfolio Manager (Orchestrator)
├── Query Analyzer → Clinical data analysis, medical terminology
├── Data Verifier → Cross-system verification, SDV processes  
├── Query Generator → Clinical query generation, compliance
└── Query Tracker → Lifecycle tracking, SLA monitoring
```

### Core Data Flow Patterns
1. **Query Resolution**: Portfolio Manager → Query Analyzer → Query Generator → Query Tracker
2. **Data Verification**: Portfolio Manager → Data Verifier → Query Generator → Query Tracker  
3. **Comprehensive Analysis**: All agents in sequence with handoffs

## 📊 Test Data Components

### 1. Synthetic Data Generation
**Location**: `/backend/tests/test_data/synthetic_data_generator.py`

**Key Features**:
- **Therapeutic Area Templates**: Cardiology and Oncology with realistic parameter ranges
- **Configurable Discrepancy Rates**: 5-20% configurable discrepancy injection
- **Multiple Study Phases**: Phase I, II, III with appropriate characteristics
- **Site Performance Variation**: Different sites with varying quality metrics
- **Critical Event Simulation**: SAEs, protocol deviations, eligibility violations

**Study Presets**:
```python
STUDY_PRESETS = {
    "cardiology_phase2": StudyConfiguration(
        protocol_id="CARD-2025-001", 
        phase="Phase II",
        therapeutic_area="cardiology",
        subject_count=50,
        site_count=3,
        discrepancy_rate=0.12,
        critical_event_rate=0.04
    ),
    "oncology_phase1": StudyConfiguration(
        protocol_id="ONCO-2025-001",
        phase="Phase I", 
        therapeutic_area="oncology",
        subject_count=30,
        site_count=2,
        discrepancy_rate=0.20,
        critical_event_rate=0.08
    )
}
```

### 2. Test Data Service Integration
**Location**: `/backend/app/services/test_data_service.py`

**Core Capabilities**:
- **Configurable Test Mode**: Environment variable controlled
- **Multi-Source Data Access**: EDC, Source Documents, Combined views
- **Ground Truth Validation**: Known discrepancies for agent testing
- **Performance Metrics**: Site and subject-level quality indicators
- **Fast Lookup Cache**: Optimized data retrieval for agent workflows

**Key Methods**:
```python
# Subject data access
await test_service.get_subject_data(subject_id, data_source="both")
await test_service.get_visit_data(subject_id, visit_name, data_source="edc")

# Discrepancy testing
await test_service.get_discrepancies(subject_id, visit_name=None)
await test_service.get_subjects_with_discrepancies(severity="critical")

# Query workflow testing
await test_service.get_queries(subject_id, visit_name=None)

# Performance monitoring
await test_service.get_site_performance_data()
```

### 3. API Endpoints for Testing
**Location**: `/backend/app/api/endpoints/test_data.py`

**Available Endpoints**:
- `GET /api/v1/test-data/status` - Test data status and statistics
- `GET /api/v1/test-data/subjects/{subject_id}` - Subject data access
- `GET /api/v1/test-data/subjects/{subject_id}/discrepancies` - Known discrepancies
- `GET /api/v1/test-data/subjects/{subject_id}/queries` - Existing queries
- `GET /api/v1/test-data/sites/performance` - Site performance metrics
- `POST /api/v1/test-data/regenerate` - Regenerate test data

## ⚙️ Configuration & Setup

### Environment Configuration
```bash
# Enable test data mode
USE_TEST_DATA=true

# Select study preset
TEST_DATA_PRESET="cardiology_phase2"  # or "oncology_phase1"

# Test data path
TEST_DATA_PATH="tests/test_data/"
```

### Backend Integration
```python
from app.core.config import get_settings
from app.services.test_data_service import TestDataService

settings = get_settings()
test_service = TestDataService(settings)

# Check if test mode is enabled
if test_service.is_test_mode():
    # Use synthetic data
    data = await test_service.get_subject_data(subject_id)
else:
    # Use real data integrations
    data = await real_data_service.get_subject_data(subject_id)
```

## 🧪 Testing Strategies

### 1. Agent Performance Testing
**Ground Truth Validation**:
```python
# Test Data Verifier accuracy
test_dataset = get_test_dataset("DISCREPANCY_001")
result = await data_verifier.cross_system_verification(
    test_dataset["edc_data"], 
    test_dataset["source_data"]
)
metrics = calculate_performance_metrics(
    result.discrepancies, 
    test_dataset["expected_discrepancies"]
)
assert metrics["precision"] >= 0.85
```

### 2. End-to-End Workflow Testing
**Complete Workflow Validation**:
```python
# 1. Portfolio Manager: Get prioritized subjects
subjects_with_issues = await test_service.get_subjects_with_discrepancies("critical")

# 2. Data Verifier: Process known discrepancies  
subject_data = await test_service.get_subject_data(subject_id, "both")
discrepancies = await test_service.get_discrepancies(subject_id)

# 3. Query Generator: Generate queries based on findings
# 4. Query Tracker: Track query lifecycle

# 5. Validate complete workflow
assert workflow_completed_successfully
```

### 3. Performance Benchmarking
**Agent Performance Metrics**:
- **Query Analyzer**: Medical terminology accuracy, pattern detection
- **Data Verifier**: Discrepancy detection precision/recall, SDV accuracy
- **Query Generator**: Query quality, compliance validation
- **Query Tracker**: SLA tracking accuracy, escalation timing
- **Portfolio Manager**: Workflow orchestration efficiency

## 📋 Test Data Structure

### Subject Data Format
```json
{
  "subject_id": "CARD001",
  "site_id": "SITE_001",
  "demographics": {
    "age": 65,
    "gender": "M",
    "weight": 85.2
  },
  "visits": [
    {
      "visit_name": "Baseline",
      "visit_date": "2025-01-15",
      "edc_data": {
        "vital_signs": {"systolic_bp": 140, "heart_rate": 72},
        "laboratory": {"troponin": 0.04, "bnp": 125}
      },
      "source_data": {
        "vital_signs": {"systolic_bp": 142, "heart_rate": 72},
        "laboratory": {"troponin": 0.04, "bnp": 125}
      },
      "discrepancies": [
        {
          "field": "vital_signs.systolic_bp",
          "edc_value": 140,
          "source_value": 142,
          "severity": "minor",
          "discrepancy_type": "value_difference"
        }
      ],
      "queries": [
        {
          "query_id": "Q_CARD001_Baseline_001",
          "query_text": "Please verify systolic BP...",
          "severity": "minor",
          "status": "Open"
        }
      ]
    }
  ]
}
```

### Discrepancy Types
- **Value Differences**: Numeric discrepancies with realistic variance
- **Missing Data**: Data present in one source but not the other
- **Unit Conversions**: Same values in different units (mg/dL vs mmol/L)
- **Protocol Deviations**: Eligibility violations, procedure deviations
- **Safety Events**: Adverse events, serious adverse events

## 🔄 Workflow Testing Examples

### 1. Data Verification Workflow
```python
# Test known discrepancy detection
subject_id = "CARD001"
both_data = await test_service.get_subject_data(subject_id, "both")

# Expected discrepancies are pre-calculated
expected_discrepancies = await test_service.get_discrepancies(subject_id)

# Test agent against known truth
agent_result = await data_verifier.verify_data(
    both_data["edc_data"], 
    both_data["source_data"]
)

# Validate accuracy
accuracy = calculate_accuracy(agent_result, expected_discrepancies)
assert accuracy >= 0.85
```

### 2. Query Generation Workflow
```python
# Test query generation from discrepancies
discrepancies = await test_service.get_discrepancies(subject_id)
generated_queries = await query_generator.generate_queries(discrepancies)

# Validate query quality
for query in generated_queries:
    assert "query_text" in query
    assert len(query["query_text"]) > 20  # Meaningful content
    assert query["severity"] in ["critical", "major", "minor"]
```

### 3. Portfolio Manager Orchestration
```python
# Test complete workflow orchestration
workflow_request = {
    "workflow_type": "data_verification",
    "subject_id": subject_id,
    "priority": "high"
}

result = await portfolio_manager.orchestrate_workflow(workflow_request)

# Validate orchestration
assert result["success"] is True
assert "workflow_id" in result
assert "agent_handoffs" in result
```

## 📈 Performance Metrics & Validation

### Agent Performance Targets
- **Precision**: ≥ 0.85 for discrepancy detection
- **Recall**: ≥ 0.80 for critical finding identification  
- **F1-Score**: ≥ 0.82 overall performance
- **Response Time**: < 30 seconds for complete subject analysis
- **Accuracy**: ≥ 0.90 for medical terminology processing

### Test Coverage Requirements
- **Unit Tests**: > 90% code coverage for all agents
- **Integration Tests**: All 8 handoff patterns tested
- **Performance Tests**: All 6 discrepancy categories validated
- **End-to-End Tests**: Complete workflows for each therapeutic area

## 🚀 Running Test Data Workflows

### Quick Start
```bash
# 1. Enable test data mode
export USE_TEST_DATA=true
export TEST_DATA_PRESET="cardiology_phase2"

# 2. Start backend with test data
cd backend
uvicorn app.main:app --reload

# 3. Access test data via API
curl http://localhost:8000/api/v1/test-data/status

# 4. Run complete workflow tests
pytest tests/test_complete_workflow_with_synthetic_data.py -v
```

### Advanced Testing
```bash
# Generate different study types
pytest tests/test_synthetic_data_generator.py -v

# Test specific agent performance
pytest tests/test_data_verifier_realistic.py -v

# Run integration tests with mocked OpenAI calls
pytest tests/test_sdk_integration.py -v
```

## 🔧 Customization & Extension

### Adding New Therapeutic Areas
```python
# In synthetic_data_generator.py
therapeutic_templates["neurology"] = {
    "vital_signs": {"systolic_bp": (100, 160), "heart_rate": (60, 100)},
    "laboratory": {"glucose": (70, 140), "creatinine": (0.6, 1.2)},
    "neurological": {"mmse_score": (24, 30), "gait_speed": (0.8, 1.4)},
    "adverse_events": ["headache", "dizziness", "confusion", "seizure"]
}
```

### Adding New Discrepancy Types
```python
def _introduce_temporal_inconsistencies(self, data: Dict) -> None:
    """Add time-based inconsistencies (dates, sequences)."""
    # Implementation for temporal discrepancies
    pass

def _introduce_calculation_errors(self, data: Dict) -> None:
    """Add calculation-based discrepancies (derived values)."""
    # Implementation for calculation errors
    pass
```

## 📝 Best Practices

### 1. Test Data Management
- **Version Control**: All synthetic data generation is deterministic and version-controlled
- **Isolation**: Test data completely separate from any real clinical data
- **Compliance**: Generated data follows de-identification best practices
- **Performance**: Cached lookups for fast agent testing

### 2. Agent Testing Strategy
- **Ground Truth First**: Always test against known expected results
- **Incremental Complexity**: Start with simple cases, progress to complex scenarios
- **Error Simulation**: Include edge cases and error conditions
- **Performance Monitoring**: Track agent performance over time

### 3. Development Workflow
- **Test Mode Toggle**: Easy switching between test and real data modes
- **Continuous Validation**: Automated testing of agent performance
- **Realistic Scenarios**: Test data mirrors real clinical trial complexity
- **Documentation**: Clear documentation of all test scenarios and expected outcomes

This test data strategy enables comprehensive testing of the Clinical Trials Agent System without requiring access to real clinical data, while maintaining realistic complexity and validation scenarios.