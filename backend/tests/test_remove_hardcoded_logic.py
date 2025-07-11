"""Tests to ensure hardcoded medical logic is removed and replaced with LLM intelligence."""

import json
from unittest.mock import AsyncMock, patch

import pytest

from app.agents.data_verifier import DataVerifier
from app.agents.query_analyzer import QueryAnalyzer

# We'll test by mocking the function tool execution


class TestRemoveHardcodedMedicalLogic:
    """Test suite to ensure hardcoded medical logic is removed."""

    def test_data_verifier_no_critical_fields_constant(self):
        """CRITICAL_FIELDS should not be referenced in the code."""
        # Check that CRITICAL_FIELDS is not used anywhere in the file
        import os

        with open(os.path.join("app", "agents", "data_verifier.py"), "r") as f:
            content = f.read()
            # Skip comments and the REMOVED line
            lines = [
                line
                for line in content.split("\n")
                if "CRITICAL_FIELDS" in line and not line.strip().startswith("#")
            ]

            # Should find no references to CRITICAL_FIELDS
            assert (
                len(lines) == 0
            ), f"Found {len(lines)} references to CRITICAL_FIELDS: {lines}"

    def test_data_verifier_no_default_tolerances(self):
        """DEFAULT_FIELD_TOLERANCES should not exist as hardcoded values."""
        # This test should FAIL initially and PASS after refactoring
        try:
            from app.agents.data_verifier import DEFAULT_FIELD_TOLERANCES

            assert False, "DEFAULT_FIELD_TOLERANCES still exists as hardcoded constant"
        except ImportError:
            pass

    def test_query_analyzer_no_medical_term_mapping(self):
        """MEDICAL_TERM_MAPPING should not exist as hardcoded dictionary."""
        # This test should FAIL initially and PASS after refactoring
        try:
            from app.agents.query_analyzer import MEDICAL_TERM_MAPPING

            assert False, "MEDICAL_TERM_MAPPING still exists as hardcoded constant"
        except ImportError:
            pass

    def test_query_analyzer_no_critical_medical_terms(self):
        """CRITICAL_MEDICAL_TERMS should not exist as hardcoded set."""
        # This test should FAIL initially and PASS after refactoring
        try:
            from app.agents.query_analyzer import CRITICAL_MEDICAL_TERMS

            assert False, "CRITICAL_MEDICAL_TERMS still exists as hardcoded constant"
        except ImportError:
            pass

    def test_query_analyzer_no_major_medical_terms(self):
        """MAJOR_MEDICAL_TERMS should not exist as hardcoded set."""
        # This test should FAIL initially and PASS after refactoring
        try:
            from app.agents.query_analyzer import MAJOR_MEDICAL_TERMS

            assert False, "MAJOR_MEDICAL_TERMS still exists as hardcoded constant"
        except ImportError:
            pass


class TestDataVerifierUsesLLM:
    """Test that DataVerifier uses LLM for medical decisions."""

    @pytest.mark.asyncio
    async def test_critical_field_detection_uses_llm(self):
        """Critical field detection should use LLM, not hardcoded list."""
        verifier = DataVerifier()

        # Mock the Runner.run to simulate LLM response
        with patch("app.agents.data_verifier.Runner.run") as mock_run:
            mock_response = AsyncMock()
            mock_response.messages = [
                type(
                    "Message",
                    (),
                    {
                        "content": json.dumps(
                            {
                                "is_critical": True,
                                "reasoning": "Hemoglobin is a critical safety parameter",
                            }
                        )
                    },
                )
            ]
            mock_run.return_value = mock_response

            # The method should ask LLM about field criticality
            result = await verifier.is_field_critical("hemoglobin")

            # Verify LLM was called
            mock_run.assert_called_once()
            assert "hemoglobin" in str(mock_run.call_args)
            assert result is True

    @pytest.mark.asyncio
    async def test_tolerance_determination_uses_llm(self):
        """Field tolerance should be determined by LLM based on context."""
        verifier = DataVerifier()

        with patch("app.agents.data_verifier.Runner.run") as mock_run:
            mock_response = AsyncMock()
            mock_response.messages = [
                type(
                    "Message",
                    (),
                    {
                        "content": json.dumps(
                            {
                                "tolerance": 0.5,
                                "reasoning": "For hemoglobin in anemic patients, 0.5 g/dL tolerance is appropriate",
                            }
                        )
                    },
                )
            ]
            mock_run.return_value = mock_response

            # The method should ask LLM for appropriate tolerance
            tolerance = await verifier.get_field_tolerance(
                field_name="hemoglobin", context={"patient_condition": "anemia"}
            )

            mock_run.assert_called_once()
            assert tolerance == 0.5


class TestQueryAnalyzerUsesLLM:
    """Test that QueryAnalyzer uses LLM for medical terminology."""

    @pytest.mark.asyncio
    async def test_medical_term_expansion_uses_llm(self):
        """Medical abbreviations should be expanded by LLM."""
        analyzer = QueryAnalyzer()

        with patch("app.agents.query_analyzer.Runner.run") as mock_run:
            mock_response = AsyncMock()
            mock_response.messages = [
                type(
                    "Message",
                    (),
                    {
                        "content": json.dumps(
                            {
                                "full_term": "Myocardial Infarction",
                                "context": "Cardiac event requiring immediate attention",
                            }
                        )
                    },
                )
            ]
            mock_run.return_value = mock_response

            # Should use LLM to expand medical abbreviations
            result = await analyzer.expand_medical_term("MI")

            mock_run.assert_called_once()
            assert result == "Myocardial Infarction"

    @pytest.mark.asyncio
    async def test_severity_classification_uses_llm(self):
        """Medical term severity should be classified by LLM."""
        analyzer = QueryAnalyzer()

        with patch("app.agents.query_analyzer.Runner.run") as mock_run:
            mock_response = AsyncMock()
            mock_response.messages = [
                type(
                    "Message",
                    (),
                    {
                        "content": json.dumps(
                            {
                                "severity": "critical",
                                "reasoning": "Cardiac arrest is life-threatening",
                            }
                        )
                    },
                )
            ]
            mock_run.return_value = mock_response

            # Should use LLM to classify severity
            severity = await analyzer.classify_term_severity("cardiac arrest")

            mock_run.assert_called_once()
            assert severity == "critical"


class TestCalculationToolsPureMath:
    """Test that calculation tools only do math, not medical judgments."""

    def test_age_calculation_has_medical_categories(self):
        """Age calculation currently includes medical categories - should fail."""
        # This test checks that age_group is currently in the output
        # After refactoring, this test should be inverted
        from app.agents.calculation_tools import calculate_age_at_visit

        # Check the docstring to see what it returns
        assert "age_group" in calculate_age_at_visit.__doc__

    def test_creatinine_clearance_has_medical_categories(self):
        """CrCl calculation currently includes kidney function categories - should fail."""
        from app.agents.calculation_tools import calculate_creatinine_clearance

        # Check the docstring mentions gfr_category
        assert "gfr_category" in calculate_creatinine_clearance.__doc__

    def test_unit_conversion_is_pure_math(self):
        """Unit conversion should only do math, no medical context."""
        from app.agents.calculation_tools import convert_medical_units

        # This one should be pure math - check docstring doesn't mention medical judgments
        assert "medical judgments" not in convert_medical_units.__doc__


class TestIntegrationWithLLM:
    """Integration tests to ensure LLM is used for medical decisions."""

    @pytest.mark.asyncio
    async def test_data_verification_workflow_uses_llm(self):
        """Full data verification workflow should use LLM for all medical decisions."""
        verifier = DataVerifier()

        with patch("app.agents.data_verifier.Runner.run") as mock_run:
            # Mock multiple LLM calls
            mock_run.side_effect = [
                # First call: field criticality
                AsyncMock(
                    messages=[
                        type(
                            "Message",
                            (),
                            {"content": json.dumps({"is_critical": True})},
                        )
                    ]
                )(),
                # Second call: tolerance
                AsyncMock(
                    messages=[
                        type("Message", (), {"content": json.dumps({"tolerance": 0.1})})
                    ]
                )(),
                # Third call: discrepancy severity
                AsyncMock(
                    messages=[
                        type(
                            "Message",
                            (),
                            {
                                "content": json.dumps(
                                    {
                                        "severity": "critical",
                                        "clinical_impact": "Significant anemia requiring intervention",
                                    }
                                )
                            },
                        )
                    ]
                )(),
            ]

            # Run verification
            result = await verifier.verify_with_llm_intelligence(
                edc_value="8.5", source_value="12.5", field_name="hemoglobin"
            )

            # Should have made multiple LLM calls
            assert mock_run.call_count >= 2
            assert result["severity"] == "critical"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
