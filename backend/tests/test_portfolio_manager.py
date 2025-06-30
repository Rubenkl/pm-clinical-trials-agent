"""Tests for Portfolio Manager (Master Orchestrator) Agent."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, List, Any
import asyncio

from app.agents.portfolio_manager import PortfolioManager, WorkflowRequest, WorkflowResponse, TaskStatus, AgentTask
from app.agents.query_analyzer import QueryAnalyzer
from app.agents.base_agent import AgentResponse


class TestTaskStatus:
    """Test cases for TaskStatus enum."""

    def test_task_status_values(self):
        """Test that TaskStatus enum has expected values."""
        assert TaskStatus.PENDING.value == "pending"
        assert TaskStatus.IN_PROGRESS.value == "in_progress"
        assert TaskStatus.COMPLETED.value == "completed"
        assert TaskStatus.FAILED.value == "failed"
        assert TaskStatus.CANCELLED.value == "cancelled"


class TestAgentTask:
    """Test cases for AgentTask data class."""

    def test_agent_task_creation(self):
        """Test AgentTask creation with required fields."""
        task = AgentTask(
            task_id="TASK_001",
            agent_id="query-analyzer",
            task_type="data_analysis",
            description="Analyze patient data for discrepancies",
            input_data={"subject_id": "S001", "visit": "Week 2"},
            priority=1
        )
        
        assert task.task_id == "TASK_001"
        assert task.agent_id == "query-analyzer"
        assert task.task_type == "data_analysis"
        assert task.status == TaskStatus.PENDING
        assert task.priority == 1
        assert task.created_at is not None
        assert task.dependencies == []

    def test_agent_task_with_dependencies(self):
        """Test AgentTask with dependencies."""
        task = AgentTask(
            task_id="TASK_002",
            agent_id="query-generator",
            task_type="query_generation",
            description="Generate queries based on analysis",
            input_data={"analysis_results": []},
            priority=2,
            dependencies=["TASK_001"]
        )
        
        assert task.dependencies == ["TASK_001"]

    def test_agent_task_serialization(self):
        """Test AgentTask serialization to dict."""
        task = AgentTask(
            task_id="TASK_003",
            agent_id="compliance-checker",
            task_type="compliance_check",
            description="Check regulatory compliance",
            input_data={"protocol": "PROTO_001"}
        )
        
        task_dict = task.to_dict()
        
        assert isinstance(task_dict, dict)
        assert task_dict["task_id"] == "TASK_003"
        assert task_dict["status"] == "pending"
        assert "created_at" in task_dict

    def test_task_can_execute(self):
        """Test task execution readiness checking."""
        # Task with no dependencies
        simple_task = AgentTask(
            task_id="TASK_004",
            agent_id="analyzer",
            task_type="analysis",
            description="Simple analysis task",
            input_data={}
        )
        
        assert simple_task.can_execute([]) is True
        
        # Task with dependencies
        dependent_task = AgentTask(
            task_id="TASK_005",
            agent_id="generator",
            task_type="generation",
            description="Dependent task",
            input_data={},
            dependencies=["TASK_004"]
        )
        
        # Should not be able to execute without completed dependencies
        assert dependent_task.can_execute([]) is False
        
        # Should be able to execute with completed dependencies
        completed_tasks = ["TASK_004"]
        assert dependent_task.can_execute(completed_tasks) is True


class TestWorkflowRequest:
    """Test cases for WorkflowRequest data class."""

    def test_workflow_request_creation(self):
        """Test WorkflowRequest creation."""
        request = WorkflowRequest(
            workflow_id="WF_001",
            workflow_type="clinical_data_analysis",
            description="Analyze clinical trial data for Site 101",
            input_data={
                "site_id": "101",
                "subjects": ["S001", "S002", "S003"],
                "data_cutoff_date": "2024-01-15"
            },
            priority=1
        )
        
        assert request.workflow_id == "WF_001"
        assert request.workflow_type == "clinical_data_analysis"
        assert request.priority == 1
        assert request.metadata == {}

    def test_workflow_request_with_metadata(self):
        """Test WorkflowRequest with metadata."""
        metadata = {
            "requester": "john.doe@clinicaltrials.com",
            "deadline": "2024-01-20",
            "urgency": "high"
        }
        
        request = WorkflowRequest(
            workflow_id="WF_002",
            workflow_type="query_generation",
            description="Generate queries for data discrepancies",
            input_data={"discrepancies": []},
            metadata=metadata
        )
        
        assert request.metadata == metadata


class TestWorkflowResponse:
    """Test cases for WorkflowResponse data class."""

    def test_workflow_response_success(self):
        """Test successful WorkflowResponse creation."""
        response = WorkflowResponse(
            workflow_id="WF_001",
            success=True,
            results={
                "queries_generated": 15,
                "discrepancies_found": 8,
                "compliance_issues": 2
            },
            execution_time=45.7,
            tasks_completed=5
        )
        
        assert response.success is True
        assert response.results["queries_generated"] == 15
        assert response.execution_time == 45.7
        assert response.error is None

    def test_workflow_response_failure(self):
        """Test failed WorkflowResponse creation."""
        response = WorkflowResponse(
            workflow_id="WF_002",
            success=False,
            results={},
            execution_time=12.3,
            tasks_completed=2,
            tasks_failed=1,
            error="Agent communication timeout"
        )
        
        assert response.success is False
        assert response.error == "Agent communication timeout"
        assert response.tasks_failed == 1


class TestPortfolioManager:
    """Test cases for PortfolioManager agent."""

    @pytest.fixture
    def mock_openai_client(self):
        """Mock OpenAI client for testing."""
        with patch('app.agents.base_agent.AsyncOpenAI') as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value = mock_instance
            yield mock_instance

    @pytest.fixture
    def portfolio_manager(self, mock_openai_client):
        """Create a PortfolioManager instance for testing."""
        return PortfolioManager()

    @pytest.fixture
    def mock_query_analyzer(self):
        """Mock QueryAnalyzer for testing."""
        with patch('app.agents.query_analyzer.QueryAnalyzer') as mock_analyzer:
            mock_instance = AsyncMock()
            mock_analyzer.return_value = mock_instance
            yield mock_instance

    def test_portfolio_manager_initialization(self, portfolio_manager):
        """Test PortfolioManager initialization."""
        assert portfolio_manager.agent_id == "portfolio-manager"
        assert portfolio_manager.name == "Portfolio Manager"
        assert "coordinates" in portfolio_manager.description.lower()
        assert portfolio_manager.model == "gpt-4"
        assert portfolio_manager.temperature == 0.1
        assert portfolio_manager.max_tokens == 3000

    def test_register_agent(self, portfolio_manager, mock_query_analyzer):
        """Test agent registration."""
        portfolio_manager.register_agent("query-analyzer", mock_query_analyzer)
        
        assert "query-analyzer" in portfolio_manager.registered_agents
        assert portfolio_manager.registered_agents["query-analyzer"] == mock_query_analyzer

    def test_unregister_agent(self, portfolio_manager, mock_query_analyzer):
        """Test agent unregistration."""
        portfolio_manager.register_agent("query-analyzer", mock_query_analyzer)
        portfolio_manager.unregister_agent("query-analyzer")
        
        assert "query-analyzer" not in portfolio_manager.registered_agents

    def test_get_available_agents(self, portfolio_manager, mock_query_analyzer):
        """Test getting list of available agents."""
        portfolio_manager.register_agent("query-analyzer", mock_query_analyzer)
        
        agents = portfolio_manager.get_available_agents()
        
        assert "query-analyzer" in agents
        assert len(agents) == 1

    @pytest.mark.asyncio
    async def test_execute_workflow_simple(self, portfolio_manager, mock_openai_client):
        """Test simple workflow execution."""
        # Mock OpenAI response for workflow planning
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock()]
        mock_completion.choices[0].message.content = '''
        {
            "workflow_plan": [
                {
                    "task_id": "TASK_001",
                    "agent_id": "query-analyzer",
                    "task_type": "data_analysis",
                    "description": "Analyze patient data",
                    "input_data": {"subject_id": "S001"},
                    "priority": 1,
                    "dependencies": []
                }
            ],
            "estimated_execution_time": 30,
            "complexity": "low"
        }
        '''
        mock_completion.usage.total_tokens = 200
        mock_openai_client.chat.completions.create = AsyncMock(return_value=mock_completion)
        
        # Mock agent execution
        mock_agent = AsyncMock()
        mock_agent.process_message = AsyncMock(return_value=AgentResponse(
            success=True,
            content="Analysis completed",
            agent_id="query-analyzer",
            execution_time=15.5
        ))
        portfolio_manager.register_agent("query-analyzer", mock_agent)
        
        # Create workflow request
        request = WorkflowRequest(
            workflow_id="WF_001",
            workflow_type="simple_analysis",
            description="Analyze single subject data",
            input_data={"subject_id": "S001"}
        )
        
        # Execute workflow
        response = await portfolio_manager.execute_workflow(request)
        
        assert response.success is True
        assert response.workflow_id == "WF_001"
        assert response.tasks_completed == 1
        assert response.tasks_failed == 0

    @pytest.mark.asyncio
    async def test_execute_workflow_with_dependencies(self, portfolio_manager, mock_openai_client):
        """Test workflow execution with task dependencies."""
        # Mock workflow planning response
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock()]
        mock_completion.choices[0].message.content = '''
        {
            "workflow_plan": [
                {
                    "task_id": "TASK_001",
                    "agent_id": "query-analyzer",
                    "task_type": "analysis",
                    "description": "Analyze data",
                    "input_data": {"data": "raw"},
                    "priority": 1,
                    "dependencies": []
                },
                {
                    "task_id": "TASK_002",
                    "agent_id": "query-generator",
                    "task_type": "generation",
                    "description": "Generate queries",
                    "input_data": {"analysis_results": "from_task_001"},
                    "priority": 2,
                    "dependencies": ["TASK_001"]
                }
            ],
            "estimated_execution_time": 60,
            "complexity": "medium"
        }
        '''
        mock_completion.usage.total_tokens = 300
        mock_openai_client.chat.completions.create = AsyncMock(return_value=mock_completion)
        
        # Mock agents
        mock_analyzer = AsyncMock()
        mock_analyzer.process_message = AsyncMock(return_value=AgentResponse(
            success=True,
            content="Analysis results",
            agent_id="query-analyzer",
            execution_time=20.0
        ))
        
        mock_generator = AsyncMock()
        mock_generator.process_message = AsyncMock(return_value=AgentResponse(
            success=True,
            content="Generated queries",
            agent_id="query-generator",
            execution_time=15.0
        ))
        
        portfolio_manager.register_agent("query-analyzer", mock_analyzer)
        portfolio_manager.register_agent("query-generator", mock_generator)
        
        request = WorkflowRequest(
            workflow_id="WF_002",
            workflow_type="analysis_and_generation",
            description="Analyze data and generate queries",
            input_data={"raw_data": "patient_data"}
        )
        
        response = await portfolio_manager.execute_workflow(request)
        
        assert response.success is True
        assert response.tasks_completed == 2
        assert response.execution_time > 0

    @pytest.mark.asyncio
    async def test_execute_parallel_tasks(self, portfolio_manager):
        """Test parallel task execution."""
        # Create tasks that can run in parallel
        tasks = [
            AgentTask(
                task_id="PARALLEL_001",
                agent_id="agent-1",
                task_type="independent_analysis",
                description="Independent analysis 1",
                input_data={"data": "dataset_1"}
            ),
            AgentTask(
                task_id="PARALLEL_002",
                agent_id="agent-2",
                task_type="independent_analysis",
                description="Independent analysis 2",
                input_data={"data": "dataset_2"}
            )
        ]
        
        # Mock agents
        mock_agent1 = AsyncMock()
        mock_agent1.process_message = AsyncMock(return_value=AgentResponse(
            success=True,
            content="Result 1",
            agent_id="agent-1",
            execution_time=10.0
        ))
        
        mock_agent2 = AsyncMock()
        mock_agent2.process_message = AsyncMock(return_value=AgentResponse(
            success=True,
            content="Result 2",
            agent_id="agent-2",
            execution_time=12.0
        ))
        
        portfolio_manager.register_agent("agent-1", mock_agent1)
        portfolio_manager.register_agent("agent-2", mock_agent2)
        
        results = await portfolio_manager.execute_parallel_tasks(tasks)
        
        assert len(results) == 2
        assert all(result.success for result in results)

    @pytest.mark.asyncio
    async def test_workflow_error_handling(self, portfolio_manager, mock_openai_client):
        """Test workflow error handling and recovery."""
        # Mock workflow planning
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock()]
        mock_completion.choices[0].message.content = '''
        {
            "workflow_plan": [
                {
                    "task_id": "TASK_FAIL",
                    "agent_id": "failing-agent",
                    "task_type": "analysis",
                    "description": "This task will fail",
                    "input_data": {},
                    "priority": 1,
                    "dependencies": []
                }
            ],
            "estimated_execution_time": 30,
            "complexity": "low"
        }
        '''
        mock_openai_client.chat.completions.create = AsyncMock(return_value=mock_completion)
        
        # Mock failing agent
        mock_agent = AsyncMock()
        mock_agent.process_message = AsyncMock(return_value=AgentResponse(
            success=False,
            content="",
            agent_id="failing-agent",
            execution_time=5.0,
            error="Agent processing failed"
        ))
        
        portfolio_manager.register_agent("failing-agent", mock_agent)
        
        request = WorkflowRequest(
            workflow_id="WF_FAIL",
            workflow_type="failing_workflow",
            description="This workflow will fail",
            input_data={}
        )
        
        response = await portfolio_manager.execute_workflow(request)
        
        assert response.success is False
        assert response.tasks_failed == 1
        assert "Agent processing failed" in response.error

    def test_task_dependency_resolution(self, portfolio_manager):
        """Test task dependency resolution and ordering."""
        tasks = [
            AgentTask(
                task_id="TASK_C",
                agent_id="agent-c",
                task_type="final",
                description="Final task",
                input_data={},
                dependencies=["TASK_A", "TASK_B"]
            ),
            AgentTask(
                task_id="TASK_A",
                agent_id="agent-a",
                task_type="initial",
                description="Initial task A",
                input_data={}
            ),
            AgentTask(
                task_id="TASK_B",
                agent_id="agent-b",
                task_type="initial",
                description="Initial task B",
                input_data={},
                dependencies=["TASK_A"]
            )
        ]
        
        ordered_tasks = portfolio_manager.resolve_task_dependencies(tasks)
        
        # Should be ordered: TASK_A, TASK_B, TASK_C
        task_ids = [task.task_id for task in ordered_tasks]
        assert task_ids.index("TASK_A") < task_ids.index("TASK_B")
        assert task_ids.index("TASK_B") < task_ids.index("TASK_C")

    def test_workflow_status_tracking(self, portfolio_manager):
        """Test workflow status tracking and monitoring."""
        workflow_id = "WF_STATUS_TEST"
        
        # Should not exist initially
        status = portfolio_manager.get_workflow_status(workflow_id)
        assert status is None
        
        # Create workflow
        request = WorkflowRequest(
            workflow_id=workflow_id,
            workflow_type="test_workflow",
            description="Status tracking test",
            input_data={}
        )
        
        portfolio_manager.track_workflow(request)
        
        # Should now exist with pending status
        status = portfolio_manager.get_workflow_status(workflow_id)
        assert status is not None
        assert status["status"] == "pending"

    def test_performance_metrics(self, portfolio_manager):
        """Test performance metrics collection."""
        metrics = portfolio_manager.get_performance_metrics()
        
        assert "workflows_executed" in metrics
        assert "total_execution_time" in metrics
        assert "average_workflow_time" in metrics
        assert "success_rate" in metrics
        assert "active_workflows" in metrics
        assert "registered_agents" in metrics

    @pytest.mark.asyncio
    async def test_agent_health_monitoring(self, portfolio_manager):
        """Test agent health monitoring."""
        # Mock healthy agent
        healthy_agent = AsyncMock()
        healthy_agent.is_active = True
        healthy_agent.get_stats = MagicMock(return_value={
            "success_rate": 95.0,
            "average_execution_time": 5.2
        })
        
        # Mock unhealthy agent
        unhealthy_agent = AsyncMock()
        unhealthy_agent.is_active = False
        unhealthy_agent.get_stats = MagicMock(return_value={
            "success_rate": 60.0,
            "average_execution_time": 25.8
        })
        
        portfolio_manager.register_agent("healthy-agent", healthy_agent)
        portfolio_manager.register_agent("unhealthy-agent", unhealthy_agent)
        
        health_report = await portfolio_manager.check_agent_health()
        
        assert "healthy-agent" in health_report
        assert "unhealthy-agent" in health_report
        assert health_report["healthy-agent"]["status"] == "healthy"
        assert health_report["unhealthy-agent"]["status"] == "unhealthy"

    def test_workflow_cancellation(self, portfolio_manager):
        """Test workflow cancellation functionality."""
        workflow_id = "WF_CANCEL_TEST"
        
        # Track a workflow
        request = WorkflowRequest(
            workflow_id=workflow_id,
            workflow_type="cancellable_workflow",
            description="Test cancellation",
            input_data={}
        )
        
        portfolio_manager.track_workflow(request)
        
        # Cancel the workflow
        result = portfolio_manager.cancel_workflow(workflow_id)
        assert result is True
        
        # Check status
        status = portfolio_manager.get_workflow_status(workflow_id)
        assert status["status"] == "cancelled"

    @pytest.mark.asyncio
    async def test_workflow_timeout_handling(self, portfolio_manager):
        """Test workflow timeout handling."""
        # This would be implemented with actual timeout logic
        # For now, just test the interface
        workflow_id = "WF_TIMEOUT_TEST"
        timeout_seconds = 30
        
        request = WorkflowRequest(
            workflow_id=workflow_id,
            workflow_type="long_running_workflow",
            description="Test timeout",
            input_data={},
            metadata={"timeout": timeout_seconds}
        )
        
        # Mock a long-running workflow that would timeout
        # In real implementation, this would use asyncio.wait_for
        assert hasattr(portfolio_manager, 'execute_workflow_with_timeout')


@pytest.fixture
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()