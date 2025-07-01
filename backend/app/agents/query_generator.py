"""Query Generator Agent using OpenAI Agents SDK."""

import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from agents import Agent, function_tool
from pydantic import BaseModel


@dataclass
class QueryTemplate:
    """Template for generating clinical trial queries."""
    
    category: str
    severity: str
    template: str
    required_fields: List[str]
    regulatory_requirements: List[str]
    
    def format(self, **kwargs) -> str:
        """Format template with provided data."""
        return self.template.format(**kwargs)


class QueryGeneratorContext(BaseModel):
    """Context for Query Generator agent using Pydantic."""
    
    analysis: Dict[str, Any] = {}
    site_preferences: Dict[str, Any] = {}
    language: str = "en"
    generated_queries: List[Dict[str, Any]] = []


# Initialize query templates
QUERY_TEMPLATES = {
    "missing_data": QueryTemplate(
        category="missing_data",
        severity="major",
        template=(
            "Dear Site {site_name},\n\n"
            "During routine data review, we identified missing {field_name} "
            "for Subject {subject_id} at {visit} visit on {visit_date}.\n\n"
            "According to the protocol, this data is required for {reason}.\n\n"
            "Please provide the missing {field_name} or explain why it is not available.\n\n"
            "Thank you for your prompt attention to this matter."
        ),
        required_fields=["site_name", "field_name", "subject_id", "visit", "visit_date", "reason"],
        regulatory_requirements=["ICH-GCP 4.9", "FDA 21 CFR 312.62"]
    ),
    "data_discrepancy": QueryTemplate(
        category="data_discrepancy",
        severity="major", 
        template=(
            "Dear Site {site_name},\n\n"
            "We have identified a discrepancy in the {field_name} value "
            "for Subject {subject_id} at {visit} visit:\n\n"
            "- EDC Value: {edc_value}\n"
            "- Source Document Value: {source_value}\n\n"
            "Please verify the correct value and update the EDC accordingly, "
            "or provide clarification for the discrepancy.\n\n"
            "Thank you for your cooperation."
        ),
        required_fields=["site_name", "field_name", "subject_id", "visit", "edc_value", "source_value"],
        regulatory_requirements=["ICH-GCP 4.9", "FDA 21 CFR 312.62"]
    ),
    "adverse_event": QueryTemplate(
        category="adverse_event",
        severity="critical",
        template=(
            "Dear Site {site_name},\n\n"
            "URGENT: Regarding the {event_type} reported for Subject {subject_id} on {event_date}:\n\n"
            "{specific_question}\n\n"
            "Due to the critical nature of this event, please respond within 24 hours.\n\n"
            "If you need assistance, please contact the medical monitor immediately."
        ),
        required_fields=["site_name", "event_type", "subject_id", "event_date", "specific_question"],
        regulatory_requirements=["ICH-GCP 4.11", "FDA 21 CFR 312.32", "EMA CT-3"]
    )
}


@function_tool
def generate_clinical_query(query_request: str) -> str:
    """Generate a clinical query based on analysis results.
    
    Args:
        query_request: JSON string containing analysis, site_preferences, language
        
    Returns:
        JSON string with generated query details
    """
    try:
        request_data = json.loads(query_request)
        analysis = request_data.get("analysis", {})
        site_preferences = request_data.get("site_preferences", {})
        language = request_data.get("language", "en")
    except json.JSONDecodeError:
        return json.dumps({"error": "Invalid JSON in query_request"})
    
    # Get appropriate template
    category = analysis.get("category", "data_discrepancy")
    template = QUERY_TEMPLATES.get(category)
    
    # Generate query text
    if template and all(field in analysis for field in template.required_fields):
        query_text = template.format(**analysis)
    else:
        # Generate using fallback format
        query_text = f"""Dear Site,

We have identified an issue that requires your attention:

Subject: {analysis.get('subject_id', 'Unknown')}
Visit: {analysis.get('visit', 'Unknown')}
Issue: {analysis.get('description', 'No description provided')}

{analysis.get('suggested_actions', ['Please review and provide clarification.'])[0]}

Thank you for your cooperation."""
    
    # Build response
    response = {
        "query_id": f"QRY_{analysis.get('subject_id', 'UNK')}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "query_text": query_text,
        "category": category,
        "priority": analysis.get("severity", "medium"),
        "supporting_docs": ["Source documents", "Protocol"],
        "regulatory_refs": template.regulatory_requirements if template else ["ICH-GCP 4.9"],
        "suggested_response_time": "24 hours" if analysis.get("severity") == "critical" else "5 business days",
        "generated_at": datetime.now().isoformat(),
        "language": language,
        "thread_id": "thread_" + datetime.now().strftime('%Y%m%d%H%M%S')
    }
    
    return json.dumps(response)


@function_tool
def validate_clinical_query(query_text: str) -> str:
    """Validate a query for compliance and quality.
    
    Returns:
        JSON string with validation results
    """
    issues = []
    
    # Check length
    if len(query_text) < 50:
        issues.append("Query too short - may lack necessary detail")
    if len(query_text) > 2000:
        issues.append("Query too long - consider breaking into multiple queries")
    
    # Check for required elements
    required_phrases = ["Dear Site", "Subject", "Please"]
    missing_phrases = [phrase for phrase in required_phrases if phrase not in query_text]
    if missing_phrases:
        issues.append(f"Missing standard phrases: {', '.join(missing_phrases)}")
    
    # Check for regulatory references
    reg_keywords = ["protocol", "ICH-GCP", "FDA", "regulation"]
    if not any(keyword.lower() in query_text.lower() for keyword in reg_keywords):
        issues.append("No regulatory or protocol reference found")
    
    result = {
        "valid": len(issues) == 0,
        "issues": issues,
        "word_count": len(query_text.split()),
        "character_count": len(query_text)
    }
    
    return json.dumps(result)


@function_tool
def preview_query_from_template(preview_request: str) -> str:
    """Preview a query using templates.
    
    Args:
        preview_request: JSON string containing analysis and optional template_category
        
    Returns:
        Query preview text
    """
    try:
        request_data = json.loads(preview_request)
        analysis = request_data.get("analysis", {})
        template_category = request_data.get("template_category")
    except json.JSONDecodeError:
        return "Error: Invalid JSON in preview_request"
    
    category = template_category or analysis.get("category", "general")
    template = QUERY_TEMPLATES.get(category)
    
    if template:
        # Check if all required fields are present
        missing_fields = [f for f in template.required_fields if f not in analysis]
        if missing_fields:
            return f"Template requires fields: {template.required_fields}"
        
        try:
            return template.format(**analysis)
        except KeyError as e:
            return f"Template error: missing field {e}"
    else:
        # Return a basic preview
        return (
            f"Query Preview:\n"
            f"Subject: {analysis.get('subject_id', 'Unknown')}\n"
            f"Issue: {analysis.get('description', 'No description')}\n"
            f"Severity: {analysis.get('severity', 'Unknown')}\n"
            f"Category: {category}"
        )


# Create the Query Generator Agent
query_generator_agent = Agent(
    name="Clinical Query Generator",
    instructions="""You are a Clinical Query Generator specialized in creating regulatory-compliant queries for clinical trials.

Your responsibilities:
1. Generate clear, professional queries based on data discrepancies
2. Follow medical writing standards and site-specific preferences
3. Ensure regulatory compliance (ICH-GCP, FDA, EMA)
4. Provide supporting documentation references
5. Support multiple languages when requested

Query Format Guidelines:
- Use professional medical terminology
- Be specific about the discrepancy or issue
- Include relevant context (visit, date, field)
- Request specific action from the site
- Maintain respectful, collaborative tone

Use the available tools to:
- generate_clinical_query: Create queries from analysis results
- validate_clinical_query: Check queries for compliance
- preview_query_from_template: Preview queries before generation""",
    tools=[generate_clinical_query, validate_clinical_query, preview_query_from_template],
    model="gpt-4-turbo-preview"
)


class QueryGenerator:
    """Wrapper class for Query Generator agent to maintain compatibility."""
    
    def __init__(self):
        """Initialize the Query Generator."""
        self.agent = query_generator_agent
        self.templates = QUERY_TEMPLATES
        self.context = QueryGeneratorContext()
        
        # Mock assistant for test compatibility
        self.assistant = type('obj', (object,), {
            'id': 'asst_query_generator',
            'name': 'Clinical Query Generator'
        })
        
        self.instructions = self.agent.instructions
    
    async def generate_query(
        self,
        analysis: Dict[str, Any],
        site_preferences: Optional[Dict[str, Any]] = None,
        language: str = "en"
    ) -> Dict[str, Any]:
        """Generate a clinical query based on analysis results."""
        request_data = {
            "analysis": analysis,
            "site_preferences": site_preferences or {},
            "language": language
        }
        result_str = generate_clinical_query(json.dumps(request_data))
        return json.loads(result_str)
    
    async def generate_batch_queries(
        self,
        analyses: List[Dict[str, Any]],
        site_preferences: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Generate multiple queries in batch."""
        queries = []
        for analysis in analyses:
            query = await self.generate_query(analysis, site_preferences)
            queries.append(query)
        return queries
    
    def get_template(self, category: str) -> Optional[QueryTemplate]:
        """Get a query template by category."""
        return self.templates.get(category)
    
    def preview_query(
        self,
        analysis: Dict[str, Any],
        template_override: Optional[str] = None
    ) -> str:
        """Preview a query before generation."""
        request_data = {
            "analysis": analysis,
            "template_category": template_override
        }
        return preview_query_from_template(json.dumps(request_data))
    
    def validate_query(self, query_text: str) -> Dict[str, Any]:
        """Validate a query for compliance and quality."""
        result_str = validate_clinical_query(query_text)
        return json.loads(result_str)


__all__ = [
    "QueryGenerator",
    "QueryTemplate", 
    "query_generator_agent",
    "generate_clinical_query",
    "validate_clinical_query",
    "preview_query_from_template",
    "QueryGeneratorContext"
]