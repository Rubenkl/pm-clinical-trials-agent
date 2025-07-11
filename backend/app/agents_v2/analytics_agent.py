"""Analytics Agent - Clean Implementation using OpenAI Agents SDK.

This agent provides analytics and performance metrics for clinical trial operations
using real intelligence instead of static reporting.
"""

import json
from datetime import datetime
from typing import Any, Dict, List

from agents import Agent, Runner
from pydantic import BaseModel, Field

from .calculation_tools import calculate_date_difference


class AnalyticsContext(BaseModel):
    """Context for Analytics Agent operations."""

    analytics_history: List[Dict[str, Any]] = Field(default_factory=list)
    metrics_cache: Dict[str, Any] = Field(default_factory=dict)
    trend_data: List[Dict[str, Any]] = Field(default_factory=list)


class AnalyticsAgentOutput(BaseModel):
    """Structured JSON output for Analytics Agent responses."""

    model_config = {"strict": True}

    success: bool
    analysis_type: str
    key_insights: List[str]
    performance_trends: List[str]
    risk_indicators: List[str]
    recommendations: List[str]
    metrics_summary: str
    predictive_insights: str


class AnalyticsAgent:
    """Analytics Agent for clinical trial performance analytics and insights.

    This agent provides comprehensive analytics, trend analysis, and performance
    insights for clinical trial operations using intelligent assessment instead
    of static reporting rules.

    Key Capabilities:
    - Performance trend analysis
    - Operational metrics calculation
    - Predictive insights
    - Risk assessment analytics
    - Study performance benchmarking
    """

    def __init__(self) -> None:
        """Initialize Analytics Agent with minimal calculation tools."""
        # Only include date calculation tools for timeline analysis
        tools = [calculate_date_difference]

        self.agent = Agent(
            name="AnalyticsAgent",
            instructions=self._get_instructions(),
            tools=tools,
            model="gpt-4o-mini",
            output_type=AnalyticsAgentOutput,
        )

    def _get_instructions(self) -> str:
        """Get comprehensive instructions for the Analytics Agent."""
        return """You are an Analytics Agent specialized in clinical trial performance analysis.

CORE RESPONSIBILITIES:
1. Analyze operational performance trends and patterns
2. Generate actionable insights for study improvement
3. Assess risk factors and mitigation strategies
4. Benchmark performance against industry standards
5. Provide predictive analytics for study outcomes

ANALYTICS EXPERTISE:
- Clinical trial operational metrics
- Site performance benchmarking
- Data quality trend analysis
- Query resolution efficiency
- Protocol compliance patterns
- Safety signal detection
- Enrollment and retention analytics

CALCULATION TOOLS (use only when needed for specific calculations):
- Date difference calculations for timeline analysis

ANALYTICS DOMAINS:
1. **Site Performance**
   - Enrollment rates and timelines
   - Data quality scores
   - Protocol compliance rates
   - Query resolution times

2. **Study Operations**
   - Overall study progress
   - Resource utilization
   - Milestone achievement
   - Risk factor identification

3. **Data Quality**
   - Data completeness trends
   - Error rate patterns
   - Source data verification efficiency
   - Critical finding frequency

4. **Predictive Insights**
   - Enrollment projections
   - Timeline risk assessment
   - Resource requirement forecasting
   - Quality trend predictions

RESPONSE FORMAT:
You MUST return a response that exactly matches this structure:
{
    "success": true,
    "analysis_type": "site_performance_analysis",
    "key_insights": [
        "Site 001 showing 15% higher enrollment rate than average",
        "Data quality scores improved 8% over last quarter",
        "Protocol compliance trending upward across all sites"
    ],
    "performance_trends": [
        "Enrollment rate increasing 12% month-over-month",
        "Query resolution time decreased to 4.2 days average",
        "Site 003 showing improvement after additional CRA support"
    ],
    "risk_indicators": [
        "Site 005 enrollment below target by 30%",
        "Data entry delays increasing at Site 002",
        "Protocol deviation rate elevated at Site 007"
    ],
    "recommendations": [
        "Share Site 001 best practices with underperforming sites",
        "Implement additional training at Site 007",
        "Consider additional resources for Site 005"
    ],
    "metrics_summary": "Overall study performance: 85.3% enrollment rate, 94.2% data quality score, 88.7% protocol compliance",
    "predictive_insights": "Study completion projected for 2024-12-15 with 95% confidence, low risk level overall"
}

IMPORTANT:
- Only use calculation tools when you need to perform actual calculations
- Focus on analytical assessment using clinical trial operations knowledge
- Return the exact JSON structure above - no nested objects

Remember: Provide intelligent analytics insights, not static report generation."""

    async def analyze_performance_trends(
        self,
        performance_data: Dict[str, Any],
        analysis_context: Dict[str, Any],
        context: AnalyticsContext,
    ) -> Dict[str, Any]:
        """Analyze performance trends using intelligent assessment.

        Args:
            performance_data: Historical performance data
            analysis_context: Analysis context and parameters
            context: Analytics context

        Returns:
            Comprehensive performance trend analysis
        """
        try:
            message = f"""Analyze performance trends in this clinical trial data:

Performance Data: {json.dumps(performance_data, indent=2)}
Analysis Context: {json.dumps(analysis_context, indent=2)}

Please provide comprehensive trend analysis including:
1. Performance metric trends over time
2. Site-specific performance patterns
3. Data quality trend analysis
4. Operational efficiency insights
5. Risk factor identification
6. Improvement opportunities
7. Predictive assessments for future performance

Focus on actionable insights that can improve study operations."""

            result = await Runner.run(self.agent, message, context=context)
            response_text = (
                result.final_output if hasattr(result, "final_output") else str(result)
            )

            try:
                parsed_response = json.loads(response_text)
            except json.JSONDecodeError:
                parsed_response = {
                    "analytics_results": response_text,
                    "analysis_type": "performance_trend_analysis",
                    "timestamp": datetime.now().isoformat(),
                }

            # Store in analytics history
            context.analytics_history.append(
                {
                    "analysis_type": "performance_trends",
                    "timestamp": datetime.now().isoformat(),
                    "data_points": len(performance_data.get("data_points", [])),
                }
            )

            return {
                "success": True,
                "analytics": parsed_response,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Performance trend analysis failed: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }

    async def generate_dashboard_metrics(
        self,
        study_data: Dict[str, Any],
        context: AnalyticsContext,
    ) -> Dict[str, Any]:
        """Generate dashboard metrics for study overview.

        Args:
            study_data: Current study data
            context: Analytics context

        Returns:
            Dashboard metrics and KPIs
        """
        try:
            message = f"""Generate dashboard metrics for this clinical trial:

Study Data: {json.dumps(study_data, indent=2)}

Please provide dashboard-ready metrics including:
1. Key performance indicators (KPIs)
2. Study progress overview
3. Site performance summary
4. Data quality metrics
5. Recent activities and alerts
6. Trend indicators and status

Format for dashboard display with clear, actionable information."""

            result = await Runner.run(self.agent, message, context=context)
            response_text = (
                result.final_output if hasattr(result, "final_output") else str(result)
            )

            try:
                parsed_response = json.loads(response_text)
            except json.JSONDecodeError:
                parsed_response = {
                    "dashboard_metrics": response_text,
                    "metrics_type": "dashboard_overview",
                    "timestamp": datetime.now().isoformat(),
                }

            return {
                "success": True,
                "dashboard": parsed_response,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Dashboard metrics generation failed: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }


# Create agent instance for use by API endpoints
analytics_agent = AnalyticsAgent().agent
