"""
Test suite for query management endpoints.
Following TDD: These tests should FAIL initially, then we implement to make them pass.
"""

import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

from app.main import app
from app.api.models.structured_responses import (
    QueryAnalyzerResponse,
    QueryStatistics,
    BatchQueryResponse,
    SeverityLevel,
    QueryStatus
)


client = TestClient(app)


class TestQueryAnalyzeEndpoint:
    """Test /api/v1/queries/analyze endpoint"""
    
    def test_analyze_query_endpoint_exists(self):
        """Test that the analyze query endpoint exists"""
        response = client.post("/api/v1/queries/analyze", json={
            "subject_id": "SUBJ001",
            "site_id": "SITE01",
            "visit": "Week 12",
            "field_name": "hemoglobin",
            "field_value": "8.5",
            "form_name": "Laboratory Results"
        })
        # Should not be 404 (endpoint exists)
        assert response.status_code != 404
    
    def test_analyze_query_with_valid_input(self):
        """Test analyzing query with valid input"""
        query_data = {
            "subject_id": "SUBJ001",
            "site_id": "SITE01",
            "visit": "Week 12",
            "field_name": "hemoglobin",
            "field_value": "8.5",
            "form_name": "Laboratory Results"
        }
        
        response = client.post("/api/v1/queries/analyze", json=query_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["response_type"] == "clinical_analysis"
        assert "query_id" in data
        assert data["subject"]["id"] == "SUBJ001"
        assert data["clinical_context"]["field"] == "hemoglobin"
        assert data["clinical_context"]["value"] == "8.5"
        assert data["agent_id"] == "query-analyzer"
        assert "execution_time" in data
        assert "confidence_score" in data
        assert "raw_response" in data
    
    def test_analyze_query_with_optional_fields(self):
        """Test analyzing query with optional fields"""
        query_data = {
            "subject_id": "SUBJ001",
            "site_id": "SITE01",
            "visit": "Week 12",
            "field_name": "hemoglobin",
            "field_value": "8.5",
            "expected_value": "12.0",
            "form_name": "Laboratory Results",
            "page_number": 2,
            "context": {
                "initials": "JD",
                "site_name": "Boston General"
            }
        }
        
        response = client.post("/api/v1/queries/analyze", json=query_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["clinical_context"]["expected_value"] == "12.0"
        assert data["clinical_context"]["page_number"] == 2
        assert data["subject"]["initials"] == "JD"
        assert data["subject"]["site"] == "Boston General"
    
    def test_analyze_query_missing_required_fields(self):
        """Test that missing required fields return validation error"""
        query_data = {
            "subject_id": "SUBJ001",
            "site_id": "SITE01",
            # Missing required fields
        }
        
        response = client.post("/api/v1/queries/analyze", json=query_data)
        assert response.status_code == 422  # Validation error
    
    def test_analyze_query_returns_structured_response(self):
        """Test that response follows QueryAnalyzerResponse structure"""
        query_data = {
            "subject_id": "SUBJ001",
            "site_id": "SITE01",
            "visit": "Week 12",
            "field_name": "hemoglobin",
            "field_value": "8.5",
            "form_name": "Laboratory Results"
        }
        
        response = client.post("/api/v1/queries/analyze", json=query_data)
        assert response.status_code == 200
        
        data = response.json()
        
        # Check required fields exist
        required_fields = [
            "success", "response_type", "query_id", "created_date", 
            "status", "severity", "category", "subject", "clinical_context",
            "clinical_findings", "ai_analysis", "agent_id", "execution_time",
            "confidence_score", "raw_response"
        ]
        
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
        
        # Check nested structures
        assert "id" in data["subject"]
        assert "site" in data["subject"]
        assert "visit" in data["clinical_context"]
        assert "field" in data["clinical_context"]
        assert len(data["clinical_findings"]) > 0
        assert "interpretation" in data["ai_analysis"]
        assert "suggested_query" in data["ai_analysis"]
        assert "recommendations" in data["ai_analysis"]
    
    def test_analyze_query_severity_classification(self):
        """Test that queries are properly classified by severity"""
        # Test critical lab value
        query_data = {
            "subject_id": "SUBJ001",
            "site_id": "SITE01",
            "visit": "Week 12",
            "field_name": "hemoglobin",
            "field_value": "6.0",  # Very low, should be critical
            "form_name": "Laboratory Results"
        }
        
        response = client.post("/api/v1/queries/analyze", json=query_data)
        assert response.status_code == 200
        
        data = response.json()
        # Should classify as critical or major
        assert data["severity"] in ["critical", "major"]
        
        # Check that clinical findings reflect severity
        assert len(data["clinical_findings"]) > 0
        assert data["clinical_findings"][0]["severity"] in ["critical", "major"]


class TestQueryListEndpoint:
    """Test /api/v1/queries/ endpoint"""
    
    def test_list_queries_endpoint_exists(self):
        """Test that the list queries endpoint exists"""
        response = client.get("/api/v1/queries/")
        assert response.status_code != 404
    
    def test_list_queries_default_pagination(self):
        """Test listing queries with default pagination"""
        response = client.get("/api/v1/queries/")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        # Should return some queries (mock data)
        assert len(data) > 0
        
        # Check that each query has required structure
        for query in data:
            assert "query_id" in query
            assert "status" in query
            assert "severity" in query
            assert "subject" in query
            assert "clinical_context" in query
    
    def test_list_queries_with_pagination(self):
        """Test listing queries with custom pagination"""
        response = client.get("/api/v1/queries/?skip=0&limit=5")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 5
    
    def test_list_queries_pagination_validation(self):
        """Test that pagination parameters are validated"""
        # Test negative skip
        response = client.get("/api/v1/queries/?skip=-1")
        assert response.status_code == 422
        
        # Test limit too large
        response = client.get("/api/v1/queries/?limit=2000")
        assert response.status_code == 422
        
        # Test zero limit
        response = client.get("/api/v1/queries/?limit=0")
        assert response.status_code == 422
    
    def test_list_queries_with_filters(self):
        """Test listing queries with filters"""
        # TODO: Implement when filters are added
        pass


class TestQueryDetailEndpoint:
    """Test /api/v1/queries/{query_id} endpoint"""
    
    def test_get_query_detail_endpoint_exists(self):
        """Test that the query detail endpoint exists"""
        response = client.get("/api/v1/queries/Q-2025-001")
        assert response.status_code != 404
    
    def test_get_query_detail_with_valid_id(self):
        """Test getting query details with valid ID"""
        query_id = "Q-2025-001"
        response = client.get(f"/api/v1/queries/{query_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["query_id"] == query_id
        assert "subject" in data
        assert "clinical_context" in data
        assert "clinical_findings" in data
        assert "ai_analysis" in data
    
    def test_get_query_detail_with_invalid_id(self):
        """Test getting query details with invalid ID"""
        # TODO: Implement proper error handling
        pass


class TestQueryResolutionEndpoint:
    """Test /api/v1/queries/{query_id}/resolve endpoint"""
    
    def test_resolve_query_endpoint_exists(self):
        """Test that the resolve query endpoint exists"""
        resolution_data = {
            "query_id": "Q-2025-001",
            "resolution": "Confirmed lab value with source documents",
            "resolved_by": "Dr. Smith"
        }
        
        response = client.post("/api/v1/queries/Q-2025-001/resolve", json=resolution_data)
        assert response.status_code != 404
    
    def test_resolve_query_with_valid_data(self):
        """Test resolving query with valid data"""
        query_id = "Q-2025-001"
        resolution_data = {
            "query_id": query_id,
            "resolution": "Confirmed lab value with source documents",
            "resolved_by": "Dr. Smith",
            "comments": "Transcription error corrected"
        }
        
        response = client.post(f"/api/v1/queries/{query_id}/resolve", json=resolution_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["query_id"] == query_id
        assert data["status"] == "resolved"
        assert data["resolved_by"] == "Dr. Smith"
        assert data["resolution"] == "Confirmed lab value with source documents"
        assert data["comments"] == "Transcription error corrected"
    
    def test_resolve_query_missing_required_fields(self):
        """Test that missing required fields return validation error"""
        query_id = "Q-2025-001"
        resolution_data = {
            "query_id": query_id,
            # Missing required fields
        }
        
        response = client.post(f"/api/v1/queries/{query_id}/resolve", json=resolution_data)
        assert response.status_code == 422


class TestQueryStatisticsEndpoint:
    """Test /api/v1/queries/stats/dashboard endpoint"""
    
    def test_query_stats_endpoint_exists(self):
        """Test that the query statistics endpoint exists"""
        response = client.get("/api/v1/queries/stats/dashboard")
        assert response.status_code != 404
    
    def test_query_stats_returns_valid_structure(self):
        """Test that statistics endpoint returns valid structure"""
        response = client.get("/api/v1/queries/stats/dashboard")
        assert response.status_code == 200
        
        data = response.json()
        
        # Check required fields
        required_fields = [
            "total_queries", "open_queries", "critical_queries", 
            "major_queries", "minor_queries", "resolved_today",
            "resolved_this_week", "average_resolution_time",
            "queries_by_site", "queries_by_category", "trend_data"
        ]
        
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
        
        # Check data types
        assert isinstance(data["total_queries"], int)
        assert isinstance(data["open_queries"], int)
        assert isinstance(data["average_resolution_time"], (int, float))
        assert isinstance(data["queries_by_site"], dict)
        assert isinstance(data["queries_by_category"], dict)
        assert isinstance(data["trend_data"], list)
    
    def test_query_stats_data_consistency(self):
        """Test that statistics data is consistent"""
        response = client.get("/api/v1/queries/stats/dashboard")
        assert response.status_code == 200
        
        data = response.json()
        
        # Open queries should be <= total queries
        assert data["open_queries"] <= data["total_queries"]
        
        # Sum of severity levels should be <= open queries
        severity_sum = data["critical_queries"] + data["major_queries"] + data["minor_queries"]
        assert severity_sum <= data["open_queries"]
        
        # Average resolution time should be positive
        assert data["average_resolution_time"] >= 0


class TestBatchQueryEndpoint:
    """Test /api/v1/queries/batch/analyze endpoint"""
    
    def test_batch_analyze_endpoint_exists(self):
        """Test that the batch analyze endpoint exists"""
        batch_data = [
            {
                "subject_id": "SUBJ001",
                "site_id": "SITE01",
                "visit": "Week 12",
                "field_name": "hemoglobin",
                "field_value": "8.5",
                "form_name": "Laboratory Results"
            }
        ]
        
        response = client.post("/api/v1/queries/batch/analyze", json=batch_data)
        assert response.status_code != 404
    
    def test_batch_analyze_with_valid_queries(self):
        """Test batch analyzing with valid queries"""
        batch_data = [
            {
                "subject_id": "SUBJ001",
                "site_id": "SITE01",
                "visit": "Week 12",
                "field_name": "hemoglobin",
                "field_value": "8.5",
                "form_name": "Laboratory Results"
            },
            {
                "subject_id": "SUBJ002",
                "site_id": "SITE01",
                "visit": "Week 8",
                "field_name": "weight",
                "field_value": "75",
                "form_name": "Vital Signs"
            }
        ]
        
        response = client.post("/api/v1/queries/batch/analyze", json=batch_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "success" in data
        assert data["total_queries"] == 2
        assert data["processed"] >= 0
        assert data["failed"] >= 0
        assert data["processed"] + data["failed"] == data["total_queries"]
        assert isinstance(data["results"], list)
        assert isinstance(data["errors"], list)
        assert "execution_time" in data
    
    def test_batch_analyze_with_mixed_valid_invalid(self):
        """Test batch analyzing with mix of valid and invalid queries"""
        batch_data = [
            {
                "subject_id": "SUBJ001",
                "site_id": "SITE01",
                "visit": "Week 12",
                "field_name": "hemoglobin",
                "field_value": "8.5",
                "form_name": "Laboratory Results"
            },
            {
                # Invalid query missing required fields
                "subject_id": "SUBJ002"
            }
        ]
        
        response = client.post("/api/v1/queries/batch/analyze", json=batch_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["total_queries"] == 2
        assert data["processed"] >= 0
        assert data["failed"] >= 0
        assert len(data["errors"]) > 0  # Should have errors for invalid queries
    
    def test_batch_analyze_empty_list(self):
        """Test batch analyzing with empty list"""
        response = client.post("/api/v1/queries/batch/analyze", json=[])
        assert response.status_code == 200
        
        data = response.json()
        assert data["total_queries"] == 0
        assert data["processed"] == 0
        assert data["failed"] == 0
        assert len(data["results"]) == 0
        assert len(data["errors"]) == 0


class TestQueryEndpointIntegration:
    """Integration tests for query endpoints"""
    
    def test_analyze_then_get_query_flow(self):
        """Test the flow of analyzing a query then retrieving it"""
        # First analyze a query
        query_data = {
            "subject_id": "SUBJ001",
            "site_id": "SITE01",
            "visit": "Week 12",
            "field_name": "hemoglobin",
            "field_value": "8.5",
            "form_name": "Laboratory Results"
        }
        
        analyze_response = client.post("/api/v1/queries/analyze", json=query_data)
        assert analyze_response.status_code == 200
        
        analyzed_data = analyze_response.json()
        query_id = analyzed_data["query_id"]
        
        # Then retrieve the query details
        detail_response = client.get(f"/api/v1/queries/{query_id}")
        assert detail_response.status_code == 200
        
        detail_data = detail_response.json()
        assert detail_data["query_id"] == query_id
        assert detail_data["subject"]["id"] == "SUBJ001"
    
    def test_analyze_then_resolve_query_flow(self):
        """Test the flow of analyzing then resolving a query"""
        # First analyze a query
        query_data = {
            "subject_id": "SUBJ001",
            "site_id": "SITE01",
            "visit": "Week 12",
            "field_name": "hemoglobin",
            "field_value": "8.5",
            "form_name": "Laboratory Results"
        }
        
        analyze_response = client.post("/api/v1/queries/analyze", json=query_data)
        assert analyze_response.status_code == 200
        
        analyzed_data = analyze_response.json()
        query_id = analyzed_data["query_id"]
        
        # Then resolve the query
        resolution_data = {
            "query_id": query_id,
            "resolution": "Confirmed with source documents",
            "resolved_by": "Dr. Smith"
        }
        
        resolve_response = client.post(f"/api/v1/queries/{query_id}/resolve", json=resolution_data)
        assert resolve_response.status_code == 200
        
        resolved_data = resolve_response.json()
        assert resolved_data["success"] is True
        assert resolved_data["query_id"] == query_id
        assert resolved_data["status"] == "resolved"


class TestQueryEndpointPerformance:
    """Performance tests for query endpoints"""
    
    def test_analyze_query_response_time(self):
        """Test that query analysis completes within reasonable time"""
        query_data = {
            "subject_id": "SUBJ001",
            "site_id": "SITE01",
            "visit": "Week 12",
            "field_name": "hemoglobin",
            "field_value": "8.5",
            "form_name": "Laboratory Results"
        }
        
        import time
        start_time = time.time()
        
        response = client.post("/api/v1/queries/analyze", json=query_data)
        
        end_time = time.time()
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 5.0  # Should complete within 5 seconds
        
        # Check that execution_time is recorded
        data = response.json()
        assert "execution_time" in data
        assert data["execution_time"] > 0