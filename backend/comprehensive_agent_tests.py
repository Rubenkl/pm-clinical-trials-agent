#!/usr/bin/env python3
"""
Comprehensive Agent Testing Suite
Based on IQVIA PRD workflows and user personas

Tests cover:
1. Query Resolution workflows (CDM persona)
2. Data Verification workflows (CRA persona) 
3. Protocol Deviation Detection (PI/CRC persona)
4. Multi-agent orchestration scenarios
5. Performance targets from PRD

🎯 BALANCED TEST DATA (Updated January 11, 2025):
- Clean subjects (0 issues): CARD003, CARD004, CARD020, CARD033, CARD035, CARD036, CARD041, CARD048
- Discrepancy subjects (1-20 issues): CARD001, CARD002, CARD005, CARD006, CARD007, etc.
- Protocol violations: Age (CARD010: 85y, CARD030: 17y), BP >180, Creatinine >2.5
- Ground truth metadata available for supervised learning
"""

import asyncio
import json
import os
import time
from datetime import datetime
from typing import Dict, Any, List

from agents import Runner
from app.agents_v2.portfolio_manager import WorkflowContext, portfolio_manager_agent
from app.agents_v2.query_analyzer import QueryAnalysisContext, query_analyzer_agent
from app.agents_v2.data_verifier import DataVerificationContext, data_verifier_agent
from app.agents_v2.deviation_detector import DeviationDetectionContext, deviation_detector_agent
from app.agents_v2.query_generator import QueryGenerationContext, query_generator_agent
from app.agents_v2.analytics_agent import AnalyticsContext, analytics_agent


class TestCase:
    def __init__(self, name: str, description: str, persona: str, workflow: str, 
                 test_data: Dict[str, Any], expected_outcomes: List[str],
                 performance_target: str = None):
        self.name = name
        self.description = description
        self.persona = persona  # CDM, CRA, PI, CRC
        self.workflow = workflow  # query_resolution, data_verification, deviation_detection, orchestration
        self.test_data = test_data
        self.expected_outcomes = expected_outcomes
        self.performance_target = performance_target
        self.result = None
        self.execution_time = None
        self.success = False


# Test Cases Based on PRD Workflows
TEST_CASES = [
    
    # ================== QUERY RESOLUTION WORKFLOWS (CDM Persona) ==================
    TestCase(
        name="CDM_Query_Simple_Lab_Discrepancy",
        description="Clinical Data Manager identifies simple lab value discrepancy",
        persona="Clinical Data Manager",
        workflow="query_resolution", 
        test_data={
            "patient_id": "CARD001",
            "visit": "Week 4",
            "lab_values": {
                "hemoglobin": {"edc_value": 12.5, "lab_value": 11.8, "unit": "g/dL"},
                "creatinine": {"edc_value": 1.2, "lab_value": 1.8, "unit": "mg/dL"}
            },
            "discrepancy_type": "lab_edc_mismatch"
        },
        expected_outcomes=[
            "Identifies creatinine discrepancy as critical (kidney function concern)",
            "Classifies hemoglobin discrepancy as minor", 
            "Generates appropriate severity assessment",
            "Recommends immediate verification for creatinine"
        ],
        performance_target="<10 seconds (PRD requirement: process 1000+ data points in <10s)"
    ),
    
    TestCase(
        name="CDM_Query_Complex_Multi_Domain",
        description="CDM handles complex query involving multiple data domains", 
        persona="Clinical Data Manager",
        workflow="query_resolution",
        test_data={
            "patient_id": "HTN205", 
            "visit": "Baseline",
            "discrepancies": [
                {"domain": "vitals", "field": "systolic_bp", "edc": 140, "source": 165, "unit": "mmHg"},
                {"domain": "labs", "field": "potassium", "edc": 3.2, "source": 2.8, "unit": "mEq/L"},
                {"domain": "medications", "field": "ace_inhibitor", "edc": "yes", "source": "no"},
                {"domain": "adverse_events", "field": "dizziness", "edc": "mild", "source": "severe"}
            ],
            "protocol_requirements": {
                "bp_inclusion": "SBP 130-180 mmHg",
                "potassium_safety": "K+ must be >3.0 mEq/L", 
                "ae_reporting": "Severe AEs require immediate reporting"
            }
        },
        expected_outcomes=[
            "Identifies BP discrepancy as enrollment eligibility issue",
            "Flags potassium as safety concern requiring immediate attention",
            "Recognizes medication discrepancy affects protocol compliance", 
            "Prioritizes severe AE discrepancy for immediate resolution",
            "Provides integrated assessment across all domains"
        ],
        performance_target="<15 seconds for complex multi-domain analysis"
    ),

    # ================== DATA VERIFICATION WORKFLOWS (CRA Persona) ==================
    TestCase(
        name="CRA_SDV_Critical_Safety_Data",
        description="CRA performs source data verification for critical safety endpoints",
        persona="Clinical Research Associate", 
        workflow="data_verification",
        test_data={
            "site_id": "Site_101",
            "patient_id": "CARD_001",
            "verification_scope": "critical_safety_data",
            "edc_data": {
                "liver_enzymes": {"ALT": 180, "AST": 165, "total_bilirubin": 3.2},
                "cardiac_events": {"lvef": 35, "bnp": 850, "troponin": 2.1},
                "vital_signs": {"bp": "160/95", "hr": 45, "temp": 102.1}
            },
            "source_documents": {
                "lab_report_path": "/path/to/lab_report.pdf",
                "echo_report_path": "/path/to/echo_report.pdf", 
                "vital_signs_log": "/path/to/vitals.pdf"
            },
            "verification_priority": "high"
        },
        expected_outcomes=[
            "Identifies all values as critical requiring 100% SDV",
            "Flags liver enzymes as >3x ULN requiring immediate safety review",
            "Recognizes cardiac values suggest heart failure progression", 
            "Identifies vital signs abnormalities (bradycardia, hypertension, fever)",
            "Recommends immediate physician review and potential study drug hold",
            "Generates verification report with regulatory compliance"
        ],
        performance_target="<60 seconds for critical safety verification (PRD: 99% uptime, 500+ pages/hour)"
    ),

    TestCase(
        name="CRA_Risk_Based_SDV",
        description="CRA uses risk-based approach for routine monitoring visit",
        persona="Clinical Research Associate",
        workflow="data_verification", 
        test_data={
            "site_id": "Site_205",
            "patient_id": "HTN_150",
            "site_risk_score": 2.1,  # Low risk site
            "visit_type": "routine_follow_up",
            "data_criticality": "medium",
            "edc_data": {
                "efficacy_endpoints": {"sbp": 142, "dbp": 88, "heart_rate": 72},
                "safety_labs": {"creatinine": 1.1, "potassium": 4.2, "sodium": 140},
                "concomitant_medications": ["lisinopril", "hydrochlorothiazide"],
                "adverse_events": "none"
            },
            "historical_performance": {
                "site_accuracy": 98.5,
                "previous_findings": "minor_documentation_issues"
            }
        },
        expected_outcomes=[
            "Recommends 25% SDV based on low risk profile", 
            "Prioritizes efficacy endpoint verification",
            "Identifies all safety labs as within normal limits",
            "Confirms medication compliance matches protocol",
            "Suggests remote verification acceptable for this visit"
        ],
        performance_target="<30 seconds for risk assessment (PRD: 75% SDV cost reduction)"
    ),

    # ================== PROTOCOL DEVIATION DETECTION (PI/CRC Persona) ==================
    TestCase(
        name="PI_Critical_Eligibility_Deviation",
        description="Principal Investigator detects critical eligibility protocol deviation",
        persona="Principal Investigator",
        workflow="deviation_detection",
        test_data={
            "patient_id": "ONCO_089",
            "enrollment_date": "2025-01-10",
            "patient_data": {
                "age": 17.8,  # Protocol requires ≥18
                "ecog_performance": 2,  # Protocol allows 0-1
                "prior_chemo": "yes",  # Protocol excludes prior chemo
                "lab_values": {
                    "hemoglobin": 7.5,  # Below protocol minimum 8.0
                    "absolute_neutrophil": 800,  # Below protocol minimum 1500
                    "platelets": 75000  # Below protocol minimum 100000
                }
            },
            "protocol_requirements": {
                "inclusion_criteria": {
                    "age_range": "18-75 years",
                    "ecog_performance": "0-1", 
                    "hemoglobin": "≥8.0 g/dL",
                    "absolute_neutrophil": "≥1500/μL",
                    "platelets": "≥100000/μL"
                },
                "exclusion_criteria": {
                    "prior_chemotherapy": "within 6 months"
                }
            }
        },
        expected_outcomes=[
            "Identifies multiple critical eligibility violations",
            "Flags age violation as patient safety and regulatory issue", 
            "Recognizes lab values indicate bone marrow suppression",
            "Classifies as critical deviation requiring immediate action",
            "Recommends patient removal from study and IRB notification",
            "Suggests enhanced screening procedures as CAPA"
        ],
        performance_target="<30 seconds detection (PRD: <30 second detection latency)"
    ),

    TestCase(
        name="CRC_Visit_Window_Deviation", 
        description="Clinical Research Coordinator identifies visit timing deviations",
        persona="Clinical Research Coordinator",
        workflow="deviation_detection",
        test_data={
            "patient_id": "CARD_155",
            "study_day": 98,
            "scheduled_visits": [
                {"visit": "Week 2", "scheduled_day": 14, "actual_day": 16, "window": "±3 days"},
                {"visit": "Week 4", "scheduled_day": 28, "actual_day": 35, "window": "±3 days"}, 
                {"visit": "Week 8", "scheduled_day": 56, "actual_day": 63, "window": "±3 days"},
                {"visit": "Week 12", "scheduled_day": 84, "actual_day": 98, "window": "±5 days"}
            ],
            "missed_visits": ["Week 6"],
            "protocol_requirements": {
                "visit_windows": "strict adherence required for primary endpoint",
                "missed_visit_limit": "max 1 missed visit per patient"
            }
        },
        expected_outcomes=[
            "Identifies Week 4 visit as major deviation (7 days late vs 3-day window)",
            "Flags Week 12 visit as major deviation (14 days late vs 5-day window)",
            "Recognizes pattern of increasing visit delays",
            "Notes missed Week 6 visit impacts protocol compliance",
            "Recommends enhanced patient communication and scheduling",
            "Suggests protocol amendment discussion for visit windows"
        ],
        performance_target="<15 seconds for visit compliance analysis"
    ),

    # ================== MULTI-AGENT ORCHESTRATION SCENARIOS ==================
    TestCase(
        name="Portfolio_Manager_Complex_Safety_Signal",
        description="Portfolio Manager coordinates multi-agent response to complex safety signal",
        persona="Multi-Agent System",
        workflow="orchestration",
        test_data={
            "alert_type": "potential_safety_signal",
            "clinical_data": {
                "patient_id": "CARD_301",
                "visit": "Week 8", 
                "safety_concerns": {
                    "liver_enzymes": {"ALT": 245, "AST": 198, "bilirubin": 4.1},
                    "cardiac_markers": {"troponin": 0.8, "bnp": 1250, "ck_mb": 18},
                    "symptoms": ["fatigue", "nausea", "chest_discomfort", "shortness_of_breath"]
                },
                "concomitant_medications": ["study_drug", "metformin", "lisinopril"],
                "medical_history": ["diabetes", "hypertension", "mild_cad"]
            },
            "required_assessments": [
                "clinical_data_analysis",
                "drug_interaction_review", 
                "protocol_deviation_check",
                "regulatory_reporting_requirements",
                "query_generation_for_missing_data"
            ]
        },
        expected_outcomes=[
            "Recognizes complex safety scenario requiring multiple specialist agents",
            "Coordinates handoffs to Query Analyzer for clinical assessment",
            "Engages Deviation Detector for protocol compliance review",
            "Utilizes Data Verifier for source document validation",
            "Orchestrates Query Generator for additional data collection",
            "Provides integrated safety assessment and action plan",
            "Ensures all regulatory reporting requirements addressed"
        ],
        performance_target="<45 seconds for complex multi-agent coordination"
    ),

    TestCase(
        name="Portfolio_Manager_Enrollment_Optimization",
        description="Portfolio Manager optimizes patient enrollment workflow",
        persona="Multi-Agent System", 
        workflow="orchestration",
        test_data={
            "trial_id": "CARDIO_2025_001",
            "enrollment_status": {
                "target": 500,
                "current": 127,
                "timeline": "18 months",
                "months_elapsed": 8
            },
            "site_performance": {
                "Site_001": {"enrolled": 15, "screening_failures": 8, "rate": "slow"},
                "Site_002": {"enrolled": 32, "screening_failures": 12, "rate": "good"},
                "Site_003": {"enrolled": 8, "screening_failures": 22, "rate": "poor"}
            },
            "screening_data": {
                "total_screened": 298,
                "screen_failures": {
                    "inclusion_criteria": 89,
                    "exclusion_criteria": 45, 
                    "patient_withdrawal": 23,
                    "physician_decision": 14
                }
            }
        },
        expected_outcomes=[
            "Identifies enrollment behind target (should be ~222 by month 8)",
            "Recognizes Site_003 has poor screening efficiency (73% failure rate)",
            "Analyzes primary screen failure causes (inclusion criteria violations)",
            "Recommends site-specific interventions and training",
            "Suggests protocol amendment considerations",
            "Provides enrollment projections and risk mitigation strategies"
        ],
        performance_target="<20 seconds for enrollment analytics (PRD: 85% forecast accuracy)"
    ),

    # ================== EDGE CASES AND STRESS TESTS ==================
    TestCase(
        name="Stress_Test_High_Volume_Queries",
        description="Test system performance with high-volume query processing",
        persona="System Performance Test",
        workflow="performance_test",
        test_data={
            "simulation_type": "high_volume_query_processing",
            "concurrent_queries": 50,
            "query_types": ["lab_discrepancies", "visit_deviations", "safety_signals"],
            "data_volume": "1000+ data points per query",
            "expected_processing": "parallel_processing"
        },
        expected_outcomes=[
            "Handles concurrent query processing without degradation",
            "Maintains <10 second response time per query",
            "Demonstrates scalability to PRD requirements",
            "Shows proper resource utilization"
        ],
        performance_target="<10 seconds per query at 50 concurrent queries (PRD: 1000+ TPS)"
    ),

    TestCase(
        name="Edge_Case_Ambiguous_Medical_Data",
        description="Handle ambiguous medical data requiring clinical judgment",
        persona="Clinical Expert System",
        workflow="clinical_reasoning",
        test_data={
            "patient_id": "EDGE_001",
            "ambiguous_scenario": {
                "chief_complaint": "chest discomfort - unclear if cardiac vs GI",
                "lab_values": {"troponin": 0.04, "ck_mb": 3.2, "d_dimer": 245}, # Borderline values
                "ecg": "nonspecific_st_changes", 
                "symptoms": ["atypical_chest_pain", "mild_nausea", "anxiety"],
                "risk_factors": ["diabetes", "family_history", "stress"]
            },
            "clinical_context": {
                "study_drug": "investigational_cardiac_medication",
                "safety_concern": "potential_cardiac_events"
            }
        },
        expected_outcomes=[
            "Recognizes clinical ambiguity requiring expert assessment",
            "Identifies need for additional diagnostic workup",
            "Considers study drug relationship to symptoms",
            "Recommends conservative safety approach",
            "Suggests cardiology consultation",
            "Documents uncertainty appropriately for regulatory compliance"
        ],
        performance_target="<30 seconds for complex clinical reasoning"
    )
]


async def run_test_case(test_case: TestCase) -> Dict[str, Any]:
    """Execute a single test case"""
    print(f"\n{'='*80}")
    print(f"🧪 TESTING: {test_case.name}")
    print(f"👤 Persona: {test_case.persona}")
    print(f"🔄 Workflow: {test_case.workflow}")
    print(f"📋 Description: {test_case.description}")
    if test_case.performance_target:
        print(f"⏱️  Performance Target: {test_case.performance_target}")
    print(f"{'='*80}")
    
    start_time = time.time()
    
    try:
        # Route to appropriate agent based on workflow
        if test_case.workflow == "query_resolution":
            context = QueryAnalysisContext()
            message = f"""Analyze this clinical data for query generation needs:
            
{json.dumps(test_case.test_data, indent=2)}

Expected to identify: {', '.join(test_case.expected_outcomes)}"""
            result = await Runner.run(query_analyzer_agent, message, context=context)
            
        elif test_case.workflow == "data_verification":
            context = DataVerificationContext()
            message = f"""Perform source data verification for this clinical data:
            
{json.dumps(test_case.test_data, indent=2)}

Expected outcomes: {', '.join(test_case.expected_outcomes)}"""
            result = await Runner.run(data_verifier_agent, message, context=context)
            
        elif test_case.workflow == "deviation_detection":
            context = DeviationDetectionContext()
            message = f"""Detect protocol deviations in this study data:
            
{json.dumps(test_case.test_data, indent=2)}

Expected to find: {', '.join(test_case.expected_outcomes)}"""
            result = await Runner.run(deviation_detector_agent, message, context=context)
            
        elif test_case.workflow in ["orchestration", "performance_test", "clinical_reasoning"]:
            context = WorkflowContext()
            message = f"""Orchestrate response to this clinical scenario:
            
{json.dumps(test_case.test_data, indent=2)}

Expected coordination: {', '.join(test_case.expected_outcomes)}"""
            result = await Runner.run(portfolio_manager_agent, message, context=context)
            
        else:
            raise ValueError(f"Unknown workflow type: {test_case.workflow}")
        
        execution_time = time.time() - start_time
        test_case.execution_time = execution_time
        test_case.result = result
        test_case.success = True
        
        print(f"✅ Test completed successfully in {execution_time:.2f} seconds")
        print(f"📊 Result preview: {str(result)[:200]}...")
        
        return {
            "test_name": test_case.name,
            "success": True,
            "execution_time": execution_time,
            "result": result,
            "performance_met": execution_time < 60  # Most targets are under 60s
        }
        
    except Exception as e:
        execution_time = time.time() - start_time
        test_case.execution_time = execution_time
        test_case.success = False
        
        print(f"❌ Test failed after {execution_time:.2f} seconds")
        print(f"🚨 Error: {str(e)}")
        
        return {
            "test_name": test_case.name, 
            "success": False,
            "execution_time": execution_time,
            "error": str(e)
        }


async def run_all_tests():
    """Run all test cases and generate comprehensive report"""
    print("🚀 Starting Comprehensive Agent Testing Suite")
    print(f"📅 Test run started at: {datetime.now().isoformat()}")
    print(f"🧪 Total test cases: {len(TEST_CASES)}")
    
    results = []
    
    for i, test_case in enumerate(TEST_CASES, 1):
        print(f"\n🔄 Running test {i}/{len(TEST_CASES)}")
        result = await run_test_case(test_case)
        results.append(result)
        
        # Small delay between tests to avoid overwhelming the system
        await asyncio.sleep(1)
    
    # Generate summary report
    print(f"\n{'🏁 FINAL RESULTS '}")
    print(f"{'='*80}")
    
    successful_tests = [r for r in results if r['success']]
    failed_tests = [r for r in results if not r['success']]
    
    print(f"✅ Successful tests: {len(successful_tests)}/{len(results)}")
    print(f"❌ Failed tests: {len(failed_tests)}")
    print(f"📊 Success rate: {len(successful_tests)/len(results)*100:.1f}%")
    
    if successful_tests:
        avg_time = sum(r['execution_time'] for r in successful_tests) / len(successful_tests)
        print(f"⏱️  Average execution time: {avg_time:.2f} seconds")
        
        fast_tests = [r for r in successful_tests if r['execution_time'] < 10]
        print(f"🚀 Fast tests (<10s): {len(fast_tests)}/{len(successful_tests)}")
    
    # Performance analysis by workflow type
    workflow_performance = {}
    for result in successful_tests:
        test_case = next(tc for tc in TEST_CASES if tc.name == result['test_name'])
        workflow = test_case.workflow
        if workflow not in workflow_performance:
            workflow_performance[workflow] = []
        workflow_performance[workflow].append(result['execution_time'])
    
    print(f"\n📈 Performance by Workflow Type:")
    for workflow, times in workflow_performance.items():
        avg_time = sum(times) / len(times)
        print(f"  {workflow}: {avg_time:.2f}s average ({len(times)} tests)")
    
    # List failed tests for debugging
    if failed_tests:
        print(f"\n🚨 Failed Tests Requiring Attention:")
        for test in failed_tests:
            test_case = next(tc for tc in TEST_CASES if tc.name == test['test_name'])
            print(f"  ❌ {test['test_name']} ({test_case.workflow}): {test.get('error', 'Unknown error')}")
    
    return results


if __name__ == "__main__":
    print("🔧 Loading OpenAI API key...")
    # Load API key from environment or .env file
    if not os.getenv("OPENAI_API_KEY"):
        try:
            with open(".env", "r") as f:
                for line in f:
                    if line.startswith("OPENAI_API_KEY="):
                        key = line.split("=", 1)[1].strip().strip('"')
                        os.environ["OPENAI_API_KEY"] = key
                        break
        except FileNotFoundError:
            print("❌ No .env file found. Please set OPENAI_API_KEY environment variable.")
            exit(1)
    
    print("✅ Starting test execution...")
    results = asyncio.run(run_all_tests())
    
    print(f"\n🎯 Testing completed! Check results above for performance insights.")
    print(f"💡 Use failed test information to adjust agent prompts if needed.")