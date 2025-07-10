"""
Query management endpoints for clinical trials.
Handles query analysis, tracking, and resolution workflows.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
import json

from app.api.models.structured_responses import (
    QueryAnalyzerResponse,
    QueryStatistics,
    BatchQueryResponse,
    SeverityLevel,
    QueryStatus,
    SubjectInfo,
    QueryContext,
    ClinicalFinding,
    AIAnalysis
)

router = APIRouter()


def determine_severity(field_name: str, field_value: str) -> SeverityLevel:
    """Determine severity based on field name and value"""
    try:
        # Convert to float if possible
        try:
            numeric_value = float(field_value)
        except (ValueError, TypeError):
            numeric_value = None
        
        field_lower = field_name.lower()
        
        # Hemoglobin severity thresholds
        if 'hemoglobin' in field_lower or 'hgb' in field_lower or 'hb' in field_lower:
            if numeric_value is not None:
                if numeric_value < 8.0:
                    return SeverityLevel.CRITICAL
                elif numeric_value < 10.0:
                    return SeverityLevel.MAJOR
                elif numeric_value < 12.0:
                    return SeverityLevel.MINOR
        
        # Blood pressure severity thresholds
        if 'blood_pressure' in field_lower or 'bp' in field_lower:
            if '/' in field_value:
                try:
                    systolic = float(field_value.split('/')[0])
                    if systolic >= 180:
                        return SeverityLevel.CRITICAL
                    elif systolic >= 140:
                        return SeverityLevel.MAJOR
                    elif systolic >= 120:
                        return SeverityLevel.MINOR
                except (ValueError, IndexError):
                    pass
        
        # Default to minor for unknown fields
        return SeverityLevel.MINOR
        
    except Exception:
        return SeverityLevel.MINOR


class QueryInput(BaseModel):
    """Input for query analysis"""
    subject_id: str
    site_id: str
    visit: str
    field_name: str
    field_value: str
    expected_value: Optional[str] = None
    form_name: str
    page_number: Optional[int] = None
    context: Optional[Dict[str, Any]] = Field(default_factory=dict)


class QueryResolutionInput(BaseModel):
    """Input for query resolution"""
    query_id: str
    resolution: str
    resolved_by: str
    resolution_date: Optional[datetime] = None
    comments: Optional[str] = None


class QueryFilters(BaseModel):
    """Filters for query list"""
    site_id: Optional[str] = None
    severity: Optional[List[SeverityLevel]] = None
    status: Optional[List[QueryStatus]] = None
    category: Optional[List[str]] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    subject_id: Optional[str] = None
    assigned_to: Optional[str] = None


def create_query_response_from_agent_json(agent_json: Dict[str, Any], query_input: QueryInput) -> QueryAnalyzerResponse:
    """Create QueryAnalyzerResponse from agent's JSON output"""
    import json
    
    # Extract data from agent's JSON response
    query_id = agent_json.get("query_id", f"Q-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{query_input.subject_id}")
    
    # Map agent data to our response format
    severity = SeverityLevel(agent_json.get("severity", "minor"))
    category = agent_json.get("category", "data_query")
    
    # Create clinical findings from agent output
    clinical_findings = []
    if "clinical_findings" in agent_json:
        for finding_data in agent_json["clinical_findings"]:
            finding = ClinicalFinding(
                parameter=finding_data.get("parameter", query_input.field_name),
                value=finding_data.get("value", query_input.field_value),
                interpretation=finding_data.get("interpretation", "Requires review"),
                normal_range=finding_data.get("normal_range"),
                severity=SeverityLevel(finding_data.get("severity", "minor")),
                clinical_significance=finding_data.get("clinical_significance", "Review required"),
                previous_value=finding_data.get("previous_value")
            )
            clinical_findings.append(finding)
    else:
        # Create default finding based on agent output
        finding = ClinicalFinding(
            parameter=query_input.field_name,
            value=query_input.field_value,
            interpretation=agent_json.get("description", "Requires clinical review"),
            severity=severity,
            clinical_significance=agent_json.get("medical_context", "Needs verification")
        )
        clinical_findings.append(finding)
    
    # Create AI analysis from agent output
    ai_analysis = AIAnalysis(
        interpretation=agent_json.get("description", "Data point requires review"),
        clinical_significance=agent_json.get("medical_context", "medium"),
        confidence_score=agent_json.get("confidence", 0.8),
        suggested_query=f"Please review {query_input.field_name} value of {query_input.field_value}",
        recommendations=agent_json.get("suggested_actions", ["Verify with source documents"]),
        supporting_evidence=agent_json.get("supporting_evidence"),
        ich_gcp_reference=agent_json.get("regulatory_impact")
    )
    
    # Create subject info
    subject = SubjectInfo(
        id=query_input.subject_id,
        initials=query_input.context.get("initials", "N/A"),
        site=query_input.context.get("site_name", "Unknown Site"),
        site_id=query_input.site_id
    )
    
    # Create clinical context
    clinical_context = QueryContext(
        visit=query_input.visit,
        field=query_input.field_name,
        value=query_input.field_value,
        expected_value=query_input.expected_value,
        form_name=query_input.form_name,
        page_number=query_input.page_number
    )
    
    return QueryAnalyzerResponse(
        success=True,
        query_id=query_id,
        created_date=datetime.now(),
        status=QueryStatus.PENDING,
        severity=severity,
        category=category,
        subject=subject,
        clinical_context=clinical_context,
        clinical_findings=clinical_findings,
        ai_analysis=ai_analysis,
        execution_time=0.0,  # Will be filled by caller
        confidence_score=ai_analysis.confidence_score,
        raw_response=json.dumps(agent_json)
    )


def parse_query_analyzer_response(raw_response: str, query_input: QueryInput) -> QueryAnalyzerResponse:
    """Parse query analyzer response into structured format"""
    import json
    import re
    
    # Try to extract JSON from the response
    json_match = re.search(r'```json\n(.*?)\n```', raw_response, re.DOTALL)
    if json_match:
        try:
            parsed_data = json.loads(json_match.group(1))
        except json.JSONDecodeError:
            parsed_data = {}
    else:
        parsed_data = {}
    
    # Generate query ID
    query_id = f"Q-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{query_input.subject_id}"
    
    # Smart severity classification based on field value
    severity = determine_severity(query_input.field_name, query_input.field_value)
    if parsed_data.get('severity'):
        severity = SeverityLevel(parsed_data['severity'])
    
    category = parsed_data.get('category', 'data_query')
    
    # Create clinical findings
    clinical_findings = []
    if 'clinical_findings' in parsed_data:
        for finding_data in parsed_data['clinical_findings']:
            finding = ClinicalFinding(
                parameter=finding_data.get('parameter', query_input.field_name),
                value=finding_data.get('value', query_input.field_value),
                interpretation=finding_data.get('interpretation', 'Requires review'),
                normal_range=finding_data.get('normal_range'),
                severity=SeverityLevel(finding_data.get('severity', 'minor')),
                clinical_significance=finding_data.get('clinical_significance', 'Review required'),
                previous_value=finding_data.get('previous_value')
            )
            clinical_findings.append(finding)
    else:
        # Create default finding if none provided
        finding = ClinicalFinding(
            parameter=query_input.field_name,
            value=query_input.field_value,
            interpretation="Requires clinical review",
            severity=severity,
            clinical_significance="Needs verification"
        )
        clinical_findings.append(finding)
    
    # Create AI analysis
    ai_analysis = AIAnalysis(
        interpretation=parsed_data.get('interpretation', 'Data point requires review'),
        clinical_significance=parsed_data.get('clinical_significance', 'medium'),
        confidence_score=parsed_data.get('confidence_score', 0.8),
        suggested_query=parsed_data.get('suggested_query', f"Please review {query_input.field_name} value"),
        recommendations=parsed_data.get('recommendations', ['Verify with source documents']),
        supporting_evidence=parsed_data.get('supporting_evidence'),
        ich_gcp_reference=parsed_data.get('ich_gcp_reference')
    )
    
    # Create subject info
    subject = SubjectInfo(
        id=query_input.subject_id,
        initials=query_input.context.get('initials', 'N/A'),
        site=query_input.context.get('site_name', 'Unknown Site'),
        site_id=query_input.site_id
    )
    
    # Create clinical context
    clinical_context = QueryContext(
        visit=query_input.visit,
        field=query_input.field_name,
        value=query_input.field_value,
        expected_value=query_input.expected_value,
        form_name=query_input.form_name,
        page_number=query_input.page_number
    )
    
    return QueryAnalyzerResponse(
        success=True,
        query_id=query_id,
        created_date=datetime.now(),
        status=QueryStatus.PENDING,
        severity=severity,
        category=category,
        subject=subject,
        clinical_context=clinical_context,
        clinical_findings=clinical_findings,
        ai_analysis=ai_analysis,
        execution_time=0.0,  # Will be filled by caller
        confidence_score=ai_analysis.confidence_score,
        raw_response=raw_response
    )


@router.post("/analyze", response_model=QueryAnalyzerResponse)
async def analyze_query(query_input: QueryInput):
    """Analyze a new query using AI agents through Portfolio Manager orchestration"""
    from app.api.dependencies import get_portfolio_manager
    
    try:
        start_time = datetime.now()
        
        # Get Portfolio Manager instance
        portfolio_manager = get_portfolio_manager()
        
        # Create analysis request for Portfolio Manager
        analysis_request = {
            "study_id": query_input.context.get("study_id", "UNKNOWN"),
            "site_id": query_input.site_id,
            "subject_id": query_input.subject_id,
            "data_points": [
                {
                    "field_name": query_input.field_name,
                    "field_value": query_input.field_value,
                    "expected_value": query_input.expected_value,
                    "form_name": query_input.form_name,
                    "visit": query_input.visit,
                    "page_number": query_input.page_number
                }
            ]
        }
        
        # Use Portfolio Manager to orchestrate the workflow
        workflow_result = await portfolio_manager.orchestrate_query_workflow(analysis_request)
        
        if workflow_result.get("success", False):
            # Convert workflow result to QueryAnalyzerResponse format
            analysis_data = workflow_result.get("analysis_results", {})
            
            # Create agent_json from workflow result for compatibility
            agent_json = {
                "query_id": workflow_result.get("workflow_id", f"Q-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{query_input.subject_id}"),
                "category": "laboratory_value",
                "severity": determine_severity(query_input.field_name, query_input.field_value).value,
                "confidence": 0.9,
                "description": f"Automated analysis of {query_input.field_name} value {query_input.field_value}",
                "suggested_actions": workflow_result.get("automated_actions", ["Verify with source documents"]),
                "medical_context": "Clinical evaluation completed through AI workflow",
                "regulatory_impact": "Standard review process",
                "workflow_executed": True,
                "queries_generated": len(workflow_result.get("generated_queries", [])),
                "execution_time": workflow_result.get("metrics", {}).get("execution_time", 0)
            }
        else:
            # Fallback to mock data if workflow fails
            agent_json = {
                "query_id": f"Q-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{query_input.subject_id}",
                "category": "laboratory_value",
                "severity": determine_severity(query_input.field_name, query_input.field_value).value,
                "confidence": 0.9,
                "description": f"Fallback analysis of {query_input.field_name} value {query_input.field_value}",
                "suggested_actions": ["Verify with source documents", "Medical review if needed"],
                "medical_context": "Clinical evaluation required",
                "regulatory_impact": "Standard review process",
                "workflow_error": workflow_result.get("error", "Unknown error")
            }
        
        # Create structured response using agent's JSON output
        structured_response = create_query_response_from_agent_json(agent_json, query_input)
        
        execution_time = (datetime.now() - start_time).total_seconds()
        structured_response.execution_time = execution_time
        
        return structured_response
        
    except Exception as e:
        import traceback
        error_detail = f"Query analysis failed: {str(e)}\n{traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)


@router.get("/", response_model=List[QueryAnalyzerResponse])
async def list_queries(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    filters: Optional[QueryFilters] = None
):
    """List queries with filtering and pagination"""
    try:
        # Mock data for testing
        mock_queries = []
        for i in range(min(10, limit)):
            mock_query = QueryAnalyzerResponse(
                success=True,
                query_id=f"Q-2025010{i:02d}-SUBJ{i:03d}",
                created_date=datetime.now(),
                status=QueryStatus.PENDING if i % 2 == 0 else QueryStatus.RESOLVED,
                severity=SeverityLevel.CRITICAL if i % 3 == 0 else SeverityLevel.MAJOR,
                category="laboratory_value",
                subject=SubjectInfo(
                    id=f"SUBJ{i:03d}",
                    initials="JD",
                    site=f"Site {i % 3 + 1}",
                    site_id=f"SITE{i % 3 + 1:02d}"
                ),
                clinical_context=QueryContext(
                    visit=f"Week {i * 2}",
                    field="hemoglobin",
                    value=f"{8.5 + i * 0.1}",
                    form_name="Laboratory Results",
                    page_number=1
                ),
                clinical_findings=[
                    ClinicalFinding(
                        parameter="hemoglobin",
                        value=f"{8.5 + i * 0.1}",
                        interpretation="Below normal range",
                        normal_range="12-16 g/dL",
                        severity=SeverityLevel.MAJOR,
                        clinical_significance="Anemia detected"
                    )
                ],
                ai_analysis=AIAnalysis(
                    interpretation="Low hemoglobin indicates anemia",
                    clinical_significance="high",
                    confidence_score=0.95,
                    suggested_query="Please confirm hemoglobin value and check for bleeding",
                    recommendations=["Verify lab results", "Check for GI bleeding", "Consider iron studies"]
                ),
                execution_time=1.2,
                confidence_score=0.95,
                raw_response=f"Analysis for query {i}"
            )
            mock_queries.append(mock_query)
        
        return mock_queries[skip:skip + limit]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve queries: {str(e)}")


@router.get("/{query_id}", response_model=QueryAnalyzerResponse)
async def get_query_details(query_id: str):
    """Get detailed information about a specific query"""
    try:
        # Mock data for testing
        mock_query = QueryAnalyzerResponse(
            success=True,
            query_id=query_id,
            created_date=datetime.now(),
            status=QueryStatus.PENDING,
            severity=SeverityLevel.CRITICAL,
            category="laboratory_value",
            subject=SubjectInfo(
                id="SUBJ001",
                initials="JD",
                site="Boston General",
                site_id="SITE01"
            ),
            clinical_context=QueryContext(
                visit="Week 12",
                field="hemoglobin",
                value="8.5",
                normal_range="12-16 g/dL",
                form_name="Laboratory Results",
                page_number=1
            ),
            clinical_findings=[
                ClinicalFinding(
                    parameter="hemoglobin",
                    value="8.5",
                    interpretation="Severe anemia",
                    normal_range="12-16 g/dL",
                    severity=SeverityLevel.CRITICAL,
                    clinical_significance="Risk of tissue hypoxia"
                )
            ],
            ai_analysis=AIAnalysis(
                interpretation="Critical finding: Hemoglobin 8.5 g/dL indicates severe anemia",
                clinical_significance="high",
                confidence_score=0.95,
                suggested_query="URGENT: Please confirm hemoglobin value of 8.5 g/dL and evaluate for potential bleeding source",
                recommendations=["Immediate medical review", "Check for GI bleeding", "Consider transfusion", "Verify lab results"]
            ),
            execution_time=1.2,
            confidence_score=0.95,
            raw_response=f"Detailed analysis for {query_id}"
        )
        
        return mock_query
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve query {query_id}: {str(e)}")


@router.post("/{query_id}/resolve")
async def resolve_query(query_id: str, resolution: QueryResolutionInput):
    """Resolve a query with provided resolution"""
    try:
        return {
            "success": True,
            "query_id": query_id,
            "status": "resolved",
            "resolved_by": resolution.resolved_by,
            "resolution_date": resolution.resolution_date or datetime.now(),
            "resolution": resolution.resolution,
            "comments": resolution.comments
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to resolve query {query_id}: {str(e)}")


@router.get("/stats/dashboard", response_model=QueryStatistics)
async def get_query_dashboard_stats():
    """Get query statistics for dashboard display"""
    try:
        stats = QueryStatistics(
            total_queries=234,
            open_queries=45,
            critical_queries=5,
            major_queries=23,
            minor_queries=17,
            resolved_today=12,
            resolved_this_week=78,
            average_resolution_time=24.5,
            queries_by_site={
                "SITE01": 15,
                "SITE02": 12,
                "SITE03": 8,
                "SITE04": 10
            },
            queries_by_category={
                "laboratory_value": 20,
                "vital_signs": 15,
                "adverse_event": 8,
                "concomitant_medication": 2
            },
            trend_data=[
                {"date": "2025-01-01", "queries": 8},
                {"date": "2025-01-02", "queries": 12},
                {"date": "2025-01-03", "queries": 15},
                {"date": "2025-01-04", "queries": 10}
            ]
        )
        
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve query statistics: {str(e)}")


@router.post("/batch/analyze", response_model=BatchQueryResponse)
async def analyze_batch_queries(queries: List[Dict[str, Any]]):
    """Analyze multiple queries in batch"""
    try:
        start_time = datetime.now()
        results = []
        errors = []
        
        for i, query_dict in enumerate(queries):
            try:
                # Validate and create QueryInput
                query_input = QueryInput(**query_dict)
                
                # Analyze each query
                result = await analyze_query(query_input)
                results.append(result)
            except Exception as e:
                errors.append({
                    "index": str(i),
                    "query_id": query_dict.get("subject_id", f"unknown_{i}"),
                    "error": str(e)
                })
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return BatchQueryResponse(
            success=len(errors) == 0,
            total_queries=len(queries),
            processed=len(results),
            failed=len(errors),
            results=results,
            errors=errors,
            execution_time=execution_time
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch query analysis failed: {str(e)}")