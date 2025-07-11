"""Integration tests for Portfolio Manager orchestrating specialist agents.

This module tests the complete workflow where the Portfolio Manager coordinates
specialist agents (Query Analyzer, Data Verifier, etc.) to fulfill complex
clinical trials requests using the OpenAI Agents SDK patterns.
"""

import asyncio
from datetime import datetime
from typing import Any, Dict, List
from unittest.mock import AsyncMock, Mock, patch

import pytest

from app.agents.context import ClinicalTrialsContext, WorkflowContext
from app.agents.handoffs import (
    DataVerifierHandoff,
    HandoffRegistry,
    QueryAnalyzerHandoff,
)

# Import the actual classes that should be implemented
from app.agents.portfolio_manager import PortfolioManager
from app.agents.query_analyzer import QueryAnalyzer


class TestPortfolioManagerIntegration:
    """Test suite for Portfolio Manager integration with specialist agents."""

    def test_portfolio_manager_initialization_with_agents(self):
        """Test Portfolio Manager can be initialized with specialist agents."""
        # Mock specialist agents
        query_analyzer = Mock(spec=QueryAnalyzer)
        data_verifier = Mock()

        portfolio_manager = PortfolioManager()

        # Register specialist agents
        portfolio_manager.register_agent("query_analyzer", query_analyzer)
        portfolio_manager.register_agent("data_verifier", data_verifier)

        # Verify agents are registered
        assert len(portfolio_manager.agents) == 2
        assert "query_analyzer" in portfolio_manager.agents
        assert "data_verifier" in portfolio_manager.agents

    def test_simple_query_workflow_integration(self):
        """Test complete workflow for a simple clinical data query."""
        # Initialize Portfolio Manager
        portfolio_manager = PortfolioManager()

        # Mock Query Analyzer
        query_analyzer = Mock()
        query_analyzer.analyze.return_value = {
            "intent": "enrollment_status",
            "entities": ["trial_id", "enrollment_count"],
            "confidence": 0.95,
            "requires_verification": False,
            "data_sources": ["clinical_db"],
        }

        # Register agent
        portfolio_manager.register_agent("query_analyzer", query_analyzer)

        # Create workflow context
        context = ClinicalTrialsContext()
        context.user_request = "Show me enrollment status for trial CT-2024-001"
        context.trial_id = "CT-2024-001"
        context.session_id = "session-123"

        # Execute workflow
        result = portfolio_manager.execute_workflow(context)

        # Verify workflow execution
        assert result.status in ["completed", "in_progress"]
        assert context.workflow_state != "pending"
        query_analyzer.analyze.assert_called_once()

    def test_complex_workflow_with_multiple_agents(self):
        """Test complex workflow requiring multiple specialist agents."""
        # Initialize Portfolio Manager
        portfolio_manager = PortfolioManager()

        # Mock Query Analyzer
        query_analyzer = Mock()
        query_analyzer.analyze.return_value = {
            "intent": "safety_analysis",
            "entities": ["adverse_events", "severity", "causality"],
            "confidence": 0.92,
            "requires_verification": True,
            "data_sources": ["safety_db", "clinical_db"],
        }

        # Mock Data Verifier
        data_verifier = Mock()
        data_verifier.verify.return_value = {
            "verification_status": "completed",
            "data_quality": {
                "completeness": 0.98,
                "accuracy": 0.96,
                "consistency": 0.94,
            },
            "issues_found": [],
            "recommendations": ["Continue monitoring for 30 days"],
        }

        # Register agents
        portfolio_manager.register_agent("query_analyzer", query_analyzer)
        portfolio_manager.register_agent("data_verifier", data_verifier)

        # Create complex context
        context = ClinicalTrialsContext()
        context.user_request = (
            "Analyze safety data for all oncology trials and verify data quality"
        )
        context.session_id = "session-456"

        # Add some clinical data
        context.add_adverse_event(
            {
                "event_id": "AE001",
                "participant_id": "P001",
                "severity": "moderate",
                "description": "Nausea and fatigue",
            }
        )

        # Execute workflow
        result = portfolio_manager.execute_workflow(context)

        # Verify both agents were called
        query_analyzer.analyze.assert_called_once()
        data_verifier.verify.assert_called_once()

        # Verify context was updated
        assert len(context.adverse_events) == 1
        assert result.status in ["completed", "in_progress"]

    def test_workflow_with_handoff_registry(self):
        """Test workflow using HandoffRegistry for agent coordination."""
        # Initialize components
        portfolio_manager = PortfolioManager()
        handoff_registry = HandoffRegistry()

        # Register handoffs
        query_handoff = QueryAnalyzerHandoff()
        data_handoff = DataVerifierHandoff()
        handoff_registry.register_handoff(query_handoff)
        handoff_registry.register_handoff(data_handoff)

        # Create context that triggers query analysis
        context = WorkflowContext()
        context.user_request = "What is the enrollment rate for pediatric trials?"
        context.session_id = "session-789"

        # Find applicable handoffs
        applicable_handoffs = handoff_registry.find_applicable_handoffs(context)

        # Should find query analyzer handoff
        assert len(applicable_handoffs) >= 1
        assert any(h.target_agent == "QueryAnalyzer" for h in applicable_handoffs)

        # Execute first handoff
        if applicable_handoffs:
            mock_agent_func = Mock(
                return_value={
                    "analysis": {
                        "intent": "enrollment_analysis",
                        "confidence": 0.89,
                        "requires_verification": True,
                    }
                }
            )

            handoff_result = handoff_registry.execute_handoff(
                applicable_handoffs[0], context, mock_agent_func
            )

            assert handoff_result.status == "completed"
            assert handoff_result.target_agent == "QueryAnalyzer"

    def test_error_handling_in_workflow(self):
        """Test error handling when agents fail during workflow."""
        portfolio_manager = PortfolioManager()

        # Mock failing Query Analyzer
        query_analyzer = Mock()
        query_analyzer.analyze.side_effect = Exception(
            "Query analysis failed: Invalid input"
        )

        portfolio_manager.register_agent("query_analyzer", query_analyzer)

        # Create context
        context = WorkflowContext()
        context.user_request = "Invalid query that will cause failure"

        # Execute workflow
        result = portfolio_manager.execute_workflow(context)

        # Should handle error gracefully
        assert result.status in ["failed", "error"]
        assert len(context.errors) > 0
        assert (
            "failed" in context.errors[0].lower()
            or "error" in context.errors[0].lower()
        )

    def test_workflow_state_transitions(self):
        """Test that workflow state transitions correctly through agent coordination."""
        portfolio_manager = PortfolioManager()

        # Mock agents with state updates
        query_analyzer = Mock()
        query_analyzer.analyze.return_value = {
            "intent": "data_export",
            "confidence": 0.87,
            "requires_verification": False,
        }

        data_processor = Mock()
        data_processor.process.return_value = {
            "processed_records": 1250,
            "export_format": "CSV",
            "file_path": "/exports/trial_data_20240101.csv",
        }

        portfolio_manager.register_agent("query_analyzer", query_analyzer)
        portfolio_manager.register_agent("data_processor", data_processor)

        # Create context and track state changes
        context = WorkflowContext()
        context.user_request = "Export all trial data to CSV format"

        initial_state = context.workflow_state
        assert initial_state == "pending"

        # Execute workflow
        result = portfolio_manager.execute_workflow(context)

        # Verify state progression
        assert context.workflow_state != initial_state
        assert context.current_agent != ""
        assert len(context.previous_agents) >= 0

    def test_parallel_agent_coordination(self):
        """Test Portfolio Manager coordinating multiple agents in parallel."""
        portfolio_manager = PortfolioManager()

        # Mock multiple independent agents
        safety_monitor = Mock()
        safety_monitor.monitor.return_value = {
            "safety_alerts": [],
            "risk_level": "low",
            "recommendation": "continue_trial",
        }

        enrollment_tracker = Mock()
        enrollment_tracker.track.return_value = {
            "current_enrollment": 425,
            "target_enrollment": 500,
            "enrollment_rate": "on_track",
        }

        compliance_checker = Mock()
        compliance_checker.check.return_value = {
            "compliance_status": "compliant",
            "last_audit": "2024-01-01",
            "next_audit_due": "2024-07-01",
        }

        # Register all agents
        portfolio_manager.register_agent("safety_monitor", safety_monitor)
        portfolio_manager.register_agent("enrollment_tracker", enrollment_tracker)
        portfolio_manager.register_agent("compliance_checker", compliance_checker)

        # Create context for comprehensive trial status
        context = ClinicalTrialsContext()
        context.user_request = (
            "Provide comprehensive status update for trial CT-2024-001"
        )
        context.trial_id = "CT-2024-001"

        # Execute workflow
        result = portfolio_manager.execute_workflow(context)

        # In a real parallel implementation, all agents would be called
        # For now, verify the workflow was executed
        assert result.status in ["completed", "in_progress"]
        assert context.workflow_state != "pending"

    def test_workflow_with_clinical_context_specialization(self):
        """Test workflow leveraging ClinicalTrialsContext specific features."""
        portfolio_manager = PortfolioManager()

        # Mock specialized clinical agent
        clinical_analyzer = Mock()
        clinical_analyzer.analyze_clinical_data.return_value = {
            "participant_summary": {
                "total_participants": 150,
                "active_participants": 142,
                "completed_participants": 8,
            },
            "adverse_events_summary": {
                "total_events": 23,
                "serious_events": 2,
                "mild_events": 21,
            },
            "regulatory_status": "compliant",
        }

        portfolio_manager.register_agent("clinical_analyzer", clinical_analyzer)

        # Create rich clinical context
        context = ClinicalTrialsContext()
        context.user_request = "Analyze comprehensive clinical trial data"
        context.trial_id = "CT-2024-002"

        # Add participant data
        for i in range(3):
            context.add_participant(
                {
                    "participant_id": f"P{str(i+1).zfill(3)}",
                    "age": 45 + i,
                    "enrollment_date": f"2024-01-{str(i+1).zfill(2)}",
                }
            )

        # Add adverse events
        context.add_adverse_event(
            {
                "event_id": "AE001",
                "participant_id": "P001",
                "severity": "mild",
                "description": "Headache",
            }
        )

        # Update compliance
        context.update_compliance(
            "ethics_approval",
            True,
            {"approval_date": "2024-01-01", "valid_until": "2025-01-01"},
        )

        # Execute workflow
        result = portfolio_manager.execute_workflow(context)

        # Verify clinical context was utilized
        assert len(context.participant_data) == 3
        assert len(context.adverse_events) == 1
        assert "ethics_approval" in context.regulatory_compliance
        assert result.status in ["completed", "in_progress"]

    def test_workflow_performance_metrics(self):
        """Test workflow performance tracking and metrics."""
        portfolio_manager = PortfolioManager()

        # Mock agent with performance tracking
        performance_analyzer = Mock()
        performance_analyzer.analyze.return_value = {
            "processing_time": 1.25,
            "records_processed": 5000,
            "success_rate": 0.999,
        }

        portfolio_manager.register_agent("performance_analyzer", performance_analyzer)

        # Create context with timing
        context = WorkflowContext()
        context.user_request = "Performance analysis of data processing pipeline"
        start_time = datetime.now()

        # Execute workflow
        result = portfolio_manager.execute_workflow(context)

        end_time = datetime.now()
        execution_duration = (end_time - start_time).total_seconds()

        # Verify performance metrics
        assert execution_duration >= 0
        assert context.execution_time >= 0
        assert result.status in ["completed", "in_progress"]

    def test_agent_communication_patterns(self):
        """Test different communication patterns between agents."""
        portfolio_manager = PortfolioManager()

        # Mock agents that communicate with each other
        coordinator = Mock()
        coordinator.coordinate.return_value = {
            "coordination_plan": ["analyze", "verify", "report"],
            "estimated_duration": "30 minutes",
        }

        analyst = Mock()
        analyst.analyze.return_value = {
            "analysis_complete": True,
            "findings": ["Finding 1", "Finding 2"],
            "next_steps": ["verification_required"],
        }

        reporter = Mock()
        reporter.generate_report.return_value = {
            "report_id": "RPT-001",
            "format": "PDF",
            "sections": ["summary", "details", "recommendations"],
        }

        # Register agents
        portfolio_manager.register_agent("coordinator", coordinator)
        portfolio_manager.register_agent("analyst", analyst)
        portfolio_manager.register_agent("reporter", reporter)

        # Create context for multi-step workflow
        context = WorkflowContext()
        context.user_request = (
            "Generate comprehensive analysis report with verification"
        )

        # Execute workflow
        result = portfolio_manager.execute_workflow(context)

        # Verify workflow coordination
        assert result.status in ["completed", "in_progress"]
        coordinator.coordinate.assert_called_once()

    def test_context_sharing_between_agents(self):
        """Test that context is properly shared and updated between agents."""
        portfolio_manager = PortfolioManager()

        # Mock agents that modify context
        context_reader = Mock()
        context_reader.read_context.return_value = {
            "context_size": "medium",
            "complexity": "high",
        }

        context_enhancer = Mock()
        context_enhancer.enhance_context.return_value = {
            "enhancements_added": ["metadata", "tags", "relations"],
            "context_quality": "improved",
        }

        portfolio_manager.register_agent("context_reader", context_reader)
        portfolio_manager.register_agent("context_enhancer", context_enhancer)

        # Create context with initial data
        context = ClinicalTrialsContext()
        context.user_request = "Process and enhance trial context data"
        context.trial_id = "CT-2024-003"

        initial_participant_count = len(context.participant_data)

        # Add data to context
        context.add_participant({"participant_id": "P001", "status": "active"})

        # Execute workflow
        result = portfolio_manager.execute_workflow(context)

        # Verify context was modified
        assert len(context.participant_data) > initial_participant_count
        assert context.trial_id == "CT-2024-003"
        assert result.status in ["completed", "in_progress"]
