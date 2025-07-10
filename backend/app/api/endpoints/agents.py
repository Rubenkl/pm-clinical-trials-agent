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


# DEPRECATED ENDPOINTS NOTICE:
# All agent management endpoints have been removed as they expose internal orchestration.
# Frontend should use the AI-powered endpoints in /queries, /sdv, and /deviations instead.
# 
# Available AI endpoints:
# - POST /api/v1/queries/analyze - AI-powered query analysis  
# - POST /api/v1/sdv/verify - AI-powered data verification
# - POST /api/v1/deviations/detect - AI-powered deviation detection
# - GET /api/v1/dashboard/analytics - Analytics with AI insights
#
# The Portfolio Manager orchestration happens internally and is not exposed via API.