"""Portfolio Manager (Master Orchestrator) Agent for multi-agent coordination."""

import asyncio
import json
import time
from enum import Enum
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict

from app.agents.base_agent import ClinicalTrialsAgent, AgentResponse


class TaskStatus(Enum):
    """Status of individual tasks in a workflow."""
    
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class AgentTask:
    """Represents a task to be executed by a specific agent."""
    
    task_id: str
    agent_id: str
    task_type: str
    description: str
    input_data: Dict[str, Any]
    priority: int = 1
    status: TaskStatus = TaskStatus.PENDING
    dependencies: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[AgentResponse] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary format."""
        return {
            "task_id": self.task_id,
            "agent_id": self.agent_id,
            "task_type": self.task_type,
            "description": self.description,
            "input_data": self.input_data,
            "priority": self.priority,
            "status": self.status.value,
            "dependencies": self.dependencies,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "metadata": self.metadata
        }
    
    def can_execute(self, completed_tasks: List[str]) -> bool:
        """Check if task can be executed based on dependencies."""
        return all(dep in completed_tasks for dep in self.dependencies)
    
    def start(self) -> None:
        """Mark task as started."""
        self.status = TaskStatus.IN_PROGRESS
        self.started_at = datetime.now()
    
    def complete(self, result: AgentResponse) -> None:
        """Mark task as completed with result."""
        self.status = TaskStatus.COMPLETED if result.success else TaskStatus.FAILED
        self.completed_at = datetime.now()
        self.result = result
    
    def cancel(self) -> None:
        """Mark task as cancelled."""
        self.status = TaskStatus.CANCELLED
        self.completed_at = datetime.now()


@dataclass
class WorkflowRequest:
    """Request to execute a multi-agent workflow."""
    
    workflow_id: str
    workflow_type: str
    description: str
    input_data: Dict[str, Any]
    priority: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class WorkflowResponse:
    """Response from workflow execution."""
    
    workflow_id: str
    success: bool
    results: Dict[str, Any]
    execution_time: float
    tasks_completed: int
    tasks_failed: int = 0
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    completed_at: datetime = field(default_factory=datetime.now)


@dataclass
class SimpleWorkflowResult:
    """Simple result for context-based workflow execution."""
    
    status: str = "completed"
    success: bool = True
    error: Optional[str] = None
    execution_time: float = 0.0
    agent_results: Dict[str, Any] = field(default_factory=dict)


class PortfolioManager(ClinicalTrialsAgent):
    """Master orchestrator agent that coordinates multiple specialized agents."""
    
    def __init__(self):
        """Initialize the Portfolio Manager agent."""
        super().__init__(
            agent_id="portfolio-manager",
            name="Portfolio Manager",
            description=(
                "Master orchestrator that coordinates multiple specialized clinical trial agents. "
                "Manages workflow execution, task dependencies, parallel processing, and "
                "resource allocation across the agent ecosystem."
            ),
            model="gpt-4",
            temperature=0.1,
            max_tokens=3000
        )
        
        # Agent registry and management
        self.registered_agents: Dict[str, Any] = {}
        self.agent_capabilities: Dict[str, List[str]] = {}
        
        # Alias for test compatibility
        self.agents = self.registered_agents
        
        # Workflow tracking
        self.active_workflows: Dict[str, Dict[str, Any]] = {}
        self.workflow_history: List[WorkflowResponse] = []
        
        # Performance metrics
        self._performance_metrics = {
            "workflows_executed": 0,
            "total_execution_time": 0.0,
            "success_count": 0,
            "failure_count": 0,
            "tasks_executed": 0
        }
        
        # Task queue and execution
        self.task_queue: List[AgentTask] = []
        self.completed_tasks: List[str] = []
        
        # Configuration
        self.max_parallel_tasks = 5
        self.default_timeout = 300  # 5 minutes
        self.retry_attempts = 3
    
    def _get_default_system_prompt(self) -> str:
        """Get specialized system prompt for workflow orchestration."""
        return (
            f"You are {self.name}, the master orchestrator for a clinical trials multi-agent system. "
            f"{self.description} "
            
            "Your responsibilities include:\n"
            "1. Analyzing workflow requests and breaking them down into agent-specific tasks\n"
            "2. Managing task dependencies and execution order\n"
            "3. Coordinating parallel task execution for optimal performance\n"
            "4. Handling error recovery and retry logic\n"
            "5. Monitoring agent health and performance\n"
            "6. Optimizing resource allocation and load balancing\n\n"
            
            "Available Agent Types:\n"
            "- query-analyzer: Analyzes clinical data for discrepancies and generates queries\n"
            "- query-generator: Creates medical queries based on analysis results\n"
            "- query-tracker: Tracks query status and manages follow-ups\n"
            "- sdv-risk-assessor: Assesses risk for source data verification\n"
            "- data-verifier: Performs cross-system data matching and verification\n"
            "- compliance-checker: Validates regulatory compliance\n"
            "- pattern-detector: Identifies patterns across multiple data points\n\n"
            
            "Workflow Planning Format:\n"
            "Always respond with JSON containing:\n"
            "- workflow_plan: array of tasks with task_id, agent_id, task_type, description, input_data, priority, dependencies\n"
            "- estimated_execution_time: estimated total time in seconds\n"
            "- complexity: low/medium/high\n"
            "- parallel_opportunities: tasks that can run in parallel\n"
            "- critical_path: sequence of tasks that determine minimum execution time\n\n"
            
            "Guidelines:\n"
            "- Optimize for parallel execution when possible\n"
            "- Consider agent capabilities and current load\n"
            "- Prioritize critical safety and compliance tasks\n"
            "- Plan for error handling and recovery\n"
            "- Ensure data flows correctly between dependent tasks"
        )
    
    def register_agent(self, agent_id: str, agent_instance: Any, capabilities: Optional[List[str]] = None) -> None:
        """Register an agent with the portfolio manager.
        
        Args:
            agent_id: Unique identifier for the agent
            agent_instance: The actual agent instance
            capabilities: List of capabilities/task types the agent can handle
        """
        self.registered_agents[agent_id] = agent_instance
        self.agent_capabilities[agent_id] = capabilities or []
        
        from app.agents.base_agent import AgentMessage
        self.add_message(AgentMessage(
            role="system",
            content=f"Agent {agent_id} registered with capabilities: {capabilities}",
            agent_id=self.agent_id
        ))
    
    def unregister_agent(self, agent_id: str) -> None:
        """Unregister an agent from the portfolio manager."""
        if agent_id in self.registered_agents:
            del self.registered_agents[agent_id]
            del self.agent_capabilities[agent_id]
    
    def get_available_agents(self) -> List[str]:
        """Get list of currently available agents."""
        return list(self.registered_agents.keys())
    
    def execute_workflow(self, context_or_request) -> Union[WorkflowResponse, SimpleWorkflowResult]:
        """Execute a complete workflow by coordinating multiple agents.
        
        Args:
            context_or_request: Either a WorkflowRequest or Context object
            
        Returns:
            WorkflowResponse or SimpleWorkflowResult depending on input type
        """
        start_time = time.time()
        
        # Check if input is a Context object (for test compatibility)
        if hasattr(context_or_request, 'user_request') and hasattr(context_or_request, 'workflow_state'):
            return self._execute_with_context(context_or_request, start_time)
        
        # Handle WorkflowRequest (original async functionality)
        return asyncio.run(self._execute_with_request(context_or_request, start_time))
    
    def _execute_with_context(self, context, start_time: float) -> SimpleWorkflowResult:
        """Execute workflow with Context object (synchronous for tests)."""
        try:
            # Update context state
            context.workflow_state = "in_progress"
            context.current_agent = self.agent_id
            context.updated_at = datetime.now()
            
            # Simple execution for registered agents
            results = {}
            
            # Execute query analyzer if registered and request looks like a query
            if "query_analyzer" in self.registered_agents and context.user_request:
                agent = self.registered_agents["query_analyzer"]
                if hasattr(agent, 'analyze'):
                    try:
                        result = agent.analyze(context.user_request)
                        results["query_analyzer"] = result
                        context.query_analysis = result
                    except Exception as e:
                        context.errors.append(f"Query analysis failed: {str(e)}")
                        results["query_analyzer"] = {"error": str(e)}
            
            # Execute coordinator if registered and request mentions coordination patterns
            if ("coordinator" in self.registered_agents and 
                context.user_request and 
                any(word in context.user_request.lower() for word in ["comprehensive", "analysis", "report", "coordination", "coordinate"])):
                agent = self.registered_agents["coordinator"]
                if hasattr(agent, 'coordinate'):
                    try:
                        result = agent.coordinate()
                        results["coordinator"] = result
                    except Exception as e:
                        context.errors.append(f"Coordination failed: {str(e)}")
                        results["coordinator"] = {"error": str(e)}
            
            # Execute analyst if registered and coordinator indicates analysis needed
            if ("analyst" in self.registered_agents and 
                "coordinator" in results and 
                isinstance(results.get("coordinator"), dict) and
                "analyze" in str(results["coordinator"]).lower()):
                agent = self.registered_agents["analyst"]
                if hasattr(agent, 'analyze'):
                    try:
                        result = agent.analyze()
                        results["analyst"] = result
                    except Exception as e:
                        context.errors.append(f"Analysis failed: {str(e)}")
                        results["analyst"] = {"error": str(e)}
            
            # Execute reporter if registered and workflow indicates reporting needed
            if ("reporter" in self.registered_agents and 
                context.user_request and 
                "report" in context.user_request.lower()):
                agent = self.registered_agents["reporter"]
                if hasattr(agent, 'generate_report'):
                    try:
                        result = agent.generate_report()
                        results["reporter"] = result
                    except Exception as e:
                        context.errors.append(f"Report generation failed: {str(e)}")
                        results["reporter"] = {"error": str(e)}
            
            # Execute data verifier if registered and analysis indicates verification needed
            if ("data_verifier" in self.registered_agents and 
                hasattr(context, 'query_analysis') and 
                context.query_analysis and 
                context.query_analysis.get('requires_verification', False)):
                agent = self.registered_agents["data_verifier"]
                if hasattr(agent, 'verify'):
                    try:
                        result = agent.verify(context)
                        results["data_verifier"] = result
                    except Exception as e:
                        context.errors.append(f"Data verification failed: {str(e)}")
                        results["data_verifier"] = {"error": str(e)}
            
            # Update context final state
            if context.errors:
                context.workflow_state = "failed"
                status = "failed"
                success = False
                error = "; ".join(context.errors)
            else:
                context.workflow_state = "completed"
                status = "completed"
                success = True
                error = None
            
            execution_time = time.time() - start_time
            context.execution_time = execution_time
            
            return SimpleWorkflowResult(
                status=status,
                success=success,
                error=error,
                execution_time=execution_time,
                agent_results=results
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            context.workflow_state = "failed"
            context.errors.append(str(e))
            context.execution_time = execution_time
            
            return SimpleWorkflowResult(
                status="failed",
                success=False,
                error=str(e),
                execution_time=execution_time,
                agent_results={}
            )
    
    async def _execute_with_request(self, request: WorkflowRequest, start_time: float) -> WorkflowResponse:
        """Execute workflow with WorkflowRequest (original async functionality)."""
        workflow_id = request.workflow_id
        
        try:
            # Track workflow
            self.track_workflow(request)
            
            # Plan the workflow
            workflow_plan = await self._plan_workflow(request)
            
            # Create tasks from plan
            tasks = self._create_tasks_from_plan(workflow_plan, request)
            
            # Resolve dependencies and order tasks
            ordered_tasks = self.resolve_task_dependencies(tasks)
            
            # Execute tasks
            task_results = await self._execute_workflow_tasks(ordered_tasks)
            
            # Analyze results
            success = all(result.success for result in task_results if result is not None)
            completed_count = sum(1 for result in task_results if result and result.success)
            failed_count = sum(1 for result in task_results if result and not result.success)
            
            execution_time = time.time() - start_time
            
            # Update metrics
            self._performance_metrics["workflows_executed"] += 1
            self._performance_metrics["total_execution_time"] += execution_time
            self._performance_metrics["tasks_executed"] += len(tasks)
            
            if success:
                self._performance_metrics["success_count"] += 1
            else:
                self._performance_metrics["failure_count"] += 1
            
            # Compile results
            results = self._compile_workflow_results(task_results, workflow_plan)
            
            # Get detailed error message for failures
            error_message = None
            if not success:
                failed_errors = [r.error for r in task_results if r and not r.success and r.error]
                if failed_errors:
                    error_message = failed_errors[0]  # Use the first specific error
                else:
                    error_message = "One or more tasks failed"
            
            response = WorkflowResponse(
                workflow_id=workflow_id,
                success=success,
                results=results,
                execution_time=execution_time,
                tasks_completed=completed_count,
                tasks_failed=failed_count,
                error=error_message
            )
            
            # Update workflow tracking
            self._update_workflow_status(workflow_id, "completed" if success else "failed")
            self.workflow_history.append(response)
            
            return response
            
        except Exception as e:
            execution_time = time.time() - start_time
            self._performance_metrics["failure_count"] += 1
            
            error_response = WorkflowResponse(
                workflow_id=workflow_id,
                success=False,
                results={},
                execution_time=execution_time,
                tasks_completed=0,
                tasks_failed=1,
                error=str(e)
            )
            
            self._update_workflow_status(workflow_id, "failed")
            return error_response
    
    async def _plan_workflow(self, request: WorkflowRequest) -> Dict[str, Any]:
        """Plan workflow execution using AI reasoning.
        
        Args:
            request: Workflow request to plan
            
        Returns:
            Dictionary containing workflow plan
        """
        planning_prompt = f"""
        Plan the execution of the following clinical trials workflow:
        
        Workflow Type: {request.workflow_type}
        Description: {request.description}
        Input Data: {json.dumps(request.input_data, indent=2)}
        Priority: {request.priority}
        
        Available Agents: {list(self.registered_agents.keys())}
        
        Create an optimal execution plan considering:
        1. Task dependencies and execution order
        2. Opportunities for parallel execution
        3. Data flow between tasks
        4. Error handling requirements
        5. Clinical trial compliance needs
        
        Respond with a detailed workflow plan in the specified JSON format.
        """
        
        response = await self.process_message(planning_prompt)
        
        if not response.success:
            raise Exception(f"Workflow planning failed: {response.error}")
        
        try:
            workflow_plan = json.loads(response.content)
            return workflow_plan
        except json.JSONDecodeError:
            raise Exception("Failed to parse workflow plan JSON")
    
    def _create_tasks_from_plan(self, workflow_plan: Dict[str, Any], request: WorkflowRequest) -> List[AgentTask]:
        """Create AgentTask objects from workflow plan.
        
        Args:
            workflow_plan: Parsed workflow plan
            request: Original workflow request
            
        Returns:
            List of AgentTask objects
        """
        tasks = []
        
        for task_spec in workflow_plan.get("workflow_plan", []):
            task = AgentTask(
                task_id=task_spec["task_id"],
                agent_id=task_spec["agent_id"],
                task_type=task_spec["task_type"],
                description=task_spec["description"],
                input_data=task_spec["input_data"],
                priority=task_spec.get("priority", 1),
                dependencies=task_spec.get("dependencies", []),
                metadata={
                    "workflow_id": request.workflow_id,
                    "workflow_type": request.workflow_type
                }
            )
            tasks.append(task)
        
        return tasks
    
    def resolve_task_dependencies(self, tasks: List[AgentTask]) -> List[AgentTask]:
        """Resolve task dependencies and return tasks in execution order.
        
        Args:
            tasks: List of tasks to order
            
        Returns:
            Tasks ordered by dependencies (topological sort)
        """
        # Create dependency graph
        task_map = {task.task_id: task for task in tasks}
        in_degree = {task.task_id: len(task.dependencies) for task in tasks}
        
        # Find tasks with no dependencies
        queue = [task_id for task_id, degree in in_degree.items() if degree == 0]
        ordered_tasks = []
        
        while queue:
            # Process tasks with no remaining dependencies
            current_task_id = queue.pop(0)
            current_task = task_map[current_task_id]
            ordered_tasks.append(current_task)
            
            # Update dependencies for other tasks
            for task in tasks:
                if current_task_id in task.dependencies:
                    in_degree[task.task_id] -= 1
                    if in_degree[task.task_id] == 0:
                        queue.append(task.task_id)
        
        # Check for circular dependencies
        if len(ordered_tasks) != len(tasks):
            raise ValueError("Circular dependency detected in task graph")
        
        return ordered_tasks
    
    async def _execute_workflow_tasks(self, tasks: List[AgentTask]) -> List[Optional[AgentResponse]]:
        """Execute workflow tasks in dependency order with parallel optimization.
        
        Args:
            tasks: Ordered list of tasks to execute
            
        Returns:
            List of agent responses
        """
        results = []
        completed_task_ids = []
        
        # Group tasks by execution batch (tasks that can run in parallel)
        execution_batches = self._group_tasks_for_parallel_execution(tasks)
        
        for batch in execution_batches:
            # Execute batch in parallel
            batch_results = await self.execute_parallel_tasks(batch)
            
            # Process results
            for i, result in enumerate(batch_results):
                task = batch[i]
                task.complete(result)
                results.append(result)
                
                if result.success:
                    completed_task_ids.append(task.task_id)
                    self.completed_tasks.append(task.task_id)
        
        return results
    
    def _group_tasks_for_parallel_execution(self, tasks: List[AgentTask]) -> List[List[AgentTask]]:
        """Group tasks into batches that can be executed in parallel.
        
        Args:
            tasks: Ordered list of tasks
            
        Returns:
            List of task batches for parallel execution
        """
        batches = []
        completed_task_ids = []
        remaining_tasks = tasks.copy()
        
        while remaining_tasks:
            # Find tasks that can execute now (dependencies satisfied)
            ready_tasks = [
                task for task in remaining_tasks 
                if task.can_execute(completed_task_ids)
            ]
            
            if not ready_tasks:
                # This shouldn't happen with proper dependency resolution
                raise ValueError("No tasks ready for execution - possible dependency issue")
            
            # Limit parallel batch size
            batch = ready_tasks[:self.max_parallel_tasks]
            batches.append(batch)
            
            # Remove batched tasks from remaining
            for task in batch:
                remaining_tasks.remove(task)
                completed_task_ids.append(task.task_id)
        
        return batches
    
    async def execute_parallel_tasks(self, tasks: List[AgentTask]) -> List[AgentResponse]:
        """Execute multiple tasks in parallel.
        
        Args:
            tasks: List of tasks to execute in parallel
            
        Returns:
            List of agent responses in same order as input tasks
        """
        # Create coroutines for each task
        coroutines = []
        
        for task in tasks:
            if task.agent_id not in self.registered_agents:
                # Create error response for missing agent
                error_response = AgentResponse(
                    success=False,
                    content="",
                    agent_id=task.agent_id,
                    execution_time=0.0,
                    error=f"Agent {task.agent_id} not registered"
                )
                coroutines.append(self._create_immediate_response(error_response))
            else:
                agent = self.registered_agents[task.agent_id]
                task.start()
                
                # Create task execution prompt
                task_prompt = self._build_task_prompt(task)
                coroutines.append(agent.process_message(task_prompt))
        
        # Execute all tasks in parallel
        results = await asyncio.gather(*coroutines, return_exceptions=True)
        
        # Convert exceptions to error responses
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                error_response = AgentResponse(
                    success=False,
                    content="",
                    agent_id=tasks[i].agent_id,
                    execution_time=0.0,
                    error=str(result)
                )
                processed_results.append(error_response)
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def _create_immediate_response(self, response: AgentResponse) -> AgentResponse:
        """Create an immediate response (for error cases)."""
        return response
    
    def _build_task_prompt(self, task: AgentTask) -> str:
        """Build prompt for task execution.
        
        Args:
            task: Task to build prompt for
            
        Returns:
            Formatted prompt string
        """
        return f"""
        Execute the following clinical trials task:
        
        Task ID: {task.task_id}
        Task Type: {task.task_type}
        Description: {task.description}
        Priority: {task.priority}
        
        Input Data:
        {json.dumps(task.input_data, indent=2)}
        
        Context:
        - Workflow: {task.metadata.get('workflow_id', 'Unknown')}
        - Workflow Type: {task.metadata.get('workflow_type', 'Unknown')}
        - Dependencies: {task.dependencies}
        
        Please process this task according to your specialization and return the results.
        """
    
    def _compile_workflow_results(self, task_results: List[Optional[AgentResponse]], workflow_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Compile individual task results into workflow results.
        
        Args:
            task_results: List of task execution results
            workflow_plan: Original workflow plan
            
        Returns:
            Compiled workflow results
        """
        successful_results = [r for r in task_results if r and r.success]
        failed_results = [r for r in task_results if r and not r.success]
        
        return {
            "total_tasks": len(task_results),
            "successful_tasks": len(successful_results),
            "failed_tasks": len(failed_results),
            "task_results": [r.to_dict() if hasattr(r, 'to_dict') else str(r) for r in task_results if r],
            "execution_summary": {
                "complexity": workflow_plan.get("complexity", "unknown"),
                "estimated_time": workflow_plan.get("estimated_execution_time", 0),
                "parallel_opportunities": workflow_plan.get("parallel_opportunities", [])
            }
        }
    
    def track_workflow(self, request: WorkflowRequest) -> None:
        """Start tracking a workflow."""
        self.active_workflows[request.workflow_id] = {
            "request": request,
            "status": "pending",
            "started_at": datetime.now(),
            "tasks": []
        }
    
    def _update_workflow_status(self, workflow_id: str, status: str) -> None:
        """Update workflow status."""
        if workflow_id in self.active_workflows:
            self.active_workflows[workflow_id]["status"] = status
            if status in ["completed", "failed", "cancelled"]:
                self.active_workflows[workflow_id]["completed_at"] = datetime.now()
    
    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of a workflow."""
        return self.active_workflows.get(workflow_id)
    
    def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel a workflow."""
        if workflow_id in self.active_workflows:
            self._update_workflow_status(workflow_id, "cancelled")
            return True
        return False
    
    async def check_agent_health(self) -> Dict[str, Dict[str, Any]]:
        """Check health status of all registered agents."""
        health_report = {}
        
        for agent_id, agent in self.registered_agents.items():
            try:
                # Check if agent is active
                is_active = getattr(agent, 'is_active', True)
                
                # Get agent statistics
                stats = agent.get_stats() if hasattr(agent, 'get_stats') else {}
                
                # Determine health status
                success_rate = stats.get('success_rate', 0)
                avg_time = stats.get('average_execution_time', 0)
                
                if is_active and success_rate > 80 and avg_time < 30:
                    status = "healthy"
                elif is_active and success_rate > 60:
                    status = "degraded"
                else:
                    status = "unhealthy"
                
                health_report[agent_id] = {
                    "status": status,
                    "is_active": is_active,
                    "statistics": stats,
                    "last_checked": datetime.now().isoformat()
                }
                
            except Exception as e:
                health_report[agent_id] = {
                    "status": "error",
                    "error": str(e),
                    "last_checked": datetime.now().isoformat()
                }
        
        return health_report
    
    def get_performance_metrics(self) -> Dict[str, Union[int, float]]:
        """Get performance metrics for the portfolio manager."""
        total_workflows = self._performance_metrics["workflows_executed"]
        success_rate = (
            (self._performance_metrics["success_count"] / total_workflows * 100) 
            if total_workflows > 0 else 0
        )
        average_workflow_time = (
            (self._performance_metrics["total_execution_time"] / total_workflows)
            if total_workflows > 0 else 0
        )
        
        return {
            "workflows_executed": total_workflows,
            "total_execution_time": self._performance_metrics["total_execution_time"],
            "average_workflow_time": average_workflow_time,
            "success_rate": success_rate,
            "tasks_executed": self._performance_metrics["tasks_executed"],
            "active_workflows": len(self.active_workflows),
            "registered_agents": len(self.registered_agents)
        }
    
    async def execute_workflow_with_timeout(self, request: WorkflowRequest, timeout_seconds: Optional[int] = None) -> WorkflowResponse:
        """Execute workflow with timeout."""
        timeout = timeout_seconds or self.default_timeout
        
        try:
            return await asyncio.wait_for(
                self._execute_with_request(request, time.time()),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            self._update_workflow_status(request.workflow_id, "failed")
            return WorkflowResponse(
                workflow_id=request.workflow_id,
                success=False,
                results={},
                execution_time=timeout,
                tasks_completed=0,
                tasks_failed=1,
                error=f"Workflow timed out after {timeout} seconds"
            )
    
    def clear_conversation(self) -> None:
        """Clear conversation history for all agents."""
        self.clear_history()
        
        # Clear history for all registered agents
        for agent in self.registered_agents.values():
            if hasattr(agent, 'clear_history'):
                agent.clear_history()
    
    def get_agent_statistics(self, agent_id: str) -> Dict[str, Any]:
        """Get statistics for a specific agent."""
        if agent_id == self.agent_id:
            return self.get_stats()
        
        if agent_id in self.registered_agents:
            agent = self.registered_agents[agent_id]
            if hasattr(agent, 'get_stats'):
                return agent.get_stats()
        
        return {}
    
    def is_agent_active(self, agent_id: str) -> bool:
        """Check if an agent is active."""
        if agent_id == self.agent_id:
            return self.is_active
        
        if agent_id in self.registered_agents:
            agent = self.registered_agents[agent_id]
            return getattr(agent, 'is_active', True)
        
        return False