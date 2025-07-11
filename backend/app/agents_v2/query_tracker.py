"""Query Tracker Agent - Clean Implementation using OpenAI Agents SDK.

This agent tracks query lifecycle, monitors response times, and manages
escalation processes using real intelligence instead of static tracking rules.
"""

import json
from datetime import datetime
from typing import Any, Dict, List

from agents import Agent, Runner
from pydantic import BaseModel, Field

from .calculation_tools import calculate_date_difference


class QueryTrackingContext(BaseModel):
    """Context for Query Tracker operations."""

    tracking_history: List[Dict[str, Any]] = Field(default_factory=list)
    escalation_patterns: Dict[str, Any] = Field(default_factory=dict)
    performance_metrics: Dict[str, Any] = Field(default_factory=dict)


class QueryTracker:
    """Query Tracker agent for query lifecycle management and performance monitoring.

    This agent tracks queries through their complete lifecycle, monitors response
    times, manages escalations, and provides performance analytics using
    intelligent assessment instead of rigid rule-based tracking.

    Key Capabilities:
    - Query lifecycle tracking and status management
    - Response time monitoring and SLA tracking
    - Intelligent escalation management
    - Performance analytics and trend analysis
    - Site communication coordination
    """

    def __init__(self) -> None:
        """Initialize Query Tracker with minimal calculation tools."""
        # Only include date calculation tools for timeline tracking
        tools = [calculate_date_difference]

        self.agent = Agent(
            name="QueryTracker",
            instructions=self._get_instructions(),
            tools=tools,
            model="gpt-4",
        )

    def _get_instructions(self) -> str:
        """Get comprehensive instructions for the Query Tracker agent."""
        return """You are a Query Tracker specialized in clinical trial query lifecycle management.

CORE RESPONSIBILITIES:
1. Track queries through complete lifecycle (sent → responded → resolved)
2. Monitor response times and SLA compliance
3. Manage escalation processes with appropriate timing
4. Analyze performance trends and patterns
5. Coordinate follow-up communications and actions

QUERY LIFECYCLE MANAGEMENT:
- **Sent**: Query delivered to site, tracking initiated
- **Acknowledged**: Site confirms receipt (optional)
- **Responded**: Site provides initial response
- **Under Review**: Response being evaluated for completeness
- **Resolved**: Query closed with satisfactory resolution
- **Escalated**: Moved to higher-level attention

AVAILABLE CALCULATION TOOLS:
- Date difference calculations for timeline tracking

SLA AND TIMING STANDARDS:
- **Immediate Queries**: 24-hour response requirement
- **Urgent Queries**: 72-hour response requirement
- **Routine Queries**: 5-7 business day standard
- **Escalation Triggers**: Based on query urgency and response delay

ESCALATION INTELLIGENCE:
Consider these factors for escalation decisions:
- Clinical significance of the query
- Patient safety implications
- Study timeline impact
- Site historical performance
- Query complexity and required effort
- Regulatory compliance requirements

PERFORMANCE ANALYTICS:
Track and analyze:
- Response time trends by site and query type
- Resolution quality and completeness
- Escalation frequency and effectiveness
- Site communication patterns
- Study-wide query burden and trends

ESCALATION LEVELS:
1. **First Reminder**: Automated follow-up after standard timeline
2. **CRA Follow-up**: Personal contact from Clinical Research Associate
3. **Site Management**: Contact site management/PI
4. **Sponsor Escalation**: Escalate to sponsor management
5. **Regulatory Consideration**: Consider regulatory implications

RESPONSE FORMAT:
Always return structured JSON with tracking analysis:
{
    "tracking_analysis": {
        "query_status": "overdue",
        "days_since_sent": 8,
        "sla_compliance": "non_compliant",
        "escalation_recommendation": {
            "level": "cra_follow_up",
            "rationale": "Routine query now 3 days overdue, site typically responsive",
            "recommended_action": "Personal CRA contact to check for issues",
            "timeline": "within 24 hours"
        },
        "performance_context": {
            "site_avg_response_time": 4.2,
            "query_type_complexity": "moderate",
            "site_current_query_load": 12
        },
        "next_steps": ["CRA to contact site", "Schedule follow-up in 48 hours"]
    }
}

Remember: Use intelligent assessment considering clinical context, not rigid rules."""

    async def track_query_lifecycle(
        self,
        query_details: Dict[str, Any],
        tracking_data: Dict[str, Any],
        context: QueryTrackingContext,
    ) -> Dict[str, Any]:
        """Track query through its lifecycle using intelligent monitoring.

        Args:
            query_details: Query information and content
            tracking_data: Current tracking status and timeline
            context: Tracking context

        Returns:
            Comprehensive tracking analysis and recommendations
        """
        try:
            message = f"""Analyze this query's lifecycle status and provide tracking recommendations:

Query Details: {json.dumps(query_details, indent=2)}
Tracking Data: {json.dumps(tracking_data, indent=2)}

Please provide comprehensive tracking analysis including:
1. Current lifecycle status assessment
2. SLA compliance evaluation
3. Response time analysis and trends
4. Escalation recommendation with rationale
5. Performance context and site patterns
6. Next steps and timeline recommendations
7. Risk assessment for study impact

Consider:
- Clinical urgency and patient safety implications
- Site historical performance and current workload
- Query complexity and required effort
- Study timeline and milestone impacts
- Communication effectiveness and patterns

Focus on intelligent assessment rather than rigid rule application."""

            result = await Runner.run(self.agent, message)
            response_text = (
                result.final_output if hasattr(result, "final_output") else str(result)
            )

            try:
                parsed_response = json.loads(response_text)
            except json.JSONDecodeError:
                parsed_response = {
                    "tracking_analysis": response_text,
                    "analysis_type": "query_lifecycle_tracking",
                    "timestamp": datetime.now().isoformat(),
                }

            # Update tracking history
            context.tracking_history.append(
                {
                    "query_id": query_details.get("query_id", "unknown"),
                    "status": parsed_response.get("tracking_analysis", {}).get(
                        "query_status", "unknown"
                    ),
                    "timestamp": datetime.now().isoformat(),
                }
            )

            return {
                "success": True,
                "tracking": parsed_response,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Query lifecycle tracking failed: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }

    async def analyze_performance_trends(
        self,
        performance_data: Dict[str, Any],
        study_context: Dict[str, Any],
        context: QueryTrackingContext,
    ) -> Dict[str, Any]:
        """Analyze query performance trends and patterns.

        Args:
            performance_data: Historical performance data
            study_context: Study context and requirements
            context: Tracking context

        Returns:
            Performance analysis and improvement recommendations
        """
        try:
            message = f"""Analyze query performance trends and provide insights:

Performance Data: {json.dumps(performance_data, indent=2)}
Study Context: {json.dumps(study_context, indent=2)}

Please provide comprehensive performance analysis including:
1. Response time trends by site and query type
2. Escalation patterns and effectiveness
3. Resolution quality assessment
4. Site performance comparisons
5. Query burden analysis and impact
6. Improvement opportunities and recommendations
7. Risk assessment for study quality

Identify:
- Best performing sites and practices
- Sites needing additional support
- Query types causing delays
- Communication effectiveness patterns
- Systemic issues requiring attention

Focus on actionable insights for study improvement."""

            result = await Runner.run(self.agent, message)
            response_text = (
                result.final_output if hasattr(result, "final_output") else str(result)
            )

            try:
                parsed_response = json.loads(response_text)
            except json.JSONDecodeError:
                parsed_response = {
                    "performance_analysis": response_text,
                    "analysis_type": "performance_trend_analysis",
                    "timestamp": datetime.now().isoformat(),
                }

            # Update performance metrics
            if "performance_analysis" in parsed_response:
                context.performance_metrics.update(
                    {
                        "last_analysis": datetime.now().isoformat(),
                        "trends_identified": True,
                    }
                )

            return {
                "success": True,
                "performance": parsed_response,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Performance trend analysis failed: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }

    async def recommend_escalation_strategy(
        self,
        escalation_request: Dict[str, Any],
        site_context: Dict[str, Any],
        context: QueryTrackingContext,
    ) -> Dict[str, Any]:
        """Recommend intelligent escalation strategy for overdue queries.

        Args:
            escalation_request: Escalation request details
            site_context: Site context and history
            context: Tracking context

        Returns:
            Escalation strategy recommendations
        """
        try:
            message = f"""Recommend escalation strategy for this overdue query situation:

Escalation Request: {json.dumps(escalation_request, indent=2)}
Site Context: {json.dumps(site_context, indent=2)}

Please recommend appropriate escalation strategy including:
1. Escalation level recommendation with rationale
2. Communication approach and messaging
3. Timeline and follow-up schedule
4. Stakeholder involvement recommendations
5. Risk mitigation strategies
6. Success criteria for escalation
7. Alternative approaches if standard escalation fails

Consider:
- Query clinical significance and urgency
- Site relationship and communication history
- Current site workload and challenges
- Study timeline and critical path impact
- Cultural and regional communication preferences

Provide practical, relationship-preserving escalation approach."""

            result = await Runner.run(self.agent, message)
            response_text = (
                result.final_output if hasattr(result, "final_output") else str(result)
            )

            try:
                parsed_response = json.loads(response_text)
            except json.JSONDecodeError:
                parsed_response = {
                    "escalation_strategy": response_text,
                    "strategy_type": "escalation_recommendation",
                    "timestamp": datetime.now().isoformat(),
                }

            return {
                "success": True,
                "escalation": parsed_response,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Escalation strategy recommendation failed: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }


# Create agent instance for use by API endpoints
query_tracker_agent = QueryTracker().agent
