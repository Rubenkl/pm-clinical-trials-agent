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
    """Verify source data against EDC data using AI-powered Data Verifier"""
    try:
        # Import and initialize the AI-powered Data Verifier
        from app.agents.data_verifier import DataVerifier
        data_verifier = DataVerifier()
        
        # Prepare verification data in the format expected by the agent
        verification_data = {
            "subject_id": sdv_input.subject_id,
            "site_id": sdv_input.site_id,
            "visit": sdv_input.visit,
            "edc_data": sdv_input.edc_data,
            "source_data": sdv_input.source_data
        }
        
        # Use AI-powered verification
        ai_result = await data_verifier.verify_clinical_data_ai(verification_data)
        
        # If AI verification is successful and powered by AI, use it
        if ai_result.get("success") and ai_result.get("ai_powered"):
            # Extract data from AI result to match DataVerifierResponse model
            return DataVerifierResponse(
                success=ai_result["success"],
                verification_id=ai_result["verification_id"],
                site=ai_result["site"],
                monitor=ai_result["monitor"],
                verification_date=datetime.fromisoformat(ai_result["verification_date"]),
                subject=SubjectInfo(**ai_result["subject"]),
                visit=ai_result["visit"],
                match_score=ai_result["match_score"],
                matching_fields=ai_result["matching_fields"],
                discrepancies=[DiscrepancyDetail(**d) for d in ai_result["discrepancies"]],
                total_fields_compared=ai_result["total_fields_compared"],
                progress=SDVProgress(**ai_result["progress"]),
                fields_to_verify=[VerificationField(**f) for f in ai_result["fields_to_verify"]],
                recommendations=ai_result["recommendations"],
                critical_findings=ai_result["critical_findings"],
                execution_time=ai_result["execution_time"],
                raw_response=json.dumps({
                    "verification_summary": ai_result.get("verification_summary", ""),
                    "ai_insights": ai_result.get("ai_insights", ""),
                    "ai_powered": True
                })
            )
        
        # Fall back to rule-based verification if AI fails
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


# SDV PROGRESS ENDPOINT REMOVED - Use /api/v1/test-data/sdv/sessions for progress
# The test-data endpoint provides comprehensive SDV session and progress information


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


# SDV DISCREPANCIES ENDPOINT REMOVED - Use /api/v1/test-data/subjects/{id}/discrepancies
# Subject-specific discrepancies are available through the test-data API


# SDV SUMMARY REPORT ENDPOINT REMOVED - Reporting functionality not needed for MVP
# Use /api/v1/sdv/stats/dashboard for summary statistics


# SDV SITE REPORT ENDPOINT REMOVED - Reporting functionality not needed for MVP
# Site-specific data available through test-data endpoints