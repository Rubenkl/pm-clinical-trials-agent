"""
Critical verification tests to ensure agents are actually working correctly.
This tests actual function tool usage and clinical reasoning capabilities.
"""

import pytest
import json
import asyncio
from datetime import datetime
from typing import Dict, Any, List

from app.agents.query_generator import QueryGenerator, generate_clinical_query, validate_clinical_query
from app.agents.data_verifier import DataVerifier, cross_system_verification
from app.agents.deviation_detector import DeviationDetector, detect_protocol_deviations
from app.agents.analytics_agent import AnalyticsAgent, generate_enrollment_trends, generate_data_quality_trends
from app.agents.query_tracker import QueryTracker, track_clinical_query, update_query_status


class TestCriticalAgentFunctionality:
    """Critical tests to verify agents are actually working, not just returning mock data."""
    
    def test_query_generator_function_tool_clinical_reasoning(self):
        """CRITICAL: Test that Query Generator actually performs clinical reasoning."""
        # Real clinical scenario requiring medical expertise
        clinical_analysis = {
            "subject_id": "CARD001",
            "site_name": "Site 001",
            "visit": "Week 12",
            "visit_date": "2025-01-09",
            "field_name": "hemoglobin",
            "edc_value": "8.2",
            "source_value": "8.1",
            "category": "laboratory_critical_value",
            "severity": "critical",
            "reason": "Hemoglobin below safety threshold (normal: 12.0-16.0 g/dL for females, 14.0-18.0 g/dL for males)",
            "clinical_significance": "moderate_anemia",
            "safety_impact": "high"
        }
        
        request_data = {
            "analysis": clinical_analysis,
            "site_preferences": {"preferred_language": "en"},
            "language": "en"
        }
        
        # Call the actual function tool
        result_str = generate_clinical_query(json.dumps(request_data))
        result = json.loads(result_str)
        
        # CRITICAL CHECKS - Must demonstrate clinical reasoning
        assert "query_text" in result, "Query tool must generate query text"
        query_text = result["query_text"]
        
        # Must contain clinical context
        assert "hemoglobin" in query_text.lower(), "Query must mention hemoglobin"
        assert "8.2" in query_text or "8.1" in query_text, "Query must reference actual values"
        assert "site 001" in query_text.lower() or "site_001" in query_text.lower(), "Query must reference site"
        assert "CARD001" in query_text, "Query must reference subject ID"
        
        # Must demonstrate severity understanding
        assert result["priority"] == "critical", "Must recognize critical severity"
        assert "24 hours" in result.get("suggested_response_time", ""), "Critical queries need 24-hour response"
        
        # Must include regulatory compliance
        assert "regulatory_refs" in result, "Must include regulatory references"
        assert len(result["regulatory_refs"]) > 0, "Must have at least one regulatory reference"
        
        print(f"✅ Query Generator Clinical Reasoning Test PASSED")
        print(f"Generated query: {query_text[:200]}...")
    
    def test_data_verifier_function_tool_discrepancy_detection(self):
        """CRITICAL: Test that Data Verifier actually detects real discrepancies."""
        # Real clinical data with known discrepancies
        verification_data = {
            "edc_data": {
                "subject_id": "CARD001",
                "hemoglobin": "12.5",
                "systolic_bp": "140",
                "diastolic_bp": "85",
                "weight": "75.2",
                "adverse_events": ["headache"]
            },
            "source_data": {
                "subject_id": "CARD001",
                "hemoglobin": "12.8",  # 0.3 difference - should be detected
                "systolic_bp": "145",  # 5 mmHg difference - should be detected
                "diastolic_bp": "88",  # 3 mmHg difference - should be detected
                "weight": "75.2",  # Exact match - should NOT be detected
                "adverse_events": ["headache", "nausea"]  # Missing event - should be detected
            },
            "subject_id": "CARD001",
            "verification_type": "routine_monitoring"
        }
        
        # Call the actual function tool
        result_str = cross_system_verification(json.dumps(verification_data))
        result = json.loads(result_str)
        
        # CRITICAL CHECKS - Must detect actual discrepancies
        assert "discrepancies" in result, "Must detect discrepancies"
        discrepancies = result["discrepancies"]
        assert len(discrepancies) > 0, "Must find at least one discrepancy"
        
        # Check for hemoglobin discrepancy
        hemoglobin_found = False
        bp_found = False
        ae_found = False
        weight_found = False
        
        for disc in discrepancies:
            if disc["field"] == "hemoglobin":
                hemoglobin_found = True
                assert disc["edc_value"] == "12.5", "Must capture correct EDC value"
                assert disc["source_value"] == "12.8", "Must capture correct source value"
                assert disc["discrepancy_type"] == "value_mismatch", "Must identify as value mismatch"
            elif disc["field"] in ["systolic_bp", "blood_pressure"]:
                bp_found = True
                assert "140" in str(disc["edc_value"]) or "145" in str(disc["source_value"]), "Must detect BP discrepancy"
            elif disc["field"] == "adverse_events":
                ae_found = True
                assert disc["discrepancy_type"] == "missing_in_edc", "Must identify missing adverse event"
            elif disc["field"] == "weight":
                weight_found = True
                # This should NOT happen since weight matches exactly
                assert False, "Must NOT detect discrepancy for matching weight values"
        
        assert hemoglobin_found, "Must detect hemoglobin discrepancy (12.5 vs 12.8)"
        assert bp_found or ae_found, "Must detect either BP or adverse event discrepancy"
        assert not weight_found, "Must NOT detect false positive for matching weight"
        
        print(f"✅ Data Verifier Discrepancy Detection Test PASSED")
        print(f"Detected {len(discrepancies)} discrepancies correctly")
    
    def test_deviation_detector_function_tool_protocol_violations(self):
        """CRITICAL: Test that Deviation Detector actually detects protocol violations."""
        # Real protocol violation scenario
        protocol_scenario = {
            "protocol_data": {
                "prohibited_medications": ["aspirin", "warfarin", "clopidogrel"],
                "visit_windows": {
                    "week_12": {"min_days": 80, "max_days": 88}
                },
                "fasting_requirements": {
                    "glucose_test": {"min_hours": 8, "max_hours": 12}
                },
                "inclusion_criteria": {
                    "age_range": {"min": 18, "max": 75},
                    "systolic_bp_range": {"min": 130, "max": 180}
                }
            },
            "actual_data": {
                "concomitant_medications": ["lisinopril", "aspirin", "metformin"],  # VIOLATION: aspirin prohibited
                "visit_date": "2025-01-17",
                "scheduled_date": "2025-01-08",  # 9 days late - outside window
                "glucose_test_fasting_hours": 6,  # VIOLATION: too short
                "subject_age": 45,  # OK
                "systolic_bp": 195  # VIOLATION: too high
            },
            "subject_id": "CARD001",
            "site_id": "SITE_001",
            "visit": "Week 12"
        }
        
        # Call the actual function tool
        result_str = detect_protocol_deviations(json.dumps(protocol_scenario))
        result = json.loads(result_str)
        
        # CRITICAL CHECKS - Must detect actual protocol violations
        assert "deviations" in result, "Must detect protocol deviations"
        deviations = result["deviations"]
        assert len(deviations) > 0, "Must find at least one deviation"
        
        # Check for prohibited medication detection
        med_violation_found = False
        fasting_violation_found = False
        bp_violation_found = False
        
        for dev in deviations:
            if dev["category"] == "prohibited_medication":
                med_violation_found = True
                assert "aspirin" in dev["actual_value"], "Must identify aspirin as prohibited"
                assert dev["severity"] == "critical", "Prohibited medication must be critical"
                assert dev["corrective_action_required"] is True, "Must require corrective action"
            elif dev["category"] == "fasting_requirement":
                fasting_violation_found = True
                assert "6" in str(dev["actual_value"]), "Must identify 6-hour fasting as violation"
                assert dev["protocol_requirement"] == "8-12 hours fasting required", "Must specify requirement"
            elif dev["category"] == "inclusion_criteria":
                bp_violation_found = True
                assert "195" in str(dev["actual_value"]), "Must identify BP 195 as violation"
        
        assert med_violation_found, "Must detect prohibited medication violation"
        # At least one of the other violations should be detected
        assert fasting_violation_found or bp_violation_found, "Must detect at least one other violation"
        
        print(f"✅ Deviation Detector Protocol Violation Test PASSED")
        print(f"Detected {len(deviations)} protocol violations correctly")
    
    def test_analytics_agent_function_tool_realistic_data(self):
        """CRITICAL: Test that Analytics Agent generates realistic, not hardcoded data."""
        # Test enrollment trends
        enrollment_request = {
            "time_period": "30_days",
            "sites": ["SITE_001", "SITE_002", "SITE_003"]
        }
        
        result_str = generate_enrollment_trends(json.dumps(enrollment_request))
        result = json.loads(result_str)
        
        # CRITICAL CHECKS - Must generate realistic data
        assert "trend_data" in result, "Must generate trend data"
        assert "summary" in result, "Must include summary"
        
        trend_data = result["trend_data"]
        assert len(trend_data) > 0, "Must have trend data points"
        
        # Check for realistic data structure
        for point in trend_data:
            assert "date" in point, "Each point must have date"
            assert "cumulative" in point, "Each point must have cumulative enrollment"
            assert "weekly" in point, "Each point must have weekly enrollment"
            assert "target" in point, "Each point must have target"
            assert "variance" in point, "Each point must have variance"
            
            # Check for realistic values
            assert isinstance(point["cumulative"], (int, float)), "Cumulative must be numeric"
            assert isinstance(point["weekly"], (int, float)), "Weekly must be numeric"
            assert point["cumulative"] >= 0, "Cumulative cannot be negative"
            assert point["weekly"] >= 0, "Weekly cannot be negative"
        
        # Check that cumulative is actually cumulative (increasing)
        cumulative_values = [p["cumulative"] for p in trend_data]
        for i in range(1, len(cumulative_values)):
            assert cumulative_values[i] >= cumulative_values[i-1], "Cumulative must be non-decreasing"
        
        # Test data quality trends
        quality_request = {
            "time_period": "30_days",
            "metrics": ["completeness", "accuracy", "consistency"]
        }
        
        quality_result_str = generate_data_quality_trends(json.dumps(quality_request))
        quality_result = json.loads(quality_result_str)
        
        assert "quality_data" in quality_result, "Must generate quality data"
        quality_data = quality_result["quality_data"]
        
        for point in quality_data:
            assert "percentage" in point, "Each point must have percentage"
            assert 0 <= point["percentage"] <= 100, "Percentage must be between 0-100"
        
        print(f"✅ Analytics Agent Realistic Data Test PASSED")
        print(f"Generated {len(trend_data)} enrollment trend points and {len(quality_data)} quality points")
    
    def test_query_tracker_function_tool_lifecycle_management(self):
        """CRITICAL: Test that Query Tracker actually manages query lifecycle."""
        # Test tracking a new query
        query_data = {
            "query_id": "Q-CARD001-20250109-001",
            "subject_id": "CARD001",
            "site_id": "SITE_001",
            "priority": "critical",
            "category": "adverse_event",
            "created_at": "2025-01-09T10:00:00Z",
            "due_date": "2025-01-10T10:00:00Z"
        }
        
        # Call the actual function tool
        result_str = track_clinical_query(json.dumps(query_data))
        result = json.loads(result_str)
        
        # CRITICAL CHECKS - Must properly track query
        assert "tracking_id" in result, "Must generate tracking ID"
        assert "query_id" in result, "Must preserve query ID"
        assert result["query_id"] == "Q-CARD001-20250109-001", "Must preserve exact query ID"
        assert result["status"] == "tracking_started", "Must confirm tracking started"
        assert result["priority"] == "critical", "Must preserve priority"
        
        # Test updating query status
        update_data = {
            "query_id": "Q-CARD001-20250109-001",
            "new_status": "in_progress",
            "notes": "Site coordinator reviewing query"
        }
        
        update_result_str = update_query_status(json.dumps(update_data))
        update_result = json.loads(update_result_str)
        
        assert update_result["success"] is True, "Must successfully update status"
        assert update_result["query_id"] == "Q-CARD001-20250109-001", "Must preserve query ID"
        assert update_result["old_status"] == "pending", "Must track previous status"
        assert update_result["new_status"] == "in_progress", "Must confirm new status"
        
        print(f"✅ Query Tracker Lifecycle Management Test PASSED")
        print(f"Successfully tracked query and updated status")
    
    def test_agents_integration_with_real_clinical_workflow(self):
        """CRITICAL: Test that agents work together in a real clinical workflow."""
        # Simulate a real clinical workflow scenario
        
        # 1. Data Verifier finds discrepancy
        verification_data = {
            "edc_data": {"subject_id": "CARD001", "hemoglobin": "8.2"},
            "source_data": {"subject_id": "CARD001", "hemoglobin": "8.1"},
            "subject_id": "CARD001"
        }
        
        verification_result_str = cross_system_verification(json.dumps(verification_data))
        verification_result = json.loads(verification_result_str)
        
        assert "discrepancies" in verification_result, "Step 1: Must find discrepancies"
        
        # 2. Query Generator creates query for discrepancy
        first_discrepancy = verification_result["discrepancies"][0]
        query_analysis = {
            "subject_id": "CARD001",
            "site_name": "Site 001",
            "visit": "Week 12",
            "category": "data_discrepancy",
            "severity": "critical",
            "field_name": first_discrepancy["field"],
            "edc_value": first_discrepancy["edc_value"],
            "source_value": first_discrepancy["source_value"]
        }
        
        query_result_str = generate_clinical_query(json.dumps({
            "analysis": query_analysis,
            "site_preferences": {},
            "language": "en"
        }))
        query_result = json.loads(query_result_str)
        
        assert "query_id" in query_result, "Step 2: Must generate query"
        
        # 3. Query Tracker tracks the query
        track_result_str = track_clinical_query(json.dumps({
            "query_id": query_result["query_id"],
            "subject_id": "CARD001",
            "site_id": "SITE_001",
            "priority": query_result["priority"]
        }))
        track_result = json.loads(track_result_str)
        
        assert track_result["status"] == "tracking_started", "Step 3: Must start tracking"
        
        # 4. Verify the workflow maintains clinical context
        assert first_discrepancy["field"] == "hemoglobin", "Must maintain clinical context"
        assert query_result["priority"] == "critical", "Must preserve clinical priority"
        assert track_result["priority"] == "critical", "Must maintain priority through workflow"
        
        print(f"✅ Integrated Clinical Workflow Test PASSED")
        print(f"Successfully completed 4-step clinical workflow")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])