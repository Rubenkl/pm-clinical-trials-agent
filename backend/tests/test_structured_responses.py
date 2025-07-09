"""
Test suite for structured response models.
Following TDD: These tests should FAIL initially, then we implement to make them pass.
"""

import pytest
from datetime import datetime
from pydantic import ValidationError

from app.api.models.structured_responses import (
    QueryAnalyzerResponse,
    DataVerifierResponse,
    DeviationDetectionResponse,
    QueryStatistics,
    SDVStatistics,
    SeverityLevel,
    QueryStatus,
    SubjectInfo,
    QueryContext,
    ClinicalFinding,
    AIAnalysis,
    DiscrepancyDetail,
    SDVProgress,
    VerificationField,
    DeviationDetail,
    ImpactAssessment,
    SystemHealthMetrics,
    TrialOverviewResponse
)


class TestSeverityLevel:
    """Test severity level enum"""
    
    def test_severity_levels_exist(self):
        """Test that all required severity levels exist"""
        assert SeverityLevel.CRITICAL == "critical"
        assert SeverityLevel.MAJOR == "major"
        assert SeverityLevel.MINOR == "minor"
        assert SeverityLevel.INFO == "info"


class TestQueryStatus:
    """Test query status enum"""
    
    def test_query_statuses_exist(self):
        """Test that all required query statuses exist"""
        assert QueryStatus.PENDING == "pending"
        assert QueryStatus.PENDING_REVIEW == "pending_review"
        assert QueryStatus.RESOLVED == "resolved"
        assert QueryStatus.CLOSED == "closed"
        assert QueryStatus.ESCALATED == "escalated"


class TestSubjectInfo:
    """Test subject information model"""
    
    def test_subject_info_creation(self):
        """Test creating subject info with required fields"""
        subject = SubjectInfo(
            id="SUBJ001",
            initials="JD",
            site="Boston General",
            site_id="SITE01"
        )
        assert subject.id == "SUBJ001"
        assert subject.initials == "JD"
        assert subject.site == "Boston General"
        assert subject.site_id == "SITE01"
    
    def test_subject_info_with_optional_fields(self):
        """Test creating subject info with optional fields"""
        enrollment_date = datetime.now()
        subject = SubjectInfo(
            id="SUBJ001",
            initials="JD",
            site="Boston General",
            site_id="SITE01",
            enrollment_date=enrollment_date,
            study_arm="Treatment"
        )
        assert subject.enrollment_date == enrollment_date
        assert subject.study_arm == "Treatment"
    
    def test_subject_info_validation(self):
        """Test that required fields are validated"""
        with pytest.raises(ValidationError):
            SubjectInfo(
                initials="JD",
                site="Boston General",
                site_id="SITE01"
                # Missing required 'id' field
            )


class TestClinicalFinding:
    """Test clinical finding model"""
    
    def test_clinical_finding_creation(self):
        """Test creating clinical finding with required fields"""
        finding = ClinicalFinding(
            parameter="hemoglobin",
            value="8.5 g/dL",
            interpretation="Severe anemia",
            severity=SeverityLevel.CRITICAL,
            clinical_significance="Risk of tissue hypoxia"
        )
        assert finding.parameter == "hemoglobin"
        assert finding.value == "8.5 g/dL"
        assert finding.interpretation == "Severe anemia"
        assert finding.severity == SeverityLevel.CRITICAL
        assert finding.clinical_significance == "Risk of tissue hypoxia"
    
    def test_clinical_finding_with_optional_fields(self):
        """Test creating clinical finding with optional fields"""
        finding = ClinicalFinding(
            parameter="hemoglobin",
            value="8.5 g/dL",
            interpretation="Severe anemia",
            normal_range="12-16 g/dL",
            severity=SeverityLevel.CRITICAL,
            clinical_significance="Risk of tissue hypoxia",
            previous_value="11.2 g/dL"
        )
        assert finding.normal_range == "12-16 g/dL"
        assert finding.previous_value == "11.2 g/dL"


class TestAIAnalysis:
    """Test AI analysis model"""
    
    def test_ai_analysis_creation(self):
        """Test creating AI analysis with required fields"""
        analysis = AIAnalysis(
            interpretation="Critical finding requiring immediate review",
            clinical_significance="high",
            confidence_score=0.95,
            suggested_query="Please confirm hemoglobin value",
            recommendations=["Verify lab results", "Check for bleeding"]
        )
        assert analysis.interpretation == "Critical finding requiring immediate review"
        assert analysis.clinical_significance == "high"
        assert analysis.confidence_score == 0.95
        assert analysis.suggested_query == "Please confirm hemoglobin value"
        assert len(analysis.recommendations) == 2
    
    def test_confidence_score_validation(self):
        """Test that confidence score is between 0 and 1"""
        with pytest.raises(ValidationError):
            AIAnalysis(
                interpretation="Test",
                clinical_significance="high",
                confidence_score=1.5,  # Invalid: > 1
                suggested_query="Test",
                recommendations=["Test"]
            )
        
        with pytest.raises(ValidationError):
            AIAnalysis(
                interpretation="Test",
                clinical_significance="high",
                confidence_score=-0.1,  # Invalid: < 0
                suggested_query="Test",
                recommendations=["Test"]
            )


class TestQueryAnalyzerResponse:
    """Test query analyzer response model"""
    
    def test_query_analyzer_response_creation(self):
        """Test creating complete query analyzer response"""
        subject = SubjectInfo(
            id="SUBJ001",
            initials="JD",
            site="Boston General",
            site_id="SITE01"
        )
        
        clinical_context = QueryContext(
            visit="Week 12",
            field="hemoglobin",
            value="8.5 g/dL",
            form_name="Laboratory Results"
        )
        
        finding = ClinicalFinding(
            parameter="hemoglobin",
            value="8.5 g/dL",
            interpretation="Severe anemia",
            severity=SeverityLevel.CRITICAL,
            clinical_significance="Risk of tissue hypoxia"
        )
        
        ai_analysis = AIAnalysis(
            interpretation="Critical finding",
            clinical_significance="high",
            confidence_score=0.95,
            suggested_query="Please confirm value",
            recommendations=["Verify results"]
        )
        
        response = QueryAnalyzerResponse(
            success=True,
            query_id="Q-2025-001",
            created_date=datetime.now(),
            status=QueryStatus.PENDING,
            severity=SeverityLevel.CRITICAL,
            category="laboratory_value",
            subject=subject,
            clinical_context=clinical_context,
            clinical_findings=[finding],
            ai_analysis=ai_analysis,
            execution_time=1.2,
            confidence_score=0.95,
            raw_response="Raw analysis text"
        )
        
        assert response.success is True
        assert response.query_id == "Q-2025-001"
        assert response.status == QueryStatus.PENDING
        assert response.severity == SeverityLevel.CRITICAL
        assert response.category == "laboratory_value"
        assert response.subject.id == "SUBJ001"
        assert len(response.clinical_findings) == 1
        assert response.execution_time == 1.2
        assert response.agent_id == "query-analyzer"  # Default value
    
    def test_query_analyzer_response_required_fields(self):
        """Test that required fields are validated"""
        with pytest.raises(ValidationError):
            QueryAnalyzerResponse(
                success=True,
                # Missing required fields
                execution_time=1.0,
                confidence_score=0.8,
                raw_response="Test"
            )


class TestDataVerifierResponse:
    """Test data verifier response model"""
    
    def test_data_verifier_response_creation(self):
        """Test creating data verifier response"""
        subject = SubjectInfo(
            id="SUBJ001",
            initials="JD",
            site="Boston General",
            site_id="SITE01"
        )
        
        discrepancy = DiscrepancyDetail(
            field="blood_pressure",
            field_label="Blood Pressure",
            edc_value="120/80",
            source_value="130/85",
            severity=SeverityLevel.MINOR,
            discrepancy_type="mismatch",
            confidence=0.9
        )
        
        progress = SDVProgress(
            total_fields=100,
            verified=75,
            discrepancies=5,
            skipped=2,
            completion_rate=0.75
        )
        
        verification_field = VerificationField(
            field_name="systolic_bp",
            field_label="Systolic Blood Pressure",
            edc_value="120",
            field_type="numeric",
            required=True
        )
        
        response = DataVerifierResponse(
            success=True,
            verification_id="SDV-2025-001",
            site="Boston General",
            monitor="Jane Smith",
            verification_date=datetime.now(),
            subject=subject,
            visit="Week 12",
            match_score=0.85,
            matching_fields=["age", "gender"],
            discrepancies=[discrepancy],
            total_fields_compared=100,
            progress=progress,
            fields_to_verify=[verification_field],
            recommendations=["Review discrepancies"],
            critical_findings=[],
            execution_time=2.5,
            raw_response="Verification analysis"
        )
        
        assert response.success is True
        assert response.verification_id == "SDV-2025-001"
        assert response.site == "Boston General"
        assert response.monitor == "Jane Smith"
        assert response.match_score == 0.85
        assert len(response.discrepancies) == 1
        assert response.progress.completion_rate == 0.75
        assert len(response.fields_to_verify) == 1
        assert response.agent_id == "data-verifier"


class TestQueryStatistics:
    """Test query statistics model"""
    
    def test_query_statistics_creation(self):
        """Test creating query statistics"""
        stats = QueryStatistics(
            total_queries=234,
            open_queries=45,
            critical_queries=5,
            major_queries=23,
            minor_queries=17,
            resolved_today=12,
            resolved_this_week=78,
            average_resolution_time=24.5,
            queries_by_site={"SITE01": 15, "SITE02": 12},
            queries_by_category={"lab": 20, "vitals": 15},
            trend_data=[{"date": "2025-01-01", "queries": 8}]
        )
        
        assert stats.total_queries == 234
        assert stats.open_queries == 45
        assert stats.critical_queries == 5
        assert stats.average_resolution_time == 24.5
        assert stats.queries_by_site["SITE01"] == 15
        assert stats.queries_by_category["lab"] == 20
        assert len(stats.trend_data) == 1


class TestSystemHealthMetrics:
    """Test system health metrics model"""
    
    def test_system_health_metrics_creation(self):
        """Test creating system health metrics"""
        metrics = SystemHealthMetrics(
            agents_online=5,
            total_agents=5,
            average_response_time=1.5,
            queries_processed_today=120,
            sdv_completed_today=25,
            deviations_detected_today=3,
            system_uptime=99.9,
            active_workflows=8,
            error_rate=0.01,
            agent_activities=[]
        )
        
        assert metrics.agents_online == 5
        assert metrics.total_agents == 5
        assert metrics.average_response_time == 1.5
        assert metrics.queries_processed_today == 120
        assert metrics.system_uptime == 99.9
        assert metrics.error_rate == 0.01


class TestTrialOverviewResponse:
    """Test trial overview response model"""
    
    def test_trial_overview_response_creation(self):
        """Test creating trial overview response"""
        overview = TrialOverviewResponse(
            trial_id="TRIAL-2025-001",
            trial_name="Phase III Cardiovascular Study",
            phase="III",
            enrolled_subjects=234,
            target_enrollment=500,
            enrollment_percentage=46.8,
            enrollment_trend="on_track",
            open_queries=45,
            query_rate_change=-12.0,
            average_query_age=5.2,
            sdv_completion=0.78,
            sdv_findings=12,
            major_deviations=3,
            minor_deviations=12,
            deviation_rate=0.05,
            total_sites=10,
            active_sites=8,
            sites_at_risk=1,
            health_score=85.5,
            health_trend="stable",
            key_risks=[],
            agent_insights=[]
        )
        
        assert overview.trial_id == "TRIAL-2025-001"
        assert overview.trial_name == "Phase III Cardiovascular Study"
        assert overview.phase == "III"
        assert overview.enrolled_subjects == 234
        assert overview.target_enrollment == 500
        assert overview.enrollment_percentage == 46.8
        assert overview.enrollment_trend == "on_track"
        assert overview.health_score == 85.5
        assert overview.health_trend == "stable"


class TestDiscrepancyDetail:
    """Test discrepancy detail model"""
    
    def test_discrepancy_detail_creation(self):
        """Test creating discrepancy detail"""
        discrepancy = DiscrepancyDetail(
            field="blood_pressure",
            field_label="Blood Pressure",
            edc_value="120/80",
            source_value="130/85",
            severity=SeverityLevel.MINOR,
            discrepancy_type="mismatch",
            confidence=0.9
        )
        
        assert discrepancy.field == "blood_pressure"
        assert discrepancy.field_label == "Blood Pressure"
        assert discrepancy.edc_value == "120/80"
        assert discrepancy.source_value == "130/85"
        assert discrepancy.severity == SeverityLevel.MINOR
        assert discrepancy.discrepancy_type == "mismatch"
        assert discrepancy.confidence == 0.9
    
    def test_discrepancy_confidence_validation(self):
        """Test that confidence score is between 0 and 1"""
        with pytest.raises(ValidationError):
            DiscrepancyDetail(
                field="test",
                field_label="Test",
                edc_value="test",
                source_value="test",
                severity=SeverityLevel.MINOR,
                discrepancy_type="mismatch",
                confidence=1.5  # Invalid: > 1
            )


class TestSDVProgress:
    """Test SDV progress model"""
    
    def test_sdv_progress_creation(self):
        """Test creating SDV progress"""
        progress = SDVProgress(
            total_fields=100,
            verified=75,
            discrepancies=5,
            skipped=2,
            completion_rate=0.75,
            estimated_time_remaining=30
        )
        
        assert progress.total_fields == 100
        assert progress.verified == 75
        assert progress.discrepancies == 5
        assert progress.skipped == 2
        assert progress.completion_rate == 0.75
        assert progress.estimated_time_remaining == 30
    
    def test_sdv_progress_completion_rate_validation(self):
        """Test that completion rate is between 0 and 1"""
        with pytest.raises(ValidationError):
            SDVProgress(
                total_fields=100,
                verified=75,
                discrepancies=5,
                skipped=2,
                completion_rate=1.5  # Invalid: > 1
            )


class TestVerificationField:
    """Test verification field model"""
    
    def test_verification_field_creation(self):
        """Test creating verification field"""
        field = VerificationField(
            field_name="systolic_bp",
            field_label="Systolic Blood Pressure",
            edc_value="120",
            source_image_url="/api/images/doc1.jpg",
            source_page=1,
            coordinates={"x": 100, "y": 200, "width": 50, "height": 20},
            field_type="numeric",
            required=True
        )
        
        assert field.field_name == "systolic_bp"
        assert field.field_label == "Systolic Blood Pressure"
        assert field.edc_value == "120"
        assert field.source_image_url == "/api/images/doc1.jpg"
        assert field.source_page == 1
        assert field.coordinates["x"] == 100
        assert field.field_type == "numeric"
        assert field.required is True