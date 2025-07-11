# Architecture Analysis: Clinical Trials Agent System

## Current State Assessment

### What We're Building (Per PRD)
- **Enterprise Automation Platform** for clinical trials
- **NOT a chatbot** - structured API endpoints triggering workflows
- Dashboard-driven UX with metrics
- Multi-agent orchestration using OpenAI Agents SDK

### Key Agent Types (from PRD)
1. **Query Resolution Agents**: Analyze discrepancies, generate queries, track lifecycle
2. **SDV Agents**: Risk assessment, data verification, monitoring orchestration
3. **Deviation Detection**: Pattern recognition, root cause analysis, compliance reporting
4. **Patient Recruitment**: Patient matching, screening, enrollment

## Current Implementation Analysis

### What Should Use LLM Intelligence
These require medical context and judgment:

1. **Field Criticality Assessment**
   - Whether hemoglobin is critical depends on the study (oncology vs cardiology)
   - Criticality changes based on patient population
   - ✅ CORRECT to use LLM

2. **Tolerance Values**
   - Acceptable variance for hemoglobin differs for anemic patients
   - Blood pressure tolerance varies by indication
   - ✅ CORRECT to use LLM

3. **Medical Term Severity**
   - "Headache" severity depends on context (migraine study vs oncology)
   - Same term can be critical or minor based on patient history
   - ✅ CORRECT to use LLM

4. **Discrepancy Impact Assessment**
   - Clinical significance of data differences
   - Whether a discrepancy requires immediate action
   - ✅ CORRECT to use LLM

### What Should Stay as Standardized Logic
These are industry-standard classifications:

1. **Age Groups**
   - Pediatric: <18 years (FDA definition)
   - Adult: 18-65 years
   - Geriatric: >65 years
   - ❌ WRONG to remove - these are regulatory standards

2. **CrCl Categories**
   - Normal: ≥90 mL/min (KDIGO guidelines)
   - Mild decrease: 60-89 mL/min
   - These are globally accepted medical standards
   - ❌ WRONG to remove

3. **Unit Conversions**
   - mg/dL to mmol/L is pure mathematics
   - No medical judgment needed
   - ✅ CORRECT to keep as calculation

4. **Visit Window Calculations**
   - Whether Day 8 is within Day 7 ± 3 window is math
   - ✅ CORRECT to keep as calculation

## Problems with Current Approach

### 1. Mixing Concerns
The current code mixes:
- Mathematical calculations (good for function tools)
- Medical standards (should be configuration/constants)
- Medical judgments (needs LLM)

### 2. Function Tool Misuse
Current function tools like `analyze_data_point()` return mock medical judgments instead of helping with calculations.

### 3. Incomplete LLM Integration
Many endpoints still use rule-based logic instead of calling the AI methods.

## Recommended Architecture

### 1. Layer Separation
```
API Endpoints
    ↓
Agent Orchestration (Portfolio Manager)
    ↓
Specialist Agents (with LLM intelligence)
    ↓
Helper Tools (pure calculations)
    ↓
Medical Standards (configuration)
```

### 2. Function Tools Should Be:
- **Unit converters**: Convert mg/dL to mmol/L
- **Date calculators**: Age at visit, days between dates
- **Statistical calculators**: Mean, SD, outlier detection
- **Format validators**: Check date formats, numeric ranges

### 3. LLM Should Handle:
- **Medical reasoning**: Is this value concerning?
- **Context assessment**: What's critical for this study?
- **Clinical interpretation**: What does this pattern mean?
- **Recommendation generation**: What action to take?

### 4. Configuration Should Define:
- **Medical standards**: Age groups, CrCl categories
- **Regulatory requirements**: ICH-GCP rules
- **Study-specific thresholds**: Protocol-defined limits

## Action Plan

### Phase 1: Clean Architecture
1. Keep calculation tools for pure math (age, CrCl, units)
2. Keep medical standard categories in configuration
3. Remove mock medical judgment functions
4. Ensure all agents use LLM for actual medical reasoning

### Phase 2: Proper Integration
1. Update API endpoints to call agent AI methods
2. Create proper handoff patterns between agents
3. Implement context sharing for medical decisions
4. Add proper error handling and fallbacks

### Phase 3: Testing & Validation
1. Test with real clinical scenarios
2. Validate medical reasoning accuracy
3. Ensure regulatory compliance
4. Performance optimization

## Conclusion

The system architecture is sound, but we need to:
1. **Keep standardized medical categories** (age groups, CrCl ranges)
2. **Use LLM for contextual decisions** (criticality, severity)
3. **Separate pure calculations from medical judgments**
4. **Focus on the enterprise automation use case**, not chat

This is about automating clinical trial workflows with intelligence, not removing all domain knowledge.