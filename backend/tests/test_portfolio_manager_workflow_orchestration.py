"""
TDD Tests for Portfolio Manager Workflow Orchestration (Task #4)

Tests for the new Portfolio Manager architecture that orchestrates structured workflows
and returns JSON responses with human-readable fields for frontend consumption.

RED Phase: These tests will fail initially and drive the implementation.
"""

import pytest
import json
from datetime import datetime
from typing import Dict, Any

from app.agents.portfolio_manager import PortfolioManager, WorkflowRequest
from app.api.models.structured_responses import QueryAnalyzerResponse, DataVerifierResponse


class TestPortfolioManagerWorkflowOrchestration:
    """Test Portfolio Manager's new role as workflow orchestrator"""
    
    @pytest.fixture
    def portfolio_manager(self):
        """Create Portfolio Manager instance for testing"""
        return PortfolioManager()
    
    @pytest.fixture
    def query_workflow_request(self):
        """Sample query analysis workflow request"""
        return {
            "workflow_type": "query_analysis",
            "input_data": {
                "subject_id": "SUBJ001",
                "site_id": "SITE01",
                "visit": "Week 12",
                "field_name": "hemoglobin",
                "field_value": "8.5",
                "form_name": "Laboratory Results"
            },
            "workflow_id": "WF_TEST_001"
        }
    
    @pytest.fixture
    def sdv_workflow_request(self):
        """Sample SDV workflow request"""
        return {
            "workflow_type": "data_verification",
            "input_data": {
                "subject_id": "SUBJ001",
                "site_id": "SITE01",
                "visit": "Week 12",
                "edc_data": {"hemoglobin": "12.5", "bp": "120/80"},
                "source_data": {"hemoglobin": "12.3", "bp": "125/85"}
            },
            "workflow_id": "WF_TEST_002"
        }
    
    @pytest.fixture
    def deviation_workflow_request(self):
        """Sample deviation detection workflow request"""
        return {
            "workflow_type": "deviation_detection",
            "input_data": {
                "subject_id": "SUBJ001",
                "site_id": "SITE01",
                "visit": "Week 12",
                "protocol_data": {"required_visit_window": "±3 days"},
                "actual_data": {"visit_date": "2025-01-15", "scheduled_date": "2025-01-09"}
            },
            "workflow_id": "WF_TEST_003"
        }

    async def test_orchestrate_query_analysis_workflow(self, portfolio_manager, query_workflow_request):
        """Test Portfolio Manager orchestrates query analysis workflow returning structured JSON"""
        # This test will FAIL initially (RED phase)
        result = await portfolio_manager.orchestrate_structured_workflow(query_workflow_request)
        
        # Verify structured response format
        assert result["success"] is True
        assert result["workflow_type"] == "query_analysis"
        assert result["workflow_id"] == "WF_TEST_001"
        
        # Verify JSON response structure matches QueryAnalyzerResponse
        assert "response_data" in result
        response_data = result["response_data"]
        
        # Core QueryAnalyzerResponse fields
        assert "query_id" in response_data
        assert "severity" in response_data
        assert "category" in response_data
        assert "subject" in response_data
        assert "clinical_findings" in response_data
        assert "ai_analysis" in response_data
        
        # Human-readable fields for frontend
        assert "human_readable_summary" in response_data
        assert "clinical_interpretation" in response_data
        assert "recommendation_summary" in response_data
        
        # Verify agent coordination metadata
        assert "agent_coordination" in result
        coordination = result["agent_coordination"]
        assert "primary_agent" in coordination
        assert coordination["primary_agent"] == "query_analyzer"
        assert "agents_involved" in coordination
        assert "query_analyzer" in coordination["agents_involved"]
        
        # Verify execution summary
        assert "execution_summary" in result
        assert "workflow_description" in result

    async def test_orchestrate_sdv_workflow(self, portfolio_manager, sdv_workflow_request):
        """Test Portfolio Manager orchestrates SDV workflow returning structured JSON"""
        # This test will FAIL initially (RED phase)
        result = await portfolio_manager.orchestrate_structured_workflow(sdv_workflow_request)
        
        # Verify structured response format
        assert result["success"] is True
        assert result["workflow_type"] == "data_verification"
        assert result["workflow_id"] == "WF_TEST_002"
        
        # Verify JSON response structure matches DataVerifierResponse
        assert "response_data" in result
        response_data = result["response_data"]
        
        # Core DataVerifierResponse fields
        assert "verification_id" in response_data
        assert "match_score" in response_data
        assert "discrepancies" in response_data
        assert "subject" in response_data
        
        # Human-readable fields for frontend
        assert "human_readable_summary" in response_data
        assert "verification_summary" in response_data
        assert "findings_description" in response_data
        
        # Verify agent coordination
        coordination = result["agent_coordination"]
        assert coordination["primary_agent"] == "data_verifier"
        assert "data_verifier" in coordination["agents_involved"]

    async def test_orchestrate_deviation_detection_workflow(self, portfolio_manager, deviation_workflow_request):
        """Test Portfolio Manager orchestrates deviation detection workflow"""
        # This test will FAIL initially (RED phase) - requires new Deviation Detector agent
        result = await portfolio_manager.orchestrate_structured_workflow(deviation_workflow_request)
        
        # Verify structured response format
        assert result["success"] is True
        assert result["workflow_type"] == "deviation_detection"
        assert result["workflow_id"] == "WF_TEST_003"
        
        # Verify JSON response structure
        assert "response_data" in result
        response_data = result["response_data"]
        
        # Core deviation detection fields
        assert "deviation_id" in response_data
        assert "deviations" in response_data
        assert "total_deviations_found" in response_data
        assert "subject" in response_data
        
        # Human-readable fields for frontend
        assert "human_readable_summary" in response_data
        assert "deviation_summary" in response_data
        assert "compliance_assessment" in response_data
        
        # Verify new Deviation Detector agent coordination
        coordination = result["agent_coordination"]
        assert coordination["primary_agent"] == "deviation_detector"
        assert "deviation_detector" in coordination["agents_involved"]

    async def test_multi_agent_coordination_workflow(self, portfolio_manager, query_workflow_request):
        """Test Portfolio Manager coordinates multiple agents in complex workflow"""
        # Modify request for comprehensive analysis
        query_workflow_request["workflow_type"] = "comprehensive_analysis"
        
        # This test will FAIL initially (RED phase)
        result = await portfolio_manager.orchestrate_structured_workflow(query_workflow_request)
        
        assert result["success"] is True
        assert result["workflow_type"] == "comprehensive_analysis"
        
        # Verify multi-agent coordination
        coordination = result["agent_coordination"]
        agents_involved = coordination["agents_involved"]
        
        # Should involve multiple agents for comprehensive analysis
        assert len(agents_involved) >= 3
        assert "query_analyzer" in agents_involved
        assert "data_verifier" in agents_involved
        assert "query_generator" in agents_involved
        
        # Verify handoff sequence
        assert "agent_handoffs" in coordination
        handoffs = coordination["agent_handoffs"]
        assert len(handoffs) >= 2  # At least 2 handoffs for multi-agent workflow
        
        # Verify each handoff has required fields
        for handoff in handoffs:
            assert "from_agent" in handoff
            assert "to_agent" in handoff
            assert "context_transferred" in handoff
            assert "handoff_reason" in handoff

    async def test_workflow_error_handling(self, portfolio_manager):
        """Test Portfolio Manager handles invalid workflow requests gracefully"""
        invalid_request = {
            "workflow_type": "invalid_workflow",
            "input_data": {},
            "workflow_id": "WF_ERROR_001"
        }
        
        # This test will FAIL initially (RED phase)
        result = await portfolio_manager.orchestrate_structured_workflow(invalid_request)
        
        assert result["success"] is False
        assert "error" in result
        assert "workflow_type" in result["error"]
        assert result["workflow_id"] == "WF_ERROR_001"
        
        # Should still provide human-readable error description
        assert "human_readable_summary" in result
        assert "supported_workflows" in result["error"]

    async def test_workflow_performance_metrics(self, portfolio_manager, query_workflow_request):
        """Test Portfolio Manager provides performance metrics for workflows"""
        # This test will FAIL initially (RED phase)
        result = await portfolio_manager.orchestrate_structured_workflow(query_workflow_request)
        
        assert result["success"] is True
        
        # Verify performance metrics
        assert "performance_metrics" in result
        metrics = result["performance_metrics"]
        
        assert "execution_time" in metrics
        assert "agent_performance" in metrics
        assert "workflow_efficiency" in metrics
        
        # Agent-specific performance
        agent_perf = metrics["agent_performance"]
        for agent_id in result["agent_coordination"]["agents_involved"]:
            assert agent_id in agent_perf
            assert "execution_time" in agent_perf[agent_id]
            assert "success" in agent_perf[agent_id]

    async def test_human_readable_field_generation(self, portfolio_manager, query_workflow_request):
        """Test Portfolio Manager generates human-readable fields for frontend display"""
        # This test will FAIL initially (RED phase)
        result = await portfolio_manager.orchestrate_structured_workflow(query_workflow_request)
        
        assert result["success"] is True
        response_data = result["response_data"]
        
        # Verify human-readable fields are meaningful and descriptive
        assert len(response_data["human_readable_summary"]) > 20
        assert len(response_data["clinical_interpretation"]) > 30
        assert len(response_data["recommendation_summary"]) > 15
        
        # Should contain clinical terminology
        summary = response_data["human_readable_summary"].lower()
        assert any(term in summary for term in ["hemoglobin", "anemia", "critical", "severe", "clinical"])
        
        # Should be suitable for frontend display
        interpretation = response_data["clinical_interpretation"]
        assert "CLINICAL FINDING:" in interpretation
        assert "g/dL" in interpretation or "mmHg" in interpretation  # Units for medical values

    async def test_workflow_state_management(self, portfolio_manager, query_workflow_request):
        """Test Portfolio Manager manages workflow state through multi-agent execution"""
        # This test will FAIL initially (RED phase)
        result = await portfolio_manager.orchestrate_structured_workflow(query_workflow_request)
        
        assert result["success"] is True
        
        # Verify workflow state tracking
        assert "workflow_state" in result
        state = result["workflow_state"]
        
        assert "status" in state
        assert state["status"] in ["completed", "in_progress", "failed"]
        assert "current_step" in state
        assert "total_steps" in state
        assert "started_at" in state
        
        if state["status"] == "completed":
            assert "completed_at" in state
            assert state["current_step"] == state["total_steps"]

    async def test_agent_specialization_routing(self, portfolio_manager):
        """Test Portfolio Manager routes to correct specialized agents based on workflow type"""
        workflows = [
            ("query_analysis", "query_analyzer"),
            ("data_verification", "data_verifier"),  
            ("deviation_detection", "deviation_detector"),
            ("comprehensive_analysis", "query_analyzer")  # Primary agent for complex workflows
        ]
        
        for workflow_type, expected_primary_agent in workflows:
            request = {
                "workflow_type": workflow_type,
                "input_data": {"subject_id": "SUBJ001"},
                "workflow_id": f"WF_{workflow_type.upper()}"
            }
            
            # This test will FAIL initially (RED phase)
            result = await portfolio_manager.orchestrate_structured_workflow(request)
            
            assert result["success"] is True
            coordination = result["agent_coordination"]
            assert coordination["primary_agent"] == expected_primary_agent


class TestPortfolioManagerAgentIntegration:
    """Test Portfolio Manager integration with specialized agents"""
    
    @pytest.fixture
    def portfolio_manager(self):
        return PortfolioManager()

    async def test_query_analyzer_integration(self, portfolio_manager):
        """Test Portfolio Manager properly integrates with Query Analyzer agent"""
        request = {
            "workflow_type": "query_analysis",
            "input_data": {
                "subject_id": "SUBJ001",
                "field_name": "hemoglobin",
                "field_value": "7.5"  # Critical value
            },
            "workflow_id": "WF_QA_001"
        }
        
        # This test will FAIL initially (RED phase)
        result = await portfolio_manager.orchestrate_structured_workflow(request)
        
        assert result["success"] is True
        response_data = result["response_data"]
        
        # Verify Query Analyzer specific output
        assert response_data["severity"] == "critical"  # Should detect critical hemoglobin
        assert response_data["category"] == "laboratory_value"
        
        # Verify medical intelligence in human-readable fields
        clinical_interp = response_data["clinical_interpretation"]
        assert "hemoglobin" in clinical_interp.lower()
        assert "7.5" in clinical_interp
        assert any(term in clinical_interp.lower() for term in ["severe", "critical", "anemia"])

    async def test_data_verifier_integration(self, portfolio_manager):
        """Test Portfolio Manager properly integrates with Data Verifier agent"""
        request = {
            "workflow_type": "data_verification",
            "input_data": {
                "subject_id": "SUBJ001",
                "edc_data": {"hemoglobin": "12.5"},
                "source_data": {"hemoglobin": "8.5"}  # Major discrepancy
            },
            "workflow_id": "WF_DV_001"
        }
        
        # This test will FAIL initially (RED phase)
        result = await portfolio_manager.orchestrate_structured_workflow(request)
        
        assert result["success"] is True
        response_data = result["response_data"]
        
        # Verify Data Verifier specific output
        assert "match_score" in response_data
        assert response_data["match_score"] < 0.8  # Should detect major discrepancy
        assert len(response_data["discrepancies"]) > 0
        
        # Verify first discrepancy has required fields
        discrepancy = response_data["discrepancies"][0]
        assert "field" in discrepancy
        assert "edc_value" in discrepancy
        assert "source_value" in discrepancy
        assert "severity" in discrepancy

    async def test_new_deviation_detector_integration(self, portfolio_manager):
        """Test Portfolio Manager integrates with new Deviation Detector agent (Task #5)"""
        request = {
            "workflow_type": "deviation_detection",
            "input_data": {
                "subject_id": "SUBJ001",
                "protocol_data": {"prohibited_medications": ["aspirin"]},
                "actual_data": {"concomitant_medications": ["aspirin"]}  # Protocol violation
            },
            "workflow_id": "WF_DD_001"
        }
        
        # This test will FAIL initially (RED phase) - requires new Deviation Detector agent
        result = await portfolio_manager.orchestrate_structured_workflow(request)
        
        assert result["success"] is True
        response_data = result["response_data"]
        
        # Verify Deviation Detector specific output
        assert "total_deviations_found" in response_data
        assert response_data["total_deviations_found"] > 0
        assert len(response_data["deviations"]) > 0
        
        # Verify deviation has required fields
        deviation = response_data["deviations"][0]
        assert "category" in deviation
        assert "severity" in deviation
        assert "protocol_requirement" in deviation
        assert "actual_value" in deviation


class TestPortfolioManagerResponseStructure:
    """Test Portfolio Manager returns properly structured responses for frontend"""
    
    @pytest.fixture
    def portfolio_manager(self):
        return PortfolioManager()

    async def test_response_structure_consistency(self, portfolio_manager):
        """Test all workflow types return consistent response structure"""
        workflow_types = ["query_analysis", "data_verification", "deviation_detection"]
        
        for workflow_type in workflow_types:
            request = {
                "workflow_type": workflow_type,
                "input_data": {"subject_id": "SUBJ001"},
                "workflow_id": f"WF_{workflow_type.upper()}"
            }
            
            # This test will FAIL initially (RED phase)
            result = await portfolio_manager.orchestrate_structured_workflow(request)
            
            # All workflows should have consistent top-level structure
            required_fields = [
                "success", "workflow_type", "workflow_id", "response_data",
                "agent_coordination", "execution_summary", "workflow_description",
                "performance_metrics", "workflow_state", "human_readable_summary"
            ]
            
            for field in required_fields:
                assert field in result, f"Missing {field} in {workflow_type} response"

    async def test_frontend_compatibility(self, portfolio_manager):
        """Test responses are optimized for frontend consumption"""
        request = {
            "workflow_type": "query_analysis",
            "input_data": {
                "subject_id": "SUBJ001",
                "field_name": "hemoglobin",
                "field_value": "8.5"
            },
            "workflow_id": "WF_FRONTEND_001"
        }
        
        # This test will FAIL initially (RED phase)
        result = await portfolio_manager.orchestrate_structured_workflow(request)
        
        assert result["success"] is True
        
        # Verify response can be directly consumed by frontend components
        response_data = result["response_data"]
        
        # Check subject data format for frontend tables
        subject = response_data["subject"]
        assert "id" in subject
        assert "site_id" in subject
        
        # Check clinical findings format for frontend display
        if "clinical_findings" in response_data:
            for finding in response_data["clinical_findings"]:
                assert "parameter" in finding
                assert "value" in finding
                assert "severity" in finding
                assert "interpretation" in finding
        
        # Check recommendations format for frontend notifications
        if "ai_analysis" in response_data and "recommendations" in response_data["ai_analysis"]:
            recommendations = response_data["ai_analysis"]["recommendations"]
            assert isinstance(recommendations, list)
            assert all(isinstance(rec, str) for rec in recommendations)