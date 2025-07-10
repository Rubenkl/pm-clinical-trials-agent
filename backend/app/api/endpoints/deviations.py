"""
Deviation Detection endpoints for clinical trials.
Handles protocol deviation detection, tracking, and resolution workflows.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
import json

from app.api.models.structured_responses import (
    SeverityLevel,
    SubjectInfo
)

router = APIRouter()


class DeviationDetectionInput(BaseModel):
    """Input for deviation detection"""
    subject_id: str
    site_id: str
    visit: str
    protocol_data: Dict[str, Any]
    actual_data: Dict[str, Any]
    monitor_id: Optional[str] = None
    detection_type: Optional[str] = "comprehensive"
    context: Optional[Dict[str, Any]] = Field(default_factory=dict)


class DeviationDetail(BaseModel):
    """Individual deviation detail"""
    category: str
    severity: SeverityLevel
    protocol_requirement: str
    actual_value: str
    impact_level: str
    corrective_action_required: bool
    deviation_description: str
    confidence: float


class DeviationStatistics(BaseModel):
    """Deviation statistics for dashboard"""
    total_deviations: int
    critical_deviations: int
    major_deviations: int
    minor_deviations: int
    resolved_deviations: int
    pending_deviations: int
    deviations_by_site: Dict[str, int]
    deviations_by_category: Dict[str, int]
    deviation_trends: List[Dict[str, Any]]
    resolution_rate: float
    average_resolution_time: float


class DeviationDetectionResponse(BaseModel):
    """Response from deviation detection"""
    success: bool
    response_type: str = "deviation_detection"
    deviation_id: str
    subject: SubjectInfo
    site: str
    visit: str
    monitor: str
    detection_date: datetime
    deviations: List[DeviationDetail]
    total_deviations_found: int
    impact_assessment: str
    recommendations: List[str]
    corrective_actions_required: List[str]
    agent_id: str = "deviation-detector"
    execution_time: float
    raw_response: str


class DeviationResolutionInput(BaseModel):
    """Input for deviation resolution"""
    resolution: str
    resolved_by: str
    corrective_actions: List[str]
    resolution_date: Optional[datetime] = None
    comments: Optional[str] = None


def detect_protocol_deviations(protocol_data: Dict[str, Any], actual_data: Dict[str, Any]) -> List[DeviationDetail]:
    """Detect protocol deviations by comparing protocol requirements to actual data"""
    deviations = []
    
    # Check visit window deviation
    if "required_visit_window" in protocol_data and "visit_date" in actual_data and "scheduled_date" in actual_data:
        try:
            visit_date = datetime.fromisoformat(actual_data["visit_date"])
            scheduled_date = datetime.fromisoformat(actual_data["scheduled_date"])
            days_diff = abs((visit_date - scheduled_date).days)
            
            # Parse window (e.g., "±3 days")
            window_str = protocol_data["required_visit_window"]
            window_days = int(window_str.replace("±", "").replace(" days", "").strip())
            
            if days_diff > window_days:
                severity = SeverityLevel.MAJOR if days_diff > window_days * 2 else SeverityLevel.MINOR
                deviations.append(DeviationDetail(
                    category="visit_window",
                    severity=severity,
                    protocol_requirement=f"Visit within {window_str}",
                    actual_value=f"{days_diff} days outside window",
                    impact_level="medium" if severity == SeverityLevel.MAJOR else "low",
                    corrective_action_required=True,
                    deviation_description=f"Visit occurred {days_diff} days outside protocol window",
                    confidence=0.95
                ))
        except (ValueError, KeyError):
            pass
    
    # Check fasting requirement deviation
    if "required_fasting" in protocol_data and "fasting_hours" in actual_data:
        try:
            required_hours = int(protocol_data["required_fasting"].replace(" hours", "").strip())
            actual_hours = int(actual_data["fasting_hours"])
            
            if actual_hours < required_hours:
                hours_short = required_hours - actual_hours
                severity = SeverityLevel.MAJOR if hours_short >= 4 else SeverityLevel.MINOR
                deviations.append(DeviationDetail(
                    category="fasting_requirement",
                    severity=severity,
                    protocol_requirement=f"Fasting {required_hours} hours",
                    actual_value=f"Only {actual_hours} hours fasting",
                    impact_level="high" if severity == SeverityLevel.MAJOR else "medium",
                    corrective_action_required=True,
                    deviation_description=f"Subject fasted {hours_short} hours less than required",
                    confidence=0.9
                ))
        except (ValueError, KeyError):
            pass
    
    # Check prohibited medication deviation
    if "prohibited_medications" in protocol_data and "concomitant_medications" in actual_data:
        prohibited = [med.lower() for med in protocol_data["prohibited_medications"]]
        actual_meds = [med.lower() for med in actual_data["concomitant_medications"]]
        
        violations = [med for med in actual_meds if med in prohibited]
        for violation in violations:
            deviations.append(DeviationDetail(
                category="prohibited_medication",
                severity=SeverityLevel.CRITICAL,
                protocol_requirement="No prohibited medications allowed",
                actual_value=f"Taking {violation}",
                impact_level="critical",
                corrective_action_required=True,
                deviation_description=f"Subject taking prohibited medication: {violation}",
                confidence=0.98
            ))
    
    return deviations


def assess_deviation_impact(deviations: List[DeviationDetail]) -> str:
    """Assess overall impact of detected deviations"""
    if not deviations:
        return "No protocol deviations detected"
    
    critical_count = sum(1 for d in deviations if d.severity == SeverityLevel.CRITICAL)
    major_count = sum(1 for d in deviations if d.severity == SeverityLevel.MAJOR)
    
    if critical_count > 0:
        return f"Critical impact: {critical_count} critical deviation(s) detected"
    elif major_count > 0:
        return f"Significant impact: {major_count} major deviation(s) detected"
    else:
        return "Minor impact: Only minor deviations detected"


def generate_deviation_recommendations(deviations: List[DeviationDetail]) -> List[str]:
    """Generate recommendations based on detected deviations"""
    recommendations = []
    
    if not deviations:
        return ["No deviations detected - continue as planned"]
    
    # Critical deviations
    critical_deviations = [d for d in deviations if d.severity == SeverityLevel.CRITICAL]
    if critical_deviations:
        recommendations.append("Immediate medical monitor notification required")
        recommendations.append("Consider subject discontinuation assessment")
    
    # Major deviations
    major_deviations = [d for d in deviations if d.severity == SeverityLevel.MAJOR]
    if major_deviations:
        recommendations.append("Site staff retraining recommended")
        recommendations.append("Enhanced monitoring for future visits")
    
    # Visit window deviations
    visit_deviations = [d for d in deviations if d.category == "visit_window"]
    if visit_deviations:
        recommendations.append("Review site scheduling procedures")
    
    # Medication deviations
    med_deviations = [d for d in deviations if d.category == "prohibited_medication"]
    if med_deviations:
        recommendations.append("Reinforce medication compliance education")
        recommendations.append("Increase frequency of medication reviews")
    
    return recommendations


@router.post("/detect", response_model=DeviationDetectionResponse)
async def detect_deviations(deviation_input: DeviationDetectionInput):
    """Detect protocol deviations using AI-powered analysis"""
    try:
        start_time = datetime.now()
        
        # Import and initialize the AI-powered Deviation Detector
        from app.agents.deviation_detector import DeviationDetector
        detector = DeviationDetector()
        
        # Prepare data for AI analysis
        protocol_data = deviation_input.protocol_data
        subject_data = {
            "subject_id": deviation_input.subject_id,
            "site_id": deviation_input.site_id,
            "visit": deviation_input.visit,
            **deviation_input.actual_data
        }
        
        # Use AI-powered detection
        ai_result = await detector.detect_protocol_deviations_ai(protocol_data, subject_data)
        
        # If AI detection is successful and powered by AI, use it
        if ai_result.get("ai_powered") and "deviations" in ai_result:
            # Convert AI deviations to response format
            deviations = []
            for dev in ai_result.get("deviations", []):
                deviations.append(DeviationDetail(
                    category=dev.get("type", "other"),
                    severity=dev.get("severity", "minor"),
                    description=dev.get("description", ""),
                    detected_value=str(dev.get("detected_value", "")),
                    expected_value=str(dev.get("expected_value", "")),
                    corrective_action_required=dev.get("severity") in ["critical", "major"],
                    medical_justification=dev.get("clinical_impact", ""),
                    regulatory_impact=dev.get("regulatory_impact", "")
                ))
            
            # Extract AI insights for impact assessment
            impact_assessment = ImpactAssessment(
                regulatory_impact=ai_result.get("overall_assessment", ""),
                patient_safety_impact="high" if ai_result.get("critical_count", 0) > 0 else "low",
                data_integrity_impact="medium" if len(deviations) > 0 else "low",
                overall_severity="critical" if ai_result.get("critical_count", 0) > 0 else "minor"
            )
            
            # Use AI recommendations
            recommendations = []
            if "recommended_actions" in ai_result:
                recommendations = ai_result["recommended_actions"]
            else:
                # Extract from individual deviations
                for dev in ai_result.get("deviations", []):
                    if "recommended_action" in dev:
                        recommendations.append(dev["recommended_action"])
            
            # Generate corrective actions from AI insights
            corrective_actions = []
            for dev in ai_result.get("deviations", []):
                if dev.get("severity") in ["critical", "major"] and "recommended_action" in dev:
                    corrective_actions.append(dev["recommended_action"])
            
            if not corrective_actions:
                corrective_actions.append("No immediate corrective actions required")
        else:
            # Fallback to rule-based detection if AI fails
            deviations = detect_protocol_deviations(deviation_input.protocol_data, deviation_input.actual_data)
            impact_assessment = assess_deviation_impact(deviations)
            recommendations = generate_deviation_recommendations(deviations)
            
            # Generate corrective actions
            corrective_actions = []
            for deviation in deviations:
                if deviation.corrective_action_required:
                    if deviation.category == "visit_window":
                        corrective_actions.append("Review and update visit scheduling procedures")
                    elif deviation.category == "fasting_requirement":
                        corrective_actions.append("Provide additional patient education on fasting requirements")
                    elif deviation.category == "prohibited_medication":
                        corrective_actions.append("Immediate medication review and discontinuation if necessary")
            
            if not corrective_actions:
                corrective_actions.append("No corrective actions required")
        
        # Create subject info
        subject = SubjectInfo(
            id=deviation_input.subject_id,
            initials=deviation_input.context.get("initials", "N/A"),
            site=deviation_input.context.get("site_name", "Unknown Site"),
            site_id=deviation_input.site_id
        )
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return DeviationDetectionResponse(
            success=True,
            deviation_id=f"DEV-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{deviation_input.subject_id}",
            subject=subject,
            site=deviation_input.site_id,
            visit=deviation_input.visit,
            monitor=deviation_input.monitor_id or "System",
            detection_date=datetime.now(),
            deviations=deviations,
            total_deviations_found=len(deviations),
            impact_assessment=impact_assessment,
            recommendations=recommendations,
            corrective_actions_required=corrective_actions,
            execution_time=execution_time,
            raw_response=json.dumps({
                "detection_summary": f"Analyzed {len(deviation_input.protocol_data)} protocol requirements",
                "deviations_found": len(deviations),
                "ai_powered": ai_result.get("ai_powered", False) if "ai_result" in locals() else False,
                "compliance_score": ai_result.get("compliance_score", 0.0) if "ai_result" in locals() else 0.0
            })
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Deviation detection failed: {str(e)}")


@router.get("/")
async def list_deviations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    severity: Optional[str] = Query(None),
    site_id: Optional[str] = Query(None),
    subject_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None)
):
    """List protocol deviations with filtering"""
    try:
        # Mock deviation data
        mock_deviations = []
        for i in range(min(15, limit)):
            deviation = {
                "deviation_id": f"DEV-{i+1:03d}",
                "subject_id": f"SUBJ{i+1:03d}",
                "site_id": f"SITE{(i % 3) + 1:02d}",
                "category": ["visit_window", "fasting_requirement", "prohibited_medication"][i % 3],
                "severity": ["critical", "major", "minor"][(i + 1) % 3],
                "status": "pending" if i % 2 == 0 else "resolved",
                "detected_date": datetime.now().isoformat(),
                "protocol_requirement": "Visit within ±3 days" if i % 3 == 0 else "12 hour fasting",
                "actual_value": "6 days late" if i % 3 == 0 else "8 hours fasting"
            }
            
            # Apply filters
            if severity and deviation["severity"] != severity:
                continue
            if site_id and deviation["site_id"] != site_id:
                continue
            if subject_id and deviation["subject_id"] != subject_id:
                continue
            if status and deviation["status"] != status:
                continue
                
            mock_deviations.append(deviation)
        
        return mock_deviations[skip:skip + limit]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve deviations: {str(e)}")


@router.get("/stats/dashboard", response_model=DeviationStatistics)
async def get_deviation_dashboard_stats():
    """Get deviation statistics for dashboard display"""
    try:
        stats = DeviationStatistics(
            total_deviations=42,
            critical_deviations=3,
            major_deviations=15,
            minor_deviations=24,
            resolved_deviations=35,
            pending_deviations=7,
            deviations_by_site={
                "SITE01": 18,
                "SITE02": 14,
                "SITE03": 10
            },
            deviations_by_category={
                "visit_window": 20,
                "fasting_requirement": 12,
                "prohibited_medication": 6,
                "inclusion_criteria": 4
            },
            deviation_trends=[
                {"date": "2025-01-01", "deviations": 5},
                {"date": "2025-01-02", "deviations": 8},
                {"date": "2025-01-03", "deviations": 3},
                {"date": "2025-01-04", "deviations": 7}
            ],
            resolution_rate=0.83,
            average_resolution_time=72.5  # hours
        )
        
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve deviation statistics: {str(e)}")


@router.get("/{deviation_id}")
async def get_deviation_details(deviation_id: str):
    """Get detailed information about a specific deviation"""
    try:
        # Mock data for testing
        mock_deviation = {
            "deviation_id": deviation_id,
            "subject_id": "SUBJ001",
            "site_id": "SITE01",
            "category": "visit_window",
            "severity": "major",
            "protocol_requirement": "Visit must occur within ±3 days of scheduled date",
            "actual_value": "Visit occurred 6 days after scheduled date",
            "detected_date": datetime.now().isoformat(),
            "status": "pending",
            "impact_assessment": "Significant impact on protocol compliance",
            "corrective_actions": [
                "Site staff retraining on visit scheduling",
                "Enhanced calendar reminders for subjects",
                "Review site scheduling procedures"
            ],
            "monitor_assigned": "Monitor A",
            "detection_method": "automated_protocol_checker"
        }
        
        return mock_deviation
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve deviation {deviation_id}: {str(e)}")


@router.post("/{deviation_id}/resolve")
async def resolve_deviation(deviation_id: str, resolution: DeviationResolutionInput):
    """Resolve a deviation with provided resolution"""
    try:
        return {
            "success": True,
            "deviation_id": deviation_id,
            "status": "resolved",
            "resolved_by": resolution.resolved_by,
            "resolution_date": resolution.resolution_date or datetime.now(),
            "resolution": resolution.resolution,
            "corrective_actions": resolution.corrective_actions,
            "comments": resolution.comments
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to resolve deviation {deviation_id}: {str(e)}")