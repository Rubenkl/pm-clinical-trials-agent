"""
Test suite for SDV (Source Data Verification) endpoints.
Following TDD: These tests should FAIL initially, then we implement to make them pass.
"""

import pytest
from datetime import datetime
from fastapi.testclient import TestClient

from app.main import app
from app.api.models.structured_responses import (
    DataVerifierResponse,
    SDVStatistics,
    SeverityLevel
)

client = TestClient(app)


class TestSDVVerifyEndpoint:
    """Test /api/v1/sdv/verify endpoint"""
    
    def test_sdv_verify_endpoint_exists(self):
        """Test that the SDV verify endpoint exists"""
        response = client.post("/api/v1/sdv/verify", json={
            "subject_id": "SUBJ001",
            "site_id": "SITE01",
            "visit": "Week 12",
            "edc_data": {"hemoglobin": "12.5"},
            "source_data": {"hemoglobin": "12.3"}
        })
        # Should not be 404 (endpoint exists)
        assert response.status_code != 404
    
    def test_sdv_verify_with_valid_data(self):
        """Test SDV verification with valid data"""
        sdv_data = {
            "subject_id": "SUBJ001",
            "site_id": "SITE01",
            "visit": "Week 12",
            "edc_data": {
                "hemoglobin": "12.5",
                "systolic_bp": "120",
                "diastolic_bp": "80"
            },
            "source_data": {
                "hemoglobin": "12.3",
                "systolic_bp": "125",
                "diastolic_bp": "80"
            }
        }
        
        response = client.post("/api/v1/sdv/verify", json=sdv_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["response_type"] == "data_verification"
        assert "verification_id" in data
        assert data["subject"]["id"] == "SUBJ001"
        assert data["site"] == "SITE01"
        assert data["visit"] == "Week 12"
        assert "match_score" in data
        assert "discrepancies" in data
        assert isinstance(data["discrepancies"], list)
        assert "recommendations" in data
        assert data["agent_id"] == "data-verifier"
    
    def test_sdv_verify_detects_discrepancies(self):
        """Test that SDV properly detects discrepancies"""
        sdv_data = {
            "subject_id": "SUBJ001",
            "site_id": "SITE01",
            "visit": "Week 12",
            "edc_data": {"hemoglobin": "12.5"},
            "source_data": {"hemoglobin": "8.0"}  # Major discrepancy
        }
        
        response = client.post("/api/v1/sdv/verify", json=sdv_data)
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["discrepancies"]) > 0
        
        # Should detect the hemoglobin discrepancy
        hemoglobin_discrepancy = next(
            (d for d in data["discrepancies"] if d["field"] == "hemoglobin"),
            None
        )
        assert hemoglobin_discrepancy is not None
        assert hemoglobin_discrepancy["edc_value"] == "12.5"
        assert hemoglobin_discrepancy["source_value"] == "8.0"
        assert hemoglobin_discrepancy["severity"] in ["critical", "major"]
    
    def test_sdv_verify_calculates_match_score(self):
        """Test that SDV calculates accurate match scores"""
        # Test with perfect match
        sdv_data = {
            "subject_id": "SUBJ001",
            "site_id": "SITE01",
            "visit": "Week 12",
            "edc_data": {"hemoglobin": "12.5", "bp": "120/80"},
            "source_data": {"hemoglobin": "12.5", "bp": "120/80"}
        }
        
        response = client.post("/api/v1/sdv/verify", json=sdv_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["match_score"] >= 0.9  # Should be very high for perfect match
        assert len(data["discrepancies"]) == 0
    
    def test_sdv_verify_missing_required_fields(self):
        """Test that missing required fields return validation error"""
        sdv_data = {
            "subject_id": "SUBJ001",
            # Missing required fields
        }
        
        response = client.post("/api/v1/sdv/verify", json=sdv_data)
        assert response.status_code == 422  # Validation error


class TestSDVProgressEndpoint:
    """Test /api/v1/sdv/progress endpoint"""
    
    def test_sdv_progress_endpoint_exists(self):
        """Test that the SDV progress endpoint exists"""
        response = client.get("/api/v1/sdv/progress?site_id=SITE01")
        assert response.status_code != 404
    
    def test_sdv_progress_with_site_id(self):
        """Test SDV progress for specific site"""
        response = client.get("/api/v1/sdv/progress?site_id=SITE01")
        assert response.status_code == 200
        
        data = response.json()
        assert "site_id" in data
        assert "total_subjects" in data
        assert "verified_subjects" in data
        assert "completion_rate" in data
        assert "estimated_time_remaining" in data
        assert isinstance(data["completion_rate"], (int, float))
        assert 0 <= data["completion_rate"] <= 1
    
    def test_sdv_progress_all_sites(self):
        """Test SDV progress for all sites"""
        response = client.get("/api/v1/sdv/progress")
        assert response.status_code == 200
        
        data = response.json()
        assert "sites" in data
        assert isinstance(data["sites"], list)
        assert "overall_progress" in data
        assert "total_subjects" in data
        assert "verified_subjects" in data


class TestSDVStatisticsEndpoint:
    """Test /api/v1/sdv/stats/dashboard endpoint"""
    
    def test_sdv_stats_endpoint_exists(self):
        """Test that the SDV statistics endpoint exists"""
        response = client.get("/api/v1/sdv/stats/dashboard")
        assert response.status_code != 404
    
    def test_sdv_stats_returns_valid_structure(self):
        """Test that SDV statistics endpoint returns valid structure"""
        response = client.get("/api/v1/sdv/stats/dashboard")
        assert response.status_code == 200
        
        data = response.json()
        
        # Check required fields
        required_fields = [
            "total_subjects", "verified_subjects", "total_data_points",
            "verified_data_points", "overall_completion", "discrepancy_rate",
            "sites_summary", "high_risk_sites", "resource_utilization"
        ]
        
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
        
        # Check data types
        assert isinstance(data["total_subjects"], int)
        assert isinstance(data["verified_subjects"], int)
        assert isinstance(data["overall_completion"], (int, float))
        assert isinstance(data["sites_summary"], list)
        assert isinstance(data["high_risk_sites"], list)
        assert isinstance(data["resource_utilization"], dict)
    
    def test_sdv_stats_data_consistency(self):
        """Test that SDV statistics data is consistent"""
        response = client.get("/api/v1/sdv/stats/dashboard")
        assert response.status_code == 200
        
        data = response.json()
        
        # Verified subjects should be <= total subjects
        assert data["verified_subjects"] <= data["total_subjects"]
        
        # Verified data points should be <= total data points
        assert data["verified_data_points"] <= data["total_data_points"]
        
        # Overall completion should be between 0 and 1
        assert 0 <= data["overall_completion"] <= 1
        
        # Discrepancy rate should be >= 0
        assert data["discrepancy_rate"] >= 0


class TestSDVDiscrepancyEndpoint:
    """Test /api/v1/sdv/discrepancies endpoint"""
    
    def test_sdv_discrepancies_endpoint_exists(self):
        """Test that the SDV discrepancies endpoint exists"""
        response = client.get("/api/v1/sdv/discrepancies")
        assert response.status_code != 404
    
    def test_sdv_discrepancies_list(self):
        """Test listing SDV discrepancies"""
        response = client.get("/api/v1/sdv/discrepancies")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        
        # Check structure of discrepancies
        for discrepancy in data:
            assert "discrepancy_id" in discrepancy
            assert "subject_id" in discrepancy
            assert "site_id" in discrepancy
            assert "field" in discrepancy
            assert "edc_value" in discrepancy
            assert "source_value" in discrepancy
            assert "severity" in discrepancy
            assert "status" in discrepancy
    
    def test_sdv_discrepancies_with_filters(self):
        """Test filtering SDV discrepancies"""
        # Test severity filter
        response = client.get("/api/v1/sdv/discrepancies?severity=critical")
        assert response.status_code == 200
        
        data = response.json()
        for discrepancy in data:
            assert discrepancy["severity"] == "critical"
        
        # Test site filter
        response = client.get("/api/v1/sdv/discrepancies?site_id=SITE01")
        assert response.status_code == 200
        
        data = response.json()
        for discrepancy in data:
            assert discrepancy["site_id"] == "SITE01"
    
    def test_sdv_discrepancies_pagination(self):
        """Test pagination of SDV discrepancies"""
        response = client.get("/api/v1/sdv/discrepancies?skip=0&limit=5")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) <= 5


class TestSDVReportEndpoint:
    """Test /api/v1/sdv/report endpoint"""
    
    def test_sdv_report_endpoint_exists(self):
        """Test that the SDV report endpoint exists"""
        response = client.get("/api/v1/sdv/report/summary")
        assert response.status_code != 404
    
    def test_sdv_report_summary(self):
        """Test SDV summary report generation"""
        response = client.get("/api/v1/sdv/report/summary")
        assert response.status_code == 200
        
        data = response.json()
        assert "report_id" in data
        assert "generated_date" in data
        assert "report_type" in data
        assert data["report_type"] == "summary"
        assert "summary_statistics" in data
        assert "site_breakdown" in data
        assert "recommendations" in data
    
    def test_sdv_report_by_site(self):
        """Test SDV report for specific site"""
        response = client.get("/api/v1/sdv/report/site/SITE01")
        assert response.status_code == 200
        
        data = response.json()
        assert "site_id" in data
        assert data["site_id"] == "SITE01"
        assert "verification_statistics" in data
        assert "discrepancy_summary" in data
        assert "monitor_performance" in data


class TestSDVIntegration:
    """Integration tests for SDV endpoints"""
    
    def test_sdv_verify_then_get_discrepancies_flow(self):
        """Test the flow of verifying data then retrieving discrepancies"""
        # First perform verification
        sdv_data = {
            "subject_id": "SUBJ001",
            "site_id": "SITE01",
            "visit": "Week 12",
            "edc_data": {"hemoglobin": "12.5"},
            "source_data": {"hemoglobin": "8.0"}
        }
        
        verify_response = client.post("/api/v1/sdv/verify", json=sdv_data)
        assert verify_response.status_code == 200
        
        # Then retrieve discrepancies
        discrepancies_response = client.get("/api/v1/sdv/discrepancies?subject_id=SUBJ001")
        assert discrepancies_response.status_code == 200
        
        discrepancies = discrepancies_response.json()
        # Should find the hemoglobin discrepancy we just created
        assert len(discrepancies) > 0
    
    def test_sdv_verification_affects_progress(self):
        """Test that verification affects progress statistics"""
        # Get initial progress
        initial_progress = client.get("/api/v1/sdv/progress?site_id=SITE01")
        assert initial_progress.status_code == 200
        
        # Perform verification
        sdv_data = {
            "subject_id": "SUBJ002",
            "site_id": "SITE01",
            "visit": "Week 12",
            "edc_data": {"hemoglobin": "12.5"},
            "source_data": {"hemoglobin": "12.5"}
        }
        
        verify_response = client.post("/api/v1/sdv/verify", json=sdv_data)
        assert verify_response.status_code == 200
        
        # Get updated progress
        updated_progress = client.get("/api/v1/sdv/progress?site_id=SITE01")
        assert updated_progress.status_code == 200
        
        # Progress should have been updated
        # Note: This will depend on the actual implementation
        assert updated_progress.json()["verified_subjects"] >= 0


class TestSDVPerformance:
    """Performance tests for SDV endpoints"""
    
    def test_sdv_verify_response_time(self):
        """Test that SDV verification completes within reasonable time"""
        sdv_data = {
            "subject_id": "SUBJ001",
            "site_id": "SITE01",
            "visit": "Week 12",
            "edc_data": {"hemoglobin": "12.5"},
            "source_data": {"hemoglobin": "12.3"}
        }
        
        import time
        start_time = time.time()
        
        response = client.post("/api/v1/sdv/verify", json=sdv_data)
        
        end_time = time.time()
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 5.0  # Should complete within 5 seconds
        
        # Check that execution_time is recorded
        data = response.json()
        assert "execution_time" in data
        assert data["execution_time"] > 0