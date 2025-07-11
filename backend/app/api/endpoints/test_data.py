"""Test Data API endpoints for development and testing."""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from app.core.config import Settings, get_settings
from app.services.test_data_service import TestDataService

router = APIRouter()


# Pydantic models for responses
class TestDataStatusResponse(BaseModel):
    """Test data status response model."""

    test_mode_enabled: bool
    current_study: Optional[str]
    available_subjects: List[str]
    available_sites: List[str]
    data_statistics: Dict[str, Any]


class SubjectDataResponse(BaseModel):
    """Subject data response model."""

    subject_id: str
    data_source: str
    data: Dict[str, Any]


class DiscrepancyResponse(BaseModel):
    """Discrepancy response model."""

    subject_id: str
    visit_name: Optional[str]
    discrepancies: List[Dict[str, Any]]


class QueryResponse(BaseModel):
    """Query response model."""

    subject_id: str
    visit_name: Optional[str]
    queries: List[Dict[str, Any]]


class SitePerformanceResponse(BaseModel):
    """Site performance response model."""

    sites: List[Dict[str, Any]]


class QueriesResponse(BaseModel):
    """Queries response model for frontend."""

    queries: List[Dict[str, Any]]
    statistics: Dict[str, Any]


class SDVSessionsResponse(BaseModel):
    """SDV sessions response model."""

    sdv_sessions: List[Dict[str, Any]]
    site_progress: List[Dict[str, Any]]


class ProtocolDeviationsResponse(BaseModel):
    """Protocol deviations response model."""

    deviations: List[Dict[str, Any]]
    compliance_metrics: Dict[str, Any]


class QueryResolutionRequest(BaseModel):
    """Request model for resolving queries."""

    resolution_notes: str
    resolved_by: str


class ProtocolMonitoringResponse(BaseModel):
    """Protocol monitoring response model."""

    monitoring_schedule: List[Dict[str, Any]]
    compliance_alerts: List[Dict[str, Any]]


class DashboardAnalyticsResponse(BaseModel):
    """Dashboard analytics response model."""

    enrollment_trend: List[Dict[str, Any]]
    data_quality_trend: List[Dict[str, Any]]
    recent_activities: List[Dict[str, Any]]


def get_test_data_service(
    settings: Settings = Depends(get_settings),
) -> TestDataService:
    """Dependency to get test data service."""
    return TestDataService(settings)


@router.get("/status", response_model=TestDataStatusResponse)
async def get_test_data_status(
    test_service: TestDataService = Depends(get_test_data_service),
) -> TestDataStatusResponse:
    """Get test data status and statistics."""

    if not test_service.is_test_mode():
        return TestDataStatusResponse(
            test_mode_enabled=False,
            current_study=None,
            available_subjects=[],
            available_sites=[],
            data_statistics={},
        )

    study_info = await test_service.get_study_info()
    available_subjects = test_service.get_available_subjects()
    available_sites = test_service.get_available_sites()

    # Calculate statistics
    subjects_with_discrepancies = await test_service.get_subjects_with_discrepancies()
    site_performance = await test_service.get_site_performance_data()

    statistics = {
        "total_subjects": len(available_subjects),
        "total_sites": len(available_sites),
        "subjects_with_discrepancies": len(subjects_with_discrepancies),
        "total_queries": sum(
            site["metrics"]["total_queries"] for site in site_performance
        ),
        "total_discrepancies": sum(
            site["metrics"]["total_discrepancies"] for site in site_performance
        ),
        "critical_findings": sum(
            site["metrics"]["critical_findings"] for site in site_performance
        ),
    }

    return TestDataStatusResponse(
        test_mode_enabled=True,
        current_study=study_info["protocol_id"] if study_info else None,
        available_subjects=available_subjects,
        available_sites=available_sites,
        data_statistics=statistics,
    )


@router.get("/subjects/{subject_id}", response_model=SubjectDataResponse)
async def get_subject_data(
    subject_id: str,
    data_source: str = Query(
        default="edc", description="Data source: edc, source, or both"
    ),
    test_service: TestDataService = Depends(get_test_data_service),
) -> SubjectDataResponse:
    """Get subject data from specified source."""

    if not test_service.is_test_mode():
        raise HTTPException(status_code=404, detail="Test data mode not enabled")

    if data_source not in ["edc", "source", "both"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid data_source. Must be 'edc', 'source', or 'both'",
        )

    subject_data = await test_service.get_subject_data(subject_id, data_source)

    if not subject_data:
        raise HTTPException(status_code=404, detail=f"Subject {subject_id} not found")

    return SubjectDataResponse(
        subject_id=subject_id, data_source=data_source, data=subject_data
    )


@router.get("/subjects/{subject_id}/visits/{visit_name}")
async def get_visit_data(
    subject_id: str,
    visit_name: str,
    data_source: str = Query(
        default="edc", description="Data source: edc, source, or both"
    ),
    test_service: TestDataService = Depends(get_test_data_service),
) -> Dict[str, Any]:
    """Get specific visit data."""

    if not test_service.is_test_mode():
        raise HTTPException(status_code=404, detail="Test data mode not enabled")

    if data_source not in ["edc", "source", "both"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid data_source. Must be 'edc', 'source', or 'both'",
        )

    visit_data = await test_service.get_visit_data(subject_id, visit_name, data_source)

    if not visit_data:
        raise HTTPException(
            status_code=404,
            detail=f"Visit {visit_name} for subject {subject_id} not found",
        )

    return visit_data


@router.get("/subjects/{subject_id}/discrepancies", response_model=DiscrepancyResponse)
async def get_subject_discrepancies(
    subject_id: str,
    visit_name: Optional[str] = Query(
        default=None, description="Optional visit name filter"
    ),
    severity: Optional[str] = Query(
        default=None, description="Optional severity filter"
    ),
    test_service: TestDataService = Depends(get_test_data_service),
) -> DiscrepancyResponse:
    """Get known discrepancies for a subject."""

    if not test_service.is_test_mode():
        raise HTTPException(status_code=404, detail="Test data mode not enabled")

    discrepancies = await test_service.get_discrepancies(subject_id, visit_name)

    # Apply severity filter if specified
    if severity:
        discrepancies = [d for d in discrepancies if d.get("severity") == severity]

    return DiscrepancyResponse(
        subject_id=subject_id, visit_name=visit_name, discrepancies=discrepancies
    )


@router.get("/subjects/{subject_id}/queries", response_model=QueryResponse)
async def get_subject_queries(
    subject_id: str,
    visit_name: Optional[str] = Query(
        default=None, description="Optional visit name filter"
    ),
    status: Optional[str] = Query(default=None, description="Optional status filter"),
    test_service: TestDataService = Depends(get_test_data_service),
) -> QueryResponse:
    """Get existing queries for a subject."""

    if not test_service.is_test_mode():
        raise HTTPException(status_code=404, detail="Test data mode not enabled")

    queries = await test_service.get_queries(subject_id, visit_name)

    # Apply status filter if specified
    if status:
        queries = [q for q in queries if q.get("status") == status]

    return QueryResponse(subject_id=subject_id, visit_name=visit_name, queries=queries)


@router.get("/discrepancies", response_model=List[Dict[str, Any]])
async def get_all_discrepancies(
    severity: Optional[str] = Query(
        default=None, description="Optional severity filter"
    ),
    test_service: TestDataService = Depends(get_test_data_service),
) -> List[Dict[str, Any]]:
    """Get all subjects with discrepancies."""

    if not test_service.is_test_mode():
        raise HTTPException(status_code=404, detail="Test data mode not enabled")

    return await test_service.get_subjects_with_discrepancies(severity)


@router.get("/sites/performance", response_model=SitePerformanceResponse)
async def get_site_performance(
    test_service: TestDataService = Depends(get_test_data_service),
) -> SitePerformanceResponse:
    """Get site performance data."""

    if not test_service.is_test_mode():
        raise HTTPException(status_code=404, detail="Test data mode not enabled")

    sites = await test_service.get_site_performance_data()

    return SitePerformanceResponse(sites=sites)


@router.get("/sites/{site_id}")
async def get_site_data(
    site_id: str, test_service: TestDataService = Depends(get_test_data_service)
) -> Dict[str, Any]:
    """Get site information."""

    if not test_service.is_test_mode():
        raise HTTPException(status_code=404, detail="Test data mode not enabled")

    site_data = await test_service.get_site_data(site_id)

    if not site_data:
        raise HTTPException(status_code=404, detail=f"Site {site_id} not found")

    return site_data


@router.get("/study-info")
async def get_study_info(
    test_service: TestDataService = Depends(get_test_data_service),
) -> Dict[str, Any]:
    """Get current study information."""

    if not test_service.is_test_mode():
        raise HTTPException(status_code=404, detail="Test data mode not enabled")

    study_info = await test_service.get_study_info()

    if not study_info:
        raise HTTPException(status_code=404, detail="Study information not available")

    return study_info


@router.post("/regenerate")
async def regenerate_test_data(
    preset_name: Optional[str] = Query(
        default=None, description="Optional preset name"
    ),
    test_service: TestDataService = Depends(get_test_data_service),
) -> Dict[str, Any]:
    """Regenerate test data with optional different preset."""

    if not test_service.is_test_mode():
        raise HTTPException(status_code=404, detail="Test data mode not enabled")

    success = await test_service.regenerate_test_data(preset_name)

    if not success:
        raise HTTPException(status_code=500, detail="Failed to regenerate test data")

    return {
        "message": "Test data regenerated successfully",
        "preset_used": preset_name or "current preset",
    }


# Example endpoint for agent testing
@router.get("/agent-test-data")
async def get_agent_test_data(
    test_service: TestDataService = Depends(get_test_data_service),
) -> Dict[str, Any]:
    """Get comprehensive test data for agent testing."""

    if not test_service.is_test_mode():
        raise HTTPException(status_code=404, detail="Test data mode not enabled")

    from app.services.test_data_service import get_test_data_for_agents

    return await get_test_data_for_agents(test_service)


# FRONTEND DEV FEEDBACK - Missing endpoints for eliminating mock data


# Helper function for agent initialization and error handling
async def _initialize_agent_with_fallback(agent_class, operation_name: str):
    """Initialize agent with consistent error handling."""
    try:
        return agent_class()
    except Exception as e:
        # Log error but don't fail - use fallback processing
        print(f"Warning: {operation_name} agent initialization failed: {e}")
        return None


# Helper function to generate analysis data efficiently
def _generate_analysis_data(subjects: list, limit: int = 50):
    """Generate analysis data for subjects efficiently."""
    analysis_templates = [
        {
            "category": "data_discrepancy",
            "field_name": "hemoglobin",
            "edc_value": "8.5",
            "source_value": "12.3",
            "description": "Discrepancy between EDC and source document values",
        },
        {
            "category": "missing_data",
            "field_name": "vital_signs.systolic_bp",
            "reason": "regulatory compliance",
            "description": "Missing required vital signs data",
        },
    ]

    analyses = []
    for subject_id in subjects[:limit]:
        subject_hash = hash(subject_id)
        template = analysis_templates[subject_hash % len(analysis_templates)]

        analysis = {
            "subject_id": subject_id,
            "site_name": f"Site {subject_id[-3:]}",
            "visit": f"Week_{(subject_hash % 12) + 1}",
            "visit_date": "2025-01-09",
            "severity": (
                "critical"
                if subject_hash % 5 == 0
                else "major" if subject_hash % 3 == 0 else "minor"
            ),
            **template,
        }
        analyses.append(analysis)

        # Add second analysis for some subjects
        if subject_hash % 2 == 0:
            second_template = analysis_templates[
                (subject_hash + 1) % len(analysis_templates)
            ]
            analyses.append({**analysis, **second_template})

    return analyses


# Helper function to format queries efficiently
def _format_queries_for_frontend(queries: list, analyses: list):
    """Format agent queries for frontend consumption."""
    formatted_queries = []

    for i, query in enumerate(queries):
        analysis = analyses[i] if i < len(analyses) else analyses[0]

        formatted_query = {
            "query_id": query.get("query_id", f"QRY-2025-{i+1:04d}"),
            "subject_id": analysis["subject_id"],
            "site_id": analysis["site_name"].replace("Site ", "SITE_"),
            "query_type": (
                "data_clarification"
                if analysis["category"] == "data_discrepancy"
                else "source_verification"
            ),
            "field": analysis.get("field_name", "unknown_field"),
            "severity": query.get("priority", analysis.get("severity", "medium")),
            "status": "open" if query.get("priority") == "high" else "pending",
            "priority": query.get("priority", "medium"),
            "assigned_to": (
                "site_coordinator"
                if query.get("priority") == "high"
                else "data_manager"
            ),
            "created_date": query.get("generated_at", "2025-01-09T10:00:00"),
            "due_date": "2025-01-13T10:00:00",
            "last_modified": query.get("generated_at", "2025-01-09T10:00:00"),
            "description": query.get("query_text", "Query generated by agent")[:100]
            + "...",
            "current_value": analysis.get("edc_value", "N/A"),
            "expected_range": analysis.get("source_value", "N/A"),
            "source_document": f"{analysis.get('field_name', 'unknown')}_form",
            "visit": analysis.get("visit", "Week_1"),
            "resolution_notes": None,
            "escalation_level": 1 if query.get("priority") == "high" else 0,
        }

        formatted_queries.append(formatted_query)

    return formatted_queries


# Helper function to calculate statistics fallback
def _calculate_query_statistics(queries: list, sites: list):
    """Calculate query statistics efficiently."""
    total_queries = len(queries)

    # Use list comprehensions for efficient counting
    open_queries = sum(1 for q in queries if q["status"] == "open")
    overdue_queries = sum(
        1
        for q in queries
        if q["due_date"] < "2025-01-10T00:00:00" and q["status"] != "resolved"
    )
    critical_queries = sum(1 for q in queries if q["severity"] == "critical")

    # Count by categories using dictionary comprehensions
    status_counts = {
        status: sum(1 for q in queries if q["status"] == status)
        for status in ["open", "pending", "resolved"]
    }
    severity_counts = {
        severity: sum(1 for q in queries if q["severity"] == severity)
        for severity in ["critical", "major", "minor"]
    }
    site_counts = {
        site: sum(1 for q in queries if q["site_id"] == site) for site in sites
    }

    return {
        "total_queries": total_queries,
        "open_queries": open_queries,
        "overdue_queries": overdue_queries,
        "critical_queries": critical_queries,
        "queries_by_status": status_counts,
        "queries_by_severity": severity_counts,
        "queries_by_site": site_counts,
    }


@router.get("/queries", response_model=QueriesResponse)
async def get_all_queries(
    test_service: TestDataService = Depends(get_test_data_service),
) -> QueriesResponse:
    """Get all queries with statistics using Query Generator agent."""

    if not test_service.is_test_mode():
        raise HTTPException(status_code=404, detail="Test data mode not enabled")

    # Import agents
    from app.agents_v2.query_generator import QueryGenerator
    from app.agents_v2.query_tracker import QueryTracker

    # Initialize agents with fallback handling
    query_generator = await _initialize_agent_with_fallback(
        QueryGenerator, "Query Generator"
    )
    query_tracker = await _initialize_agent_with_fallback(QueryTracker, "Query Tracker")

    # Get subject data and generate analysis data efficiently
    subjects = test_service.get_available_subjects()
    sites = ["SITE_001", "SITE_002", "SITE_003"]
    analyses = _generate_analysis_data(subjects, 50)

    # Generate queries using agent if available
    if query_generator:
        try:
            queries = await query_generator.generate_batch_queries(analyses)
        except Exception as e:
            print(f"Query generation failed: {e}")
            queries = []  # Use empty list for fallback formatting
    else:
        queries = []  # Use empty list for fallback formatting

    # Format queries for frontend
    formatted_queries = _format_queries_for_frontend(queries, analyses)

    # Get statistics from Query Tracker agent if available
    statistics = None
    if query_tracker:
        try:
            statistics_result = await query_tracker.generate_performance_metrics(
                {
                    "queries": formatted_queries,
                    "sites": sites,
                    "analysis_type": "comprehensive",
                }
            )
            if statistics_result.get("success"):
                statistics = statistics_result.get("statistics", {})
        except Exception as e:
            print(f"Statistics generation failed: {e}")

    # Use fallback statistics if agent failed
    if not statistics:
        statistics = _calculate_query_statistics(formatted_queries, sites)

    return QueriesResponse(queries=formatted_queries, statistics=statistics)


@router.put("/queries/{query_id}/resolve")
async def resolve_query(
    query_id: str,
    resolution_request: QueryResolutionRequest,
    test_service: TestDataService = Depends(get_test_data_service),
) -> Dict[str, Any]:
    """Resolve a specific query using Query Tracker agent."""

    if not test_service.is_test_mode():
        raise HTTPException(status_code=404, detail="Test data mode not enabled")

    from datetime import datetime

    from app.agents_v2.query_tracker import QueryTracker

    # Initialize Query Tracker with fallback handling
    query_tracker = await _initialize_agent_with_fallback(QueryTracker, "Query Tracker")

    # Prepare resolution data
    resolution_data = {
        "query_id": query_id,
        "resolution_notes": resolution_request.resolution_notes,
        "resolved_by": resolution_request.resolved_by,
        "resolution_date": datetime.now().isoformat(),
    }

    # Base response structure
    base_response = {
        "success": True,
        "query_id": query_id,
        "resolution_notes": resolution_request.resolution_notes,
        "resolved_by": resolution_request.resolved_by,
        "resolved_date": resolution_data["resolution_date"],
        "status": "resolved",
    }

    # Use Query Tracker agent if available
    if query_tracker:
        try:
            resolution_result = await query_tracker.resolve_query(resolution_data)
            if resolution_result.get("success"):
                base_response["agent_metadata"] = resolution_result.get("metadata", {})
        except Exception as e:
            print(f"Query resolution failed: {e}")
            # Continue with base response

    return base_response


# Helper function to generate SDV verification contexts
def _generate_sdv_verification_contexts(
    subjects: list, sites_data: list, limit: int = 20
):
    """Generate verification contexts for SDV sessions efficiently."""
    verification_contexts = []

    for subject_id in subjects[:limit]:
        site_data = sites_data[hash(subject_id) % len(sites_data)]
        subject_hash = hash(subject_id)

        # Generate realistic mock data with variations
        edc_data = {
            "vital_signs": {
                "systolic_bp": 140 + (subject_hash % 20),
                "diastolic_bp": 90 + (subject_hash % 10),
                "heart_rate": 72 + (subject_hash % 15),
            },
            "laboratory": {
                "hemoglobin": 12.5 + (subject_hash % 30) / 10,
                "creatinine": 1.2 + (subject_hash % 20) / 100,
                "bnp": 250 + (subject_hash % 100),
            },
            "demographics": {
                "age": 45 + (subject_hash % 25),
                "gender": "F" if subject_hash % 2 == 0 else "M",
                "weight": 70 + (subject_hash % 40),
            },
        }

        # Create source data with small variations for discrepancies
        source_data = {
            "vital_signs": {
                "systolic_bp": edc_data["vital_signs"]["systolic_bp"]
                + (2 if subject_hash % 5 == 0 else 0),
                "diastolic_bp": edc_data["vital_signs"]["diastolic_bp"]
                + (-2 if subject_hash % 7 == 0 else 0),
                "heart_rate": edc_data["vital_signs"]["heart_rate"]
                + (1 if subject_hash % 3 == 0 else 0),
            },
            "laboratory": {
                "hemoglobin": edc_data["laboratory"]["hemoglobin"]
                + (-0.2 if subject_hash % 4 == 0 else 0),
                "creatinine": edc_data["laboratory"]["creatinine"]
                + (0.05 if subject_hash % 6 == 0 else 0),
                "bnp": edc_data["laboratory"]["bnp"]
                + (-2 if subject_hash % 8 == 0 else 0),
            },
            "demographics": edc_data["demographics"],  # Demographics usually match
        }

        verification_contexts.append(
            {
                "subject_id": subject_id,
                "site_id": site_data["site_id"],
                "monitor_name": site_data["monitor"],
                "edc_data": edc_data,
                "source_data": source_data,
                "verification_type": "routine_sdv",
            }
        )

    return verification_contexts


# Helper function to process SDV sessions concurrently
async def _process_sdv_sessions(verification_contexts: list, data_verifier):
    """Process SDV sessions with improved error handling."""
    import asyncio

    async def process_single_session(i: int, context: dict):
        try:
            if data_verifier:
                verification_result = await data_verifier.cross_system_verification(
                    context["edc_data"], context["source_data"]
                )
                discrepancies = verification_result.get("discrepancies", [])
            else:
                # Fallback: simulate discrepancies based on data differences
                discrepancies = []
                for category in ["vital_signs", "laboratory"]:
                    if (
                        category in context["edc_data"]
                        and category in context["source_data"]
                    ):
                        for field, edc_value in context["edc_data"][category].items():
                            source_value = context["source_data"][category].get(field)
                            if source_value != edc_value:
                                discrepancies.append(
                                    {
                                        "field": field,
                                        "edc_value": edc_value,
                                        "source_value": source_value,
                                        "severity": "minor",
                                    }
                                )

            critical_findings = sum(
                1 for d in discrepancies if d.get("severity") == "critical"
            )

            return {
                "session_id": f"SDV-2025-{i+1:04d}",
                "subject_id": context["subject_id"],
                "site_id": context["site_id"],
                "monitor_name": context["monitor_name"],
                "visit_date": "2025-01-09",
                "status": "completed" if len(discrepancies) < 3 else "in_progress",
                "verification_progress": 100 if len(discrepancies) < 3 else 85,
                "total_fields": 15,
                "verified_fields": 15 if len(discrepancies) < 3 else 13,
                "discrepancies_found": len(discrepancies),
                "critical_findings": critical_findings,
                "session_notes": f"Agent verification completed - {len(discrepancies)} discrepancies found",
                "source_documents_reviewed": [
                    "medical_history_form",
                    "vital_signs_log",
                    "laboratory_results",
                    "adverse_events_log",
                ],
                "next_monitoring_date": "2025-02-09",
            }
        except Exception as e:
            print(
                f"SDV session processing failed for {context.get('subject_id', 'unknown')}: {e}"
            )
            # Return minimal session data
            return {
                "session_id": f"SDV-2025-{i+1:04d}",
                "subject_id": context["subject_id"],
                "site_id": context["site_id"],
                "monitor_name": context["monitor_name"],
                "visit_date": "2025-01-09",
                "status": "pending",
                "verification_progress": 0,
                "total_fields": 15,
                "verified_fields": 0,
                "discrepancies_found": 0,
                "critical_findings": 0,
                "session_notes": "Processing failed - manual review required",
                "source_documents_reviewed": [],
                "next_monitoring_date": "2025-02-09",
            }

    # Process sessions concurrently for better performance
    tasks = [
        process_single_session(i, context)
        for i, context in enumerate(verification_contexts)
    ]
    return await asyncio.gather(*tasks)


# Helper function to calculate site progress efficiently
def _calculate_site_progress(sites_data: list, subjects: list, sdv_sessions: list):
    """Calculate site progress from SDV session data."""
    site_progress = []

    for site_data in sites_data:
        site_subjects = [
            s for s in subjects if hash(s) % 3 == int(site_data["site_id"][-1]) - 1
        ][:17]
        site_sessions = [
            s for s in sdv_sessions if s["site_id"] == site_data["site_id"]
        ]
        verified_count = sum(1 for s in site_sessions if s["status"] == "completed")

        progress = {
            "site_id": site_data["site_id"],
            "site_name": site_data["site_name"],
            "total_subjects": len(site_subjects),
            "subjects_verified": verified_count,
            "verification_percentage": (
                round((verified_count / len(site_subjects)) * 100, 1)
                if site_subjects
                else 0
            ),
            "pending_subjects": len(site_subjects) - verified_count,
            "last_visit": "2025-01-09",
            "monitor_assigned": site_data["monitor"],
            "risk_level": (
                "low" if verified_count >= len(site_subjects) * 0.8 else "medium"
            ),
        }
        site_progress.append(progress)

    return site_progress


@router.get("/sdv/sessions", response_model=SDVSessionsResponse)
async def get_sdv_sessions(
    test_service: TestDataService = Depends(get_test_data_service),
) -> SDVSessionsResponse:
    """Get SDV sessions and site progress using Data Verifier agent."""

    if not test_service.is_test_mode():
        raise HTTPException(status_code=404, detail="Test data mode not enabled")

    from app.agents_v2.data_verifier import DataVerifier

    # Initialize agent with fallback handling
    data_verifier = await _initialize_agent_with_fallback(DataVerifier, "Data Verifier")

    # Get subject data and site information
    subjects = test_service.get_available_subjects()
    sites_data = [
        {
            "site_id": "SITE_001",
            "site_name": "Metropolitan Medical Center",
            "monitor": "Dr. Michael Chen",
        },
        {
            "site_id": "SITE_002",
            "site_name": "Regional Heart Institute",
            "monitor": "Lisa Rodriguez",
        },
        {
            "site_id": "SITE_003",
            "site_name": "University Cardiology Center",
            "monitor": "Dr. Sarah Kim",
        },
    ]

    # Generate verification contexts efficiently
    verification_contexts = _generate_sdv_verification_contexts(
        subjects, sites_data, 20
    )

    # Process SDV sessions with improved error handling
    sdv_sessions = await _process_sdv_sessions(verification_contexts, data_verifier)

    # Calculate site progress efficiently
    site_progress = _calculate_site_progress(sites_data, subjects, sdv_sessions)

    return SDVSessionsResponse(sdv_sessions=sdv_sessions, site_progress=site_progress)


@router.get("/protocol/deviations", response_model=ProtocolDeviationsResponse)
async def get_protocol_deviations(
    test_service: TestDataService = Depends(get_test_data_service),
) -> ProtocolDeviationsResponse:
    """Get protocol deviations and compliance metrics with static test data."""

    if not test_service.is_test_mode():
        raise HTTPException(status_code=404, detail="Test data mode not enabled")

    # Generate realistic static protocol deviations (no AI agent calls)
    deviations = [
        {
            "deviation_id": "DEV-2025-0001",
            "subject_id": "CARD001",
            "site_id": "SITE_001",
            "deviation_type": "inclusion_criteria",
            "severity": "major",
            "status": "under_review",
            "detected_date": "2025-01-09T10:00:00",
            "reported_date": "2025-01-09T12:00:00",
            "description": "Subject age 17 years does not meet minimum inclusion criteria (18 years)",
            "protocol_section": "Section 4.1 - Inclusion Criteria",
            "impact_assessment": "high_regulatory_risk",
            "capa_required": True,
            "capa_due_date": "2025-01-23T10:00:00",
            "root_cause": "data_entry_error",
            "corrective_action": "Re-verify subject eligibility documentation",
            "preventive_action": "Enhanced training on inclusion criteria verification",
        },
        {
            "deviation_id": "DEV-2025-0002",
            "subject_id": "CARD002", 
            "site_id": "SITE_001",
            "deviation_type": "visit_window",
            "severity": "minor",
            "status": "resolved",
            "detected_date": "2025-01-08T14:30:00",
            "reported_date": "2025-01-08T16:00:00",
            "description": "Week 4 visit conducted on Day 29 (outside 21-35 day window)",
            "protocol_section": "Section 5.2 - Visit Schedule",
            "impact_assessment": "low_regulatory_risk",
            "capa_required": False,
            "capa_due_date": None,
            "investigator": "Dr. Site 001 Investigator",
            "root_cause": "scheduling_conflict",
            "corrective_action": "Visit rescheduled within window",
            "preventive_action": "Improved scheduling coordination",
        },
        {
            "deviation_id": "DEV-2025-0003",
            "subject_id": "CARD003",
            "site_id": "SITE_002", 
            "deviation_type": "procedure_violation",
            "severity": "major",
            "status": "under_review",
            "detected_date": "2025-01-07T11:15:00",
            "reported_date": "2025-01-07T13:45:00",
            "description": "Required ECG not performed at baseline visit",
            "protocol_section": "Section 6.3 - Required Assessments",
            "impact_assessment": "medium_regulatory_risk",
            "capa_required": True,
            "capa_due_date": "2025-01-21T10:00:00",
            "investigator": "Dr. Site 002 Investigator",
            "root_cause": "procedure_oversight",
            "corrective_action": "ECG completed within 24 hours",
            "preventive_action": "Enhanced visit checklist implementation",
        },
    ]

    # Static compliance metrics
    compliance_metrics = {
        "overall_compliance_rate": 87.3,
        "active_deviations": 2,
        "resolved_deviations": 1,
        "deviations_by_type": {
            "inclusion_criteria": 1,
            "visit_window": 1, 
            "procedure_violation": 1
        },
        "deviations_by_severity": {
            "major": 2,
            "minor": 1
        },
        "risk_score": "medium",
        "trend": "stable",
    }

    return ProtocolDeviationsResponse(
        deviations=deviations, compliance_metrics=compliance_metrics
    )


@router.post("/sdv/sessions")
async def create_sdv_session(
    session_data: Dict[str, Any],
    test_service: TestDataService = Depends(get_test_data_service),
) -> Dict[str, Any]:
    """Create a new SDV session using Data Verifier agent."""

    if not test_service.is_test_mode():
        raise HTTPException(status_code=404, detail="Test data mode not enabled")

    # Import Data Verifier agent
    from datetime import datetime

    from app.agents_v2.data_verifier import DataVerifier

    # Initialize agent
    data_verifier = DataVerifier()

    # Generate session ID
    session_id = f"SDV-2025-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    # Create verification context for the agent
    verification_context = {
        "session_id": session_id,
        "subject_id": session_data.get("subject_id"),
        "site_id": session_data.get("site_id"),
        "monitor_name": session_data.get("monitor_name"),
        "session_type": "planned_verification",
        "verification_scope": [
            "vital_signs",
            "laboratory",
            "demographics",
            "adverse_events",
        ],
    }

    # Use Data Verifier agent to set up the session
    session_setup_result = await data_verifier.setup_verification_session(
        verification_context
    )

    # Parse agent response
    success = session_setup_result.get("success", True)
    session_metadata = session_setup_result.get("session_metadata", {})

    if not success:
        raise HTTPException(status_code=500, detail="Failed to create SDV session")

    return {
        "success": True,
        "session_id": session_id,
        "subject_id": session_data.get("subject_id"),
        "site_id": session_data.get("site_id"),
        "monitor_name": session_data.get("monitor_name"),
        "status": "planned",
        "created_date": datetime.now().isoformat(),
        "verification_scope": session_metadata.get(
            "verification_scope", ["vital_signs", "laboratory"]
        ),
        "estimated_duration": session_metadata.get("estimated_duration", "2 hours"),
        "priority": session_metadata.get("priority", "medium"),
    }


@router.get("/protocol/monitoring", response_model=ProtocolMonitoringResponse)
async def get_protocol_monitoring(
    test_service: TestDataService = Depends(get_test_data_service),
) -> ProtocolMonitoringResponse:
    """Get protocol monitoring schedule and compliance alerts using Portfolio Manager."""

    if not test_service.is_test_mode():
        raise HTTPException(status_code=404, detail="Test data mode not enabled")

    # Import Portfolio Manager agent
    from app.agents_v2.portfolio_manager import PortfolioManager

    # Initialize Portfolio Manager for orchestration
    portfolio_manager = PortfolioManager()

    # Get subjects data for monitoring context
    subjects = test_service.get_available_subjects()
    sites = ["SITE_001", "SITE_002", "SITE_003"]

    # Create monitoring workflow request
    monitoring_request = {
        "workflow_type": "protocol_monitoring",
        "sites": sites,
        "total_subjects": len(subjects),
        "time_period": "current_month",
        "monitoring_scope": ["schedule", "compliance_alerts", "site_performance"],
    }

    # Use Portfolio Manager to orchestrate monitoring workflow
    monitoring_result = await portfolio_manager.orchestrate_monitoring_workflow(
        monitoring_request
    )

    # Use agent result if available, otherwise fallback
    if monitoring_result.get("success"):
        return ProtocolMonitoringResponse(
            monitoring_schedule=monitoring_result.get("monitoring_schedule", []),
            compliance_alerts=monitoring_result.get("compliance_alerts", []),
        )
    else:
        # Fallback to basic monitoring data
        from datetime import datetime, timedelta

        # Basic monitoring schedule
        monitoring_schedule = [
            {
                "site_id": "SITE_001",
                "site_name": "Metropolitan Medical Center",
                "next_visit_date": (datetime.now() + timedelta(days=10)).strftime(
                    "%Y-%m-%d"
                ),
                "visit_type": "routine_monitoring",
                "monitor_assigned": "Dr. Michael Chen",
                "subjects_to_review": 5,
                "priority_items": ["adverse_event_follow_up", "source_verification"],
                "estimated_duration": "2 days",
            }
        ]

        # Basic compliance alerts
        compliance_alerts = [
            {
                "alert_id": "ALERT-2025-001",
                "type": "enrollment_rate_decline",
                "severity": "medium",
                "site_affected": "SITE_001",
                "description": "Enrollment rate below target",
                "action_required": "investigator_meeting",
                "due_date": (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d"),
                "responsible_person": "Dr. Michael Chen",
            }
        ]

        return ProtocolMonitoringResponse(
            monitoring_schedule=monitoring_schedule, compliance_alerts=compliance_alerts
        )


@router.get("/analytics/dashboard", response_model=DashboardAnalyticsResponse)
async def get_dashboard_analytics(
    test_service: TestDataService = Depends(get_test_data_service),
) -> DashboardAnalyticsResponse:
    """Get dashboard analytics and trends using Analytics Agent."""

    if not test_service.is_test_mode():
        raise HTTPException(status_code=404, detail="Test data mode not enabled")

    # Import Analytics Agent
    from app.agents_v2.analytics_agent import AnalyticsAgent

    # Initialize Analytics Agent
    analytics_agent = AnalyticsAgent()

    # Get subjects data for analytics context
    subjects = test_service.get_available_subjects()
    sites = ["SITE_001", "SITE_002", "SITE_003"]

    # Generate analytics using agent
    analytics_request = {
        "time_period": "30_days",
        "sites": sites,
        "total_subjects": len(subjects),
        "activity_limit": 10,
        "metrics": ["enrollment", "data_quality", "activities"],
    }

    # Prepare comprehensive trial data for AI analysis
    trial_data = {
        "study_id": "CARD-2025-001",
        "enrollment": {
            "target": 300,
            "actual": len(subjects),
            "rate_per_month": 12.5,
            "months_active": 2,
            "site_performance": {
                site: {
                    "enrolled": len([s for s in subjects if hash(s + site) % 3 == i]),
                    "screen_fail_rate": 0.15 + (i * 0.1),
                }
                for i, site in enumerate(sites)
            },
        },
        "data_quality": {
            "query_rate": 0.085,
            "critical_findings": 3,
            "protocol_deviations": 8,
            "missing_data_rate": 0.032,
        },
        "safety": {
            "adverse_events": 12,
            "serious_adverse_events": 2,
            "deaths": 0,
            "discontinuations": 3,
        },
        "timeline": {
            "start_date": "2024-12-01",
            "planned_end": "2025-11-30",
            "current_date": datetime.now().strftime("%Y-%m-%d"),
        },
    }

    # Call AI-powered Analytics Agent to generate insights
    ai_analytics_result = await analytics_agent.generate_analytics_insights_ai(
        trial_data
    )

    # Check if AI analysis was successful
    if (
        ai_analytics_result.get("ai_powered")
        and "analytics_insights" in ai_analytics_result
    ):
        # Extract insights from AI analysis
        insights = ai_analytics_result.get("analytics_insights", {})
        enrollment_analysis = insights.get("enrollment_analysis", {})
        quality_analysis = insights.get("quality_analysis", {})

        # Generate trend data based on AI insights
        enrollment_trend = []
        data_quality_trend = []

        # Create enrollment trend based on AI predictions
        base_date = datetime.now() - timedelta(days=30)
        for i in range(5):
            date = base_date + timedelta(days=i * 7)
            enrollment_trend.append(
                {
                    "date": date.strftime("%Y-%m-%d"),
                    "cumulative": int(len(subjects) * (0.7 + i * 0.075)),
                    "weekly": int(12.5 / 4),  # Weekly rate from monthly
                }
            )

        # Create data quality trend
        for i in range(5):
            date = base_date + timedelta(days=i * 7)
            data_quality_trend.append(
                {
                    "date": date.strftime("%Y-%m-%d"),
                    "percentage": round(94.0 + (i * 0.5), 1),
                }
            )

        # Create recent activities with AI insights
        recent_activities = [
            {
                "activity_id": f"ACT-2025-{i+1:03d}",
                "type": (
                    "ai_insight"
                    if i == 0
                    else ["subject_enrolled", "query_resolved", "deviation_detected"][
                        i % 3
                    ]
                ),
                "subject_id": f"CARD{(len(subjects) - i):03d}" if i > 0 else "N/A",
                "site_id": sites[i % 3],
                "timestamp": (datetime.now() - timedelta(hours=i * 2)).isoformat(),
                "description": (
                    ai_analytics_result.get(
                        "executive_summary", "AI analysis completed"
                    )
                    if i == 0
                    else [
                        "New subject enrolled",
                        "Query resolved",
                        "Protocol deviation detected",
                    ][i % 3]
                ),
                "performed_by": (
                    "AI Analytics"
                    if i == 0
                    else f"Dr. {['Smith', 'Johnson', 'Davis'][i % 3]}"
                ),
            }
            for i in range(min(10, len(subjects)))
        ]

        analytics_result = {
            "success": True,
            "enrollment_trend": enrollment_trend,
            "data_quality_trend": data_quality_trend,
            "recent_activities": recent_activities,
        }
    else:
        # Fallback to rule-based analytics
        analytics_result = await analytics_agent.generate_dashboard_analytics(
            analytics_request
        )

    # Use agent result if available, otherwise fallback
    if analytics_result.get("success"):
        return DashboardAnalyticsResponse(
            enrollment_trend=analytics_result.get("enrollment_trend", []),
            data_quality_trend=analytics_result.get("data_quality_trend", []),
            recent_activities=analytics_result.get("recent_activities", []),
        )
    else:
        # Fallback to basic analytics
        from datetime import datetime, timedelta

        # Basic fallback data
        enrollment_trend = [
            {"date": datetime.now().strftime("%Y-%m-%d"), "cumulative": 45, "weekly": 3}
        ]

        data_quality_trend = [
            {"date": datetime.now().strftime("%Y-%m-%d"), "percentage": 94.2}
        ]

        recent_activities = [
            {
                "activity_id": "ACT-2025-001",
                "type": "subject_enrolled",
                "subject_id": "CARD050",
                "site_id": "SITE_001",
                "timestamp": datetime.now().isoformat(),
                "description": "New subject enrolled",
                "performed_by": "Dr. Smith",
            }
        ]

        return DashboardAnalyticsResponse(
            enrollment_trend=enrollment_trend,
            data_quality_trend=data_quality_trend,
            recent_activities=recent_activities,
        )
