"""Tests for Query Analyzer using OpenAI Agents SDK."""

import json
from datetime import datetime
from typing import Any, Dict, List
from unittest.mock import MagicMock, Mock, patch

import pytest

from app.agents.query_analyzer_sdk import (
    QueryAnalysisContext,
    QueryAnalyzer,
    QueryCategory,
    QuerySeverity,
    analyze_data_point,
    batch_analyze_data,
    detect_patterns,
)


class TestQueryAnalyzerSDK:
    """Test suite for Query Analyzer with OpenAI Agents SDK."""

    @pytest.fixture
    def mock_openai_client(self):
        """Mock OpenAI client for testing."""
        with patch("app.agents.query_analyzer_sdk.OpenAI") as mock_client:
            # Mock assistant
            mock_assistant = Mock()
            mock_assistant.id = "asst_analyzer123"
            mock_assistant.name = "Clinical Query Analyzer"

            # Mock thread
            mock_thread = Mock()
            mock_thread.id = "thread_analyzer123"

            # Mock message for analysis response
            mock_message = Mock()
            mock_message.content = [
                Mock(
                    text=Mock(
                        value=json.dumps(
                            {
                                "query_id": "QA_20250101_001",
                                "category": "data_discrepancy",
                                "severity": "major",
                                "confidence": 0.92,
                                "subject_id": "SUBJ001",
                                "visit": "Week 4",
                                "field_name": "Hemoglobin",
                                "description": "EDC value (12.5) differs from source document (11.2)",
                                "suggested_actions": [
                                    "Review source document",
                                    "Clarify with site",
                                ],
                                "medical_context": "Clinically significant hemoglobin difference",
                                "regulatory_impact": "May affect primary endpoint analysis",
                            }
                        )
                    )
                )
            ]

            # Mock run
            mock_run = Mock()
            mock_run.status = "completed"
            mock_run.id = "run_analyzer123"

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
    def query_analyzer(self, mock_openai_client):
        """Create QueryAnalyzer instance with mocked client."""
        return QueryAnalyzer()

    @pytest.fixture
    def sample_data_point(self) -> Dict[str, Any]:
        """Sample data point for testing."""
        return {
            "subject_id": "SUBJ001",
            "visit": "Week 4",
            "field_name": "Hemoglobin",
            "edc_value": "12.5",
            "source_value": "11.2",
            "unit": "g/dL",
            "normal_range": "12.0-15.0",
            "site_name": "Memorial Hospital",
            "visit_date": "2024-12-15",
        }

    @pytest.fixture
    def sample_batch_data(self) -> List[Dict[str, Any]]:
        """Sample batch data for testing."""
        return [
            {
                "subject_id": "SUBJ001",
                "visit": "Week 4",
                "field_name": "Hemoglobin",
                "edc_value": "12.5",
                "source_value": "11.2",
            },
            {
                "subject_id": "SUBJ002",
                "visit": "Week 4",
                "field_name": "Weight",
                "edc_value": "75.0",
                "source_value": "",
            },
            {
                "subject_id": "SUBJ003",
                "visit": "Baseline",
                "field_name": "Blood Pressure",
                "edc_value": "140/90",
                "source_value": "130/85",
            },
        ]

    def test_query_analyzer_initialization(self, query_analyzer):
        """Test QueryAnalyzer initialization."""
        assert query_analyzer.agent is not None
        assert query_analyzer.instructions is not None
        assert query_analyzer.medical_terms is not None
        assert query_analyzer.context is not None
        assert query_analyzer.confidence_threshold == 0.7
        assert query_analyzer.severity_filter == QuerySeverity.INFO

    def test_medical_terminology_mapping(self, query_analyzer):
        """Test medical terminology standardization."""
        # Test abbreviation expansion
        assert query_analyzer.medical_terms["MI"] == "Myocardial infarction"
        assert query_analyzer.medical_terms["HTN"] == "Hypertension"
        assert query_analyzer.medical_terms["SAE"] == "Serious adverse event"

        # Test critical terms classification
        assert "death" in query_analyzer.critical_terms
        assert "myocardial infarction" in query_analyzer.critical_terms
        assert "life-threatening" in query_analyzer.critical_terms

    @pytest.mark.asyncio
    async def test_single_data_point_analysis(self, query_analyzer, sample_data_point):
        """Test analysis of a single data point."""
        result = await query_analyzer.analyze_data_point(sample_data_point)

        assert result is not None
        assert "query_id" in result
        assert "category" in result
        assert "severity" in result
        assert "confidence" in result
        assert result["category"] == "data_discrepancy"
        assert result["severity"] in ["critical", "major", "minor", "info"]
        assert 0.0 <= result["confidence"] <= 1.0

    @pytest.mark.asyncio
    async def test_batch_data_analysis(self, query_analyzer, sample_batch_data):
        """Test batch analysis of multiple data points."""
        results = await query_analyzer.batch_analyze(sample_batch_data)

        assert isinstance(results, list)
        assert len(results) == len(sample_batch_data)

        for result in results:
            assert "query_id" in result
            assert "category" in result
            assert "severity" in result
            assert "confidence" in result
            assert "suggested_actions" in result

    @pytest.mark.asyncio
    async def test_pattern_detection(self, query_analyzer):
        """Test pattern detection across historical data."""
        historical_data = [
            {"site_name": "Site A", "field_name": "Weight", "discrepancy_count": 5},
            {"site_name": "Site A", "field_name": "Height", "discrepancy_count": 3},
            {"site_name": "Site B", "field_name": "Weight", "discrepancy_count": 1},
            {
                "site_name": "Site C",
                "field_name": "Blood Pressure",
                "discrepancy_count": 8,
            },
        ]

        patterns = await query_analyzer.detect_patterns(historical_data)

        assert "site_patterns" in patterns
        assert "field_patterns" in patterns
        assert "temporal_patterns" in patterns
        assert "recommendations" in patterns

    @pytest.mark.asyncio
    async def test_cross_system_matching(self, query_analyzer):
        """Test cross-system data matching and verification."""
        edc_data = {
            "subject_id": "SUBJ001",
            "visit": "Week 4",
            "hemoglobin": "12.5",
            "weight": "75.0",
        }

        source_data = {
            "subject_id": "SUBJ001",
            "visit": "Week 4",
            "hemoglobin": "11.2",
            "weight": "75.0",
        }

        match_result = await query_analyzer.cross_system_match(edc_data, source_data)

        assert "match_score" in match_result
        assert "discrepancies" in match_result
        assert "matching_fields" in match_result
        assert 0.0 <= match_result["match_score"] <= 1.0

    @pytest.mark.asyncio
    async def test_regulatory_compliance_check(self, query_analyzer):
        """Test regulatory compliance checking."""
        subject_data = {
            "subject_id": "SUBJ001",
            "age": 65,
            "inclusion_criteria_met": True,
            "informed_consent_date": "2024-01-15",
            "first_dose_date": "2024-01-20",
            "adverse_events": [
                {"term": "Headache", "severity": "mild", "serious": False}
            ],
        }

        compliance_result = await query_analyzer.check_regulatory_compliance(
            subject_data
        )

        assert "compliance_score" in compliance_result
        assert "violations" in compliance_result
        assert "recommendations" in compliance_result
        assert 0.0 <= compliance_result["compliance_score"] <= 1.0

    def test_severity_assessment(self, query_analyzer):
        """Test medical severity assessment."""
        # Critical terms should return CRITICAL severity
        critical_result = query_analyzer.assess_medical_severity(
            "myocardial infarction"
        )
        assert critical_result == QuerySeverity.CRITICAL

        # Major terms should return MAJOR severity
        major_result = query_analyzer.assess_medical_severity("hospitalization")
        assert major_result == QuerySeverity.MAJOR

        # Unknown terms should return INFO severity
        info_result = query_analyzer.assess_medical_severity("routine checkup")
        assert info_result == QuerySeverity.INFO

    def test_confidence_threshold_configuration(self, query_analyzer):
        """Test confidence threshold configuration."""
        # Test setting confidence threshold
        query_analyzer.set_confidence_threshold(0.8)
        assert query_analyzer.confidence_threshold == 0.8

        # Test invalid threshold
        with pytest.raises(ValueError):
            query_analyzer.set_confidence_threshold(1.5)

        with pytest.raises(ValueError):
            query_analyzer.set_confidence_threshold(-0.1)

    def test_severity_filter_configuration(self, query_analyzer):
        """Test severity filter configuration."""
        # Test setting severity filter
        query_analyzer.set_severity_filter(QuerySeverity.MAJOR)
        assert query_analyzer.severity_filter == QuerySeverity.MAJOR

    @pytest.mark.asyncio
    async def test_performance_optimization(self, query_analyzer, sample_batch_data):
        """Test performance optimization features."""
        # Test batch size optimization
        large_batch = sample_batch_data * 10  # 30 items

        start_time = datetime.now()
        results = await query_analyzer.batch_analyze(large_batch)
        execution_time = (datetime.now() - start_time).total_seconds()

        assert len(results) == len(large_batch)
        assert execution_time < 30.0  # Should complete in reasonable time

        # Test recommended batch size
        assert query_analyzer.recommended_batch_size == 25
        assert query_analyzer.max_batch_size == 100

    @pytest.mark.asyncio
    async def test_error_handling(self, query_analyzer):
        """Test error handling in analysis."""
        # Test with invalid data
        invalid_data = {"invalid_field": "test"}

        result = await query_analyzer.analyze_data_point(invalid_data)

        # Should handle gracefully and return appropriate response
        assert result is not None
        assert "error" in result or "category" in result

    @pytest.mark.asyncio
    async def test_context_sharing(self, query_analyzer, sample_data_point):
        """Test context sharing between analysis calls."""
        # First analysis
        result1 = await query_analyzer.analyze_data_point(sample_data_point)

        # Check context contains analysis history
        assert len(query_analyzer.context.analysis_history) > 0

        # Second analysis with related data
        related_data = sample_data_point.copy()
        related_data["visit"] = "Week 8"
        result2 = await query_analyzer.analyze_data_point(related_data)

        # Context should accumulate results
        assert len(query_analyzer.context.analysis_history) >= 2

    def test_query_category_enum(self):
        """Test QueryCategory enum values."""
        assert QueryCategory.DATA_DISCREPANCY.value == "data_discrepancy"
        assert QueryCategory.MISSING_DATA.value == "missing_data"
        assert QueryCategory.PROTOCOL_DEVIATION.value == "protocol_deviation"
        assert QueryCategory.ADVERSE_EVENT.value == "adverse_event"

    def test_query_severity_enum(self):
        """Test QuerySeverity enum and priority system."""
        assert QuerySeverity.CRITICAL.get_priority() == 4
        assert QuerySeverity.MAJOR.get_priority() == 3
        assert QuerySeverity.MINOR.get_priority() == 2
        assert QuerySeverity.INFO.get_priority() == 1

    def test_context_data_structure(self):
        """Test QueryAnalysisContext data structure."""
        context = QueryAnalysisContext()

        # Test default values
        assert context.analysis_history == []
        assert context.detected_patterns == {}
        assert context.performance_metrics == {}

        # Test adding analysis results
        analysis_result = {
            "query_id": "QA_TEST_001",
            "category": "data_discrepancy",
            "severity": "major",
        }
        context.analysis_history.append(analysis_result)

        assert len(context.analysis_history) == 1
        assert context.analysis_history[0]["query_id"] == "QA_TEST_001"

    @pytest.mark.asyncio
    async def test_medical_term_standardization(self, query_analyzer):
        """Test medical terminology standardization and expansion."""
        # Test standardization method exists and works
        standardized = query_analyzer.standardize_medical_term("MI")
        assert standardized == "Myocardial infarction"

        # Test case insensitive matching
        standardized_lower = query_analyzer.standardize_medical_term("mi")
        assert standardized_lower == "Myocardial infarction"

        # Test unknown terms pass through
        unknown = query_analyzer.standardize_medical_term("unknown_term")
        assert unknown == "unknown_term"

    @pytest.mark.asyncio
    async def test_bulk_processing_capabilities(self, query_analyzer):
        """Test bulk processing with large datasets."""
        # Create large dataset
        large_dataset = []
        for i in range(50):
            data_point = {
                "subject_id": f"SUBJ{i:03d}",
                "visit": "Week 4",
                "field_name": "Hemoglobin",
                "edc_value": str(12.0 + i * 0.1),
                "source_value": str(11.5 + i * 0.1),
            }
            large_dataset.append(data_point)

        results = await query_analyzer.batch_analyze(large_dataset)

        assert len(results) == len(large_dataset)
        assert all("query_id" in result for result in results)
        assert all("confidence" in result for result in results)
