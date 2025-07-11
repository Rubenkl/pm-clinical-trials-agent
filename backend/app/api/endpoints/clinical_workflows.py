"""
Clinical workflow endpoints using OpenAI Agents SDK Runner.run() directly.
One endpoint per major workflow type.
"""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional

# OpenAI Agents SDK
from agents import Runner
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.agents_v2.data_verifier import DataVerificationContext, data_verifier_agent
from app.agents_v2.deviation_detector import (
    DeviationDetectionContext,
    deviation_detector_agent,
)

# Import agents and contexts
from app.agents_v2.portfolio_manager import WorkflowContext, portfolio_manager_agent
from app.agents_v2.query_analyzer import QueryAnalysisContext, query_analyzer_agent

router = APIRouter()


class QueryAnalysisRequest(BaseModel):
    """Request for clinical query analysis."""

    query_id: str
    subject_id: str
    query_text: str
    data_points: Optional[List[Dict[str, Any]]] = []


class DataVerificationRequest(BaseModel):
    """Request for EDC vs source data verification."""

    subject_id: str
    visit: str
    edc_data: Dict[str, Any]
    source_data: Dict[str, Any]


class DeviationDetectionRequest(BaseModel):
    """Request for protocol deviation detection."""

    subject_id: str
    visit_data: Dict[str, Any]
    protocol_requirements: Dict[str, Any]


class WorkflowRequest(BaseModel):
    """Request for multi-agent workflows."""

    workflow_type: str  # comprehensive_analysis, query_resolution, data_verification
    subject_id: str
    input_data: Dict[str, Any]


@router.post("/analyze-query")
async def analyze_clinical_query(request: QueryAnalysisRequest):
    """Analyze clinical queries for severity and required actions."""
    try:
        start_time = datetime.now()

        # Create message for Query Analyzer
        message = f"""Analyze this clinical query:
        Query ID: {request.query_id}
        Subject: {request.subject_id}
        Query Text: {request.query_text}
        Data Points: {json.dumps(request.data_points)}
        
        Return JSON with severity, findings, and recommendations."""

        # Run analysis
        context = QueryAnalysisContext()
        result = await Runner.run(query_analyzer_agent, message, context)

        # Parse response
        try:
            response_data = json.loads(result.final_output)
        except:
            response_data = {"analysis": result.final_output}

        return {
            "success": True,
            "query_id": request.query_id,
            "analysis": response_data,
            "execution_time": (datetime.now() - start_time).total_seconds(),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/verify-data")
async def verify_source_data(request: DataVerificationRequest):
    """Verify EDC data against source documents."""
    try:
        start_time = datetime.now()

        # Create message for Data Verifier
        message = f"""Verify source data for:
        Subject: {request.subject_id}
        Visit: {request.visit}
        
        EDC Data: {json.dumps(request.edc_data)}
        Source Data: {json.dumps(request.source_data)}
        
        Return JSON with discrepancies and match percentage."""

        # Run verification
        context = DataVerificationContext()
        result = await Runner.run(data_verifier_agent, message, context)

        # Parse response
        try:
            response_data = json.loads(result.final_output)
        except:
            response_data = {"verification": result.final_output}

        return {
            "success": True,
            "subject_id": request.subject_id,
            "verification": response_data,
            "execution_time": (datetime.now() - start_time).total_seconds(),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/detect-deviations")
async def detect_protocol_deviations(request: DeviationDetectionRequest):
    """Detect protocol compliance issues."""
    try:
        start_time = datetime.now()

        # Create message for Deviation Detector
        message = f"""Check protocol compliance:
        Subject: {request.subject_id}
        Visit Data: {json.dumps(request.visit_data)}
        Protocol Requirements: {json.dumps(request.protocol_requirements)}
        
        Return JSON with deviations and compliance score."""

        # Run detection
        context = DeviationDetectionContext()
        result = await Runner.run(deviation_detector_agent, message, context)

        # Parse response
        try:
            response_data = json.loads(result.final_output)
        except:
            response_data = {"deviations": result.final_output}

        return {
            "success": True,
            "subject_id": request.subject_id,
            "compliance": response_data,
            "execution_time": (datetime.now() - start_time).total_seconds(),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/execute-workflow")
async def execute_clinical_workflow(request: WorkflowRequest):
    """Execute multi-agent clinical workflows."""
    try:
        start_time = datetime.now()

        # Create message for Portfolio Manager
        workflow_descriptions = {
            "comprehensive_analysis": "Complete clinical data analysis with all agents",
            "query_resolution": "Analyze and resolve clinical queries",
            "data_verification": "Verify all data points and generate queries",
        }

        message = f"""Execute {request.workflow_type} workflow:
        Description: {workflow_descriptions.get(request.workflow_type, 'Custom workflow')}
        Subject ID: {request.subject_id}
        Input Data: {json.dumps(request.input_data)}
        
        Coordinate with relevant agents and return comprehensive results."""

        # Run workflow
        context = WorkflowContext()
        result = await Runner.run(portfolio_manager_agent, message, context)

        # Parse response
        try:
            response_data = json.loads(result.final_output)
        except:
            response_data = {"workflow_results": result.final_output}

        return {
            "success": True,
            "workflow_type": request.workflow_type,
            "results": response_data,
            "execution_time": (datetime.now() - start_time).total_seconds(),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def check_workflow_health():
    """Health check for clinical workflow endpoints."""
    return {
        "status": "operational",
        "endpoints": [
            "/analyze-query - Clinical query analysis",
            "/verify-data - EDC vs source verification",
            "/detect-deviations - Protocol compliance",
            "/execute-workflow - Multi-agent workflows",
        ],
        "timestamp": datetime.now().isoformat(),
    }
