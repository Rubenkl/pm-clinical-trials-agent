"""Test data function tools for clinical trial development.

These function tools provide access to test data for development and testing purposes.
They retrieve realistic clinical data from the TestDataService to support frontend
development and agent testing without making expensive API calls.
"""

import asyncio
import concurrent.futures
import json

from agents import function_tool


@function_tool
def get_test_subject_data(subject_id: str) -> str:
    """Retrieve comprehensive clinical trial data for a specific test subject.

    This function accesses the test data service to fetch complete medical records for a subject
    participating in the cardiology Phase 2 study (CARD-2025-001). The data includes all clinical
    measurements, test results, and medical history needed for clinical assessment.

    Clinical Data Retrieved:
    - Demographics: age, gender, race, BMI, enrollment date
    - Vital Signs: blood pressure (systolic/diastolic), heart rate, temperature, respiratory rate
    - Laboratory Results: hemoglobin, creatinine, BNP, troponin, liver enzymes, lipid panel
    - Cardiac Imaging: echocardiogram LVEF%, wall motion abnormalities, valve function
    - Medical History: cardiovascular conditions, risk factors, prior interventions
    - Current Medications: cardiac drugs, antihypertensives, anticoagulants with dosages
    - Visit Schedule: screening, baseline, week 4/8/12 follow-ups with compliance status

    Available Test Subjects:
    - CARD001-CARD050: 50 subjects across 3 clinical sites
    - Each subject has realistic cardiology profiles (heart failure, hypertension, arrhythmias)
    - Pre-calculated EDC vs source document discrepancies for testing SDV workflows

    Use Cases:
    - Real-time clinical assessment during monitoring visits
    - Cross-reference with protocol inclusion/exclusion criteria
    - Identify safety signals or adverse trends
    - Generate queries for data clarification

    Args:
        subject_id: Subject identifier in format "CARDXXX" (e.g., "CARD001", "CARD015")

    Returns:
        JSON string containing:
        - Complete subject profile with all clinical data
        - Current visit status and compliance metrics
        - Historical trends for safety parameters
        - Data quality indicators and completeness scores

    Example Response:
    {
        "subject_id": "CARD001",
        "demographics": {"age": 67, "gender": "F", "bmi": 28.5},
        "vital_signs": {"systolic_bp": 147.5, "diastolic_bp": 79.6, "heart_rate": 72},
        "laboratory": {"hemoglobin": 12.3, "bnp": 319.57, "creatinine": 1.84},
        "imaging": {"lvef": 58.8, "wall_motion": "normal"},
        "visit_status": "Week 8 completed",
        "data_quality_score": 0.94
    }
    """
    try:
        from app.core.config import get_settings
        from app.services.test_data_service import TestDataService

        settings = get_settings()
        test_service = TestDataService(settings)

        # Get subject data synchronously (function tools can't be async)
        try:
            # Try to use existing event loop if available
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is running, create a new thread for async operation
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        asyncio.run, test_service.get_subject_data(subject_id)
                    )
                    subject_data = future.result()
            else:
                subject_data = loop.run_until_complete(
                    test_service.get_subject_data(subject_id)
                )
        except RuntimeError:
            # No event loop, create new one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            subject_data = loop.run_until_complete(
                test_service.get_subject_data(subject_id)
            )
            loop.close()

        if not subject_data:
            return json.dumps({"message": f"No data found for subject {subject_id}"})

        return json.dumps(subject_data)

    except Exception as e:
        return json.dumps(
            {
                "error": f"Failed to retrieve subject data: {str(e)}",
                "subject_id": subject_id,
            }
        )


@function_tool
def get_subject_discrepancies(subject_id: str) -> str:
    """Retrieve comprehensive discrepancy analysis for a clinical trial subject.

    This function accesses the test data service to identify all data discrepancies between
    Electronic Data Capture (EDC) systems and source documents for quality assessment and
    Source Data Verification (SDV) workflows.

    Discrepancy Detection Coverage:
    - Vital Signs: Blood pressure, heart rate, temperature variances
    - Laboratory Values: Missing results, out-of-range values, unit mismatches
    - Demographics: Age, weight, height inconsistencies
    - Medical History: Missing conditions, medication discrepancies
    - Visit Dates: Scheduling deviations, missed assessments
    - Safety Data: Adverse events, concomitant medication changes

    Quality Metrics Calculated:
    - Discrepancy rate per visit and per data domain
    - Time to resolution tracking
    - Site-specific error patterns
    - Monitor performance indicators

    Args:
        subject_id: Subject identifier (e.g., "CARD001" through "CARD050")

    Returns:
        JSON string containing:
        - subject_id: Subject identifier
        - total_discrepancies: Count of all discrepancies found
        - severity_breakdown: Counts by critical/major/minor
        - discrepancies: Detailed array of each discrepancy with:
          - field: Data field name
          - edc_value: Value in EDC system
          - source_value: Value in source document
          - severity: critical/major/minor classification
          - visit: Visit where discrepancy occurred
          - date_identified: When discrepancy was detected
          - clinical_impact: Assessment of impact on trial
          - resolution_required: Specific action needed
        - priority_action_required: Boolean flag for critical findings
        - site_quality_score: Overall data quality metric for the site

    Example Response:
    {
        "subject_id": "CARD001",
        "total_discrepancies": 3,
        "severity_breakdown": {"critical": 1, "major": 1, "minor": 1},
        "discrepancies": [
            {
                "field": "systolic_bp",
                "edc_value": "125",
                "source_value": "185",
                "severity": "critical",
                "visit": "Week 4",
                "clinical_impact": "Missed hypertensive crisis requiring intervention",
                "resolution_required": "Immediate query to site, safety assessment"
            }
        ],
        "priority_action_required": true,
        "site_quality_score": 0.76
    }
    """
    try:
        from app.core.config import get_settings
        from app.services.test_data_service import TestDataService

        settings = get_settings()
        test_service = TestDataService(settings)

        # Get discrepancies synchronously
        try:
            # Try to use existing event loop if available
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is running, create a new thread for async operation
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        asyncio.run, test_service.get_discrepancies(subject_id)
                    )
                    discrepancies = future.result()
            else:
                discrepancies = loop.run_until_complete(
                    test_service.get_discrepancies(subject_id)
                )
        except RuntimeError:
            # No event loop, create new one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            discrepancies = loop.run_until_complete(
                test_service.get_discrepancies(subject_id)
            )
            loop.close()

        if not discrepancies:
            return json.dumps(
                {"message": f"No discrepancies found for subject {subject_id}"}
            )

        # Analyze discrepancy severity
        critical_count = sum(
            1 for d in discrepancies if d.get("severity") == "critical"
        )
        major_count = sum(1 for d in discrepancies if d.get("severity") == "major")
        minor_count = sum(1 for d in discrepancies if d.get("severity") == "minor")

        result = {
            "subject_id": subject_id,
            "total_discrepancies": len(discrepancies),
            "severity_breakdown": {
                "critical": critical_count,
                "major": major_count,
                "minor": minor_count,
            },
            "discrepancies": discrepancies,
            "priority_action_required": critical_count > 0,
            "site_quality_score": max(0.0, 1.0 - (len(discrepancies) * 0.02)),
        }

        return json.dumps(result)

    except Exception as e:
        return json.dumps(
            {
                "error": f"Failed to retrieve discrepancies: {str(e)}",
                "subject_id": subject_id,
            }
        )


# Export test data tools
__all__ = [
    "get_test_subject_data",
    "get_subject_discrepancies",
]
