"""Tests for Portfolio Manager using OpenAI Agents SDK."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import json
from typing import Dict, List, Any
from datetime import datetime

from app.agents.portfolio_manager_sdk import (
    PortfolioManager,
    WorkflowContext,
    WorkflowStatus,
    orchestrate_query_resolution,
    coordinate_agents,
    track_workflow_progress
)


class TestPortfolioManagerSDK:
    """Test suite for Portfolio Manager with OpenAI Agents SDK."""
    
    @pytest.fixture
    def mock_openai_client(self):
        """Mock OpenAI client for testing."""
        with patch('app.agents.portfolio_manager_sdk.OpenAI') as mock_client:
            # Mock assistant
            mock_assistant = Mock()
            mock_assistant.id = "asst_portfolio123"
            mock_assistant.name = "Clinical Portfolio Manager"
            
            # Mock thread
            mock_thread = Mock()
            mock_thread.id = "thread_portfolio123"
            
            # Mock message for orchestration response
            mock_message = Mock()
            mock_message.content = [Mock(text=Mock(value=json.dumps({
                "workflow_plan": [
                    {"step": 1, "agent": "query_analyzer", "action": "analyze_data"},
                    {"step": 2, "agent": "query_generator", "action": "generate_query"},
                    {"step": 3, "agent": "query_tracker", "action": "track_lifecycle"}
                ],
                "execution_order": ["query_analyzer", "query_generator", "query_tracker"],
                "estimated_time": "3.5 seconds",
                "success_probability": 0.95
            })))]
            
            # Mock run
            mock_run = Mock()
            mock_run.status = "completed"
            mock_run.id = "run_portfolio123"
            
            # Set up client methods
            mock_client.return_value.beta.assistants.create.return_value = mock_assistant
            mock_client.return_value.beta.threads.create.return_value = mock_thread
            mock_client.return_value.beta.threads.messages.create.return_value = Mock()
            mock_client.return_value.beta.threads.runs.create.return_value = mock_run
            mock_client.return_value.beta.threads.runs.retrieve.return_value = mock_run
            mock_client.return_value.beta.threads.messages.list.return_value = Mock(data=[mock_message])
            
            yield mock_client
    
    @pytest.fixture
    def portfolio_manager(self, mock_openai_client):
        """Create PortfolioManager instance with mocked client."""
        return PortfolioManager()
    
    @pytest.fixture
    def sample_workflow_request(self) -> Dict[str, Any]:
        """Sample workflow request for testing."""
        return {
            "workflow_id": "WF_QUERY_RESOLUTION_001",
            "workflow_type": "query_resolution",
            "description": "Process clinical data discrepancy",
            "input_data": {
                "subject_id": "SUBJ001",
                "visit": "Week 4",
                "field_name": "Hemoglobin",
                "edc_value": "12.5",
                "source_value": "11.2",
                "site_name": "Memorial Hospital"
            },
            "priority": "major",
            "user_id": "user123"
        }
    
    def test_portfolio_manager_initialization(self, portfolio_manager):
        """Test PortfolioManager initialization."""
        assert portfolio_manager.agent is not None
        assert portfolio_manager.instructions is not None
        assert portfolio_manager.available_agents is not None
        assert len(portfolio_manager.available_agents) >= 3
        assert portfolio_manager.context is not None
    
    def test_available_agents_registration(self, portfolio_manager):
        """Test that agents are properly registered."""
        agents = portfolio_manager.available_agents
        expected_agents = ["query_analyzer", "query_generator", "query_tracker"]
        
        for agent in expected_agents:
            assert agent in agents
            assert "capabilities" in agents[agent]
            assert "handoff_condition" in agents[agent]
    
    @pytest.mark.asyncio
    async def test_orchestrate_query_resolution(self, portfolio_manager, sample_workflow_request):
        """Test query resolution workflow orchestration."""
        result = await portfolio_manager.orchestrate_workflow(sample_workflow_request)
        
        assert result is not None
        assert "workflow_id" in result
        assert "execution_plan" in result
        assert "status" in result
        assert result["workflow_id"] == sample_workflow_request["workflow_id"]
        assert result["status"] in ["planned", "in_progress", "completed"]
    
    @pytest.mark.asyncio
    async def test_agent_coordination(self, portfolio_manager):
        """Test coordination between multiple agents."""
        agents_to_coordinate = [
            {"agent_id": "query_analyzer", "task": "analyze_discrepancy"},
            {"agent_id": "query_generator", "task": "create_query"},
            {"agent_id": "query_tracker", "task": "monitor_lifecycle"}
        ]
        
        coordination_result = await portfolio_manager.coordinate_agents(agents_to_coordinate)
        
        assert coordination_result["success"] is True
        assert "coordination_plan" in coordination_result
        assert "handoff_sequence" in coordination_result
        assert len(coordination_result["handoff_sequence"]) == 3
    
    @pytest.mark.asyncio
    async def test_workflow_context_management(self, portfolio_manager, sample_workflow_request):
        """Test workflow context creation and management."""
        # Start workflow
        workflow_result = await portfolio_manager.orchestrate_workflow(sample_workflow_request)
        
        # Check context was created
        workflow_id = workflow_result["workflow_id"]
        assert workflow_id in portfolio_manager.context.active_workflows
        
        # Get workflow status
        status = await portfolio_manager.get_workflow_status(workflow_id)
        assert status["workflow_id"] == workflow_id
        assert "current_step" in status
        assert "progress_percentage" in status
    
    @pytest.mark.asyncio
    async def test_parallel_agent_execution(self, portfolio_manager):
        """Test parallel execution of independent agents."""
        parallel_tasks = [
            {"agent": "query_analyzer", "data": {"type": "analysis1"}},
            {"agent": "query_analyzer", "data": {"type": "analysis2"}},
            {"agent": "query_analyzer", "data": {"type": "analysis3"}}
        ]
        
        start_time = datetime.now()
        results = await portfolio_manager.execute_parallel_tasks(parallel_tasks)
        execution_time = (datetime.now() - start_time).total_seconds()
        
        assert len(results) == 3
        assert all(r["success"] for r in results)
        # Parallel execution should be faster than sequential
        assert execution_time < 5.0  # Should complete in reasonable time
    
    @pytest.mark.asyncio
    async def test_workflow_error_handling(self, portfolio_manager):
        """Test error handling in workflow execution."""
        invalid_request = {
            "workflow_id": "WF_INVALID",
            "workflow_type": "invalid_type",
            "input_data": {}  # Missing required data
        }
        
        result = await portfolio_manager.orchestrate_workflow(invalid_request)
        
        assert result["success"] is False
        assert "error" in result
        assert "validation_errors" in result
    
    @pytest.mark.asyncio
    async def test_workflow_progress_tracking(self, portfolio_manager, sample_workflow_request):
        """Test workflow progress tracking and updates."""
        # Start workflow
        workflow = await portfolio_manager.orchestrate_workflow(sample_workflow_request)
        workflow_id = workflow["workflow_id"]
        
        # Update progress
        await portfolio_manager.update_workflow_progress(
            workflow_id,
            step="query_analysis",
            status="completed",
            result={"analysis": "successful"}
        )
        
        # Check progress
        status = await portfolio_manager.get_workflow_status(workflow_id)
        assert status["current_step"] == "query_analysis"
        assert status["last_update"] is not None
        assert status["progress_percentage"] > 0
    
    @pytest.mark.asyncio
    async def test_agent_handoffs(self, portfolio_manager):
        """Test agent handoff mechanisms."""
        handoff_data = {
            "from_agent": "query_analyzer",
            "to_agent": "query_generator", 
            "context": {"analysis_result": "data_discrepancy"},
            "handoff_reason": "analysis_complete"
        }
        
        handoff_result = await portfolio_manager.execute_handoff(handoff_data)
        
        assert handoff_result["success"] is True
        assert handoff_result["from_agent"] == "query_analyzer"
        assert handoff_result["to_agent"] == "query_generator"
        assert "handoff_time" in handoff_result
        assert "context_transferred" in handoff_result
    
    @pytest.mark.asyncio
    async def test_workflow_metrics_collection(self, portfolio_manager, sample_workflow_request):
        """Test collection of workflow performance metrics."""
        # Execute workflow
        workflow = await portfolio_manager.orchestrate_workflow(sample_workflow_request)
        workflow_id = workflow["workflow_id"]
        
        # Simulate workflow completion
        await portfolio_manager.complete_workflow(workflow_id, {"success": True})
        
        # Get metrics
        metrics = await portfolio_manager.get_workflow_metrics(workflow_id)
        
        assert "execution_time" in metrics
        assert "agents_involved" in metrics
        assert "handoffs_count" in metrics
        assert "success_rate" in metrics
        assert metrics["workflow_id"] == workflow_id
    
    @pytest.mark.asyncio
    async def test_workflow_cancellation(self, portfolio_manager, sample_workflow_request):
        """Test workflow cancellation functionality."""
        # Start workflow
        workflow = await portfolio_manager.orchestrate_workflow(sample_workflow_request)
        workflow_id = workflow["workflow_id"]
        
        # Cancel workflow
        cancel_result = await portfolio_manager.cancel_workflow(
            workflow_id,
            reason="User requested cancellation"
        )
        
        assert cancel_result["success"] is True
        assert cancel_result["workflow_id"] == workflow_id
        
        # Check status is cancelled
        status = await portfolio_manager.get_workflow_status(workflow_id)
        assert status["status"] == "cancelled"
    
    def test_workflow_context_class(self):
        """Test WorkflowContext data structure."""
        context = WorkflowContext()
        
        # Test default values
        assert context.active_workflows == {}
        assert context.agent_states == {}
        assert context.workflow_history == []
        
        # Test adding workflow
        workflow_data = {
            "workflow_id": "test123",
            "status": WorkflowStatus.IN_PROGRESS,
            "steps": ["step1", "step2"]
        }
        context.active_workflows["test123"] = workflow_data
        
        assert "test123" in context.active_workflows
        assert context.active_workflows["test123"]["status"] == WorkflowStatus.IN_PROGRESS
    
    def test_workflow_status_enum(self):
        """Test WorkflowStatus enum values."""
        assert WorkflowStatus.PENDING.value == "pending"
        assert WorkflowStatus.IN_PROGRESS.value == "in_progress"
        assert WorkflowStatus.COMPLETED.value == "completed"
        assert WorkflowStatus.FAILED.value == "failed"
        assert WorkflowStatus.CANCELLED.value == "cancelled"
    
    @pytest.mark.asyncio
    async def test_bulk_workflow_execution(self, portfolio_manager):
        """Test execution of multiple workflows simultaneously."""
        workflows = [
            {
                "workflow_id": f"WF_BULK_{i}",
                "workflow_type": "query_resolution",
                "input_data": {"subject_id": f"SUBJ{i:03d}"}
            }
            for i in range(5)
        ]
        
        results = await portfolio_manager.execute_bulk_workflows(workflows)
        
        assert len(results) == 5
        assert all("workflow_id" in r for r in results)
        assert all(r["workflow_id"].startswith("WF_BULK_") for r in results)
    
    @pytest.mark.asyncio
    async def test_agent_health_monitoring(self, portfolio_manager):
        """Test monitoring of agent health and availability."""
        health_status = await portfolio_manager.check_agent_health()
        
        assert "agents" in health_status
        assert "overall_health" in health_status
        assert "last_check" in health_status
        
        # Check individual agent status
        for agent_id, status in health_status["agents"].items():
            assert "status" in status  # healthy, degraded, unavailable
            assert "response_time" in status
            assert "last_used" in status