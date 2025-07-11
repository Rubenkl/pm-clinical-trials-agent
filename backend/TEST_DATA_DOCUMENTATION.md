# Test Data Generator Documentation

## Overview

The synthetic test data generator creates realistic clinical trial data for comprehensive agent testing, demos, and supervised learning. The system generates balanced datasets with controlled data quality profiles to support various testing scenarios.

## Key Features

### 🎯 Balanced Data Distribution
- **30% Clean Subjects**: No discrepancies or protocol deviations (perfect for "no issues found" demos)
- **34% Discrepancy-Only Subjects**: Have EDC vs source discrepancies but are protocol compliant
- **36% Complex Subjects**: May have both discrepancies AND protocol deviations

### 🏥 Realistic Clinical Scenarios
- **Cardiology Phase 2 Study**: 50 subjects across 3 sites with cardiovascular data
- **Protocol Requirements**: Age limits, BP thresholds, LVEF minimums, creatinine maximums
- **Visit Windows**: Screening, Baseline, Week 4/8/12, End of Study with compliance tracking
- **Clinical Parameters**: Vital signs, laboratory values, imaging results, adverse events

### 🤖 Supervised Learning Support
Every subject includes `_generation_metadata` for model training:
```json
{
  "quality_profile": "clean|discrepancy_only|complex",
  "has_discrepancies": true/false,
  "has_protocol_deviations": true/false,
  "is_ground_truth": true,
  "generation_timestamp": "2025-01-11T..."
}
```

## Data Quality Profiles

### Clean Subjects (30%)
- **Purpose**: Demo scenarios showing perfect compliance
- **Characteristics**: 
  - Zero EDC vs source discrepancies
  - All values within protocol limits
  - Visits within allowed windows
- **Demo Use**: "No issues found" workflows, baseline performance
- **Examples**: CARD001, CARD002, CARD010, CARD012, CARD013

### Discrepancy-Only Subjects (34%) 
- **Purpose**: Demo EDC vs source verification workflows
- **Characteristics**:
  - 1-10 EDC vs source discrepancies per subject
  - Protocol compliant (age, BP, labs within limits)
  - Visit timing compliant
- **Demo Use**: Source Data Verification (SDV), query generation
- **Examples**: CARD008 (8 discrepancies), CARD014 (9 discrepancies)

### Complex Subjects (36%)
- **Purpose**: Demo comprehensive clinical oversight
- **Characteristics**:
  - May have EDC vs source discrepancies (80% chance)
  - May have protocol deviations (20% chance)
  - Multiple data integrity issues
- **Demo Use**: Full clinical monitoring workflows, escalation scenarios
- **Examples**: CARD003 (16 discrepancies), CARD004 (14 discrepancies)

## Protocol Deviations Generated

### Inclusion Criteria Violations
- **Age Deviations**: Subjects aged 17 or 81+ (outside 18-80 range)
- **Blood Pressure**: Systolic BP >185 mmHg (protocol limit: 180 mmHg)
- **Kidney Function**: Creatinine >2.7 mg/dL (protocol limit: 2.5 mg/dL)
- **Cardiac Function**: LVEF <35% (protocol minimum: 40%)

### Visit Window Violations
- **Week 4**: Outside ±3 day window
- **Week 8**: Outside ±5 day window  
- **Week 12**: Outside ±7 day window
- **End of Study**: Outside ±14 day window

### Missing Required Assessments
- Vital signs: systolic_bp, diastolic_bp, heart_rate
- Laboratory: troponin, BNP, creatinine
- Imaging: LVEF

## Demo Scenarios by Agent

### Data Verifier Agent
- **Clean Demo**: Use CARD001, CARD002 → "No discrepancies found"
- **Issues Demo**: Use CARD008, CARD014 → Shows 8-9 specific discrepancies
- **Complex Demo**: Use CARD003, CARD006 → Shows 15-17 discrepancies

### Deviation Detector Agent  
- **Compliant Demo**: Use CARD001, CARD010 → "No protocol deviations detected"
- **Minor Violations**: Use subjects with single parameter deviations
- **Major Violations**: Use subjects with age or multiple parameter violations

### Query Generator Agent
- **No Queries Demo**: Use clean subjects → "No queries required"
- **Standard Queries**: Use discrepancy-only subjects → Generate 1-10 queries
- **Complex Queries**: Use complex subjects → Generate queries for both discrepancies and deviations

### Portfolio Manager Agent
- **Low Risk**: Use clean subjects → Minimal oversight needed
- **Medium Risk**: Use discrepancy-only subjects → Focus on data quality
- **High Risk**: Use complex subjects → Comprehensive monitoring required

## Configuration Parameters

```python
# Current cardiology_phase2 preset
StudyConfiguration(
    protocol_id="CARD-2025-001",
    phase="Phase II", 
    therapeutic_area="cardiology",
    subject_count=50,
    site_count=3,
    discrepancy_rate=0.02,           # 2% chance per data point
    critical_event_rate=0.04,        # 4% serious adverse events
    protocol_deviation_rate=0.20,    # 20% of subjects may have deviations
    clean_subjects_rate=0.30,        # 30% completely clean subjects
)
```

## Agent Evaluation & Supervised Learning

### Ground Truth Labels
Each subject's metadata provides definitive labels for training:
- `has_discrepancies`: Whether EDC vs source issues exist
- `has_protocol_deviations`: Whether protocol violations exist  
- `quality_profile`: Overall data quality classification

### Model Training Scenarios
1. **Binary Classification**: Clean vs problematic subjects
2. **Multi-class Classification**: clean/discrepancy_only/complex profiles
3. **Regression**: Predict number of discrepancies/deviations
4. **Object Detection**: Identify specific types of violations

### Evaluation Metrics
- **Data Verifier**: Precision/recall on discrepancy detection
- **Deviation Detector**: Accuracy on protocol compliance assessment
- **Query Generator**: Appropriateness of generated queries
- **Portfolio Manager**: Risk stratification accuracy

## API Integration

### Test Data Service Methods
```python
# Get subject with metadata
subject_data = await test_service.get_subject_data("CARD001")

# Check if subject has known issues (for evaluation)
metadata = subject_data["_generation_metadata"] 
expected_discrepancies = metadata["has_discrepancies"]
expected_deviations = metadata["has_protocol_deviations"]

# Get discrepancies for verification
discrepancies = await test_service.get_discrepancies("CARD001")
```

### Frontend Demo Guidelines
- **Hide metadata**: Never display `_generation_metadata` in demos
- **Use variety**: Rotate between clean and problematic subjects
- **Show progression**: Start with clean, then show increasingly complex cases
- **Realistic timing**: Use subjects that demonstrate realistic clinical scenarios

## Performance Benchmarks

### Expected Agent Performance
- **Clean Subjects**: Should return "no issues" results in <5 seconds
- **Simple Issues**: Should detect 1-10 discrepancies accurately 
- **Complex Issues**: Should handle 15+ issues without timeout
- **Protocol Compliance**: Should identify age, BP, lab limit violations

### Realistic Metrics
- **Discrepancy Rate**: 8.4 per subject average (range 0-20)
- **Protocol Deviation Rate**: ~20% of subjects affected
- **Clean Subject Rate**: 38% have zero issues
- **Query Generation**: 1-3 queries per discrepancy typically

This balanced approach ensures comprehensive testing coverage while providing realistic demo scenarios that showcase both successful "no issues found" workflows and complex clinical monitoring capabilities.