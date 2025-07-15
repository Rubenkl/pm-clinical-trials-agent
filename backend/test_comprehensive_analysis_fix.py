#!/usr/bin/env python3
"""Test script to debug and fix the comprehensive_analysis workflow issue."""

import asyncio
import json
import sys
from typing import Dict, Any

# Add the app directory to the Python path
sys.path.insert(0, "/mnt/d/Dropbox/Coding/GIT/pm-clinical-trials-agent/backend")

from app.agents_v2.portfolio_manager import WorkflowContext, portfolio_manager_agent
from agents import Runner


async def test_comprehensive_analysis():
    """Test the comprehensive analysis workflow directly."""
    print("Testing comprehensive_analysis workflow...")
    
    # Create the same message the endpoint sends
    workflow_type = "comprehensive_analysis"
    input_data = {
        "clinical_data": {
            "blood_pressure": "120/80",
            "heart_rate": 72,
            "hemoglobin": 13.2,
            "creatinine": 0.9
        },
        "context": "Routine Clinical Review"
    }
    
    message = f"""Execute {workflow_type} workflow:
        Description: Complete clinical data analysis with all agents
        Subject ID: CARD003
        Input Data: {json.dumps(input_data)}

        Coordinate with relevant agents and return comprehensive results."""
    
    # Run with the Portfolio Manager
    context = WorkflowContext()
    
    try:
        print("\nSending to Portfolio Manager...")
        result = await Runner.run(
            portfolio_manager_agent,
            message,
            context=context,
            max_turns=10  # Limit turns for testing
        )
        
        print(f"\nResult type: {type(result)}")
        print(f"Has final_output: {hasattr(result, 'final_output')}")
        
        if hasattr(result, "final_output"):
            print(f"Final output type: {type(result.final_output)}")
            if hasattr(result.final_output, "model_dump"):
                output = result.final_output.model_dump()
                print("\nPydantic model output:")
                print(json.dumps(output, indent=2))
            else:
                print("\nRaw final output:")
                print(result.final_output)
        
        # Check the conversation history
        if hasattr(result, "messages"):
            print(f"\nConversation had {len(result.messages)} messages")
            for i, msg in enumerate(result.messages):
                print(f"\nMessage {i+1}:")
                print(f"Role: {msg.role}")
                if hasattr(msg, "content"):
                    print(f"Content preview: {str(msg.content)[:200]}...")
                if hasattr(msg, "tool_calls") and msg.tool_calls:
                    print(f"Tool calls: {len(msg.tool_calls)} tools used")
        
    except Exception as e:
        print(f"\nError: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()


async def test_with_real_subject_data():
    """Test with actual subject data."""
    print("\n\nTesting with real subject data (CARD003)...")
    
    workflow_type = "comprehensive_analysis"
    input_data = {
        "subject_id": "CARD003",
        "context": "Analyze clinical data for CARD003"
    }
    
    message = f"""Execute {workflow_type} workflow:
        Description: Complete clinical data analysis with all agents
        Subject ID: CARD003
        Input Data: {json.dumps(input_data)}

        Analyze the clinical data for subject CARD003. Retrieve their actual data, perform a comprehensive clinical assessment, and return results in the PortfolioManagerOutput format."""
    
    context = WorkflowContext()
    
    try:
        result = await Runner.run(
            portfolio_manager_agent,
            message,
            context=context,
            max_turns=10
        )
        
        if hasattr(result.final_output, "model_dump"):
            output = result.final_output.model_dump()
            print("\nPortfolio Manager Output:")
            print(json.dumps(output, indent=2))
            
            # Verify structure matches expected format
            required_fields = ["success", "workflow_type", "findings", "recommended_actions", "workflow_next_steps"]
            missing_fields = [f for f in required_fields if f not in output]
            if missing_fields:
                print(f"\nWARNING: Missing required fields: {missing_fields}")
            else:
                print("\n✓ All required fields present")
        
    except Exception as e:
        print(f"\nError: {type(e).__name__}: {e}")


if __name__ == "__main__":
    # Run both tests
    asyncio.run(test_comprehensive_analysis())
    asyncio.run(test_with_real_subject_data())