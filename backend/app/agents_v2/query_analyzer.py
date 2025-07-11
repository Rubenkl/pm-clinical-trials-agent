"""Query Analyzer Agent - Clean Implementation using OpenAI Agents SDK.

This agent analyzes clinical data discrepancies and generates intelligent queries
using real medical knowledge instead of hardcoded rules.
"""

import json
from datetime import datetime
from typing import Any, Dict, List

from agents import Agent, Runner
from pydantic import BaseModel, Field

from .calculation_tools import (
    calculate_age_at_visit,
    calculate_change_from_baseline,
    calculate_date_difference,
    convert_medical_units,
)


class QueryAnalysisContext(BaseModel):
    """Context for Query Analyzer operations."""

    analysis_history: List[Dict[str, Any]] = Field(default_factory=list)
    medical_terminology: Dict[str, str] = Field(default_factory=dict)
    query_patterns: List[Dict[str, Any]] = Field(default_factory=list)


class QueryAnalyzer:
    """Query Analyzer agent for clinical data analysis and query generation.

    This agent analyzes clinical trial data to identify discrepancies, assess
    clinical significance, and recommend appropriate queries. It uses real
    medical intelligence instead of hardcoded severity rules.

    Key Capabilities:
    - Clinical data interpretation using medical knowledge
    - Discrepancy severity assessment with clinical context
    - Medical terminology expansion and interpretation
    - Query prioritization based on patient safety and data integrity
    """

    def __init__(self) -> None:
        """Initialize Query Analyzer with calculation tools only."""
        # Only include calculation tools - no mock medical judgment tools
        tools = [
            convert_medical_units,
            calculate_age_at_visit,
            calculate_change_from_baseline,
            calculate_date_difference,
        ]

        self.agent = Agent(
            name="QueryAnalyzer",
            instructions=self._get_instructions(),
            tools=tools,
            model="gpt-4",
        )

    def _get_instructions(self) -> str:
        """Get comprehensive instructions for the Query Analyzer agent."""
        return """You are a Query Analyzer specialized in clinical trial data analysis.

CORE RESPONSIBILITIES:
1. Analyze clinical data for discrepancies and anomalies
2. Assess clinical significance using medical knowledge
3. Determine query priorities based on patient safety
4. Interpret medical terminology and abbreviations
5. Recommend appropriate follow-up actions

MEDICAL EXPERTISE:
You have comprehensive medical knowledge including:
- Clinical laboratory normal ranges and critical values
- Vital signs interpretation (BP, HR, temperature, respiratory rate)
- Cardiology: LVEF ranges, BNP levels, cardiac markers
- Nephrology: Creatinine, GFR, electrolyte balance
- Hematology: CBC parameters, coagulation studies
- Medical terminology and abbreviations
- Drug interactions and contraindications
- Clinical trial safety monitoring

AVAILABLE CALCULATION TOOLS:
- Medical unit conversions (mg/dL ↔ mmol/L, etc.)
- Age calculations for age-specific ranges
- Change from baseline calculations
- Date difference calculations

CRITICAL ASSESSMENT APPROACH:
1. **Patient Safety First**: Identify values that could impact patient safety
2. **Clinical Context**: Consider patient age, condition, and study phase
3. **Medical Significance**: Distinguish between statistically and clinically significant changes
4. **Regulatory Impact**: Assess impact on primary/secondary endpoints

SEVERITY CLASSIFICATION (use medical judgment):
- **CRITICAL**: Life-threatening values, safety signals, primary endpoint impact
  - Examples: BP >180/110, Hgb <6.0, Troponin elevation, SAE-related
- **MAJOR**: Clinically significant but not immediately life-threatening
  - Examples: BP 160-179/100-109, Hgb 6.0-8.0, significant lab changes
- **MINOR**: Administrative or non-clinically significant discrepancies
  - Examples: Minor timing variations, non-critical data entry errors

QUERY RECOMMENDATIONS:
For each finding, provide:
- Clinical interpretation with medical reasoning
- Severity assessment based on clinical impact
- Specific query text addressing the medical concern
- Recommended timeline for response
- Follow-up actions (investigator contact, safety review, etc.)

RESPONSE FORMAT:
Always return structured JSON with clinical assessments:
{
    "analysis": {
        "findings": [
            {
                "parameter": "systolic_bp",
                "value": "185 mmHg",
                "clinical_interpretation": "Stage 2 Hypertension - requires immediate evaluation",
                "severity": "critical",
                "medical_reasoning": "BP >180 mmHg increases risk of cardiovascular events",
                "query_recommendation": "Please verify BP reading and confirm if patient received antihypertensive treatment",
                "timeline": "immediate",
                "safety_implications": "Potential for stroke, MI, or hypertensive crisis"
            }
        ],
        "overall_assessment": "Critical safety findings require immediate attention",
        "recommended_actions": ["Contact investigator", "Safety assessment", "Consider study drug hold"]
    }
}

Remember: You provide real medical intelligence, not rule-based assessments."""

    async def analyze_clinical_data(
        self,
        clinical_data: Dict[str, Any],
        context: QueryAnalysisContext,
    ) -> Dict[str, Any]:
        """Analyze clinical data using medical intelligence.

        Args:
            clinical_data: Clinical data to analyze
            context: Analysis context

        Returns:
            Clinical analysis with medical assessments
        """
        try:
            message = f"""Analyze this clinical data using your medical expertise:

Clinical Data: {json.dumps(clinical_data, indent=2)}

Please provide comprehensive analysis including:
1. Clinical interpretation of each parameter
2. Assessment of values (normal/abnormal/critical)
3. Medical significance and patient safety implications
4. Severity classification with clinical reasoning
5. Specific query recommendations with medical context
6. Timeline for follow-up based on clinical urgency

Focus on actionable medical insights and patient safety."""

            result = await Runner.run(self.agent, message, context=context)
            response_text = (
                result.final_output if hasattr(result, "final_output") else str(result)
            )

            try:
                parsed_response = json.loads(response_text)
            except json.JSONDecodeError:
                parsed_response = {
                    "analysis": response_text,
                    "analysis_type": "clinical_data_analysis",
                    "timestamp": datetime.now().isoformat(),
                }

            # Store in context history
            context.analysis_history.append(
                {
                    "timestamp": datetime.now().isoformat(),
                    "data_summary": str(clinical_data)[:200] + "...",
                    "findings_count": len(
                        parsed_response.get("analysis", {}).get("findings", [])
                    ),
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
                "error": f"Clinical data analysis failed: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }

    async def assess_discrepancy_severity(
        self,
        edc_value: str,
        source_value: str,
        field_name: str,
        patient_context: Dict[str, Any],
        context: QueryAnalysisContext,
    ) -> Dict[str, Any]:
        """Assess the severity of a data discrepancy using medical knowledge.

        Args:
            edc_value: Value in EDC system
            source_value: Value in source document
            field_name: Name of the data field
            patient_context: Patient context (age, condition, etc.)
            context: Analysis context

        Returns:
            Severity assessment with clinical reasoning
        """
        try:
            message = f"""Assess the clinical significance of this data discrepancy:

Field: {field_name}
EDC Value: {edc_value}
Source Value: {source_value}
Patient Context: {json.dumps(patient_context, indent=2)}

Please evaluate:
1. Which value is more likely to be correct based on clinical context
2. Clinical significance of the discrepancy
3. Impact on patient safety and study integrity
4. Severity classification (critical/major/minor) with medical reasoning
5. Recommended corrective actions
6. Urgency of resolution

Consider medical plausibility, patient safety, and study endpoints."""

            result = await Runner.run(self.agent, message, context=context)
            response_text = (
                result.final_output if hasattr(result, "final_output") else str(result)
            )

            try:
                parsed_response = json.loads(response_text)
            except json.JSONDecodeError:
                parsed_response = {
                    "severity_assessment": response_text,
                    "field": field_name,
                    "edc_value": edc_value,
                    "source_value": source_value,
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
                "error": f"Severity assessment failed: {str(e)}",
                "field": field_name,
                "timestamp": datetime.now().isoformat(),
            }

    async def expand_medical_terminology(
        self,
        medical_term: str,
        context: QueryAnalysisContext,
    ) -> Dict[str, Any]:
        """Expand and interpret medical terminology using medical knowledge.

        Args:
            medical_term: Medical term or abbreviation to expand
            context: Analysis context

        Returns:
            Medical terminology expansion and interpretation
        """
        try:
            message = f"""Interpret this medical term or abbreviation: {medical_term}

Please provide:
1. Full expansion if it's an abbreviation
2. Medical definition and explanation
3. Clinical significance and context
4. Normal ranges or reference values if applicable
5. Related medical conditions or implications
6. Usage in clinical trials context

Focus on clinical relevance and practical application."""

            result = await Runner.run(self.agent, message, context=context)
            response_text = (
                result.final_output if hasattr(result, "final_output") else str(result)
            )

            try:
                parsed_response = json.loads(response_text)
            except json.JSONDecodeError:
                parsed_response = {
                    "terminology_expansion": response_text,
                    "original_term": medical_term,
                    "timestamp": datetime.now().isoformat(),
                }

            # Cache terminology for future use
            if isinstance(parsed_response, dict) and "expansion" in parsed_response:
                context.medical_terminology[medical_term] = parsed_response["expansion"]

            return {
                "success": True,
                "terminology": parsed_response,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Medical terminology expansion failed: {str(e)}",
                "term": medical_term,
                "timestamp": datetime.now().isoformat(),
            }


# Create agent instance for use by API endpoints
query_analyzer_agent = QueryAnalyzer().agent
