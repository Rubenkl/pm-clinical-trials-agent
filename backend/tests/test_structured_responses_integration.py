"""
Integration tests for structured responses to verify frontend compatibility.
Tests that all endpoints return properly structured JSON for frontend consumption.
"""

import json
from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestQueryResponseStructure:
    """Test query endpoints return proper structure for frontend"""

    def test_query_analyze_response_structure(self):
        """Test that query analysis returns frontend-compatible structure"""
        query_data = {
            "subject_id": "SUBJ001",
            "site_id": "SITE01",
            "visit": "Week 12",
            "field_name": "hemoglobin",
            "field_value": "8.5",
            "form_name": "Laboratory Results",
        }

        response = client.post("/api/v1/queries/analyze", json=query_data)
        assert response.status_code == 200

        data = response.json()

        # Verify frontend-required fields
        frontend_fields = [
            "success",
            "response_type",
            "query_id",
            "created_date",
            "status",
            "severity",
            "category",
            "subject",
            "clinical_context",
            "clinical_findings",
            "ai_analysis",
            "execution_time",
            "confidence_score",
        ]

        for field in frontend_fields:
            assert field in data, f"Missing frontend field: {field}"

        # Verify nested object structures
        assert isinstance(data["subject"], dict)
        assert "id" in data["subject"]
        assert "site_id" in data["subject"]

        assert isinstance(data["clinical_findings"], list)
        if data["clinical_findings"]:
            finding = data["clinical_findings"][0]
            assert "parameter" in finding
            assert "value" in finding
            assert "severity" in finding
            assert "interpretation" in finding

        assert isinstance(data["ai_analysis"], dict)
        assert "interpretation" in data["ai_analysis"]
        assert "recommendations" in data["ai_analysis"]

    def test_query_list_response_structure(self):
        """Test that query list returns frontend-compatible pagination"""
        response = client.get("/api/v1/queries/?skip=0&limit=5")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)

        # Verify each query item has frontend fields
        for query in data[:3]:  # Check first 3 items
            assert "query_id" in query
            assert "subject" in query
            assert "severity" in query
            assert "status" in query
            assert "created_date" in query

    def test_query_statistics_response_structure(self):
        """Test that query statistics return dashboard-compatible data"""
        response = client.get("/api/v1/queries/stats/dashboard")
        assert response.status_code == 200

        data = response.json()

        # Verify dashboard widget compatibility
        dashboard_fields = [
            "total_queries",
            "open_queries",
            "critical_queries",
            "queries_by_site",
            "queries_by_category",
            "trend_data",
        ]

        for field in dashboard_fields:
            assert field in data, f"Missing dashboard field: {field}"

        # Verify chart data format
        assert isinstance(data["queries_by_site"], dict)
        assert isinstance(data["queries_by_category"], dict)
        assert isinstance(data["trend_data"], list)

        # Verify trend data format for charts
        if data["trend_data"]:
            trend_item = data["trend_data"][0]
            assert "date" in trend_item
            assert "queries" in trend_item


class TestSDVResponseStructure:
    """Test SDV endpoints return proper structure for frontend"""

    def test_sdv_verify_response_structure(self):
        """Test that SDV verification returns frontend-compatible structure"""
        sdv_data = {
            "subject_id": "SUBJ001",
            "site_id": "SITE01",
            "visit": "Week 12",
            "edc_data": {"hemoglobin": "12.5", "bp": "120/80"},
            "source_data": {"hemoglobin": "12.3", "bp": "125/85"},
        }

        response = client.post("/api/v1/sdv/verify", json=sdv_data)
        assert response.status_code == 200

        data = response.json()

        # Verify frontend-required fields for SDV
        sdv_fields = [
            "success",
            "response_type",
            "verification_id",
            "site",
            "monitor",
            "verification_date",
            "subject",
            "visit",
            "match_score",
            "discrepancies",
            "recommendations",
            "progress",
            "execution_time",
        ]

        for field in sdv_fields:
            assert field in data, f"Missing SDV field: {field}"

        # Verify match score is percentage-compatible
        assert 0 <= data["match_score"] <= 1

        # Verify discrepancy structure for frontend tables
        assert isinstance(data["discrepancies"], list)
        for discrepancy in data["discrepancies"][:2]:  # Check first 2
            assert "field" in discrepancy
            assert "edc_value" in discrepancy
            assert "source_value" in discrepancy
            assert "severity" in discrepancy

        # Verify progress data for progress bars
        progress = data["progress"]
        assert "total_fields" in progress
        assert "verified" in progress
        assert "completion_rate" in progress

    def test_sdv_statistics_response_structure(self):
        """Test that SDV statistics return dashboard-compatible data"""
        response = client.get("/api/v1/sdv/stats/dashboard")
        assert response.status_code == 200

        data = response.json()

        # Verify SDV dashboard fields
        sdv_dashboard_fields = [
            "total_subjects",
            "verified_subjects",
            "overall_completion",
            "discrepancy_rate",
            "sites_summary",
            "high_risk_sites",
        ]

        for field in sdv_dashboard_fields:
            assert field in data, f"Missing SDV dashboard field: {field}"

        # Verify completion rates are percentage-compatible
        assert 0 <= data["overall_completion"] <= 1
        assert data["discrepancy_rate"] >= 0

        # Verify sites data for frontend tables
        assert isinstance(data["sites_summary"], list)
        for site in data["sites_summary"]:
            assert "site_id" in site
            assert "completion_rate" in site
            assert "discrepancy_rate" in site


class TestDeviationResponseStructure:
    """Test deviation endpoints return proper structure for frontend"""

    def test_deviation_detect_response_structure(self):
        """Test that deviation detection returns frontend-compatible structure"""
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
                "scheduled_date": "2025-01-09",
                "fasting_hours": "8",
            },
        }

        response = client.post("/api/v1/deviations/detect", json=deviation_data)
        assert response.status_code == 200

        data = response.json()

        # Verify frontend-required fields for deviations
        deviation_fields = [
            "success",
            "response_type",
            "deviation_id",
            "subject",
            "site",
            "visit",
            "deviations",
            "total_deviations_found",
            "impact_assessment",
            "recommendations",
            "corrective_actions_required",
            "execution_time",
        ]

        for field in deviation_fields:
            assert field in data, f"Missing deviation field: {field}"

        # Verify deviation structure for frontend tables
        assert isinstance(data["deviations"], list)
        for deviation in data["deviations"]:
            assert "category" in deviation
            assert "severity" in deviation
            assert "protocol_requirement" in deviation
            assert "actual_value" in deviation
            assert "corrective_action_required" in deviation

        # Verify counts match
        assert data["total_deviations_found"] == len(data["deviations"])

    def test_deviation_statistics_response_structure(self):
        """Test that deviation statistics return dashboard-compatible data"""
        response = client.get("/api/v1/deviations/stats/dashboard")
        assert response.status_code == 200

        data = response.json()

        # Verify deviation dashboard fields
        deviation_dashboard_fields = [
            "total_deviations",
            "critical_deviations",
            "major_deviations",
            "minor_deviations",
            "resolution_rate",
            "average_resolution_time",
            "deviations_by_site",
            "deviations_by_category",
            "deviation_trends",
        ]

        for field in deviation_dashboard_fields:
            assert field in data, f"Missing deviation dashboard field: {field}"

        # Verify resolution rate is percentage-compatible
        assert 0 <= data["resolution_rate"] <= 1

        # Verify trend data format for charts
        assert isinstance(data["deviation_trends"], list)
        if data["deviation_trends"]:
            trend_item = data["deviation_trends"][0]
            assert "date" in trend_item
            assert "deviations" in trend_item


class TestCrossWorkflowCompatibility:
    """Test that responses work together for integrated frontend views"""

    def test_subject_data_consistency(self):
        """Test that subject data is consistent across all workflows"""
        subject_id = "SUBJ001"
        site_id = "SITE01"

        # Get data from all three workflows
        query_response = client.post(
            "/api/v1/queries/analyze",
            json={
                "subject_id": subject_id,
                "site_id": site_id,
                "visit": "Week 12",
                "field_name": "hemoglobin",
                "field_value": "8.5",
                "form_name": "Lab Results",
            },
        )

        sdv_response = client.post(
            "/api/v1/sdv/verify",
            json={
                "subject_id": subject_id,
                "site_id": site_id,
                "visit": "Week 12",
                "edc_data": {"hemoglobin": "8.5"},
                "source_data": {"hemoglobin": "8.3"},
            },
        )

        deviation_response = client.post(
            "/api/v1/deviations/detect",
            json={
                "subject_id": subject_id,
                "site_id": site_id,
                "visit": "Week 12",
                "protocol_data": {"required_visit_window": "±3 days"},
                "actual_data": {
                    "visit_date": "2025-01-15",
                    "scheduled_date": "2025-01-09",
                },
            },
        )

        # Verify all succeed
        assert query_response.status_code == 200
        assert sdv_response.status_code == 200
        assert deviation_response.status_code == 200

        # Verify subject consistency
        query_data = query_response.json()
        sdv_data = sdv_response.json()
        deviation_data = deviation_response.json()

        assert query_data["subject"]["id"] == subject_id
        assert sdv_data["subject"]["id"] == subject_id
        assert deviation_data["subject"]["id"] == subject_id

        assert query_data["subject"]["site_id"] == site_id
        assert sdv_data["subject"]["site_id"] == site_id
        # Note: deviation uses "site" not "subject.site_id"
        assert deviation_data["site"] == site_id

    def test_dashboard_data_aggregation(self):
        """Test that dashboard statistics can be aggregated for overview"""
        # Get all dashboard statistics
        query_stats = client.get("/api/v1/queries/stats/dashboard")
        sdv_stats = client.get("/api/v1/sdv/stats/dashboard")
        deviation_stats = client.get("/api/v1/deviations/stats/dashboard")

        assert query_stats.status_code == 200
        assert sdv_stats.status_code == 200
        assert deviation_stats.status_code == 200

        query_data = query_stats.json()
        sdv_data = sdv_stats.json()
        deviation_data = deviation_stats.json()

        # Verify we can aggregate site data
        query_sites = set(query_data["queries_by_site"].keys())
        sdv_sites = set(site["site_id"] for site in sdv_data["sites_summary"])
        deviation_sites = set(deviation_data["deviations_by_site"].keys())

        # Should have overlapping sites for integrated dashboard
        assert len(query_sites & sdv_sites & deviation_sites) > 0

    def test_severity_consistency(self):
        """Test that severity levels are consistent across workflows"""
        severity_levels = ["critical", "major", "minor", "info"]

        # Test query severity
        query_response = client.post(
            "/api/v1/queries/analyze",
            json={
                "subject_id": "SUBJ001",
                "site_id": "SITE01",
                "visit": "Week 12",
                "field_name": "hemoglobin",
                "field_value": "7.5",  # Critical value
                "form_name": "Lab Results",
            },
        )

        assert query_response.status_code == 200
        query_data = query_response.json()
        assert query_data["severity"] in severity_levels

        # Test SDV discrepancy severity
        sdv_response = client.post(
            "/api/v1/sdv/verify",
            json={
                "subject_id": "SUBJ001",
                "site_id": "SITE01",
                "visit": "Week 12",
                "edc_data": {"hemoglobin": "12.5"},
                "source_data": {"hemoglobin": "7.5"},  # Major discrepancy
            },
        )

        assert sdv_response.status_code == 200
        sdv_data = sdv_response.json()
        for discrepancy in sdv_data["discrepancies"]:
            assert discrepancy["severity"] in severity_levels

        # Test deviation severity
        deviation_response = client.post(
            "/api/v1/deviations/detect",
            json={
                "subject_id": "SUBJ001",
                "site_id": "SITE01",
                "visit": "Week 12",
                "protocol_data": {"prohibited_medications": ["aspirin"]},
                "actual_data": {
                    "concomitant_medications": ["aspirin"]
                },  # Critical deviation
            },
        )

        assert deviation_response.status_code == 200
        deviation_data = deviation_response.json()
        for deviation in deviation_data["deviations"]:
            assert deviation["severity"] in severity_levels


class TestFrontendComponentCompatibility:
    """Test specific frontend component data requirements"""

    def test_data_table_compatibility(self):
        """Test that list endpoints return data suitable for frontend tables"""
        # Test queries list for data table
        queries = client.get("/api/v1/queries/?limit=10")
        assert queries.status_code == 200

        query_data = queries.json()
        for query in query_data:
            # Verify table column data
            assert "query_id" in query  # ID column
            assert "subject" in query and "id" in query["subject"]  # Subject column
            assert "severity" in query  # Severity column with badge
            assert "status" in query  # Status column with badge
            assert "created_date" in query  # Date column

        # Test SDV discrepancies list
        discrepancies = client.get("/api/v1/sdv/discrepancies?limit=10")
        assert discrepancies.status_code == 200

        discrepancy_data = discrepancies.json()
        for discrepancy in discrepancy_data:
            # Verify discrepancy table columns
            assert "discrepancy_id" in discrepancy
            assert "subject_id" in discrepancy
            assert "field" in discrepancy
            assert "edc_value" in discrepancy
            assert "source_value" in discrepancy
            assert "severity" in discrepancy

    def test_chart_data_compatibility(self):
        """Test that statistics return data suitable for frontend charts"""
        # Test trend data for line charts
        query_stats = client.get("/api/v1/queries/stats/dashboard")
        assert query_stats.status_code == 200

        data = query_stats.json()
        trend_data = data["trend_data"]

        # Verify chart data format
        for point in trend_data:
            assert "date" in point  # X-axis
            assert "queries" in point  # Y-axis
            # Verify date format is compatible
            datetime.fromisoformat(point["date"])

        # Test pie chart data
        assert isinstance(data["queries_by_category"], dict)
        category_data = data["queries_by_category"]

        # Verify pie chart format (label: value)
        for category, count in category_data.items():
            assert isinstance(category, str)  # Label
            assert isinstance(count, int)  # Value

    def test_progress_bar_compatibility(self):
        """Test that progress data works with frontend progress components"""
        sdv_progress = client.get("/api/v1/sdv/progress")
        assert sdv_progress.status_code == 200

        data = sdv_progress.json()

        # Verify progress bar data
        assert "total_subjects" in data
        assert "verified_subjects" in data
        assert "completion_rate" in data

        # Verify percentage calculation
        if data["total_subjects"] > 0:
            calculated_rate = data["verified_subjects"] / data["total_subjects"]
            assert abs(calculated_rate - data["completion_rate"]) < 0.01

        # Verify percentage is in valid range for progress bars
        assert 0 <= data["completion_rate"] <= 1

    def test_notification_data_compatibility(self):
        """Test that critical findings can trigger frontend notifications"""
        # Test critical hemoglobin value
        critical_query = client.post(
            "/api/v1/queries/analyze",
            json={
                "subject_id": "SUBJ001",
                "site_id": "SITE01",
                "visit": "Week 12",
                "field_name": "hemoglobin",
                "field_value": "6.5",  # Critical value
                "form_name": "Lab Results",
            },
        )

        assert critical_query.status_code == 200
        data = critical_query.json()

        # Verify notification trigger data
        if data["severity"] == "critical":
            assert "ai_analysis" in data
            assert "recommendations" in data["ai_analysis"]
            assert len(data["ai_analysis"]["recommendations"]) > 0

            # Verify urgent action indicators
            recommendations = data["ai_analysis"]["recommendations"]
            urgent_keywords = ["immediate", "urgent", "critical", "emergency"]
            has_urgent = any(
                any(keyword in rec.lower() for keyword in urgent_keywords)
                for rec in recommendations
            )
            # Should have urgent recommendations for critical values
            assert has_urgent or data["confidence_score"] >= 0.9
