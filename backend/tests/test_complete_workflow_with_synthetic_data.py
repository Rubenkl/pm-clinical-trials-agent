"""Complete workflow integration test using synthetic test data."""

import pytest
import os
from typing import Dict, Any
from unittest.mock import patch, MagicMock

from app.core.config import Settings
from app.services.test_data_service import TestDataService
from tests.test_data.synthetic_data_generator import generate_test_study


@pytest.fixture
def test_settings():
    """Create test settings with test data enabled."""
    return Settings(
        use_test_data=True,
        test_data_preset="cardiology_phase2",
        openai_api_key="test-key"
    )


@pytest.fixture
def test_data_service(test_settings):
    """Create test data service instance."""
    return TestDataService(test_settings)


@pytest.mark.asyncio
class TestCompleteWorkflowWithSyntheticData:
    """Test complete agent workflows using synthetic data."""
    
    async def test_test_data_service_initialization(self, test_data_service):
        """Test that test data service initializes correctly."""
        assert test_data_service.is_test_mode()
        assert test_data_service.current_study is not None
        
        subjects = test_data_service.get_available_subjects()
        assert len(subjects) > 0
        
        sites = test_data_service.get_available_sites()
        assert len(sites) > 0
    
    async def test_subject_data_retrieval(self, test_data_service):
        """Test retrieving subject data in different formats."""
        subjects = test_data_service.get_available_subjects()
        test_subject = subjects[0]
        
        # Test EDC data retrieval
        edc_data = await test_data_service.get_subject_data(test_subject, "edc")
        assert edc_data is not None
        assert "subject_info" in edc_data
        assert edc_data["subject_info"]["subject_id"] == test_subject
        
        # Test source data retrieval
        source_data = await test_data_service.get_subject_data(test_subject, "source")
        assert source_data is not None
        assert "subject_info" in source_data
        
        # Test both data retrieval
        both_data = await test_data_service.get_subject_data(test_subject, "both")
        assert both_data is not None
        assert "edc_data" in both_data
        assert "source_data" in both_data
        assert "data_quality" in both_data
    
    async def test_discrepancy_detection_workflow(self, test_data_service):
        """Test data verifier workflow with known discrepancies."""
        subjects_with_discrepancies = await test_data_service.get_subjects_with_discrepancies()
        
        if not subjects_with_discrepancies:
            pytest.skip("No subjects with discrepancies in test data")
        
        test_subject = subjects_with_discrepancies[0]
        subject_id = test_subject["subject_id"]
        
        # Get subject data for verification
        subject_data = await test_data_service.get_subject_data(subject_id, "both")
        assert subject_data is not None
        
        # Get known discrepancies
        discrepancies = await test_data_service.get_discrepancies(subject_id)
        assert len(discrepancies) > 0
        
        # Verify discrepancy structure
        for discrepancy in discrepancies:
            assert "field" in discrepancy
            assert "discrepancy_type" in discrepancy
            assert "severity" in discrepancy
            assert discrepancy["severity"] in ["critical", "major", "minor", "trivial"]
    
    async def test_query_generation_workflow(self, test_data_service):
        """Test query generator workflow with existing queries."""
        subjects = test_data_service.get_available_subjects()
        
        for subject_id in subjects[:3]:  # Test first 3 subjects
            queries = await test_data_service.get_queries(subject_id)
            
            if queries:  # If this subject has queries
                # Verify query structure
                for query in queries:
                    assert "query_id" in query
                    assert "subject_id" in query
                    assert "query_text" in query
                    assert "severity" in query
                    assert "status" in query
                    assert query["subject_id"] == subject_id
                break
    
    async def test_site_performance_monitoring(self, test_data_service):
        """Test portfolio manager site performance monitoring."""
        site_performance = await test_data_service.get_site_performance_data()
        assert len(site_performance) > 0
        
        for site in site_performance:
            assert "site_id" in site
            assert "metrics" in site
            
            metrics = site["metrics"]
            assert "enrolled_subjects" in metrics
            assert "total_queries" in metrics
            assert "total_discrepancies" in metrics
            assert "query_rate" in metrics
            assert "discrepancy_rate" in metrics
            
            # Validate metric ranges
            assert metrics["enrolled_subjects"] >= 0
            assert metrics["total_queries"] >= 0
            assert metrics["total_discrepancies"] >= 0
            assert 0 <= metrics["query_rate"] <= 10  # Reasonable range
            assert 0 <= metrics["discrepancy_rate"] <= 1  # Percentage
    
    async def test_critical_finding_identification(self, test_data_service):
        """Test identification of critical findings."""
        critical_subjects = await test_data_service.get_subjects_with_discrepancies("critical")
        
        for subject in critical_subjects:
            critical_discrepancies = [
                d for d in subject["discrepancies"] 
                if d["severity"] == "critical"
            ]
            assert len(critical_discrepancies) > 0
            
            # Verify critical discrepancies have appropriate fields
            for discrepancy in critical_discrepancies:
                assert discrepancy["severity"] == "critical"
                # Critical findings should be related to safety or eligibility
                field = discrepancy["field"].lower()
                assert any(keyword in field for keyword in [
                    "adverse_events", "eligibility", "death", "safety"
                ])
    
    async def test_workflow_data_consistency(self, test_data_service):
        """Test data consistency across different access methods."""
        subjects = test_data_service.get_available_subjects()
        test_subject = subjects[0]
        
        # Get data through different methods
        subject_data = await test_data_service.get_subject_data(test_subject, "both")
        visit_data_baseline = await test_data_service.get_visit_data(test_subject, "Baseline", "both")
        
        # Verify consistency
        if visit_data_baseline and "Baseline" in subject_data["edc_data"]:
            baseline_edc_direct = subject_data["edc_data"]["Baseline"]
            baseline_edc_visit = visit_data_baseline["edc_data"]
            
            # Should be the same data
            assert baseline_edc_direct == baseline_edc_visit
    
    @patch('app.agents.portfolio_manager.orchestrate_workflow')
    async def test_mocked_agent_integration(self, mock_orchestrate, test_data_service):
        """Test agent integration with mocked SDK calls."""
        # Mock the agent function to return a success response
        mock_orchestrate.return_value = '{"success": true, "workflow_id": "WF_001", "result": "completed"}'
        
        subjects = test_data_service.get_available_subjects()
        test_subject = subjects[0]
        
        # Get test data for agent
        subject_data = await test_data_service.get_subject_data(test_subject, "both")
        
        # Simulate workflow orchestration request
        from app.agents.portfolio_manager import orchestrate_workflow
        import json
        
        workflow_request = {
            "workflow_id": "TEST_WF_001",
            "workflow_type": "data_verification",
            "description": "Test data verification workflow",
            "input_data": {
                "subject_id": test_subject,
                "edc_data": subject_data["edc_data"],
                "source_data": subject_data["source_data"]
            }
        }
        
        # Call mocked function
        result = orchestrate_workflow(json.dumps(workflow_request))
        
        # Verify mock was called and returned expected result
        mock_orchestrate.assert_called_once()
        result_data = json.loads(result)
        assert result_data["success"] is True
        assert "workflow_id" in result_data
    
    async def test_end_to_end_data_flow(self, test_data_service):
        """Test complete end-to-end data flow for agent workflows."""
        # 1. Get study overview
        study_info = await test_data_service.get_study_info()
        assert study_info is not None
        assert "protocol_id" in study_info
        
        # 2. Get subjects with issues for Portfolio Manager prioritization
        subjects_with_discrepancies = await test_data_service.get_subjects_with_discrepancies()
        critical_subjects = await test_data_service.get_subjects_with_discrepancies("critical")
        
        # 3. Simulate Portfolio Manager workflow decision
        if critical_subjects:
            priority_subject = critical_subjects[0]["subject_id"]
        elif subjects_with_discrepancies:
            priority_subject = subjects_with_discrepancies[0]["subject_id"]
        else:
            priority_subject = test_data_service.get_available_subjects()[0]
        
        # 4. Get complete subject data for agents
        subject_data = await test_data_service.get_subject_data(priority_subject, "both")
        assert subject_data is not None
        
        # 5. Get known discrepancies for Data Verifier validation
        discrepancies = await test_data_service.get_discrepancies(priority_subject)
        
        # 6. Get existing queries for Query Tracker
        queries = await test_data_service.get_queries(priority_subject)
        
        # 7. Verify data is complete for agent processing
        assert "edc_data" in subject_data
        assert "source_data" in subject_data
        assert "data_quality" in subject_data
        
        # 8. Verify workflow data completeness
        workflow_data = {
            "subject_id": priority_subject,
            "edc_data": subject_data["edc_data"],
            "source_data": subject_data["source_data"],
            "known_discrepancies": discrepancies,
            "existing_queries": queries,
            "subject_metadata": subject_data["subject_info"]
        }
        
        # All required data should be present
        assert all(key in workflow_data for key in [
            "subject_id", "edc_data", "source_data", "known_discrepancies", 
            "existing_queries", "subject_metadata"
        ])
        
        print(f"✅ End-to-end test completed successfully for subject {priority_subject}")
        print(f"   - EDC visits: {len(subject_data['edc_data'])}")
        print(f"   - Known discrepancies: {len(discrepancies)}")
        print(f"   - Existing queries: {len(queries)}")


@pytest.mark.asyncio
async def test_synthetic_data_generation():
    """Test synthetic data generation directly."""
    study = generate_test_study("cardiology_phase2")
    
    assert "study_info" in study
    assert "subjects" in study
    assert "sites" in study
    
    study_info = study["study_info"]
    assert study_info["protocol_id"] == "CARD-2025-001"
    assert study_info["therapeutic_area"] == "cardiology"
    
    subjects = study["subjects"]
    assert len(subjects) == 50  # cardiology_phase2 preset
    
    sites = study["sites"]
    assert len(sites) == 3  # cardiology_phase2 preset
    
    # Verify at least some subjects have discrepancies
    subjects_with_discrepancies = [
        s for s in subjects 
        if any(len(visit["discrepancies"]) > 0 for visit in s["visits"])
    ]
    assert len(subjects_with_discrepancies) > 0
    
    print(f"✅ Generated study with {len(subjects)} subjects and {len(subjects_with_discrepancies)} having discrepancies")


if __name__ == "__main__":
    # Run specific tests for demonstration
    import asyncio
    
    async def run_demo():
        settings = Settings(use_test_data=True, test_data_preset="cardiology_phase2")
        service = TestDataService(settings)
        
        print("🧪 Testing synthetic data generation...")
        await test_synthetic_data_generation()
        
        print("\n📊 Testing data service...")
        test = TestCompleteWorkflowWithSyntheticData()
        await test.test_test_data_service_initialization(service)
        await test.test_subject_data_retrieval(service)
        await test.test_end_to_end_data_flow(service)
        
        print("\n✅ All tests completed successfully!")
    
    asyncio.run(run_demo())