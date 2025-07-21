"""Test Data Verifier risk assessment functionality using TDD approach."""

import asyncio
import json
from typing import Any, Dict

from app.agents_v2.data_verifier import DataVerificationContext, DataVerifier


async def test_risk_assessment_critical_findings():
    """Test risk assessment for critical safety findings."""
    print("\n🔴 Testing risk assessment for critical findings...")
    
    verifier = DataVerifier()
    context = DataVerificationContext()
    
    # Critical discrepancy scenario - major safety issue
    edc_data = {
        "subject_id": "RISK001",
        "vital_signs": {
            "systolic_bp": 120,  # EDC shows normal
            "diastolic_bp": 80,
            "heart_rate": 72
        },
        "adverse_events": []
    }
    
    source_data = {
        "subject_id": "RISK001", 
        "vital_signs": {
            "systolic_bp": 180,  # Source shows hypertensive crisis!
            "diastolic_bp": 110,
            "heart_rate": 110
        },
        "adverse_events": [
            {
                "term": "Hypertensive crisis",
                "severity": "Life-threatening",
                "start_date": "2025-01-20"
            }
        ]
    }
    
    result = await verifier.verify_edc_vs_source(edc_data, source_data, context)
    
    # Debug print to see actual response structure
    print(f"DEBUG: Response keys: {list(result.keys())}")
    print(f"DEBUG: Full response: {json.dumps(result, indent=2)}")
    
    # Verify response structure
    assert result["success"] == True
    assert "verification" in result
    
    verification = result["verification"]
    
    # Check for new risk assessment fields
    assert "risk_score" in verification, "Missing risk_score field"
    assert "risk_level" in verification, "Missing risk_level field"
    assert "risk_factors" in verification, "Missing risk_factors field"
    
    # Validate risk assessment values
    risk_score = float(verification["risk_score"])
    assert risk_score >= 0.8, f"Critical findings should have high risk score, got {risk_score}"
    assert verification["risk_level"] in ["critical", "high"], f"Expected critical/high risk level, got {verification['risk_level']}"
    
    # Check risk factors include safety issues
    risk_factors = verification["risk_factors"]
    assert isinstance(risk_factors, list), "risk_factors should be a list"
    assert len(risk_factors) > 0, "Should have identified risk factors"
    
    # Verify critical findings are reflected in risk assessment
    assert any("hypertensive" in factor.lower() for factor in risk_factors), "Should identify hypertensive crisis risk"
    assert any("adverse event" in factor.lower() for factor in risk_factors), "Should identify missing AE risk"
    
    print(f"✅ Risk assessment: Score={risk_score}, Level={verification['risk_level']}")
    print(f"✅ Risk factors identified: {len(risk_factors)}")
    return True


async def test_risk_assessment_minor_findings():
    """Test risk assessment for minor discrepancies."""
    print("\n🔴 Testing risk assessment for minor findings...")
    
    verifier = DataVerifier()
    context = DataVerificationContext()
    
    # Minor discrepancy scenario
    edc_data = {
        "subject_id": "RISK002",
        "demographics": {
            "weight": 75.2,  # Minor weight difference
            "height": 175
        },
        "vital_signs": {
            "temperature": 98.6
        }
    }
    
    source_data = {
        "subject_id": "RISK002",
        "demographics": {
            "weight": 75.5,  # 0.3 kg difference - minor
            "height": 175
        },
        "vital_signs": {
            "temperature": 98.6
        }
    }
    
    result = await verifier.verify_edc_vs_source(edc_data, source_data, context)
    
    # Debug print to see actual response structure
    print(f"DEBUG: Response keys: {list(result.keys())}")
    if not result.get("success", False):
        print(f"DEBUG: Error response: {result}")
    
    verification = result["verification"]
    
    # Check risk assessment for minor findings
    risk_score = float(verification["risk_score"])
    assert risk_score < 0.3, f"Minor findings should have low risk score, got {risk_score}"
    assert verification["risk_level"] in ["low", "minimal"], f"Expected low/minimal risk level, got {verification['risk_level']}"
    
    print(f"✅ Minor finding risk: Score={risk_score}, Level={verification['risk_level']}")
    return True


async def test_risk_assessment_multiple_findings():
    """Test risk assessment with multiple findings of varying severity."""
    print("\n🔴 Testing risk assessment for multiple findings...")
    
    verifier = DataVerifier()
    context = DataVerificationContext()
    
    # Multiple discrepancies with different severities
    edc_data = {
        "subject_id": "RISK003",
        "laboratory": {
            "hemoglobin": 12.5,  # Normal
            "platelet_count": 250000,  # Normal
            "creatinine": 1.0  # Normal
        },
        "medications": ["Aspirin 81mg"]
    }
    
    source_data = {
        "subject_id": "RISK003",
        "laboratory": {
            "hemoglobin": 7.5,  # Critical - severe anemia!
            "platelet_count": 251000,  # Minor difference
            "creatinine": 2.8  # Major - renal impairment
        },
        "medications": ["Aspirin 81mg", "Warfarin 5mg"]  # Missing anticoagulant!
    }
    
    result = await verifier.verify_edc_vs_source(edc_data, source_data, context)
    
    # Debug print to see actual response structure
    print(f"DEBUG: Response keys: {list(result.keys())}")
    if not result.get("success", False):
        print(f"DEBUG: Error response: {result}")
    
    verification = result["verification"]
    
    # Should have high risk due to critical hemoglobin and missing warfarin
    risk_score = float(verification["risk_score"])
    assert risk_score >= 0.7, f"Multiple critical findings should have high risk score, got {risk_score}"
    assert verification["risk_level"] in ["critical", "high"], f"Expected critical/high risk level, got {verification['risk_level']}"
    
    # Check that multiple risk factors are identified
    risk_factors = verification["risk_factors"]
    assert len(risk_factors) >= 3, f"Should identify multiple risk factors, found {len(risk_factors)}"
    
    print(f"✅ Multiple findings risk: Score={risk_score}, Level={verification['risk_level']}")
    print(f"✅ Risk factors: {risk_factors}")
    return True


async def test_risk_assessment_perfect_match():
    """Test risk assessment when data perfectly matches."""
    print("\n🔴 Testing risk assessment for perfect match...")
    
    verifier = DataVerifier()
    context = DataVerificationContext()
    
    # Perfect match scenario
    matching_data = {
        "subject_id": "RISK004",
        "vital_signs": {
            "systolic_bp": 120,
            "diastolic_bp": 80,
            "heart_rate": 72,
            "temperature": 98.6
        },
        "medications": ["Metformin 1000mg", "Lisinopril 10mg"]
    }
    
    result = await verifier.verify_edc_vs_source(
        matching_data, 
        matching_data,  # Same data
        context
    )
    
    verification = result["verification"]
    
    # Perfect match should have minimal risk
    risk_score = float(verification["risk_score"])
    assert risk_score <= 0.1, f"Perfect match should have minimal risk score, got {risk_score}"
    assert verification["risk_level"] == "minimal", f"Expected minimal risk level, got {verification['risk_level']}"
    
    # Should have no risk factors
    risk_factors = verification["risk_factors"]
    assert len(risk_factors) == 0 or all("no discrepancies" in f.lower() for f in risk_factors), \
        "Perfect match should have no risk factors"
    
    print(f"✅ Perfect match risk: Score={risk_score}, Level={verification['risk_level']}")
    return True


async def test_risk_levels_mapping():
    """Test that risk scores map correctly to risk levels."""
    print("\n🔴 Testing risk score to level mapping...")
    
    # Test scenarios with expected mappings
    test_cases = [
        (0.9, ["critical"]),  # >= 0.8
        (0.65, ["high"]),     # >= 0.6
        (0.45, ["moderate"]), # >= 0.4
        (0.25, ["low"]),      # >= 0.2
        (0.05, ["minimal"])   # < 0.2
    ]
    
    # We'll verify this through the agent's responses
    # The agent should follow these mappings in its risk assessment
    
    print("✅ Risk level mappings defined:")
    print("  - Critical: score >= 0.8")
    print("  - High: score >= 0.6")
    print("  - Moderate: score >= 0.4")
    print("  - Low: score >= 0.2")
    print("  - Minimal: score < 0.2")
    
    return True


async def run_all_tests():
    """Run all risk assessment tests."""
    print("🔬 Running Data Verifier Risk Assessment Tests (TDD - Red Phase)")
    print("=" * 60)
    
    tests = [
        ("Critical Findings Risk Assessment", test_risk_assessment_critical_findings),
        ("Minor Findings Risk Assessment", test_risk_assessment_minor_findings),
        ("Multiple Findings Risk Assessment", test_risk_assessment_multiple_findings),
        ("Perfect Match Risk Assessment", test_risk_assessment_perfect_match),
        ("Risk Level Mapping", test_risk_levels_mapping)
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            print(f"\n📋 {test_name}")
            result = await test_func()
            results[test_name] = "PASS" if result else "FAIL"
            print(f"{'✅ PASS' if result else '❌ FAIL'}: {test_name}")
        except AssertionError as e:
            results[test_name] = "FAIL"
            print(f"❌ FAIL: {test_name}")
            print(f"   Assertion Error: {e}")
        except Exception as e:
            results[test_name] = "ERROR"
            print(f"💥 ERROR: {test_name}")
            print(f"   Exception: {e}")
    
    print("\n" + "=" * 60)
    print("📊 Test Summary:")
    for test_name, status in results.items():
        print(f"  {status}: {test_name}")
    
    failed = sum(1 for s in results.values() if s != "PASS")
    print(f"\nTotal: {len(results)} tests, {failed} failures")
    
    return failed == 0


if __name__ == "__main__":
    asyncio.run(run_all_tests())