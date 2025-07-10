"""Agent management endpoints for workflow orchestration (NO CHAT)."""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
import time

from app.api.models.agent_models import (
    WorkflowExecutionRequest, WorkflowExecutionResponse,
    AgentStatusResponse, WorkflowStatusRequest, WorkflowStatusResponse,
    AgentHealthResponse
)
from app.api.dependencies import (
    get_portfolio_manager, validate_openai_key,
    validate_workflow_permissions
)
from app.agents.portfolio_manager import PortfolioManager, WorkflowRequest


agents_router = APIRouter()


# CHAT ENDPOINT REMOVED - Use structured endpoints in /queries, /sdv, /deviations instead


@agents_router.post(
    "/workflow",
    response_model=WorkflowExecutionResponse,
    dependencies=[Depends(validate_openai_key), Depends(validate_workflow_permissions)]
)
async def execute_workflow(
    request: WorkflowExecutionRequest,
    portfolio_manager: PortfolioManager = Depends(get_portfolio_manager)
) -> WorkflowExecutionResponse:
    """Execute a multi-agent workflow."""
    try:
        # Convert API request to internal workflow request
        workflow_request = WorkflowRequest(
            workflow_id=request.workflow_id,
            workflow_type=request.workflow_type,
            description=request.description,
            input_data=request.input_data,
            priority=request.priority,
            metadata=request.metadata
        )
        
        # Execute workflow - handle both async and sync execution
        try:
            # Try async execution first (for real Portfolio Manager)
            if hasattr(portfolio_manager, '_execute_with_request'):
                workflow_response = await portfolio_manager._execute_with_request(workflow_request, time.time())
            else:
                # Fallback for mocked Portfolio Manager or sync execution
                workflow_response = portfolio_manager.execute_workflow(workflow_request)
                # If it's a coroutine, await it
                if hasattr(workflow_response, '__await__'):
                    workflow_response = await workflow_response
        except Exception as e:
            # If the above fails, try direct execution
            workflow_response = portfolio_manager.execute_workflow(workflow_request)
            if hasattr(workflow_response, '__await__'):
                workflow_response = await workflow_response
        
        return WorkflowExecutionResponse(
            success=workflow_response.success,
            workflow_id=workflow_response.workflow_id,
            tasks_completed=workflow_response.tasks_completed,
            tasks_failed=workflow_response.tasks_failed,
            execution_time=workflow_response.execution_time,
            results=workflow_response.results,
            error=workflow_response.error,
            metadata=workflow_response.metadata
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Workflow execution failed: {str(e)}"
        )


@agents_router.get("/status", response_model=AgentStatusResponse)
async def get_agent_status(
    portfolio_manager: PortfolioManager = Depends(get_portfolio_manager)
) -> AgentStatusResponse:
    """Get status of all agents."""
    try:
        # Get portfolio manager metrics
        pm_metrics = portfolio_manager.get_performance_metrics()
        
        # Check agent health
        agent_health = await portfolio_manager.check_agent_health()
        
        # Compile agent status
        agents_data = {}
        available_agents = portfolio_manager.get_available_agents()
        
        # Add portfolio manager status
        agents_data["portfolio-manager"] = {
            "status": "active",
            "success_rate": pm_metrics.get("success_rate", 0),
            "workflows_executed": pm_metrics.get("workflows_executed", 0),
            "active_workflows": pm_metrics.get("active_workflows", 0),
            "registered_agents": pm_metrics.get("registered_agents", 0)
        }
        
        # Add other agents status
        for agent_id in available_agents:
            if agent_id in agent_health:
                agents_data[agent_id] = agent_health[agent_id]
        
        return AgentStatusResponse(
            agents=agents_data,
            total_agents=len(agents_data),
            active_agents=sum(1 for agent in agents_data.values() if agent.get("status") == "active"),
            system_load=None,  # TODO: Implement system load monitoring
            uptime_seconds=None  # TODO: Implement uptime tracking
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get agent status: {str(e)}"
        )


@agents_router.get("/workflow/{workflow_id}/status", response_model=WorkflowStatusResponse)
async def get_workflow_status(
    workflow_id: str,
    portfolio_manager: PortfolioManager = Depends(get_portfolio_manager)
) -> WorkflowStatusResponse:
    """Get status of a specific workflow."""
    try:
        status_data = portfolio_manager.get_workflow_status(workflow_id)
        
        if not status_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Workflow {workflow_id} not found"
            )
        
        return WorkflowStatusResponse(
            workflow_id=workflow_id,
            status=status_data["status"],
            created_at=status_data["started_at"],
            started_at=status_data.get("started_at"),
            completed_at=status_data.get("completed_at"),
            progress=status_data.get("progress", {}),
            current_task=status_data.get("current_task")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get workflow status: {str(e)}"
        )


@agents_router.delete("/workflow/{workflow_id}")
async def cancel_workflow(
    workflow_id: str,
    portfolio_manager: PortfolioManager = Depends(get_portfolio_manager)
) -> Dict[str, Any]:
    """Cancel a running workflow."""
    try:
        success = portfolio_manager.cancel_workflow(workflow_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Workflow {workflow_id} not found or cannot be cancelled"
            )
        
        return {
            "success": True,
            "message": f"Workflow {workflow_id} has been cancelled",
            "workflow_id": workflow_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel workflow: {str(e)}"
        )


@agents_router.get("/health/{agent_id}", response_model=AgentHealthResponse)
async def get_agent_health(
    agent_id: str,
    portfolio_manager: PortfolioManager = Depends(get_portfolio_manager)
) -> AgentHealthResponse:
    """Get health status of a specific agent."""
    try:
        agent_health = await portfolio_manager.check_agent_health()
        
        if agent_id not in agent_health:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent {agent_id} not found"
            )
        
        health_data = agent_health[agent_id]
        
        return AgentHealthResponse(
            agent_id=agent_id,
            status=health_data["status"],
            is_active=health_data.get("is_active", False),
            statistics=health_data.get("statistics", {}),
            last_activity=None,  # TODO: Implement activity tracking
            error=health_data.get("error")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get agent health: {str(e)}"
        )


@agents_router.post("/reset")
async def reset_agent_system(
    portfolio_manager: PortfolioManager = Depends(get_portfolio_manager)
) -> Dict[str, Any]:
    """Reset the agent system (development/testing only)."""
    try:
        # Reset performance metrics (no conversation history to clear)
        portfolio_manager._performance_metrics = {
            "workflows_executed": 0,
            "total_execution_time": 0.0,
            "success_count": 0,
            "failure_count": 0,
            "tasks_executed": 0
        }
        
        return {
            "success": True,
            "message": "Agent system has been reset",
            "timestamp": time.time()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reset agent system: {str(e)}"
        )


# BATCH CHAT ENDPOINT REMOVED - Use structured bulk endpoints instead
# Example: POST /api/v1/queries/batch/analyze for bulk query processing