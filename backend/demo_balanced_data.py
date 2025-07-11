#!/usr/bin/env python3
"""
Demo script showing balanced test data generation for clinical trials.

This script demonstrates the comprehensive test data that supports:
1. Realistic demo scenarios (clean vs problematic subjects)
2. Supervised learning with ground truth labels
3. Protocol compliance testing
4. Agent evaluation across different complexity levels
"""

from tests.test_data.synthetic_data_generator import generate_test_study
import json


def analyze_study_balance():
    """Generate and analyze balanced test data distribution."""
    print("🏥 GENERATING BALANCED CLINICAL TRIAL DATA...")
    study = generate_test_study('cardiology_phase2')
    
    # Categorize subjects by data quality
    clean_subjects = []
    discrepancy_only = []
    protocol_only = []
    complex_subjects = []
    
    for subject in study['subjects']:
        metadata = subject.get('_generation_metadata', {})
        subject_id = subject['subject_id']
        
        # Count actual issues
        discrepancy_count = sum(len(visit['discrepancies']) for visit in subject['visits'])
        protocol_deviation_count = sum(len(visit.get('protocol_deviations', [])) for visit in subject['visits'])
        
        # Categorize for demo purposes
        if discrepancy_count == 0 and protocol_deviation_count == 0:
            clean_subjects.append(subject_id)
        elif discrepancy_count > 0 and protocol_deviation_count == 0:
            discrepancy_only.append((subject_id, discrepancy_count))
        elif discrepancy_count == 0 and protocol_deviation_count > 0:
            protocol_only.append((subject_id, protocol_deviation_count))
        else:
            complex_subjects.append((subject_id, discrepancy_count, protocol_deviation_count))
    
    print(f"\n📊 BALANCED DATA DISTRIBUTION")
    print(f"{'='*50}")
    print(f"Total Subjects: {len(study['subjects'])}")
    print(f"Clean Subjects: {len(clean_subjects)} ({len(clean_subjects)/len(study['subjects'])*100:.1f}%)")
    print(f"Discrepancy-Only: {len(discrepancy_only)} ({len(discrepancy_only)/len(study['subjects'])*100:.1f}%)")
    print(f"Protocol-Only: {len(protocol_only)} ({len(protocol_only)/len(study['subjects'])*100:.1f}%)")
    print(f"Complex Subjects: {len(complex_subjects)} ({len(complex_subjects)/len(study['subjects'])*100:.1f}%)")
    
    print(f"\n🎭 DEMO SUBJECTS BY SCENARIO")
    print(f"{'='*50}")
    print(f"✅ Clean Subjects (Perfect for 'No Issues' demos):")
    print(f"   {', '.join(clean_subjects[:8])}")
    
    print(f"\n⚠️  Low-Problem Subjects (1-10 discrepancies):")
    for subj_id, count in discrepancy_only[:5]:
        print(f"   {subj_id}: {count} discrepancies")
    
    print(f"\n🚨 High-Problem Subjects (Complex cases):")
    for subj_id, disc_count, prot_count in complex_subjects[:5]:
        print(f"   {subj_id}: {disc_count} discrepancies, {prot_count} protocol deviations")
    
    return study, clean_subjects, discrepancy_only, complex_subjects


def demonstrate_ground_truth_labels(study):
    """Show how metadata supports supervised learning."""
    print(f"\n🤖 SUPERVISED LEARNING SUPPORT")
    print(f"{'='*50}")
    
    sample_subjects = study['subjects'][:3]
    for subject in sample_subjects:
        metadata = subject['_generation_metadata']
        actual_discrepancies = sum(len(visit['discrepancies']) for visit in subject['visits'])
        
        print(f"\n📋 Subject: {subject['subject_id']}")
        print(f"   Quality Profile: {metadata['quality_profile']}")
        print(f"   Ground Truth - Has Discrepancies: {metadata['has_discrepancies']}")
        print(f"   Ground Truth - Has Protocol Deviations: {metadata['has_protocol_deviations']}")
        print(f"   Actual Discrepancies Found: {actual_discrepancies}")
        print(f"   Is Ground Truth Dataset: {metadata['is_ground_truth']}")


def show_demo_workflows():
    """Display agent-specific demo scenarios."""
    print(f"\n🔧 AGENT-SPECIFIC DEMO WORKFLOWS")
    print(f"{'='*50}")
    
    workflows = {
        "Data Verifier Agent": {
            "Clean Demo": "Use CARD001, CARD002 → 'No discrepancies found'",
            "Issues Demo": "Use CARD008, CARD014 → Shows 8-9 specific discrepancies",
            "Complex Demo": "Use CARD003, CARD006 → Shows 15-17 discrepancies"
        },
        "Deviation Detector Agent": {
            "Compliant Demo": "Use CARD001, CARD010 → 'No protocol deviations detected'",
            "Minor Violations": "Use subjects with single parameter deviations",
            "Major Violations": "Use subjects with age or multiple parameter violations"
        },
        "Query Generator Agent": {
            "No Queries Demo": "Use clean subjects → 'No queries required'",
            "Standard Queries": "Use discrepancy-only subjects → Generate 1-10 queries",
            "Complex Queries": "Use complex subjects → Generate queries for both discrepancies and deviations"
        },
        "Portfolio Manager Agent": {
            "Low Risk": "Use clean subjects → Minimal oversight needed",
            "Medium Risk": "Use discrepancy-only subjects → Focus on data quality",
            "High Risk": "Use complex subjects → Comprehensive monitoring required"
        }
    }
    
    for agent, scenarios in workflows.items():
        print(f"\n🤖 {agent}")
        for scenario, description in scenarios.items():
            print(f"   • {scenario}: {description}")


def show_protocol_compliance_examples(study):
    """Demonstrate protocol compliance testing capabilities."""
    print(f"\n⚖️ PROTOCOL COMPLIANCE EXAMPLES")
    print(f"{'='*50}")
    
    # Find subjects with different types of issues
    age_violations = []
    bp_violations = []
    lab_violations = []
    
    for subject in study['subjects']:
        # Check demographics for age violations
        age = subject['demographics']['age']
        if age < 18 or age > 80:
            age_violations.append((subject['subject_id'], age))
        
        # Check visits for BP and lab violations
        for visit in subject['visits']:
            edc_data = visit['edc_data']
            
            # Check BP violations
            if 'vital_signs' in edc_data:
                systolic_bp = edc_data['vital_signs'].get('systolic_bp', 0)
                if systolic_bp > 180:
                    bp_violations.append((subject['subject_id'], visit['visit_name'], systolic_bp))
            
            # Check lab violations
            if 'laboratory' in edc_data:
                creatinine = edc_data['laboratory'].get('creatinine', 0)
                if creatinine > 2.5:
                    lab_violations.append((subject['subject_id'], visit['visit_name'], creatinine))
    
    print(f"📅 Age Violations (outside 18-80 range):")
    for subj_id, age in age_violations[:3]:
        print(f"   {subj_id}: Age {age} years")
    
    print(f"\n🩸 Blood Pressure Violations (>180 mmHg systolic):")
    for subj_id, visit, bp in bp_violations[:3]:
        print(f"   {subj_id} - {visit}: {bp} mmHg")
    
    print(f"\n🧪 Laboratory Violations (creatinine >2.5 mg/dL):")
    for subj_id, visit, creat in lab_violations[:3]:
        print(f"   {subj_id} - {visit}: {creat} mg/dL")


if __name__ == "__main__":
    print("🏥 CLINICAL TRIALS AI AGENT - BALANCED TEST DATA DEMO")
    print("="*60)
    
    # Generate and analyze balanced data
    study, clean_subjects, discrepancy_only, complex_subjects = analyze_study_balance()
    
    # Show supervised learning capabilities
    demonstrate_ground_truth_labels(study)
    
    # Display agent-specific workflows
    show_demo_workflows()
    
    # Show protocol compliance examples
    show_protocol_compliance_examples(study)
    
    print(f"\n✅ DEMO COMPLETE")
    print(f"{'='*60}")
    print(f"📖 See TEST_DATA_DOCUMENTATION.md for complete specifications")
    print(f"🎯 Ready for comprehensive demos and agent evaluation!")