"""
Structured response models for clinical trial workflows.
These models transform agent outputs into UI-friendly JSON structures.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from enum import Enum


class SeverityLevel(str, Enum):
    CRITICAL = "critical"
    MAJOR = "major" 
    MINOR = "minor"
    INFO = "info"


class QueryStatus(str, Enum):
    PENDING = "pending"
    PENDING_REVIEW = "pending_review"
    RESOLVED = "resolved"
    CLOSED = "closed"
    ESCALATED = "escalated"


class ClinicalFinding(BaseModel):
    """Represents a clinical finding from data analysis"""
    parameter: str
    value: str
    interpretation: str
    normal_range: Optional[str] = None
    severity: SeverityLevel
    clinical_significance: str
    previous_value: Optional[str] = None


class SubjectInfo(BaseModel):
    """Subject information for queries"""
    id: str
    initials: str
    site: str
    site_id: str
    enrollment_date: Optional[datetime] = None
    study_arm: Optional[str] = None


class QueryContext(BaseModel):
    """Clinical context for a query"""
    visit: str
    field: str
    value: str
    expected_value: Optional[str] = None
    normal_range: Optional[str] = None
    previous_value: Optional[str] = None
    form_name: str
    page_number: Optional[int] = None


class AIAnalysis(BaseModel):
    """AI-generated analysis and recommendations"""
    interpretation: str
    clinical_significance: str = Field(description="high, medium, low")
    confidence_score: float = Field(ge=0.0, le=1.0)
    suggested_query: str
    recommendations: List[str]
    supporting_evidence: Optional[List[str]] = None
    ich_gcp_reference: Optional[str] = None


class QueryAnalyzerResponse(BaseModel):
    """Structured response from Query Analyzer agent"""
    success: bool
    response_type: str = "clinical_analysis"
    
    # Query identification
    query_id: str
    created_date: datetime
    
    # Query details
    status: QueryStatus
    severity: SeverityLevel
    category: str  # laboratory_value, vital_signs, adverse_event, etc.
    
    # Subject and clinical context
    subject: SubjectInfo
    clinical_context: QueryContext
    
    # Clinical findings
    clinical_findings: List[ClinicalFinding]
    
    # AI analysis
    ai_analysis: AIAnalysis
    
    # Metadata
    agent_id: str = "query-analyzer"
    execution_time: float
    confidence_score: float
    raw_response: str  # Original text for backward compatibility
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DiscrepancyDetail(BaseModel):
    """Details of a data discrepancy"""
    field: str
    field_label: str
    edc_value: str
    source_value: str
    severity: SeverityLevel
    discrepancy_type: str  # missing, mismatch, format_error, etc.
    confidence: float = Field(ge=0.0, le=1.0)


class SDVProgress(BaseModel):
    """Source data verification progress"""
    total_fields: int
    verified: int
    discrepancies: int
    skipped: int
    completion_rate: float = Field(ge=0.0, le=1.0)
    estimated_time_remaining: Optional[int] = None  # minutes


class VerificationField(BaseModel):
    """Field to be verified in SDV"""
    field_name: str
    field_label: str
    edc_value: str
    source_image_url: Optional[str] = None
    source_page: Optional[int] = None
    coordinates: Optional[Dict[str, int]] = None  # x, y, width, height
    field_type: str  # text, numeric, date, checkbox, etc.
    required: bool = True


class DataVerifierResponse(BaseModel):
    """Structured response from Data Verifier agent"""
    success: bool
    response_type: str = "data_verification"
    
    # Verification session info
    verification_id: str
    site: str
    monitor: str
    verification_date: datetime
    
    # Subject being verified
    subject: SubjectInfo
    visit: str
    
    # Verification results
    match_score: float = Field(ge=0.0, le=1.0)
    matching_fields: List[str]
    discrepancies: List[DiscrepancyDetail]
    total_fields_compared: int
    
    # Progress tracking
    progress: SDVProgress
    
    # Current verification state
    fields_to_verify: List[VerificationField]
    
    # Recommendations
    recommendations: List[str]
    critical_findings: List[str]
    
    # Metadata
    agent_id: str = "data-verifier"
    execution_time: float
    raw_response: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DeviationDetail(BaseModel):
    """Protocol deviation details"""
    criterion: str
    expected_value: str
    actual_value: str
    detection_method: str  # automated_check, manual_review, etc.
    occurrence_date: datetime
    reported_date: Optional[datetime] = None


class ImpactAssessment(BaseModel):
    """Impact assessment for a deviation"""
    subject_safety: str  # high, moderate, low, none
    data_integrity: str  # high, moderate, low, none
    regulatory_risk: str  # high, moderate, low, none
    study_validity: str  # high, moderate, low, none
    overall_impact: str  # critical, major, minor


class RootCauseAnalysis(BaseModel):
    """Root cause analysis for deviation"""
    primary_cause: str
    contributing_factors: List[str]
    systemic_issues: List[str]
    preventable: bool
    prevention_measures: List[str]


class DeviationDetectionResponse(BaseModel):
    """Response for protocol deviation detection"""
    success: bool
    response_type: str = "deviation_detection"
    
    # Deviation identification
    deviation_id: str
    detected_date: datetime
    
    # Deviation details
    type: str  # inclusion_criteria, dosing_error, visit_window, etc.
    severity: SeverityLevel
    subject: SubjectInfo
    details: DeviationDetail
    
    # Analysis
    impact_assessment: ImpactAssessment
    root_cause: Optional[RootCauseAnalysis] = None
    
    # Recommendations
    immediate_actions: List[str]
    corrective_actions: List[str]
    preventive_actions: List[str]
    
    # Related deviations
    similar_deviations: List[Dict[str, Any]]
    pattern_detected: bool
    
    # Metadata
    agent_id: str = "portfolio-manager"  # Since we don't have deviation agent yet
    execution_time: float
    raw_response: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class QueryStatistics(BaseModel):
    """Dashboard statistics for queries"""
    total_queries: int
    open_queries: int
    critical_queries: int
    major_queries: int
    minor_queries: int
    resolved_today: int
    resolved_this_week: int
    average_resolution_time: float  # hours
    queries_by_site: Dict[str, int]
    queries_by_category: Dict[str, int]
    trend_data: List[Dict[str, Any]]  # For charts


class SDVStatistics(BaseModel):
    """Dashboard statistics for SDV"""
    total_subjects: int
    verified_subjects: int
    total_data_points: int
    verified_data_points: int
    overall_completion: float
    discrepancy_rate: float
    sites_summary: List[Dict[str, Any]]
    high_risk_sites: List[str]
    resource_utilization: Dict[str, float]


class AgentActivity(BaseModel):
    """Agent activity log entry"""
    timestamp: datetime
    agent_id: str
    agent_name: str
    action: str
    details: str
    impact: Optional[str] = None
    execution_time: float


class SystemHealthMetrics(BaseModel):
    """System health and performance metrics"""
    agents_online: int
    total_agents: int
    average_response_time: float  # seconds
    queries_processed_today: int
    sdv_completed_today: int
    deviations_detected_today: int
    system_uptime: float  # percentage
    active_workflows: int
    error_rate: float
    agent_activities: List[AgentActivity]


class TrialOverviewResponse(BaseModel):
    """Executive overview of trial health"""
    trial_id: str
    trial_name: str
    phase: str  # I, II, III, IV
    
    # Enrollment metrics
    enrolled_subjects: int
    target_enrollment: int
    enrollment_percentage: float
    enrollment_trend: str  # ahead, on_track, behind
    
    # Query metrics
    open_queries: int
    query_rate_change: float  # percentage change from last period
    average_query_age: float  # days
    
    # SDV metrics
    sdv_completion: float
    sdv_findings: int
    
    # Deviation metrics
    major_deviations: int
    minor_deviations: int
    deviation_rate: float  # per subject
    
    # Site performance
    total_sites: int
    active_sites: int
    sites_at_risk: int
    
    # Overall health score
    health_score: float  # 0-100
    health_trend: str  # improving, stable, declining
    
    # Key risks
    key_risks: List[Dict[str, Any]]
    
    # Recent agent insights
    agent_insights: List[str]
    
    metadata: Dict[str, Any] = Field(default_factory=dict)


class BatchQueryResponse(BaseModel):
    """Response for batch query operations"""
    success: bool
    total_queries: int
    processed: int
    failed: int
    results: List[QueryAnalyzerResponse]
    errors: List[Dict[str, str]]
    execution_time: float
    metadata: Dict[str, Any] = Field(default_factory=dict)


class QueryWorkflowResponse(BaseModel):
    """Response from orchestrate_query_workflow"""
    success: bool
    workflow_id: str
    workflow_type: str = "query_analysis"
    
    # Analysis results
    analysis_results: Dict[str, Any]
    discrepancies_found: List[Dict[str, Any]]
    generated_queries: List[Dict[str, Any]]
    
    # Workflow execution
    agents_executed: List[str]
    execution_steps: List[Dict[str, Any]]
    
    # Automated actions taken
    automated_actions: List[str]
    dashboard_update: Dict[str, Any]
    
    # Performance metrics
    execution_time: float
    metrics: Dict[str, Any] = Field(default_factory=dict)
    
    # Status
    status: str = "completed"
    error: Optional[str] = None
    
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SDVWorkflowResponse(BaseModel):
    """Response from orchestrate_sdv_workflow"""
    success: bool
    workflow_id: str
    workflow_type: str = "source_data_verification"
    
    # SDV results
    verification_plan: Dict[str, Any]
    risk_scores: Dict[str, float]
    scheduled_verifications: List[Dict[str, Any]]
    
    # Quality metrics
    data_quality_score: float = Field(ge=0.0, le=1.0)
    completion_percentage: float = Field(ge=0.0, le=100.0)
    discrepancy_rate: float = Field(ge=0.0, le=1.0)
    
    # Automated actions
    automated_actions: List[str]
    dashboard_update: Dict[str, Any]
    
    # Performance
    execution_time: float
    estimated_completion_time: Optional[float] = None
    
    # Status
    status: str = "completed"
    error: Optional[str] = None
    
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DeviationWorkflowResponse(BaseModel):
    """Response from orchestrate_deviation_workflow"""
    success: bool
    workflow_id: str
    workflow_type: str = "deviation_monitoring"
    
    # Deviation detection results
    deviations_detected: List[Dict[str, Any]]
    compliance_status: str  # compliant, non_compliant, needs_review
    deviation_alerts: List[Dict[str, Any]]
    
    # Pattern analysis
    patterns_identified: List[Dict[str, Any]]
    risk_assessment: Dict[str, Any]
    
    # Automated actions
    automated_actions: List[str]
    escalations_triggered: List[Dict[str, Any]]
    dashboard_update: Dict[str, Any]
    
    # Performance
    execution_time: float
    subjects_analyzed: int
    
    # Status
    status: str = "completed"
    error: Optional[str] = None
    
    metadata: Dict[str, Any] = Field(default_factory=dict)


class WorkflowExecutionResponse(BaseModel):
    """Response for complex multi-agent workflows"""
    success: bool
    workflow_id: str
    workflow_type: str
    
    # Execution details
    started_at: datetime
    completed_at: Optional[datetime] = None
    status: str  # running, completed, failed, partial
    
    # Agent participation
    agents_involved: List[str]
    handoffs_completed: int
    
    # Results by step
    steps: List[Dict[str, Any]]
    
    # Aggregated results
    aggregated_findings: Dict[str, Any]
    recommendations: List[str]
    actions_required: List[Dict[str, Any]]
    
    # Performance
    total_execution_time: float
    agent_execution_times: Dict[str, float]
    
    # Errors and warnings
    errors: List[str]
    warnings: List[str]
    
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DashboardOverviewResponse(BaseModel):
    """Dashboard overview response for GET /api/v1/dashboard/overview"""
    success: bool = True
    
    # Trial overview
    trial_metrics: TrialOverviewResponse
    
    # Query metrics
    query_statistics: QueryStatistics
    
    # SDV metrics
    sdv_statistics: SDVStatistics
    
    # System health
    system_health: SystemHealthMetrics
    
    # Recent activity
    recent_activities: List[AgentActivity]
    
    # Alerts and notifications
    critical_alerts: List[Dict[str, Any]]
    pending_actions: List[Dict[str, Any]]
    
    # Performance summary
    performance_summary: Dict[str, Any]
    
    # Last updated
    last_updated: datetime = Field(default_factory=datetime.now)
    
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DiscrepancyFinding(BaseModel):
    """Individual discrepancy finding for API responses"""
    finding_id: str
    field_name: str
    field_label: str
    edc_value: str
    source_value: str
    discrepancy_type: str  # missing, mismatch, format_error
    severity: SeverityLevel
    confidence: float = Field(ge=0.0, le=1.0)
    detection_method: str  # automated, manual
    detected_date: datetime
    resolution_status: str = "pending"  # pending, resolved, dismissed


class QueryAnalysisResponse(BaseModel):
    """Simplified response model for query analysis endpoint"""
    success: bool
    
    # Query identification
    query_id: str
    analysis_type: str = "clinical_data_analysis"
    
    # Subject and context
    subject_id: str
    site_id: str
    visit: str
    
    # Analysis results
    discrepancies_found: List[DiscrepancyFinding]
    clinical_findings: List[ClinicalFinding]
    
    # AI recommendations
    recommendations: List[str]
    suggested_actions: List[str]
    priority: str  # high, medium, low
    
    # Performance
    execution_time: float
    confidence_score: float = Field(ge=0.0, le=1.0)
    
    # Metadata
    generated_at: datetime = Field(default_factory=datetime.now)
    agent_id: str = "portfolio-manager"
    
    metadata: Dict[str, Any] = Field(default_factory=dict)