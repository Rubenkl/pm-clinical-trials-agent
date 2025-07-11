# Function Tool Audit and Refactoring Plan

## Current State Analysis

### Function Tools by File

#### 1. calculation_tools.py (7 tools) - ✅ KEEP ALL
These are legitimate calculation helpers:
- `convert_medical_units` - Pure unit conversion (mg/dL to mmol/L)
- `calculate_age_at_visit` - Date math for age calculation
- `check_visit_window_compliance` - Date window validation
- `calculate_change_from_baseline` - Percentage/absolute change
- `calculate_body_surface_area` - BSA calculation formulas
- `calculate_creatinine_clearance` - CrCl calculation
- `calculate_date_difference` - Date interval calculations

**Assessment**: These are EXACTLY what function tools should be - pure calculations without medical judgments.

#### 2. portfolio_manager.py (8 tools) - 🔍 MIXED
- `get_test_subject_data` - ✅ KEEP (needed for test data endpoints)
- `analyze_clinical_values` - ❌ REMOVE (makes mock medical judgments)
- `get_subject_discrepancies` - ✅ KEEP (retrieves test data)
- `orchestrate_workflow` - ❌ REMOVE (returns mock workflow templates)
- `execute_workflow_step` - ❌ REMOVE (likely mock execution)
- `get_workflow_status` - ❌ REMOVE (likely mock status)
- `coordinate_agent_handoff` - ❌ REMOVE (likely mock coordination)
- `monitor_workflow_performance` - ❌ REMOVE (returns mock metrics)

#### 3. deviation_detector.py (2 tools) - ❌ REMOVE BOTH
- `classify_deviation_severity` - Makes mock medical severity judgments
- `assess_compliance_impact` - Makes mock compliance assessments

### Other Agents Without Function Tools
- data_verifier.py - No function tools (uses AI methods)
- query_analyzer.py - No function tools (uses AI methods)
- query_generator.py - No function tools (uses AI methods)
- query_tracker.py - No function tools (uses AI methods)

## The Core Problem

1. **Mixed Purposes**: Function tools are doing three different things:
   - Pure calculations (GOOD)
   - Mock medical judgments (BAD)
   - Test data retrieval (NECESSARY for test endpoints)

2. **Incomplete Removal**: I removed function definitions but left docstrings

3. **Architecture Confusion**: The system has both:
   - Test endpoints (`/test-data/*`) that need predictable data
   - Production endpoints (`/clinical/*`) that should use real AI

## Proposed Plan

### Option A: Clean Refactor in Place
1. Keep calculation_tools.py as is (it's perfect)
2. Move test data functions to a separate `test_data_tools.py`
3. Remove all mock medical judgment functions
4. Update agents to only include appropriate tools
5. Ensure production endpoints use AI methods via Runner.run()

### Option B: Fresh Start in New Directory (RECOMMENDED)
1. Create `/app/agents_v2/` directory
2. Copy over only the good parts:
   - Agent class structures with AI methods
   - calculation_tools.py unchanged
   - Test data retrieval tools in separate file
3. Remove ALL mock judgment functions
4. Update imports in API endpoints
5. Delete old `/app/agents/` once verified

## Plan Critique

### Strengths:
- Clear separation of concerns
- Preserves working calculation tools
- Maintains test data functionality
- Clean architecture aligned with PRD

### Weaknesses:
- Option A risks missing something in complex files
- Option B requires updating all imports
- Need to carefully preserve the extensive docstrings for legitimate tools
- Must ensure we don't break test endpoints

### Critical Questions (ANSWERED):
1. **Are the workflow orchestration tools in portfolio_manager.py actually useful?**
   - NO - They return mock workflow templates and fake metrics
   - Real orchestration should happen via Runner.run() and agent handoffs
   
2. **Should test data tools be function tools at all?**
   - YES for now - They're needed by the Portfolio Manager when called via Runner.run()
   - Could be refactored to service methods later
   
3. **How do we ensure the extensive documentation stays with the right functions?**
   - The extensive docs are valuable for calculation tools (they explain medical context)
   - Copy entire functions including docstrings for keepers
   - Remove entire functions (including docstrings) for mock tools

## Major Architecture Issues Found

1. **Mock Function Tools Everywhere**: 
   - 11 out of 17 function tools are mock implementations
   - They return fake medical assessments, not real calculations
   
2. **Orchestration Confusion**:
   - Portfolio Manager has mock orchestration tools
   - Real orchestration should use OpenAI SDK's Runner and handoffs
   
3. **Mixed Test/Production Logic**:
   - Test data retrieval mixed with mock medical logic
   - No clear separation between test helpers and production tools

4. **Incomplete Refactoring**:
   - Previous attempts removed function definitions but left docstrings
   - This created 200+ line docstrings with no function!

## Recommendation

Go with **Option B: Fresh Start** because:
1. Cleaner to build right than fix wrong
2. Easier to audit what we're keeping
3. Less risk of leaving broken code
4. Clear git history of the refactor

## Detailed Implementation Plan

### Step 1: Create Clean Structure
```bash
mkdir -p app/agents_v2
touch app/agents_v2/__init__.py

# After EACH file creation:
make lint
```

### Step 2: Copy Good Calculation Tools
```bash
cp app/agents/calculation_tools.py app/agents_v2/
# This file is perfect as-is - all 7 tools are pure calculations
make lint
```

### Step 3: Create Test Data Tools
Create `app/agents_v2/test_data_tools.py` with only:
- `get_test_subject_data()` - From portfolio_manager.py
- `get_subject_discrepancies()` - From portfolio_manager.py
```bash
make lint
```

### Step 4: Create Clean Agents (NO mock function tools)
For each agent, create clean version with:
- Agent class with proper instructions
- Context class (Pydantic BaseModel)
- AI methods (async def with Runner.run())
- NO mock function tools

Order:
1. `portfolio_manager_v2.py` - Only include calculation_tools and test_data_tools
2. `query_analyzer_v2.py` - Only include calculation_tools
3. `data_verifier_v2.py` - Only include calculation_tools
4. `deviation_detector_v2.py` - Only include calculation_tools
5. `query_generator_v2.py` - Only include calculation_tools if needed
6. `query_tracker_v2.py` - Only include calculation_tools if needed

After EACH file:
```bash
make lint
make test-cov  # Run specific tests for that agent
```

### Step 5: Update API Endpoints
```python
# Change imports from:
from app.agents.portfolio_manager import portfolio_manager_agent

# To:
from app.agents_v2.portfolio_manager_v2 import portfolio_manager_agent
```

### Step 6: Full Testing
```bash
make check-all  # Lint + full test suite
pytest tests/test_sdk_integration.py -v  # Specific integration tests
```

### Step 7: Cleanup
Once all tests pass:
```bash
rm -rf app/agents/
mv app/agents_v2/ app/agents/
make check-all  # Final validation
```

## Why This Will Work

1. **Incremental**: Each step is small and testable
2. **Validated**: Linting after every change catches errors early
3. **Clean**: No mixing of old and new code
4. **Safe**: Original code stays until we're sure new version works
5. **Systematic**: Clear order of operations

## What We're Fixing

1. ✅ Removing 11 mock function tools that fake medical judgments
2. ✅ Keeping 7 calculation tools with their valuable documentation
3. ✅ Separating test data tools from agent logic
4. ✅ Ensuring agents use AI (Runner.run()) not mock functions
5. ✅ Clean architecture aligned with PRD vision

This approach addresses your concerns about:
- Being systematic (step-by-step plan)
- Using linting regularly (after EVERY file change)
- Avoiding the mess of partial refactoring
- Preserving valuable documentation
- Ensuring testability throughout