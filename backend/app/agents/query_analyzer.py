"""Query Analyzer using OpenAI Agents SDK."""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
import json
import uuid

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

try:
    from openai import OpenAI
    from app.core.config import get_settings
except ImportError:
    # Mock for testing
    OpenAI = None
    get_settings = lambda: None


class QueryCategory(Enum):
    """Categories of clinical trial queries."""
    
    DATA_DISCREPANCY = "data_discrepancy"
    MISSING_DATA = "missing_data"
    PROTOCOL_DEVIATION = "protocol_deviation"
    ADVERSE_EVENT = "adverse_event"
    ELIGIBILITY = "eligibility"
    CONCOMITANT_MEDICATION = "concomitant_medication"
    LABORATORY_VALUE = "laboratory_value"
    OTHER = "other"


class QuerySeverity(Enum):
    """Severity levels for clinical trial queries."""
    
    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"
    INFO = "info"
    
    def get_priority(self) -> int:
        """Get numeric priority for severity (higher = more critical)."""
        priority_map = {
            QuerySeverity.CRITICAL: 4,
            QuerySeverity.MAJOR: 3,
            QuerySeverity.MINOR: 2,
            QuerySeverity.INFO: 1
        }
        return priority_map[self]


class QueryAnalysisContext(Context):
    """Context for Query Analyzer operations."""
    
    analysis_history: List[Dict[str, Any]] = Field(default_factory=list)
    detected_patterns: Dict[str, Any] = Field(default_factory=dict)
    performance_metrics: Dict[str, Any] = Field(default_factory=dict)
    medical_context: Dict[str, Any] = Field(default_factory=dict)
    regulatory_guidelines: Dict[str, Any] = Field(default_factory=dict)


# Medical terminology and severity mappings
MEDICAL_TERM_MAPPING = {
    "MI": "Myocardial infarction",
    "HTN": "Hypertension", 
    "DM": "Diabetes mellitus",
    "COPD": "Chronic obstructive pulmonary disease",
    "CHF": "Congestive heart failure",
    "DVT": "Deep vein thrombosis",
    "PE": "Pulmonary embolism",
    "SAE": "Serious adverse event",
    "AE": "Adverse event",
    "BP": "Blood pressure",
    "HR": "Heart rate",
    "RR": "Respiratory rate",
    "ECG": "Electrocardiogram",
    "CBC": "Complete blood count",
    "LFT": "Liver function tests"
}

CRITICAL_MEDICAL_TERMS = {
    "death", "died", "fatal", "life-threatening", "life threatening",
    "myocardial infarction", "stroke", "cardiac arrest", "anaphylaxis",
    "respiratory failure", "sepsis", "seizure", "coma", "shock"
}

MAJOR_MEDICAL_TERMS = {
    "hospitalization", "hospitalized", "emergency", "significant disability",
    "permanent impairment", "surgery", "surgical intervention", "icu",
    "intensive care", "transfusion", "dialysis"
}


@function_tool
def analyze_data_point(
    context: QueryAnalysisContext,
    data_point: str
) -> str:
    """Analyze a single clinical data point for discrepancies and issues."""
    
    # Parse input data
    data_point_dict = json.loads(data_point)
    
    query_id = f"QA_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:6]}"
    
    # Extract key information
    subject_id = data_point_dict.get("subject_id", "")
    visit = data_point_dict.get("visit", "")
    field_name = data_point_dict.get("field_name", "")
    edc_value = data_point_dict.get("edc_value", "")
    source_value = data_point_dict.get("source_value", "")
    
    # Determine category based on data characteristics
    category = _determine_category(data_point_dict)
    
    # Assess severity
    severity = _assess_severity(data_point_dict, field_name, edc_value, source_value)
    
    # Calculate confidence based on data completeness and patterns
    confidence = _calculate_confidence(data_point_dict)
    
    # Generate description
    description = _generate_description(data_point_dict, category)
    
    # Suggest actions
    suggested_actions = _generate_suggested_actions(category, severity)
    
    # Determine medical context
    medical_context = _determine_medical_context(field_name, edc_value, source_value)
    
    # Assess regulatory impact
    regulatory_impact = _assess_regulatory_impact(category, severity, field_name)
    
    # Create analysis result
    analysis_result = {
        "query_id": query_id,
        "category": category.value,
        "severity": severity.value,
        "confidence": confidence,
        "subject_id": subject_id,
        "visit": visit,
        "field_name": field_name,
        "description": description,
        "suggested_actions": suggested_actions,
        "medical_context": medical_context,
        "regulatory_impact": regulatory_impact,
        "created_at": datetime.now().isoformat(),
        "metadata": {
            "edc_value": edc_value,
            "source_value": source_value,
            "analysis_version": "1.0"
        }
    }
    
    # Store in context
    context.analysis_history.append(analysis_result)
    
    return json.dumps(analysis_result)


@function_tool
def batch_analyze_data(
    context: QueryAnalysisContext,
    data_points: str
) -> str:
    """Analyze multiple data points in batch for efficiency."""
    
    # Parse input data
    data_points_list = json.loads(data_points)
    
    results = []
    
    for data_point in data_points_list:
        try:
            result_json = analyze_data_point(context, json.dumps(data_point))
            result = json.loads(result_json)
            results.append(result)
        except Exception as e:
            # Handle individual failures gracefully
            error_result = {
                "query_id": f"ERROR_{uuid.uuid4().hex[:8]}",
                "category": QueryCategory.OTHER.value,
                "severity": QuerySeverity.INFO.value,
                "confidence": 0.0,
                "subject_id": data_point.get("subject_id", ""),
                "visit": data_point.get("visit", ""),
                "field_name": data_point.get("field_name", ""),
                "description": f"Analysis failed: {str(e)}",
                "suggested_actions": ["Review data format", "Contact technical support"],
                "error": str(e),
                "created_at": datetime.now().isoformat()
            }
            results.append(error_result)
    
    # Update performance metrics
    context.performance_metrics["batch_analyses"] = context.performance_metrics.get("batch_analyses", 0) + 1
    context.performance_metrics["total_data_points"] = context.performance_metrics.get("total_data_points", 0) + len(data_points_list)
    
    return json.dumps(results)


@function_tool
def detect_patterns(
    context: QueryAnalysisContext,
    historical_data: str
) -> str:
    """Detect patterns across historical clinical data."""
    
    # Parse input data
    historical_data_list = json.loads(historical_data)
    
    site_patterns = {}
    field_patterns = {}
    temporal_patterns = {}
    
    # Analyze site-specific patterns
    for data in historical_data_list:
        site_name = data.get("site_name", "Unknown")
        if site_name not in site_patterns:
            site_patterns[site_name] = {"discrepancy_count": 0, "fields": {}}
        
        site_patterns[site_name]["discrepancy_count"] += data.get("discrepancy_count", 0)
        
        field_name = data.get("field_name", "")
        if field_name:
            if field_name not in site_patterns[site_name]["fields"]:
                site_patterns[site_name]["fields"][field_name] = 0
            site_patterns[site_name]["fields"][field_name] += data.get("discrepancy_count", 0)
    
    # Analyze field-specific patterns
    for data in historical_data_list:
        field_name = data.get("field_name", "")
        if field_name not in field_patterns:
            field_patterns[field_name] = {"total_discrepancies": 0, "sites": []}
        
        field_patterns[field_name]["total_discrepancies"] += data.get("discrepancy_count", 0)
        
        site_name = data.get("site_name", "")
        if site_name and site_name not in field_patterns[field_name]["sites"]:
            field_patterns[field_name]["sites"].append(site_name)
    
    # Generate recommendations
    recommendations = []
    
    # Identify high-risk sites
    high_risk_sites = [
        site for site, data in site_patterns.items() 
        if data["discrepancy_count"] > 5
    ]
    
    if high_risk_sites:
        recommendations.append(f"Focus additional monitoring on sites: {', '.join(high_risk_sites)}")
    
    # Identify problematic fields
    problematic_fields = [
        field for field, data in field_patterns.items()
        if data["total_discrepancies"] > 10
    ]
    
    if problematic_fields:
        recommendations.append(f"Review data collection procedures for fields: {', '.join(problematic_fields)}")
    
    pattern_result = {
        "site_patterns": site_patterns,
        "field_patterns": field_patterns,
        "temporal_patterns": temporal_patterns,
        "recommendations": recommendations,
        "analysis_date": datetime.now().isoformat(),
        "data_points_analyzed": len(historical_data_list)
    }
    
    # Store patterns in context
    context.detected_patterns.update(pattern_result)
    
    return json.dumps(pattern_result)


@function_tool
def cross_system_match(
    context: QueryAnalysisContext,
    edc_data: str,
    source_data: str
) -> str:
    """Perform cross-system data matching and verification."""
    
    # Parse input data
    edc_data_dict = json.loads(edc_data)
    source_data_dict = json.loads(source_data)
    
    matching_fields = []
    discrepancies = []
    total_fields = 0
    
    # Compare common fields
    for field, edc_value in edc_data_dict.items():
        if field in source_data_dict:
            total_fields += 1
            source_value = source_data_dict[field]
            
            if str(edc_value).strip().lower() == str(source_value).strip().lower():
                matching_fields.append(field)
            else:
                discrepancies.append({
                    "field": field,
                    "edc_value": edc_value,
                    "source_value": source_value,
                    "severity": _assess_field_discrepancy_severity(field, edc_value, source_value)
                })
    
    # Calculate match score
    match_score = len(matching_fields) / total_fields if total_fields > 0 else 0.0
    
    # Generate recommendations
    recommendations = []
    if match_score < 0.8:
        recommendations.append("Low match score - review data entry procedures")
    if len(discrepancies) > 3:
        recommendations.append("Multiple discrepancies detected - consider site retraining")
    
    result = {
        "match_score": match_score,
        "matching_fields": matching_fields,
        "discrepancies": discrepancies,
        "total_fields_compared": total_fields,
        "recommendations": recommendations,
        "analysis_date": datetime.now().isoformat()
    }
    
    return json.dumps(result)


@function_tool
def check_regulatory_compliance(
    context: QueryAnalysisContext,
    subject_data: str
) -> str:
    """Check subject data for regulatory compliance issues."""
    
    # Parse input data
    subject_data_dict = json.loads(subject_data)
    
    violations = []
    warnings = []
    compliance_score = 1.0
    
    # Check informed consent
    if not subject_data_dict.get("informed_consent_date"):
        violations.append("Missing informed consent date")
        compliance_score -= 0.3
    
    # Check eligibility criteria
    if not subject_data_dict.get("inclusion_criteria_met", True):
        violations.append("Inclusion criteria not met")
        compliance_score -= 0.4
    
    # Check adverse event reporting
    adverse_events = subject_data_dict.get("adverse_events", [])
    for ae in adverse_events:
        if ae.get("serious", False) and not ae.get("reported_within_24h", False):
            violations.append(f"SAE not reported within 24 hours: {ae.get('term', 'Unknown')}")
            compliance_score -= 0.2
    
    # Check protocol deviations
    deviations = subject_data_dict.get("protocol_deviations", [])
    for deviation in deviations:
        if deviation.get("severity") == "major":
            warnings.append(f"Major protocol deviation: {deviation.get('description', 'Unknown')}")
            compliance_score -= 0.1
    
    # Ensure score doesn't go below 0
    compliance_score = max(0.0, compliance_score)
    
    # Generate recommendations
    recommendations = []
    if violations:
        recommendations.append("Address regulatory violations immediately")
    if warnings:
        recommendations.append("Review protocol adherence with site staff")
    if compliance_score < 0.7:
        recommendations.append("Consider additional monitoring for this subject")
    
    result = {
        "compliance_score": compliance_score,
        "violations": violations,
        "warnings": warnings,
        "recommendations": recommendations,
        "subject_id": subject_data_dict.get("subject_id", ""),
        "analysis_date": datetime.now().isoformat()
    }
    
    return json.dumps(result)


# Helper functions
def _determine_category(data_point: Dict[str, Any]) -> QueryCategory:
    """Determine the category of a query based on data characteristics."""
    edc_value = str(data_point.get("edc_value", "")).strip()
    source_value = str(data_point.get("source_value", "")).strip()
    field_name = data_point.get("field_name", "").lower()
    
    # Missing data
    if not edc_value or not source_value:
        return QueryCategory.MISSING_DATA
    
    # Data discrepancy
    if edc_value != source_value:
        return QueryCategory.DATA_DISCREPANCY
    
    # Adverse event related
    if any(term in field_name for term in ["adverse", "ae", "sae", "event"]):
        return QueryCategory.ADVERSE_EVENT
    
    # Laboratory values
    if any(term in field_name for term in ["lab", "blood", "urine", "hemoglobin", "glucose"]):
        return QueryCategory.LABORATORY_VALUE
    
    return QueryCategory.OTHER


def _assess_severity(data_point: Dict[str, Any], field_name: str, edc_value: str, source_value: str) -> QuerySeverity:
    """Assess the severity of a data issue."""
    field_lower = field_name.lower()
    edc_lower = edc_value.lower()
    source_lower = source_value.lower()
    
    # Critical severity for safety-related fields
    if any(term in field_lower for term in ["death", "fatal", "life-threatening"]):
        return QuerySeverity.CRITICAL
    
    # Critical severity for serious medical terms
    if any(term in edc_lower or term in source_lower for term in CRITICAL_MEDICAL_TERMS):
        return QuerySeverity.CRITICAL
    
    # Major severity for important medical terms
    if any(term in edc_lower or term in source_lower for term in MAJOR_MEDICAL_TERMS):
        return QuerySeverity.MAJOR
    
    # Major severity for primary endpoint fields
    if any(term in field_lower for term in ["primary", "endpoint", "efficacy"]):
        return QuerySeverity.MAJOR
    
    # Minor severity for significant discrepancies
    try:
        if edc_value and source_value:
            edc_num = float(edc_value)
            source_num = float(source_value)
            if abs(edc_num - source_num) / max(abs(edc_num), abs(source_num), 1) > 0.1:
                return QuerySeverity.MINOR
    except (ValueError, TypeError):
        pass
    
    return QuerySeverity.INFO


def _calculate_confidence(data_point: Dict[str, Any]) -> float:
    """Calculate confidence score for the analysis."""
    confidence = 0.5  # Base confidence
    
    # Increase confidence if we have both values
    if data_point.get("edc_value") and data_point.get("source_value"):
        confidence += 0.3
    
    # Increase confidence if we have subject and visit info
    if data_point.get("subject_id") and data_point.get("visit"):
        confidence += 0.2
    
    # Cap at 1.0
    return min(1.0, confidence)


def _generate_description(data_point: Dict[str, Any], category: QueryCategory) -> str:
    """Generate a human-readable description of the issue."""
    subject_id = data_point.get("subject_id", "Unknown Subject")
    visit = data_point.get("visit", "Unknown Visit")
    field_name = data_point.get("field_name", "Unknown Field")
    edc_value = data_point.get("edc_value", "")
    source_value = data_point.get("source_value", "")
    
    if category == QueryCategory.DATA_DISCREPANCY:
        return f"EDC value ({edc_value}) differs from source document ({source_value}) for {field_name}"
    elif category == QueryCategory.MISSING_DATA:
        if not edc_value:
            return f"Missing EDC value for {field_name}"
        else:
            return f"Missing source document value for {field_name}"
    else:
        return f"{category.value.replace('_', ' ').title()} identified for {field_name}"


def _generate_suggested_actions(category: QueryCategory, severity: QuerySeverity) -> List[str]:
    """Generate suggested actions based on category and severity."""
    actions = []
    
    if category == QueryCategory.DATA_DISCREPANCY:
        actions.extend(["Review source document", "Verify data entry", "Contact site for clarification"])
    elif category == QueryCategory.MISSING_DATA:
        actions.extend(["Obtain missing data from site", "Check for alternative sources"])
    elif category == QueryCategory.ADVERSE_EVENT:
        actions.extend(["Verify AE details", "Check reporting timelines", "Assess causality"])
    
    if severity in [QuerySeverity.CRITICAL, QuerySeverity.MAJOR]:
        actions.insert(0, "Prioritize immediate review")
    
    return actions


def _determine_medical_context(field_name: str, edc_value: str, source_value: str) -> Optional[str]:
    """Determine medical context for the field."""
    field_lower = field_name.lower()
    
    if "hemoglobin" in field_lower:
        return "Hemoglobin levels are critical for assessing anemia and treatment response"
    elif "blood pressure" in field_lower or "bp" in field_lower:
        return "Blood pressure monitoring is essential for cardiovascular safety"
    elif "weight" in field_lower:
        return "Weight changes may indicate treatment efficacy or safety concerns"
    
    return None


def _assess_regulatory_impact(category: QueryCategory, severity: QuerySeverity, field_name: str) -> Optional[str]:
    """Assess potential regulatory impact."""
    if severity == QuerySeverity.CRITICAL:
        return "Critical issue - may affect regulatory submission"
    elif severity == QuerySeverity.MAJOR and category == QueryCategory.ADVERSE_EVENT:
        return "May require regulatory reporting within specified timelines"
    elif "primary" in field_name.lower() or "endpoint" in field_name.lower():
        return "May affect primary endpoint analysis and regulatory conclusions"
    
    return None


def _assess_field_discrepancy_severity(field: str, edc_value: Any, source_value: Any) -> str:
    """Assess severity of field discrepancy."""
    field_lower = field.lower()
    
    if any(term in field_lower for term in ["primary", "endpoint", "efficacy"]):
        return "major"
    elif any(term in field_lower for term in ["safety", "adverse", "vital"]):
        return "major"
    else:
        return "minor"


# Create the Query Analyzer Agent
query_analyzer_agent = Agent(
    name="Clinical Query Analyzer",
    instructions="""You are a Clinical Query Analyzer specialized in analyzing clinical trial data for discrepancies, missing information, and protocol deviations.

Your responsibilities:
1. Analyze individual data points for potential issues
2. Perform batch analysis for efficiency
3. Detect patterns across historical data
4. Cross-reference data between systems (EDC vs source documents)
5. Check regulatory compliance requirements
6. Assess medical significance and severity
7. Generate actionable recommendations

Analysis Focus Areas:
- Data discrepancies between EDC and source documents
- Missing critical data points
- Protocol deviations and violations
- Adverse event reporting compliance
- Laboratory value anomalies
- Eligibility criteria compliance

Use the available tools to:
- analyze_data_point: Analyze single clinical data points
- batch_analyze_data: Process multiple data points efficiently
- detect_patterns: Identify trends across historical data
- cross_system_match: Verify data consistency between systems
- check_regulatory_compliance: Ensure regulatory adherence

Always provide confidence scores, medical context, and actionable recommendations.""",
    tools=[
        analyze_data_point,
        batch_analyze_data,
        detect_patterns,
        cross_system_match,
        check_regulatory_compliance
    ],
    model="gpt-4-turbo-preview"
)


class QueryAnalyzer:
    """Query Analyzer for clinical trials data analysis."""
    
    def __init__(self):
        """Initialize the Query Analyzer."""
        self.agent = query_analyzer_agent
        self.context = QueryAnalysisContext()
        self.medical_terms = MEDICAL_TERM_MAPPING
        self.critical_terms = CRITICAL_MEDICAL_TERMS
        self.major_terms = MAJOR_MEDICAL_TERMS
        
        # Configuration
        self.confidence_threshold = 0.7
        self.severity_filter = QuerySeverity.INFO
        self.max_batch_size = 100
        self.recommended_batch_size = 25
        
        # Mock assistant for test compatibility
        self.assistant = type('obj', (object,), {
            'id': 'asst_query_analyzer',
            'name': 'Clinical Query Analyzer'
        })
        
        self.instructions = self.agent.instructions
    
    async def analyze_data_point(self, data_point: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a single data point."""
        result_json = analyze_data_point(self.context, json.dumps(data_point))
        return json.loads(result_json)
    
    async def batch_analyze(self, data_points: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze multiple data points in batch."""
        result_json = batch_analyze_data(self.context, json.dumps(data_points))
        return json.loads(result_json)
    
    async def detect_patterns(self, historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect patterns in historical data."""
        result_json = detect_patterns(self.context, json.dumps(historical_data))
        return json.loads(result_json)
    
    async def cross_system_match(self, edc_data: Dict[str, Any], source_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform cross-system data matching."""
        result_json = cross_system_match(self.context, json.dumps(edc_data), json.dumps(source_data))
        return json.loads(result_json)
    
    async def check_regulatory_compliance(self, subject_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check regulatory compliance."""
        result_json = check_regulatory_compliance(self.context, json.dumps(subject_data))
        return json.loads(result_json)
    
    def assess_medical_severity(self, medical_term: str) -> QuerySeverity:
        """Assess medical severity of a term."""
        term_lower = medical_term.lower()
        
        if any(critical_term in term_lower for critical_term in self.critical_terms):
            return QuerySeverity.CRITICAL
        elif any(major_term in term_lower for major_term in self.major_terms):
            return QuerySeverity.MAJOR
        else:
            return QuerySeverity.INFO
    
    def standardize_medical_term(self, term: str) -> str:
        """Standardize medical terminology."""
        term_upper = term.upper()
        return self.medical_terms.get(term_upper, term)
    
    def set_confidence_threshold(self, threshold: float) -> None:
        """Set confidence threshold."""
        if not 0.0 <= threshold <= 1.0:
            raise ValueError("Confidence threshold must be between 0.0 and 1.0")
        self.confidence_threshold = threshold
    
    def set_severity_filter(self, severity: QuerySeverity) -> None:
        """Set severity filter."""
        self.severity_filter = severity


__all__ = [
    "QueryAnalyzer",
    "QueryAnalysisContext", 
    "QueryCategory",
    "QuerySeverity",
    "analyze_data_point",
    "batch_analyze_data",
    "detect_patterns",
    "cross_system_match",
    "check_regulatory_compliance",
    "query_analyzer_agent"
]