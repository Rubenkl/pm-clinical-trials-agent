"""Portfolio Manager Agent - Clean Implementation using OpenAI Agents SDK.

This agent orchestrates clinical trial workflows without mock medical judgments.
It uses real AI intelligence via Runner.run() for clinical reasoning and coordinates
with specialized agents through handoffs.
"""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from agents import Agent, Runner, handoff
from pydantic import BaseModel, Field

from .calculation_tools import (
    calculate_age_at_visit,
    calculate_body_surface_area,
    calculate_change_from_baseline,
    calculate_creatinine_clearance,
    calculate_date_difference,
    check_visit_window_compliance,
    convert_medical_units,
)
from .test_data_tools import get_subject_discrepancies, get_test_subject_data

# Import specialist agents for handoffs
from .query_analyzer import query_analyzer_agent
from .data_verifier import data_verifier_agent
from .deviation_detector import deviation_detector_agent
from .query_generator import query_generator_agent
from .query_tracker import query_tracker_agent
from .analytics_agent import analytics_agent


class WorkflowContext(BaseModel):
    """Context for Portfolio Manager workflow orchestration."""

    active_workflows: Dict[str, Any] = Field(default_factory=dict)
    completed_workflows: List[Dict[str, Any]] = Field(default_factory=list)
    performance_metrics: Dict[str, Any] = Field(default_factory=dict)
    agent_handoffs: List[Dict[str, Any]] = Field(default_factory=list)


class PortfolioManagerOutput(BaseModel):
    """Structured JSON output for Portfolio Manager responses."""

    model_config = {"strict": True}

    success: bool
    workflow_type: str
    clinical_assessment: Optional[str] = None
    findings: List[str]
    severity: Optional[str] = None
    safety_implications: Optional[str] = None
    recommended_actions: List[str]
    workflow_next_steps: List[str]
    priority: Optional[str] = None
    execution_time: Optional[str] = None


class PortfolioManager:
    """Portfolio Manager agent for clinical trial workflow orchestration.

    This agent serves as the central coordinator for multi-agent clinical workflows.
    It orchestrates complex clinical operations by delegating to specialized agents
    and ensuring proper workflow execution without making mock medical judgments.

    Key Responsibilities:
    - Workflow planning and orchestration
    - Agent coordination and handoffs
    - Context management across workflows
    - Performance monitoring and reporting

    Function Tools Available:
    - All calculation tools for mathematical operations
    - Test data tools for development/testing scenarios
    - NO mock medical judgment tools
    """

    def __init__(self) -> None:
        """Initialize Portfolio Manager with clean tool set."""
        # Only include legitimate calculation and test data tools
        tools = [
            # Calculation tools (pure mathematics)
            convert_medical_units,
            calculate_age_at_visit,
            check_visit_window_compliance,
            calculate_change_from_baseline,
            calculate_body_surface_area,
            calculate_creatinine_clearance,
            calculate_date_difference,
            # Test data tools (for development)
            get_test_subject_data,
            get_subject_discrepancies,
        ]

        self.agent = Agent(
            name="PortfolioManager",
            instructions=self._get_instructions(),
            tools=tools,
            handoffs=[
                handoff(query_analyzer_agent, tool_name_override="transfer_to_query_analyzer"),
                handoff(data_verifier_agent, tool_name_override="transfer_to_data_verifier"),
                handoff(deviation_detector_agent, tool_name_override="transfer_to_deviation_detector"),
                handoff(query_generator_agent, tool_name_override="transfer_to_query_generator"),
                handoff(query_tracker_agent, tool_name_override="transfer_to_query_tracker"),
                handoff(analytics_agent, tool_name_override="transfer_to_analytics_agent"),
            ],
            model="gpt-4o-mini",
            output_type=PortfolioManagerOutput,
        )

    def _get_instructions(self) -> str:
        """Get comprehensive instructions for the Portfolio Manager agent."""
        return """You are the Portfolio Manager for a clinical trials automation platform.

CORE RESPONSIBILITIES:
1. **Input Validation**: First check if sufficient data is provided for meaningful analysis
2. **Intelligent Triage**: Analyze valid input and determine what expertise is needed
3. **Smart Delegation**: Use handoffs to transfer control to specialist agents when their expertise is required
4. **Direct Analysis**: Perform analysis yourself when specialist expertise isn't needed
5. **Result Integration**: When multiple specialists are needed, coordinate their work
6. **Quality Assessment**: Evaluate results and determine if additional expertise is needed

CRITICAL RULE - INSUFFICIENT DATA HANDLING:
If input lacks specific clinical data, subject details, or clear analysis requirements:
→ Return immediate response explaining what data is needed
→ Do NOT use tools to explore or gather missing data
→ Do NOT make speculative tool calls
→ Do NOT try to "do something anyway"

AVAILABLE SPECIALIST AGENTS (via handoffs):
- **transfer_to_query_analyzer**: For clinical data analysis and discrepancy assessment
- **transfer_to_data_verifier**: For EDC vs source document verification
- **transfer_to_deviation_detector**: For protocol compliance and regulatory analysis
- **transfer_to_query_generator**: For professional clinical query creation
- **transfer_to_query_tracker**: For query lifecycle and SLA management
- **transfer_to_analytics_agent**: For performance analytics and operational insights

DELEGATION DECISION LOGIC:
- **Simple clinical assessment**: Do it yourself using medical knowledge
- **Complex data analysis with multiple discrepancies**: → transfer_to_query_analyzer
- **Data verification between systems**: → transfer_to_data_verifier
- **Protocol compliance evaluation**: → transfer_to_deviation_detector
- **Query creation needed**: → transfer_to_query_generator
- **Query management/tracking**: → transfer_to_query_tracker  
- **Performance analysis**: → transfer_to_analytics_agent
- **Multiple specialties needed**: Handle coordination yourself, use handoffs as needed

TOOL USAGE RULES (STRICTLY ENFORCE):
1. **NEVER use tools for exploration or "see what happens"**
2. **ONLY use tools when you have specific data requiring calculation**
3. **MAXIMUM 1-2 tool calls per request (for verification only)**

CALCULATION TOOLS (use sparingly for specific needs):
- Medical unit conversion tools (when units need conversion)
- Age and date calculation tools (when age/date math needed)
- Visit window compliance checking (when verifying specific borderline dates)
- Change from baseline calculations (when trend analysis requested)
- Body surface area calculations (when BSA calculation needed)
- Creatinine clearance calculations (when kidney function assessment needed)
- Test data retrieval (ONLY when specific subject data clearly requested)

WHEN NOT TO USE TOOLS:
❌ Input is vague or asks "what can you do"
❌ No specific clinical data provided
❌ Empty data arrays or missing information
❌ General questions without clinical context
❌ Requests that lack clear analytical requirements

CRITICAL: You do NOT have mock medical judgment tools. Instead:
- Use your medical knowledge directly for clinical assessments
- Leverage calculation tools ONLY for mathematical operations on provided data
- Coordinate with specialized agents for complex analyses
- Make real medical reasoning based on clinical data
- If insufficient data → explain what's needed without using tools

WORKFLOW TYPES TO SUPPORT:
1. Comprehensive Clinical Analysis
2. Query Resolution Workflows
3. Data Verification Processes
4. Protocol Deviation Detection
5. Patient Safety Assessments

MEDICAL CONTEXT:
You have extensive medical knowledge including:
- Cardiology: BP ranges, BNP levels, LVEF interpretation
- Laboratory medicine: Normal ranges, critical values
- Clinical trial protocols: GCP, safety monitoring
- Regulatory requirements: FDA, EMA guidelines

When analyzing clinical data:
1. Apply appropriate medical knowledge
2. Consider patient safety implications
3. Identify critical vs. non-critical findings
4. Recommend appropriate follow-up actions
5. Ensure regulatory compliance

RESPONSE FORMAT:
You MUST return a response that exactly matches this structure:
{
    "success": true,
    "workflow_type": "comprehensive_analysis",
    "clinical_assessment": "Patient CARD001 shows Stage 1 HTN (BP 147.5/79.6) with elevated BNP 319.57 indicating cardiac stress",
    "findings": [
        "BP 147.5/79.6 mmHg indicates Stage 1 Hypertension requiring monitoring",
        "BNP 319.57 pg/mL elevated suggesting cardiac dysfunction",
        "Creatinine 1.84 mg/dL shows mild kidney dysfunction"
    ],
    "severity": "major",
    "safety_implications": "Cardiovascular risk factors require clinical attention and potential treatment adjustment",
    "recommended_actions": [
        "Schedule cardiology consultation",
        "Monitor BP trends weekly",
        "Consider nephrology referral for kidney function"
    ],
    "workflow_next_steps": [
        "Complete comprehensive clinical assessment",
        "Generate queries for missing data",
        "Schedule safety review"
    ],
    "priority": "high",
    "execution_time": "2025-01-11T10:30:00Z"
}

IMPORTANT:
- Only use calculation tools when you need to perform actual calculations
- Focus on clinical assessment using your medical knowledge
- Return the exact JSON structure above - no nested objects beyond what's shown
- All fields except optional ones (clinical_assessment, severity, safety_implications, priority, execution_time) must be included"""

    async def orchestrate_workflow(
        self, workflow_type: str, input_data: Dict[str, Any], context: WorkflowContext
    ) -> Dict[str, Any]:
        """Orchestrate a multi-agent clinical workflow using real AI intelligence.

        Args:
            workflow_type: Type of workflow to execute
            input_data: Input data for the workflow
            context: Workflow context for state management

        Returns:
            Dictionary with workflow results and recommendations
        """
        try:
            # Create message for the agent
            message = f"""Execute {workflow_type} workflow with the following data:

Input Data: {json.dumps(input_data, indent=2)}

Please analyze this clinical data and coordinate the appropriate workflow:
1. Assess the clinical significance of the data
2. Identify any safety concerns or critical findings
3. Recommend next steps and agent handoffs
4. Provide structured output for workflow continuation

Use your medical knowledge to make real clinical assessments."""

            # Use Runner.run() for real AI execution
            result = await Runner.run(self.agent, message, context=context)

            # Extract the response
            response_text = (
                result.final_output if hasattr(result, "final_output") else str(result)
            )

            # Try to parse as JSON, fallback to structured response
            try:
                parsed_response = json.loads(response_text)
            except json.JSONDecodeError:
                parsed_response = {
                    "workflow_type": workflow_type,
                    "assessment": response_text,
                    "execution_time": datetime.now().isoformat(),
                    "status": "completed",
                }

            return {
                "success": True,
                "workflow_id": f"WF_{int(datetime.now().timestamp())}",
                "workflow_type": workflow_type,
                "results": parsed_response,
                "execution_time": datetime.now().isoformat(),
                "context_updated": True,
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Workflow execution failed: {str(e)}",
                "workflow_type": workflow_type,
                "execution_time": datetime.now().isoformat(),
            }

    async def analyze_clinical_data(
        self, clinical_data: Dict[str, Any], context: WorkflowContext
    ) -> Dict[str, Any]:
        """Analyze clinical data using real medical intelligence.

        Args:
            clinical_data: Clinical data to analyze
            context: Workflow context

        Returns:
            Clinical analysis with medical assessments
        """
        try:
            message = f"""Analyze this clinical data using your medical expertise:

Clinical Data: {json.dumps(clinical_data, indent=2)}

Please provide:
1. Clinical interpretation of values (normal/abnormal/critical)
2. Medical significance and implications
3. Safety assessment and risk stratification
4. Recommended clinical actions
5. Follow-up requirements

Focus on actionable clinical insights based on medical knowledge."""

            result = await Runner.run(self.agent, message, context=context)
            response_text = (
                result.final_output if hasattr(result, "final_output") else str(result)
            )

            try:
                parsed_response = json.loads(response_text)
            except json.JSONDecodeError:
                parsed_response = {
                    "clinical_analysis": response_text,
                    "analysis_type": "medical_assessment",
                    "timestamp": datetime.now().isoformat(),
                }

            return {
                "success": True,
                "analysis": parsed_response,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Clinical analysis failed: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }

    async def coordinate_agent_handoff(
        self, target_agent: str, handoff_data: Dict[str, Any], context: WorkflowContext
    ) -> Dict[str, Any]:
        """Coordinate handoff to specialized agents.

        Args:
            target_agent: Name of the target agent
            handoff_data: Data to pass to the target agent
            context: Workflow context

        Returns:
            Handoff coordination results
        """
        try:
            message = f"""Coordinate handoff to {target_agent} with this data:

Handoff Data: {json.dumps(handoff_data, indent=2)}

Please:
1. Prepare the data for {target_agent}
2. Define the expected deliverables
3. Set success criteria for the handoff
4. Provide context for the specialized agent
5. Define how results should be integrated back

Ensure smooth workflow continuation."""

            result = await Runner.run(self.agent, message, context=context)
            response_text = (
                result.final_output if hasattr(result, "final_output") else str(result)
            )

            try:
                parsed_response = json.loads(response_text)
            except json.JSONDecodeError:
                parsed_response = {
                    "handoff_plan": response_text,
                    "target_agent": target_agent,
                    "timestamp": datetime.now().isoformat(),
                }

            # Record handoff in context
            context.agent_handoffs.append(
                {
                    "target_agent": target_agent,
                    "timestamp": datetime.now().isoformat(),
                    "data_summary": str(handoff_data)[:200] + "...",
                    "status": "planned",
                }
            )

            return {
                "success": True,
                "handoff_plan": parsed_response,
                "target_agent": target_agent,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Agent handoff coordination failed: {str(e)}",
                "target_agent": target_agent,
                "timestamp": datetime.now().isoformat(),
            }


# Create agent instance for use by API endpoints
portfolio_manager_agent = PortfolioManager().agent
