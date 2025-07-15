#!/usr/bin/env python3
"""Test the API response structure for comprehensive_analysis."""

import json


def test_response_structure():
    """Test different response structures to ensure proper handling."""
    
    # Test case 1: Proper PortfolioManagerOutput structure
    portfolio_output = {
        "success": True,
        "workflow_type": "comprehensive_analysis",
        "clinical_assessment": "Patient CARD003 shows normal vital signs with BP 120/80, HR 72",
        "findings": [
            "Blood pressure 120/80 mmHg is within normal range",
            "Heart rate 72 bpm is normal",
            "Hemoglobin 13.2 g/dL is within normal range",
            "Creatinine 0.9 mg/dL indicates normal kidney function"
        ],
        "severity": "minor",
        "safety_implications": "No immediate safety concerns identified",
        "recommended_actions": [
            "Continue standard monitoring",
            "Maintain current treatment plan"
        ],
        "workflow_next_steps": [
            "Schedule routine follow-up in 3 months",
            "Continue collecting vital signs per protocol"
        ],
        "priority": "low"
    }
    
    # Check if it has required fields
    required_fields = ["success", "workflow_type", "findings", "recommended_actions"]
    has_all_fields = all(key in portfolio_output for key in required_fields)
    print(f"Has all required fields: {has_all_fields}")
    
    # Test case 2: Query generator output (wrong structure)
    query_output = {
        "success": True,
        "query_type": "data_clarification",
        "generated_query": "Please clarify the data...",
        "query_priority": "urgent"
    }
    
    has_all_fields_query = all(key in query_output for key in required_fields)
    print(f"Query output has required fields: {has_all_fields_query}")
    
    # Show expected frontend structure
    print("\nExpected structure for frontend:")
    print(json.dumps(portfolio_output, indent=2))
    
    print("\nCurrent problematic structure:")
    wrapped_response = {
        "success": True,
        "workflow_type": "comprehensive_analysis",
        "results": query_output,
        "execution_time": 13.2
    }
    print(json.dumps(wrapped_response, indent=2))


if __name__ == "__main__":
    test_response_structure()