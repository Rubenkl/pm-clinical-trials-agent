"""
Integration tests to verify that API endpoints are using AI-powered methods.
Tests that endpoints call the correct AI methods and handle responses properly.
"""

import json
from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestDeviationsEndpointAI:
    """Test that deviations endpoint uses AI-powered detection."""

    def test_detect_deviations_uses_ai_method(self, client):
        """Test that /api/v1/deviations/detect uses detect_protocol_deviations_ai."""

        # Mock AI response
        mock_ai_response = {
            "ai_powered": True,
            "protocol_id": "CARD-2025-001",
            "subject_id": "CARD001",
            "deviations": [
                {
                    "type": "prohibited_medication",
                    "severity": "major",
                    "description": "Subject taking amiodarone (prohibited)",
                    "clinical_impact": "Risk of QT prolongation with study drug",
                    "regulatory_impact": "Major protocol deviation requiring sponsor notification",
                    "recommended_action": "Discontinue amiodarone with washout period",
                }
            ],
            "compliance_score": 0.75,
            "overall_assessment": "Subject has major deviation requiring intervention",
        }

        with patch(
            "app.agents.deviation_detector.DeviationDetector.detect_protocol_deviations_ai",
            new_callable=AsyncMock,
        ) as mock_ai_method:
            mock_ai_method.return_value = mock_ai_response

            # Make request to endpoint
            response = client.post(
                "/api/v1/deviations/detect",
                json={
                    "subject_id": "CARD001",
                    "site_id": "SITE01",
                    "visit": "Week 4",
                    "protocol_data": {
                        "prohibited_medications": ["amiodarone", "dronedarone"]
                    },
                    "actual_data": {
                        "current_medications": ["metoprolol", "amiodarone"]
                    },
                },
            )

            # Verify response
            assert response.status_code == 200
            result = response.json()

            # Verify AI method was called
            assert mock_ai_method.called

            # Verify response contains AI-powered data
            assert result["success"] == True
            assert len(result["deviations"]) == 1
            assert result["deviations"][0]["severity"] == "major"
            assert "amiodarone" in result["deviations"][0]["description"]

            # Check raw response indicates AI usage
            raw = json.loads(result["raw_response"])
            assert raw.get("ai_powered") == True
            assert raw.get("compliance_score") == 0.75


class TestAnalyticsEndpointAI:
    """Test that analytics endpoint uses AI-powered insights."""

    def test_dashboard_analytics_uses_ai_method(self, client):
        """Test that /api/v1/test-data/analytics/dashboard uses generate_analytics_insights_ai."""

        # Mock AI response
        mock_ai_response = {
            "ai_powered": True,
            "study_id": "CARD-2025-001",
            "analytics_insights": {
                "enrollment_analysis": {
                    "status": "at_risk",
                    "completion_probability": 0.68,
                    "key_findings": [
                        "Current rate insufficient to meet target",
                        "Site SITE_003 underperforming",
                    ],
                },
                "quality_analysis": {
                    "overall_score": 0.82,
                    "concerns": ["Query rate above benchmark"],
                },
                "predictive_insights": {
                    "study_completion_date": "2026-01-15",
                    "final_enrollment": 245,
                },
            },
            "executive_summary": "Study at risk of missing enrollment target by 18%.",
        }

        # Mock the test data service
        with patch("app.api.endpoints.test_data.TestDataService") as mock_service_class:
            mock_service = Mock()
            mock_service.is_test_mode.return_value = True
            mock_service.get_available_subjects.return_value = [
                "CARD001",
                "CARD002",
                "CARD003",
            ]
            mock_service_class.return_value = mock_service

            with patch(
                "app.agents.analytics_agent.AnalyticsAgent.generate_analytics_insights_ai",
                new_callable=AsyncMock,
            ) as mock_ai_method:
                mock_ai_method.return_value = mock_ai_response

                # Make request to endpoint
                response = client.get("/api/v1/test-data/analytics/dashboard")

                # Verify response
                assert response.status_code == 200
                result = response.json()

                # Verify AI method was called
                assert mock_ai_method.called

                # Verify response contains data influenced by AI insights
                assert "enrollment_trend" in result
                assert "data_quality_trend" in result
                assert "recent_activities" in result

                # Check that AI insights influenced the response
                # First activity should be AI insight
                assert len(result["recent_activities"]) > 0
                first_activity = result["recent_activities"][0]
                assert first_activity["type"] == "ai_insight"
                assert first_activity["performed_by"] == "AI Analytics"
                assert "18%" in first_activity["description"]  # From executive summary


class TestProtocolDeviationsEndpointAI:
    """Test that protocol deviations endpoint uses AI detection."""

    def test_get_protocol_deviations_uses_ai_method(self, client):
        """Test that /api/v1/test-data/protocol/deviations uses detect_protocol_deviations_ai."""

        # Mock AI response
        mock_ai_response = {
            "ai_powered": True,
            "deviations": [
                {
                    "type": "age_violation",
                    "severity": "critical",
                    "description": "Subject age 17 below inclusion criteria (18-75)",
                    "clinical_impact": "Minor cannot provide informed consent",
                    "regulatory_impact": "Critical GCP violation",
                    "recommended_action": "Immediate subject withdrawal required",
                }
            ],
            "compliance_score": 0.45,
        }

        # Mock the test data service
        with patch("app.api.endpoints.test_data.TestDataService") as mock_service_class:
            mock_service = Mock()
            mock_service.is_test_mode.return_value = True
            mock_service.get_available_subjects.return_value = ["CARD001", "CARD002"]
            mock_service_class.return_value = mock_service

            with patch(
                "app.agents.deviation_detector.DeviationDetector.detect_protocol_deviations_ai",
                new_callable=AsyncMock,
            ) as mock_ai_method:
                mock_ai_method.return_value = mock_ai_response

                # Make request to endpoint
                response = client.get("/api/v1/test-data/protocol/deviations")

                # Verify response
                assert response.status_code == 200
                result = response.json()

                # Verify AI method was called (multiple times for different subjects)
                assert mock_ai_method.called
                assert mock_ai_method.call_count >= 1  # Called for each subject checked

                # Verify response structure
                assert "deviations" in result
                assert "compliance_metrics" in result


class TestSDVEndpointAI:
    """Test that SDV endpoint continues to use AI verification."""

    def test_sdv_verify_uses_ai_method(self, client):
        """Test that /api/v1/sdv/verify continues to use verify_clinical_data_ai."""

        # Mock AI response
        mock_ai_response = {
            "success": True,
            "ai_powered": True,
            "verification_id": "VER-AI-20250110-CARD001",
            "site": "SITE01",
            "monitor": "System",
            "verification_date": datetime.now().isoformat(),
            "subject": {
                "id": "CARD001",
                "initials": "JD",
                "site": "Test Site",
                "site_id": "SITE01",
            },
            "visit": "Baseline",
            "match_score": 0.85,
            "matching_fields": ["age", "gender"],
            "discrepancies": [
                {
                    "field": "hemoglobin",
                    "field_label": "Hemoglobin",
                    "edc_value": "12.5",
                    "source_value": "11.8",
                    "severity": "minor",
                    "discrepancy_type": "value_mismatch",
                    "confidence": 0.92,
                    "medical_significance": "0.7 g/dL difference within normal variation",
                    "recommended_action": "Verify with source document",
                }
            ],
            "total_fields_compared": 10,
            "progress": {
                "total_fields": 10,
                "verified": 9,
                "discrepancies": 1,
                "skipped": 0,
                "completion_rate": 0.9,
                "estimated_time_remaining": 5,
            },
            "fields_to_verify": [],
            "recommendations": ["Complete verification"],
            "critical_findings": [],
            "execution_time": 1.2,
            "raw_response": "{}",
        }

        with patch(
            "app.agents.data_verifier.DataVerifier.verify_clinical_data_ai",
            new_callable=AsyncMock,
        ) as mock_ai_method:
            mock_ai_method.return_value = mock_ai_response

            # Make request to endpoint
            response = client.post(
                "/api/v1/sdv/verify",
                json={
                    "subject_id": "CARD001",
                    "site_id": "SITE01",
                    "visit": "Baseline",
                    "edc_data": {"hemoglobin": "12.5"},
                    "source_data": {"hemoglobin": "11.8"},
                },
            )

            # Verify response
            assert response.status_code == 200
            result = response.json()

            # Verify AI method was called
            assert mock_ai_method.called

            # Verify response contains AI-powered verification
            assert result["success"] == True
            assert result["match_score"] == 0.85
            assert len(result["discrepancies"]) == 1
            assert "medical_significance" in result["discrepancies"][0]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
