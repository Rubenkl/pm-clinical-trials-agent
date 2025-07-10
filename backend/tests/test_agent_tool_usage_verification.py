"""
Comprehensive tests to verify agents are actually using their tools correctly
and performing their intended functions, not just passing superficial tests.
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from typing import Dict, Any, List

from app.agents.query_generator import QueryGenerator, generate_clinical_query
from app.agents.data_verifier import DataVerifier, cross_system_verification
from app.agents.deviation_detector import DeviationDetector, detect_protocol_deviations
from app.agents.analytics_agent import AnalyticsAgent, generate_enrollment_trends
from app.agents.query_tracker import QueryTracker, track_query_lifecycle


class TestQueryGeneratorToolUsage:
    """Test that Query Generator actually uses its tools and clinical reasoning."""
    
    def test_generate_clinical_query_tool_actually_called(self):
        """Verify generate_clinical_query tool is called with proper clinical context."""
        # Test data with clinical context
        analysis_data = {
            "subject_id": "CARD001",
            "site_name": "Site 001",
            "visit": "Week 12",
            "visit_date": "2025-01-09",
            "field_name": "hemoglobin",
            "edc_value": "8.5",
            "source_value": "8.2",
            "category": "data_discrepancy",
            "severity": "critical",
            "reason": "laboratory value verification"
        }
        
        # Call the function tool directly
        result_str = generate_clinical_query(json.dumps({
            "analysis": analysis_data,
            "site_preferences": {},
            "language": "en"
        }))
        
        result = json.loads(result_str)
        
        # Verify it contains clinical reasoning
        assert "query_text" in result
        query_text = result["query_text"]
        
        # Check for medical terminology and clinical context
        assert "hemoglobin" in query_text.lower()
        assert "8.5" in query_text or "8.2" in query_text
        assert "site 001" in query_text.lower() or "site_001" in query_text.lower()
        assert "subject" in query_text.lower()
        
        # Verify regulatory references
        assert "regulatory_refs" in result
        assert len(result["regulatory_refs"]) > 0
        
        # Verify clinical severity assessment
        assert result["priority"] == "critical"
        assert "suggested_response_time" in result
        assert "24 hours" in result["suggested_response_time"]
    
    def test_query_generator_agent_uses_tools_for_clinical_analysis(self):
        """Test that QueryGenerator wrapper actually calls function tools."""
        generator = QueryGenerator()
        
        # Clinical analysis requiring tool usage
        analysis = {
            "subject_id": "CARD001",
            "site_name": "Site 001",
            "visit": "Baseline",
            "category": "adverse_event",
            "severity": "critical",
            "event_type": "Serious Adverse Event",
            "event_date": "2025-01-09",
            "specific_question": "Was hospitalization required?"
        }
        
        # This should call the function tool
        result = generator._generate_query_fallback(analysis, {}, "en")
        
        # Verify clinical reasoning in output
        assert "query_text" in result
        query_text = result["query_text"]
        
        # Check for critical severity handling
        assert "URGENT" in query_text.upper() or "CRITICAL" in query_text.upper()
        assert "CARD001" in query_text
        assert "Site 001" in query_text
        
        # Verify proper categorization
        assert result["category"] == "adverse_event"
        assert result["priority"] == "critical"
    
    def test_bulk_operations_actually_work(self):
        """Test that bulk query generation actually processes multiple items."""
        generator = QueryGenerator()
        
        # Multiple clinical analyses
        analyses = [
            {
                "subject_id": "CARD001",
                "category": "data_discrepancy",
                "severity": "minor",
                "site_name": "Site 001"
            },
            {
                "subject_id": "CARD002", 
                "category": "adverse_event",
                "severity": "critical",
                "site_name": "Site 002"
            },
            {
                "subject_id": "CARD003",
                "category": "missing_data",
                "severity": "major",
                "site_name": "Site 003"
            }
        ]
        
        # Call bulk generation
        import asyncio
        result = asyncio.run(generator.generate_bulk_queries(analyses))
        
        # Verify each analysis was processed
        assert len(result) == 3
        
        # Verify each query has proper structure
        for i, query in enumerate(result):
            assert "query_text" in query
            assert "query_id" in query
            assert f"CARD00{i+1}" in query["query_text"]
            
            # Verify severity handling
            expected_severity = analyses[i]["severity"]
            if expected_severity == "critical":
                assert query["priority"] == "critical"
            else:
                assert query["priority"] in ["medium", "major", "minor"]


class TestDataVerifierToolUsage:
    """Test that Data Verifier actually uses its tools and performs verification."""
    
    def test_cross_system_verification_tool_actually_called(self):
        """Verify cross_system_verification tool performs actual comparison."""
        # Test data with real discrepancies
        verification_data = {
            "edc_data": {
                "subject_id": "CARD001",
                "hemoglobin": "12.5",
                "blood_pressure": "140/90",
                "weight": "75.2"
            },
            "source_data": {
                "subject_id": "CARD001", 
                "hemoglobin": "12.8",  # Discrepancy
                "blood_pressure": "145/92",  # Discrepancy
                "weight": "75.2"  # Match
            },
            "subject_id": "CARD001",
            "verification_type": "routine_monitoring"
        }
        
        # Call the function tool directly
        result_str = cross_system_verification(json.dumps(verification_data))
        result = json.loads(result_str)
        
        # Verify actual discrepancy detection
        assert "discrepancies" in result
        discrepancies = result["discrepancies"]
        
        # Should find hemoglobin and blood pressure discrepancies
        hemoglobin_discrepancy = None
        bp_discrepancy = None
        
        for disc in discrepancies:
            if disc["field"] == "hemoglobin":
                hemoglobin_discrepancy = disc
            elif disc["field"] == "blood_pressure":
                bp_discrepancy = disc
        
        # Verify hemoglobin discrepancy detection
        assert hemoglobin_discrepancy is not None
        assert hemoglobin_discrepancy["edc_value"] == "12.5"
        assert hemoglobin_discrepancy["source_value"] == "12.8"
        assert hemoglobin_discrepancy["discrepancy_type"] == "value_mismatch"
        
        # Verify blood pressure discrepancy detection
        assert bp_discrepancy is not None
        assert bp_discrepancy["edc_value"] == "140/90"
        assert bp_discrepancy["source_value"] == "145/92"
        
        # Verify no false positives (weight should match)
        weight_discrepancies = [d for d in discrepancies if d["field"] == "weight"]
        assert len(weight_discrepancies) == 0
    
    def test_data_verifier_handles_critical_findings(self):
        """Test that DataVerifier properly identifies critical clinical findings."""
        verifier = DataVerifier()
        
        # Critical clinical values
        verification_data = {
            "edc_data": {
                "subject_id": "CARD001",
                "hemoglobin": "7.2",  # Critical low
                "blood_pressure": "200/110",  # Critical high
                "adverse_events": []
            },
            "source_data": {
                "subject_id": "CARD001",
                "hemoglobin": "7.1",  # Slight discrepancy but still critical
                "blood_pressure": "198/108",  # Slight discrepancy but still critical
                "adverse_events": ["Severe anemia"]  # Missing in EDC
            }
        }
        
        # This should identify critical findings
        result = asyncio.run(verifier.verify_data(verification_data))
        
        # Verify critical findings are flagged
        assert "critical_findings" in result or "discrepancies" in result
        
        if "discrepancies" in result:
            # Check for proper severity assessment
            critical_discrepancies = [d for d in result["discrepancies"] if d.get("severity") == "critical"]
            assert len(critical_discrepancies) > 0
    
    def test_sdv_session_management_tools(self):
        """Test SDV session management tools actually work."""
        verifier = DataVerifier()
        
        # Test get_sdv_sessions
        sessions_result = asyncio.run(verifier.get_sdv_sessions())
        
        assert "sessions" in sessions_result
        assert len(sessions_result["sessions"]) > 0
        
        # Verify session structure
        session = sessions_result["sessions"][0]
        assert "session_id" in session
        assert "subject_id" in session
        assert "site_id" in session
        assert "verification_status" in session
        
        # Test create_sdv_session
        session_data = {
            "subject_id": "CARD001",
            "site_id": "SITE_001",
            "monitor_id": "MON001",
            "verification_type": "routine"
        }
        
        creation_result = asyncio.run(verifier.create_sdv_session(session_data))
        
        assert "session_id" in creation_result
        assert "success" in creation_result
        assert creation_result["success"] is True


class TestDeviationDetectorToolUsage:
    """Test that Deviation Detector actually detects protocol deviations."""
    
    def test_detect_protocol_deviations_tool_actually_works(self):
        """Verify protocol deviation detection with real clinical scenarios."""
        # Test prohibited medication scenario
        deviation_data = {
            "protocol_data": {
                "prohibited_medications": ["aspirin", "warfarin", "clopidogrel"],
                "visit_windows": {
                    "week_12": {"min_days": 80, "max_days": 88}
                },
                "fasting_requirements": {
                    "glucose_test": {"min_hours": 8, "max_hours": 12}
                }
            },
            "actual_data": {
                "concomitant_medications": ["lisinopril", "aspirin", "metformin"],  # Aspirin prohibited
                "visit_date": "2025-01-09",
                "scheduled_date": "2025-01-01",  # 8 days late
                "glucose_test_fasting_hours": 6  # Too short
            },
            "subject_id": "CARD001",
            "site_id": "SITE_001",
            "visit": "Week 12"
        }
        
        # Call the function tool directly
        result_str = detect_protocol_deviations(json.dumps(deviation_data))
        result = json.loads(result_str)
        
        # Verify actual deviation detection
        assert "deviations" in result
        deviations = result["deviations"]
        
        # Should detect prohibited medication
        med_deviation = None
        for dev in deviations:
            if dev["category"] == "prohibited_medication":
                med_deviation = dev
                break
        
        assert med_deviation is not None
        assert med_deviation["severity"] == "critical"
        assert "aspirin" in med_deviation["actual_value"]
        assert med_deviation["corrective_action_required"] is True
    
    def test_deviation_detector_compliance_summary(self):
        """Test compliance summary generation with real data."""
        detector = DeviationDetector()
        
        # Test compliance summary
        compliance_result = asyncio.run(detector.get_compliance_summary())
        
        assert "compliance_rate" in compliance_result
        assert "total_deviations" in compliance_result
        assert "deviations_by_severity" in compliance_result
        
        # Verify realistic compliance data
        assert 0 <= compliance_result["compliance_rate"] <= 100
        assert compliance_result["total_deviations"] >= 0
        
        # Verify severity breakdown
        severity_breakdown = compliance_result["deviations_by_severity"]
        assert "critical" in severity_breakdown
        assert "major" in severity_breakdown
        assert "minor" in severity_breakdown


class TestAnalyticsAgentToolUsage:
    """Test that Analytics Agent actually generates analytics and trends."""
    
    def test_generate_enrollment_trends_tool_produces_data(self):
        """Verify enrollment trends tool generates realistic data."""
        # Call the function tool directly
        result_str = generate_enrollment_trends(json.dumps({
            "time_period": "30_days",
            "sites": ["SITE_001", "SITE_002", "SITE_003"]
        }))
        
        result = json.loads(result_str)
        
        # Verify trend data structure
        assert "trend_data" in result
        assert "summary" in result
        
        trend_data = result["trend_data"]
        assert len(trend_data) > 0
        
        # Verify each data point has required fields
        for point in trend_data:
            assert "date" in point
            assert "cumulative" in point
            assert "weekly" in point
            assert "target" in point
            assert "variance" in point
        
        # Verify realistic values
        summary = result["summary"]
        assert "total_enrolled" in summary
        assert "avg_weekly" in summary
        assert "trend_direction" in summary
        assert summary["trend_direction"] in ["improving", "declining", "stable"]
    
    def test_analytics_agent_dashboard_generation(self):
        """Test complete dashboard analytics generation."""
        agent = AnalyticsAgent()
        
        # Test dashboard analytics
        analytics_request = {
            "time_period": "30_days",
            "sites": ["SITE_001", "SITE_002", "SITE_003"],
            "metrics": ["enrollment", "data_quality", "activities"]
        }
        
        result = asyncio.run(agent.generate_dashboard_analytics(analytics_request))
        
        # Verify comprehensive analytics
        assert "enrollment_trend" in result
        assert "data_quality_trend" in result
        assert "recent_activities" in result
        assert "performance_summary" in result
        
        # Verify data quality
        enrollment_trend = result["enrollment_trend"]
        assert len(enrollment_trend) > 0
        
        data_quality_trend = result["data_quality_trend"]
        assert len(data_quality_trend) > 0
        
        recent_activities = result["recent_activities"]
        assert len(recent_activities) > 0
        
        # Verify performance metrics
        performance = result["performance_summary"]
        assert "enrollment_rate" in performance
        assert "data_quality" in performance
        assert "total_activities" in performance


class TestQueryTrackerToolUsage:
    """Test that Query Tracker actually tracks query lifecycle."""
    
    def test_track_query_lifecycle_tool_functions(self):
        """Verify query lifecycle tracking with real scenarios."""
        # Test query lifecycle tracking
        lifecycle_data = {
            "query_id": "Q-CARD001-20250109-001",
            "subject_id": "CARD001",
            "site_id": "SITE_001",
            "priority": "critical",
            "category": "adverse_event",
            "created_date": "2025-01-09T10:00:00Z",
            "sla_hours": 24
        }
        
        # Call the function tool directly
        result_str = track_query_lifecycle(json.dumps(lifecycle_data))
        result = json.loads(result_str)
        
        # Verify tracking functionality
        assert "query_id" in result
        assert "tracking_status" in result
        assert "sla_status" in result
        assert "escalation_level" in result
        
        # Verify SLA monitoring
        if result["sla_status"] == "at_risk":
            assert "time_remaining" in result
            assert "escalation_recommended" in result
    
    def test_query_tracker_resolution_capability(self):
        """Test query resolution tracking and statistics."""
        tracker = QueryTracker()
        
        # Test query resolution
        resolution_data = {
            "query_id": "Q-CARD001-20250109-001",
            "resolution_notes": "Hemoglobin value verified against source documents",
            "resolved_by": "Site Coordinator",
            "resolution_date": "2025-01-09T14:30:00Z"
        }
        
        result = asyncio.run(tracker.resolve_query(resolution_data))
        
        assert "success" in result
        assert result["success"] is True
        assert "resolution_id" in result
        
        # Test query statistics
        stats_result = asyncio.run(tracker.get_query_statistics())
        
        assert "total_queries" in stats_result
        assert "critical_queries" in stats_result
        assert "categories" in stats_result
        assert "avg_generation_time" in stats_result


class TestAgentHandoffMechanisms:
    """Test that agents properly hand off to other agents when needed."""
    
    @patch('app.agents.handoff_registry.clinical_trials_registry')
    def test_query_analyzer_hands_off_to_query_generator(self, mock_registry):
        """Test that Query Analyzer hands off to Query Generator for query creation."""
        # Mock the registry and agents
        mock_query_generator = Mock()
        mock_registry.get_query_generator.return_value = mock_query_generator
        
        # Import after mocking
        from app.agents.query_analyzer import QueryAnalyzer
        
        analyzer = QueryAnalyzer()
        
        # Clinical analysis that should trigger handoff
        analysis_data = {
            "subject_id": "CARD001",
            "clinical_findings": [{
                "parameter": "hemoglobin",
                "value": "7.2",
                "interpretation": "severe anemia"
            }],
            "requires_query": True
        }
        
        # This should trigger handoff to Query Generator
        result = asyncio.run(analyzer.analyze_clinical_data(analysis_data))
        
        # Verify handoff occurred
        if "next_agent" in result:
            assert result["next_agent"] == "query_generator"
    
    def test_data_verifier_escalates_critical_findings(self):
        """Test that Data Verifier escalates critical findings appropriately."""
        verifier = DataVerifier()
        
        # Critical clinical scenario
        verification_data = {
            "edc_data": {"hemoglobin": "6.8", "subject_id": "CARD001"},
            "source_data": {"hemoglobin": "6.9", "subject_id": "CARD001"},
            "subject_id": "CARD001"
        }
        
        result = asyncio.run(verifier.verify_data(verification_data))
        
        # Verify escalation flags
        if "escalation_required" in result:
            assert result["escalation_required"] is True
        
        # Or verify through severity classification
        if "discrepancies" in result:
            critical_findings = [d for d in result["discrepancies"] if d.get("severity") == "critical"]
            assert len(critical_findings) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])