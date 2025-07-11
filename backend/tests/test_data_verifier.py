"""Tests for Data Verifier Agent - Source Data Verification functionality."""

import json
from datetime import datetime
from typing import Any, Dict, List
from unittest.mock import AsyncMock, Mock, patch

import pytest

from app.agents.base_agent import AgentResponse
from app.agents.data_verifier import (
    CriticalDataField,
    DataDiscrepancy,
    DataVerifier,
    DiscrepancySeverity,
    DiscrepancyType,
    RiskAssessment,
    VerificationResult,
)


class TestDataVerifierCore:
    """Test core Data Verifier functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.data_verifier = DataVerifier()

        # Sample test data
        self.edc_data = {
            "subject_id": "S001",
            "visit": "V1",
            "vital_signs": {
                "systolic_bp": 120,
                "diastolic_bp": 80,
                "heart_rate": 72,
                "temperature": 98.6,
            },
            "adverse_events": [],
            "concomitant_meds": ["Aspirin 81mg"],
        }

        self.source_data = {
            "subject_id": "S001",
            "visit": "V1",
            "vital_signs": {
                "systolic_bp": 125,  # Discrepancy
                "diastolic_bp": 80,
                "heart_rate": 72,
                "temperature": 98.7,  # Minor discrepancy
            },
            "adverse_events": [
                {"term": "Headache", "severity": "Mild"}
            ],  # Missing in EDC
            "concomitant_meds": ["Aspirin 81mg"],
        }

    def test_data_verifier_initialization(self):
        """Test Data Verifier agent initialization."""
        assert self.data_verifier.agent_id == "data-verifier"
        assert self.data_verifier.name == "Data Verifier"
        assert (
            "verifying and validating clinical trial data"
            in self.data_verifier.description
        )
        assert hasattr(self.data_verifier, "confidence_threshold")
        assert hasattr(self.data_verifier, "critical_fields")
        assert hasattr(self.data_verifier, "discrepancy_tolerance")

    @pytest.mark.asyncio
    async def test_cross_system_verification_basic(self):
        """Test basic cross-system data verification."""
        # Mock the AI response for verification
        mock_response = AgentResponse(
            success=True,
            content=json.dumps(
                {
                    "discrepancies_found": 3,
                    "discrepancies": [
                        {
                            "field": "vital_signs.systolic_bp",
                            "edc_value": 120,
                            "source_value": 125,
                            "difference": 5,
                            "severity": "minor",
                            "confidence": 0.95,
                        },
                        {
                            "field": "vital_signs.temperature",
                            "edc_value": 98.6,
                            "source_value": 98.7,
                            "difference": 0.1,
                            "severity": "minor",
                            "confidence": 0.92,
                        },
                        {
                            "field": "adverse_events",
                            "edc_value": [],
                            "source_value": [{"term": "Headache", "severity": "Mild"}],
                            "difference": "missing_in_edc",
                            "severity": "major",
                            "confidence": 0.98,
                        },
                    ],
                    "matches": [
                        "vital_signs.diastolic_bp",
                        "vital_signs.heart_rate",
                        "concomitant_meds",
                    ],
                    "overall_accuracy": 0.75,
                }
            ),
            agent_id="data-verifier",
            execution_time=2.1,
            metadata={"verification_type": "cross_system"},
        )

        with patch.object(
            self.data_verifier, "process_message", new_callable=AsyncMock
        ) as mock_process:
            mock_process.return_value = mock_response

            result = await self.data_verifier.cross_system_verification(
                self.edc_data, self.source_data
            )

            # Verify the result structure
            assert isinstance(result, VerificationResult)
            assert result.subject_id == "S001"
            assert result.visit == "V1"
            assert result.discrepancies_found == 3
            assert len(result.discrepancies) == 3
            assert result.overall_accuracy == 0.75

            # Check specific discrepancies
            bp_discrepancy = next(
                d
                for d in result.discrepancies
                if d.field_name == "vital_signs.systolic_bp"
            )
            assert bp_discrepancy.edc_value == 120
            assert bp_discrepancy.source_value == 125
            assert bp_discrepancy.severity == DiscrepancySeverity.MINOR

    @pytest.mark.asyncio
    async def test_critical_data_identification(self):
        """Test identification of critical data fields."""
        critical_data = {
            "subject_id": "S002",
            "adverse_events": [
                {"term": "Myocardial infarction", "severity": "Life-threatening"},
                {"term": "Death", "outcome": "Fatal"},
            ],
            "vital_signs": {
                "systolic_bp": 220,  # Critically high
                "diastolic_bp": 130,  # Critically high
            },
            "eligibility": {"inclusion_criteria": False},  # Critical protocol violation
        }

        mock_response = AgentResponse(
            success=True,
            content=json.dumps(
                {
                    "critical_fields_identified": 4,
                    "critical_fields": [
                        {
                            "field": "adverse_events.myocardial_infarction",
                            "risk_level": "critical",
                            "reason": "Life-threatening serious adverse event",
                            "immediate_action_required": True,
                            "regulatory_reporting_required": True,
                        },
                        {
                            "field": "adverse_events.death",
                            "risk_level": "critical",
                            "reason": "Fatal outcome - immediate reporting required",
                            "immediate_action_required": True,
                            "regulatory_reporting_required": True,
                        },
                        {
                            "field": "vital_signs.blood_pressure",
                            "risk_level": "critical",
                            "reason": "Hypertensive crisis - safety concern",
                            "immediate_action_required": True,
                            "regulatory_reporting_required": False,
                        },
                        {
                            "field": "eligibility.inclusion_criteria",
                            "risk_level": "critical",
                            "reason": "Protocol deviation - subject ineligible",
                            "immediate_action_required": True,
                            "regulatory_reporting_required": True,
                        },
                    ],
                    "overall_risk_score": 0.95,
                }
            ),
            agent_id="data-verifier",
            execution_time=1.8,
            metadata={"analysis_type": "critical_data"},
        )

        with patch.object(
            self.data_verifier, "process_message", new_callable=AsyncMock
        ) as mock_process:
            mock_process.return_value = mock_response

            risk_assessment = await self.data_verifier.assess_critical_data(
                critical_data
            )

            # Verify risk assessment
            assert isinstance(risk_assessment, RiskAssessment)
            assert risk_assessment.overall_risk_score == 0.95
            assert len(risk_assessment.critical_fields) == 4
            assert risk_assessment.requires_immediate_action is True

            # Check specific critical fields
            ae_field = next(
                f
                for f in risk_assessment.critical_fields
                if f.field_name == "adverse_events.myocardial_infarction"
            )
            assert ae_field.risk_level == "critical"
            assert ae_field.regulatory_reporting_required is True

    @pytest.mark.asyncio
    async def test_discrepancy_pattern_detection(self):
        """Test detection of patterns in discrepancies across multiple subjects."""
        historical_discrepancies = [
            {
                "subject_id": "S001",
                "site_id": "Site_001",
                "discrepancy": "vital_signs.systolic_bp",
                "difference": 5,
                "timestamp": "2025-01-15",
            },
            {
                "subject_id": "S002",
                "site_id": "Site_001",
                "discrepancy": "vital_signs.systolic_bp",
                "difference": 8,
                "timestamp": "2025-01-16",
            },
            {
                "subject_id": "S003",
                "site_id": "Site_001",
                "discrepancy": "vital_signs.systolic_bp",
                "difference": 6,
                "timestamp": "2025-01-17",
            },
            {
                "subject_id": "S004",
                "site_id": "Site_002",
                "discrepancy": "laboratory.glucose",
                "difference": 15,
                "timestamp": "2025-01-18",
            },
        ]

        mock_response = AgentResponse(
            success=True,
            content=json.dumps(
                {
                    "patterns_detected": 2,
                    "patterns": [
                        {
                            "pattern_type": "site_specific",
                            "description": "Site_001 consistently reports lower systolic BP values",
                            "affected_subjects": ["S001", "S002", "S003"],
                            "affected_sites": ["Site_001"],
                            "pattern_strength": 0.92,
                            "suggested_actions": [
                                "Investigate BP measurement equipment at Site_001",
                                "Provide additional training to Site_001 staff",
                                "Audit Site_001 procedures",
                            ],
                        },
                        {
                            "pattern_type": "field_specific",
                            "description": "Vital signs measurements show systematic differences",
                            "affected_fields": ["vital_signs.systolic_bp"],
                            "pattern_strength": 0.88,
                            "suggested_actions": [
                                "Review vital signs measurement SOPs",
                                "Calibrate measurement equipment",
                            ],
                        },
                    ],
                }
            ),
            agent_id="data-verifier",
            execution_time=3.2,
            metadata={"analysis_type": "pattern_detection"},
        )

        with patch.object(
            self.data_verifier, "process_message", new_callable=AsyncMock
        ) as mock_process:
            mock_process.return_value = mock_response

            patterns = await self.data_verifier.detect_discrepancy_patterns(
                historical_discrepancies
            )

            # Verify pattern detection
            assert patterns["patterns_detected"] == 2
            assert len(patterns["patterns"]) == 2

            site_pattern = patterns["patterns"][0]
            assert site_pattern["pattern_type"] == "site_specific"
            assert "Site_001" in site_pattern["description"]
            assert len(site_pattern["affected_subjects"]) == 3

    @pytest.mark.asyncio
    async def test_audit_trail_generation(self):
        """Test generation of comprehensive audit trails."""
        verification_data = {
            "verification_id": "VER_001",
            "subject_id": "S001",
            "verifier": "data-verifier-agent",
            "verification_type": "cross_system",
            "discrepancies_found": 2,
            "actions_taken": ["Query generated", "Site notification sent"],
            "timestamp": datetime.now().isoformat(),
        }

        mock_response = AgentResponse(
            success=True,
            content=json.dumps(
                {
                    "audit_trail_created": True,
                    "audit_id": "AUDIT_VER_001_20250129",
                    "trail_entries": [
                        {
                            "timestamp": "2025-01-29T10:00:00Z",
                            "action": "verification_initiated",
                            "user": "data-verifier-agent",
                            "details": "Cross-system verification started for S001",
                        },
                        {
                            "timestamp": "2025-01-29T10:02:00Z",
                            "action": "discrepancies_detected",
                            "user": "data-verifier-agent",
                            "details": "2 discrepancies found in vital signs data",
                        },
                        {
                            "timestamp": "2025-01-29T10:03:00Z",
                            "action": "query_generated",
                            "user": "data-verifier-agent",
                            "details": "Automatic query created for BP discrepancy",
                        },
                        {
                            "timestamp": "2025-01-29T10:04:00Z",
                            "action": "notification_sent",
                            "user": "data-verifier-agent",
                            "details": "Site notification sent to investigate discrepancies",
                        },
                    ],
                    "compliance_status": "compliant_21cfr11",
                }
            ),
            agent_id="data-verifier",
            execution_time=0.8,
            metadata={"audit_type": "verification"},
        )

        with patch.object(
            self.data_verifier, "process_message", new_callable=AsyncMock
        ) as mock_process:
            mock_process.return_value = mock_response

            audit_trail = await self.data_verifier.generate_audit_trail(
                verification_data
            )

            # Verify audit trail
            assert audit_trail["audit_trail_created"] is True
            assert "AUDIT_VER_001" in audit_trail["audit_id"]
            assert len(audit_trail["trail_entries"]) == 4
            assert audit_trail["compliance_status"] == "compliant_21cfr11"

            # Check specific trail entries
            init_entry = audit_trail["trail_entries"][0]
            assert init_entry["action"] == "verification_initiated"
            assert "S001" in init_entry["details"]


class TestDataVerifierEdgeCases:
    """Test edge cases and error handling for Data Verifier."""

    def setup_method(self):
        """Set up test fixtures."""
        self.data_verifier = DataVerifier()

    @pytest.mark.asyncio
    async def test_verification_with_missing_fields(self):
        """Test verification when data has missing fields."""
        incomplete_edc = {"subject_id": "S001"}
        incomplete_source = {"subject_id": "S001", "visit": "V1"}

        mock_response = AgentResponse(
            success=True,
            content=json.dumps(
                {
                    "discrepancies_found": 1,
                    "discrepancies": [
                        {
                            "field": "visit",
                            "edc_value": None,
                            "source_value": "V1",
                            "difference": "missing_in_edc",
                            "severity": "major",
                            "confidence": 1.0,
                        }
                    ],
                    "matches": [],
                    "overall_accuracy": 0.0,
                    "data_completeness": {
                        "edc_completeness": 0.2,
                        "source_completeness": 0.4,
                    },
                }
            ),
            agent_id="data-verifier",
            execution_time=1.1,
        )

        with patch.object(
            self.data_verifier, "process_message", new_callable=AsyncMock
        ) as mock_process:
            mock_process.return_value = mock_response

            result = await self.data_verifier.cross_system_verification(
                incomplete_edc, incomplete_source
            )

            assert result.discrepancies_found == 1
            assert result.overall_accuracy == 0.0
            assert "data_completeness" in result.metadata

    @pytest.mark.asyncio
    async def test_verification_failure_handling(self):
        """Test handling of verification failures."""
        mock_response = AgentResponse(
            success=False,
            content="",
            agent_id="data-verifier",
            execution_time=0.5,
            error="OpenAI API rate limit exceeded",
        )

        with patch.object(
            self.data_verifier, "process_message", new_callable=AsyncMock
        ) as mock_process:
            mock_process.return_value = mock_response

            with pytest.raises(
                Exception, match="Verification failed: OpenAI API rate limit exceeded"
            ):
                await self.data_verifier.cross_system_verification({}, {})

    @pytest.mark.asyncio
    async def test_invalid_json_response_handling(self):
        """Test handling of invalid JSON responses from AI."""
        mock_response = AgentResponse(
            success=True,
            content="This is not valid JSON",
            agent_id="data-verifier",
            execution_time=1.0,
        )

        with patch.object(
            self.data_verifier, "process_message", new_callable=AsyncMock
        ) as mock_process:
            mock_process.return_value = mock_response

            with pytest.raises(
                Exception, match="Failed to parse verification response"
            ):
                await self.data_verifier.cross_system_verification({}, {})

    def test_confidence_threshold_validation(self):
        """Test confidence threshold validation."""
        # Valid threshold
        self.data_verifier.set_confidence_threshold(0.8)
        assert self.data_verifier.confidence_threshold == 0.8

        # Invalid thresholds
        with pytest.raises(
            ValueError, match="Confidence threshold must be between 0.0 and 1.0"
        ):
            self.data_verifier.set_confidence_threshold(1.5)

        with pytest.raises(
            ValueError, match="Confidence threshold must be between 0.0 and 1.0"
        ):
            self.data_verifier.set_confidence_threshold(-0.1)

    def test_tolerance_configuration(self):
        """Test discrepancy tolerance configuration."""
        # Test setting tolerance for different field types
        self.data_verifier.set_field_tolerance("vital_signs.systolic_bp", 5.0)
        self.data_verifier.set_field_tolerance("laboratory.glucose", 10.0)

        assert self.data_verifier.get_field_tolerance("vital_signs.systolic_bp") == 5.0
        assert self.data_verifier.get_field_tolerance("laboratory.glucose") == 10.0
        assert self.data_verifier.get_field_tolerance("unknown_field") == 0.0  # Default


class TestDataVerifierPerformance:
    """Test Data Verifier performance and metrics."""

    def setup_method(self):
        """Set up test fixtures."""
        self.data_verifier = DataVerifier()

    def test_performance_metrics_tracking(self):
        """Test performance metrics tracking."""
        initial_metrics = self.data_verifier.get_performance_metrics()

        assert "verifications_performed" in initial_metrics
        assert "total_verification_time" in initial_metrics
        assert "average_verification_time" in initial_metrics
        assert "accuracy_rate" in initial_metrics
        assert initial_metrics["verifications_performed"] == 0

    @pytest.mark.asyncio
    async def test_batch_verification_performance(self):
        """Test batch verification performance."""
        # Create multiple data sets for batch processing
        batch_data = []
        for i in range(5):
            edc_data = {"subject_id": f"S{i:03d}", "visit": "V1", "data": f"value_{i}"}
            source_data = {
                "subject_id": f"S{i:03d}",
                "visit": "V1",
                "data": f"value_{i}_source",
            }
            batch_data.append((edc_data, source_data))

        mock_response = AgentResponse(
            success=True,
            content=json.dumps(
                {
                    "batch_results": [
                        {
                            "subject_id": f"S{i:03d}",
                            "discrepancies_found": 1,
                            "accuracy": 0.8,
                        }
                        for i in range(5)
                    ],
                    "overall_batch_accuracy": 0.8,
                    "processing_time": 3.5,
                }
            ),
            agent_id="data-verifier",
            execution_time=3.5,
        )

        with patch.object(
            self.data_verifier, "process_message", new_callable=AsyncMock
        ) as mock_process:
            mock_process.return_value = mock_response

            results = await self.data_verifier.batch_verification(batch_data)

            assert len(results["batch_results"]) == 5
            assert results["overall_batch_accuracy"] == 0.8
            assert results["processing_time"] == 3.5


# Test fixtures for complex data structures
@pytest.fixture
def sample_edc_data():
    """Sample EDC data for testing."""
    return {
        "subject_id": "S001",
        "site_id": "SITE_001",
        "visit": "Screening",
        "demographics": {"age": 45, "gender": "Female", "race": "Caucasian"},
        "vital_signs": {
            "systolic_bp": 120,
            "diastolic_bp": 80,
            "heart_rate": 72,
            "temperature": 98.6,
            "weight": 65.5,
            "height": 165,
        },
        "laboratory": {"glucose": 95, "cholesterol": 180, "hemoglobin": 12.5},
        "adverse_events": [],
        "concomitant_medications": ["Lisinopril 10mg", "Metformin 500mg"],
    }


@pytest.fixture
def sample_source_data():
    """Sample source data for testing."""
    return {
        "subject_id": "S001",
        "site_id": "SITE_001",
        "visit": "Screening",
        "demographics": {"age": 45, "gender": "Female", "race": "Caucasian"},
        "vital_signs": {
            "systolic_bp": 125,  # 5 point discrepancy
            "diastolic_bp": 80,
            "heart_rate": 72,
            "temperature": 98.7,  # 0.1 point discrepancy
            "weight": 65.5,
            "height": 165,
        },
        "laboratory": {
            "glucose": 110,  # 15 point discrepancy
            "cholesterol": 180,
            "hemoglobin": 12.5,
        },
        "adverse_events": [
            {"term": "Headache", "severity": "Mild", "start_date": "2025-01-15"}
        ],  # Missing in EDC
        "concomitant_medications": ["Lisinopril 10mg", "Metformin 500mg"],
    }


class TestDataVerifierIntegration:
    """Integration tests for Data Verifier with real-world scenarios."""

    def setup_method(self):
        """Set up test fixtures."""
        self.data_verifier = DataVerifier()

    @pytest.mark.asyncio
    async def test_end_to_end_verification_workflow(
        self, sample_edc_data, sample_source_data
    ):
        """Test complete end-to-end verification workflow."""
        # Mock comprehensive verification response
        mock_response = AgentResponse(
            success=True,
            content=json.dumps(
                {
                    "verification_summary": {
                        "subject_id": "S001",
                        "verification_type": "complete_sdv",
                        "discrepancies_found": 3,
                        "critical_discrepancies": 0,
                        "overall_accuracy": 0.85,
                    },
                    "discrepancies": [
                        {
                            "field": "vital_signs.systolic_bp",
                            "edc_value": 120,
                            "source_value": 125,
                            "difference": 5,
                            "severity": "minor",
                            "confidence": 0.95,
                            "requires_query": True,
                        },
                        {
                            "field": "vital_signs.temperature",
                            "edc_value": 98.6,
                            "source_value": 98.7,
                            "difference": 0.1,
                            "severity": "minor",
                            "confidence": 0.92,
                            "requires_query": False,
                        },
                        {
                            "field": "adverse_events",
                            "edc_value": [],
                            "source_value": [{"term": "Headache", "severity": "Mild"}],
                            "difference": "missing_in_edc",
                            "severity": "major",
                            "confidence": 0.98,
                            "requires_query": True,
                        },
                    ],
                    "risk_assessment": {
                        "overall_risk": "low",
                        "critical_fields_affected": 0,
                        "regulatory_impact": "minimal",
                    },
                    "recommended_actions": [
                        "Generate query for systolic BP discrepancy",
                        "Generate query for missing adverse event",
                        "Schedule follow-up verification in 30 days",
                    ],
                }
            ),
            agent_id="data-verifier",
            execution_time=4.2,
            metadata={"verification_type": "complete_sdv"},
        )

        with patch.object(
            self.data_verifier, "process_message", new_callable=AsyncMock
        ) as mock_process:
            mock_process.return_value = mock_response

            result = await self.data_verifier.complete_sdv_verification(
                sample_edc_data, sample_source_data
            )

            # Verify comprehensive results
            assert result.verification_summary["subject_id"] == "S001"
            assert result.verification_summary["discrepancies_found"] == 3
            assert result.verification_summary["overall_accuracy"] == 0.85

            # Check that critical discrepancies are properly identified
            critical_discrepancies = [
                d for d in result.discrepancies if d.severity == "critical"
            ]
            assert len(critical_discrepancies) == 0

            # Verify recommended actions are provided
            assert len(result.recommended_actions) == 3
            assert any(
                "query" in action.lower() for action in result.recommended_actions
            )
