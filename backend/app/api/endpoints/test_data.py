"""Test Data API endpoints for development and testing."""

from typing import Dict, List, Any, Optional
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

def get_test_data_service(settings: Settings = Depends(get_settings)) -> TestDataService:
    """Dependency to get test data service."""
    return TestDataService(settings)

@router.get("/status", response_model=TestDataStatusResponse)
async def get_test_data_status(
    test_service: TestDataService = Depends(get_test_data_service)
) -> TestDataStatusResponse:
    """Get test data status and statistics."""
    
    if not test_service.is_test_mode():
        return TestDataStatusResponse(
            test_mode_enabled=False,
            current_study=None,
            available_subjects=[],
            available_sites=[],
            data_statistics={}
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
            site["metrics"]["total_queries"] 
            for site in site_performance
        ),
        "total_discrepancies": sum(
            site["metrics"]["total_discrepancies"] 
            for site in site_performance
        ),
        "critical_findings": sum(
            site["metrics"]["critical_findings"] 
            for site in site_performance
        )
    }
    
    return TestDataStatusResponse(
        test_mode_enabled=True,
        current_study=study_info["protocol_id"] if study_info else None,
        available_subjects=available_subjects,
        available_sites=available_sites,
        data_statistics=statistics
    )

@router.get("/subjects/{subject_id}", response_model=SubjectDataResponse)
async def get_subject_data(
    subject_id: str,
    data_source: str = Query(default="edc", description="Data source: edc, source, or both"),
    test_service: TestDataService = Depends(get_test_data_service)
) -> SubjectDataResponse:
    """Get subject data from specified source."""
    
    if not test_service.is_test_mode():
        raise HTTPException(status_code=404, detail="Test data mode not enabled")
    
    if data_source not in ["edc", "source", "both"]:
        raise HTTPException(status_code=400, detail="Invalid data_source. Must be 'edc', 'source', or 'both'")
    
    subject_data = await test_service.get_subject_data(subject_id, data_source)
    
    if not subject_data:
        raise HTTPException(status_code=404, detail=f"Subject {subject_id} not found")
    
    return SubjectDataResponse(
        subject_id=subject_id,
        data_source=data_source,
        data=subject_data
    )

@router.get("/subjects/{subject_id}/visits/{visit_name}")
async def get_visit_data(
    subject_id: str,
    visit_name: str,
    data_source: str = Query(default="edc", description="Data source: edc, source, or both"),
    test_service: TestDataService = Depends(get_test_data_service)
) -> Dict[str, Any]:
    """Get specific visit data."""
    
    if not test_service.is_test_mode():
        raise HTTPException(status_code=404, detail="Test data mode not enabled")
    
    if data_source not in ["edc", "source", "both"]:
        raise HTTPException(status_code=400, detail="Invalid data_source. Must be 'edc', 'source', or 'both'")
    
    visit_data = await test_service.get_visit_data(subject_id, visit_name, data_source)
    
    if not visit_data:
        raise HTTPException(status_code=404, detail=f"Visit {visit_name} for subject {subject_id} not found")
    
    return visit_data

@router.get("/subjects/{subject_id}/discrepancies", response_model=DiscrepancyResponse)
async def get_subject_discrepancies(
    subject_id: str,
    visit_name: Optional[str] = Query(default=None, description="Optional visit name filter"),
    severity: Optional[str] = Query(default=None, description="Optional severity filter"),
    test_service: TestDataService = Depends(get_test_data_service)
) -> DiscrepancyResponse:
    """Get known discrepancies for a subject."""
    
    if not test_service.is_test_mode():
        raise HTTPException(status_code=404, detail="Test data mode not enabled")
    
    discrepancies = await test_service.get_discrepancies(subject_id, visit_name)
    
    # Apply severity filter if specified
    if severity:
        discrepancies = [d for d in discrepancies if d.get("severity") == severity]
    
    return DiscrepancyResponse(
        subject_id=subject_id,
        visit_name=visit_name,
        discrepancies=discrepancies
    )

@router.get("/subjects/{subject_id}/queries", response_model=QueryResponse)
async def get_subject_queries(
    subject_id: str,
    visit_name: Optional[str] = Query(default=None, description="Optional visit name filter"),
    status: Optional[str] = Query(default=None, description="Optional status filter"),
    test_service: TestDataService = Depends(get_test_data_service)
) -> QueryResponse:
    """Get existing queries for a subject."""
    
    if not test_service.is_test_mode():
        raise HTTPException(status_code=404, detail="Test data mode not enabled")
    
    queries = await test_service.get_queries(subject_id, visit_name)
    
    # Apply status filter if specified
    if status:
        queries = [q for q in queries if q.get("status") == status]
    
    return QueryResponse(
        subject_id=subject_id,
        visit_name=visit_name,
        queries=queries
    )

@router.get("/discrepancies", response_model=List[Dict[str, Any]])
async def get_all_discrepancies(
    severity: Optional[str] = Query(default=None, description="Optional severity filter"),
    test_service: TestDataService = Depends(get_test_data_service)
) -> List[Dict[str, Any]]:
    """Get all subjects with discrepancies."""
    
    if not test_service.is_test_mode():
        raise HTTPException(status_code=404, detail="Test data mode not enabled")
    
    return await test_service.get_subjects_with_discrepancies(severity)

@router.get("/sites/performance", response_model=SitePerformanceResponse)
async def get_site_performance(
    test_service: TestDataService = Depends(get_test_data_service)
) -> SitePerformanceResponse:
    """Get site performance data."""
    
    if not test_service.is_test_mode():
        raise HTTPException(status_code=404, detail="Test data mode not enabled")
    
    sites = await test_service.get_site_performance_data()
    
    return SitePerformanceResponse(sites=sites)

@router.get("/sites/{site_id}")
async def get_site_data(
    site_id: str,
    test_service: TestDataService = Depends(get_test_data_service)
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
    test_service: TestDataService = Depends(get_test_data_service)
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
    preset_name: Optional[str] = Query(default=None, description="Optional preset name"),
    test_service: TestDataService = Depends(get_test_data_service)
) -> Dict[str, Any]:
    """Regenerate test data with optional different preset."""
    
    if not test_service.is_test_mode():
        raise HTTPException(status_code=404, detail="Test data mode not enabled")
    
    success = await test_service.regenerate_test_data(preset_name)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to regenerate test data")
    
    return {
        "message": "Test data regenerated successfully",
        "preset_used": preset_name or "current preset"
    }

# Example endpoint for agent testing
@router.get("/agent-test-data")
async def get_agent_test_data(
    test_service: TestDataService = Depends(get_test_data_service)
) -> Dict[str, Any]:
    """Get comprehensive test data for agent testing."""
    
    if not test_service.is_test_mode():
        raise HTTPException(status_code=404, detail="Test data mode not enabled")
    
    from app.services.test_data_service import get_test_data_for_agents
    return await get_test_data_for_agents(test_service)