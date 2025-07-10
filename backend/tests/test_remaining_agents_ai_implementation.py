"""
Test AI implementation for remaining agents (Query Analyzer, Deviation Detector, Query Tracker, Analytics).
Following TDD approach - write tests first, then implement AI functionality.
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from app.agents.query_analyzer import QueryAnalyzer
from app.agents.deviation_detector import DeviationDetector
from app.agents.query_tracker import QueryTracker
from app.agents.analytics_agent import AnalyticsAgent


class TestQueryAnalyzerAI:
    """Test AI implementation for Query Analyzer agent."""
    
    @pytest.mark.asyncio
    async def test_analyze_clinical_data_ai(self):
        """Test that Query Analyzer uses AI for clinical data analysis."""
        # Test data with complex clinical scenario
        test_data = {
            "subject_id": "CARD001",
            "clinical_data": {
                "hemoglobin": "7.2",  # Critically low
                "heart_rate": "145",  # Tachycardia
                "blood_pressure": "85/50",  # Hypotension
                "medications": ["norepinephrine", "dopamine"],  # Vasopressors
                "symptoms": ["chest pain", "shortness of breath", "dizziness"]
            },
            "medical_history": ["coronary artery disease", "heart failure"],
            "current_status": "ICU admission"
        }
        
        analyzer = QueryAnalyzer()
        
        # Mock the AI response
        mock_ai_response = Mock()
        mock_ai_response.messages = [Mock(content=json.dumps({
            "analysis": {
                "clinical_assessment": "Critical condition - patient in cardiogenic shock",
                "key_findings": [
                    "Severe anemia (Hgb 7.2 g/dL) requiring urgent transfusion",
                    "Hemodynamic instability with hypotension despite dual vasopressor support",
                    "Tachycardia likely compensatory for low cardiac output"
                ],
                "severity": "critical",
                "immediate_actions": [
                    "Urgent blood transfusion (target Hgb >9)",
                    "Echocardiogram to assess cardiac function",
                    "Consider mechanical circulatory support",
                    "Cardiology consultation STAT"
                ],
                "differential_diagnosis": [
                    "Acute coronary syndrome with cardiogenic shock",
                    "Acute decompensated heart failure",
                    "Septic shock with cardiac involvement"
                ],
                "monitoring_requirements": [
                    "Continuous cardiac monitoring",
                    "Hourly vital signs",
                    "Serial lactate and troponin levels",
                    "Urine output monitoring"
                ]
            },
            "medical_reasoning": "The combination of severe anemia, hypotension despite vasopressors, and cardiac history suggests cardiogenic shock. The critically low hemoglobin is compromising oxygen delivery and must be corrected urgently.",
            "confidence": 0.92,
            "ai_powered": True
        }))]
        
        with patch('app.agents.query_analyzer.Runner.run', new_callable=AsyncMock) as mock_run:
            mock_run.return_value = mock_ai_response
            
            # This method needs to be implemented
            result = await analyzer.analyze_clinical_data_ai(test_data)
        
        # Verify AI was called
        assert mock_run.called
        
        # Verify AI provided medical insights
        assert result.get("ai_powered") == True
        assert "clinical_assessment" in result.get("analysis", {})
        assert result["analysis"]["severity"] == "critical"
        assert len(result["analysis"]["immediate_actions"]) > 0
        assert result.get("confidence", 0) > 0.8
        
        # Verify medical reasoning was provided
        assert "medical_reasoning" in result
        assert "cardiogenic shock" in result["medical_reasoning"]


class TestDeviationDetectorAI:
    """Test AI implementation for Deviation Detector agent."""
    
    @pytest.mark.asyncio
    async def test_detect_protocol_deviations_ai(self):
        """Test that Deviation Detector uses AI for protocol violation detection."""
        # Complex protocol scenario
        protocol_data = {
            "protocol_id": "CARD-2025-001",
            "inclusion_criteria": {
                "age": "18-75 years",
                "ejection_fraction": "≤40%",
                "nyha_class": "II-IV"
            },
            "exclusion_criteria": {
                "pregnancy": True,
                "active_bleeding": True,
                "platelet_count": "<50,000"
            },
            "prohibited_medications": ["amiodarone", "dronedarone"],
            "required_procedures": {
                "echocardiogram": "baseline and every 3 months",
                "ekg": "monthly"
            }
        }
        
        subject_data = {
            "subject_id": "SUBJ042",
            "age": 68,
            "ejection_fraction": "35%",
            "nyha_class": "III",
            "current_medications": ["metoprolol", "lisinopril", "amiodarone"],  # Prohibited!
            "last_echo": "4 months ago",  # Overdue!
            "last_ekg": "2 weeks ago",
            "platelet_count": "48000"  # Below exclusion threshold!
        }
        
        detector = DeviationDetector()
        
        # Mock AI response with intelligent detection
        mock_ai_response = Mock()
        mock_ai_response.messages = [Mock(content=json.dumps({
            "deviations": [
                {
                    "type": "prohibited_medication",
                    "severity": "major",
                    "description": "Subject is taking amiodarone, which is prohibited per protocol",
                    "clinical_impact": "Amiodarone can interfere with study drug metabolism and increase QT prolongation risk",
                    "recommended_action": "Discontinue amiodarone with 5-7 day washout period before study drug initiation",
                    "regulatory_impact": "Major protocol deviation requiring notification to IRB and sponsor"
                },
                {
                    "type": "exclusion_criteria_violation",
                    "severity": "critical",
                    "description": "Platelet count 48,000 is below protocol threshold of 50,000",
                    "clinical_impact": "Increased bleeding risk, especially with antiplatelet therapy",
                    "recommended_action": "Subject should be withdrawn from study for safety",
                    "regulatory_impact": "Screen failure - document in regulatory binder"
                },
                {
                    "type": "missed_procedure",
                    "severity": "minor",
                    "description": "Echocardiogram overdue by 1 month",
                    "clinical_impact": "Missing efficacy endpoint data",
                    "recommended_action": "Schedule echo within 1 week, document reason for delay",
                    "regulatory_impact": "Minor deviation, include in monitoring report"
                }
            ],
            "overall_assessment": "Subject has critical safety concerns and should not continue in study",
            "compliance_score": 0.45,
            "ai_reasoning": "The combination of thrombocytopenia and prohibited antiarrhythmic creates unacceptable safety risk",
            "ai_powered": True
        }))]
        
        with patch('app.agents.deviation_detector.Runner.run', new_callable=AsyncMock) as mock_run:
            mock_run.return_value = mock_ai_response
            
            # This method needs to be implemented
            result = await detector.detect_protocol_deviations_ai(protocol_data, subject_data)
        
        # Verify AI was called
        assert mock_run.called
        
        # Verify AI detected all deviations
        assert result.get("ai_powered") == True
        assert len(result.get("deviations", [])) == 3
        
        # Verify AI understood clinical impact
        deviations_by_type = {d["type"]: d for d in result["deviations"]}
        assert "clinical_impact" in deviations_by_type["prohibited_medication"]
        assert "QT prolongation" in deviations_by_type["prohibited_medication"]["clinical_impact"]
        
        # Verify AI provided regulatory guidance
        assert "regulatory_impact" in deviations_by_type["exclusion_criteria_violation"]
        assert result.get("compliance_score", 1.0) < 0.5  # Low compliance


class TestQueryTrackerAI:
    """Test AI implementation for Query Tracker agent."""
    
    @pytest.mark.asyncio
    async def test_track_query_lifecycle_ai(self):
        """Test that Query Tracker uses AI for intelligent query lifecycle management."""
        # Query with complex history
        query_data = {
            "query_id": "Q-CARD-20240115-001",
            "subject_id": "SUBJ015",
            "created_date": "2024-01-15",
            "due_date": "2024-01-22",
            "current_date": "2024-02-01",  # Overdue by 10 days!
            "query_text": "Please clarify the discrepancy in systolic blood pressure readings",
            "severity": "major",
            "response_history": [
                {
                    "date": "2024-01-20",
                    "response": "Will check with source documents",
                    "status": "partial_response"
                },
                {
                    "date": "2024-01-25", 
                    "response": "Unable to locate source documents",
                    "status": "insufficient_response"
                }
            ],
            "site_performance": {
                "average_response_time": "8.5 days",
                "outstanding_queries": 15,
                "query_close_rate": 0.65
            }
        }
        
        tracker = QueryTracker()
        
        # Mock AI response with intelligent tracking
        mock_ai_response = Mock()
        mock_ai_response.messages = [Mock(content=json.dumps({
            "lifecycle_analysis": {
                "current_status": "escalation_required",
                "days_overdue": 10,
                "response_quality": "inadequate",
                "risk_assessment": "high",
                "escalation_reasons": [
                    "Query overdue by 10 days despite two response attempts",
                    "Site unable to provide source documentation for major finding",
                    "Pattern detected: Site has 15 outstanding queries (poor performance)"
                ],
                "recommended_actions": [
                    "Immediate escalation to Site Principal Investigator",
                    "Schedule monitoring visit within 2 weeks",
                    "Consider site retraining on source documentation requirements",
                    "Flag for potential FDA inspection risk"
                ],
                "predictive_analysis": {
                    "likelihood_of_resolution": 0.35,
                    "estimated_days_to_close": 21,
                    "risk_of_data_loss": 0.75
                },
                "similar_queries": [
                    "Q-CARD-20240110-003: Similar BP discrepancy, closed after PI intervention",
                    "Q-CARD-20240105-007: Source doc issue, required on-site visit"
                ]
            },
            "ai_insights": "Site showing systematic issues with source documentation. High risk of inspection findings.",
            "confidence": 0.88,
            "ai_powered": True
        }))]
        
        with patch('app.agents.query_tracker.Runner.run', new_callable=AsyncMock) as mock_run:
            mock_run.return_value = mock_ai_response
            
            # This method needs to be implemented
            result = await tracker.track_query_lifecycle_ai(query_data)
        
        # Verify AI was called
        assert mock_run.called
        
        # Verify AI provided lifecycle analysis
        assert result.get("ai_powered") == True
        assert result["lifecycle_analysis"]["current_status"] == "escalation_required"
        assert result["lifecycle_analysis"]["risk_assessment"] == "high"
        
        # Verify AI identified patterns
        assert len(result["lifecycle_analysis"]["escalation_reasons"]) > 0
        assert "pattern detected" in result["lifecycle_analysis"]["escalation_reasons"][2].lower()
        
        # Verify predictive capabilities
        assert "predictive_analysis" in result["lifecycle_analysis"]
        assert result["lifecycle_analysis"]["predictive_analysis"]["risk_of_data_loss"] > 0.7


class TestAnalyticsAgentAI:
    """Test AI implementation for Analytics Agent."""
    
    @pytest.mark.asyncio 
    async def test_generate_analytics_insights_ai(self):
        """Test that Analytics Agent uses AI for intelligent insights generation."""
        # Complex trial data for analysis
        trial_data = {
            "study_id": "CARD-2025-001",
            "enrollment": {
                "target": 300,
                "actual": 187,
                "rate_per_month": 12.5,
                "months_active": 15,
                "site_performance": {
                    "SITE01": {"enrolled": 67, "screen_fail_rate": 0.15},
                    "SITE02": {"enrolled": 45, "screen_fail_rate": 0.28}, 
                    "SITE03": {"enrolled": 38, "screen_fail_rate": 0.42},  # High screen fail!
                    "SITE04": {"enrolled": 37, "screen_fail_rate": 0.18}
                }
            },
            "data_quality": {
                "query_rate": 0.085,  # 8.5% of data points
                "critical_findings": 23,
                "protocol_deviations": 67,
                "missing_data_rate": 0.032
            },
            "safety": {
                "adverse_events": 145,
                "serious_adverse_events": 12,
                "deaths": 2,
                "discontinuations": 28
            },
            "timeline": {
                "start_date": "2023-10-01",
                "planned_end": "2025-09-30",
                "current_date": "2025-01-10"
            }
        }
        
        analytics = AnalyticsAgent()
        
        # Mock AI response with intelligent insights
        mock_ai_response = Mock()
        mock_ai_response.messages = [Mock(content=json.dumps({
            "analytics_insights": {
                "enrollment_analysis": {
                    "status": "at_risk",
                    "completion_probability": 0.42,
                    "key_findings": [
                        "Current enrollment rate (12.5/month) will only achieve 237 subjects by study end",
                        "Need to increase rate to 19.4/month to meet target",
                        "SITE03 has 42% screen failure rate - 2.8x higher than SITE01"
                    ],
                    "recommendations": [
                        "Investigate SITE03 screening criteria application",
                        "Consider adding 2 additional sites",
                        "Implement recruitment enhancement strategies"
                    ]
                },
                "quality_analysis": {
                    "overall_score": 0.72,
                    "concerns": [
                        "Query rate of 8.5% exceeds industry benchmark of 5%",
                        "23 critical findings indicate potential training gaps",
                        "67 protocol deviations (35.8% of subjects) is concerning"
                    ],
                    "risk_areas": [
                        "Data integrity issues may impact FDA submission",
                        "High deviation rate suggests protocol complexity issues"
                    ]
                },
                "safety_signals": {
                    "mortality_rate": 0.011,  # 1.1%
                    "sae_rate": 0.064,  # 6.4%
                    "discontinuation_rate": 0.15,  # 15%
                    "analysis": "Discontinuation rate 50% higher than expected - investigate tolerability"
                },
                "predictive_insights": {
                    "study_completion_date": "2026-01-15",  # 3.5 months delayed
                    "final_enrollment": 237,
                    "data_lock_readiness": 0.68,
                    "regulatory_submission_risk": "medium-high"
                }
            },
            "executive_summary": "Study at risk of missing enrollment target by 21%. Data quality issues and high discontinuation rate threaten study integrity. Immediate action required on SITE03 performance.",
            "ai_confidence": 0.91,
            "ai_powered": True
        }))]
        
        with patch('app.agents.analytics_agent.Runner.run', new_callable=AsyncMock) as mock_run:
            mock_run.return_value = mock_ai_response
            
            # This method needs to be implemented
            result = await analytics.generate_analytics_insights_ai(trial_data)
        
        # Verify AI was called
        assert mock_run.called
        
        # Verify AI provided comprehensive insights
        assert result.get("ai_powered") == True
        assert "analytics_insights" in result
        
        # Verify enrollment analysis
        enrollment = result["analytics_insights"]["enrollment_analysis"]
        assert enrollment["status"] == "at_risk"
        assert enrollment["completion_probability"] < 0.5
        
        # Verify quality analysis
        quality = result["analytics_insights"]["quality_analysis"]
        assert quality["overall_score"] < 0.75
        assert len(quality["concerns"]) > 0
        
        # Verify predictive capabilities
        assert "predictive_insights" in result["analytics_insights"]
        assert result["analytics_insights"]["predictive_insights"]["regulatory_submission_risk"] == "medium-high"
        
        # Verify executive summary
        assert "executive_summary" in result
        assert "21%" in result["executive_summary"]  # Specific metric mentioned


if __name__ == "__main__":
    pytest.main([__file__, "-v"])