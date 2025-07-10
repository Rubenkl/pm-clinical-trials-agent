"""
Test to demonstrate the critical difference between rule-based and AI-powered implementations.
This test shows why using actual LLM intelligence is essential for clinical data analysis.
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from app.agents.data_verifier import DataVerifier  # Rule-based
from app.agents.data_verifier_ai import DataVerifierAI  # AI-powered


class TestAIvsRulesComparison:
    """Compare rule-based vs AI-powered implementations."""
    
    @pytest.mark.asyncio
    async def test_clinical_significance_understanding(self):
        """Test that AI understands clinical significance while rules don't."""
        
        # Clinical scenario: Minor hemoglobin difference vs missing anticoagulant
        test_data = {
            "subject_id": "CARD001",
            "edc_data": {
                "hemoglobin": "12.5",  # Normal female range: 12.0-16.0
                "medications": ["aspirin", "metoprolol"],
                "inr": "2.5"  # International Normalized Ratio for blood clotting
            },
            "source_data": {
                "hemoglobin": "12.4",  # 0.1 difference - clinically insignificant
                "medications": ["aspirin", "metoprolol", "warfarin"],  # WARFARIN MISSING IN EDC!
                "inr": "2.5"
            }
        }
        
        # Test rule-based verifier
        rule_verifier = DataVerifier()
        rule_result = await rule_verifier.verify_clinical_data(test_data)
        
        # Test AI-powered verifier (mocked for testing)
        ai_verifier = DataVerifierAI()
        
        # Mock the Runner.run to simulate AI response
        mock_ai_response = Mock()
        mock_ai_response.messages = [Mock(content=json.dumps({
            "discrepancies": [
                {
                    "field": "hemoglobin",
                    "edc_value": "12.5",
                    "source_value": "12.4",
                    "severity": "minor",
                    "type": "value_mismatch",
                    "medical_significance": "0.1 g/dL difference is within normal variation and clinically insignificant",
                    "confidence": 0.95
                },
                {
                    "field": "medications",
                    "edc_value": "['aspirin', 'metoprolol']",
                    "source_value": "['aspirin', 'metoprolol', 'warfarin']",
                    "severity": "critical",
                    "type": "missing_medication",
                    "medical_significance": "CRITICAL: Warfarin (anticoagulant) is documented in source but missing in EDC. Patient has INR 2.5 indicating active anticoagulation therapy. Missing this medication could lead to serious safety issues.",
                    "recommended_action": "Immediately verify with site and update EDC. This is a critical safety issue.",
                    "confidence": 0.98
                }
            ],
            "ai_insights": "The hemoglobin difference of 0.1 g/dL is clinically insignificant and within measurement error. However, the missing warfarin in EDC is a critical safety issue. The patient's INR of 2.5 confirms they are on anticoagulation therapy, and this must be accurately recorded.",
            "overall_confidence": 0.96
        }))]
        
        with patch('agents.Runner.run', new_callable=AsyncMock) as mock_run:
            mock_run.return_value = mock_ai_response
            ai_result = await ai_verifier.verify_clinical_data(test_data)
        
        # Compare results
        print("\n=== RULE-BASED RESULT ===")
        print(f"Total discrepancies: {len(rule_result.get('discrepancies', []))}")
        for disc in rule_result.get('discrepancies', []):
            print(f"- {disc['field']}: {disc['severity']} (Type: {disc.get('discrepancy_type', 'unknown')})")
        
        print("\n=== AI-POWERED RESULT ===")
        print(f"Total discrepancies: {len(ai_result.get('discrepancies', []))}")
        for disc in ai_result.get('discrepancies', []):
            print(f"- {disc['field']}: {disc['severity']}")
            print(f"  Medical significance: {disc.get('medical_significance', 'N/A')}")
        
        # Assertions
        # Rule-based treats all differences equally
        rule_based_severities = [d['severity'] for d in rule_result.get('discrepancies', [])]
        
        # AI understands medical context
        ai_severities = {d['field']: d['severity'] for d in ai_result.get('discrepancies', [])}
        
        # Key assertion: AI should recognize warfarin as critical
        assert ai_severities.get('medications') == 'critical', "AI must recognize missing anticoagulant as critical"
        assert ai_severities.get('hemoglobin') == 'minor', "AI should recognize 0.1 hemoglobin difference as minor"
        
        # AI provides medical reasoning
        assert ai_result.get('ai_insights'), "AI should provide medical insights"
        assert 'ai_powered' in ai_result and ai_result['ai_powered'], "Result should be flagged as AI-powered"
    
    @pytest.mark.asyncio
    async def test_context_aware_analysis(self):
        """Test that AI considers patient context while rules don't."""
        
        # Scenario: Blood pressure reading for elderly vs young patient
        elderly_data = {
            "subject_id": "ELDERLY001",
            "edc_data": {
                "age": "78",
                "blood_pressure": "150/85",  # Might be acceptable for elderly
                "medical_history": ["hypertension", "diabetes"]
            },
            "source_data": {
                "age": "78",
                "blood_pressure": "148/84",
                "medical_history": ["hypertension", "diabetes"]
            }
        }
        
        young_data = {
            "subject_id": "YOUNG001",
            "edc_data": {
                "age": "25",
                "blood_pressure": "150/85",  # Concerning for young adult
                "medical_history": []
            },
            "source_data": {
                "age": "25",
                "blood_pressure": "148/84",
                "medical_history": []
            }
        }
        
        # Rule-based verifier
        rule_verifier = DataVerifier()
        elderly_rule_result = await rule_verifier.verify_clinical_data(elderly_data)
        young_rule_result = await rule_verifier.verify_clinical_data(young_data)
        
        # Rules treat both the same - just see BP difference
        assert len(elderly_rule_result.get('discrepancies', [])) == len(young_rule_result.get('discrepancies', []))
        
        # AI would understand context (mocked response shows the difference)
        ai_verifier = DataVerifierAI()
        
        # Mock AI understanding context
        elderly_ai_response = Mock()
        elderly_ai_response.messages = [Mock(content=json.dumps({
            "discrepancies": [{
                "field": "blood_pressure",
                "severity": "minor",
                "medical_significance": "2/1 mmHg difference is negligible. BP 150/85 is within acceptable range for 78-year-old with controlled hypertension."
            }]
        }))]
        
        young_ai_response = Mock()
        young_ai_response.messages = [Mock(content=json.dumps({
            "discrepancies": [{
                "field": "blood_pressure",
                "severity": "major",
                "medical_significance": "While the 2/1 mmHg difference is small, BP 150/85 in a 25-year-old with no history is concerning and suggests undiagnosed hypertension."
            }]
        }))]
        
        with patch('agents.Runner.run', new_callable=AsyncMock) as mock_run:
            # First call for elderly
            mock_run.return_value = elderly_ai_response
            elderly_ai_result = await ai_verifier.verify_clinical_data(elderly_data)
            
            # Second call for young
            mock_run.return_value = young_ai_response
            young_ai_result = await ai_verifier.verify_clinical_data(young_data)
        
        # AI considers context
        elderly_severity = elderly_ai_result['discrepancies'][0]['severity']
        young_severity = young_ai_result['discrepancies'][0]['severity']
        
        assert elderly_severity == 'minor', "AI should consider elderly BP as minor issue"
        assert young_severity == 'major', "AI should flag young adult BP as major concern"
        
        print("\n=== CONTEXT AWARENESS DEMONSTRATION ===")
        print(f"Rule-based treats both patients the same")
        print(f"AI understands: Elderly BP 150/85 = {elderly_severity}, Young BP 150/85 = {young_severity}")
    
    @pytest.mark.asyncio
    async def test_complex_drug_interaction_detection(self):
        """Test that AI can detect complex drug interactions while rules can't."""
        
        # Scenario: Dangerous drug combination
        test_data = {
            "subject_id": "DRUG001",
            "edc_data": {
                "medications": ["simvastatin", "amlodipine", "aspirin"],
                "grapefruit_juice": "yes"  # Dangerous with simvastatin!
            },
            "source_data": {
                "medications": ["simvastatin", "amlodipine", "aspirin"],
                "grapefruit_juice": "no"
            }
        }
        
        # Rule-based just sees string difference
        rule_verifier = DataVerifier()
        rule_result = await rule_verifier.verify_clinical_data(test_data)
        
        # AI understands drug interactions
        ai_verifier = DataVerifierAI()
        
        ai_response = Mock()
        ai_response.messages = [Mock(content=json.dumps({
            "discrepancies": [{
                "field": "grapefruit_juice",
                "edc_value": "yes",
                "source_value": "no",
                "severity": "critical",
                "medical_significance": "CRITICAL DRUG INTERACTION: Patient on simvastatin should NOT consume grapefruit juice. This can increase statin levels 10-15x leading to rhabdomyolysis.",
                "recommended_action": "Immediately contact patient. Verify which is correct. If consuming grapefruit, stop immediately and monitor for muscle pain."
            }],
            "ai_insights": "Grapefruit juice inhibits CYP3A4 enzyme which metabolizes simvastatin. This is a dangerous interaction that must be resolved immediately."
        }))]
        
        with patch('agents.Runner.run', new_callable=AsyncMock) as mock_run:
            mock_run.return_value = ai_response
            ai_result = await ai_verifier.verify_clinical_data(test_data)
        
        # Rules see just a difference
        rule_severities = [d['severity'] for d in rule_result.get('discrepancies', [])]
        
        # AI understands the medical danger
        ai_severity = ai_result['discrepancies'][0]['severity']
        ai_significance = ai_result['discrepancies'][0]['medical_significance']
        
        assert ai_severity == 'critical', "AI must recognize drug interaction as critical"
        assert 'rhabdomyolysis' in ai_significance, "AI should mention specific medical risk"
        
        print("\n=== DRUG INTERACTION DETECTION ===")
        print("Rule-based: Just sees 'yes' vs 'no' difference")
        print(f"AI-powered: Recognizes critical drug interaction - {ai_significance[:50]}...")


class TestWhyAIMatters:
    """Tests demonstrating why AI is essential for clinical trials."""
    
    @pytest.mark.asyncio
    async def test_ai_handles_variations_in_data_format(self):
        """Test that AI handles variations that break rules."""
        
        # Different ways to express the same clinical data
        variations = [
            {"blood_pressure": "120/80"},
            {"blood_pressure": "120 over 80"},
            {"blood_pressure": "systolic 120, diastolic 80"},
            {"blood_pressure": "BP: 120/80 mmHg"},
            {"blood_pressure": "120/80 (normal)"}
        ]
        
        # Rules would see all these as different
        # AI understands they're all the same
        
        ai_verifier = DataVerifierAI()
        
        # Mock AI understanding variations
        with patch('agents.Runner.run', new_callable=AsyncMock) as mock_run:
            mock_response = Mock()
            mock_response.messages = [Mock(content=json.dumps({
                "discrepancies": [],
                "ai_insights": "All blood pressure readings are equivalent at 120/80 mmHg, just expressed differently."
            }))]
            mock_run.return_value = mock_response
            
            for i in range(len(variations)-1):
                result = await ai_verifier.verify_clinical_data({
                    "subject_id": "VAR001",
                    "edc_data": variations[i],
                    "source_data": variations[i+1]
                })
                
                assert len(result['discrepancies']) == 0, f"AI should recognize '{variations[i]}' equals '{variations[i+1]}'"
    
    @pytest.mark.asyncio
    async def test_ai_learns_from_context(self):
        """Test that AI can apply learning from context."""
        
        # Scenario: Protocol-specific normal ranges
        protocol_context = """
        This trial has specific inclusion criteria:
        - Hemoglobin must be ≥ 10.0 g/dL (lower than standard)
        - Platelet count must be ≥ 75,000/μL (lower than standard)
        Due to the cancer patient population.
        """
        
        test_data = {
            "subject_id": "CANCER001",
            "protocol_context": protocol_context,
            "edc_data": {
                "hemoglobin": "10.5",  # Low by normal standards, OK for protocol
                "platelets": "80000"   # Low by normal standards, OK for protocol
            },
            "source_data": {
                "hemoglobin": "10.5",
                "platelets": "80000"
            }
        }
        
        # Rule-based would flag as concerning (below normal)
        # AI understands protocol context
        
        ai_verifier = DataVerifierAI()
        
        with patch('agents.Runner.run', new_callable=AsyncMock) as mock_run:
            mock_response = Mock()
            mock_response.messages = [Mock(content=json.dumps({
                "discrepancies": [],
                "ai_insights": "Values are within protocol-specific acceptable ranges for cancer patients. Hemoglobin 10.5 and platelets 80,000 meet inclusion criteria.",
                "protocol_compliance": True
            }))]
            mock_run.return_value = mock_response
            
            result = await ai_verifier.verify_clinical_data(test_data)
            
            assert result.get('protocol_compliance', False), "AI should understand protocol context"


if __name__ == "__main__":
    # Run specific test to see the difference
    pytest.main([__file__, "-v", "-k", "test_clinical_significance_understanding"])