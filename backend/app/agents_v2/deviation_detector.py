"""Deviation Detector Agent - Clean Implementation using OpenAI Agents SDK.

This agent detects protocol deviations and compliance issues using real medical
intelligence instead of hardcoded compliance rules.
"""

import json
from datetime import datetime
from typing import Any, Dict, List

from agents import Agent, Runner
from pydantic import BaseModel, Field

from .calculation_tools import (
    calculate_age_at_visit,
    calculate_date_difference,
    check_visit_window_compliance,
)


class DeviationDetectionContext(BaseModel):
    """Context for Deviation Detector operations."""

    detection_history: List[Dict[str, Any]] = Field(default_factory=list)
    compliance_patterns: Dict[str, Any] = Field(default_factory=dict)
    deviation_trends: List[Dict[str, Any]] = Field(default_factory=list)


class DeviationDetectorOutput(BaseModel):
    """Structured JSON output for Deviation Detector responses."""

    model_config = {"strict": True}

    success: bool
    detection_type: str
    deviations: List[str]
    severity_assessment: str
    compliance_status: str
    regulatory_risk: str
    corrective_actions: List[str]
    preventive_measures: List[str]


class DeviationDetector:
    """Deviation Detector agent for protocol compliance monitoring.

    This agent identifies protocol deviations, assesses their clinical significance,
    and recommends corrective actions using real medical and regulatory knowledge
    instead of hardcoded compliance rules.

    Key Capabilities:
    - Protocol deviation detection with clinical context
    - Compliance impact assessment
    - Root cause analysis suggestions
    - Corrective action recommendations
    - Regulatory risk assessment
    """

    def __init__(self) -> None:
        """Initialize Deviation Detector with calculation tools only."""
        # Only include calculation tools - no mock compliance tools
        tools = [
            calculate_age_at_visit,
            calculate_date_difference,
            check_visit_window_compliance,
        ]

        self.agent = Agent(
            name="DeviationDetector",
            instructions=self._get_instructions(),
            tools=tools,
            model="gpt-4o-mini",
            output_type=DeviationDetectorOutput,
        )

    def _get_instructions(self) -> str:
        """Get comprehensive instructions for the Deviation Detector agent."""
        return """You are a Deviation Detector specialized in clinical trial protocol compliance monitoring.

CORE RESPONSIBILITIES:
1. Detect protocol deviations using medical and regulatory knowledge
2. Assess clinical and regulatory impact of deviations
3. Classify deviation severity based on patient safety and study integrity
4. Recommend corrective and preventive actions (CAPA)
5. Support regulatory compliance and audit readiness

REGULATORY EXPERTISE:
- ICH-GCP guidelines for clinical trial conduct
- FDA/EMA guidance on protocol deviations
- Good Clinical Practice standards
- Protocol compliance requirements
- Regulatory reporting obligations

CALCULATION TOOLS (AVOID unless absolutely necessary for math):
- Age calculations: ONLY if age not provided and must calculate from birth date
- Date calculations: ONLY if time difference not obvious from dates
- Visit window compliance: MAXIMUM ONE CALL per analysis - use only if dates are complex

ANALYSIS APPROACH:
1. **Check Age**: Is patient_age >= min_age and <= max_age?
2. **Check Visit Window**: Is visit_date within window_days of scheduled_date?  
3. **Check Medications**: Are any prohibited_meds in concomitant_meds?
4. **Check Safety Values**: Are vital signs within acceptable ranges?

DO NOT overthink - analyze data directly without excessive tool usage.

SEVERITY CLASSIFICATION (use regulatory knowledge):
- **Critical**: Impact patient safety or study validity
  - Examples: Enrollment of ineligible patient, safety lab delays, unreported SAEs
- **Major**: Significant protocol non-compliance
  - Examples: Dose administration errors, major visit window violations
- **Minor**: Administrative deviations with minimal impact
  - Examples: Minor documentation delays, non-critical timing variations

IMPACT ASSESSMENT:
For each deviation, evaluate:
- Patient safety implications
- Impact on study endpoints
- Regulatory reporting requirements
- Effect on data integrity
- Need for immediate action

RESPONSE FORMAT:
You MUST return a response that exactly matches this structure:
{
    "success": true,
    "detection_type": "protocol_deviation_analysis",
    "deviations": [
        "Patient age 17.8 years at enrollment (protocol requires ≥18 years)",
        "Visit conducted 5 days outside protocol window",
        "Missed safety lab collection at baseline"
    ],
    "severity_assessment": "critical",
    "compliance_status": "major_violations_detected",
    "regulatory_risk": "high_risk_immediate_action_required",
    "corrective_actions": [
        "Remove ineligible patient from study immediately",
        "Notify IRB/EC within 24 hours",
        "Report to regulatory authorities",
        "Implement enhanced eligibility verification"
    ],
    "preventive_measures": [
        "Additional site training on inclusion criteria",
        "Enhanced pre-enrollment verification checklist",
        "Real-time eligibility review process"
    ]
}

IMPORTANT:
- Use calculation tools SPARINGLY and only for actual mathematical calculations
- Do NOT call the same tool multiple times with similar data
- For visit windows: call check_visit_window_compliance ONCE per visit maximum
- Focus on regulatory and medical assessment using your clinical knowledge first
- Return the exact JSON structure above - no nested objects

TOOL USAGE GUIDELINES:
- If visit date and scheduled date are provided, you may use visit window tool ONCE
- If only dates are provided without needing calculation, analyze them directly
- Don't use tools for obvious deviations that don't require calculation

Remember: Use real regulatory and medical knowledge for deviation assessment."""

    async def detect_protocol_deviations(
        self,
        study_data: Dict[str, Any],
        protocol_requirements: Dict[str, Any],
        context: DeviationDetectionContext,
    ) -> Dict[str, Any]:
        """Detect protocol deviations using regulatory and medical knowledge.

        Args:
            study_data: Current study data to evaluate
            protocol_requirements: Protocol requirements and criteria
            context: Detection context

        Returns:
            Comprehensive deviation analysis
        """
        try:
            message = f"""Analyze this study data for protocol deviations:

Study Data: {json.dumps(study_data, indent=2)}
Protocol Requirements: {json.dumps(protocol_requirements, indent=2)}

Please conduct comprehensive deviation detection including:
1. Inclusion/exclusion criteria compliance verification
2. Visit timing and window compliance assessment
3. Dosing and administration compliance review
4. Safety monitoring compliance evaluation
5. Required procedure and assessment completion
6. Regulatory timeline compliance (AE reporting, etc.)

For each deviation found, provide:
- Clear description of the deviation
- Severity classification with regulatory rationale
- Patient safety and study integrity impact
- Immediate corrective actions required
- CAPA recommendations for prevention
- Regulatory reporting requirements

Focus on patient safety and regulatory compliance."""

            result = await Runner.run(self.agent, message, context=context)
            response_text = (
                result.final_output if hasattr(result, "final_output") else str(result)
            )

            try:
                parsed_response = json.loads(response_text)
            except json.JSONDecodeError:
                parsed_response = {
                    "deviation_analysis": response_text,
                    "analysis_type": "protocol_deviation_detection",
                    "timestamp": datetime.now().isoformat(),
                }

            # Track deviation patterns
            if "deviation_analysis" in parsed_response:
                deviations = parsed_response["deviation_analysis"].get(
                    "deviations_detected", []
                )
                for deviation in deviations:
                    context.deviation_trends.append(
                        {
                            "type": deviation.get("deviation_type"),
                            "severity": deviation.get("severity"),
                            "timestamp": datetime.now().isoformat(),
                        }
                    )

            return {
                "success": True,
                "analysis": parsed_response,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Protocol deviation detection failed: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }

    async def assess_compliance_impact(
        self,
        deviation_details: Dict[str, Any],
        study_context: Dict[str, Any],
        context: DeviationDetectionContext,
    ) -> Dict[str, Any]:
        """Assess the compliance impact of detected deviations.

        Args:
            deviation_details: Details of the deviation
            study_context: Study context and objectives
            context: Detection context

        Returns:
            Compliance impact assessment
        """
        try:
            message = f"""Assess the compliance impact of this protocol deviation:

Deviation Details: {json.dumps(deviation_details, indent=2)}
Study Context: {json.dumps(study_context, indent=2)}

Please evaluate:
1. Regulatory compliance implications
2. Impact on study objectives and endpoints
3. Patient safety considerations
4. Data integrity and validity effects
5. Audit and inspection risks
6. Corrective action urgency and scope
7. Preventive measures to avoid recurrence

Provide specific recommendations for:
- Immediate corrective actions
- Communication requirements (IRB, regulatory, sponsor)
- Documentation and reporting needs
- Monitoring enhancements
- Training or process improvements

Consider ICH-GCP and regulatory guidance."""

            result = await Runner.run(self.agent, message, context=context)
            response_text = (
                result.final_output if hasattr(result, "final_output") else str(result)
            )

            try:
                parsed_response = json.loads(response_text)
            except json.JSONDecodeError:
                parsed_response = {
                    "compliance_impact": response_text,
                    "assessment_type": "compliance_impact_assessment",
                    "timestamp": datetime.now().isoformat(),
                }

            return {
                "success": True,
                "impact_assessment": parsed_response,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Compliance impact assessment failed: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }


# Create agent instance for use by API endpoints
deviation_detector_agent = DeviationDetector().agent
