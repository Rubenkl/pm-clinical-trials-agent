#!/usr/bin/env python3
"""Test clinical workflow endpoints."""

import asyncio
import httpx
import json
import os
from datetime import datetime


BASE_URL = "http://localhost:8000/api/v1"


async def test_query_analysis():
    """Test query analysis endpoint."""
    print("\n🔍 Testing Query Analysis")
    
    payload = {
        "query_id": "TEST-001",
        "subject_id": "CARD001",
        "query_text": "Patient shows hemoglobin of 8.5 g/dL and blood pressure 180/95 mmHg. Please review.",
        "data_points": [
            {"field": "hemoglobin", "value": "8.5", "unit": "g/dL"},
            {"field": "systolic_bp", "value": "180", "unit": "mmHg"},
            {"field": "diastolic_bp", "value": "95", "unit": "mmHg"}
        ]
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{BASE_URL}/clinical/analyze-query",
            json=payload
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success - Execution time: {data.get('execution_time', 0):.2f}s")
            print(f"Analysis: {json.dumps(data.get('analysis', {}), indent=2)[:300]}...")
            return True
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
            return False


async def test_data_verification():
    """Test data verification endpoint."""
    print("\n📄 Testing Data Verification")
    
    payload = {
        "subject_id": "CARD001",
        "visit": "Week 4",
        "edc_data": {
            "hemoglobin": {"value": "12.5", "unit": "g/dL"},
            "creatinine": {"value": "1.8", "unit": "mg/dL"},
            "systolic_bp": {"value": "147", "unit": "mmHg"}
        },
        "source_data": {
            "hemoglobin": {"value": "11.2", "unit": "g/dL"},
            "creatinine": {"value": "1.84", "unit": "mg/dL"},
            "systolic_bp": {"value": "145", "unit": "mmHg"}
        }
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{BASE_URL}/clinical/verify-data",
            json=payload
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success - Execution time: {data.get('execution_time', 0):.2f}s")
            print(f"Verification: {json.dumps(data.get('verification', {}), indent=2)[:300]}...")
            return True
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
            return False


async def test_deviation_detection():
    """Test deviation detection endpoint."""
    print("\n⚠️  Testing Deviation Detection")
    
    payload = {
        "subject_id": "CARD001",
        "visit_data": {
            "visit_date": "2025-01-10",
            "scheduled_date": "2025-01-05",
            "procedures_completed": ["ECG", "Blood Draw"],
            "procedures_required": ["ECG", "Blood Draw", "ECHO"],
            "medications": ["Aspirin"]
        },
        "protocol_requirements": {
            "visit_window_days": 3,
            "required_procedures": ["ECG", "Blood Draw", "ECHO"],
            "prohibited_medications": ["Aspirin", "Warfarin"]
        }
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{BASE_URL}/clinical/detect-deviations",
            json=payload
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success - Execution time: {data.get('execution_time', 0):.2f}s")
            print(f"Compliance: {json.dumps(data.get('compliance', {}), indent=2)[:300]}...")
            return True
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
            return False


async def test_workflow_execution():
    """Test multi-agent workflow execution."""
    print("\n🔄 Testing Workflow Execution")
    
    workflows = [
        {
            "name": "Comprehensive Analysis",
            "workflow_type": "comprehensive_analysis",
            "subject_id": "CARD001",
            "input_data": {
                "clinical_concern": "Patient shows low hemoglobin (8.5 g/dL) with Stage 2 hypertension",
                "data_points": [
                    {"field": "hemoglobin", "value": "8.5"},
                    {"field": "blood_pressure", "value": "180/95"}
                ]
            }
        },
        {
            "name": "Query Resolution",
            "workflow_type": "query_resolution",
            "subject_id": "CARD002",
            "input_data": {
                "query_text": "BNP elevation to 450 pg/mL needs medical review",
                "query_id": "QUERY-002"
            }
        }
    ]
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        for workflow in workflows:
            print(f"\n  📋 Testing {workflow['name']}...")
            
            response = await client.post(
                f"{BASE_URL}/clinical/execute-workflow",
                json=workflow
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"  ✅ Success - Execution time: {data.get('execution_time', 0):.2f}s")
                print(f"  Results: {json.dumps(data.get('results', {}), indent=2)[:200]}...")
            else:
                print(f"  ❌ Failed: {response.status_code} - {response.text}")


async def test_health_check():
    """Test health check endpoint."""
    print("\n💚 Testing Health Check")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/clinical/health")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {data.get('status')}")
            print("Available endpoints:")
            for endpoint in data.get('endpoints', []):
                print(f"  - {endpoint}")
            return True
        else:
            print(f"❌ Failed: {response.status_code}")
            return False


async def verify_function_tools():
    """Verify that function tools are executing."""
    print("\n🔧 Verifying Function Tool Execution")
    
    # Test with a message that should trigger function tools
    payload = {
        "workflow_type": "comprehensive_analysis",
        "subject_id": "CARD001",
        "input_data": {
            "request": "Get test data for subject CARD001 and analyze clinical values"
        }
    }
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{BASE_URL}/clinical/execute-workflow",
            json=payload
        )
        
        if response.status_code == 200:
            data = response.json()
            results_str = json.dumps(data.get('results', {}))
            
            # Look for evidence of real data
            evidence = []
            if "CARD001" in results_str:
                evidence.append("✓ Subject ID found")
            if "hemoglobin" in results_str.lower():
                evidence.append("✓ Clinical data retrieved")
            if any(x in results_str for x in ["12.3", "147.5", "319.57", "1.84"]):
                evidence.append("✓ Specific test values found")
            if "demographics" in results_str or "age" in results_str:
                evidence.append("✓ Demographics included")
                
            print("Evidence of function tool execution:")
            for e in evidence:
                print(f"  {e}")
                
            if len(evidence) >= 2:
                print("  ✅ Function tools appear to be working!")
            else:
                print("  ⚠️  Limited evidence of function tool execution")
                
            return len(evidence) >= 2
        else:
            print(f"❌ Failed: {response.status_code}")
            return False


async def main():
    """Run all tests."""
    print("=" * 60)
    print("🧪 Clinical Workflow Endpoints Test Suite")
    print("=" * 60)
    
    # Check if API is running
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/health")
            if response.status_code != 200:
                print("❌ API is not running on localhost:8000")
                print("Please start the API with: uvicorn app.main:app --reload")
                return
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        print("Please start the API with: uvicorn app.main:app --reload")
        return
    
    # Run tests
    results = []
    
    results.append(("Health Check", await test_health_check()))
    results.append(("Query Analysis", await test_query_analysis()))
    results.append(("Data Verification", await test_data_verification()))
    results.append(("Deviation Detection", await test_deviation_detection()))
    results.append(("Workflow Execution", await test_workflow_execution()))
    results.append(("Function Tools", await verify_function_tools()))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! The clinical workflow endpoints are working correctly.")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")


if __name__ == "__main__":
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY environment variable not set")
        exit(1)
    
    print("Starting clinical workflow tests...")
    asyncio.run(main())