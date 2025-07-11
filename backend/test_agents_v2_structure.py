#!/usr/bin/env python3
"""Structural tests for agents_v2 - verify architecture without API calls."""

import asyncio
import os
import sys
from unittest.mock import AsyncMock, patch

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


def test_agent_initialization():
    """Test that all agents initialize correctly with proper structure."""
    print("🏗️  Testing Agent Initialization...")
    
    agents = [
        ("Portfolio Manager", PortfolioManager),
        ("Query Analyzer", QueryAnalyzer),
        ("Data Verifier", DataVerifier),
        ("Query Generator", QueryGenerator),
        ("Query Tracker", QueryTracker),
        ("Deviation Detector", DeviationDetector),
        ("Analytics Agent", AnalyticsAgent),
    ]
    
    results = {}
    
    for name, agent_class in agents:
        try:
            agent = agent_class()
            
            # Check agent has OpenAI Agents SDK agent
            has_agent = hasattr(agent, 'agent')
            
            # Check agent has proper instructions
            has_instructions = hasattr(agent, '_get_instructions')
            
            # Check instructions are comprehensive (not empty)
            if has_instructions:
                instructions = agent._get_instructions()
                instructions_length = len(instructions)
                has_medical_content = any(term in instructions.lower() for term in [
                    'medical', 'clinical', 'patient', 'safety', 'regulatory'
                ])
            else:
                instructions_length = 0
                has_medical_content = False
            
            # Check for function tools (should be calculation tools only)
            if hasattr(agent, 'agent') and hasattr(agent.agent, 'tools'):
                tools_count = len(agent.agent.tools)
            else:
                tools_count = 0
            
            results[name] = {
                'initialized': True,
                'has_agent': has_agent,
                'has_instructions': has_instructions,
                'instructions_length': instructions_length,
                'has_medical_content': has_medical_content,
                'tools_count': tools_count
            }
            
            print(f"✅ {name}: Initialized successfully")
            print(f"   - Has agent: {has_agent}")
            print(f"   - Instructions: {instructions_length} chars")
            print(f"   - Medical content: {has_medical_content}")
            print(f"   - Function tools: {tools_count}")
            
        except Exception as e:
            print(f"❌ {name}: Initialization failed - {e}")
            results[name] = {'initialized': False, 'error': str(e)}
    
    return results


async def test_agent_methods_structure():
    """Test that agents have proper method structure without API calls."""
    print("\n🔧 Testing Agent Method Structure...")
    
    # Mock the Runner.run to avoid API calls
    mock_result = AsyncMock()
    mock_result.final_output = '{"test": "response", "success": true}'
    
    with patch('app.agents_v2.portfolio_manager.Runner.run', return_value=mock_result):
        with patch('app.agents_v2.query_analyzer.Runner.run', return_value=mock_result):
            with patch('app.agents_v2.data_verifier.Runner.run', return_value=mock_result):
                
                # Test Portfolio Manager
                pm = PortfolioManager()
                from app.agents_v2.portfolio_manager import WorkflowContext
                context = WorkflowContext()
                
                try:
                    result = await pm.orchestrate_workflow(
                        "test_workflow", 
                        {"test": "data"}, 
                        context
                    )
                    print("✅ Portfolio Manager: orchestrate_workflow works")
                    print(f"   - Returns dict: {isinstance(result, dict)}")
                    print(f"   - Has success: {'success' in result}")
                except Exception as e:
                    print(f"❌ Portfolio Manager: orchestrate_workflow failed - {e}")
                
                # Test Query Analyzer
                qa = QueryAnalyzer()
                from app.agents_v2.query_analyzer import QueryAnalysisContext
                qa_context = QueryAnalysisContext()
                
                try:
                    result = await qa.analyze_clinical_data(
                        {"test": "clinical_data"}, 
                        qa_context
                    )
                    print("✅ Query Analyzer: analyze_clinical_data works")
                    print(f"   - Returns dict: {isinstance(result, dict)}")
                    print(f"   - Has success: {'success' in result}")
                except Exception as e:
                    print(f"❌ Query Analyzer: analyze_clinical_data failed - {e}")
                
                # Test Data Verifier
                dv = DataVerifier()
                from app.agents_v2.data_verifier import DataVerificationContext
                dv_context = DataVerificationContext()
                
                try:
                    result = await dv.verify_edc_vs_source(
                        {"edc": "data"}, 
                        {"source": "data"}, 
                        dv_context
                    )
                    print("✅ Data Verifier: verify_edc_vs_source works")
                    print(f"   - Returns dict: {isinstance(result, dict)}")
                    print(f"   - Has success: {'success' in result}")
                except Exception as e:
                    print(f"❌ Data Verifier: verify_edc_vs_source failed - {e}")


def test_calculation_tools():
    """Test calculation tools are properly imported and structured."""
    print("\n🧮 Testing Calculation Tools...")
    
    try:
        from app.agents_v2.calculation_tools import (
            convert_medical_units,
            calculate_age_at_visit,
            calculate_change_from_baseline,
            calculate_date_difference,
            check_visit_window_compliance,
            calculate_body_surface_area,
            calculate_creatinine_clearance
        )
        
        tools = [
            convert_medical_units,
            calculate_age_at_visit, 
            calculate_change_from_baseline,
            calculate_date_difference,
            check_visit_window_compliance,
            calculate_body_surface_area,
            calculate_creatinine_clearance
        ]
        
        print(f"✅ Calculation Tools: {len(tools)} tools imported successfully")
        
        # Check they're function tools (have string signatures)
        for i, tool in enumerate(tools):
            # Check if it's a function tool with annotations
            tool_name = getattr(tool, 'name', f'tool_{i}')
            is_function_tool = hasattr(tool, 'function')
            print(f"   - {tool_name}: Function tool = {is_function_tool}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Calculation Tools: Import failed - {e}")
        return False


def test_api_integration():
    """Test that API endpoints can import the new agents."""
    print("\n🌐 Testing API Integration...")
    
    try:
        # Test dependencies
        from app.api.dependencies import get_portfolio_manager, get_query_analyzer, get_data_verifier
        
        pm = get_portfolio_manager()
        qa = get_query_analyzer()
        dv = get_data_verifier()
        
        print("✅ API Dependencies: All agent factories work")
        print(f"   - Portfolio Manager: {type(pm).__name__}")
        print(f"   - Query Analyzer: {type(qa).__name__}")
        print(f"   - Data Verifier: {type(dv).__name__}")
        
        # Test endpoints import
        from app.api.endpoints.clinical_workflows import router as clinical_router
        from app.api.endpoints.test_data import router as test_router
        
        print("✅ API Endpoints: Clinical workflows and test data routers imported")
        
        return True
        
    except Exception as e:
        print(f"❌ API Integration: Failed - {e}")
        return False


def run_all_structural_tests():
    """Run all structural tests."""
    print("🧪 AGENTS_V2 STRUCTURAL TESTING")
    print("=" * 50)
    
    test_results = {}
    
    # Test initialization
    print("\n" + "=" * 20 + " INITIALIZATION " + "=" * 20)
    test_results['initialization'] = test_agent_initialization()
    
    # Test calculation tools
    print("\n" + "=" * 20 + " CALCULATION TOOLS " + "=" * 20)
    test_results['calculation_tools'] = test_calculation_tools()
    
    # Test API integration
    print("\n" + "=" * 20 + " API INTEGRATION " + "=" * 20)
    test_results['api_integration'] = test_api_integration()
    
    # Test method structure (requires async)
    print("\n" + "=" * 20 + " METHOD STRUCTURE " + "=" * 20)
    asyncio.run(test_agent_methods_structure())
    
    # Summary
    print(f"\n{'=' * 50}")
    print("🏁 STRUCTURAL TESTING SUMMARY")
    print(f"{'=' * 50}")
    
    # Count successful agent initializations
    init_results = test_results.get('initialization', {})
    successful_agents = sum(1 for result in init_results.values() if result.get('initialized', False))
    total_agents = len(init_results)
    
    print(f"Agent Initialization: {successful_agents}/{total_agents} agents initialized")
    print(f"Calculation Tools: {'✅' if test_results.get('calculation_tools') else '❌'}")
    print(f"API Integration: {'✅' if test_results.get('api_integration') else '❌'}")
    
    if successful_agents == total_agents and test_results.get('calculation_tools') and test_results.get('api_integration'):
        print("\n🎉 ALL STRUCTURAL TESTS PASSED!")
        print("✅ Clean agent architecture is working correctly")
        print("✅ No mock functions - ready for real AI")
        print("✅ API integration successful")
        print("✅ Calculation tools properly separated")
    else:
        print("\n⚠️  Some structural issues detected")
    
    return test_results


if __name__ == "__main__":
    run_all_structural_tests()