"""API models for agent interactions and responses."""

from pydantic import BaseModel, Field, validator
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum


class AgentType(str, Enum):
    """Available agent types for interaction."""
    
    PORTFOLIO_MANAGER = "portfolio-manager"
    QUERY_ANALYZER = "query-analyzer"
    QUERY_GENERATOR = "query-generator"
    QUERY_TRACKER = "query-tracker"
    SDV_RISK_ASSESSOR = "sdv-risk-assessor"
    DATA_VERIFIER = "data-verifier"
    COMPLIANCE_CHECKER = "compliance-checker"
    PATTERN_DETECTOR = "pattern-detector"


class WorkflowType(str, Enum):
    """Available workflow types."""
    
    CLINICAL_DATA_ANALYSIS = "clinical_data_analysis"
    QUERY_GENERATION = "query_generation"
    DATA_VERIFICATION = "data_verification"
    COMPLIANCE_CHECK = "compliance_check"
    PATTERN_ANALYSIS = "pattern_analysis"
    RISK_ASSESSMENT = "risk_assessment"


# Chat Models
class ChatRequest(BaseModel):
    """Request model for agent chat interactions."""
    
    message: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="Message to send to the agent"
    )
    agent_type: AgentType = Field(
        default=AgentType.PORTFOLIO_MANAGER,
        description="Type of agent to interact with"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata for the request"
    )

    class Config:
        extra = "forbid"  # Prevent extra fields


class ChatResponse(BaseModel):
    """Response model for agent chat interactions."""
    
    success: bool = Field(..., description="Whether the request was successful")
    response: str = Field(..., description="Agent response content")
    agent_id: str = Field(..., description="ID of the agent that processed the request")
    execution_time: float = Field(
        ...,
        ge=0,
        description="Time taken to process the request in seconds"
    )
    error: Optional[str] = Field(
        default=None,
        description="Error message if the request failed"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional response metadata"
    )
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp of the response"
    )


# Workflow Models
class WorkflowExecutionRequest(BaseModel):
    """Request model for workflow execution."""
    
    workflow_id: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Unique identifier for the workflow"
    )
    workflow_type: WorkflowType = Field(
        ...,
        description="Type of workflow to execute"
    )
    description: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Description of the workflow"
    )
    input_data: Dict[str, Any] = Field(
        ...,
        description="Input data for the workflow"
    )
    priority: int = Field(
        default=1,
        ge=1,
        le=10,
        description="Workflow priority (1=highest, 10=lowest)"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional workflow metadata"
    )

    class Config:
        extra = "forbid"


class WorkflowExecutionResponse(BaseModel):
    """Response model for workflow execution."""
    
    success: bool = Field(..., description="Whether the workflow was successful")
    workflow_id: str = Field(..., description="ID of the executed workflow")
    tasks_completed: int = Field(
        ...,
        ge=0,
        description="Number of tasks completed successfully"
    )
    tasks_failed: int = Field(
        default=0,
        ge=0,
        description="Number of tasks that failed"
    )
    execution_time: float = Field(
        ...,
        ge=0,
        description="Total workflow execution time in seconds"
    )
    results: Dict[str, Any] = Field(
        ...,
        description="Workflow execution results"
    )
    error: Optional[str] = Field(
        default=None,
        description="Error message if workflow failed"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional response metadata"
    )
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp of the response"
    )


# Status Models
class AgentStatusResponse(BaseModel):
    """Response model for agent status information."""
    
    agents: Dict[str, Dict[str, Any]] = Field(
        ...,
        description="Status information for each agent"
    )
    total_agents: int = Field(
        ...,
        ge=0,
        description="Total number of registered agents"
    )
    active_agents: int = Field(
        ...,
        ge=0,
        description="Number of currently active agents"
    )
    system_load: Optional[float] = Field(
        default=None,
        ge=0,
        le=100,
        description="Current system load percentage"
    )
    uptime_seconds: Optional[int] = Field(
        default=None,
        ge=0,
        description="System uptime in seconds"
    )
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp of the status check"
    )


# Health Check Models
class HealthCheckResponse(BaseModel):
    """Response model for health check endpoints."""
    
    status: str = Field(
        ...,
        description="Overall health status (healthy/unhealthy/degraded)"
    )
    timestamp: datetime = Field(
        ...,
        description="Timestamp of the health check"
    )
    version: str = Field(
        ...,
        description="API version"
    )
    services: Optional[Dict[str, Dict[str, Any]]] = Field(
        default=None,
        description="Status of individual services"
    )
    details: Optional[str] = Field(
        default=None,
        description="Additional health details"
    )

    @validator('status')
    def validate_status(cls, v):
        """Validate health status values."""
        allowed_statuses = ["healthy", "unhealthy", "degraded"]
        if v not in allowed_statuses:
            raise ValueError(f"Status must be one of: {allowed_statuses}")
        return v


# Error Models
class ErrorResponse(BaseModel):
    """Response model for API errors."""
    
    error: str = Field(..., description="Error type or category")
    message: str = Field(..., description="Human-readable error message")
    status_code: int = Field(
        default=500,
        ge=400,
        le=599,
        description="HTTP status code"
    )
    details: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional error details"
    )
    request_id: Optional[str] = Field(
        default=None,
        description="Request ID for tracking"
    )
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp of the error"
    )


# Workflow Status Models
class WorkflowStatusRequest(BaseModel):
    """Request model for workflow status check."""
    
    workflow_id: str = Field(
        ...,
        min_length=1,
        description="Workflow ID to check status for"
    )


class WorkflowStatusResponse(BaseModel):
    """Response model for workflow status."""
    
    workflow_id: str = Field(..., description="Workflow ID")
    status: str = Field(..., description="Current workflow status")
    created_at: datetime = Field(..., description="Workflow creation timestamp")
    started_at: Optional[datetime] = Field(
        default=None,
        description="Workflow start timestamp"
    )
    completed_at: Optional[datetime] = Field(
        default=None,
        description="Workflow completion timestamp"
    )
    progress: Dict[str, Any] = Field(
        default_factory=dict,
        description="Workflow progress information"
    )
    current_task: Optional[str] = Field(
        default=None,
        description="Currently executing task"
    )


# Agent Health Models
class AgentHealthResponse(BaseModel):
    """Response model for agent health check."""
    
    agent_id: str = Field(..., description="Agent identifier")
    status: str = Field(..., description="Agent health status")
    is_active: bool = Field(..., description="Whether agent is currently active")
    statistics: Dict[str, Any] = Field(
        default_factory=dict,
        description="Agent performance statistics"
    )
    last_activity: Optional[datetime] = Field(
        default=None,
        description="Last activity timestamp"
    )
    error: Optional[str] = Field(
        default=None,
        description="Error message if agent is unhealthy"
    )


# Batch Request Models
class BatchChatRequest(BaseModel):
    """Request model for batch chat operations."""
    
    requests: List[ChatRequest] = Field(
        ...,
        min_items=1,
        max_items=10,
        description="List of chat requests to process"
    )
    batch_id: str = Field(
        ...,
        min_length=1,
        description="Unique identifier for the batch"
    )
    parallel_execution: bool = Field(
        default=True,
        description="Whether to execute requests in parallel"
    )


class BatchChatResponse(BaseModel):
    """Response model for batch chat operations."""
    
    batch_id: str = Field(..., description="Batch identifier")
    responses: List[ChatResponse] = Field(
        ...,
        description="List of chat responses"
    )
    total_requests: int = Field(
        ...,
        ge=0,
        description="Total number of requests in batch"
    )
    successful_requests: int = Field(
        ...,
        ge=0,
        description="Number of successful requests"
    )
    failed_requests: int = Field(
        ...,
        ge=0,
        description="Number of failed requests"
    )
    total_execution_time: float = Field(
        ...,
        ge=0,
        description="Total time to process all requests"
    )