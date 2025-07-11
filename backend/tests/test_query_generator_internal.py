"""
TDD Tests for Query Generator Internal Component (Task #8)

Tests for updating Query Generator to function as an internal workflow component
that integrates with Portfolio Manager orchestration rather than standalone use.
This focuses on internal agent-to-agent communication and workflow integration.

RED Phase: These tests will fail initially and drive the implementation.
"""

import json
from datetime import datetime
from typing import Any, Dict

import pytest

from app.agents.portfolio_manager import PortfolioManager
from app.agents.query_generator import QueryGenerator


class TestQueryGeneratorInternal:
    """Test Query Generator as internal workflow component"""

    @pytest.fixture
    def query_generator(self):
        """Create Query Generator instance for testing"""
        return QueryGenerator()

    @pytest.fixture
    def portfolio_manager(self):
        """Create Portfolio Manager instance for testing"""
        return PortfolioManager()

    @pytest.fixture
    def clinical_analysis_result(self):
        """Sample clinical analysis result from Query Analyzer"""
        return {
            "success": True,
            "response_type": "clinical_analysis",
            "query_id": "Q-20250109-001",
            "severity": "critical",
            "category": "laboratory_value",
            "subject": {"id": "SUBJ001", "site_id": "SITE01"},
            "clinical_findings": [
                {
                    "parameter": "hemoglobin",
                    "value": "8.5 g/dL",
                    "interpretation": "severe anemia",
                    "severity": "critical",
                    "clinical_significance": "high",
                }
            ],
            "ai_analysis": {
                "interpretation": "Critical finding requiring immediate review",
                "clinical_significance": "high",
                "confidence_score": 0.95,
                "suggested_query": "Please explain the hemoglobin value of 8.5 g/dL",
                "recommendations": [
                    "Immediate medical review",
                    "Check for bleeding sources",
                ],
            },
        }

    @pytest.fixture
    def verification_result(self):
        """Sample verification result from Data Verifier"""
        return {
            "success": True,
            "response_type": "data_verification",
            "verification_id": "VER-20250109-001",
            "subject": {"id": "SUBJ001", "site_id": "SITE01"},
            "match_score": 0.65,
            "discrepancies": [
                {
                    "field": "hemoglobin",
                    "edc_value": "12.0",
                    "source_value": "8.5",
                    "severity": "critical",
                    "discrepancy_type": "value_mismatch",
                }
            ],
            "critical_findings": [
                "Critical hemoglobin discrepancy: EDC 12.0 vs Source 8.5"
            ],
        }

    async def test_query_generator_internal_integration(
        self, query_generator, clinical_analysis_result
    ):
        """Test Query Generator integrates with workflow results from other agents"""
        # This test will FAIL initially (RED phase)

        # Query Generator should accept workflow context from other agents
        workflow_context = {
            "workflow_id": "WF_QG_001",
            "workflow_type": "query_generation",
            "input_data": clinical_analysis_result,
            "agent_chain": ["query_analyzer", "query_generator"],
        }

        result = await query_generator.generate_clinical_query(workflow_context)

        assert result["success"] is True
        assert result["workflow_id"] == "WF_QG_001"
        assert "query_text" in result
        assert "query_metadata" in result

        # Should reference the input clinical analysis
        assert (
            clinical_analysis_result["query_id"]
            in result["query_metadata"]["source_analysis_id"]
        )

        # Should generate appropriate query for critical hemoglobin
        query_text = result["query_text"]
        assert "hemoglobin" in query_text.lower()
        assert "8.5" in query_text
        assert any(
            term in query_text.lower() for term in ["severe", "anemia", "critical"]
        )

    async def test_portfolio_manager_query_generator_handoff(
        self, portfolio_manager, clinical_analysis_result
    ):
        """Test Portfolio Manager can orchestrate Query Generator in workflow"""
        # This test will FAIL initially (RED phase)

        workflow_request = {
            "workflow_id": "WF_PM_QG_001",
            "workflow_type": "query_generation",
            "description": "Generate clinical query from analysis results",
            "input_data": clinical_analysis_result,
            "target_agent": "query_generator",
            "orchestration_context": {
                "previous_agent": "query_analyzer",
                "next_agent": "query_tracker",
            },
        }

        result = await portfolio_manager.orchestrate_structured_workflow(
            workflow_request
        )

        assert result["success"] is True
        assert result["workflow_type"] == "query_generation"
        assert result["agent_coordination"]["primary_agent"] == "query_generator"
        assert result["agent_coordination"]["workflow_step"] == "query_generation"

        # Should contain Query Generator response
        response_data = result["response_data"]
        assert "query_text" in response_data
        assert "query_metadata" in response_data
        assert response_data["query_metadata"]["generated_from"] == "clinical_analysis"

    async def test_query_generator_discrepancy_integration(
        self, query_generator, verification_result
    ):
        """Test Query Generator creates queries from verification discrepancies"""
        # This test will FAIL initially (RED phase)

        workflow_context = {
            "workflow_id": "WF_QG_002",
            "workflow_type": "discrepancy_query_generation",
            "input_data": verification_result,
            "agent_chain": ["data_verifier", "query_generator"],
        }

        result = await query_generator.generate_discrepancy_query(workflow_context)

        assert result["success"] is True
        assert result["workflow_id"] == "WF_QG_002"
        assert "query_text" in result

        # Should generate query addressing the discrepancy
        query_text = result["query_text"]
        assert "hemoglobin" in query_text.lower()
        assert "12.0" in query_text and "8.5" in query_text
        assert any(
            term in query_text.lower()
            for term in ["discrepancy", "difference", "mismatch"]
        )

        # Should include severity context
        assert "critical" in query_text.lower() or "urgent" in query_text.lower()

    async def test_query_generator_workflow_chaining(self, query_generator):
        """Test Query Generator can be chained with other agents in workflow"""
        # This test will FAIL initially (RED phase)

        # Multi-step workflow: Analysis -> Verification -> Query Generation
        workflow_context = {
            "workflow_id": "WF_CHAIN_001",
            "workflow_type": "comprehensive_query_workflow",
            "input_data": {
                "analysis_result": {
                    "severity": "major",
                    "clinical_findings": [
                        {"parameter": "glucose", "value": "250 mg/dL"}
                    ],
                },
                "verification_result": {
                    "discrepancies": [{"field": "glucose", "severity": "major"}]
                },
            },
            "agent_chain": [
                "query_analyzer",
                "data_verifier",
                "query_generator",
                "query_tracker",
            ],
        }

        result = await query_generator.process_workflow_chain(workflow_context)

        assert result["success"] is True
        assert result["workflow_step"] == "query_generation"
        assert result["next_agent"] == "query_tracker"

        # Should prepare data for next agent (Query Tracker)
        assert "query_for_tracking" in result
        assert result["query_for_tracking"]["query_id"] is not None
        assert result["query_for_tracking"]["priority"] == "high"  # Major severity

    async def test_query_generator_batch_processing(self, query_generator):
        """Test Query Generator handles batch workflow processing"""
        # This test will FAIL initially (RED phase)

        batch_context = {
            "workflow_id": "WF_BATCH_001",
            "workflow_type": "batch_query_generation",
            "input_data": {
                "batch_size": 5,
                "analysis_results": [
                    {"subject_id": f"SUBJ{i:03d}", "severity": "minor", "findings": []}
                    for i in range(1, 6)
                ],
            },
            "agent_chain": ["query_analyzer", "query_generator"],
        }

        result = await query_generator.process_batch_workflow(batch_context)

        assert result["success"] is True
        assert result["batch_size"] == 5
        assert len(result["generated_queries"]) == 5

        # Should generate queries efficiently
        assert result["processing_time"] < 10.0  # Should be efficient

        # Each query should have proper metadata
        for query in result["generated_queries"]:
            assert "query_id" in query
            assert "subject_id" in query
            assert "query_text" in query

    async def test_query_generator_error_handling(self, query_generator):
        """Test Query Generator handles workflow errors gracefully"""
        # This test will FAIL initially (RED phase)

        # Invalid workflow context
        invalid_context = {
            "workflow_id": "WF_ERROR_001",
            "workflow_type": "invalid_workflow",
            "input_data": None,  # Invalid input
            "agent_chain": ["query_generator"],
        }

        result = await query_generator.handle_workflow_error(invalid_context)

        assert result["success"] is False
        assert "error" in result
        assert result["error_type"] == "workflow_error"
        assert result["recovery_action"] is not None

        # Should provide meaningful error context
        assert "workflow_id" in result
        assert result["workflow_id"] == "WF_ERROR_001"

    async def test_query_generator_template_selection(self, query_generator):
        """Test Query Generator selects appropriate templates for workflow context"""
        # This test will FAIL initially (RED phase)

        # Different workflow types should use different templates
        test_scenarios = [
            {
                "workflow_type": "critical_safety_query",
                "expected_template": "safety_query_template",
                "severity": "critical",
            },
            {
                "workflow_type": "discrepancy_query",
                "expected_template": "discrepancy_query_template",
                "severity": "major",
            },
            {
                "workflow_type": "routine_query",
                "expected_template": "standard_query_template",
                "severity": "minor",
            },
        ]

        for scenario in test_scenarios:
            workflow_context = {
                "workflow_id": f"WF_TEMPLATE_{scenario['workflow_type']}",
                "workflow_type": scenario["workflow_type"],
                "input_data": {"severity": scenario["severity"]},
                "agent_chain": ["query_generator"],
            }

            result = await query_generator.select_query_template(workflow_context)

            assert result["success"] is True
            assert result["template_selected"] == scenario["expected_template"]
            assert result["template_rationale"] is not None

    async def test_query_generator_compliance_integration(self, query_generator):
        """Test Query Generator integrates compliance requirements in workflow"""
        # This test will FAIL initially (RED phase)

        workflow_context = {
            "workflow_id": "WF_COMPLIANCE_001",
            "workflow_type": "regulatory_compliance_query",
            "input_data": {
                "regulation": "ICH-GCP",
                "compliance_context": "serious_adverse_event",
                "severity": "critical",
            },
            "agent_chain": ["query_generator"],
            "compliance_requirements": {
                "regulatory_standard": "ICH-GCP",
                "timeline_requirement": "24_hour_reporting",
                "documentation_level": "full",
            },
        }

        result = await query_generator.generate_compliance_query(workflow_context)

        assert result["success"] is True
        assert result["compliance_validated"] is True
        assert result["regulatory_reference"] == "ICH-GCP"

        # Should include compliance-specific language
        query_text = result["query_text"]
        assert any(
            term in query_text.lower()
            for term in ["regulatory", "compliance", "ich-gcp"]
        )

        # Should include timeline requirements
        assert "24" in query_text or "immediate" in query_text.lower()


class TestQueryTrackerInternal:
    """Test Query Tracker as internal workflow component"""

    @pytest.fixture
    def query_tracker(self):
        """Create Query Tracker instance for testing"""
        return QueryTracker()

    @pytest.fixture
    def portfolio_manager(self):
        """Create Portfolio Manager instance for testing"""
        return PortfolioManager()

    @pytest.fixture
    def generated_query(self):
        """Sample generated query from Query Generator"""
        return {
            "query_id": "Q-20250109-001",
            "subject_id": "SUBJ001",
            "site_id": "SITE01",
            "query_text": "Please explain the hemoglobin value of 8.5 g/dL documented in the source document.",
            "severity": "critical",
            "category": "laboratory_value",
            "generated_date": datetime.now().isoformat(),
            "query_metadata": {
                "generated_from": "clinical_analysis",
                "source_analysis_id": "Q-20250109-001",
            },
        }

    async def test_query_tracker_workflow_integration(
        self, query_tracker, generated_query
    ):
        """Test Query Tracker integrates with workflow results from Query Generator"""
        # This test will FAIL initially (RED phase)

        workflow_context = {
            "workflow_id": "WF_QT_001",
            "workflow_type": "query_tracking",
            "input_data": generated_query,
            "agent_chain": ["query_generator", "query_tracker"],
        }

        result = await query_tracker.track_workflow_query(workflow_context)

        assert result["success"] is True
        assert result["workflow_id"] == "WF_QT_001"
        assert result["query_id"] == generated_query["query_id"]
        assert result["tracking_status"] == "active"

        # Should set up tracking metadata
        assert "tracking_metadata" in result
        assert result["tracking_metadata"]["priority"] == "high"  # Critical severity
        assert result["tracking_metadata"]["sla_deadline"] is not None

    async def test_portfolio_manager_query_tracker_handoff(
        self, portfolio_manager, generated_query
    ):
        """Test Portfolio Manager can orchestrate Query Tracker in workflow"""
        # This test will FAIL initially (RED phase)

        workflow_request = {
            "workflow_id": "WF_PM_QT_001",
            "workflow_type": "query_tracking",
            "description": "Track generated clinical query",
            "input_data": generated_query,
            "target_agent": "query_tracker",
            "orchestration_context": {
                "previous_agent": "query_generator",
                "final_step": True,
            },
        }

        result = await portfolio_manager.orchestrate_structured_workflow(
            workflow_request
        )

        assert result["success"] is True
        assert result["workflow_type"] == "query_tracking"
        assert result["agent_coordination"]["primary_agent"] == "query_tracker"
        assert result["agent_coordination"]["workflow_step"] == "query_tracking"

        # Should contain Query Tracker response
        response_data = result["response_data"]
        assert "query_id" in response_data
        assert "tracking_status" in response_data
        assert response_data["tracking_initiated"] is True

    async def test_query_tracker_sla_workflow(self, query_tracker):
        """Test Query Tracker manages SLA requirements in workflow"""
        # This test will FAIL initially (RED phase)

        workflow_context = {
            "workflow_id": "WF_SLA_001",
            "workflow_type": "sla_management",
            "input_data": {
                "query_id": "Q-20250109-001",
                "severity": "critical",
                "site_id": "SITE01",
                "created_date": datetime.now().isoformat(),
            },
            "agent_chain": ["query_tracker"],
            "sla_requirements": {
                "critical_response_time": "4_hours",
                "escalation_trigger": "2_hours",
                "compliance_standard": "ICH-GCP",
            },
        }

        result = await query_tracker.manage_sla_workflow(workflow_context)

        assert result["success"] is True
        assert result["sla_configured"] is True
        assert result["response_deadline"] is not None
        assert result["escalation_scheduled"] is True

        # Should set appropriate timelines for critical queries
        assert (
            "4" in result["response_deadline"] or "hour" in result["response_deadline"]
        )

    async def test_query_tracker_batch_workflow(self, query_tracker):
        """Test Query Tracker handles batch query tracking in workflow"""
        # This test will FAIL initially (RED phase)

        batch_context = {
            "workflow_id": "WF_BATCH_TRACK_001",
            "workflow_type": "batch_query_tracking",
            "input_data": {
                "batch_size": 10,
                "queries": [
                    {"query_id": f"Q-{i:03d}", "severity": "minor", "site_id": "SITE01"}
                    for i in range(1, 11)
                ],
            },
            "agent_chain": ["query_generator", "query_tracker"],
        }

        result = await query_tracker.process_batch_tracking(batch_context)

        assert result["success"] is True
        assert result["batch_size"] == 10
        assert len(result["tracking_initiated"]) == 10

        # Should set up efficient tracking
        assert result["processing_time"] < 5.0
        assert result["tracking_summary"]["total_queries"] == 10


class TestQueryInternalIntegration:
    """Test integration between Query Generator and Query Tracker"""

    @pytest.fixture
    def query_generator(self):
        return QueryGenerator()

    @pytest.fixture
    def query_tracker(self):
        return QueryTracker()

    @pytest.fixture
    def portfolio_manager(self):
        return PortfolioManager()

    async def test_full_query_workflow_integration(self, portfolio_manager):
        """Test complete workflow: Analysis -> Generator -> Tracker"""
        # This test will FAIL initially (RED phase)

        workflow_request = {
            "workflow_id": "WF_FULL_001",
            "workflow_type": "complete_query_workflow",
            "description": "Full query workflow from analysis to tracking",
            "input_data": {
                "subject_id": "SUBJ001",
                "clinical_data": {"hemoglobin": "8.5", "severity": "critical"},
            },
            "agent_chain": ["query_analyzer", "query_generator", "query_tracker"],
        }

        result = await portfolio_manager.orchestrate_structured_workflow(
            workflow_request
        )

        assert result["success"] is True
        assert result["workflow_type"] == "complete_query_workflow"
        assert len(result["agent_coordination"]["agents_involved"]) == 3

        # Should complete full workflow
        assert result["agent_coordination"]["workflow_completed"] is True
        assert result["response_data"]["query_generated"] is True
        assert result["response_data"]["tracking_initiated"] is True

    async def test_error_recovery_workflow(self, portfolio_manager):
        """Test error recovery in multi-agent query workflow"""
        # This test will FAIL initially (RED phase)

        workflow_request = {
            "workflow_id": "WF_ERROR_RECOVERY_001",
            "workflow_type": "error_recovery_workflow",
            "description": "Test error recovery in query workflow",
            "input_data": {
                "subject_id": "SUBJ001",
                "clinical_data": None,  # This will cause an error
                "force_error": True,
            },
            "agent_chain": ["query_analyzer", "query_generator", "query_tracker"],
        }

        result = await portfolio_manager.orchestrate_structured_workflow(
            workflow_request
        )

        # Should handle error gracefully
        assert result["success"] is False
        assert "error" in result
        assert result["error_recovery"]["attempted"] is True
        assert result["error_recovery"]["recovery_action"] is not None

        # Should identify which agent failed
        assert result["error_recovery"]["failed_agent"] is not None
        assert result["error_recovery"]["workflow_step"] is not None
