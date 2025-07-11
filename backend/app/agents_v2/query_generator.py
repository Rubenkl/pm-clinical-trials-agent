"""Query Generator Agent - Clean Implementation using OpenAI Agents SDK.

This agent generates professional clinical trial queries using real medical
and regulatory knowledge instead of template-based generation.
"""

import json
from datetime import datetime
from typing import Any, Dict, List

from agents import Agent, Runner
from pydantic import BaseModel, Field


class QueryGenerationContext(BaseModel):
    """Context for Query Generator operations."""

    generation_history: List[Dict[str, Any]] = Field(default_factory=list)
    query_templates: Dict[str, str] = Field(default_factory=dict)
    response_patterns: List[Dict[str, Any]] = Field(default_factory=list)


class QueryGeneratorOutput(BaseModel):
    """Structured JSON output for Query Generator responses."""
    
    model_config = {"strict": True}
    
    success: bool
    query_type: str
    generated_query: str
    query_priority: str
    regulatory_compliance: str
    recommended_timeline: str
    follow_up_actions: List[str]


class QueryGenerator:
    """Query Generator agent for professional clinical trial query creation.

    This agent generates contextually appropriate, professionally written queries
    for clinical trial data clarification using real medical knowledge and
    regulatory requirements instead of static templates.

    Key Capabilities:
    - Professional medical query writing
    - Context-appropriate language and tone
    - Regulatory compliance in query content
    - Multi-language support capabilities
    - Query prioritization and urgency assessment
    """

    def __init__(self) -> None:
        """Initialize Query Generator with no function tools.

        This agent relies on language generation capabilities and doesn't need
        calculation tools for query creation.
        """
        self.agent = Agent(
            name="QueryGenerator",
            instructions=self._get_instructions(),
            tools=[],  # No tools needed for text generation
            model="gpt-4o-mini",
            output_type=QueryGeneratorOutput,
        )

    def _get_instructions(self) -> str:
        """Get comprehensive instructions for the Query Generator agent."""
        return """You are a Query Generator specialized in creating professional clinical trial queries.

CORE RESPONSIBILITIES:
1. Generate clear, professional queries for data clarification
2. Ensure queries are medically appropriate and regulatory compliant
3. Adapt language and tone for different audiences (sites, investigators, CRAs)
4. Prioritize queries based on clinical significance and urgency
5. Provide specific, actionable query text

QUERY WRITING EXPERTISE:
- Medical terminology and professional clinical language
- ICH-GCP compliance in query content
- Site communication best practices
- Investigator and CRA interaction protocols
- Multi-cultural communication considerations
- Regulatory audit requirements

QUERY TYPES AND PURPOSES:
1. **Data Clarification Queries**
   - Missing or incomplete data
   - Inconsistent values across forms
   - Values outside expected ranges

2. **Medical Review Queries**
   - Clinical significance clarification
   - AE causality assessment
   - Concomitant medication justification

3. **Source Verification Queries**
   - EDC vs source document discrepancies
   - Source document availability
   - Data transcription accuracy

4. **Protocol Compliance Queries**
   - Protocol deviation clarification
   - Procedure timing questions
   - Eligibility criteria verification

5. **Safety Queries**
   - SAE details and follow-up
   - Safety parameter clarification
   - Urgent safety assessments

QUERY QUALITY STANDARDS:
- **Clear and Specific**: Exactly what information is needed
- **Medically Appropriate**: Uses correct medical terminology
- **Actionable**: Site knows exactly what to do
- **Professional**: Maintains appropriate tone and respect
- **Compliant**: Meets ICH-GCP and regulatory standards

QUERY STRUCTURE:
1. **Context**: Brief background of the issue
2. **Specific Question**: Exact information needed
3. **Rationale**: Why this information is important (when appropriate)
4. **Instructions**: How to provide the information
5. **Timeline**: When response is needed

URGENCY CLASSIFICATION:
- **Immediate**: Safety-related, requires response within 24 hours
- **Urgent**: Protocol compliance, requires response within 72 hours
- **Routine**: Administrative, standard response timeline

RESPONSE FORMAT:
Always return structured JSON with query content:
{
    "query_details": {
        "query_text": "Please clarify the systolic blood pressure reading of 180 mmHg recorded on Day 15. The source document shows 120 mmHg. Please verify which value is correct and provide the source document page reference.",
        "query_type": "source_verification",
        "urgency": "urgent",
        "medical_context": "Significant BP discrepancy may indicate safety concern",
        "response_timeline": "72 hours",
        "follow_up_required": true,
        "regulatory_implications": "Data integrity requirement for safety parameter",
        "suggested_response_format": "Verified value: [X] mmHg, Source document page: [X]"
    }
}

Remember: Generate professional, medically appropriate queries that facilitate clear communication."""

    async def generate_clinical_query(
        self,
        query_request: Dict[str, Any],
        clinical_context: Dict[str, Any],
        context: QueryGenerationContext,
    ) -> Dict[str, Any]:
        """Generate a professional clinical trial query.

        Args:
            query_request: Query request details and requirements
            clinical_context: Clinical context and patient information
            context: Generation context

        Returns:
            Professional query with context and instructions
        """
        try:
            message = f"""Generate a professional clinical trial query based on this request:

Query Request: {json.dumps(query_request, indent=2)}
Clinical Context: {json.dumps(clinical_context, indent=2)}

Please create a professional query that includes:
1. Clear, specific question about the data issue
2. Medical context and rationale when appropriate
3. Specific instructions for site response
4. Appropriate urgency and timeline
5. Professional tone suitable for investigator/site communication
6. Regulatory compliance considerations

Ensure the query is:
- Medically accurate and appropriate
- Clear and actionable for the site
- Professional and respectful in tone
- Specific about what information is needed
- Compliant with ICH-GCP standards

Consider the clinical significance and patient safety implications."""

            result = await Runner.run(self.agent, message, context=context)
            response_text = (
                result.final_output if hasattr(result, "final_output") else str(result)
            )

            try:
                parsed_response = json.loads(response_text)
            except json.JSONDecodeError:
                parsed_response = {
                    "query_details": {
                        "query_text": response_text,
                        "query_type": query_request.get("type", "data_clarification"),
                        "timestamp": datetime.now().isoformat(),
                    }
                }

            # Track generation history
            context.generation_history.append(
                {
                    "query_type": query_request.get("type", "unknown"),
                    "urgency": parsed_response.get("query_details", {}).get(
                        "urgency", "routine"
                    ),
                    "timestamp": datetime.now().isoformat(),
                }
            )

            return {
                "success": True,
                "query": parsed_response,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Query generation failed: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }

    async def generate_batch_queries(
        self,
        query_requests: List[Dict[str, Any]],
        study_context: Dict[str, Any],
        context: QueryGenerationContext,
    ) -> Dict[str, Any]:
        """Generate multiple queries efficiently with consistent context.

        Args:
            query_requests: List of query requests to process
            study_context: Overall study context
            context: Generation context

        Returns:
            Batch of generated queries with summary
        """
        try:
            message = f"""Generate multiple professional clinical trial queries:

Query Requests: {json.dumps(query_requests, indent=2)}
Study Context: {json.dumps(study_context, indent=2)}

Please generate queries for each request ensuring:
1. Consistent professional tone across all queries
2. Appropriate prioritization based on clinical significance
3. Efficient grouping of related queries when possible
4. Clear identification of urgent vs. routine queries
5. Appropriate medical context for each query type

Provide a summary of:
- Total queries generated
- Urgency breakdown (immediate/urgent/routine)
- Query type distribution
- Recommended sending schedule
- Overall communication strategy

Maintain quality and consistency across all queries."""

            result = await Runner.run(self.agent, message, context=context)
            response_text = (
                result.final_output if hasattr(result, "final_output") else str(result)
            )

            try:
                parsed_response = json.loads(response_text)
            except json.JSONDecodeError:
                parsed_response = {
                    "batch_queries": response_text,
                    "generation_type": "batch_query_generation",
                    "query_count": len(query_requests),
                    "timestamp": datetime.now().isoformat(),
                }

            return {
                "success": True,
                "batch_results": parsed_response,
                "query_count": len(query_requests),
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Batch query generation failed: {str(e)}",
                "query_count": len(query_requests),
                "timestamp": datetime.now().isoformat(),
            }


# Create agent instance for use by API endpoints
query_generator_agent = QueryGenerator().agent
