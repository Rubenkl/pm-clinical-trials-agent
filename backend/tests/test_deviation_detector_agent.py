"""
TDD Tests for Deviation Detector Agent (Task #5)

Tests for the new specialized Deviation Detector agent that focuses on protocol
compliance monitoring with minimal responsibilities and JSON output with human-readable fields.

RED Phase: These tests will fail initially and drive the implementation.
"""

import json
from datetime import datetime
from typing import Any, Dict, List

import pytest

from app.agents.deviation_detector import DeviationDetector


class TestDeviationDetectorAgent:
    """Test the new Deviation Detector agent with minimal responsibilities"""

    @pytest.fixture
    def deviation_detector(self):
        """Create Deviation Detector instance for testing"""
        return DeviationDetector()

    @pytest.fixture
    def protocol_violation_data(self):
        """Sample protocol violation data"""
        return {
            "protocol_data": {
                "prohibited_medications": ["aspirin", "warfarin", "clopidogrel"],
                "required_visit_window": "±3 days",
                "required_fasting": "12 hours",
                "maximum_visit_duration": "2 hours",
            },
            "actual_data": {
                "concomitant_medications": ["aspirin", "metformin", "lisinopril"],
                "visit_date": "2025-01-15",
                "scheduled_date": "2025-01-09",
                "fasting_hours": "8",
                "visit_duration": "3 hours",
            },
            "subject_id": "SUBJ001",
            "site_id": "SITE01",
            "visit": "Week 12",
        }

    @pytest.fixture
    def compliant_data(self):
        """Sample compliant data (no deviations)"""
        return {
            "protocol_data": {
                "prohibited_medications": ["aspirin", "warfarin"],
                "required_visit_window": "±3 days",
                "required_fasting": "12 hours",
            },
            "actual_data": {
                "concomitant_medications": ["metformin", "lisinopril"],
                "visit_date": "2025-01-10",
                "scheduled_date": "2025-01-09",
                "fasting_hours": "14",
            },
            "subject_id": "SUBJ002",
            "site_id": "SITE01",
            "visit": "Week 8",
        }

    async def test_deviation_detector_initialization(self, deviation_detector):
        """Test Deviation Detector initializes correctly with OpenAI Agents SDK"""
        # This test will FAIL initially (RED phase)
        assert deviation_detector is not None
        assert hasattr(deviation_detector, "agent")
        assert hasattr(deviation_detector, "context")
        assert hasattr(deviation_detector, "instructions")

        # Should have minimal responsibilities focused on deviation detection
        assert "deviation" in deviation_detector.instructions.lower()
        assert "protocol" in deviation_detector.instructions.lower()
        assert "compliance" in deviation_detector.instructions.lower()

    async def test_detect_protocol_deviations_basic(
        self, deviation_detector, protocol_violation_data
    ):
        """Test basic protocol deviation detection with JSON output"""
        # This test will FAIL initially (RED phase)
        result = await deviation_detector.detect_protocol_deviations(
            protocol_violation_data
        )

        # Verify JSON structure
        assert isinstance(result, dict)
        assert "success" in result
        assert result["success"] is True

        # Core deviation detection fields
        assert "deviations" in result
        assert "total_deviations_found" in result
        assert "compliance_status" in result
        assert "subject_id" in result
        assert "site_id" in result

        # Should detect multiple deviations
        assert result["total_deviations_found"] > 0
        assert len(result["deviations"]) > 0

        # Human-readable fields for frontend
        assert "human_readable_summary" in result
        assert "deviation_summary" in result
        assert "compliance_assessment" in result

        # Should detect prohibited medication
        deviations = result["deviations"]
        medication_violation = next(
            (d for d in deviations if d["category"] == "prohibited_medication"), None
        )
        assert medication_violation is not None
        assert medication_violation["severity"] == "critical"
        assert "aspirin" in medication_violation["actual_value"]

    async def test_detect_visit_window_deviation(self, deviation_detector):
        """Test visit window deviation detection"""
        visit_window_data = {
            "protocol_data": {"required_visit_window": "±3 days"},
            "actual_data": {
                "visit_date": "2025-01-15",
                "scheduled_date": "2025-01-08",  # 7 days difference
            },
            "subject_id": "SUBJ003",
            "site_id": "SITE02",
            "visit": "Week 4",
        }

        # This test will FAIL initially (RED phase)
        result = await deviation_detector.detect_protocol_deviations(visit_window_data)

        assert result["success"] is True
        assert result["total_deviations_found"] == 1

        deviation = result["deviations"][0]
        assert deviation["category"] == "visit_window"
        assert deviation["severity"] == "major"  # More than 2x the window
        assert "7 days" in deviation["actual_value"]
        assert "±3 days" in deviation["protocol_requirement"]

    async def test_detect_fasting_requirement_deviation(self, deviation_detector):
        """Test fasting requirement deviation detection"""
        fasting_data = {
            "protocol_data": {"required_fasting": "12 hours"},
            "actual_data": {"fasting_hours": "4"},
            "subject_id": "SUBJ004",
            "site_id": "SITE03",
            "visit": "Week 2",
        }

        # This test will FAIL initially (RED phase)
        result = await deviation_detector.detect_protocol_deviations(fasting_data)

        assert result["success"] is True
        assert result["total_deviations_found"] == 1

        deviation = result["deviations"][0]
        assert deviation["category"] == "fasting_requirement"
        assert deviation["severity"] == "minor"
        assert "4 hours" in deviation["actual_value"]
        assert "12 hours" in deviation["protocol_requirement"]

    async def test_compliant_data_no_deviations(
        self, deviation_detector, compliant_data
    ):
        """Test that compliant data returns no deviations"""
        # This test will FAIL initially (RED phase)
        result = await deviation_detector.detect_protocol_deviations(compliant_data)

        assert result["success"] is True
        assert result["total_deviations_found"] == 0
        assert len(result["deviations"]) == 0
        assert result["compliance_status"] == "compliant"

        # Human-readable fields should reflect compliance
        assert (
            "no" in result["human_readable_summary"].lower()
            and "deviations" in result["human_readable_summary"].lower()
        )
        assert "compliant" in result["compliance_assessment"].lower()

    async def test_deviation_severity_classification(self, deviation_detector):
        """Test proper severity classification for different deviation types"""
        # This test will FAIL initially (RED phase)

        # Critical: Prohibited medication
        critical_data = {
            "protocol_data": {"prohibited_medications": ["warfarin"]},
            "actual_data": {"concomitant_medications": ["warfarin"]},
            "subject_id": "SUBJ005",
            "site_id": "SITE01",
            "visit": "Week 1",
        }

        result = await deviation_detector.detect_protocol_deviations(critical_data)
        assert result["deviations"][0]["severity"] == "critical"

        # Major: Visit window > 2x limit
        major_data = {
            "protocol_data": {"required_visit_window": "±2 days"},
            "actual_data": {"visit_date": "2025-01-15", "scheduled_date": "2025-01-10"},
            "subject_id": "SUBJ006",
            "site_id": "SITE01",
            "visit": "Week 1",
        }

        result = await deviation_detector.detect_protocol_deviations(major_data)
        assert result["deviations"][0]["severity"] == "major"

        # Minor: Fasting requirement not met
        minor_data = {
            "protocol_data": {"required_fasting": "8 hours"},
            "actual_data": {"fasting_hours": "6"},
            "subject_id": "SUBJ007",
            "site_id": "SITE01",
            "visit": "Week 1",
        }

        result = await deviation_detector.detect_protocol_deviations(minor_data)
        assert result["deviations"][0]["severity"] == "minor"

    async def test_batch_deviation_detection(self, deviation_detector):
        """Test batch processing of multiple subjects for deviation detection"""
        batch_data = [
            {
                "protocol_data": {"prohibited_medications": ["aspirin"]},
                "actual_data": {"concomitant_medications": ["aspirin"]},
                "subject_id": "SUBJ008",
                "site_id": "SITE01",
                "visit": "Week 1",
            },
            {
                "protocol_data": {"required_visit_window": "±3 days"},
                "actual_data": {
                    "visit_date": "2025-01-15",
                    "scheduled_date": "2025-01-08",
                },
                "subject_id": "SUBJ009",
                "site_id": "SITE01",
                "visit": "Week 1",
            },
            {
                "protocol_data": {"required_fasting": "12 hours"},
                "actual_data": {"fasting_hours": "14"},
                "subject_id": "SUBJ010",
                "site_id": "SITE01",
                "visit": "Week 1",
            },
        ]

        # This test will FAIL initially (RED phase)
        result = await deviation_detector.batch_detect_deviations(batch_data)

        assert result["success"] is True
        assert "batch_results" in result
        assert len(result["batch_results"]) == 3

        # Should have summary statistics
        assert "batch_summary" in result
        summary = result["batch_summary"]
        assert "total_subjects" in summary
        assert "subjects_with_deviations" in summary
        assert "total_deviations" in summary
        assert "critical_deviations" in summary

        # Human-readable batch summary
        assert "human_readable_summary" in result
        assert "batch" in result["human_readable_summary"].lower()

    async def test_deviation_context_preservation(self, deviation_detector):
        """Test that Deviation Detector preserves context for OpenAI Agents SDK"""
        # This test will FAIL initially (RED phase)

        # First detection
        data1 = {
            "protocol_data": {"prohibited_medications": ["aspirin"]},
            "actual_data": {"concomitant_medications": ["aspirin"]},
            "subject_id": "SUBJ011",
            "site_id": "SITE01",
            "visit": "Week 1",
        }

        result1 = await deviation_detector.detect_protocol_deviations(data1)
        assert result1["success"] is True

        # Second detection - context should be preserved
        data2 = {
            "protocol_data": {"prohibited_medications": ["warfarin"]},
            "actual_data": {"concomitant_medications": ["warfarin"]},
            "subject_id": "SUBJ012",
            "site_id": "SITE01",
            "visit": "Week 1",
        }

        result2 = await deviation_detector.detect_protocol_deviations(data2)
        assert result2["success"] is True

        # Should have detection history in context
        assert hasattr(deviation_detector, "context")
        assert hasattr(deviation_detector.context, "detection_history")
        assert len(deviation_detector.context.detection_history) >= 2

    async def test_deviation_agent_function_tools(self, deviation_detector):
        """Test that Deviation Detector has proper OpenAI Agents SDK function tools"""
        # This test will FAIL initially (RED phase)

        # Should have minimal function tools focused on deviation detection
        assert hasattr(deviation_detector, "agent")
        assert hasattr(deviation_detector.agent, "tools")

        # Expected function tools for deviation detection
        expected_tools = [
            "detect_protocol_deviations",
            "classify_deviation_severity",
            "assess_compliance_impact",
            "generate_corrective_actions",
        ]

        # At least some of these tools should be present
        tool_names = [tool.__name__ for tool in deviation_detector.agent.tools]
        assert len(tool_names) >= 3
        assert any("detect" in name or "deviation" in name for name in tool_names)

    async def test_deviation_response_format_consistency(
        self, deviation_detector, protocol_violation_data
    ):
        """Test that Deviation Detector returns consistent response format"""
        # This test will FAIL initially (RED phase)
        result = await deviation_detector.detect_protocol_deviations(
            protocol_violation_data
        )

        # Should match DeviationDetectionResponse schema structure
        required_fields = [
            "success",
            "deviations",
            "total_deviations_found",
            "compliance_status",
            "subject_id",
            "site_id",
            "visit",
            "detection_date",
            "recommendations",
            "corrective_actions_required",
            "human_readable_summary",
            "deviation_summary",
            "compliance_assessment",
            "execution_time",
            "agent_id",
        ]

        for field in required_fields:
            assert field in result, f"Missing required field: {field}"

        # Each deviation should have proper structure
        for deviation in result["deviations"]:
            deviation_fields = [
                "category",
                "severity",
                "protocol_requirement",
                "actual_value",
                "impact_level",
                "corrective_action_required",
                "deviation_description",
                "confidence",
            ]
            for field in deviation_fields:
                assert field in deviation, f"Missing deviation field: {field}"

    async def test_deviation_medical_context_integration(self, deviation_detector):
        """Test that Deviation Detector integrates medical context for clinical deviations"""
        medical_deviation_data = {
            "protocol_data": {
                "maximum_systolic_bp": "140",
                "minimum_hemoglobin": "10.0",
                "prohibited_medications": ["aspirin"],
            },
            "actual_data": {
                "systolic_bp": "165",
                "hemoglobin": "8.5",
                "concomitant_medications": ["aspirin", "metformin"],
            },
            "subject_id": "SUBJ013",
            "site_id": "SITE02",
            "visit": "Week 8",
        }

        # This test will FAIL initially (RED phase)
        result = await deviation_detector.detect_protocol_deviations(
            medical_deviation_data
        )

        assert result["success"] is True
        assert result["total_deviations_found"] >= 3  # BP, Hemoglobin, Medication

        # Should have medical context in human-readable fields
        clinical_terms = ["blood pressure", "hemoglobin", "anemia", "hypertension"]
        summary = result["human_readable_summary"].lower()
        assert any(term in summary for term in clinical_terms)

        # Should classify medical deviations appropriately
        medical_deviations = [
            d
            for d in result["deviations"]
            if d["category"] in ["vital_signs", "laboratory_value"]
        ]
        assert len(medical_deviations) >= 2


class TestDeviationDetectorIntegration:
    """Test Deviation Detector integration with other agents"""

    @pytest.fixture
    def deviation_detector(self):
        return DeviationDetector()

    async def test_deviation_detector_portfolio_manager_integration(
        self, deviation_detector
    ):
        """Test that Deviation Detector integrates properly with Portfolio Manager"""
        # This test will FAIL initially (RED phase)

        # Should work with Portfolio Manager's orchestration
        from app.agents.portfolio_manager import PortfolioManager

        portfolio_manager = PortfolioManager()

        deviation_request = {
            "workflow_type": "deviation_detection",
            "input_data": {
                "protocol_data": {"prohibited_medications": ["aspirin"]},
                "actual_data": {"concomitant_medications": ["aspirin"]},
                "subject_id": "SUBJ014",
                "site_id": "SITE01",
                "visit": "Week 1",
            },
            "workflow_id": "WF_DEVIATION_001",
        }

        result = await portfolio_manager.orchestrate_structured_workflow(
            deviation_request
        )

        # Should successfully orchestrate deviation detection
        assert result["success"] is True
        assert result["workflow_type"] == "deviation_detection"
        assert result["agent_coordination"]["primary_agent"] == "deviation_detector"

        # Should have deviation detection results
        response_data = result["response_data"]
        assert "deviations" in response_data
        assert "total_deviations_found" in response_data

    async def test_deviation_detector_structured_endpoint_compatibility(
        self, deviation_detector
    ):
        """Test that Deviation Detector works with structured endpoints"""
        # This test will FAIL initially (RED phase)

        # Should be compatible with /api/v1/deviations/detect endpoint format
        endpoint_data = {
            "subject_id": "SUBJ015",
            "site_id": "SITE01",
            "visit": "Week 12",
            "protocol_data": {
                "required_visit_window": "±3 days",
                "prohibited_medications": ["warfarin"],
            },
            "actual_data": {
                "visit_date": "2025-01-15",
                "scheduled_date": "2025-01-08",
                "concomitant_medications": ["warfarin"],
            },
        }

        result = await deviation_detector.detect_protocol_deviations(endpoint_data)

        # Should return format compatible with DeviationDetectionResponse
        assert result["success"] is True
        assert "deviation_id" in result or "detection_id" in result
        assert result["subject_id"] == "SUBJ015"
        assert result["site_id"] == "SITE01"

        # Should detect both deviations
        assert result["total_deviations_found"] == 2
        deviation_categories = [d["category"] for d in result["deviations"]]
        assert "visit_window" in deviation_categories
        assert "prohibited_medication" in deviation_categories


class TestDeviationDetectorPerformance:
    """Test Deviation Detector performance and efficiency"""

    @pytest.fixture
    def deviation_detector(self):
        return DeviationDetector()

    async def test_deviation_detection_performance(self, deviation_detector):
        """Test that Deviation Detector performs efficiently"""
        # This test will FAIL initially (RED phase)

        large_dataset = []
        for i in range(50):  # 50 subjects
            large_dataset.append(
                {
                    "protocol_data": {
                        "prohibited_medications": ["aspirin", "warfarin"]
                    },
                    "actual_data": {
                        "concomitant_medications": [
                            "aspirin" if i % 2 == 0 else "metformin"
                        ]
                    },
                    "subject_id": f"SUBJ{i:03d}",
                    "site_id": f"SITE{(i % 3) + 1:02d}",
                    "visit": "Week 1",
                }
            )

        start_time = datetime.now()
        result = await deviation_detector.batch_detect_deviations(large_dataset)
        execution_time = (datetime.now() - start_time).total_seconds()

        # Should complete efficiently
        assert result["success"] is True
        assert execution_time < 5.0  # Should complete in under 5 seconds

        # Should process all subjects
        assert len(result["batch_results"]) == 50

        # Should have performance metrics
        assert "execution_time" in result
        assert result["execution_time"] < 5.0

    async def test_deviation_detector_minimal_memory_usage(self, deviation_detector):
        """Test that Deviation Detector uses minimal memory (minimal responsibilities)"""
        # This test will FAIL initially (RED phase)

        # Should only store essential deviation detection context
        assert hasattr(deviation_detector, "context")

        # Context should be focused on deviation detection only
        context_attrs = [
            attr for attr in dir(deviation_detector.context) if not attr.startswith("_")
        ]
        deviation_related = [
            attr
            for attr in context_attrs
            if "deviation" in attr.lower() or "compliance" in attr.lower()
        ]

        # Should have deviation-specific context fields
        assert len(deviation_related) >= 1

        # Should not have unnecessary fields from other agents (excluding Pydantic methods)
        pydantic_methods = [
            "construct",
            "from_orm",
            "model_computed_fields",
            "model_config",
            "model_construct",
            "model_copy",
            "model_dump",
            "model_dump_json",
            "model_extra",
            "model_fields",
            "model_fields_set",
            "model_json_schema",
            "model_parametrized_name",
            "model_post_init",
            "model_rebuild",
            "model_validate",
            "model_validate_json",
            "model_validate_strings",
            "parse_file",
            "parse_obj",
            "parse_raw",
            "schema",
            "schema_json",
            "update_forward_refs",
            "validate",
        ]
        non_deviation_attrs = [
            attr
            for attr in context_attrs
            if attr not in deviation_related
            and attr not in ["dict", "json", "copy", "update"]
            and attr not in pydantic_methods
        ]
        assert (
            len(non_deviation_attrs) <= 5
        )  # Minimal non-deviation fields only (excluding Pydantic methods)
