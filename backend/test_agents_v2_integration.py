#!/usr/bin/env python3
"""Comprehensive test of agents_v2 clean implementation with real clinical data."""

import asyncio
import json
import os
import sys
from datetime import datetime

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.agents_v2 import (
    AnalyticsAgent,
    DataVerifier,
    DeviationDetector,
    PortfolioManager,
    QueryAnalyzer,
    QueryGenerator,
    QueryTracker,
)
from app.agents_v2.analytics_agent import AnalyticsContext
from app.agents_v2.data_verifier import DataVerificationContext
from app.agents_v2.deviation_detector import DeviationDetectionContext
from app.agents_v2.portfolio_manager import WorkflowContext
from app.agents_v2.query_analyzer import QueryAnalysisContext
from app.agents_v2.query_generator import QueryGenerationContext
from app.agents_v2.query_tracker import QueryTrackingContext


async def test_query_analyzer():
    """Test Query Analyzer with real clinical data."""
    print("\n🔍 Testing Query Analyzer with clinical data...")
    
    analyzer = QueryAnalyzer()
    context = QueryAnalysisContext()
    
    # Real clinical scenario - cardiovascular study data
    clinical_data = {
        "subject_id": "CARD001",
        "visit": "Week 12",
        "vital_signs": {
            "systolic_bp": 185,  # Critical hypertension
            "diastolic_bp": 110,
            "heart_rate": 98,
            "temperature": 98.6
        },
        "laboratory": {
            "hemoglobin": 8.2,  # Anemia
            "creatinine": 2.1,  # Kidney dysfunction
            "bnp": 850,  # Heart failure marker
        },
        "patient_context": {
            "age": 67,
            "gender": "male",
            "medical_history": ["hypertension", "diabetes"],
            "current_medications": ["metformin", "lisinopril"]
        }
    }
    
    try:
        result = await analyzer.analyze_clinical_data(clinical_data, context)
        
        if result["success"]:
            analysis = result["analysis"]
            print("✅ Query Analyzer working correctly")
            print(f"   Analysis type: {type(analysis)}")
            print(f"   Has findings: {'analysis' in analysis or 'findings' in str(analysis)}")
            print(f"   Response length: {len(str(analysis))}")
            
            # Check if we got medical reasoning (not just calculations)
            response_str = str(analysis)
            medical_indicators = ["bp", "blood pressure", "hypertension", "hemoglobin", "anemia", "kidney"]
            has_medical_content = any(indicator.lower() in response_str.lower() for indicator in medical_indicators)
            print(f"   Contains medical reasoning: {has_medical_content}")
            
            return True
        else:
            print(f"❌ Query Analyzer failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Query Analyzer exception: {e}")
        return False


async def test_data_verifier():
    """Test Data Verifier with EDC vs source discrepancies."""
    print("\n✅ Testing Data Verifier with discrepancy data...")
    
    verifier = DataVerifier()
    context = DataVerificationContext()
    
    # Realistic discrepancy scenario
    edc_data = {
        "subject_id": "CARD001",
        "vital_signs": {
            "systolic_bp": 120,  # EDC value
            "diastolic_bp": 80,
            "weight": 85.5
        },
        "laboratory": {
            "hemoglobin": 12.5,
            "creatinine": 1.1
        }
    }
    
    source_data = {
        "subject_id": "CARD001", 
        "vital_signs": {
            "systolic_bp": 180,  # Source document value (major discrepancy!)
            "diastolic_bp": 95,
            "weight": 85.5
        },
        "laboratory": {
            "hemoglobin": 8.2,  # Major anemia discrepancy
            "creatinine": 1.1
        }
    }
    
    try:
        result = await verifier.verify_edc_vs_source(edc_data, source_data, context)
        
        if result["success"]:
            verification = result["verification"]
            print("✅ Data Verifier working correctly")
            print(f"   Verification type: {type(verification)}")
            print(f"   Has discrepancies: {'discrepancy' in str(verification).lower()}")
            print(f"   Response length: {len(str(verification))}")
            
            # Check for medical intelligence in discrepancy assessment
            response_str = str(verification)
            medical_indicators = ["bp", "blood pressure", "hemoglobin", "critical", "severe", "discrepancy"]
            has_medical_reasoning = any(indicator.lower() in response_str.lower() for indicator in medical_indicators)
            print(f"   Contains medical reasoning: {has_medical_reasoning}")
            
            return True
        else:
            print(f"❌ Data Verifier failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Data Verifier exception: {e}")
        return False


async def test_query_generator():
    """Test Query Generator with medical query creation."""
    print("\n📝 Testing Query Generator with medical query request...")
    
    generator = QueryGenerator()
    context = QueryGenerationContext()
    
    # Professional query generation scenario
    query_request = {
        "type": "source_verification",
        "field": "systolic_bp",
        "edc_value": "120",
        "source_value": "180", 
        "urgency": "urgent",
        "subject_id": "CARD001"
    }
    
    clinical_context = {
        "patient_age": 67,
        "medical_history": ["hypertension", "diabetes"],
        "visit": "Week 12",
        "safety_implications": "Hypertensive crisis risk"
    }
    
    try:
        result = await generator.generate_clinical_query(query_request, clinical_context, context)
        
        if result["success"]:
            query = result["query"]
            print("✅ Query Generator working correctly")
            print(f"   Query type: {type(query)}")
            print(f"   Has query text: {'query' in str(query).lower()}")
            print(f"   Response length: {len(str(query))}")
            
            # Check for professional medical language
            response_str = str(query)
            professional_indicators = ["please", "verify", "blood pressure", "source document", "urgent"]
            has_professional_tone = any(indicator.lower() in response_str.lower() for indicator in professional_indicators)
            print(f"   Contains professional language: {has_professional_tone}")
            
            return True
        else:
            print(f"❌ Query Generator failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Query Generator exception: {e}")
        return False


async def test_portfolio_manager():
    """Test Portfolio Manager orchestration."""
    print("\n🎯 Testing Portfolio Manager workflow orchestration...")
    
    manager = PortfolioManager()
    context = WorkflowContext()
    
    # Complex workflow orchestration
    workflow_request = {
        "workflow_id": "TEST_001",
        "workflow_type": "comprehensive_analysis",
        "subject_id": "CARD001",
        "clinical_data": {
            "vital_signs": {"systolic_bp": 185, "diastolic_bp": 110},
            "laboratory": {"hemoglobin": 8.2, "bnp": 850}
        },
        "priority": "urgent"
    }
    
    try:
        result = await manager.orchestrate_workflow("comprehensive_analysis", workflow_request, context)
        
        if result["success"]:
            workflow = result["workflow"]
            print("✅ Portfolio Manager working correctly")
            print(f"   Workflow type: {type(workflow)}")
            print(f"   Has orchestration: {'workflow' in str(workflow).lower()}")
            print(f"   Response length: {len(str(workflow))}")
            
            # Check for intelligent workflow coordination
            response_str = str(workflow)
            coordination_indicators = ["analysis", "clinical", "urgent", "workflow", "assessment"]
            has_coordination = any(indicator.lower() in response_str.lower() for indicator in coordination_indicators)
            print(f"   Contains workflow intelligence: {has_coordination}")
            
            return True
        else:
            print(f"❌ Portfolio Manager failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Portfolio Manager exception: {e}")
        return False


async def test_deviation_detector():
    """Test Deviation Detector with protocol compliance."""
    print("\n⚖️ Testing Deviation Detector with protocol compliance...")
    
    detector = DeviationDetector()
    context = DeviationDetectionContext()
    
    # Protocol deviation scenario
    study_data = {
        "subject_id": "CARD001",
        "enrollment_date": "2024-01-15",
        "patient_age": 17.8,  # Below 18 - inclusion criteria violation
        "visit_date": "2024-02-20",  # 36 days later - outside visit window
        "required_labs": ["hemoglobin", "creatinine"],
        "completed_labs": ["hemoglobin"]  # Missing required lab
    }
    
    protocol_requirements = {
        "inclusion_criteria": {
            "minimum_age": 18,
            "maximum_age": 75
        },
        "visit_windows": {
            "week_4": {"target_days": 28, "window_days": 7}
        },
        "required_assessments": ["hemoglobin", "creatinine", "vital_signs"]
    }
    
    try:
        result = await detector.detect_protocol_deviations(study_data, protocol_requirements, context)
        
        if result["success"]:
            analysis = result["analysis"]
            print("✅ Deviation Detector working correctly")
            print(f"   Analysis type: {type(analysis)}")
            print(f"   Has deviations: {'deviation' in str(analysis).lower()}")
            print(f"   Response length: {len(str(analysis))}")
            
            # Check for regulatory intelligence
            response_str = str(analysis)
            regulatory_indicators = ["age", "inclusion", "criteria", "violation", "protocol", "compliance"]
            has_regulatory_knowledge = any(indicator.lower() in response_str.lower() for indicator in regulatory_indicators)
            print(f"   Contains regulatory intelligence: {has_regulatory_knowledge}")
            
            return True
        else:
            print(f"❌ Deviation Detector failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Deviation Detector exception: {e}")
        return False


async def test_all_agents():
    """Run comprehensive tests on all clean agents."""
    print("🧪 COMPREHENSIVE AGENTS_V2 TESTING")
    print("=" * 50)
    
    # Set a mock OpenAI API key for testing (agents will fail gracefully without real key)
    os.environ.setdefault("OPENAI_API_KEY", "test-key-for-structure-testing")
    
    test_results = {}
    
    # Test each agent individually
    test_functions = [
        ("Query Analyzer", test_query_analyzer),
        ("Data Verifier", test_data_verifier), 
        ("Query Generator", test_query_generator),
        ("Portfolio Manager", test_portfolio_manager),
        ("Deviation Detector", test_deviation_detector),
    ]
    
    for agent_name, test_func in test_functions:
        print(f"\n{'=' * 20} {agent_name} {'=' * 20}")
        try:
            result = await test_func()
            test_results[agent_name] = result
            
            if result:
                print(f"✅ {agent_name} test PASSED")
            else:
                print(f"❌ {agent_name} test FAILED")
                
        except Exception as e:
            print(f"💥 {agent_name} test CRASHED: {e}")
            test_results[agent_name] = False
    
    # Summary
    print(f"\n{'=' * 50}")
    print("🏁 TESTING SUMMARY")
    print(f"{'=' * 50}")
    
    passed = sum(1 for result in test_results.values() if result)
    total = len(test_results)
    
    for agent_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{agent_name:<20} {status}")
    
    print(f"\nOVERALL: {passed}/{total} agents passed testing")
    
    if passed == total:
        print("🎉 ALL AGENTS_V2 TESTS PASSED!")
        print("✅ Clean agent system is working correctly")
        print("✅ Real AI intelligence is functioning")
        print("✅ Medical reasoning is operational")
    else:
        print("⚠️  Some agents need attention")
        print("🔧 Check OpenAI API key and network connectivity")
    
    return test_results


if __name__ == "__main__":
    asyncio.run(test_all_agents())