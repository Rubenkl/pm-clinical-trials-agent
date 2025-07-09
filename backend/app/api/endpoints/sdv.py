"""
SDV (Source Data Verification) endpoints for clinical trials.
Handles data verification, discrepancy detection, and audit trails.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
import json

from app.api.models.structured_responses import (
    DataVerifierResponse,
    SDVStatistics,
    SeverityLevel,
    DiscrepancyDetail,
    SDVProgress,
    VerificationField,
    SubjectInfo
)

router = APIRouter()


class SDVVerifyInput(BaseModel):
    """Input for SDV verification"""
    subject_id: str
    site_id: str
    visit: str
    edc_data: Dict[str, Any]
    source_data: Dict[str, Any]
    monitor_id: Optional[str] = None
    verification_type: Optional[str] = "comprehensive"
    context: Optional[Dict[str, Any]] = Field(default_factory=dict)


class SDVFilters(BaseModel):
    """Filters for SDV discrepancies"""
    site_id: Optional[str] = None
    severity: Optional[List[SeverityLevel]] = None
    subject_id: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    verified_by: Optional[str] = None


def detect_discrepancies(edc_data: Dict[str, Any], source_data: Dict[str, Any]) -> List[DiscrepancyDetail]:
    """Detect discrepancies between EDC and source data"""
    discrepancies = []
    
    # Get all unique field names from both datasets
    all_fields = set(edc_data.keys()) | set(source_data.keys())
    
    for field in all_fields:
        edc_value = edc_data.get(field)
        source_value = source_data.get(field)
        
        # Check for missing values
        if edc_value is None and source_value is not None:
            discrepancies.append(DiscrepancyDetail(
                field=field,
                field_label=field.replace("_", " ").title(),
                edc_value="",
                source_value=str(source_value),
                severity=SeverityLevel.MINOR,
                discrepancy_type="missing_in_edc",
                confidence=0.95
            ))
        elif edc_value is not None and source_value is None:
            discrepancies.append(DiscrepancyDetail(
                field=field,
                field_label=field.replace("_", " ").title(),
                edc_value=str(edc_value),
                source_value="",
                severity=SeverityLevel.MINOR,
                discrepancy_type="missing_in_source",
                confidence=0.95
            ))
        elif edc_value is not None and source_value is not None:
            # Check for value mismatches
            if str(edc_value) != str(source_value):
                severity = determine_discrepancy_severity(field, edc_value, source_value)
                discrepancies.append(DiscrepancyDetail(
                    field=field,
                    field_label=field.replace("_", " ").title(),
                    edc_value=str(edc_value),
                    source_value=str(source_value),
                    severity=severity,
                    discrepancy_type="value_mismatch",
                    confidence=0.9
                ))
    
    return discrepancies


def determine_discrepancy_severity(field: str, edc_value: Any, source_value: Any) -> SeverityLevel:
    """Determine severity of discrepancy based on field and values"""
    try:
        field_lower = field.lower()
        
        # Critical fields (safety-related)
        if any(keyword in field_lower for keyword in ['hemoglobin', 'hgb', 'bp', 'blood_pressure']):
            try:
                # For numeric fields, check magnitude of difference
                edc_num = float(edc_value)
                source_num = float(source_value)
                diff_percent = abs(edc_num - source_num) / max(edc_num, source_num) * 100
                
                if diff_percent > 20:
                    return SeverityLevel.CRITICAL
                elif diff_percent > 10:
                    return SeverityLevel.MAJOR
                else:
                    return SeverityLevel.MINOR
            except (ValueError, TypeError):
                return SeverityLevel.MAJOR
        
        # Other fields default to minor
        return SeverityLevel.MINOR
        
    except Exception:
        return SeverityLevel.MINOR


def calculate_match_score(total_fields: int, discrepancies: List[DiscrepancyDetail]) -> float:
    """Calculate match score based on discrepancies"""
    if total_fields == 0:
        return 1.0
    
    matching_fields = total_fields - len(discrepancies)
    return matching_fields / total_fields


@router.post("/verify", response_model=DataVerifierResponse)
async def verify_sdv_data(sdv_input: SDVVerifyInput):
    """Verify source data against EDC data"""
    try:
        start_time = datetime.now()
        
        # Detect discrepancies
        discrepancies = detect_discrepancies(sdv_input.edc_data, sdv_input.source_data)
        
        # Calculate match score
        total_fields = len(set(sdv_input.edc_data.keys()) | set(sdv_input.source_data.keys()))
        match_score = calculate_match_score(total_fields, discrepancies)
        
        # Generate matching fields list
        matching_fields = []
        for field in sdv_input.edc_data.keys():
            if field in sdv_input.source_data:
                if str(sdv_input.edc_data[field]) == str(sdv_input.source_data[field]):
                    matching_fields.append(field)
        
        # Generate recommendations
        recommendations = []
        critical_findings = []
        
        for disc in discrepancies:
            if disc.severity == SeverityLevel.CRITICAL:
                critical_findings.append(f"Critical discrepancy in {disc.field}: {disc.edc_value} vs {disc.source_value}")
                recommendations.append(f"Immediately verify {disc.field} with source documents")
            elif disc.severity == SeverityLevel.MAJOR:
                recommendations.append(f"Review {disc.field} discrepancy with medical monitor")
        
        if not recommendations:
            recommendations.append("Data verification complete - no issues found")
        
        # Create progress tracking
        progress = SDVProgress(
            total_fields=total_fields,
            verified=len(matching_fields),
            discrepancies=len(discrepancies),
            skipped=0,
            completion_rate=match_score,
            estimated_time_remaining=0 if match_score == 1.0 else 30
        )
        
        # Create subject info
        subject = SubjectInfo(
            id=sdv_input.subject_id,
            initials=sdv_input.context.get("initials", "N/A"),
            site=sdv_input.context.get("site_name", "Unknown Site"),
            site_id=sdv_input.site_id
        )
        
        # Fields to verify (for future verification)
        fields_to_verify = []
        for field, value in sdv_input.edc_data.items():
            if field not in matching_fields:
                fields_to_verify.append(VerificationField(
                    field_name=field,
                    field_label=field.replace("_", " ").title(),
                    edc_value=str(value),
                    field_type="text",
                    required=True
                ))
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return DataVerifierResponse(
            success=True,
            verification_id=f"SDV-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{sdv_input.subject_id}",
            site=sdv_input.site_id,
            monitor=sdv_input.monitor_id or "System",
            verification_date=datetime.now(),
            subject=subject,
            visit=sdv_input.visit,
            match_score=match_score,
            matching_fields=matching_fields,
            discrepancies=discrepancies,
            total_fields_compared=total_fields,
            progress=progress,
            fields_to_verify=fields_to_verify,
            recommendations=recommendations,
            critical_findings=critical_findings,
            execution_time=execution_time,
            raw_response=json.dumps({
                "verification_summary": f"Processed {total_fields} fields with {len(discrepancies)} discrepancies",
                "match_score": match_score
            })
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SDV verification failed: {str(e)}")


@router.get("/progress")
async def get_sdv_progress(
    site_id: Optional[str] = Query(None),
    subject_id: Optional[str] = Query(None)
):
    """Get SDV progress for sites or subjects"""
    try:
        if site_id:
            # Return progress for specific site
            return {
                "site_id": site_id,
                "total_subjects": 25,
                "verified_subjects": 18,
                "completion_rate": 0.72,
                "estimated_time_remaining": 120,  # minutes
                "last_verification": datetime.now().isoformat(),
                "monitor_assigned": "Monitor A",
                "verification_rate": 2.5  # subjects per day
            }
        else:
            # Return progress for all sites
            return {
                "total_subjects": 75,
                "verified_subjects": 60,
                "completion_rate": 0.8,
                "sites": [
                    {
                        "site_id": "SITE01",
                        "total_subjects": 25,
                        "verified_subjects": 18,
                        "completion_rate": 0.72
                    },
                    {
                        "site_id": "SITE02",
                        "total_subjects": 30,
                        "verified_subjects": 22,
                        "completion_rate": 0.73
                    },
                    {
                        "site_id": "SITE03",
                        "total_subjects": 20,
                        "verified_subjects": 20,
                        "completion_rate": 1.0
                    }
                ],
                "overall_progress": {
                    "total_subjects": 75,
                    "verified_subjects": 60,
                    "completion_rate": 0.8
                }
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve SDV progress: {str(e)}")


@router.get("/stats/dashboard", response_model=SDVStatistics)
async def get_sdv_dashboard_stats():
    """Get SDV statistics for dashboard display"""
    try:
        stats = SDVStatistics(
            total_subjects=75,
            verified_subjects=60,
            total_data_points=2250,
            verified_data_points=1800,
            overall_completion=0.8,
            discrepancy_rate=0.05,
            sites_summary=[
                {
                    "site_id": "SITE01",
                    "completion_rate": 0.72,
                    "discrepancy_rate": 0.06,
                    "monitor": "Monitor A"
                },
                {
                    "site_id": "SITE02", 
                    "completion_rate": 0.73,
                    "discrepancy_rate": 0.04,
                    "monitor": "Monitor B"
                },
                {
                    "site_id": "SITE03",
                    "completion_rate": 1.0,
                    "discrepancy_rate": 0.02,
                    "monitor": "Monitor C"
                }
            ],
            high_risk_sites=["SITE01"],
            resource_utilization={
                "monitor_a": 0.85,
                "monitor_b": 0.75,
                "monitor_c": 0.60
            }
        )
        
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve SDV statistics: {str(e)}")


@router.get("/discrepancies")
async def list_sdv_discrepancies(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    severity: Optional[str] = Query(None),
    site_id: Optional[str] = Query(None),
    subject_id: Optional[str] = Query(None)
):
    """List SDV discrepancies with filtering"""
    try:
        # Mock discrepancy data
        mock_discrepancies = []
        for i in range(min(20, limit)):
            discrepancy = {
                "discrepancy_id": f"DISC-{i+1:03d}",
                "subject_id": f"SUBJ{i+1:03d}",
                "site_id": f"SITE{(i % 3) + 1:02d}",
                "field": "hemoglobin" if i % 2 == 0 else "blood_pressure",
                "edc_value": "12.5" if i % 2 == 0 else "120/80",
                "source_value": "12.0" if i % 2 == 0 else "125/85",
                "severity": ["critical", "major", "minor"][i % 3],
                "status": "pending",
                "detected_date": datetime.now().isoformat(),
                "monitor": f"Monitor {chr(65 + (i % 3))}"
            }
            
            # Apply filters
            if severity and discrepancy["severity"] != severity:
                continue
            if site_id and discrepancy["site_id"] != site_id:
                continue
            if subject_id and discrepancy["subject_id"] != subject_id:
                continue
                
            mock_discrepancies.append(discrepancy)
        
        return mock_discrepancies[skip:skip + limit]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve discrepancies: {str(e)}")


@router.get("/report/summary")
async def get_sdv_summary_report():
    """Generate SDV summary report"""
    try:
        return {
            "report_id": f"SDV-REPORT-{datetime.now().strftime('%Y%m%d')}",
            "generated_date": datetime.now().isoformat(),
            "report_type": "summary",
            "summary_statistics": {
                "total_subjects": 75,
                "verified_subjects": 60,
                "completion_rate": 0.8,
                "total_discrepancies": 25,
                "critical_discrepancies": 3,
                "major_discrepancies": 8,
                "minor_discrepancies": 14
            },
            "site_breakdown": [
                {
                    "site_id": "SITE01",
                    "completion_rate": 0.72,
                    "discrepancy_count": 12,
                    "status": "on_track"
                },
                {
                    "site_id": "SITE02",
                    "completion_rate": 0.73,
                    "discrepancy_count": 8,
                    "status": "on_track"
                },
                {
                    "site_id": "SITE03",
                    "completion_rate": 1.0,
                    "discrepancy_count": 5,
                    "status": "completed"
                }
            ],
            "recommendations": [
                "Prioritize completion of SITE01 verification",
                "Review critical discrepancies with medical monitor",
                "Consider additional training for sites with high discrepancy rates"
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate SDV report: {str(e)}")


@router.get("/report/site/{site_id}")
async def get_sdv_site_report(site_id: str):
    """Generate SDV report for specific site"""
    try:
        return {
            "site_id": site_id,
            "report_id": f"SDV-SITE-{site_id}-{datetime.now().strftime('%Y%m%d')}",
            "generated_date": datetime.now().isoformat(),
            "verification_statistics": {
                "total_subjects": 25,
                "verified_subjects": 18,
                "completion_rate": 0.72,
                "average_verification_time": 45,  # minutes per subject
                "total_discrepancies": 12
            },
            "discrepancy_summary": {
                "critical": 2,
                "major": 4,
                "minor": 6,
                "most_common_fields": ["hemoglobin", "blood_pressure", "weight"]
            },
            "monitor_performance": {
                "monitor_name": "Monitor A",
                "subjects_per_day": 2.5,
                "accuracy_rate": 0.95,
                "efficiency_score": 0.88
            },
            "recommendations": [
                f"Focus on completing remaining {25-18} subjects",
                "Address critical discrepancies in hemoglobin values",
                "Consider process improvements for blood pressure measurements"
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate site report: {str(e)}")