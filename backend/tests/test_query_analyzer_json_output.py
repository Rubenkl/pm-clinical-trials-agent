"""
TDD Tests for Query Analyzer JSON Output (Task #6)

Tests for updating Query Analyzer to output structured JSON with human-readable fields
instead of plain text responses. This aligns with the new architecture where agents
output frontend-compatible JSON responses.

RED Phase: These tests will fail initially and drive the implementation.
"""

import json
from datetime import datetime
from typing import Any, Dict

import pytest

from app.agents.query_analyzer import QueryAnalyzer
from app.api.models.structured_responses import (
    QueryAnalyzerResponse,
    QueryStatus,
    SeverityLevel,
)


class TestQueryAnalyzerJSONOutput:
    """Test Query Analyzer outputs structured JSON with human-readable fields"""

    @pytest.fixture
    def query_analyzer(self):
        """Create Query Analyzer instance for testing"""
        return QueryAnalyzer()

    @pytest.fixture
    def critical_hemoglobin_data(self):
        """Sample critical hemoglobin data for testing"""
        return {
            "subject_id": "SUBJ001",
            "site_id": "SITE01",
            "visit": "Week 12",
            "field_name": "hemoglobin",
            "field_value": "7.2",  # Critical low value
            "form_name": "Laboratory Results",
            "normal_range": "12.0-15.5 g/dL",
            "previous_value": "11.8",
        }

    @pytest.fixture
    def elevated_bp_data(self):
        """Sample elevated blood pressure data"""
        return {
            "subject_id": "SUBJ002",
            "site_id": "SITE01",
            "visit": "Week 8",
            "field_name": "systolic_bp",
            "field_value": "185",  # Critical high value
            "form_name": "Vital Signs",
            "normal_range": "<140 mmHg",
            "previous_value": "142",
        }

    @pytest.fixture
    def normal_value_data(self):
        """Sample normal value data (should not generate query)"""
        return {
            "subject_id": "SUBJ003",
            "site_id": "SITE02",
            "visit": "Week 4",
            "field_name": "glucose",
            "field_value": "95",  # Normal value
            "form_name": "Laboratory Results",
            "normal_range": "70-100 mg/dL",
        }

    async def test_query_analyzer_json_output_structure(
        self, query_analyzer, critical_hemoglobin_data
    ):
        """Test Query Analyzer returns structured JSON matching QueryAnalyzerResponse"""
        # This test will FAIL initially (RED phase)
        result = await query_analyzer.analyze_clinical_data(critical_hemoglobin_data)

        # Verify top-level JSON structure
        assert isinstance(result, dict)
        assert "success" in result
        assert result["success"] is True

        # Core QueryAnalyzerResponse fields
        assert "query_id" in result
        assert "created_date" in result
        assert "status" in result
        assert "severity" in result
        assert "category" in result

        # Subject and clinical context
        assert "subject" in result
        assert "clinical_context" in result

        # Clinical findings and AI analysis
        assert "clinical_findings" in result
        assert "ai_analysis" in result

        # Human-readable fields for frontend
        assert "human_readable_summary" in result
        assert "clinical_interpretation" in result
        assert "recommendation_summary" in result

        # Metadata
        assert "agent_id" in result
        assert result["agent_id"] == "query-analyzer"
        assert "execution_time" in result
        assert "confidence_score" in result

    async def test_critical_hemoglobin_analysis(
        self, query_analyzer, critical_hemoglobin_data
    ):
        """Test Query Analyzer properly analyzes critical hemoglobin values"""
        # This test will FAIL initially (RED phase)
        result = await query_analyzer.analyze_clinical_data(critical_hemoglobin_data)

        assert result["success"] is True

        # Should classify as critical severity
        assert result["severity"] == SeverityLevel.CRITICAL.value
        assert result["category"] == "laboratory_value"

        # Subject information should be properly structured
        subject = result["subject"]
        assert subject["id"] == "SUBJ001"
        assert subject["site_id"] == "SITE01"

        # Clinical context should include field details
        context = result["clinical_context"]
        assert context["field"] == "hemoglobin"
        assert context["value"] == "7.2"
        assert context["visit"] == "Week 12"
        assert context["normal_range"] == "12.0-15.5 g/dL"
        assert context["previous_value"] == "11.8"

        # Should have clinical findings
        assert len(result["clinical_findings"]) >= 1
        finding = result["clinical_findings"][0]
        assert finding["parameter"] == "hemoglobin"
        assert finding["value"] == "7.2"
        assert finding["severity"] == SeverityLevel.CRITICAL.value
        assert "anemia" in finding["interpretation"].lower()

        # AI analysis should be comprehensive
        ai_analysis = result["ai_analysis"]
        assert ai_analysis["clinical_significance"] == "high"
        assert ai_analysis["confidence_score"] >= 0.85
        assert len(ai_analysis["recommendations"]) >= 2
        assert any(
            "transfusion" in rec.lower() or "hematology" in rec.lower()
            for rec in ai_analysis["recommendations"]
        )

        # Human-readable fields should be meaningful
        assert len(result["human_readable_summary"]) > 30
        assert "critical" in result["human_readable_summary"].lower()
        assert "hemoglobin" in result["human_readable_summary"].lower()

        clinical_interp = result["clinical_interpretation"]
        assert "CLINICAL FINDING:" in clinical_interp
        assert "7.2" in clinical_interp
        assert "g/dL" in clinical_interp
        assert any(
            term in clinical_interp.lower()
            for term in ["severe anemia", "anemia", "critical"]
        )

    async def test_elevated_blood_pressure_analysis(
        self, query_analyzer, elevated_bp_data
    ):
        """Test Query Analyzer properly analyzes elevated blood pressure"""
        # This test will FAIL initially (RED phase)
        result = await query_analyzer.analyze_clinical_data(elevated_bp_data)

        assert result["success"] is True
        assert result["severity"] == SeverityLevel.CRITICAL.value
        assert result["category"] == "vital_signs"

        # Clinical findings should identify hypertension
        finding = result["clinical_findings"][0]
        assert finding["parameter"] == "systolic_bp"
        assert finding["value"] == "185"
        assert any(
            term in finding["interpretation"].lower()
            for term in ["hypertension", "hypertensive", "elevated", "crisis"]
        )

        # AI analysis should include appropriate recommendations
        recommendations = result["ai_analysis"]["recommendations"]
        assert any(
            "cardiology" in rec.lower() or "antihypertensive" in rec.lower()
            for rec in recommendations
        )

        # Human-readable summary should include blood pressure context
        summary = result["human_readable_summary"].lower()
        assert any(
            term in summary for term in ["blood pressure", "bp", "hypertension", "185"]
        )

    async def test_normal_value_handling(self, query_analyzer, normal_value_data):
        """Test Query Analyzer handles normal values appropriately"""
        # This test will FAIL initially (RED phase)
        result = await query_analyzer.analyze_clinical_data(normal_value_data)

        assert result["success"] is True

        # Normal values should be classified as info or minor
        assert result["severity"] in [
            SeverityLevel.INFO.value,
            SeverityLevel.MINOR.value,
        ]

        # Should indicate no query needed in recommendations
        ai_analysis = result["ai_analysis"]
        assert (
            "no action" in ai_analysis["interpretation"].lower()
            or "normal" in ai_analysis["interpretation"].lower()
        )

        # Human-readable summary should indicate normal finding
        summary = result["human_readable_summary"].lower()
        assert any(term in summary for term in ["normal", "within range", "acceptable"])

    async def test_query_analyzer_response_validation(
        self, query_analyzer, critical_hemoglobin_data
    ):
        """Test Query Analyzer response can be validated against Pydantic model"""
        # This test will FAIL initially (RED phase)
        result = await query_analyzer.analyze_clinical_data(critical_hemoglobin_data)

        # Should be able to create QueryAnalyzerResponse from result
        try:
            # Add required fields that might be missing
            if "response_type" not in result:
                result["response_type"] = "clinical_analysis"
            if "created_date" not in result:
                result["created_date"] = datetime.now()
            if "raw_response" not in result:
                result["raw_response"] = json.dumps(result)

            response = QueryAnalyzerResponse(**result)
            assert response.success is True
            assert response.agent_id == "query-analyzer"
            assert response.severity == SeverityLevel.CRITICAL
        except Exception as e:
            pytest.fail(f"QueryAnalyzerResponse validation failed: {str(e)}")

    async def test_medical_intelligence_integration(self, query_analyzer):
        """Test Query Analyzer integrates medical intelligence for clinical interpretation"""
        # Test multiple clinical scenarios
        test_cases = [
            {
                "data": {
                    "subject_id": "SUBJ004",
                    "site_id": "SITE01",
                    "visit": "Week 1",
                    "field_name": "creatinine",
                    "field_value": "3.2",
                    "normal_range": "0.6-1.2 mg/dL",
                },
                "expected_severity": SeverityLevel.CRITICAL.value,
                "expected_terms": ["kidney", "renal", "creatinine", "dysfunction"],
            },
            {
                "data": {
                    "subject_id": "SUBJ005",
                    "site_id": "SITE02",
                    "visit": "Week 2",
                    "field_name": "platelet_count",
                    "field_value": "45000",
                    "normal_range": "150000-450000 /μL",
                },
                "expected_severity": SeverityLevel.CRITICAL.value,
                "expected_terms": ["platelet", "thrombocytopenia", "bleeding", "low"],
            },
        ]

        for test_case in test_cases:
            # This test will FAIL initially (RED phase)
            result = await query_analyzer.analyze_clinical_data(test_case["data"])

            assert result["success"] is True
            assert result["severity"] == test_case["expected_severity"]

            # Check medical intelligence in clinical interpretation
            clinical_interp = result["clinical_interpretation"].lower()
            assert any(term in clinical_interp for term in test_case["expected_terms"])

            # Should have appropriate medical recommendations
            recommendations = result["ai_analysis"]["recommendations"]
            assert len(recommendations) >= 2
            assert any(
                len(rec) > 10 for rec in recommendations
            )  # Meaningful recommendations

    async def test_human_readable_field_quality(
        self, query_analyzer, critical_hemoglobin_data
    ):
        """Test quality and usefulness of human-readable fields for frontend display"""
        # This test will FAIL initially (RED phase)
        result = await query_analyzer.analyze_clinical_data(critical_hemoglobin_data)

        # Human-readable summary quality checks
        summary = result["human_readable_summary"]
        assert len(summary) >= 50  # Substantial content
        assert len(summary) <= 200  # Not too verbose for UI
        assert summary.count(".") <= 3  # Concise, not overly complex
        assert "SUBJ001" in summary  # Includes subject reference

        # Clinical interpretation quality checks
        interpretation = result["clinical_interpretation"]
        assert "CLINICAL FINDING:" in interpretation
        assert any(
            unit in interpretation for unit in ["g/dL", "mg/dL", "mmHg", "/μL"]
        )  # Medical units
        assert interpretation.count("\n") >= 1  # Multi-line for readability

        # Recommendation summary quality checks
        rec_summary = result["recommendation_summary"]
        assert len(rec_summary) >= 30
        assert any(
            word in rec_summary.lower()
            for word in ["recommend", "suggest", "consider", "should"]
        )
        assert rec_summary.endswith(".")  # Proper sentence structure

    async def test_confidence_scoring_accuracy(self, query_analyzer):
        """Test Query Analyzer provides accurate confidence scores"""
        test_scenarios = [
            {
                "data": {
                    "subject_id": "SUBJ006",
                    "site_id": "SITE01",
                    "visit": "Week 1",
                    "field_name": "hemoglobin",
                    "field_value": "7.0",
                    "normal_range": "12.0-15.5 g/dL",
                },
                "expected_confidence": 0.95,  # Clear critical value
            },
            {
                "data": {
                    "subject_id": "SUBJ007",
                    "site_id": "SITE01",
                    "visit": "Week 1",
                    "field_name": "glucose",
                    "field_value": "102",
                    "normal_range": "70-100 mg/dL",
                },
                "expected_confidence": 0.75,  # Borderline value (less confident)
            },
        ]

        for scenario in test_scenarios:
            # This test will FAIL initially (RED phase)
            result = await query_analyzer.analyze_clinical_data(scenario["data"])

            assert result["success"] is True
            confidence = result["confidence_score"]

            # Should meet expected confidence threshold
            if scenario["expected_confidence"] >= 0.9:
                assert confidence >= 0.85
            else:
                assert confidence >= 0.6 and confidence <= 0.85

    async def test_batch_analysis_capability(self, query_analyzer):
        """Test Query Analyzer can handle batch analysis requests"""
        batch_data = [
            {
                "subject_id": "SUBJ008",
                "site_id": "SITE01",
                "visit": "Week 1",
                "field_name": "hemoglobin",
                "field_value": "8.2",
                "normal_range": "12.0-15.5 g/dL",
            },
            {
                "subject_id": "SUBJ009",
                "site_id": "SITE01",
                "visit": "Week 1",
                "field_name": "systolic_bp",
                "field_value": "165",
                "normal_range": "<140 mmHg",
            },
            {
                "subject_id": "SUBJ010",
                "site_id": "SITE02",
                "visit": "Week 1",
                "field_name": "glucose",
                "field_value": "95",
                "normal_range": "70-100 mg/dL",
            },
        ]

        # This test will FAIL initially (RED phase)
        result = await query_analyzer.batch_analyze_clinical_data(batch_data)

        assert result["success"] is True
        assert "batch_results" in result
        assert len(result["batch_results"]) == 3

        # Each result should be properly formatted
        for batch_result in result["batch_results"]:
            assert "query_id" in batch_result
            assert "severity" in batch_result
            assert "human_readable_summary" in batch_result

        # Should have batch summary
        assert "batch_summary" in result
        summary = result["batch_summary"]
        assert "total_analyses" in summary
        assert "critical_findings" in summary
        assert summary["total_analyses"] == 3


class TestQueryAnalyzerIntegration:
    """Test Query Analyzer integration with Portfolio Manager and endpoints"""

    @pytest.fixture
    def query_analyzer(self):
        return QueryAnalyzer()

    async def test_portfolio_manager_integration(self, query_analyzer):
        """Test Query Analyzer integrates with Portfolio Manager workflow orchestration"""
        from app.agents.portfolio_manager import PortfolioManager

        portfolio_manager = PortfolioManager()

        query_request = {
            "workflow_type": "query_analysis",
            "input_data": {
                "subject_id": "SUBJ011",
                "site_id": "SITE01",
                "visit": "Week 4",
                "field_name": "hemoglobin",
                "field_value": "6.8",
            },
            "workflow_id": "WF_QA_JSON_001",
        }

        # This test will FAIL initially (RED phase)
        result = await portfolio_manager.orchestrate_structured_workflow(query_request)

        assert result["success"] is True
        assert result["workflow_type"] == "query_analysis"
        assert result["agent_coordination"]["primary_agent"] == "query_analyzer"

        # Response data should match QueryAnalyzerResponse structure
        response_data = result["response_data"]
        assert "query_id" in response_data
        assert "severity" in response_data
        assert "human_readable_summary" in response_data
        assert "clinical_interpretation" in response_data

    async def test_structured_endpoint_compatibility(self, query_analyzer):
        """Test Query Analyzer works with structured endpoint format"""
        # Should be compatible with /api/v1/queries/analyze endpoint format
        endpoint_data = {
            "subject_id": "SUBJ012",
            "site_id": "SITE03",
            "visit": "Week 8",
            "clinical_data": {
                "field_name": "systolic_bp",
                "field_value": "190",
                "form_name": "Vital Signs",
                "normal_range": "<140 mmHg",
            },
            "analysis_options": {
                "include_recommendations": True,
                "confidence_threshold": 0.8,
            },
        }

        # This test will FAIL initially (RED phase)
        result = await query_analyzer.analyze_clinical_data(endpoint_data)

        # Should return format compatible with QueryAnalyzerResponse
        assert result["success"] is True
        assert "query_id" in result
        assert result["subject"]["id"] == "SUBJ012"
        assert result["subject"]["site_id"] == "SITE03"

        # Should detect critical BP and recommend actions
        assert result["severity"] == SeverityLevel.CRITICAL.value
        assert len(result["ai_analysis"]["recommendations"]) >= 2


class TestQueryAnalyzerPerformance:
    """Test Query Analyzer performance with JSON output"""

    @pytest.fixture
    def query_analyzer(self):
        return QueryAnalyzer()

    async def test_json_output_performance(self, query_analyzer):
        """Test Query Analyzer JSON output performs efficiently"""
        # This test will FAIL initially (RED phase)

        large_dataset = []
        for i in range(20):  # 20 analyses
            large_dataset.append(
                {
                    "subject_id": f"SUBJ{i:03d}",
                    "site_id": f"SITE{(i % 3) + 1:02d}",
                    "visit": "Week 1",
                    "field_name": "hemoglobin",
                    "field_value": str(7.0 + (i * 0.2)),  # Varying critical values
                    "normal_range": "12.0-15.5 g/dL",
                }
            )

        start_time = datetime.now()
        result = await query_analyzer.batch_analyze_clinical_data(large_dataset)
        execution_time = (datetime.now() - start_time).total_seconds()

        # Should complete efficiently
        assert result["success"] is True
        assert execution_time < 10.0  # Should complete in under 10 seconds

        # Should process all subjects
        assert len(result["batch_results"]) == 20

        # Should have performance metrics
        assert "execution_time" in result
        assert result["execution_time"] < 10.0

    async def test_json_response_size_optimization(self, query_analyzer):
        """Test Query Analyzer JSON responses are optimized for frontend transmission"""
        test_data = {
            "subject_id": "SUBJ013",
            "site_id": "SITE01",
            "visit": "Week 1",
            "field_name": "hemoglobin",
            "field_value": "7.5",
            "normal_range": "12.0-15.5 g/dL",
        }

        # This test will FAIL initially (RED phase)
        result = await query_analyzer.analyze_clinical_data(test_data)

        # JSON size should be reasonable for network transmission
        json_str = json.dumps(result)
        json_size_kb = len(json_str.encode("utf-8")) / 1024

        assert json_size_kb < 50  # Should be under 50KB for efficient transmission

        # Should not have unnecessary verbose fields
        assert "raw_response" not in result or len(result["raw_response"]) < 1000

        # Human-readable fields should be concise but informative
        assert len(result["human_readable_summary"]) < 300
        assert len(result["clinical_interpretation"]) < 500
