"""Portfolio Manager Agent - Clean Implementation using OpenAI Agents SDK.

This agent orchestrates clinical trial workflows without mock medical judgments.
It uses real AI intelligence via Runner.run() for clinical reasoning and coordinates
with specialized agents through handoffs.
"""

import json
from datetime import datetime
from typing import Any, Dict, List

from agents import Agent, Runner
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


class WorkflowContext(BaseModel):
    """Context for Portfolio Manager workflow orchestration."""

    active_workflows: Dict[str, Any] = Field(default_factory=dict)
    completed_workflows: List[Dict[str, Any]] = Field(default_factory=list)
    performance_metrics: Dict[str, Any] = Field(default_factory=dict)
    agent_handoffs: List[Dict[str, Any]] = Field(default_factory=list)


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
            model="gpt-4",
        )

    def _get_instructions(self) -> str:
        """Get comprehensive instructions for the Portfolio Manager agent."""
        return """You are the Portfolio Manager for a clinical trials automation platform.

CORE RESPONSIBILITIES:
1. Orchestrate multi-agent workflows for clinical operations
2. Coordinate with specialized agents (Query Analyzer, Data Verifier, etc.)
3. Manage workflow context and state across complex operations
4. Make clinical assessments using your medical knowledge
5. Delegate specific tasks to appropriate specialized agents

AVAILABLE FUNCTION TOOLS:
- Medical unit conversion tools (mg/dL to mmol/L, etc.)
- Age and date calculation tools
- Visit window compliance checking
- Change from baseline calculations
- Body surface area calculations
- Creatinine clearance calculations
- Test data retrieval (for development scenarios)

CRITICAL: You do NOT have mock medical judgment tools. Instead:
- Use your medical knowledge directly for clinical assessments
- Leverage calculation tools for mathematical operations
- Coordinate with specialized agents for complex analyses
- Make real medical reasoning based on clinical data

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
Always return structured JSON responses with:
- Clinical findings and assessments
- Recommended actions
- Priority levels (critical/major/minor)
- Next steps in workflow
- Agent handoff recommendations if needed

Example Clinical Assessment:
{
    "clinical_assessment": {
        "findings": ["BP 180/95 = Stage 2 Hypertension", "BNP 850 = Heart Failure"],
        "severity": "critical",
        "safety_implications": "Requires immediate medical evaluation",
        "recommended_actions": ["Contact investigator", "Safety assessment", "Consider dose modification"]
    },
    "workflow_next_steps": ["hand_off_to_query_generator", "schedule_safety_review"],
    "priority": "urgent"
}

Remember: You are providing real clinical intelligence, not mock responses."""

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
