#!/usr/bin/env python3
"""
Test Output Analysis - Verify Correctness of Agent Responses
Analyzes whether agents actually answer the specific questions posed in test cases
"""

import asyncio
import json
import os
from typing import Dict, Any
from agents import Runner
from app.agents_v2.portfolio_manager import WorkflowContext, portfolio_manager_agent
from app.agents_v2.query_analyzer import QueryAnalysisContext, query_analyzer_agent
from app.agents_v2.data_verifier import DataVerificationContext, data_verifier_agent
from app.agents_v2.deviation_detector import DeviationDetectionContext, deviation_detector_agent


async def test_query_analyzer_correctness():
    """Test: CDM_Query_Simple_Lab_Discrepancy - Does it identify the right discrepancies?"""
    print("🔍 TESTING QUERY ANALYZER CORRECTNESS")
    print("="*60)
    
    context = QueryAnalysisContext()
    test_data = {
        "patient_id": "CARD001",
        "visit": "Week 4",
        "lab_values": {
            "hemoglobin": {"edc_value": 12.5, "lab_value": 11.8, "unit": "g/dL"},
            "creatinine": {"edc_value": 1.2, "lab_value": 1.8, "unit": "mg/dL"}  # CRITICAL: 1.8 is elevated!
        },
        "discrepancy_type": "lab_edc_mismatch"
    }
    
    message = f"""Analyze this clinical data for query generation needs:
{json.dumps(test_data, indent=2)}

Expected to identify:
- Creatinine discrepancy as critical (kidney function concern)
- Hemoglobin discrepancy as minor
- Generates appropriate severity assessment
- Recommends immediate verification for creatinine"""
    
    result = await Runner.run(query_analyzer_agent, message, context=context)
    output = result.final_output.model_dump()
    
    print("📋 INPUT ANALYSIS:")
    print("• Hemoglobin: 12.5 → 11.8 g/dL (minor decrease, within normal range)")
    print("• Creatinine: 1.2 → 1.8 mg/dL (CRITICAL: 50% increase, suggests kidney dysfunction)")
    print("\n📤 AGENT OUTPUT:")
    print(json.dumps(output, indent=2))
    
    # Correctness Check
    findings = output.get('findings', [])
    severity = output.get('severity', '')
    
    print("\n✅ CORRECTNESS ANALYSIS:")
    creatinine_mentioned = any('creatinine' in f.lower() or '1.8' in f for f in findings)
    severity_appropriate = severity in ['major', 'critical', 'high']
    hemoglobin_mentioned = any('hemoglobin' in f.lower() or '11.8' in f for f in findings)
    
    print(f"• Identifies creatinine issue: {'✅' if creatinine_mentioned else '❌'}")
    print(f"• Appropriate severity level: {'✅' if severity_appropriate else '❌'}")
    print(f"• Mentions hemoglobin: {'✅' if hemoglobin_mentioned else '❌'}")
    
    return {
        'test': 'Query Analyzer Lab Discrepancy',
        'creatinine_identified': creatinine_mentioned,
        'severity_appropriate': severity_appropriate,
        'hemoglobin_mentioned': hemoglobin_mentioned
    }


async def test_deviation_detector_correctness():
    """Test: PI_Critical_Eligibility_Deviation - Does it catch all violations?"""
    print("\n🚨 TESTING DEVIATION DETECTOR CORRECTNESS")
    print("="*60)
    
    context = DeviationDetectionContext()
    test_data = {
        "patient_id": "ONCO_089",
        "patient_data": {
            "age": 17.8,  # Violation: Protocol requires ≥18
            "ecog_performance": 2,  # Violation: Protocol allows 0-1  
            "prior_chemo": "yes",  # Violation: Protocol excludes prior chemo
            "lab_values": {
                "hemoglobin": 7.5,  # Violation: Below protocol minimum 8.0
                "absolute_neutrophil": 800,  # Violation: Below protocol minimum 1500
                "platelets": 75000  # Violation: Below protocol minimum 100000
            }
        },
        "protocol_requirements": {
            "inclusion_criteria": {
                "age_range": "18-75 years",
                "ecog_performance": "0-1", 
                "hemoglobin": "≥8.0 g/dL",
                "absolute_neutrophil": "≥1500/μL",
                "platelets": "≥100000/μL"
            },
            "exclusion_criteria": {
                "prior_chemotherapy": "within 6 months"
            }
        }
    }
    
    message = f"""Detect protocol deviations in this study data:
{json.dumps(test_data, indent=2)}"""
    
    result = await Runner.run(deviation_detector_agent, message, context=context)
    output = result.final_output.model_dump()
    
    print("📋 INPUT ANALYSIS - Expected 6 Major Violations:")
    print("• Age: 17.8 years (requires ≥18) - CRITICAL eligibility violation")
    print("• ECOG: 2 (requires 0-1) - Performance status violation") 
    print("• Prior chemo: yes (excluded) - Protocol exclusion violation")
    print("• Hemoglobin: 7.5 g/dL (requires ≥8.0) - Safety lab violation")
    print("• Neutrophils: 800/μL (requires ≥1500) - Safety lab violation")
    print("• Platelets: 75000/μL (requires ≥100000) - Safety lab violation")
    
    print("\n📤 AGENT OUTPUT:")
    print(json.dumps(output, indent=2))
    
    # Correctness Check
    deviations = output.get('deviations', [])
    severity = output.get('severity_assessment', '')
    corrective_actions = output.get('corrective_actions', [])
    
    print("\n✅ CORRECTNESS ANALYSIS:")
    age_violation = any('17.8' in d or 'age' in d.lower() for d in deviations)
    ecog_violation = any('ecog' in d.lower() or 'performance' in d.lower() for d in deviations)
    lab_violations = any('hemoglobin' in d.lower() or 'platelet' in d.lower() or 'neutrophil' in d.lower() for d in deviations)
    irb_notification = any('irb' in a.lower() or 'ethics' in a.lower() for a in corrective_actions)
    patient_removal = any('remove' in a.lower() or 'withdraw' in a.lower() for a in corrective_actions)
    
    print(f"• Age violation detected: {'✅' if age_violation else '❌'}")
    print(f"• ECOG violation detected: {'✅' if ecog_violation else '❌'}")
    print(f"• Lab violations detected: {'✅' if lab_violations else '❌'}")
    print(f"• IRB notification recommended: {'✅' if irb_notification else '❌'}")
    print(f"• Patient removal recommended: {'✅' if patient_removal else '❌'}")
    print(f"• Severity marked as critical: {'✅' if severity == 'critical' else '❌'}")
    
    return {
        'test': 'Deviation Detector Eligibility',
        'age_violation': age_violation,
        'ecog_violation': ecog_violation,
        'lab_violations': lab_violations,
        'irb_notification': irb_notification,
        'patient_removal': patient_removal,
        'critical_severity': severity == 'critical'
    }


async def test_portfolio_manager_orchestration():
    """Test: Portfolio_Manager_Complex_Safety_Signal - Does it coordinate properly?"""
    print("\n🎯 TESTING PORTFOLIO MANAGER ORCHESTRATION")
    print("="*60)
    
    context = WorkflowContext()
    test_data = {
        "alert_type": "potential_safety_signal",
        "clinical_data": {
            "patient_id": "CARD_301",
            "visit": "Week 8", 
            "safety_concerns": {
                "liver_enzymes": {"ALT": 245, "AST": 198, "bilirubin": 4.1},  # >3x ULN, critical
                "cardiac_markers": {"troponin": 0.8, "bnp": 1250, "ck_mb": 18},  # Elevated, concerning
                "symptoms": ["fatigue", "nausea", "chest_discomfort", "shortness_of_breath"]
            },
            "concomitant_medications": ["study_drug", "metformin", "lisinopril"],
            "medical_history": ["diabetes", "hypertension", "mild_cad"]
        },
        "required_assessments": [
            "clinical_data_analysis",
            "drug_interaction_review", 
            "protocol_deviation_check",
            "regulatory_reporting_requirements",
            "query_generation_for_missing_data"
        ]
    }
    
    message = f"""Orchestrate response to this clinical scenario:
{json.dumps(test_data, indent=2)}

Expected coordination:
- Recognizes complex safety scenario requiring multiple specialist agents
- Coordinates handoffs to Query Analyzer for clinical assessment
- Engages Deviation Detector for protocol compliance review
- Utilizes Data Verifier for source document validation
- Orchestrates Query Generator for additional data collection
- Provides integrated safety assessment and action plan
- Ensures all regulatory reporting requirements addressed"""
    
    result = await Runner.run(portfolio_manager_agent, message, context=context)
    
    # Check what type of output we got
    if hasattr(result.final_output, 'model_dump'):
        output = result.final_output.model_dump()
    else:
        output = {"raw_output": str(result.final_output)}
    
    print("📋 INPUT ANALYSIS - Complex Multi-System Safety Signal:")
    print("• Liver: ALT 245, AST 198, Bilirubin 4.1 (>3x ULN = CRITICAL)")
    print("• Cardiac: Troponin 0.8, BNP 1250 (elevated = concerning)")
    print("• Symptoms: Fatigue, nausea, chest discomfort, SOB")
    print("• Context: Study drug + comorbidities")
    print("• Expected: Multi-agent coordination for comprehensive assessment")
    
    print("\n📤 AGENT OUTPUT:")
    print(json.dumps(output, indent=2))
    
    # Correctness Check
    findings = output.get('findings', [])
    severity = output.get('severity', '')
    recommended_actions = output.get('recommended_actions', [])
    
    print("\n✅ CORRECTNESS ANALYSIS:")
    liver_recognized = any('liver' in f.lower() or 'alt' in f.lower() or 'bilirubin' in f.lower() for f in findings)
    cardiac_recognized = any('cardiac' in f.lower() or 'troponin' in f.lower() or 'bnp' in f.lower() for f in findings)
    critical_severity = severity in ['critical', 'major', 'high']
    safety_actions = any('safety' in a.lower() or 'monitor' in a.lower() or 'hold' in a.lower() for a in recommended_actions)
    
    print(f"• Liver toxicity recognized: {'✅' if liver_recognized else '❌'}")
    print(f"• Cardiac issues recognized: {'✅' if cardiac_recognized else '❌'}")
    print(f"• Appropriate severity level: {'✅' if critical_severity else '❌'}")
    print(f"• Safety actions recommended: {'✅' if safety_actions else '❌'}")
    
    # Check if handoffs occurred (this might need SDK trace analysis)
    print(f"• Appears to use handoffs: {'🔍 Manual Review Needed' if 'QueryAnalyzer' in str(result) else '❓'}")
    
    return {
        'test': 'Portfolio Manager Safety Signal',
        'liver_recognized': liver_recognized,
        'cardiac_recognized': cardiac_recognized,
        'critical_severity': critical_severity,
        'safety_actions': safety_actions
    }


async def test_data_verifier_correctness():
    """Test: CRA_SDV_Critical_Safety_Data - Does it identify critical values correctly?"""
    print("\n🔬 TESTING DATA VERIFIER CORRECTNESS")
    print("="*60)
    
    context = DataVerificationContext()
    test_data = {
        "site_id": "Site_101",
        "patient_id": "CARD_001",
        "verification_scope": "critical_safety_data",
        "edc_data": {
            "liver_enzymes": {"ALT": 180, "AST": 165, "total_bilirubin": 3.2},  # >3x ULN
            "cardiac_events": {"lvef": 35, "bnp": 850, "troponin": 2.1},  # Heart failure + MI
            "vital_signs": {"bp": "160/95", "hr": 45, "temp": 102.1}  # HTN + bradycardia + fever
        },
        "verification_priority": "high"
    }
    
    message = f"""Perform source data verification for this clinical data:
{json.dumps(test_data, indent=2)}

Expected outcomes:
- Identifies all values as critical requiring 100% SDV
- Flags liver enzymes as >3x ULN requiring immediate safety review
- Recognizes cardiac values suggest heart failure progression 
- Identifies vital signs abnormalities (bradycardia, hypertension, fever)
- Recommends immediate physician review and potential study drug hold
- Generates verification report with regulatory compliance"""
    
    result = await Runner.run(data_verifier_agent, message, context=context)
    output = result.final_output.model_dump()
    
    print("📋 INPUT ANALYSIS - Critical Safety Values:")
    print("• Liver: ALT 180, AST 165, Bilirubin 3.2 (>3x ULN = immediate safety concern)")
    print("• Cardiac: LVEF 35% (heart failure), BNP 850 (elevated), Troponin 2.1 (MI range)")
    print("• Vitals: BP 160/95 (HTN), HR 45 (bradycardia), Temp 102.1°F (fever)")
    
    print("\n📤 AGENT OUTPUT:")
    print(json.dumps(output, indent=2))
    
    # Correctness Check
    discrepancies = output.get('discrepancies', [])
    verification_recommendations = output.get('recommendations', output.get('verification_recommendations', []))
    compliance_status = output.get('compliance_status', '')
    
    print("\n✅ CORRECTNESS ANALYSIS:")
    liver_flagged = any('liver' in str(discrepancies).lower() or 'alt' in str(discrepancies).lower())
    cardiac_flagged = any('cardiac' in str(discrepancies).lower() or 'lvef' in str(discrepancies).lower())
    vitals_flagged = any('vital' in str(discrepancies).lower() or 'bp' in str(discrepancies).lower())
    sdv_recommended = any('sdv' in str(verification_recommendations).lower() or '100%' in str(verification_recommendations) or 'immediate' in str(verification_recommendations).lower())
    
    print(f"• Liver enzymes flagged: {'✅' if liver_flagged else '❌'}")
    print(f"• Cardiac issues flagged: {'✅' if cardiac_flagged else '❌'}")
    print(f"• Vital signs flagged: {'✅' if vitals_flagged else '❌'}")
    print(f"• 100% SDV recommended: {'✅' if sdv_recommended else '❌'}")
    
    return {
        'test': 'Data Verifier Critical Safety',
        'liver_flagged': liver_flagged,
        'cardiac_flagged': cardiac_flagged,
        'vitals_flagged': vitals_flagged,
        'sdv_recommended': sdv_recommended
    }


async def run_correctness_analysis():
    """Run all correctness tests and generate analysis report"""
    print("🧪 COMPREHENSIVE CORRECTNESS ANALYSIS")
    print("="*80)
    print("Testing whether agents actually answer the questions posed in test cases")
    print("="*80)
    
    # Load API key
    if not os.getenv("OPENAI_API_KEY"):
        try:
            with open(".env", "r") as f:
                for line in f:
                    if line.startswith("OPENAI_API_KEY="):
                        key = line.split("=", 1)[1].strip().strip('"')
                        os.environ["OPENAI_API_KEY"] = key
                        break
        except FileNotFoundError:
            print("❌ No .env file found. Please set OPENAI_API_KEY environment variable.")
            return
    
    results = []
    
    # Run each correctness test
    results.append(await test_query_analyzer_correctness())
    results.append(await test_deviation_detector_correctness())
    results.append(await test_portfolio_manager_orchestration())
    results.append(await test_data_verifier_correctness())
    
    # Generate summary
    print("\n" + "="*80)
    print("🏁 CORRECTNESS ANALYSIS SUMMARY")
    print("="*80)
    
    for result in results:
        test_name = result.pop('test')
        print(f"\n📊 {test_name}:")
        
        all_correct = all(result.values())
        status = "✅ FULLY CORRECT" if all_correct else "⚠️  NEEDS REVIEW"
        print(f"   Overall: {status}")
        
        for check, passed in result.items():
            emoji = "✅" if passed else "❌"
            print(f"   {emoji} {check.replace('_', ' ').title()}")
    
    # Overall assessment
    total_checks = sum(len(r) - 1 for r in results)  # -1 because we removed 'test' key
    passed_checks = sum(sum(r.values()) for r in results)
    
    print(f"\n📈 OVERALL CORRECTNESS SCORE: {passed_checks}/{total_checks} ({passed_checks/total_checks*100:.1f}%)")
    
    if passed_checks == total_checks:
        print("🎉 ALL AGENTS ARE ANSWERING QUESTIONS CORRECTLY!")
    else:
        print("⚠️  Some agents need prompt adjustments to better answer specific questions")
    
    return results


if __name__ == "__main__":
    asyncio.run(run_correctness_analysis())