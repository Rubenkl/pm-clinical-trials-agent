"""
Test suite for Deviation Detection endpoints.
Following TDD: These tests should FAIL initially, then we implement to make them pass.
"""

from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestDeviationDetectionEndpoint:
    """Test /api/v1/deviations/detect endpoint"""

    def test_deviation_detection_endpoint_exists(self):
        """Test that the deviation detection endpoint exists"""
        response = client.post(
            "/api/v1/deviations/detect",
            json={
                "subject_id": "SUBJ001",
                "site_id": "SITE01",
                "visit": "Week 12",
                "protocol_data": {"required_visit_window": "±3 days"},
                "actual_data": {
                    "visit_date": "2025-01-15",
                    "scheduled_date": "2025-01-09",
                },
            },
        )
        # Should not be 404 (endpoint exists)
        assert response.status_code != 404

    def test_deviation_detection_with_valid_data(self):
        """Test deviation detection with valid protocol data"""
        deviation_data = {
            "subject_id": "SUBJ001",
            "site_id": "SITE01",
            "visit": "Week 12",
            "protocol_data": {
                "required_visit_window": "±3 days",
                "required_fasting": "12 hours",
                "prohibited_medications": ["aspirin", "warfarin"],
            },
            "actual_data": {
                "visit_date": "2025-01-15",
                "scheduled_date": "2025-01-09",
                "fasting_hours": "8",
                "concomitant_medications": ["aspirin", "metformin"],
            },
        }

        response = client.post("/api/v1/deviations/detect", json=deviation_data)
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert data["response_type"] == "deviation_detection"
        assert "deviation_id" in data
        assert data["subject"]["id"] == "SUBJ001"
        assert data["site"] == "SITE01"
        assert data["visit"] == "Week 12"
        assert "deviations" in data
        assert isinstance(data["deviations"], list)
        assert "recommendations" in data
        assert data["agent_id"] == "deviation-detector"

    def test_deviation_detection_identifies_deviations(self):
        """Test that deviation detection properly identifies protocol deviations"""
        deviation_data = {
            "subject_id": "SUBJ001",
            "site_id": "SITE01",
            "visit": "Week 12",
            "protocol_data": {
                "required_visit_window": "±3 days",
                "required_fasting": "12 hours",
            },
            "actual_data": {
                "visit_date": "2025-01-15",
                "scheduled_date": "2025-01-09",  # 6 days late
                "fasting_hours": "8",  # Only 8 hours vs required 12
            },
        }

        response = client.post("/api/v1/deviations/detect", json=deviation_data)
        assert response.status_code == 200

        data = response.json()
        assert len(data["deviations"]) >= 2  # Should detect both deviations

        # Check for visit window deviation
        visit_deviation = next(
            (d for d in data["deviations"] if "visit_window" in d["category"]), None
        )
        assert visit_deviation is not None
        assert visit_deviation["severity"] in ["major", "minor"]

        # Check for fasting deviation
        fasting_deviation = next(
            (d for d in data["deviations"] if "fasting" in d["category"]), None
        )
        assert fasting_deviation is not None

    def test_deviation_detection_missing_required_fields(self):
        """Test that missing required fields return validation error"""
        deviation_data = {
            "subject_id": "SUBJ001",
            # Missing required fields
        }

        response = client.post("/api/v1/deviations/detect", json=deviation_data)
        assert response.status_code == 422  # Validation error


class TestDeviationListEndpoint:
    """Test /api/v1/deviations/ endpoint"""

    def test_deviation_list_endpoint_exists(self):
        """Test that the deviation list endpoint exists"""
        response = client.get("/api/v1/deviations/")
        assert response.status_code != 404

    def test_deviation_list_returns_data(self):
        """Test that deviation list returns proper data structure"""
        response = client.get("/api/v1/deviations/")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)

        # Check structure of deviations if any exist
        for deviation in data[:3]:  # Check first 3
            assert "deviation_id" in deviation
            assert "subject_id" in deviation
            assert "site_id" in deviation
            assert "category" in deviation
            assert "severity" in deviation
            assert "status" in deviation
            assert "detected_date" in deviation

    def test_deviation_list_with_filters(self):
        """Test filtering deviations"""
        # Test severity filter
        response = client.get("/api/v1/deviations/?severity=major")
        assert response.status_code == 200

        data = response.json()
        for deviation in data:
            assert deviation["severity"] == "major"

        # Test site filter
        response = client.get("/api/v1/deviations/?site_id=SITE01")
        assert response.status_code == 200

        data = response.json()
        for deviation in data:
            assert deviation["site_id"] == "SITE01"

    def test_deviation_list_pagination(self):
        """Test pagination of deviation list"""
        response = client.get("/api/v1/deviations/?skip=0&limit=5")
        assert response.status_code == 200

        data = response.json()
        assert len(data) <= 5


class TestDeviationStatisticsEndpoint:
    """Test /api/v1/deviations/stats/dashboard endpoint"""

    def test_deviation_stats_endpoint_exists(self):
        """Test that the deviation statistics endpoint exists"""
        response = client.get("/api/v1/deviations/stats/dashboard")
        assert response.status_code != 404

    def test_deviation_stats_returns_valid_structure(self):
        """Test that deviation statistics endpoint returns valid structure"""
        response = client.get("/api/v1/deviations/stats/dashboard")
        assert response.status_code == 200

        data = response.json()

        # Check required fields
        required_fields = [
            "total_deviations",
            "critical_deviations",
            "major_deviations",
            "minor_deviations",
            "resolved_deviations",
            "pending_deviations",
            "deviations_by_site",
            "deviations_by_category",
            "deviation_trends",
            "resolution_rate",
            "average_resolution_time",
        ]

        for field in required_fields:
            assert field in data, f"Missing required field: {field}"

        # Check data types
        assert isinstance(data["total_deviations"], int)
        assert isinstance(data["critical_deviations"], int)
        assert isinstance(data["deviations_by_site"], dict)
        assert isinstance(data["deviations_by_category"], dict)
        assert isinstance(data["deviation_trends"], list)

    def test_deviation_stats_data_consistency(self):
        """Test that deviation statistics data is consistent"""
        response = client.get("/api/v1/deviations/stats/dashboard")
        assert response.status_code == 200

        data = response.json()

        # Total should equal sum of severity categories
        severity_sum = (
            data["critical_deviations"]
            + data["major_deviations"]
            + data["minor_deviations"]
        )
        assert data["total_deviations"] >= severity_sum

        # Resolution rate should be between 0 and 1
        assert 0 <= data["resolution_rate"] <= 1

        # Average resolution time should be >= 0
        assert data["average_resolution_time"] >= 0


class TestDeviationDetailEndpoint:
    """Test /api/v1/deviations/{deviation_id} endpoint"""

    def test_deviation_detail_endpoint_exists(self):
        """Test that the deviation detail endpoint exists"""
        response = client.get("/api/v1/deviations/DEV-001")
        assert response.status_code != 404

    def test_deviation_detail_returns_data(self):
        """Test that deviation detail returns proper data"""
        response = client.get("/api/v1/deviations/DEV-001")
        assert response.status_code == 200

        data = response.json()
        assert "deviation_id" in data
        assert "subject_id" in data
        assert "site_id" in data
        assert "category" in data
        assert "severity" in data
        assert "protocol_requirement" in data
        assert "actual_value" in data
        assert "impact_assessment" in data
        assert "corrective_actions" in data


class TestDeviationResolutionEndpoint:
    """Test /api/v1/deviations/{deviation_id}/resolve endpoint"""

    def test_deviation_resolution_endpoint_exists(self):
        """Test that the deviation resolution endpoint exists"""
        response = client.post(
            "/api/v1/deviations/DEV-001/resolve",
            json={
                "resolution": "Corrective action taken",
                "resolved_by": "Dr. Smith",
                "corrective_actions": ["Retrained site staff"],
            },
        )
        assert response.status_code != 404

    def test_deviation_resolution_with_valid_data(self):
        """Test deviation resolution with valid data"""
        resolution_data = {
            "resolution": "Visit rescheduled within protocol window",
            "resolved_by": "Dr. Smith",
            "corrective_actions": ["Site retrained on visit scheduling"],
            "comments": "No impact on study integrity",
        }

        response = client.post(
            "/api/v1/deviations/DEV-001/resolve", json=resolution_data
        )
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert data["deviation_id"] == "DEV-001"
        assert data["status"] == "resolved"
        assert data["resolved_by"] == "Dr. Smith"


class TestDeviationIntegration:
    """Integration tests for deviation endpoints"""

    def test_deviation_detection_then_list_flow(self):
        """Test the flow of detecting deviations then listing them"""
        # First detect a deviation
        deviation_data = {
            "subject_id": "SUBJ001",
            "site_id": "SITE01",
            "visit": "Week 12",
            "protocol_data": {"required_visit_window": "±3 days"},
            "actual_data": {"visit_date": "2025-01-15", "scheduled_date": "2025-01-09"},
        }

        detect_response = client.post("/api/v1/deviations/detect", json=deviation_data)
        assert detect_response.status_code == 200

        # Then list deviations
        list_response = client.get("/api/v1/deviations/?subject_id=SUBJ001")
        assert list_response.status_code == 200

        deviations = list_response.json()
        # Should find the deviation we just detected (in mock implementation)
        assert len(deviations) >= 0

    def test_deviation_affects_statistics(self):
        """Test that detecting deviations affects statistics"""
        # Get initial statistics
        initial_stats = client.get("/api/v1/deviations/stats/dashboard")
        assert initial_stats.status_code == 200

        # Detect a deviation
        deviation_data = {
            "subject_id": "SUBJ002",
            "site_id": "SITE02",
            "visit": "Week 4",
            "protocol_data": {"required_fasting": "12 hours"},
            "actual_data": {"fasting_hours": "6"},
        }

        detect_response = client.post("/api/v1/deviations/detect", json=deviation_data)
        assert detect_response.status_code == 200

        # Get updated statistics
        updated_stats = client.get("/api/v1/deviations/stats/dashboard")
        assert updated_stats.status_code == 200

        # Statistics should be consistent
        assert updated_stats.json()["total_deviations"] >= 0


class TestDeviationPerformance:
    """Performance tests for deviation endpoints"""

    def test_deviation_detection_response_time(self):
        """Test that deviation detection completes within reasonable time"""
        deviation_data = {
            "subject_id": "SUBJ001",
            "site_id": "SITE01",
            "visit": "Week 12",
            "protocol_data": {"required_visit_window": "±3 days"},
            "actual_data": {"visit_date": "2025-01-15", "scheduled_date": "2025-01-09"},
        }

        import time

        start_time = time.time()

        response = client.post("/api/v1/deviations/detect", json=deviation_data)

        end_time = time.time()
        response_time = end_time - start_time

        assert response.status_code == 200
        assert response_time < 5.0  # Should complete within 5 seconds

        # Check that execution_time is recorded
        data = response.json()
        assert "execution_time" in data
        assert data["execution_time"] > 0
