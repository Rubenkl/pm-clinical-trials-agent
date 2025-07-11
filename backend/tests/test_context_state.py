"""Tests for OpenAI Agents SDK Context-based state management.

This module tests the Context objects that provide shared state between agents
in the multi-agent orchestration system using the OpenAI Agents SDK patterns.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from unittest.mock import Mock

import pytest

# Import the actual Context classes that should be implemented
from app.agents.context import ClinicalTrialsContext, WorkflowContext


class TestWorkflowContext:
    """Test suite for base WorkflowContext functionality."""

    def test_workflow_context_initialization(self):
        """Test WorkflowContext initializes with correct defaults."""
        context = WorkflowContext()

        assert context.user_request == ""
        assert context.session_id == ""
        assert context.user_id is None
        assert context.workflow_state == "pending"
        assert context.current_agent == ""
        assert context.previous_agents == []
        assert context.query_analysis == {}
        assert context.data_verification == {}
        assert context.final_results == {}
        assert context.errors == []
        assert context.warnings == []
        assert isinstance(context.created_at, datetime)
        assert isinstance(context.updated_at, datetime)
        assert context.execution_time == 0.0

    def test_workflow_context_with_values(self):
        """Test WorkflowContext initialization with provided values."""
        context = WorkflowContext(
            user_request="Test request",
            session_id="test-session-123",
            user_id="user-456",
            workflow_state="analyzing",
        )

        assert context.user_request == "Test request"
        assert context.session_id == "test-session-123"
        assert context.user_id == "user-456"
        assert context.workflow_state == "analyzing"

    def test_update_state_tracks_agent_transitions(self):
        """Test that update_state properly tracks agent transitions."""
        context = WorkflowContext()

        # First agent
        context.update_state("analyzing", "QueryAnalyzer")
        assert context.workflow_state == "analyzing"
        assert context.current_agent == "QueryAnalyzer"
        assert context.previous_agents == []

        # Second agent
        context.update_state("verifying", "DataVerifier")
        assert context.workflow_state == "verifying"
        assert context.current_agent == "DataVerifier"
        assert context.previous_agents == ["QueryAnalyzer"]

        # Third agent
        context.update_state("completed", "PortfolioManager")
        assert context.workflow_state == "completed"
        assert context.current_agent == "PortfolioManager"
        assert context.previous_agents == ["QueryAnalyzer", "DataVerifier"]

    def test_update_state_updates_timestamp(self):
        """Test that update_state updates the timestamp."""
        context = WorkflowContext()
        original_time = context.updated_at

        # Small delay to ensure timestamp difference
        import time

        time.sleep(0.001)

        context.update_state("analyzing", "QueryAnalyzer")
        assert context.updated_at > original_time

    def test_add_error_functionality(self):
        """Test error addition and tracking."""
        context = WorkflowContext()

        context.add_error("Test error 1")
        assert len(context.errors) == 1
        assert "Test error 1" in context.errors

        context.add_error("Test error 2")
        assert len(context.errors) == 2
        assert "Test error 2" in context.errors

    def test_add_warning_functionality(self):
        """Test warning addition and tracking."""
        context = WorkflowContext()

        context.add_warning("Test warning 1")
        assert len(context.warnings) == 1
        assert "Test warning 1" in context.warnings

        context.add_warning("Test warning 2")
        assert len(context.warnings) == 2
        assert "Test warning 2" in context.warnings

    def test_is_failed_with_errors(self):
        """Test is_failed returns True when errors exist."""
        context = WorkflowContext()
        assert not context.is_failed()

        context.add_error("Something went wrong")
        assert context.is_failed()

    def test_is_failed_with_failed_state(self):
        """Test is_failed returns True when workflow_state is 'failed'."""
        context = WorkflowContext()
        context.workflow_state = "failed"
        assert context.is_failed()

    def test_is_completed_success(self):
        """Test is_completed returns True for successful completion."""
        context = WorkflowContext()
        context.workflow_state = "completed"
        assert context.is_completed()

    def test_is_completed_with_errors(self):
        """Test is_completed returns False when errors exist."""
        context = WorkflowContext()
        context.workflow_state = "completed"
        context.add_error("Error occurred")
        assert not context.is_completed()

    def test_is_completed_wrong_state(self):
        """Test is_completed returns False for non-completed states."""
        context = WorkflowContext()
        context.workflow_state = "analyzing"
        assert not context.is_completed()


class TestClinicalTrialsContext:
    """Test suite for ClinicalTrialsContext functionality."""

    def test_clinical_trials_context_initialization(self):
        """Test ClinicalTrialsContext initializes with correct defaults."""
        context = ClinicalTrialsContext()

        # Base context fields
        assert context.workflow_state == "pending"
        assert context.errors == []

        # Clinical trials specific fields
        assert context.trial_id is None
        assert context.protocol_data == {}
        assert context.participant_data == []
        assert context.adverse_events == []
        assert context.regulatory_compliance == {}
        assert context.data_quality_scores == {}
        assert context.validation_results == {}

    def test_clinical_trials_context_inheritance(self):
        """Test that ClinicalTrialsContext inherits WorkflowContext methods."""
        context = ClinicalTrialsContext()

        # Test inherited method
        context.update_state("analyzing", "ClinicalAnalyzer")
        assert context.workflow_state == "analyzing"
        assert context.current_agent == "ClinicalAnalyzer"

        # Test inherited error handling
        context.add_error("Clinical data error")
        assert context.is_failed()

    def test_add_participant_functionality(self):
        """Test participant data addition."""
        context = ClinicalTrialsContext()

        participant1 = {
            "participant_id": "P001",
            "age": 45,
            "gender": "F",
            "enrollment_date": "2024-01-15",
        }

        participant2 = {
            "participant_id": "P002",
            "age": 52,
            "gender": "M",
            "enrollment_date": "2024-01-16",
        }

        context.add_participant(participant1)
        assert len(context.participant_data) == 1
        assert context.participant_data[0]["participant_id"] == "P001"

        context.add_participant(participant2)
        assert len(context.participant_data) == 2
        assert context.participant_data[1]["participant_id"] == "P002"

    def test_add_adverse_event_functionality(self):
        """Test adverse event data addition."""
        context = ClinicalTrialsContext()

        event1 = {
            "event_id": "AE001",
            "participant_id": "P001",
            "severity": "mild",
            "description": "Mild headache",
            "date": "2024-01-20",
        }

        event2 = {
            "event_id": "AE002",
            "participant_id": "P002",
            "severity": "moderate",
            "description": "Nausea",
            "date": "2024-01-21",
        }

        context.add_adverse_event(event1)
        assert len(context.adverse_events) == 1
        assert context.adverse_events[0]["event_id"] == "AE001"

        context.add_adverse_event(event2)
        assert len(context.adverse_events) == 2
        assert context.adverse_events[1]["severity"] == "moderate"

    def test_update_compliance_functionality(self):
        """Test regulatory compliance update."""
        context = ClinicalTrialsContext()

        compliance_details = {
            "review_date": "2024-01-15",
            "reviewer": "Dr. Smith",
            "notes": "All documentation complete",
        }

        context.update_compliance("FDA_approval", True, compliance_details)

        assert "FDA_approval" in context.regulatory_compliance
        compliance_record = context.regulatory_compliance["FDA_approval"]
        assert compliance_record["status"] is True
        assert compliance_record["details"] == compliance_details
        assert "updated_at" in compliance_record
        assert isinstance(compliance_record["updated_at"], datetime)

    def test_clinical_context_with_values(self):
        """Test ClinicalTrialsContext initialization with provided values."""
        context = ClinicalTrialsContext(
            user_request="Analyze trial CT-2024-001",
            trial_id="CT-2024-001",
            workflow_state="analyzing",
        )

        assert context.user_request == "Analyze trial CT-2024-001"
        assert context.trial_id == "CT-2024-001"
        assert context.workflow_state == "analyzing"


class TestContextIntegration:
    """Test suite for Context integration with agent workflows."""

    def test_context_agent_workflow_simulation(self):
        """Test complete workflow simulation with context state management."""
        context = ClinicalTrialsContext(
            user_request="Analyze safety data for trial CT-2024-001",
            session_id="session-123",
            trial_id="CT-2024-001",
        )

        # Step 1: Portfolio Manager receives request
        context.update_state("analyzing", "PortfolioManager")
        assert context.current_agent == "PortfolioManager"
        assert context.workflow_state == "analyzing"

        # Step 2: Hand off to Query Analyzer
        context.update_state("query_analysis", "QueryAnalyzer")
        context.query_analysis = {
            "intent": "safety_analysis",
            "entities": ["trial_id", "safety_data"],
            "confidence": 0.95,
        }

        # Step 3: Hand off to Data Verifier
        context.update_state("data_verification", "DataVerifier")

        # Add some clinical data
        context.add_participant(
            {"participant_id": "P001", "age": 45, "status": "active"}
        )

        context.add_adverse_event(
            {"event_id": "AE001", "participant_id": "P001", "severity": "mild"}
        )

        # Verify data quality
        context.data_verification = {
            "data_completeness": 0.98,
            "data_accuracy": 0.95,
            "compliance_check": True,
        }

        # Step 4: Complete workflow
        context.update_state("completed", "PortfolioManager")
        context.final_results = {
            "safety_summary": "1 mild adverse event reported",
            "recommendation": "Continue trial with monitoring",
        }

        # Verify final state
        assert context.is_completed()
        assert not context.is_failed()
        assert len(context.previous_agents) == 3
        assert "QueryAnalyzer" in context.previous_agents
        assert "DataVerifier" in context.previous_agents
        assert context.current_agent == "PortfolioManager"

    def test_context_error_handling_workflow(self):
        """Test workflow with error conditions."""
        context = WorkflowContext(
            user_request="Invalid request with missing data",
            session_id="session-error-123",
        )

        # Start workflow
        context.update_state("analyzing", "PortfolioManager")

        # Query analyzer encounters error
        context.update_state("query_analysis", "QueryAnalyzer")
        context.add_error("Unable to parse user request: missing required parameters")

        # Workflow should be marked as failed
        assert context.is_failed()
        assert not context.is_completed()
        assert len(context.errors) == 1

        # Mark workflow as failed
        context.update_state("failed", "QueryAnalyzer")
        assert context.workflow_state == "failed"

    def test_context_warning_handling(self):
        """Test workflow with warnings but successful completion."""
        context = ClinicalTrialsContext(
            user_request="Analyze incomplete trial data", trial_id="CT-2024-002"
        )

        # Add some data with warnings
        context.add_participant({"participant_id": "P001", "age": None})  # Missing age
        context.add_warning("Participant P001 missing age data")

        # Complete workflow despite warnings
        context.update_state("completed", "PortfolioManager")

        assert context.is_completed()  # Can complete with warnings
        assert not context.is_failed()  # Warnings don't fail workflow
        assert len(context.warnings) == 1

    def test_context_timestamp_tracking(self):
        """Test that context properly tracks timestamps."""
        context = WorkflowContext()
        original_time = context.updated_at

        # Small delay to ensure timestamp difference
        import time

        time.sleep(0.001)

        context.update_state("analyzing", "QueryAnalyzer")

        # Verify timestamp was updated (should be later than original)
        assert context.updated_at > original_time

    def test_context_state_transitions(self):
        """Test valid state transitions in workflow context."""
        context = WorkflowContext()

        # Valid state progression (skip initial "pending" since context starts with empty current_agent)
        valid_states = ["analyzing", "verifying", "completed"]

        for i, state in enumerate(valid_states, 1):
            context.update_state(state, f"Agent{i}")
            assert context.workflow_state == state

        # Verify agent progression was tracked (should be 2 transitions for 3 states)
        assert len(context.previous_agents) == len(valid_states) - 1

    def test_context_concurrent_access_simulation(self):
        """Test context behavior under simulated concurrent access."""
        context = ClinicalTrialsContext()

        # Simulate multiple agents updating context
        # (In real implementation, this would need proper locking)

        # Agent 1: Add participant data
        context.add_participant({"participant_id": "P001", "status": "enrolled"})

        # Agent 2: Add adverse event
        context.add_adverse_event({"event_id": "AE001", "participant_id": "P001"})

        # Agent 3: Update compliance
        context.update_compliance("ethics_approval", True, {"date": "2024-01-15"})

        # Verify all updates were applied
        assert len(context.participant_data) == 1
        assert len(context.adverse_events) == 1
        assert "ethics_approval" in context.regulatory_compliance
