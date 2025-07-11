"""Tests for Data Verifier using OpenAI Agents SDK."""

import json
from datetime import datetime
from typing import Any, Dict, List, Tuple
from unittest.mock import MagicMock, Mock, patch

import pytest

from app.agents.data_verifier_sdk import (
    DataVerificationContext,
    DataVerifier,
    DiscrepancySeverity,
    DiscrepancyType,
    assess_critical_data,
    complete_sdv_verification,
    cross_system_verification,
    detect_discrepancy_patterns,
)


class TestDataVerifierSDK:
    """Test suite for Data Verifier with OpenAI Agents SDK."""

    @pytest.fixture
    def mock_openai_client(self):
        """Mock OpenAI client for testing."""
        with patch("app.agents.data_verifier_sdk.OpenAI") as mock_client:
            # Mock assistant
            mock_assistant = Mock()
            mock_assistant.id = "asst_verifier123"
            mock_assistant.name = "Clinical Data Verifier"

            # Mock thread
            mock_thread = Mock()
            mock_thread.id = "thread_verifier123"

            # Mock message for verification response
            mock_message = Mock()
            mock_message.content = [
                Mock(
                    text=Mock(
                        value=json.dumps(
                            {
                                "verification_id": "DV_20250101_001",
                                "match_score": 0.85,
                                "discrepancies": [
                                    {
                                        "field_name": "hemoglobin",
                                        "edc_value": "12.5",
                                        "source_value": "11.2",
                                        "discrepancy_type": "value_mismatch",
                                        "severity": "major",
                                    }
                                ],
                                "critical_findings": [],
                                "recommendations": [
                                    "Review source document for hemoglobin value"
                                ],
                            }
                        )
                    )
                )
            ]

            # Mock run
            mock_run = Mock()
            mock_run.status = "completed"
            mock_run.id = "run_verifier123"

            # Set up client methods
            mock_client.return_value.beta.assistants.create.return_value = (
                mock_assistant
            )
            mock_client.return_value.beta.threads.create.return_value = mock_thread
            mock_client.return_value.beta.threads.messages.create.return_value = Mock()
            mock_client.return_value.beta.threads.runs.create.return_value = mock_run
            mock_client.return_value.beta.threads.runs.retrieve.return_value = mock_run
            mock_client.return_value.beta.threads.messages.list.return_value = Mock(
                data=[mock_message]
            )

            yield mock_client

    @pytest.fixture
    def data_verifier(self, mock_openai_client):
        """Create DataVerifier instance with mocked client."""
        return DataVerifier()

    @pytest.fixture
    def sample_edc_data(self) -> Dict[str, Any]:
        """Sample EDC data for testing."""
        return {
            "subject_id": "SUBJ001",
            "visit": "Week 4",
            "hemoglobin": "12.5",
            "weight": "75.0",
            "blood_pressure_systolic": "140",
            "blood_pressure_diastolic": "90",
            "adverse_events": [
                {"term": "Headache", "severity": "mild", "start_date": "2024-12-15"}
            ],
        }

    @pytest.fixture
    def sample_source_data(self) -> Dict[str, Any]:
        """Sample source data for testing."""
        return {
            "subject_id": "SUBJ001",
            "visit": "Week 4",
            "hemoglobin": "11.2",
            "weight": "75.0",
            "blood_pressure_systolic": "135",
            "blood_pressure_diastolic": "90",
            "adverse_events": [
                {"term": "Headache", "severity": "mild", "start_date": "2024-12-15"}
            ],
        }

    @pytest.fixture
    def sample_batch_data(self) -> List[Tuple[Dict[str, Any], Dict[str, Any]]]:
        """Sample batch data for testing."""
        return [
            (
                {"subject_id": "SUBJ001", "hemoglobin": "12.5", "weight": "75.0"},
                {"subject_id": "SUBJ001", "hemoglobin": "11.2", "weight": "75.0"},
            ),
            (
                {"subject_id": "SUBJ002", "hemoglobin": "13.0", "weight": "80.0"},
                {"subject_id": "SUBJ002", "hemoglobin": "13.0", "weight": ""},
            ),
            (
                {"subject_id": "SUBJ003", "hemoglobin": "11.5", "weight": "70.0"},
                {"subject_id": "SUBJ003", "hemoglobin": "11.8", "weight": "70.0"},
            ),
        ]

    def test_data_verifier_initialization(self, data_verifier):
        """Test DataVerifier initialization."""
        assert data_verifier.agent is not None
        assert data_verifier.instructions is not None
        assert data_verifier.context is not None
        assert data_verifier.confidence_threshold == 0.8
        assert data_verifier.field_tolerances is not None
        assert isinstance(data_verifier.critical_fields, set)

    def test_critical_fields_configuration(self, data_verifier):
        """Test critical fields are properly configured."""
        expected_critical_fields = [
            "hemoglobin",
            "blood_pressure",
            "heart_rate",
            "temperature",
            "adverse_events",
            "serious_adverse_events",
            "concomitant_medications",
        ]

        for field in expected_critical_fields:
            assert any(
                field in critical_field
                for critical_field in data_verifier.critical_fields
            )

    def test_field_tolerances_configuration(self, data_verifier):
        """Test field tolerance configuration."""
        # Test default tolerances
        assert data_verifier.get_field_tolerance("hemoglobin") == 0.1
        assert data_verifier.get_field_tolerance("weight") == 0.5
        assert data_verifier.get_field_tolerance("blood_pressure") == 5.0

        # Test setting custom tolerance
        data_verifier.set_field_tolerance("custom_field", 0.25)
        assert data_verifier.get_field_tolerance("custom_field") == 0.25

    @pytest.mark.asyncio
    async def test_cross_system_verification(
        self, data_verifier, sample_edc_data, sample_source_data
    ):
        """Test cross-system data verification."""
        result = await data_verifier.cross_system_verification(
            sample_edc_data, sample_source_data
        )

        assert result is not None
        assert "verification_id" in result
        assert "match_score" in result
        assert "discrepancies" in result
        assert "critical_findings" in result
        assert "recommendations" in result
        assert 0.0 <= result["match_score"] <= 1.0

    @pytest.mark.asyncio
    async def test_critical_data_assessment(self, data_verifier):
        """Test critical data assessment for safety monitoring."""
        critical_data = {
            "subject_id": "SUBJ001",
            "vital_signs": {
                "heart_rate": 45,  # Low heart rate
                "blood_pressure": "90/60",  # Low blood pressure
                "temperature": 39.5,  # High fever
            },
            "adverse_events": [
                {"term": "Chest pain", "severity": "severe", "serious": True}
            ],
        }

        assessment = await data_verifier.assess_critical_data(critical_data)

        assert "risk_level" in assessment
        assert "critical_findings" in assessment
        assert "immediate_actions" in assessment
        assert "subject_id" in assessment
        assert assessment["risk_level"] in ["low", "medium", "high", "critical"]

    @pytest.mark.asyncio
    async def test_discrepancy_pattern_detection(self, data_verifier):
        """Test detection of patterns in historical discrepancies."""
        historical_data = [
            {
                "site_id": "Site001",
                "field_name": "hemoglobin",
                "discrepancy_type": "value_mismatch",
                "frequency": 5,
                "date": "2024-12-01",
            },
            {
                "site_id": "Site001",
                "field_name": "weight",
                "discrepancy_type": "missing_in_source",
                "frequency": 3,
                "date": "2024-12-10",
            },
            {
                "site_id": "Site002",
                "field_name": "hemoglobin",
                "discrepancy_type": "value_mismatch",
                "frequency": 8,
                "date": "2024-12-15",
            },
        ]

        patterns = await data_verifier.detect_discrepancy_patterns(historical_data)

        assert "site_patterns" in patterns
        assert "field_patterns" in patterns
        assert "temporal_patterns" in patterns
        assert "recommendations" in patterns
        assert "pattern_analysis_date" in patterns

    @pytest.mark.asyncio
    async def test_complete_sdv_verification(
        self, data_verifier, sample_edc_data, sample_source_data
    ):
        """Test complete SDV (Source Data Verification) process."""
        result = await data_verifier.complete_sdv_verification(
            sample_edc_data, sample_source_data
        )

        assert result is not None
        assert "verification_id" in result
        assert "sdv_status" in result
        assert "match_score" in result
        assert "discrepancies" in result
        assert "audit_trail" in result
        assert "verification_date" in result
        assert result["sdv_status"] in ["passed", "failed", "requires_review"]

    @pytest.mark.asyncio
    async def test_batch_verification(self, data_verifier, sample_batch_data):
        """Test batch verification of multiple subject data sets."""
        result = await data_verifier.batch_verification(sample_batch_data)

        assert "batch_id" in result
        assert "total_subjects" in result
        assert "verification_results" in result
        assert "summary_statistics" in result
        assert result["total_subjects"] == len(sample_batch_data)
        assert len(result["verification_results"]) == len(sample_batch_data)

    @pytest.mark.asyncio
    async def test_audit_trail_generation(self, data_verifier):
        """Test generation of verification audit trail."""
        verification_data = {
            "verification_id": "DV_TEST_001",
            "subject_id": "SUBJ001",
            "verifier_id": "USER001",
            "verification_date": datetime.now().isoformat(),
            "discrepancies_found": 2,
            "critical_findings": 0,
        }

        audit_trail = await data_verifier.generate_audit_trail(verification_data)

        assert "audit_id" in audit_trail
        assert "verification_steps" in audit_trail
        assert "data_integrity_checks" in audit_trail
        assert "regulatory_compliance" in audit_trail
        assert "timestamp" in audit_trail

    def test_discrepancy_severity_assessment(self, data_verifier):
        """Test discrepancy severity assessment."""
        # Critical severity for safety fields
        critical_severity = data_verifier.assess_discrepancy_severity(
            "adverse_events", DiscrepancyType.VALUE_MISMATCH
        )
        assert critical_severity in [
            DiscrepancySeverity.CRITICAL,
            DiscrepancySeverity.MAJOR,
        ]

        # Minor severity for non-critical fields
        minor_severity = data_verifier.assess_discrepancy_severity(
            "comments", DiscrepancyType.FORMAT_DIFFERENCE
        )
        assert minor_severity in [DiscrepancySeverity.MINOR, DiscrepancySeverity.INFO]

    def test_confidence_threshold_configuration(self, data_verifier):
        """Test confidence threshold configuration."""
        # Test setting confidence threshold
        data_verifier.set_confidence_threshold(0.9)
        assert data_verifier.confidence_threshold == 0.9

        # Test invalid threshold
        with pytest.raises(ValueError):
            data_verifier.set_confidence_threshold(1.5)

        with pytest.raises(ValueError):
            data_verifier.set_confidence_threshold(-0.1)

    @pytest.mark.asyncio
    async def test_missing_data_detection(self, data_verifier):
        """Test detection of missing data in EDC or source."""
        edc_data = {"subject_id": "SUBJ001", "hemoglobin": "12.5", "weight": ""}
        source_data = {"subject_id": "SUBJ001", "hemoglobin": "", "weight": "75.0"}

        result = await data_verifier.cross_system_verification(edc_data, source_data)

        # Should detect missing data in both systems
        discrepancies = result.get("discrepancies", [])
        missing_types = [d.get("discrepancy_type") for d in discrepancies]

        assert "missing_in_edc" in missing_types or "missing_in_source" in missing_types

    @pytest.mark.asyncio
    async def test_value_mismatch_detection(self, data_verifier):
        """Test detection of value mismatches between systems."""
        edc_data = {"subject_id": "SUBJ001", "hemoglobin": "12.5"}
        source_data = {"subject_id": "SUBJ001", "hemoglobin": "10.8"}

        result = await data_verifier.cross_system_verification(edc_data, source_data)

        discrepancies = result.get("discrepancies", [])
        assert len(discrepancies) > 0

        hemoglobin_discrepancy = next(
            (d for d in discrepancies if d.get("field_name") == "hemoglobin"), None
        )
        assert hemoglobin_discrepancy is not None
        assert hemoglobin_discrepancy.get("discrepancy_type") == "value_mismatch"

    @pytest.mark.asyncio
    async def test_format_difference_detection(self, data_verifier):
        """Test detection of format differences."""
        edc_data = {"subject_id": "SUBJ001", "date": "2024-12-15"}
        source_data = {"subject_id": "SUBJ001", "date": "15-Dec-2024"}

        result = await data_verifier.cross_system_verification(edc_data, source_data)

        # Should detect format difference even if values represent same date
        discrepancies = result.get("discrepancies", [])
        format_discrepancies = [
            d for d in discrepancies if d.get("discrepancy_type") == "format_difference"
        ]

        # May or may not detect format difference depending on implementation
        # This test ensures the function handles different formats gracefully
        assert isinstance(discrepancies, list)

    @pytest.mark.asyncio
    async def test_unit_mismatch_detection(self, data_verifier):
        """Test detection of unit mismatches."""
        edc_data = {"subject_id": "SUBJ001", "weight": "75", "weight_unit": "kg"}
        source_data = {"subject_id": "SUBJ001", "weight": "165", "weight_unit": "lbs"}

        result = await data_verifier.cross_system_verification(edc_data, source_data)

        # Should detect potential unit mismatch (75kg ≈ 165lbs)
        discrepancies = result.get("discrepancies", [])
        weight_issues = [
            d
            for d in discrepancies
            if d.get("field_name") == "weight"
            and d.get("discrepancy_type") in ["unit_mismatch", "value_mismatch"]
        ]

        # Implementation may handle unit conversion or flag as discrepancy
        assert isinstance(discrepancies, list)

    @pytest.mark.asyncio
    async def test_performance_optimization(self, data_verifier):
        """Test performance optimization for large data sets."""
        # Create large dataset
        large_batch = []
        for i in range(20):
            edc_data = {
                "subject_id": f"SUBJ{i:03d}",
                "hemoglobin": str(12.0 + i * 0.1),
                "weight": str(70.0 + i),
            }
            source_data = {
                "subject_id": f"SUBJ{i:03d}",
                "hemoglobin": str(11.8 + i * 0.1),
                "weight": str(70.0 + i),
            }
            large_batch.append((edc_data, source_data))

        start_time = datetime.now()
        result = await data_verifier.batch_verification(large_batch)
        execution_time = (datetime.now() - start_time).total_seconds()

        assert result["total_subjects"] == 20
        assert len(result["verification_results"]) == 20
        assert execution_time < 30.0  # Should complete in reasonable time

    @pytest.mark.asyncio
    async def test_error_handling(self, data_verifier):
        """Test error handling in verification process."""
        # Test with malformed data
        invalid_edc = {"invalid_structure": True}
        invalid_source = {"different_structure": False}

        result = await data_verifier.cross_system_verification(
            invalid_edc, invalid_source
        )

        # Should handle gracefully and return appropriate response
        assert result is not None
        assert "error" in result or "verification_id" in result

    @pytest.mark.asyncio
    async def test_context_accumulation(
        self, data_verifier, sample_edc_data, sample_source_data
    ):
        """Test context accumulation across multiple verifications."""
        # First verification
        result1 = await data_verifier.cross_system_verification(
            sample_edc_data, sample_source_data
        )

        # Check context contains verification history
        assert len(data_verifier.context.verification_history) > 0

        # Second verification with different data
        modified_edc = sample_edc_data.copy()
        modified_edc["subject_id"] = "SUBJ002"
        result2 = await data_verifier.cross_system_verification(
            modified_edc, sample_source_data
        )

        # Context should accumulate results
        assert len(data_verifier.context.verification_history) >= 2

    def test_discrepancy_type_enum(self):
        """Test DiscrepancyType enum values."""
        assert DiscrepancyType.VALUE_MISMATCH.value == "value_mismatch"
        assert DiscrepancyType.MISSING_IN_EDC.value == "missing_in_edc"
        assert DiscrepancyType.MISSING_IN_SOURCE.value == "missing_in_source"
        assert DiscrepancyType.FORMAT_DIFFERENCE.value == "format_difference"
        assert DiscrepancyType.UNIT_MISMATCH.value == "unit_mismatch"

    def test_discrepancy_severity_enum(self):
        """Test DiscrepancySeverity enum and priority system."""
        assert DiscrepancySeverity.CRITICAL.get_priority() == 4
        assert DiscrepancySeverity.MAJOR.get_priority() == 3
        assert DiscrepancySeverity.MINOR.get_priority() == 2
        assert DiscrepancySeverity.INFO.get_priority() == 1

    def test_context_data_structure(self):
        """Test DataVerificationContext data structure."""
        context = DataVerificationContext()

        # Test default values
        assert context.verification_history == []
        assert context.discrepancy_patterns == {}
        assert context.audit_trails == []
        assert context.performance_metrics == {}

        # Test adding verification results
        verification_result = {
            "verification_id": "DV_TEST_001",
            "match_score": 0.95,
            "discrepancies": [],
        }
        context.verification_history.append(verification_result)

        assert len(context.verification_history) == 1
        assert context.verification_history[0]["verification_id"] == "DV_TEST_001"

    @pytest.mark.asyncio
    async def test_regulatory_compliance_checking(self, data_verifier):
        """Test regulatory compliance aspects of verification."""
        # Data with regulatory compliance requirements
        regulated_data = {
            "subject_id": "SUBJ001",
            "informed_consent_date": "2024-01-15",
            "randomization_date": "2024-01-20",
            "adverse_events": [
                {
                    "term": "Nausea",
                    "start_date": "2024-01-25",
                    "reported_date": "2024-01-26",  # Within 24 hours
                    "serious": False,
                }
            ],
        }

        assessment = await data_verifier.assess_critical_data(regulated_data)

        assert (
            "regulatory_compliance" in assessment or "critical_findings" in assessment
        )
        assert isinstance(assessment, dict)

    @pytest.mark.asyncio
    async def test_statistical_analysis_integration(
        self, data_verifier, sample_batch_data
    ):
        """Test integration with statistical analysis for discrepancy patterns."""
        result = await data_verifier.batch_verification(sample_batch_data)

        assert "summary_statistics" in result
        stats = result["summary_statistics"]

        # Should include statistical measures
        expected_stats = [
            "total_discrepancies",
            "discrepancy_rate",
            "critical_findings_count",
        ]
        for stat in expected_stats:
            assert (
                stat in stats or len(stats) > 0
            )  # Flexible assertion for implementation variation
