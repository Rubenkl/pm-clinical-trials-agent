"""
TDD Tests for Data Verifier JSON Output (Task #7)

Tests for updating Data Verifier to output structured JSON with human-readable fields
instead of plain text responses. This aligns with the new architecture where agents
output frontend-compatible JSON responses.

RED Phase: These tests will fail initially and drive the implementation.
"""

import pytest
import json
from datetime import datetime
from typing import Dict, Any

from app.agents.data_verifier import DataVerifier
from app.api.models.structured_responses import DataVerifierResponse, SeverityLevel


class TestDataVerifierJSONOutput:
    """Test Data Verifier outputs structured JSON with human-readable fields"""
    
    @pytest.fixture
    def data_verifier(self):
        """Create Data Verifier instance for testing"""
        return DataVerifier()
    
    @pytest.fixture
    def major_discrepancy_data(self):
        """Sample data with major discrepancies for testing"""
        return {
            "subject_id": "SUBJ001",
            "site_id": "SITE01",
            "visit": "Week 12",
            "edc_data": {
                "hemoglobin": "12.5",
                "systolic_bp": "120",
                "weight": "70.2",
                "adverse_events": "none"
            },
            "source_data": {
                "hemoglobin": "8.5",  # Major discrepancy
                "systolic_bp": "122",  # Minor discrepancy
                "weight": "70.2",     # Exact match
                "adverse_events": "headache reported"  # Missing in EDC
            }
        }
    
    @pytest.fixture
    def minor_discrepancy_data(self):
        """Sample data with minor discrepancies"""
        return {
            "subject_id": "SUBJ002",
            "site_id": "SITE01",
            "visit": "Week 8",
            "edc_data": {
                "glucose": "95",
                "temperature": "36.5",
                "visit_date": "2025-01-15"
            },
            "source_data": {
                "glucose": "96",      # Minor discrepancy within tolerance
                "temperature": "36.6", # Minor discrepancy
                "visit_date": "2025-01-15"  # Exact match
            }
        }
    
    @pytest.fixture
    def perfect_match_data(self):
        """Sample data with perfect matches (no discrepancies)"""
        return {
            "subject_id": "SUBJ003",
            "site_id": "SITE02",
            "visit": "Week 4",
            "edc_data": {
                "hemoglobin": "13.2",
                "glucose": "88",
                "weight": "68.5"
            },
            "source_data": {
                "hemoglobin": "13.2",
                "glucose": "88",
                "weight": "68.5"
            }
        }

    async def test_data_verifier_json_output_structure(self, data_verifier, major_discrepancy_data):
        """Test Data Verifier returns structured JSON matching DataVerifierResponse"""
        # This test will FAIL initially (RED phase)
        result = await data_verifier.verify_clinical_data(major_discrepancy_data)
        
        # Verify top-level JSON structure
        assert isinstance(result, dict)
        assert "success" in result
        assert result["success"] is True
        
        # Core DataVerifierResponse fields
        assert "verification_id" in result
        assert "site" in result
        assert "monitor" in result
        assert "verification_date" in result
        
        # Subject and verification context
        assert "subject" in result
        assert "visit" in result
        
        # Verification results
        assert "match_score" in result
        assert "discrepancies" in result
        assert "progress" in result
        assert "fields_verified" in result
        
        # Human-readable fields for frontend
        assert "human_readable_summary" in result
        assert "verification_summary" in result
        assert "findings_description" in result
        
        # Metadata
        assert "agent_id" in result
        assert result["agent_id"] == "data-verifier"
        assert "execution_time" in result

    async def test_major_discrepancy_detection(self, data_verifier, major_discrepancy_data):
        """Test Data Verifier properly detects and classifies major discrepancies"""
        # This test will FAIL initially (RED phase)
        result = await data_verifier.verify_clinical_data(major_discrepancy_data)
        
        assert result["success"] is True
        
        # Should detect multiple discrepancies
        assert len(result["discrepancies"]) >= 2
        assert result["match_score"] < 0.8  # Low match score due to major discrepancy
        
        # Subject information should be properly structured
        subject = result["subject"]
        assert subject["id"] == "SUBJ001"
        assert subject["site_id"] == "SITE01"
        
        # Should have hemoglobin discrepancy flagged as critical/major
        hemoglobin_discrepancy = next(
            (d for d in result["discrepancies"] if d["field"] == "hemoglobin"), 
            None
        )
        assert hemoglobin_discrepancy is not None
        assert hemoglobin_discrepancy["edc_value"] == "12.5"
        assert hemoglobin_discrepancy["source_value"] == "8.5"
        assert hemoglobin_discrepancy["severity"] in [SeverityLevel.CRITICAL.value, SeverityLevel.MAJOR.value]
        assert hemoglobin_discrepancy["discrepancy_type"] == "value_mismatch"
        
        # Should detect missing adverse event in EDC
        ae_discrepancy = next(
            (d for d in result["discrepancies"] if d["field"] == "adverse_events"), 
            None
        )
        assert ae_discrepancy is not None
        assert ae_discrepancy["discrepancy_type"] == "missing_in_edc"
        
        # Human-readable fields should be meaningful
        assert len(result["human_readable_summary"]) > 30
        assert "discrepancies" in result["human_readable_summary"].lower()
        assert "SUBJ001" in result["human_readable_summary"]
        
        verification_summary = result["verification_summary"]
        assert "hemoglobin" in verification_summary.lower()
        assert any(term in verification_summary.lower() for term in ["mismatch", "discrepancy", "difference"])

    async def test_minor_discrepancy_handling(self, data_verifier, minor_discrepancy_data):
        """Test Data Verifier handles minor discrepancies appropriately"""
        # This test will FAIL initially (RED phase)
        result = await data_verifier.verify_clinical_data(minor_discrepancy_data)
        
        assert result["success"] is True
        
        # Minor discrepancies should result in good match score
        assert result["match_score"] >= 0.8
        
        # Should detect minor discrepancies but classify appropriately
        minor_discrepancies = [d for d in result["discrepancies"] if d["severity"] == SeverityLevel.MINOR.value]
        assert len(minor_discrepancies) >= 1
        
        # Glucose discrepancy should be within tolerance
        glucose_discrepancy = next(
            (d for d in result["discrepancies"] if d["field"] == "glucose"), 
            None
        )
        if glucose_discrepancy:
            assert glucose_discrepancy["severity"] == SeverityLevel.MINOR.value
            assert float(glucose_discrepancy["edc_value"]) - float(glucose_discrepancy["source_value"]) <= 2
        
        # Human-readable summary should reflect minor nature
        summary = result["human_readable_summary"].lower()
        assert any(term in summary for term in ["minor", "acceptable", "within tolerance"])

    async def test_perfect_match_verification(self, data_verifier, perfect_match_data):
        """Test Data Verifier handles perfect matches correctly"""
        # This test will FAIL initially (RED phase)
        result = await data_verifier.verify_clinical_data(perfect_match_data)
        
        assert result["success"] is True
        
        # Perfect matches should have high match score
        assert result["match_score"] >= 0.95
        
        # Should have no or minimal discrepancies
        assert len(result["discrepancies"]) == 0
        
        # Progress should show 100% verification
        progress = result["progress"]
        assert progress["completion_rate"] == 1.0
        assert progress["verified"] == progress["total_fields"]
        assert progress["discrepancies"] == 0
        
        # Human-readable summary should reflect successful verification
        summary = result["human_readable_summary"].lower()
        assert any(term in summary for term in ["complete", "verified", "no discrepancies", "match"])

    async def test_data_verifier_response_validation(self, data_verifier, major_discrepancy_data):
        """Test Data Verifier response can be validated against Pydantic model"""
        # This test will FAIL initially (RED phase)
        result = await data_verifier.verify_clinical_data(major_discrepancy_data)
        
        # Should be able to create DataVerifierResponse from result
        try:
            # Add required fields that might be missing
            if "response_type" not in result:
                result["response_type"] = "data_verification"
            if "verification_date" not in result:
                result["verification_date"] = datetime.now()
            if "monitor" not in result:
                result["monitor"] = "System Monitor"
                
            response = DataVerifierResponse(**result)
            assert response.success is True
            assert response.agent_id == "data-verifier"
            assert response.match_score < 1.0  # Should detect discrepancies
        except Exception as e:
            pytest.fail(f"DataVerifierResponse validation failed: {str(e)}")

    async def test_medical_discrepancy_intelligence(self, data_verifier):
        """Test Data Verifier integrates medical intelligence for clinical discrepancies"""
        medical_discrepancy_data = {
            "subject_id": "SUBJ004",
            "site_id": "SITE01", 
            "visit": "Week 1",
            "edc_data": {
                "hemoglobin": "12.0",
                "systolic_bp": "140",
                "creatinine": "1.2",
                "platelet_count": "200000"
            },
            "source_data": {
                "hemoglobin": "7.5",    # Critical discrepancy
                "systolic_bp": "180",   # Critical discrepancy
                "creatinine": "2.8",    # Critical discrepancy
                "platelet_count": "45000"  # Critical discrepancy
            }
        }
        
        # This test will FAIL initially (RED phase)
        result = await data_verifier.verify_clinical_data(medical_discrepancy_data)
        
        assert result["success"] is True
        assert len(result["discrepancies"]) >= 4
        
        # All should be flagged as critical due to medical significance
        critical_discrepancies = [d for d in result["discrepancies"] if d["severity"] == SeverityLevel.CRITICAL.value]
        assert len(critical_discrepancies) >= 3
        
        # Human-readable fields should include medical context
        findings = result["findings_description"].lower()
        medical_terms = ["anemia", "hypertension", "kidney", "platelet", "bleeding"]
        assert any(term in findings for term in medical_terms)
        
        # Should have very low match score due to critical medical discrepancies
        assert result["match_score"] < 0.5

    async def test_verification_progress_tracking(self, data_verifier):
        """Test Data Verifier tracks verification progress accurately"""
        progress_data = {
            "subject_id": "SUBJ005",
            "site_id": "SITE02",
            "visit": "Week 6",
            "edc_data": {
                "field1": "value1",
                "field2": "value2", 
                "field3": "value3",
                "field4": "value4",
                "field5": "value5"
            },
            "source_data": {
                "field1": "value1",      # Match
                "field2": "different",   # Discrepancy
                "field3": "value3",      # Match
                # field4 missing          # Missing in source
                "field5": "value5"       # Match
            }
        }
        
        # This test will FAIL initially (RED phase)
        result = await data_verifier.verify_clinical_data(progress_data)
        
        progress = result["progress"]
        
        # Should accurately track field counts
        assert progress["total_fields"] == 5
        assert progress["verified"] == 3  # 3 exact matches
        assert progress["discrepancies"] >= 2  # 1 mismatch + 1 missing
        assert progress["completion_rate"] == 0.6  # 3/5 verified
        
        # Should provide time estimates
        if "estimated_time_remaining" in progress:
            assert progress["estimated_time_remaining"] >= 0

    async def test_batch_verification_capability(self, data_verifier):
        """Test Data Verifier can handle batch verification requests"""
        batch_data = [
            {
                "subject_id": "SUBJ006", "site_id": "SITE01", "visit": "Week 1",
                "edc_data": {"hemoglobin": "12.0"}, "source_data": {"hemoglobin": "8.0"}
            },
            {
                "subject_id": "SUBJ007", "site_id": "SITE01", "visit": "Week 1",
                "edc_data": {"glucose": "95"}, "source_data": {"glucose": "95"}
            },
            {
                "subject_id": "SUBJ008", "site_id": "SITE02", "visit": "Week 1",
                "edc_data": {"weight": "70"}, "source_data": {"weight": "71"}
            }
        ]
        
        # This test will FAIL initially (RED phase)
        result = await data_verifier.batch_verify_clinical_data(batch_data)
        
        assert result["success"] is True
        assert "batch_results" in result
        assert len(result["batch_results"]) == 3
        
        # Each result should be properly formatted
        for batch_result in result["batch_results"]:
            assert "verification_id" in batch_result
            assert "match_score" in batch_result
            assert "human_readable_summary" in batch_result
        
        # Should have batch summary
        assert "batch_summary" in result
        summary = result["batch_summary"]
        assert "total_verifications" in summary
        assert "average_match_score" in summary
        assert "critical_discrepancies" in summary

    async def test_human_readable_field_quality(self, data_verifier, major_discrepancy_data):
        """Test quality and usefulness of human-readable fields for frontend display"""
        # This test will FAIL initially (RED phase)
        result = await data_verifier.verify_clinical_data(major_discrepancy_data)
        
        # Human-readable summary quality checks
        summary = result["human_readable_summary"]
        assert len(summary) >= 50  # Substantial content
        assert len(summary) <= 250  # Not too verbose for UI
        assert "SUBJ001" in summary  # Includes subject reference
        
        # Verification summary quality checks
        verification_summary = result["verification_summary"]
        assert len(verification_summary) >= 30
        assert any(word in verification_summary.lower() for word in ["verified", "discrepancy", "mismatch", "reviewed"])
        
        # Findings description quality checks
        findings = result["findings_description"]
        assert len(findings) >= 40
        assert ":" in findings or "." in findings  # Proper sentence structure
        
        # Should include specific field names and values
        assert any(field in findings for field in ["hemoglobin", "adverse_events", "systolic_bp"])

    async def test_confidence_and_match_scoring(self, data_verifier):
        """Test Data Verifier provides accurate match scores and confidence"""
        test_scenarios = [
            {
                "data": {
                    "subject_id": "SUBJ009", "site_id": "SITE01", "visit": "Week 1",
                    "edc_data": {"hemoglobin": "12.0"}, "source_data": {"hemoglobin": "12.0"}
                },
                "expected_match_score": 1.0  # Perfect match
            },
            {
                "data": {
                    "subject_id": "SUBJ010", "site_id": "SITE01", "visit": "Week 1", 
                    "edc_data": {"hemoglobin": "12.0"}, "source_data": {"hemoglobin": "6.0"}
                },
                "expected_match_score": 0.3  # Major discrepancy
            }
        ]
        
        for scenario in test_scenarios:
            # This test will FAIL initially (RED phase)
            result = await data_verifier.verify_clinical_data(scenario["data"])
            
            assert result["success"] is True
            match_score = result["match_score"]
            
            if scenario["expected_match_score"] == 1.0:
                assert match_score >= 0.95  # Perfect or near-perfect match
            else:
                assert match_score <= 0.5   # Poor match due to major discrepancy


class TestDataVerifierIntegration:
    """Test Data Verifier integration with Portfolio Manager and endpoints"""
    
    @pytest.fixture
    def data_verifier(self):
        return DataVerifier()

    async def test_portfolio_manager_integration(self, data_verifier):
        """Test Data Verifier integrates with Portfolio Manager workflow orchestration"""
        from app.agents.portfolio_manager import PortfolioManager
        
        portfolio_manager = PortfolioManager()
        
        verification_request = {
            "workflow_type": "data_verification",
            "input_data": {
                "subject_id": "SUBJ011",
                "site_id": "SITE01",
                "visit": "Week 4",
                "edc_data": {"hemoglobin": "12.0"},
                "source_data": {"hemoglobin": "8.5"}
            },
            "workflow_id": "WF_DV_JSON_001"
        }
        
        # This test will FAIL initially (RED phase)
        result = await portfolio_manager.orchestrate_structured_workflow(verification_request)
        
        assert result["success"] is True
        assert result["workflow_type"] == "data_verification"
        assert result["agent_coordination"]["primary_agent"] == "data_verifier"
        
        # Response data should match DataVerifierResponse structure
        response_data = result["response_data"]
        assert "verification_id" in response_data
        assert "match_score" in response_data
        assert "human_readable_summary" in response_data
        assert "verification_summary" in response_data

    async def test_structured_endpoint_compatibility(self, data_verifier):
        """Test Data Verifier works with structured endpoint format"""
        # Should be compatible with /api/v1/sdv/verify endpoint format
        endpoint_data = {
            "subject_id": "SUBJ012",
            "site_id": "SITE03",
            "visit": "Week 8",
            "verification_session": {
                "monitor_id": "MON001",
                "verification_type": "source_data_verification"
            },
            "data_comparison": {
                "edc_data": {"systolic_bp": "140", "weight": "70.5"},
                "source_data": {"systolic_bp": "185", "weight": "70.5"}
            },
            "verification_options": {
                "tolerance_level": "strict",
                "include_recommendations": True
            }
        }
        
        # This test will FAIL initially (RED phase)
        result = await data_verifier.verify_clinical_data(endpoint_data)
        
        # Should return format compatible with DataVerifierResponse
        assert result["success"] is True
        assert "verification_id" in result
        assert result["subject"]["id"] == "SUBJ012"
        assert result["subject"]["site_id"] == "SITE03"
        
        # Should detect BP discrepancy
        assert result["match_score"] < 0.8
        bp_discrepancy = next(
            (d for d in result["discrepancies"] if "bp" in d["field"].lower()),
            None
        )
        assert bp_discrepancy is not None


class TestDataVerifierPerformance:
    """Test Data Verifier performance with JSON output"""
    
    @pytest.fixture
    def data_verifier(self):
        return DataVerifier()

    async def test_json_output_performance(self, data_verifier):
        """Test Data Verifier JSON output performs efficiently"""
        # This test will FAIL initially (RED phase)
        
        large_dataset = []
        for i in range(15):  # 15 verifications
            large_dataset.append({
                "subject_id": f"SUBJ{i:03d}",
                "site_id": f"SITE{(i % 3) + 1:02d}",
                "visit": "Week 1",
                "edc_data": {"hemoglobin": str(12.0 + (i * 0.1))},
                "source_data": {"hemoglobin": str(12.0 + (i * 0.1) + (0.5 if i % 2 == 0 else 0))}
            })
        
        start_time = datetime.now()
        result = await data_verifier.batch_verify_clinical_data(large_dataset)
        execution_time = (datetime.now() - start_time).total_seconds()
        
        # Should complete efficiently
        assert result["success"] is True
        assert execution_time < 8.0  # Should complete in under 8 seconds
        
        # Should process all verifications
        assert len(result["batch_results"]) == 15
        
        # Should have performance metrics
        assert "execution_time" in result
        assert result["execution_time"] < 8.0

    async def test_json_response_size_optimization(self, data_verifier):
        """Test Data Verifier JSON responses are optimized for frontend transmission"""
        test_data = {
            "subject_id": "SUBJ013",
            "site_id": "SITE01",
            "visit": "Week 1",
            "edc_data": {"hemoglobin": "12.0", "glucose": "95"},
            "source_data": {"hemoglobin": "8.5", "glucose": "96"}
        }
        
        # This test will FAIL initially (RED phase)
        result = await data_verifier.verify_clinical_data(test_data)
        
        # JSON size should be reasonable for network transmission
        json_str = json.dumps(result)
        json_size_kb = len(json_str.encode('utf-8')) / 1024
        
        assert json_size_kb < 40  # Should be under 40KB for efficient transmission
        
        # Human-readable fields should be concise but informative
        assert len(result["human_readable_summary"]) < 300
        assert len(result["verification_summary"]) < 400