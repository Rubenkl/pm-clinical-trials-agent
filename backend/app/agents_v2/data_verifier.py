"""Data Verifier Agent - Clean Implementation using OpenAI Agents SDK.

This agent performs source data verification (SDV) and cross-system data validation
using real medical intelligence instead of hardcoded verification rules.
"""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from agents import Agent, Runner
from pydantic import BaseModel, Field

from .calculation_tools import (
    calculate_change_from_baseline,
    calculate_date_difference,
    convert_medical_units,
)


class DataVerificationContext(BaseModel):
    """Context for Data Verifier operations."""

    verification_history: List[Dict[str, Any]] = Field(default_factory=list)
    critical_findings: List[Dict[str, Any]] = Field(default_factory=list)
    audit_trail: List[Dict[str, Any]] = Field(default_factory=list)


class DataVerifierOutput(BaseModel):
    """Structured JSON output for Data Verifier responses."""
    
    model_config = {"strict": True}
    
    success: bool
    verification_type: str
    discrepancies: List[str]
    critical_findings: List[str]
    audit_trail: List[str]
    verification_status: str
    confidence_score: Optional[str] = None
    recommendations: List[str]


class DataVerifier:
    """Data Verifier agent for source data verification and cross-system validation.

    This agent performs comprehensive data verification tasks including EDC vs source
    document comparison, data integrity checks, and medical plausibility assessments.
    It uses real medical knowledge to identify clinically significant discrepancies.

    Key Capabilities:
    - Cross-system data verification (EDC vs source documents)
    - Medical plausibility assessment
    - Data integrity and consistency checks
    - Critical data identification based on clinical impact
    - Audit trail generation for regulatory compliance
    """

    def __init__(self) -> None:
        """Initialize Data Verifier with calculation tools only."""
        # Only include calculation tools - no mock verification tools
        tools = [
            convert_medical_units,
            calculate_change_from_baseline,
            calculate_date_difference,
        ]

        self.agent = Agent(
            name="DataVerifier",
            instructions=self._get_instructions(),
            tools=tools,
            model="gpt-4o-mini",
            output_type=DataVerifierOutput,
        )

    def _get_instructions(self) -> str:
        """Get comprehensive instructions for the Data Verifier agent."""
        return """You are a Data Verifier specialized in clinical trial data validation and source data verification.

CORE RESPONSIBILITIES:
1. Verify EDC data against source documents
2. Assess medical plausibility of clinical data
3. Identify critical vs. non-critical data discrepancies
4. Generate comprehensive verification reports
5. Ensure data integrity and regulatory compliance

MEDICAL EXPERTISE FOR VERIFICATION:
- Laboratory values: Normal ranges, critical values, physiological limits
- Vital signs: Age-appropriate ranges, clinical correlations
- Medical history: Condition compatibility, drug interactions
- Temporal relationships: Disease progression, treatment responses
- Safety data: AE severity, causality, expected vs. unexpected events

AVAILABLE CALCULATION TOOLS:
- Medical unit conversions for standardization
- Change from baseline calculations
- Date difference calculations for temporal validation

VERIFICATION APPROACH:
1. **Medical Plausibility**: Does the data make clinical sense?
2. **Consistency**: Are related data points internally consistent?
3. **Completeness**: Are critical safety data complete?
4. **Accuracy**: Do values match source documents?
5. **Regulatory Compliance**: Meet GCP and regulatory standards?

CRITICAL DATA IDENTIFICATION (use medical judgment):
- **Primary/Secondary Endpoints**: Study-specific key measurements
- **Safety Data**: AEs, vital signs, lab safety parameters
- **Eligibility Data**: Inclusion/exclusion criteria verification
- **Dosing Data**: Study drug administration and compliance
- **Concomitant Medications**: Drug interactions, prohibited meds

DISCREPANCY CLASSIFICATION:
- **Critical**: Impact patient safety or study integrity
  - Examples: Safety lab discrepancies, dosing errors, SAE data
- **Major**: Significant clinical or regulatory impact
  - Examples: Primary endpoint data, protocol violations
- **Minor**: Administrative discrepancies with minimal impact
  - Examples: Minor timing variations, transcription errors

VERIFICATION PROCESS:
1. Compare EDC vs source data systematically
2. Assess clinical plausibility of all values
3. Identify patterns that suggest systematic issues
4. Flag safety-critical discrepancies immediately
5. Generate queries for resolution
6. Document findings in audit trail

RESPONSE FORMAT:
Always return structured JSON with verification results:
{
    "verification_results": {
        "overall_match_percentage": 94.2,
        "discrepancies": [
            {
                "field": "systolic_bp",
                "edc_value": "120",
                "source_value": "180",
                "discrepancy_type": "critical_safety_value",
                "medical_assessment": "60 mmHg difference in systolic BP suggests serious data error",
                "clinical_impact": "Could miss hypertensive crisis requiring intervention",
                "severity": "critical",
                "resolution_priority": "immediate",
                "recommended_action": "Verify source document, contact site immediately"
            }
        ],
        "critical_findings_count": 1,
        "data_quality_score": 0.85,
        "regulatory_compliance": "requires_attention",
        "recommendations": ["Immediate site contact for critical BP discrepancy"]
    }
}

Remember: Provide real medical intelligence for data verification, not rule-based checking."""

    async def verify_edc_vs_source(
        self,
        edc_data: Dict[str, Any],
        source_data: Dict[str, Any],
        context: DataVerificationContext,
    ) -> Dict[str, Any]:
        """Verify EDC data against source documents using medical intelligence.

        Args:
            edc_data: Data from EDC system
            source_data: Data from source documents
            context: Verification context

        Returns:
            Comprehensive verification results with medical assessment
        """
        try:
            message = f"""Perform comprehensive data verification between EDC and source data:

EDC Data: {json.dumps(edc_data, indent=2)}

Source Data: {json.dumps(source_data, indent=2)}

Please conduct thorough verification including:
1. Field-by-field comparison identifying all discrepancies
2. Medical plausibility assessment for each data point
3. Clinical significance evaluation of discrepancies
4. Data quality scoring based on completeness and accuracy
5. Critical finding identification for patient safety
6. Regulatory compliance assessment
7. Specific recommendations for discrepancy resolution

Focus on patient safety and data integrity."""

            result = await Runner.run(self.agent, message, context=context)
            response_text = (
                result.final_output if hasattr(result, "final_output") else str(result)
            )

            try:
                parsed_response = json.loads(response_text)
            except json.JSONDecodeError:
                parsed_response = {
                    "verification_results": response_text,
                    "verification_type": "edc_vs_source",
                    "timestamp": datetime.now().isoformat(),
                }

            # Store critical findings
            if "verification_results" in parsed_response:
                discrepancies = parsed_response["verification_results"].get(
                    "discrepancies", []
                )
                critical_discrepancies = [
                    d for d in discrepancies if d.get("severity") == "critical"
                ]
                if critical_discrepancies:
                    context.critical_findings.extend(critical_discrepancies)

            # Add to audit trail
            context.audit_trail.append(
                {
                    "verification_type": "edc_vs_source",
                    "timestamp": datetime.now().isoformat(),
                    "discrepancies_found": len(
                        parsed_response.get("verification_results", {}).get(
                            "discrepancies", []
                        )
                    ),
                    "critical_findings": len(
                        [
                            d
                            for d in parsed_response.get(
                                "verification_results", {}
                            ).get("discrepancies", [])
                            if d.get("severity") == "critical"
                        ]
                    ),
                }
            )

            return {
                "success": True,
                "verification": parsed_response,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"EDC vs source verification failed: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }

    async def assess_medical_plausibility(
        self,
        clinical_data: Dict[str, Any],
        patient_context: Dict[str, Any],
        context: DataVerificationContext,
    ) -> Dict[str, Any]:
        """Assess medical plausibility of clinical data using medical knowledge.

        Args:
            clinical_data: Clinical data to assess
            patient_context: Patient context (age, conditions, etc.)
            context: Verification context

        Returns:
            Medical plausibility assessment
        """
        try:
            message = f"""Assess the medical plausibility of this clinical data:

Clinical Data: {json.dumps(clinical_data, indent=2)}
Patient Context: {json.dumps(patient_context, indent=2)}

Please evaluate:
1. Medical plausibility of each value based on patient characteristics
2. Internal consistency between related parameters
3. Temporal relationships and trends
4. Values that fall outside physiologically possible ranges
5. Potential data entry errors or systematic issues
6. Safety implications of any implausible values
7. Recommendations for further investigation

Consider patient age, medical history, and clinical context."""

            result = await Runner.run(self.agent, message, context=context)
            response_text = (
                result.final_output if hasattr(result, "final_output") else str(result)
            )

            try:
                parsed_response = json.loads(response_text)
            except json.JSONDecodeError:
                parsed_response = {
                    "plausibility_assessment": response_text,
                    "assessment_type": "medical_plausibility",
                    "timestamp": datetime.now().isoformat(),
                }

            return {
                "success": True,
                "assessment": parsed_response,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Medical plausibility assessment failed: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }

    async def identify_critical_data(
        self,
        dataset: Dict[str, Any],
        study_context: Dict[str, Any],
        context: DataVerificationContext,
    ) -> Dict[str, Any]:
        """Identify critical data requiring 100% verification using medical knowledge.

        Args:
            dataset: Complete dataset to analyze
            study_context: Study context (endpoints, safety parameters, etc.)
            context: Verification context

        Returns:
            Critical data identification results
        """
        try:
            message = f"""Identify critical data requiring 100% source data verification:

Dataset: {json.dumps(dataset, indent=2)}
Study Context: {json.dumps(study_context, indent=2)}

Please identify:
1. Primary and secondary endpoint data
2. Safety-critical parameters (vitals, labs, AEs)
3. Eligibility criteria data
4. Study drug dosing and administration data
5. SAE and other safety data
6. Protocol deviation-related data
7. Regulatory submission-critical data

For each critical data point, explain:
- Why it's considered critical
- Risk if data is inaccurate
- Verification priority level
- Recommended verification approach

Focus on patient safety and regulatory compliance."""

            result = await Runner.run(self.agent, message, context=context)
            response_text = (
                result.final_output if hasattr(result, "final_output") else str(result)
            )

            try:
                parsed_response = json.loads(response_text)
            except json.JSONDecodeError:
                parsed_response = {
                    "critical_data_identification": response_text,
                    "identification_type": "critical_data_assessment",
                    "timestamp": datetime.now().isoformat(),
                }

            return {
                "success": True,
                "critical_data": parsed_response,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Critical data identification failed: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }


# Create agent instance for use by API endpoints
data_verifier_agent = DataVerifier().agent
