"""Tests for API request/response models and validation."""

import pytest
from pydantic import ValidationError
from datetime import datetime
from typing import Dict, Any, List

from app.api.models.agent_models import (
    ChatRequest, ChatResponse, WorkflowExecutionRequest, WorkflowExecutionResponse,
    AgentStatusResponse, HealthCheckResponse, ErrorResponse
)


class TestChatModels:
    """Test cases for chat-related API models."""

    def test_chat_request_valid(self):
        """Test valid ChatRequest creation."""
        request = ChatRequest(
            message="Analyze clinical trial data for Site 101",
            agent_type="portfolio-manager",
            metadata={
                "user_id": "user123",
                "session_id": "session456",
                "priority": "high"
            }
        )
        
        assert request.message == "Analyze clinical trial data for Site 101"
        assert request.agent_type == "portfolio-manager"
        assert request.metadata["user_id"] == "user123"

    def test_chat_request_defaults(self):
        """Test ChatRequest with default values."""
        request = ChatRequest(message="Test message")
        
        assert request.message == "Test message"
        assert request.agent_type == "portfolio-manager"  # Default
        assert request.metadata == {}

    def test_chat_request_validation_empty_message(self):
        """Test ChatRequest validation with empty message."""
        with pytest.raises(ValidationError) as exc_info:
            ChatRequest(message="")
        
        assert "at least 1 character" in str(exc_info.value)

    def test_chat_request_validation_long_message(self):
        """Test ChatRequest validation with overly long message."""
        long_message = "a" * 10001  # Assuming 10000 char limit
        
        with pytest.raises(ValidationError) as exc_info:
            ChatRequest(message=long_message)
        
        assert "at most" in str(exc_info.value)

    def test_chat_request_invalid_agent_type(self):
        """Test ChatRequest validation with invalid agent type."""
        with pytest.raises(ValidationError) as exc_info:
            ChatRequest(
                message="Test message",
                agent_type="invalid-agent"
            )
        
        assert "Input should be" in str(exc_info.value) or "not a valid enumeration" in str(exc_info.value)

    def test_chat_response_success(self):
        """Test successful ChatResponse creation."""
        response = ChatResponse(
            success=True,
            response="Analysis completed successfully. Found 5 discrepancies.",
            agent_id="portfolio-manager",
            execution_time=3.25,
            metadata={
                "tokens_used": 250,
                "model": "gpt-4",
                "timestamp": "2024-01-15T10:30:00Z"
            }
        )
        
        assert response.success is True
        assert response.response == "Analysis completed successfully. Found 5 discrepancies."
        assert response.agent_id == "portfolio-manager"
        assert response.execution_time == 3.25
        assert response.error is None

    def test_chat_response_failure(self):
        """Test failed ChatResponse creation."""
        response = ChatResponse(
            success=False,
            response="",
            agent_id="portfolio-manager",
            execution_time=0.5,
            error="OpenAI API rate limit exceeded"
        )
        
        assert response.success is False
        assert response.response == ""
        assert response.error == "OpenAI API rate limit exceeded"

    def test_chat_response_validation_negative_execution_time(self):
        """Test ChatResponse validation with negative execution time."""
        with pytest.raises(ValidationError) as exc_info:
            ChatResponse(
                success=True,
                response="Test response",
                agent_id="test-agent",
                execution_time=-1.0
            )
        
        assert "greater than or equal to 0" in str(exc_info.value)


class TestWorkflowModels:
    """Test cases for workflow-related API models."""

    def test_workflow_execution_request_valid(self):
        """Test valid WorkflowExecutionRequest creation."""
        request = WorkflowExecutionRequest(
            workflow_id="WF_2024_001",
            workflow_type="clinical_data_analysis",
            description="Comprehensive analysis of Site 101 clinical trial data",
            input_data={
                "site_id": "101",
                "subjects": ["S001", "S002", "S003"],
                "data_cutoff_date": "2024-01-15",
                "analysis_type": "discrepancy_detection"
            },
            priority=1,
            metadata={
                "requester": "john.doe@clinicaltrials.com",
                "deadline": "2024-01-20T17:00:00Z"
            }
        )
        
        assert request.workflow_id == "WF_2024_001"
        assert request.workflow_type == "clinical_data_analysis"
        assert request.priority == 1
        assert request.input_data["site_id"] == "101"

    def test_workflow_execution_request_defaults(self):
        """Test WorkflowExecutionRequest with default values."""
        request = WorkflowExecutionRequest(
            workflow_id="WF_001",
            workflow_type="clinical_data_analysis",
            description="Test workflow",
            input_data={"test": "data"}
        )
        
        assert request.priority == 1  # Default priority
        assert request.metadata == {}

    def test_workflow_execution_request_validation_priority(self):
        """Test WorkflowExecutionRequest validation with invalid priority."""
        with pytest.raises(ValidationError) as exc_info:
            WorkflowExecutionRequest(
                workflow_id="WF_001",
                workflow_type="test",
                description="Test",
                input_data={},
                priority=0  # Invalid priority (should be >= 1)
            )
        
        assert "greater than or equal to 1" in str(exc_info.value)

    def test_workflow_execution_request_validation_workflow_id(self):
        """Test WorkflowExecutionRequest validation with invalid workflow ID."""
        with pytest.raises(ValidationError) as exc_info:
            WorkflowExecutionRequest(
                workflow_id="",  # Empty workflow ID
                workflow_type="test",
                description="Test",
                input_data={}
            )
        
        assert "at least 1 character" in str(exc_info.value)

    def test_workflow_execution_response_success(self):
        """Test successful WorkflowExecutionResponse creation."""
        response = WorkflowExecutionResponse(
            success=True,
            workflow_id="WF_001",
            tasks_completed=5,
            tasks_failed=0,
            execution_time=45.7,
            results={
                "queries_generated": 15,
                "discrepancies_found": 8,
                "compliance_issues": 2,
                "data_quality_score": 92.5
            },
            metadata={
                "total_subjects_analyzed": 150,
                "completion_timestamp": "2024-01-15T15:30:00Z"
            }
        )
        
        assert response.success is True
        assert response.workflow_id == "WF_001"
        assert response.tasks_completed == 5
        assert response.results["queries_generated"] == 15

    def test_workflow_execution_response_failure(self):
        """Test failed WorkflowExecutionResponse creation."""
        response = WorkflowExecutionResponse(
            success=False,
            workflow_id="WF_002",
            tasks_completed=2,
            tasks_failed=3,
            execution_time=12.3,
            results={},
            error="Agent communication timeout after 300 seconds"
        )
        
        assert response.success is False
        assert response.tasks_failed == 3
        assert response.error == "Agent communication timeout after 300 seconds"


class TestStatusModels:
    """Test cases for status and health check models."""

    def test_agent_status_response_valid(self):
        """Test valid AgentStatusResponse creation."""
        response = AgentStatusResponse(
            agents={
                "portfolio-manager": {
                    "status": "active",
                    "success_rate": 95.5,
                    "average_execution_time": 3.2,
                    "active_workflows": 2,
                    "total_requests": 1250
                },
                "query-analyzer": {
                    "status": "active",
                    "success_rate": 98.1,
                    "average_execution_time": 1.8,
                    "active_workflows": 0,
                    "total_requests": 850
                }
            },
            total_agents=2,
            active_agents=2,
            system_load=65.2,
            uptime_seconds=86400
        )
        
        assert response.total_agents == 2
        assert response.active_agents == 2
        assert response.agents["portfolio-manager"]["status"] == "active"
        assert response.system_load == 65.2

    def test_agent_status_response_with_inactive_agents(self):
        """Test AgentStatusResponse with some inactive agents."""
        response = AgentStatusResponse(
            agents={
                "portfolio-manager": {
                    "status": "active",
                    "success_rate": 95.5
                },
                "query-analyzer": {
                    "status": "inactive",
                    "success_rate": 0.0,
                    "error": "OpenAI API key expired"
                }
            },
            total_agents=2,
            active_agents=1
        )
        
        assert response.total_agents == 2
        assert response.active_agents == 1
        assert response.agents["query-analyzer"]["status"] == "inactive"

    def test_health_check_response_healthy(self):
        """Test healthy HealthCheckResponse creation."""
        response = HealthCheckResponse(
            status="healthy",
            timestamp=datetime.now(),
            version="0.1.0",
            services={
                "database": {
                    "status": "healthy",
                    "response_time": 0.05,
                    "connection_pool": "8/20"
                },
                "redis": {
                    "status": "healthy",
                    "response_time": 0.02,
                    "memory_usage": "45MB"
                },
                "agents": {
                    "status": "healthy",
                    "active_agents": 3,
                    "total_agents": 3
                }
            }
        )
        
        assert response.status == "healthy"
        assert response.version == "0.1.0"
        assert response.services["database"]["status"] == "healthy"

    def test_health_check_response_unhealthy(self):
        """Test unhealthy HealthCheckResponse creation."""
        response = HealthCheckResponse(
            status="unhealthy",
            timestamp=datetime.now(),
            version="0.1.0",
            services={
                "database": {
                    "status": "unhealthy",
                    "error": "Connection timeout",
                    "last_successful_connection": "2024-01-15T10:00:00Z"
                },
                "redis": {
                    "status": "healthy",
                    "response_time": 0.02
                },
                "agents": {
                    "status": "degraded",
                    "active_agents": 2,
                    "total_agents": 3,
                    "issues": ["query-analyzer offline"]
                }
            },
            details="Database connection issues affecting system health"
        )
        
        assert response.status == "unhealthy"
        assert response.services["database"]["status"] == "unhealthy"
        assert response.details == "Database connection issues affecting system health"


class TestErrorModels:
    """Test cases for error response models."""

    def test_error_response_basic(self):
        """Test basic ErrorResponse creation."""
        error = ErrorResponse(
            error="Validation failed",
            message="The provided input data is invalid",
            status_code=422
        )
        
        assert error.error == "Validation failed"
        assert error.message == "The provided input data is invalid"
        assert error.status_code == 422

    def test_error_response_with_details(self):
        """Test ErrorResponse with detailed information."""
        error = ErrorResponse(
            error="Agent execution failed",
            message="The portfolio manager encountered an error during workflow execution",
            status_code=500,
            details={
                "agent_id": "portfolio-manager",
                "workflow_id": "WF_001",
                "error_type": "OpenAIAPIError",
                "timestamp": "2024-01-15T12:30:00Z"
            }
        )
        
        assert error.error == "Agent execution failed"
        assert error.details["agent_id"] == "portfolio-manager"
        assert error.details["workflow_id"] == "WF_001"

    def test_error_response_defaults(self):
        """Test ErrorResponse with default values."""
        error = ErrorResponse(
            error="Unknown error",
            message="An unexpected error occurred"
        )
        
        assert error.status_code == 500  # Default
        assert error.details is None


class TestModelSerialization:
    """Test cases for model serialization and deserialization."""

    def test_chat_request_serialization(self):
        """Test ChatRequest serialization to dict."""
        request = ChatRequest(
            message="Test message",
            agent_type="portfolio-manager",
            metadata={"user_id": "123"}
        )
        
        data = request.model_dump()
        assert data["message"] == "Test message"
        assert data["agent_type"] == "portfolio-manager"
        assert data["metadata"]["user_id"] == "123"

    def test_chat_response_serialization(self):
        """Test ChatResponse serialization to dict."""
        response = ChatResponse(
            success=True,
            response="Test response",
            agent_id="test-agent",
            execution_time=1.5
        )
        
        data = response.model_dump()
        assert data["success"] is True
        assert data["response"] == "Test response"
        assert data["execution_time"] == 1.5

    def test_workflow_request_json_serialization(self):
        """Test WorkflowExecutionRequest JSON serialization."""
        request = WorkflowExecutionRequest(
            workflow_id="WF_001",
            workflow_type="query_generation",
            description="Test workflow",
            input_data={"nested": {"data": "value"}},
            metadata={"key": "value"}
        )
        
        json_str = request.model_dump_json()
        assert "WF_001" in json_str
        assert "nested" in json_str

    def test_model_validation_with_extra_fields(self):
        """Test model validation with extra fields."""
        # Test that extra fields are ignored (if model configured for it)
        with pytest.raises(ValidationError):
            ChatRequest(
                message="Test",
                agent_type="portfolio-manager",
                extra_field="should_be_ignored"  # This should cause validation error
            )


class TestModelEdgeCases:
    """Test cases for edge cases and boundary conditions."""

    def test_very_large_input_data(self):
        """Test workflow request with very large input data."""
        large_data = {f"key_{i}": f"value_{i}" * 100 for i in range(100)}
        
        request = WorkflowExecutionRequest(
            workflow_id="WF_LARGE",
            workflow_type="data_verification",
            description="Test with large data",
            input_data=large_data
        )
        
        assert len(request.input_data) == 100
        assert "key_99" in request.input_data

    def test_unicode_characters_in_message(self):
        """Test handling of unicode characters in messages."""
        request = ChatRequest(
            message="Analyze data for site München with 中文 characters and émojis 🧬",
            agent_type="portfolio-manager"
        )
        
        assert "München" in request.message
        assert "中文" in request.message
        assert "🧬" in request.message

    def test_null_values_in_optional_fields(self):
        """Test handling of null values in optional fields."""
        response = ChatResponse(
            success=False,
            response="",
            agent_id="test-agent",
            execution_time=0.0,
            error=None,  # Explicitly set to None
            metadata={}
        )
        
        assert response.error is None
        assert response.metadata == {}

    def test_extreme_execution_times(self):
        """Test handling of extreme execution time values."""
        # Very small execution time
        response1 = ChatResponse(
            success=True,
            response="Quick response",
            agent_id="test-agent",
            execution_time=0.001
        )
        assert response1.execution_time == 0.001

        # Very large execution time
        response2 = ChatResponse(
            success=True,
            response="Slow response",
            agent_id="test-agent",
            execution_time=3600.0  # 1 hour
        )
        assert response2.execution_time == 3600.0