"""Tests for Query Analyzer Agent."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, List, Any
import asyncio

from app.agents.query_analyzer import QueryAnalyzer, QueryAnalysis, QueryCategory, QuerySeverity
from app.agents.base_agent import AgentResponse


class TestQueryCategory:
    """Test cases for QueryCategory enum."""

    def test_query_category_values(self):
        """Test that QueryCategory enum has expected values."""
        assert QueryCategory.DATA_DISCREPANCY.value == "data_discrepancy"
        assert QueryCategory.MISSING_DATA.value == "missing_data"
        assert QueryCategory.PROTOCOL_DEVIATION.value == "protocol_deviation"
        assert QueryCategory.ADVERSE_EVENT.value == "adverse_event"
        assert QueryCategory.ELIGIBILITY.value == "eligibility"
        assert QueryCategory.CONCOMITANT_MEDICATION.value == "concomitant_medication"
        assert QueryCategory.LABORATORY_VALUE.value == "laboratory_value"
        assert QueryCategory.OTHER.value == "other"


class TestQuerySeverity:
    """Test cases for QuerySeverity enum."""

    def test_query_severity_values(self):
        """Test that QuerySeverity enum has expected values."""
        assert QuerySeverity.CRITICAL.value == "critical"
        assert QuerySeverity.MAJOR.value == "major"
        assert QuerySeverity.MINOR.value == "minor"
        assert QuerySeverity.INFO.value == "info"

    def test_query_severity_priority_order(self):
        """Test that severity levels have correct priority order."""
        severities = [QuerySeverity.CRITICAL, QuerySeverity.MAJOR, QuerySeverity.MINOR, QuerySeverity.INFO]
        priorities = [s.get_priority() for s in severities]
        
        # Higher priority numbers = more critical
        assert priorities[0] > priorities[1] > priorities[2] > priorities[3]


class TestQueryAnalysis:
    """Test cases for QueryAnalysis data class."""

    def test_query_analysis_creation(self):
        """Test QueryAnalysis creation with required fields."""
        analysis = QueryAnalysis(
            query_id="Q001",
            category=QueryCategory.DATA_DISCREPANCY,
            severity=QuerySeverity.MAJOR,
            confidence=0.85,
            subject_id="S001",
            visit="Visit 2",
            field_name="systolic_bp",
            description="Systolic BP value seems unusually high"
        )
        
        assert analysis.query_id == "Q001"
        assert analysis.category == QueryCategory.DATA_DISCREPANCY
        assert analysis.severity == QuerySeverity.MAJOR
        assert analysis.confidence == 0.85
        assert analysis.subject_id == "S001"
        assert analysis.visit == "Visit 2"
        assert analysis.field_name == "systolic_bp"
        assert "unusually high" in analysis.description

    def test_query_analysis_with_suggestions(self):
        """Test QueryAnalysis with suggested actions."""
        suggestions = [
            "Verify the measurement with source documents",
            "Check if patient was on antihypertensive medication"
        ]
        
        analysis = QueryAnalysis(
            query_id="Q002",
            category=QueryCategory.LABORATORY_VALUE,
            severity=QuerySeverity.CRITICAL,
            confidence=0.95,
            subject_id="S002",
            visit="Screening",
            field_name="creatinine",
            description="Creatinine level exceeds safety limits",
            suggested_actions=suggestions
        )
        
        assert len(analysis.suggested_actions) == 2
        assert "source documents" in analysis.suggested_actions[0]

    def test_query_analysis_serialization(self):
        """Test QueryAnalysis serialization to dict."""
        analysis = QueryAnalysis(
            query_id="Q003",
            category=QueryCategory.ADVERSE_EVENT,
            severity=QuerySeverity.CRITICAL,
            confidence=0.92,
            subject_id="S003",
            visit="Week 4",
            field_name="ae_term",
            description="Serious adverse event reported"
        )
        
        analysis_dict = analysis.to_dict()
        
        assert isinstance(analysis_dict, dict)
        assert analysis_dict["query_id"] == "Q003"
        assert analysis_dict["category"] == "adverse_event"
        assert analysis_dict["severity"] == "critical"
        assert analysis_dict["confidence"] == 0.92

    def test_requires_immediate_attention(self):
        """Test identification of queries requiring immediate attention."""
        critical_analysis = QueryAnalysis(
            query_id="Q004",
            category=QueryCategory.ADVERSE_EVENT,
            severity=QuerySeverity.CRITICAL,
            confidence=0.9,
            subject_id="S004",
            visit="Week 2",
            field_name="ae_outcome",
            description="Fatal adverse event"
        )
        
        minor_analysis = QueryAnalysis(
            query_id="Q005",
            category=QueryCategory.DATA_DISCREPANCY,
            severity=QuerySeverity.MINOR,
            confidence=0.7,
            subject_id="S005",
            visit="Baseline",
            field_name="height",
            description="Height unit unclear"
        )
        
        assert critical_analysis.requires_immediate_attention() is True
        assert minor_analysis.requires_immediate_attention() is False


class TestQueryAnalyzer:
    """Test cases for QueryAnalyzer agent."""

    @pytest.fixture
    def mock_openai_client(self):
        """Mock OpenAI client for testing."""
        with patch('app.agents.base_agent.AsyncOpenAI') as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value = mock_instance
            yield mock_instance

    @pytest.fixture
    def query_analyzer(self, mock_openai_client):
        """Create a QueryAnalyzer instance for testing."""
        return QueryAnalyzer()

    def test_query_analyzer_initialization(self, query_analyzer):
        """Test QueryAnalyzer initialization."""
        assert query_analyzer.agent_id == "query-analyzer"
        assert query_analyzer.name == "Query Analyzer"
        assert "medical terminology" in query_analyzer.description
        assert query_analyzer.model == "gpt-4"
        assert query_analyzer.temperature == 0.1  # Low temperature for consistency
        assert query_analyzer.max_tokens == 2000

    def test_query_analyzer_system_prompt(self, query_analyzer):
        """Test that system prompt includes medical and regulatory context."""
        system_prompt = query_analyzer.system_prompt
        
        assert "clinical trials" in system_prompt.lower()
        assert "medical terminology" in system_prompt.lower()
        assert "ich-gcp" in system_prompt.lower() or "regulatory" in system_prompt.lower()
        assert "severity" in system_prompt.lower()

    @pytest.mark.asyncio
    async def test_analyze_simple_data_discrepancy(self, query_analyzer, mock_openai_client):
        """Test analysis of a simple data discrepancy."""
        # Mock OpenAI response for data discrepancy
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock()]
        mock_completion.choices[0].message.content = '''
        {
            "category": "data_discrepancy",
            "severity": "major",
            "confidence": 0.88,
            "description": "Systolic blood pressure of 250 mmHg is clinically implausible",
            "suggested_actions": [
                "Verify measurement with source documents",
                "Check for transcription errors",
                "Consider remeasurement if possible"
            ],
            "medical_context": "Normal systolic BP range is 90-140 mmHg",
            "regulatory_impact": "Potential impact on primary endpoint analysis"
        }
        '''
        mock_completion.usage.total_tokens = 150
        mock_openai_client.chat.completions.create = AsyncMock(return_value=mock_completion)
        
        # Test data
        data_point = {
            "subject_id": "S001",
            "visit": "Week 2",
            "field_name": "systolic_bp",
            "value": "250",
            "unit": "mmHg",
            "normal_range": "90-140"
        }
        
        analysis = await query_analyzer.analyze_data_point(data_point)
        
        assert isinstance(analysis, QueryAnalysis)
        assert analysis.category == QueryCategory.DATA_DISCREPANCY
        assert analysis.severity == QuerySeverity.MAJOR
        assert analysis.confidence >= 0.8
        assert analysis.subject_id == "S001"
        assert "250 mmHg" in analysis.description
        assert len(analysis.suggested_actions) > 0

    @pytest.mark.asyncio
    async def test_analyze_missing_data(self, query_analyzer, mock_openai_client):
        """Test analysis of missing required data."""
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock()]
        mock_completion.choices[0].message.content = '''
        {
            "category": "missing_data",
            "severity": "major",
            "confidence": 0.95,
            "description": "Primary endpoint measurement missing at critical timepoint",
            "suggested_actions": [
                "Contact site for missing data collection",
                "Check if visit occurred as scheduled",
                "Document reason for missing data"
            ],
            "medical_context": "Primary endpoint critical for efficacy analysis",
            "regulatory_impact": "Missing primary endpoint affects ITT population"
        }
        '''
        mock_completion.usage.total_tokens = 120
        mock_openai_client.chat.completions.create = AsyncMock(return_value=mock_completion)
        
        data_point = {
            "subject_id": "S002",
            "visit": "Week 12",
            "field_name": "primary_endpoint_score",
            "value": None,
            "required": True,
            "visit_status": "completed"
        }
        
        analysis = await query_analyzer.analyze_data_point(data_point)
        
        assert analysis.category == QueryCategory.MISSING_DATA
        assert analysis.severity == QuerySeverity.MAJOR
        assert "primary endpoint" in analysis.description.lower()

    @pytest.mark.asyncio
    async def test_analyze_adverse_event(self, query_analyzer, mock_openai_client):
        """Test analysis of adverse event data."""
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock()]
        mock_completion.choices[0].message.content = '''
        {
            "category": "adverse_event",
            "severity": "critical",
            "confidence": 0.98,
            "description": "Serious adverse event requires immediate reporting",
            "suggested_actions": [
                "Immediate safety reporting required",
                "Notify medical monitor",
                "Complete SAE form within 24 hours",
                "Consider unblinding if necessary"
            ],
            "medical_context": "Myocardial infarction is a serious cardiac event",
            "regulatory_impact": "Expedited reporting to FDA required within 24 hours"
        }
        '''
        mock_completion.usage.total_tokens = 180
        mock_openai_client.chat.completions.create = AsyncMock(return_value=mock_completion)
        
        data_point = {
            "subject_id": "S003",
            "visit": "Week 8",
            "field_name": "ae_term",
            "value": "Myocardial infarction",
            "ae_serious": "Yes",
            "ae_outcome": "Ongoing"
        }
        
        analysis = await query_analyzer.analyze_data_point(data_point)
        
        assert analysis.category == QueryCategory.ADVERSE_EVENT
        assert analysis.severity == QuerySeverity.CRITICAL
        assert "immediate" in analysis.description.lower()
        assert any("24 hours" in action for action in analysis.suggested_actions)

    @pytest.mark.asyncio
    async def test_batch_analysis(self, query_analyzer, mock_openai_client):
        """Test batch analysis of multiple data points."""
        # Mock responses for batch analysis
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock()]
        mock_completion.choices[0].message.content = '''
        [
            {
                "query_id": "AUTO_001",
                "category": "data_discrepancy",
                "severity": "minor",
                "confidence": 0.75,
                "description": "Slight height discrepancy from screening"
            },
            {
                "query_id": "AUTO_002",
                "category": "missing_data",
                "severity": "major",
                "confidence": 0.90,
                "description": "Weight measurement missing at baseline"
            }
        ]
        '''
        mock_completion.usage.total_tokens = 200
        mock_openai_client.chat.completions.create = AsyncMock(return_value=mock_completion)
        
        data_points = [
            {
                "subject_id": "S001",
                "visit": "Baseline",
                "field_name": "height",
                "value": "175",
                "previous_value": "174"
            },
            {
                "subject_id": "S001",
                "visit": "Baseline",
                "field_name": "weight",
                "value": None,
                "required": True
            }
        ]
        
        analyses = await query_analyzer.batch_analyze(data_points)
        
        assert len(analyses) == 2
        assert all(isinstance(analysis, QueryAnalysis) for analysis in analyses)
        assert analyses[0].category == QueryCategory.DATA_DISCREPANCY
        assert analyses[1].category == QueryCategory.MISSING_DATA

    @pytest.mark.asyncio
    async def test_pattern_recognition(self, query_analyzer, mock_openai_client):
        """Test pattern recognition across multiple subjects."""
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock()]
        mock_completion.choices[0].message.content = '''
        {
            "pattern_detected": true,
            "pattern_type": "systematic_site_error",
            "pattern_description": "Multiple subjects at Site 101 showing consistently low hemoglobin values",
            "affected_subjects": ["S001", "S003", "S005"],
            "severity": "major",
            "confidence": 0.92,
            "suggested_actions": [
                "Audit Site 101 laboratory procedures",
                "Check calibration of hemoglobin analyzer",
                "Review lab normal ranges used at site"
            ]
        }
        '''
        mock_completion.usage.total_tokens = 180
        mock_openai_client.chat.completions.create = AsyncMock(return_value=mock_completion)
        
        historical_data = [
            {"subject_id": "S001", "site": "101", "field": "hemoglobin", "value": 8.5},
            {"subject_id": "S003", "site": "101", "field": "hemoglobin", "value": 8.2},
            {"subject_id": "S005", "site": "101", "field": "hemoglobin", "value": 8.0},
            {"subject_id": "S007", "site": "102", "field": "hemoglobin", "value": 12.1}
        ]
        
        patterns = await query_analyzer.detect_patterns(historical_data)
        
        assert patterns["pattern_detected"] is True
        assert "Site 101" in patterns["pattern_description"]
        assert patterns["confidence"] > 0.9

    def test_medical_terminology_processing(self, query_analyzer):
        """Test medical terminology processing and standardization."""
        # Test medical term standardization
        assert query_analyzer.standardize_medical_term("MI") == "Myocardial infarction"
        assert query_analyzer.standardize_medical_term("HTN") == "Hypertension"
        assert query_analyzer.standardize_medical_term("DM") == "Diabetes mellitus"
        
        # Test severity assessment based on medical terms
        critical_terms = ["death", "life-threatening", "myocardial infarction"]
        major_terms = ["hospitalization", "significant disability"]
        
        for term in critical_terms:
            severity = query_analyzer.assess_medical_severity(term)
            assert severity == QuerySeverity.CRITICAL
            
        for term in major_terms:
            severity = query_analyzer.assess_medical_severity(term)
            assert severity == QuerySeverity.MAJOR

    @pytest.mark.asyncio
    async def test_cross_system_data_matching(self, query_analyzer, mock_openai_client):
        """Test cross-system data matching and discrepancy detection."""
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock()]
        mock_completion.choices[0].message.content = '''
        {
            "discrepancies_found": 2,
            "discrepancies": [
                {
                    "field": "concomitant_medication",
                    "edc_value": "Aspirin 81mg daily",
                    "source_value": "Aspirin 100mg daily",
                    "confidence": 0.85,
                    "severity": "minor"
                },
                {
                    "field": "adverse_event_date",
                    "edc_value": "2024-01-15",
                    "source_value": "2024-01-14",
                    "confidence": 0.95,
                    "severity": "major"
                }
            ]
        }
        '''
        mock_completion.usage.total_tokens = 220
        mock_openai_client.chat.completions.create = AsyncMock(return_value=mock_completion)
        
        edc_data = {
            "subject_id": "S001",
            "concomitant_medication": "Aspirin 81mg daily",
            "adverse_event_date": "2024-01-15"
        }
        
        source_data = {
            "subject_id": "S001",
            "concomitant_medication": "Aspirin 100mg daily",
            "adverse_event_date": "2024-01-14"
        }
        
        discrepancies = await query_analyzer.cross_system_match(edc_data, source_data)
        
        assert discrepancies["discrepancies_found"] == 2
        assert len(discrepancies["discrepancies"]) == 2

    def test_performance_metrics(self, query_analyzer):
        """Test performance metrics and optimization."""
        # Test that analyzer can handle large volumes
        assert query_analyzer.max_batch_size >= 100
        assert query_analyzer.recommended_batch_size >= 10
        
        # Test cache functionality
        query_analyzer.enable_caching()
        assert query_analyzer.cache_enabled is True
        
        # Test performance monitoring
        metrics = query_analyzer.get_performance_metrics()
        assert "queries_processed" in metrics
        assert "average_processing_time" in metrics
        assert "accuracy_rate" in metrics

    @pytest.mark.asyncio
    async def test_error_handling(self, query_analyzer, mock_openai_client):
        """Test error handling for various failure scenarios."""
        # Test API failure
        mock_openai_client.chat.completions.create = AsyncMock(
            side_effect=Exception("API rate limit exceeded")
        )
        
        data_point = {
            "subject_id": "S001",
            "visit": "Week 1",
            "field_name": "test_field",
            "value": "test_value"
        }
        
        with pytest.raises(Exception):
            await query_analyzer.analyze_data_point(data_point)
        
        # Test invalid data format
        invalid_data = {"invalid": "format"}
        
        with pytest.raises(ValueError):
            await query_analyzer.analyze_data_point(invalid_data)

    def test_configuration_validation(self, query_analyzer):
        """Test configuration validation and settings."""
        # Test confidence threshold setting
        query_analyzer.set_confidence_threshold(0.8)
        assert query_analyzer.confidence_threshold == 0.8
        
        # Test invalid confidence threshold
        with pytest.raises(ValueError):
            query_analyzer.set_confidence_threshold(1.5)
        
        # Test severity filter setting
        query_analyzer.set_severity_filter(QuerySeverity.MAJOR)
        assert query_analyzer.severity_filter == QuerySeverity.MAJOR

    @pytest.mark.asyncio
    async def test_regulatory_compliance_checks(self, query_analyzer, mock_openai_client):
        """Test regulatory compliance checking functionality."""
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock()]
        mock_completion.choices[0].message.content = '''
        {
            "compliance_issues": [
                {
                    "regulation": "ICH-GCP 5.1.3",
                    "description": "Informed consent date after first study procedure",
                    "severity": "critical",
                    "action_required": "Immediate protocol deviation reporting"
                }
            ],
            "compliance_score": 0.75
        }
        '''
        mock_completion.usage.total_tokens = 160
        mock_openai_client.chat.completions.create = AsyncMock(return_value=mock_completion)
        
        subject_data = {
            "subject_id": "S001",
            "informed_consent_date": "2024-01-15",
            "first_study_procedure_date": "2024-01-10",
            "randomization_date": "2024-01-16"
        }
        
        compliance_check = await query_analyzer.check_regulatory_compliance(subject_data)
        
        assert "compliance_issues" in compliance_check
        assert compliance_check["compliance_score"] < 1.0
        assert "ICH-GCP" in compliance_check["compliance_issues"][0]["regulation"]


@pytest.fixture
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()