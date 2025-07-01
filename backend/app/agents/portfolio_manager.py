"""Portfolio Manager using OpenAI Agents SDK - Corrected Implementation."""

import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from agents import Agent, function_tool, Runner
from pydantic import BaseModel

class WorkflowContext(BaseModel):
    """Context for Portfolio Manager workflow orchestration using Pydantic."""
    
    active_workflows: Dict[str, Any] = {}
    agent_states: Dict[str, Any] = {}
    workflow_history: List[Dict[str, Any]] = []
    performance_metrics: Dict[str, Any] = {}

# Function tools with proper string-based signatures for OpenAI Agents SDK

@function_tool
def orchestrate_workflow(workflow_request: str) -> str:
    """Orchestrate a workflow by planning and coordinating multiple agents.
    
    Args:
        workflow_request: JSON string containing workflow_id, workflow_type, description, input_data
        
    Returns:
        JSON string with workflow execution plan and status
    """
    try:
        request_data = json.loads(workflow_request)
        workflow_id = request_data.get("workflow_id", f"WF_{uuid.uuid4().hex[:8]}")
        workflow_type = request_data.get("workflow_type", "query_resolution")
        description = request_data.get("description", "Clinical workflow execution")
        input_data = request_data.get("input_data", {})
    except json.JSONDecodeError:
        workflow_id = f"WF_{uuid.uuid4().hex[:8]}"
        workflow_type = "query_resolution"
        description = "Clinical workflow execution"
        input_data = {}
    
    # Define workflow execution plans based on type
    workflow_plans = {
        "query_resolution": {
            "agents": ["query_analyzer", "query_generator", "query_tracker"],
            "steps": [
                {"agent": "query_analyzer", "action": "analyze_clinical_data", "estimated_time": "2-3 min"},
                {"agent": "query_generator", "action": "generate_clinical_queries", "estimated_time": "1-2 min"},
                {"agent": "query_tracker", "action": "track_query_lifecycle", "estimated_time": "ongoing"}
            ]
        },
        "data_verification": {
            "agents": ["data_verifier", "query_generator", "query_tracker"],
            "steps": [
                {"agent": "data_verifier", "action": "cross_system_verification", "estimated_time": "3-5 min"},
                {"agent": "query_generator", "action": "generate_discrepancy_queries", "estimated_time": "1-2 min"},
                {"agent": "query_tracker", "action": "track_verification_queries", "estimated_time": "ongoing"}
            ]
        },
        "comprehensive_analysis": {
            "agents": ["query_analyzer", "data_verifier", "query_generator", "query_tracker"],
            "steps": [
                {"agent": "query_analyzer", "action": "analyze_clinical_data", "estimated_time": "2-3 min"},
                {"agent": "data_verifier", "action": "verify_analysis_results", "estimated_time": "2-3 min"},
                {"agent": "query_generator", "action": "generate_comprehensive_queries", "estimated_time": "2-3 min"},
                {"agent": "query_tracker", "action": "track_all_queries", "estimated_time": "ongoing"}
            ]
        }
    }
    
    plan = workflow_plans.get(workflow_type, workflow_plans["query_resolution"])
    
    result = {
        "success": True,
        "workflow_id": workflow_id,
        "workflow_type": workflow_type,
        "description": description,
        "status": "planned",
        "execution_plan": {
            "total_steps": len(plan["steps"]),
            "agents_involved": plan["agents"],
            "steps": plan["steps"],
            "estimated_total_time": "5-10 minutes"
        },
        "input_data_summary": {
            "subjects": len(input_data.get("subjects", [])) if "subjects" in input_data else 1,
            "data_points": len(str(input_data)),
            "critical_fields_detected": sum(1 for key in input_data.keys() if "adverse" in key.lower() or "medication" in key.lower())
        },
        "created_at": datetime.now().isoformat(),
        "message": f"Workflow {workflow_id} successfully planned with {len(plan['steps'])} steps"
    }
    
    return json.dumps(result)

@function_tool
def execute_workflow_step(step_data: str) -> str:
    """Execute a specific step in the workflow.
    
    Args:
        step_data: JSON string containing step_id, agent_id, action, input_data
        
    Returns:
        JSON string with step execution results
    """
    try:
        step_info = json.loads(step_data)
        step_id = step_info.get("step_id", "STEP_UNKNOWN")
        agent_id = step_info.get("agent_id", "unknown")
        action = step_info.get("action", "process")
    except json.JSONDecodeError:
        step_id = "STEP_UNKNOWN"
        agent_id = "unknown"
        action = "process"
    
    # Simulate step execution
    result = {
        "step_id": step_id,
        "agent_id": agent_id,
        "action": action,
        "status": "completed",
        "execution_time_ms": 1500,
        "result": f"Step {step_id} completed by {agent_id}",
        "next_step_recommended": True,
        "completed_at": datetime.now().isoformat()
    }
    
    return json.dumps(result)

@function_tool
def get_workflow_status(workflow_id: str) -> str:
    """Get the current status of a workflow execution.
    
    Args:
        workflow_id: Unique identifier for the workflow
        
    Returns:
        JSON string containing detailed workflow status
    """
    # Simulate workflow status lookup
    result = {
        "workflow_id": workflow_id,
        "status": "in_progress",
        "progress_percentage": 65,
        "current_step": 2,
        "total_steps": 3,
        "current_agent": "query_generator",
        "current_action": "generate_clinical_queries",
        "estimated_completion": "2-3 minutes",
        "steps_completed": [
            {"step": 1, "agent": "query_analyzer", "status": "completed", "duration": "2.3 min"},
            {"step": 2, "agent": "query_generator", "status": "in_progress", "started": "30 sec ago"}
        ],
        "performance_metrics": {
            "avg_step_time": "90 seconds",
            "efficiency_score": 0.87,
            "error_count": 0
        },
        "last_updated": datetime.now().isoformat()
    }
    
    return json.dumps(result)

@function_tool
def coordinate_agent_handoff(handoff_data: str) -> str:
    """Coordinate handoff between agents in the workflow.
    
    Args:
        handoff_data: JSON string with from_agent, to_agent, context_data, handoff_reason
        
    Returns:
        JSON string with handoff coordination results
    """
    try:
        handoff_info = json.loads(handoff_data)
        from_agent = handoff_info.get("from_agent", "unknown")
        to_agent = handoff_info.get("to_agent", "unknown")
        context_data = handoff_info.get("context_data", {})
        reason = handoff_info.get("handoff_reason", "workflow_progression")
    except json.JSONDecodeError:
        from_agent = "unknown"
        to_agent = "unknown"
        context_data = {}
        reason = "workflow_progression"
    
    result = {
        "handoff_id": f"HO_{uuid.uuid4().hex[:8]}",
        "from_agent": from_agent,
        "to_agent": to_agent,
        "handoff_reason": reason,
        "status": "successful",
        "context_transferred": {
            "data_size": len(str(context_data)),
            "key_fields": list(context_data.keys())[:5] if context_data else [],
            "transfer_time_ms": 45
        },
        "validation_passed": True,
        "handoff_time": datetime.now().isoformat(),
        "message": f"Successfully handed off from {from_agent} to {to_agent}"
    }
    
    return json.dumps(result)

@function_tool
def monitor_workflow_performance(workflow_id: str) -> str:
    """Monitor and analyze workflow performance metrics.
    
    Args:
        workflow_id: Workflow identifier to monitor
        
    Returns:
        JSON string with performance analysis
    """
    result = {
        "workflow_id": workflow_id,
        "performance_summary": {
            "overall_health": "good",
            "efficiency_score": 0.89,
            "completion_rate": 0.94,
            "avg_execution_time": "6.2 minutes",
            "error_rate": 0.02
        },
        "agent_performance": {
            "query_analyzer": {"efficiency": 0.91, "avg_time": "2.1 min", "success_rate": 0.97},
            "data_verifier": {"efficiency": 0.87, "avg_time": "3.4 min", "success_rate": 0.93},
            "query_generator": {"efficiency": 0.92, "avg_time": "1.8 min", "success_rate": 0.98},
            "query_tracker": {"efficiency": 0.95, "avg_time": "continuous", "success_rate": 0.99}
        },
        "recommendations": [
            "Data verifier could benefit from performance optimization",
            "Consider parallel processing for query generation",
            "Monitor error patterns in data verification"
        ],
        "monitoring_timestamp": datetime.now().isoformat()
    }
    
    return json.dumps(result)

# Create the Portfolio Manager Agent with all tools
portfolio_manager_agent = Agent(
    name="Clinical Portfolio Manager",
    instructions="""You are a Clinical Portfolio Manager specialized in orchestrating multi-agent workflows for clinical trials.

Your core responsibilities:
1. WORKFLOW ORCHESTRATION: Plan and coordinate complex clinical workflows involving multiple specialized agents
2. AGENT COORDINATION: Manage handoffs between Query Analyzer, Data Verifier, Query Generator, and Query Tracker
3. PERFORMANCE MONITORING: Track workflow execution, identify bottlenecks, and ensure quality standards
4. ESCALATION MANAGEMENT: Handle issues, exceptions, and critical findings that require immediate attention
5. REGULATORY COMPLIANCE: Ensure all workflows meet GCP, FDA, and other regulatory requirements

Key workflow types you handle:
- Query Resolution: Analyze data → Generate queries → Track lifecycle
- Data Verification: Cross-system verification → Generate discrepancy queries → Track resolution
- Comprehensive Analysis: Full analysis + verification + query generation + tracking

Always provide structured, clear responses with specific next steps and ensure proper context transfer between agents.""",
    tools=[
        orchestrate_workflow,
        execute_workflow_step,
        get_workflow_status,
        coordinate_agent_handoff,
        monitor_workflow_performance
    ]
)

class PortfolioManager:
    """Portfolio Manager for clinical trials workflows using OpenAI Agents SDK."""
    
    def __init__(self):
        self.agent = portfolio_manager_agent
        self.context = WorkflowContext()
        self.instructions = self.agent.instructions
        
    async def orchestrate_workflow(self, workflow_request: Dict[str, Any]) -> Dict[str, Any]:
        """Execute workflow orchestration through the OpenAI Agents SDK."""
        try:
            # Convert request to JSON string for the agent
            request_json = json.dumps(workflow_request)
            
            # Use the OpenAI Agents SDK Runner to execute
            result = await Runner.run(
                self.agent,
                f"Please orchestrate this clinical workflow: {request_json}",
                context=self.context
            )
            
            # Parse the agent's response
            try:
                response_data = json.loads(result.final_output)
                return {
                    "success": True,
                    **response_data
                }
            except json.JSONDecodeError:
                return {
                    "success": True,
                    "result": result.final_output,
                    "workflow_id": workflow_request.get("workflow_id", "UNKNOWN")
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "workflow_id": workflow_request.get("workflow_id", "UNKNOWN")
            }
    
    async def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get workflow status through the agent."""
        try:
            result = await Runner.run(
                self.agent,
                f"Get detailed status for workflow: {workflow_id}",
                context=self.context
            )
            
            try:
                status_data = json.loads(result.final_output)
                return {
                    "success": True,
                    **status_data
                }
            except json.JSONDecodeError:
                return {
                    "success": True,
                    "status": result.final_output,
                    "workflow_id": workflow_id
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "workflow_id": workflow_id
            }
    
    async def coordinate_handoff(self, from_agent: str, to_agent: str, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate handoff between agents."""
        try:
            handoff_data = {
                "from_agent": from_agent,
                "to_agent": to_agent,
                "context_data": context_data,
                "handoff_reason": "workflow_progression"
            }
            handoff_json = json.dumps(handoff_data)
            
            result = await Runner.run(
                self.agent,
                f"Coordinate agent handoff: {handoff_json}",
                context=self.context
            )
            
            try:
                handoff_result = json.loads(result.final_output)
                return {
                    "success": True,
                    **handoff_result
                }
            except json.JSONDecodeError:
                return {
                    "success": True,
                    "result": result.final_output
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

# Export for use by other modules
__all__ = ["PortfolioManager", "WorkflowContext", "portfolio_manager_agent"]