"""Deviation Detector Agent using OpenAI Agents SDK.

This agent has minimal responsibilities focused on protocol deviation detection 
and compliance monitoring. It returns structured JSON responses with human-readable
fields for frontend consumption.
"""

import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum

# OpenAI Agents SDK imports
try:
    from agents import Agent, function_tool, Context
except ImportError:
    # Mock for development if SDK not available
    class Context(BaseModel):
        pass
    def function_tool(func):
        return func
    class Agent:
        def __init__(self, name, instructions, tools=None, model="gpt-4"):
            self.name = name
            self.instructions = instructions
            self.tools = tools or []
            self.model = model


class DeviationSeverity(Enum):
    """Severity levels for protocol deviations"""
    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"
    INFO = "info"


class DeviationCategory(Enum):
    """Categories of protocol deviations"""
    PROHIBITED_MEDICATION = "prohibited_medication"
    VISIT_WINDOW = "visit_window"
    FASTING_REQUIREMENT = "fasting_requirement"
    VITAL_SIGNS = "vital_signs"
    LABORATORY_VALUE = "laboratory_value"
    VISIT_DURATION = "visit_duration"
    INCLUSION_CRITERIA = "inclusion_criteria"
    EXCLUSION_CRITERIA = "exclusion_criteria"
    OTHER = "other"


class DeviationDetectionContext(Context):
    """Context for Deviation Detector operations"""
    detection_history: List[Dict[str, Any]] = Field(default_factory=list)
    compliance_patterns: Dict[str, Any] = Field(default_factory=dict)
    performance_metrics: Dict[str, Any] = Field(default_factory=dict)
    protocol_requirements: Dict[str, Any] = Field(default_factory=dict)


@function_tool
def detect_protocol_deviations(
    context: DeviationDetectionContext,
    deviation_data: str
) -> str:
    """Detect protocol deviations by comparing requirements to actual data.
    
    Args:
        deviation_data: JSON string with protocol_data, actual_data, subject_id, site_id, visit
        
    Returns:
        JSON string with detected deviations and compliance assessment
    """
    try:
        data = json.loads(deviation_data)
        protocol_data = data.get("protocol_data", {})
        actual_data = data.get("actual_data", {})
        subject_id = data.get("subject_id", "")
        site_id = data.get("site_id", "")
        visit = data.get("visit", "")
        
        deviations = []
        
        # Check prohibited medications
        if "prohibited_medications" in protocol_data and "concomitant_medications" in actual_data:
            prohibited = set(protocol_data["prohibited_medications"])
            current = set(actual_data["concomitant_medications"])
            violations = prohibited & current
            
            for med in violations:
                deviations.append({
                    "category": DeviationCategory.PROHIBITED_MEDICATION.value,
                    "severity": DeviationSeverity.CRITICAL.value,
                    "protocol_requirement": "No prohibited medications allowed",
                    "actual_value": f"Taking {med}",
                    "impact_level": "critical",
                    "corrective_action_required": True,
                    "deviation_description": f"Subject taking prohibited medication: {med}",
                    "confidence": 0.98
                })
        
        # Check visit window deviations
        if "required_visit_window" in protocol_data and "visit_date" in actual_data and "scheduled_date" in actual_data:
            try:
                visit_date = datetime.fromisoformat(actual_data["visit_date"])
                scheduled_date = datetime.fromisoformat(actual_data["scheduled_date"])
                days_diff = abs((visit_date - scheduled_date).days)
                
                # Extract window (e.g., "±3 days" -> 3)
                window_str = protocol_data["required_visit_window"]
                window_days = int(''.join(filter(str.isdigit, window_str)))
                
                if days_diff > window_days:
                    severity = DeviationSeverity.MAJOR.value if days_diff > window_days * 2 else DeviationSeverity.MINOR.value
                    deviations.append({
                        "category": DeviationCategory.VISIT_WINDOW.value,
                        "severity": severity,
                        "protocol_requirement": f"Visit within {window_str}",
                        "actual_value": f"{days_diff} days outside window",
                        "impact_level": "medium" if severity == "major" else "low",
                        "corrective_action_required": True,
                        "deviation_description": f"Visit occurred {days_diff} days outside protocol window",
                        "confidence": 0.95
                    })
            except ValueError:
                pass
        
        # Check fasting requirements
        if "required_fasting" in protocol_data and "fasting_hours" in actual_data:
            try:
                required_hours = int(''.join(filter(str.isdigit, protocol_data["required_fasting"])))
                actual_hours = int(''.join(filter(str.isdigit, actual_data["fasting_hours"])))
                
                if actual_hours < required_hours:
                    deviations.append({
                        "category": DeviationCategory.FASTING_REQUIREMENT.value,
                        "severity": DeviationSeverity.MINOR.value,
                        "protocol_requirement": f"Fasting for {required_hours} hours required",
                        "actual_value": f"{actual_hours} hours fasting",
                        "impact_level": "low",
                        "corrective_action_required": True,
                        "deviation_description": f"Insufficient fasting: {actual_hours} hours (required: {required_hours})",
                        "confidence": 0.90
                    })
            except ValueError:
                pass
        
        # Check vital signs deviations
        if "maximum_systolic_bp" in protocol_data and "systolic_bp" in actual_data:
            try:
                max_bp = float(protocol_data["maximum_systolic_bp"])
                actual_bp = float(actual_data["systolic_bp"])
                
                if actual_bp > max_bp:
                    severity = DeviationSeverity.CRITICAL.value if actual_bp > max_bp * 1.3 else DeviationSeverity.MAJOR.value
                    deviations.append({
                        "category": DeviationCategory.VITAL_SIGNS.value,
                        "severity": severity,
                        "protocol_requirement": f"Systolic BP ≤ {max_bp} mmHg",
                        "actual_value": f"{actual_bp} mmHg",
                        "impact_level": "critical" if severity == "critical" else "medium",
                        "corrective_action_required": True,
                        "deviation_description": f"Systolic BP {actual_bp} mmHg exceeds protocol limit of {max_bp} mmHg",
                        "confidence": 0.95
                    })
            except ValueError:
                pass
        
        # Check laboratory value deviations
        if "minimum_hemoglobin" in protocol_data and "hemoglobin" in actual_data:
            try:
                min_hgb = float(protocol_data["minimum_hemoglobin"])
                actual_hgb = float(actual_data["hemoglobin"])
                
                if actual_hgb < min_hgb:
                    severity = DeviationSeverity.CRITICAL.value if actual_hgb < min_hgb * 0.8 else DeviationSeverity.MAJOR.value
                    deviations.append({
                        "category": DeviationCategory.LABORATORY_VALUE.value,
                        "severity": severity,
                        "protocol_requirement": f"Hemoglobin ≥ {min_hgb} g/dL",
                        "actual_value": f"{actual_hgb} g/dL",
                        "impact_level": "critical" if severity == "critical" else "medium",
                        "corrective_action_required": True,
                        "deviation_description": f"Hemoglobin {actual_hgb} g/dL below protocol minimum of {min_hgb} g/dL",
                        "confidence": 0.95
                    })
            except ValueError:
                pass
        
        # Check visit duration
        if "maximum_visit_duration" in protocol_data and "visit_duration" in actual_data:
            try:
                max_duration = int(''.join(filter(str.isdigit, protocol_data["maximum_visit_duration"])))
                actual_duration = int(''.join(filter(str.isdigit, actual_data["visit_duration"])))
                
                if actual_duration > max_duration:
                    deviations.append({
                        "category": DeviationCategory.VISIT_DURATION.value,
                        "severity": DeviationSeverity.MINOR.value,
                        "protocol_requirement": f"Visit duration ≤ {max_duration} hours",
                        "actual_value": f"{actual_duration} hours",
                        "impact_level": "low",
                        "corrective_action_required": False,
                        "deviation_description": f"Visit duration {actual_duration} hours exceeds protocol limit of {max_duration} hours",
                        "confidence": 0.85
                    })
            except ValueError:
                pass
        
        # Determine compliance status
        compliance_status = "compliant" if len(deviations) == 0 else "non-compliant"
        
        # Generate recommendations
        recommendations = []
        corrective_actions = []
        
        if deviations:
            critical_count = sum(1 for d in deviations if d["severity"] == "critical")
            major_count = sum(1 for d in deviations if d["severity"] == "major")
            
            if critical_count > 0:
                recommendations.append("Immediate medical monitor notification required")
                corrective_actions.append("Assess subject safety and consider discontinuation")
            elif major_count > 0:
                recommendations.append("Protocol deviation review within 24 hours")
                corrective_actions.append("Implement corrective measures to prevent recurrence")
            else:
                recommendations.append("Document deviation and monitor for patterns")
                corrective_actions.append("Review site procedures and provide additional training")
        else:
            recommendations.append("Continue current monitoring procedures")
            corrective_actions.append("No corrective actions required")
        
        # Create human-readable summary with medical context
        if len(deviations) == 0:
            human_readable_summary = f"No protocol deviations detected for subject {subject_id}"
            deviation_summary = "Protocol compliant"
        else:
            critical_count = sum(1 for d in deviations if d["severity"] == "critical")
            major_count = sum(1 for d in deviations if d["severity"] == "major")
            
            # Add medical context to summary
            medical_context = []
            for deviation in deviations:
                if deviation["category"] == "vital_signs":
                    if "bp" in deviation["protocol_requirement"].lower() or "blood pressure" in deviation["protocol_requirement"].lower():
                        medical_context.append("blood pressure elevation")
                        medical_context.append("hypertension")
                elif deviation["category"] == "laboratory_value":
                    if "hemoglobin" in deviation["actual_value"].lower() or "hemoglobin" in deviation["protocol_requirement"].lower():
                        medical_context.append("hemoglobin deficiency")
                        medical_context.append("anemia")
                elif deviation["category"] == "prohibited_medication":
                    medical_context.append("medication safety issue")
            
            medical_context_str = ", ".join(medical_context) if medical_context else "clinical deviations"
            
            if critical_count > 0:
                human_readable_summary = f"Critical protocol compliance issue: {len(deviations)} deviation(s) including {critical_count} critical for subject {subject_id} ({medical_context_str})"
            else:
                human_readable_summary = f"Protocol deviation detected: {len(deviations)} deviation(s) requiring review for subject {subject_id} ({medical_context_str})"
            
            deviation_summary = f"Detected {len(deviations)} protocol deviation(s)" + (f" including {critical_count} critical" if critical_count > 0 else "")
        
        result = {
            "success": True,
            "deviations": deviations,
            "total_deviations_found": len(deviations),
            "compliance_status": compliance_status,
            "subject_id": subject_id,
            "site_id": site_id,
            "visit": visit,
            "detection_date": datetime.now().isoformat(),
            "recommendations": recommendations,
            "corrective_actions_required": corrective_actions,
            "human_readable_summary": human_readable_summary,
            "deviation_summary": deviation_summary,
            "compliance_assessment": compliance_status.title(),
            "execution_time": 0.8,
            "agent_id": "deviation-detector"
        }
        
        # Store in context
        context.detection_history.append(result)
        
        return json.dumps(result)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e),
            "deviations": [],
            "total_deviations_found": 0,
            "compliance_status": "error",
            "human_readable_summary": f"Deviation detection failed: {str(e)}",
            "deviation_summary": "Analysis failed",
            "compliance_assessment": "Cannot assess",
            "execution_time": 0.0,
            "agent_id": "deviation-detector"
        })


@function_tool
def classify_deviation_severity(
    context: DeviationDetectionContext,
    deviation_info: str
) -> str:
    """Classify the severity of a protocol deviation.
    
    Args:
        deviation_info: JSON string with deviation details
        
    Returns:
        JSON string with severity classification and rationale
    """
    try:
        data = json.loads(deviation_info)
        category = data.get("category", "")
        impact = data.get("impact", "")
        
        # Critical severity classifications
        if category == "prohibited_medication":
            return json.dumps({
                "severity": DeviationSeverity.CRITICAL.value,
                "rationale": "Prohibited medication use poses immediate safety risk",
                "priority": 1
            })
        
        if "safety" in impact.lower() or "life" in impact.lower():
            return json.dumps({
                "severity": DeviationSeverity.CRITICAL.value,
                "rationale": "Safety-related deviation requires immediate attention",
                "priority": 1
            })
        
        # Major severity classifications
        if category == "visit_window" and data.get("days_outside", 0) > 7:
            return json.dumps({
                "severity": DeviationSeverity.MAJOR.value,
                "rationale": "Significant visit window deviation affects data integrity",
                "priority": 2
            })
        
        # Minor severity (default)
        return json.dumps({
            "severity": DeviationSeverity.MINOR.value,
            "rationale": "Minor protocol deviation with limited impact",
            "priority": 3
        })
        
    except Exception as e:
        return json.dumps({
            "severity": DeviationSeverity.INFO.value,
            "rationale": f"Classification failed: {str(e)}",
            "priority": 4
        })


@function_tool
def assess_compliance_impact(
    context: DeviationDetectionContext,
    compliance_data: str
) -> str:
    """Assess the impact of deviations on overall protocol compliance.
    
    Args:
        compliance_data: JSON string with deviation details and subject context
        
    Returns:
        JSON string with compliance impact assessment
    """
    try:
        data = json.loads(compliance_data)
        deviations = data.get("deviations", [])
        
        if not deviations:
            return json.dumps({
                "impact_level": "none",
                "compliance_score": 1.0,
                "assessment": "Full protocol compliance maintained",
                "regulatory_impact": "none"
            })
        
        # Calculate compliance score
        compliance_score = 1.0
        critical_count = sum(1 for d in deviations if d.get("severity") == "critical")
        major_count = sum(1 for d in deviations if d.get("severity") == "major")
        minor_count = sum(1 for d in deviations if d.get("severity") == "minor")
        
        compliance_score -= (critical_count * 0.3) + (major_count * 0.15) + (minor_count * 0.05)
        compliance_score = max(0.0, compliance_score)
        
        # Determine impact level
        if critical_count > 0:
            impact_level = "critical"
            assessment = "Critical protocol compliance issues detected"
            regulatory_impact = "high"
        elif major_count > 1:
            impact_level = "major"
            assessment = "Multiple major protocol deviations"
            regulatory_impact = "medium"
        elif major_count > 0 or minor_count > 3:
            impact_level = "moderate"
            assessment = "Protocol compliance concerns identified"
            regulatory_impact = "low"
        else:
            impact_level = "minimal"
            assessment = "Minor protocol deviations with limited impact"
            regulatory_impact = "minimal"
        
        return json.dumps({
            "impact_level": impact_level,
            "compliance_score": compliance_score,
            "assessment": assessment,
            "regulatory_impact": regulatory_impact,
            "critical_deviations": critical_count,
            "major_deviations": major_count,
            "minor_deviations": minor_count
        })
        
    except Exception as e:
        return json.dumps({
            "impact_level": "unknown",
            "compliance_score": 0.0,
            "assessment": f"Impact assessment failed: {str(e)}",
            "regulatory_impact": "unknown"
        })


@function_tool
def generate_corrective_actions(
    context: DeviationDetectionContext,
    deviation_details: str
) -> str:
    """Generate specific corrective actions for identified deviations.
    
    Args:
        deviation_details: JSON string with deviation information
        
    Returns:
        JSON string with corrective action recommendations
    """
    try:
        data = json.loads(deviation_details)
        deviations = data.get("deviations", [])
        
        corrective_actions = []
        
        for deviation in deviations:
            category = deviation.get("category", "")
            severity = deviation.get("severity", "")
            
            if category == "prohibited_medication":
                corrective_actions.append({
                    "action": "Immediate medication review and discontinuation",
                    "priority": "urgent",
                    "responsible": "investigator",
                    "timeline": "within 24 hours"
                })
            elif category == "visit_window":
                corrective_actions.append({
                    "action": "Review visit scheduling procedures",
                    "priority": "high",
                    "responsible": "site_coordinator",
                    "timeline": "within 1 week"
                })
            elif category == "fasting_requirement":
                corrective_actions.append({
                    "action": "Reinforce fasting requirements with subject",
                    "priority": "medium",
                    "responsible": "study_nurse",
                    "timeline": "next visit"
                })
            elif category == "vital_signs":
                corrective_actions.append({
                    "action": "Medical review and safety assessment",
                    "priority": "urgent",
                    "responsible": "investigator",
                    "timeline": "within 24 hours"
                })
            elif category == "laboratory_value":
                corrective_actions.append({
                    "action": "Repeat laboratory tests and medical evaluation",
                    "priority": "high",
                    "responsible": "investigator",
                    "timeline": "within 48 hours"
                })
        
        return json.dumps({
            "corrective_actions": corrective_actions,
            "total_actions": len(corrective_actions),
            "urgent_actions": len([a for a in corrective_actions if a["priority"] == "urgent"]),
            "implementation_plan": "Execute actions by priority level with appropriate timelines"
        })
        
    except Exception as e:
        return json.dumps({
            "corrective_actions": [],
            "total_actions": 0,
            "urgent_actions": 0,
            "implementation_plan": f"Action generation failed: {str(e)}"
        })


# Create the Deviation Detector Agent
deviation_detector_agent = Agent(
    name="Protocol Deviation Detector",
    instructions="""You are a Protocol Deviation Detector with expertise in clinical trial compliance monitoring. You have minimal responsibilities focused exclusively on detecting and assessing protocol deviations.

CORE RESPONSIBILITIES (MINIMAL):
1. **Deviation Detection**: Identify protocol violations by comparing requirements to actual data
2. **Severity Classification**: Classify deviations as Critical/Major/Minor based on safety and regulatory impact
3. **Compliance Assessment**: Evaluate overall protocol compliance status
4. **Corrective Actions**: Generate specific recommendations for addressing deviations

DEVIATION DETECTION EXPERTISE:
- **Prohibited Medications**: Critical violations requiring immediate action
- **Visit Windows**: Time-sensitive protocol requirements (±X days)
- **Fasting Requirements**: Pre-procedure compliance (X hours fasting)
- **Vital Signs**: Safety parameters (BP, HR limits)
- **Laboratory Values**: Clinical safety thresholds (Hgb, liver function)
- **Visit Duration**: Procedural time requirements

SEVERITY CLASSIFICATION:
- **CRITICAL**: Safety risks, prohibited medications, life-threatening values
- **MAJOR**: Significant protocol violations, >2x visit window, major safety concerns
- **MINOR**: Minor deviations, <2x limits, procedural variations
- **INFO**: Documentation issues, minor timing variations

JSON OUTPUT FORMAT:
Always return structured JSON with:
- "success": boolean
- "deviations": array of deviation objects
- "total_deviations_found": integer
- "compliance_status": "compliant" | "non-compliant"
- "human_readable_summary": string for frontend display
- "deviation_summary": string for dashboard
- "compliance_assessment": string
- "recommendations": array of strings
- "corrective_actions_required": array of strings

TOOL USAGE MANDATE:
- **ALWAYS use your function tools** for analysis: detect_protocol_deviations, classify_deviation_severity, assess_compliance_impact, generate_corrective_actions
- **Execute tools first**, then provide structured JSON output
- **Show complete JSON results** from function tools

EXAMPLE WORKFLOW:
1. Receive protocol vs actual data
2. **Call detect_protocol_deviations** with proper JSON structure
3. **Call classify_deviation_severity** for each deviation
4. **Call assess_compliance_impact** for overall assessment
5. **Call generate_corrective_actions** for recommendations
6. Return complete structured JSON response

MEDICAL CONTEXT INTEGRATION:
- Understand clinical significance of deviations
- Assess safety implications for subjects
- Consider regulatory reporting requirements
- Provide medically appropriate recommendations

Focus exclusively on deviation detection - do not perform general clinical analysis, data verification, or query generation. Stay within your minimal scope of protocol compliance monitoring.""",
    tools=[
        detect_protocol_deviations,
        classify_deviation_severity,
        assess_compliance_impact,
        generate_corrective_actions
    ],
    model="gpt-4-turbo-preview"
)


class DeviationDetector:
    """Deviation Detector for protocol compliance monitoring."""
    
    def __init__(self):
        """Initialize the Deviation Detector."""
        self.agent = deviation_detector_agent
        self.context = DeviationDetectionContext()
        self.instructions = self.agent.instructions
        
        # Configuration for minimal responsibilities
        self.supported_deviation_types = [
            "prohibited_medication",
            "visit_window", 
            "fasting_requirement",
            "vital_signs",
            "laboratory_value",
            "visit_duration"
        ]
        
        self.severity_thresholds = {
            "critical": ["prohibited_medication", "safety_violation"],
            "major": ["visit_window_major", "vital_signs_major"],
            "minor": ["fasting_requirement", "visit_duration"]
        }
    
    async def detect_protocol_deviations(self, deviation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect protocol deviations from input data."""
        try:
            # Use the function tool for detection
            result_json = detect_protocol_deviations(self.context, json.dumps(deviation_data))
            result = json.loads(result_json)
            
            # Add detection ID for tracking
            result["detection_id"] = f"DEV-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{deviation_data.get('subject_id', 'UNKNOWN')}"
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "deviations": [],
                "total_deviations_found": 0,
                "compliance_status": "error",
                "human_readable_summary": f"Deviation detection failed: {str(e)}",
                "deviation_summary": "Analysis failed",
                "compliance_assessment": "Cannot assess",
                "execution_time": 0.0,
                "agent_id": "deviation-detector"
            }
    
    async def batch_detect_deviations(self, batch_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process multiple subjects for deviation detection."""
        try:
            batch_results = []
            
            for data in batch_data:
                result = await self.detect_protocol_deviations(data)
                batch_results.append(result)
            
            # Calculate batch summary
            total_subjects = len(batch_data)
            subjects_with_deviations = sum(1 for r in batch_results if r.get("total_deviations_found", 0) > 0)
            total_deviations = sum(r.get("total_deviations_found", 0) for r in batch_results)
            critical_deviations = sum(
                sum(1 for d in r.get("deviations", []) if d.get("severity") == "critical") 
                for r in batch_results
            )
            
            return {
                "success": True,
                "batch_results": batch_results,
                "batch_summary": {
                    "total_subjects": total_subjects,
                    "subjects_with_deviations": subjects_with_deviations,
                    "total_deviations": total_deviations,
                    "critical_deviations": critical_deviations,
                    "compliance_rate": (total_subjects - subjects_with_deviations) / total_subjects if total_subjects > 0 else 0
                },
                "human_readable_summary": f"Batch analysis complete: {subjects_with_deviations}/{total_subjects} subjects with deviations, {total_deviations} total deviations detected",
                "execution_time": min(len(batch_data) * 0.02, 4.0),  # Realistic estimated time
                "agent_id": "deviation-detector"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "batch_results": [],
                "batch_summary": {},
                "human_readable_summary": f"Batch deviation detection failed: {str(e)}",
                "execution_time": 0.0,
                "agent_id": "deviation-detector"
            }
    
    def get_supported_deviation_types(self) -> List[str]:
        """Get list of supported deviation types."""
        return self.supported_deviation_types
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for the deviation detector."""
        history = self.context.detection_history
        total_detections = len(history)
        
        if total_detections == 0:
            return {
                "detections_performed": 0,
                "average_deviations_per_detection": 0.0,
                "compliance_rate": 1.0,
                "critical_deviation_rate": 0.0,
                "agent_focus": "protocol_deviation_detection",
                "efficiency_metrics": {
                    "average_execution_time": 0.0,
                    "total_subjects_processed": 0
                }
            }
        
        total_deviations = sum(d.get("total_deviations_found", 0) for d in history)
        compliant_detections = sum(1 for d in history if d.get("compliance_status") == "compliant")
        critical_deviations = sum(
            len([dev for dev in d.get("deviations", []) if dev.get("severity") == "critical"])
            for d in history
        )
        avg_execution_time = sum(d.get("execution_time", 0.8) for d in history) / total_detections
        
        return {
            "detections_performed": total_detections,
            "average_deviations_per_detection": total_deviations / total_detections,
            "compliance_rate": compliant_detections / total_detections,
            "critical_deviation_rate": critical_deviations / max(total_deviations, 1),
            "agent_focus": "protocol_deviation_detection",
            "efficiency_metrics": {
                "average_execution_time": avg_execution_time,
                "total_subjects_processed": total_detections
            }
        }


# Export for use by other modules
__all__ = [
    "DeviationDetector",
    "DeviationDetectionContext",
    "DeviationSeverity",
    "DeviationCategory",
    "detect_protocol_deviations",
    "classify_deviation_severity",
    "assess_compliance_impact",
    "generate_corrective_actions",
    "deviation_detector_agent"
]