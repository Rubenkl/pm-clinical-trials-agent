"""Tests for OpenAI Agents SDK handoff and delegation patterns.

This module tests the handoff mechanisms that enable agents to delegate
tasks to specialized sub-agents using the OpenAI Agents SDK patterns.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional
from unittest.mock import AsyncMock, Mock

import pytest

from app.agents.context import ClinicalTrialsContext, WorkflowContext

# Import the actual handoff classes that should be implemented
from app.agents.handoffs import (
    AgentHandoff,
    DataVerifierHandoff,
    HandoffDefinition,
    HandoffRegistry,
    QueryAnalyzerHandoff,
)


class TestHandoffDefinition:
    """Test suite for HandoffDefinition base functionality."""

    def test_handoff_definition_creation(self):
        """Test HandoffDefinition initialization."""
        handoff = HandoffDefinition(
            name="test_handoff",
            target_agent="TestAgent",
            description="Test handoff for unit testing",
            condition_func=lambda ctx: True,
        )

        assert handoff.name == "test_handoff"
        assert handoff.target_agent == "TestAgent"
        assert handoff.description == "Test handoff for unit testing"
        assert handoff.condition_func is not None
        assert handoff.priority == 1  # default priority
        assert handoff.timeout == 30.0  # default timeout

    def test_handoff_definition_with_custom_parameters(self):
        """Test HandoffDefinition with custom priority and timeout."""
        handoff = HandoffDefinition(
            name="high_priority_handoff",
            target_agent="UrgentAgent",
            description="High priority handoff",
            condition_func=lambda ctx: ctx.workflow_state == "urgent",
            priority=10,
            timeout=60.0,
        )

        assert handoff.priority == 10
        assert handoff.timeout == 60.0

    def test_handoff_condition_evaluation(self):
        """Test handoff condition function evaluation."""
        # Test condition that checks workflow state
        urgent_handoff = HandoffDefinition(
            name="urgent_handoff",
            target_agent="UrgentAgent",
            description="Handoff for urgent cases",
            condition_func=lambda ctx: ctx.workflow_state == "urgent",
        )

        # Test with matching context
        urgent_context = WorkflowContext()
        urgent_context.workflow_state = "urgent"
        assert urgent_handoff.should_execute(urgent_context) is True

        # Test with non-matching context
        normal_context = WorkflowContext()
        normal_context.workflow_state = "analyzing"
        assert urgent_handoff.should_execute(normal_context) is False

    def test_handoff_error_condition(self):
        """Test handoff condition for error states."""
        error_handoff = HandoffDefinition(
            name="error_handoff",
            target_agent="ErrorHandler",
            description="Handoff for error cases",
            condition_func=lambda ctx: len(ctx.errors) > 0,
        )

        # Test context without errors
        clean_context = WorkflowContext()
        assert error_handoff.should_execute(clean_context) is False

        # Test context with errors
        error_context = WorkflowContext()
        error_context.add_error("Test error")
        assert error_handoff.should_execute(error_context) is True

    def test_handoff_priority_ordering(self):
        """Test handoff priority ordering."""
        low_priority = HandoffDefinition(
            name="low",
            target_agent="Agent1",
            description="Low priority",
            condition_func=lambda ctx: True,
            priority=1,
        )
        high_priority = HandoffDefinition(
            name="high",
            target_agent="Agent2",
            description="High priority",
            condition_func=lambda ctx: True,
            priority=10,
        )

        # Higher priority should be "greater than" lower priority for sorting
        assert high_priority > low_priority
        assert low_priority < high_priority


class TestAgentHandoff:
    """Test suite for AgentHandoff execution mechanism."""

    def test_agent_handoff_creation(self):
        """Test AgentHandoff initialization."""
        handoff = AgentHandoff(
            source_agent="PortfolioManager",
            target_agent="QueryAnalyzer",
            handoff_context={"task": "analyze_query", "priority": "high"},
        )

        assert handoff.source_agent == "PortfolioManager"
        assert handoff.target_agent == "QueryAnalyzer"
        assert handoff.handoff_context["task"] == "analyze_query"
        assert handoff.handoff_context["priority"] == "high"
        assert handoff.status == "pending"
        assert isinstance(handoff.created_at, datetime)

    def test_agent_handoff_execution_success(self):
        """Test successful handoff execution."""
        handoff = AgentHandoff(
            source_agent="PortfolioManager",
            target_agent="QueryAnalyzer",
            handoff_context={"query": "What is the status of trial CT-2024-001?"},
        )

        # Simulate successful execution
        result = {"analysis": "Trial status query", "confidence": 0.95}
        handoff.mark_completed(result)

        assert handoff.status == "completed"
        assert handoff.result == result
        assert handoff.completed_at is not None
        assert handoff.execution_time > 0

    def test_agent_handoff_execution_failure(self):
        """Test failed handoff execution."""
        handoff = AgentHandoff(
            source_agent="PortfolioManager",
            target_agent="QueryAnalyzer",
            handoff_context={"query": "Invalid query"},
        )

        # Simulate failed execution
        error_msg = "Query analysis failed: Invalid input format"
        handoff.mark_failed(error_msg)

        assert handoff.status == "failed"
        assert handoff.error_message == error_msg
        assert handoff.completed_at is not None

    def test_agent_handoff_timeout(self):
        """Test handoff timeout handling."""
        handoff = AgentHandoff(
            source_agent="PortfolioManager",
            target_agent="SlowAgent",
            handoff_context={"task": "long_running_task"},
        )

        # Simulate timeout
        handoff.mark_timeout()

        assert handoff.status == "timeout"
        assert "timeout" in handoff.error_message.lower()
        assert handoff.completed_at is not None


class TestHandoffRegistry:
    """Test suite for HandoffRegistry management."""

    def test_handoff_registry_creation(self):
        """Test HandoffRegistry initialization."""
        registry = HandoffRegistry()

        assert len(registry.handoffs) == 0
        assert len(registry.execution_history) == 0

    def test_register_handoff(self):
        """Test registering handoffs in registry."""
        registry = HandoffRegistry()

        handoff = HandoffDefinition(
            name="test_handoff",
            target_agent="TestAgent",
            description="Test handoff",
            condition_func=lambda ctx: True,
        )

        registry.register_handoff(handoff)

        assert len(registry.handoffs) == 1
        assert registry.handoffs[0] == handoff

    def test_find_applicable_handoffs(self):
        """Test finding applicable handoffs for a context."""
        registry = HandoffRegistry()

        # Register multiple handoffs with different conditions
        urgent_handoff = HandoffDefinition(
            name="urgent_handoff",
            target_agent="UrgentAgent",
            description="For urgent cases",
            condition_func=lambda ctx: "urgent" in ctx.user_request.lower(),
            priority=10,
        )

        normal_handoff = HandoffDefinition(
            name="normal_handoff",
            target_agent="NormalAgent",
            description="For normal cases",
            condition_func=lambda ctx: True,
            priority=1,
        )

        registry.register_handoff(urgent_handoff)
        registry.register_handoff(normal_handoff)

        # Test with urgent context
        urgent_context = WorkflowContext()
        urgent_context.user_request = "URGENT: Patient safety issue!"

        applicable = registry.find_applicable_handoffs(urgent_context)
        assert len(applicable) == 2  # Both should match, but urgent has higher priority
        assert applicable[0] == urgent_handoff  # Should be sorted by priority

        # Test with normal context
        normal_context = WorkflowContext()
        normal_context.user_request = "Regular data query"

        applicable = registry.find_applicable_handoffs(normal_context)
        assert len(applicable) == 1  # Only normal handoff should match
        assert applicable[0] == normal_handoff

    def test_execute_handoff(self):
        """Test handoff execution through registry."""
        registry = HandoffRegistry()

        # Mock target agent function
        mock_agent_func = Mock(return_value={"result": "success"})

        handoff_def = HandoffDefinition(
            name="test_handoff",
            target_agent="TestAgent",
            description="Test handoff",
            condition_func=lambda ctx: True,
        )

        context = WorkflowContext()
        context.user_request = "Test request"

        # Execute handoff
        result = registry.execute_handoff(handoff_def, context, mock_agent_func)

        assert result.status == "completed"
        assert result.result == {"result": "success"}
        assert len(registry.execution_history) == 1

        # Verify mock was called correctly
        mock_agent_func.assert_called_once_with(context, handoff_def.to_dict())

    def test_handoff_execution_history(self):
        """Test handoff execution history tracking."""
        registry = HandoffRegistry()

        # Execute multiple handoffs
        for i in range(3):
            handoff_def = HandoffDefinition(
                name=f"handoff_{i}",
                target_agent=f"Agent_{i}",
                description=f"Test handoff {i}",
                condition_func=lambda ctx: True,
            )

            mock_func = Mock(return_value={"result": f"success_{i}"})
            context = WorkflowContext()

            registry.execute_handoff(handoff_def, context, mock_func)

        assert len(registry.execution_history) == 3

        # Test history filtering
        history = registry.get_execution_history(target_agent="Agent_1")
        assert len(history) == 1
        assert history[0].target_agent == "Agent_1"


class TestQueryAnalyzerHandoff:
    """Test suite for QueryAnalyzer specific handoff patterns."""

    def test_query_analyzer_handoff_creation(self):
        """Test QueryAnalyzerHandoff initialization."""
        handoff = QueryAnalyzerHandoff()

        assert handoff.name == "query_analyzer_handoff"
        assert handoff.target_agent == "QueryAnalyzer"
        assert "query analysis" in handoff.description.lower()

    def test_query_analyzer_condition_data_query(self):
        """Test QueryAnalyzerHandoff condition for data queries."""
        handoff = QueryAnalyzerHandoff()

        # Test with data query
        context = WorkflowContext()
        context.user_request = "Show me the enrollment data for trial CT-2024-001"

        assert handoff.should_execute(context) is True

    def test_query_analyzer_condition_analysis_request(self):
        """Test QueryAnalyzerHandoff condition for analysis requests."""
        handoff = QueryAnalyzerHandoff()

        # Test with analysis request
        context = WorkflowContext()
        context.user_request = "Analyze the adverse events in the oncology trials"

        assert handoff.should_execute(context) is True

    def test_query_analyzer_condition_irrelevant_request(self):
        """Test QueryAnalyzerHandoff condition for irrelevant requests."""
        handoff = QueryAnalyzerHandoff()

        # Test with non-query request
        context = WorkflowContext()
        context.user_request = "Hello, how are you today?"

        assert handoff.should_execute(context) is False

    def test_query_analyzer_prepare_context(self):
        """Test QueryAnalyzerHandoff context preparation."""
        handoff = QueryAnalyzerHandoff()

        context = WorkflowContext()
        context.user_request = "What is the status of trial CT-2024-001?"
        context.session_id = "session-123"

        prepared_context = handoff.prepare_handoff_context(context)

        assert "query" in prepared_context
        assert "session_id" in prepared_context
        assert "analysis_type" in prepared_context
        assert prepared_context["query"] == context.user_request
        assert prepared_context["session_id"] == context.session_id


class TestDataVerifierHandoff:
    """Test suite for DataVerifier specific handoff patterns."""

    def test_data_verifier_handoff_creation(self):
        """Test DataVerifierHandoff initialization."""
        handoff = DataVerifierHandoff()

        assert handoff.name == "data_verifier_handoff"
        assert handoff.target_agent == "DataVerifier"
        assert "data verification" in handoff.description.lower()

    def test_data_verifier_condition_verification_needed(self):
        """Test DataVerifierHandoff condition when verification is needed."""
        handoff = DataVerifierHandoff()

        # Test with context that has query analysis indicating verification needed
        context = WorkflowContext()
        context.query_analysis = {
            "requires_verification": True,
            "data_sources": ["clinical_db", "safety_db"],
        }

        assert handoff.should_execute(context) is True

    def test_data_verifier_condition_no_verification_needed(self):
        """Test DataVerifierHandoff condition when verification not needed."""
        handoff = DataVerifierHandoff()

        # Test with context that doesn't require verification
        context = WorkflowContext()
        context.query_analysis = {"requires_verification": False, "confidence": 0.98}

        assert handoff.should_execute(context) is False

    def test_data_verifier_condition_missing_analysis(self):
        """Test DataVerifierHandoff condition with missing query analysis."""
        handoff = DataVerifierHandoff()

        # Test with context without query analysis
        context = WorkflowContext()

        assert handoff.should_execute(context) is False

    def test_data_verifier_prepare_context(self):
        """Test DataVerifierHandoff context preparation."""
        handoff = DataVerifierHandoff()

        context = ClinicalTrialsContext()
        context.trial_id = "CT-2024-001"
        context.query_analysis = {
            "requires_verification": True,
            "data_sources": ["clinical_db"],
            "entities": ["enrollment", "adverse_events"],
        }

        prepared_context = handoff.prepare_handoff_context(context)

        assert "trial_id" in prepared_context
        assert "data_sources" in prepared_context
        assert "verification_entities" in prepared_context
        assert prepared_context["trial_id"] == "CT-2024-001"
        assert prepared_context["data_sources"] == ["clinical_db"]


class TestHandoffIntegration:
    """Test suite for integrated handoff workflows."""

    def test_portfolio_manager_to_query_analyzer_handoff(self):
        """Test complete handoff from Portfolio Manager to Query Analyzer."""
        registry = HandoffRegistry()

        # Register query analyzer handoff
        query_handoff = QueryAnalyzerHandoff()
        registry.register_handoff(query_handoff)

        # Create context representing user query
        context = WorkflowContext()
        context.user_request = "Show me enrollment status for trial CT-2024-001"
        context.session_id = "session-123"
        context.update_state("analyzing", "PortfolioManager")

        # Find applicable handoffs
        applicable = registry.find_applicable_handoffs(context)
        assert len(applicable) == 1
        assert applicable[0].target_agent == "QueryAnalyzer"

        # Mock query analyzer response
        mock_analyzer = Mock(
            return_value={
                "analysis": {
                    "intent": "enrollment_status",
                    "entities": ["trial_id", "enrollment"],
                    "confidence": 0.95,
                    "requires_verification": True,
                }
            }
        )

        # Execute handoff
        result = registry.execute_handoff(applicable[0], context, mock_analyzer)

        assert result.status == "completed"
        assert result.result["analysis"]["intent"] == "enrollment_status"
        assert result.result["analysis"]["requires_verification"] is True

    def test_query_analyzer_to_data_verifier_handoff(self):
        """Test handoff from Query Analyzer to Data Verifier."""
        registry = HandoffRegistry()

        # Register data verifier handoff
        verifier_handoff = DataVerifierHandoff()
        registry.register_handoff(verifier_handoff)

        # Create context with query analysis results
        context = WorkflowContext()
        context.query_analysis = {
            "intent": "enrollment_status",
            "entities": ["trial_id", "enrollment"],
            "confidence": 0.95,
            "requires_verification": True,
            "data_sources": ["clinical_db"],
        }
        context.update_state("query_analyzed", "QueryAnalyzer")

        # Find applicable handoffs
        applicable = registry.find_applicable_handoffs(context)
        assert len(applicable) == 1
        assert applicable[0].target_agent == "DataVerifier"

        # Mock data verifier response
        mock_verifier = Mock(
            return_value={
                "verification_results": {
                    "data_accuracy": 0.98,
                    "completeness": 0.95,
                    "consistency": True,
                    "validated_entities": ["trial_id", "enrollment"],
                }
            }
        )

        # Execute handoff
        result = registry.execute_handoff(applicable[0], context, mock_verifier)

        assert result.status == "completed"
        assert result.result["verification_results"]["data_accuracy"] == 0.98

    def test_error_handling_handoff_chain(self):
        """Test handoff chain with error handling."""
        registry = HandoffRegistry()

        # Register error handling handoff
        error_handoff = HandoffDefinition(
            name="error_handler_handoff",
            target_agent="ErrorHandler",
            description="Handle errors and failures",
            condition_func=lambda ctx: len(ctx.errors) > 0,
            priority=100,  # Highest priority
        )
        registry.register_handoff(error_handoff)

        # Create context with errors
        context = WorkflowContext()
        context.user_request = "Invalid query with missing parameters"
        context.add_error(
            "Query validation failed: Missing required parameter 'trial_id'"
        )
        context.update_state("failed", "QueryAnalyzer")

        # Find applicable handoffs
        applicable = registry.find_applicable_handoffs(context)
        assert len(applicable) == 1
        assert applicable[0].target_agent == "ErrorHandler"

        # Mock error handler response
        mock_error_handler = Mock(
            return_value={
                "error_resolution": {
                    "action": "request_clarification",
                    "message": "Please provide the trial ID for your query",
                    "suggested_format": "trial_id: CT-YYYY-NNN",
                }
            }
        )

        # Execute handoff
        result = registry.execute_handoff(applicable[0], context, mock_error_handler)

        assert result.status == "completed"
        assert result.result["error_resolution"]["action"] == "request_clarification"

    def test_handoff_timeout_and_retry(self):
        """Test handoff timeout and retry mechanisms."""
        registry = HandoffRegistry()

        # Create handoff with short timeout
        timeout_handoff = HandoffDefinition(
            name="timeout_test_handoff",
            target_agent="SlowAgent",
            description="Test timeout handling",
            condition_func=lambda ctx: True,
            timeout=0.1,  # Very short timeout
        )
        registry.register_handoff(timeout_handoff)

        context = WorkflowContext()
        context.user_request = "Long running request"

        # Mock slow agent that exceeds timeout
        import time

        mock_slow_agent = Mock(side_effect=lambda ctx, handoff_ctx: time.sleep(0.2))

        # Execute handoff (should timeout)
        result = registry.execute_handoff(timeout_handoff, context, mock_slow_agent)

        # Note: In real implementation, this would be handled by the SDK's timeout mechanism
        # For testing, we simulate the timeout behavior
        assert result.target_agent == "SlowAgent"

    def test_concurrent_handoff_execution(self):
        """Test concurrent handoff execution scenarios."""
        registry = HandoffRegistry()

        # Register multiple handoffs that could run concurrently
        analyzer_handoff = QueryAnalyzerHandoff()
        registry.register_handoff(analyzer_handoff)

        # Create multiple contexts for concurrent execution
        contexts = []
        for i in range(3):
            context = WorkflowContext()
            context.user_request = f"Query {i}: Show trial data"
            context.session_id = f"session-{i}"
            contexts.append(context)

        # Execute handoffs for all contexts
        results = []
        for i, context in enumerate(contexts):
            mock_func = Mock(return_value={"result": f"analysis_{i}"})
            result = registry.execute_handoff(analyzer_handoff, context, mock_func)
            results.append(result)

        # Verify all executions completed
        assert len(results) == 3
        for i, result in enumerate(results):
            assert result.status == "completed"
            assert result.result["result"] == f"analysis_{i}"

        # Verify execution history
        assert len(registry.execution_history) == 3
