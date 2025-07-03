"""Agent interaction endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import Dict, Any
import asyncio
import time
import json

# OpenAI Agents SDK
from agents import Runner

from app.api.models.agent_models import (
    ChatRequest, ChatResponse, WorkflowExecutionRequest, WorkflowExecutionResponse,
    AgentStatusResponse, WorkflowStatusRequest, WorkflowStatusResponse,
    AgentHealthResponse, BatchChatRequest, BatchChatResponse
)
from app.api.dependencies import (
    get_portfolio_manager, get_agent_by_type, validate_openai_key,
    validate_workflow_permissions, get_request_context
)
from app.agents.portfolio_manager import PortfolioManager, WorkflowRequest
from app.agents.base_agent import AgentResponse


agents_router = APIRouter()


@agents_router.post(
    "/chat",
    response_model=ChatResponse,
    dependencies=[Depends(validate_openai_key)]
)
async def chat_with_agent(
    request: ChatRequest,
    http_request: Request,
    portfolio_manager: PortfolioManager = Depends(get_portfolio_manager)
) -> ChatResponse:
    """Chat with an AI agent."""
    start_time = time.time()
    
    try:
        # Get request context
        context = get_request_context(http_request)
        
        # Route to appropriate agent with workflow orchestration
        if request.agent_type == "portfolio-manager":
            agent = portfolio_manager
        else:
            # For other agent types, use portfolio manager to coordinate
            agent = portfolio_manager
        
        # Determine if this requires workflow orchestration
        message_lower = request.message.lower()
        clinical_keywords = ['analyze', 'hemoglobin', 'blood pressure', 'clinical', 'subject', 'discrepancy', 'verify']
        
        if any(keyword in message_lower for keyword in clinical_keywords):
            # Use workflow orchestration for clinical tasks
            workflow_type = "comprehensive_analysis"
            if "verify" in message_lower or "verification" in message_lower:
                workflow_type = "data_verification"
            elif "query" in message_lower or "generate" in message_lower:
                workflow_type = "query_resolution"
            
            # Create workflow request
            workflow_request = {
                "workflow_id": f"CHAT_{int(time.time())}",
                "workflow_type": workflow_type,
                "description": f"Chat-initiated {workflow_type}",
                "input_data": {"message": request.message},
                "priority": 1
            }
            
            # Use OpenAI Agents SDK Runner to execute with function tools
            
            # Create a message that will trigger function tool usage
            workflow_message = f"""
CLINICAL DATA ANALYSIS REQUEST:
{request.message}

WORKFLOW TYPE: {workflow_type}
INSTRUCTIONS: Use your function tools to analyze this data. Call orchestrate_workflow with this JSON:
{json.dumps(workflow_request)}

Execute your tools and show the actual results, not just planning descriptions.
"""
            
            # Execute through OpenAI Agents SDK Runner
            sdk_result = await Runner.run(
                agent.agent,  # Use the actual SDK agent
                workflow_message,
                context=agent.context
            )
            
            # Create agent response from SDK result
            response = AgentResponse(
                success=True,
                content=sdk_result.final_output,
                agent_id="portfolio-manager",
                execution_time=0.0,
                metadata={"workflow_executed": True, "workflow_type": workflow_type, "tools_used": True}
            )
        else:
            # Process as simple message using OpenAI Agents SDK
            
            sdk_result = await Runner.run(
                agent.agent,  # Use the actual SDK agent
                request.message,
                context=agent.context
            )
            
            response = AgentResponse(
                success=True,
                content=sdk_result.final_output,
                agent_id="portfolio-manager",
                execution_time=0.0,
                metadata={"simple_query": True, "tools_available": True}
            )
        
        execution_time = time.time() - start_time
        
        return ChatResponse(
            success=response.success,
            response=response.content,
            agent_id=response.agent_id,
            execution_time=execution_time,
            error=response.error if not response.success else None,
            metadata={
                "request_context": context,
                "tokens_used": response.metadata.get("tokens_used", 0),
                "model": response.metadata.get("model", "unknown")
            }
        )
        
    except Exception as e:
        execution_time = time.time() - start_time
        
        return ChatResponse(
            success=False,
            response="",
            agent_id=request.agent_type,
            execution_time=execution_time,
            error=str(e),
            metadata={"request_context": get_request_context(http_request)}
        )


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
        # Clear conversation history
        portfolio_manager.clear_conversation()
        
        # Reset performance metrics
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


@agents_router.post("/batch/chat", response_model=BatchChatResponse)
async def batch_chat_with_agents(
    request: BatchChatRequest,
    portfolio_manager: PortfolioManager = Depends(get_portfolio_manager)
) -> BatchChatResponse:
    """Process multiple chat requests in batch."""
    start_time = time.time()
    
    try:
        if request.parallel_execution:
            # Execute requests in parallel
            tasks = []
            for chat_req in request.requests:
                task = portfolio_manager.process_message(chat_req.message)
                tasks.append(task)
            
            responses = await asyncio.gather(*tasks, return_exceptions=True)
        else:
            # Execute requests sequentially
            responses = []
            for chat_req in request.requests:
                response = await portfolio_manager.process_message(chat_req.message)
                responses.append(response)
        
        # Convert to ChatResponse objects
        chat_responses = []
        successful_count = 0
        failed_count = 0
        
        for i, response in enumerate(responses):
            if isinstance(response, Exception):
                chat_response = ChatResponse(
                    success=False,
                    response="",
                    agent_id="portfolio-manager",
                    execution_time=0.0,
                    error=str(response)
                )
                failed_count += 1
            else:
                chat_response = ChatResponse(
                    success=response.success,
                    response=response.content,
                    agent_id=response.agent_id,
                    execution_time=response.execution_time,
                    error=response.error if not response.success else None
                )
                if response.success:
                    successful_count += 1
                else:
                    failed_count += 1
            
            chat_responses.append(chat_response)
        
        total_execution_time = time.time() - start_time
        
        return BatchChatResponse(
            batch_id=request.batch_id,
            responses=chat_responses,
            total_requests=len(request.requests),
            successful_requests=successful_count,
            failed_requests=failed_count,
            total_execution_time=total_execution_time
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch chat processing failed: {str(e)}"
        )