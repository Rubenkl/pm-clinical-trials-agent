"""Test datasets for validating Data Verifier Agent performance."""

from typing import Dict, Any, List, Tuple
from datetime import datetime

# Ground truth test data with known discrepancies
GROUND_TRUTH_DATASETS = [
    {
        "test_id": "DISCREPANCY_001",
        "description": "Blood pressure measurement discrepancy",
        "edc_data": {
            "subject_id": "S001",
            "visit": "V1",
            "vital_signs": {
                "systolic_bp": 120,
                "diastolic_bp": 80,
                "heart_rate": 72,
                "temperature": 98.6
            }
        },
        "source_data": {
            "subject_id": "S001",
            "visit": "V1",
            "vital_signs": {
                "systolic_bp": 125,  # 5 point discrepancy
                "diastolic_bp": 80,
                "heart_rate": 72,
                "temperature": 98.6
            }
        },
        "expected_discrepancies": [
            {
                "field": "vital_signs.systolic_bp",
                "edc_value": 120,
                "source_value": 125,
                "difference": 5,
                "expected_severity": "minor",
                "expected_confidence_min": 0.9
            }
        ],
        "expected_accuracy": 0.75  # 3/4 fields match
    },
    
    {
        "test_id": "DISCREPANCY_002", 
        "description": "Missing adverse event - critical safety issue",
        "edc_data": {
            "subject_id": "S002",
            "visit": "V2",
            "adverse_events": [],
            "vital_signs": {
                "systolic_bp": 130,
                "diastolic_bp": 85
            }
        },
        "source_data": {
            "subject_id": "S002",
            "visit": "V2", 
            "adverse_events": [
                {
                    "term": "Myocardial infarction",
                    "severity": "Life-threatening",
                    "outcome": "Recovered",
                    "start_date": "2025-01-15"
                }
            ],
            "vital_signs": {
                "systolic_bp": 130,
                "diastolic_bp": 85
            }
        },
        "expected_discrepancies": [
            {
                "field": "adverse_events",
                "edc_value": [],
                "source_value": [{"term": "Myocardial infarction", "severity": "Life-threatening"}],
                "difference": "missing_in_edc",
                "expected_severity": "critical",  # Safety issue
                "expected_confidence_min": 0.95
            }
        ],
        "expected_accuracy": 0.67  # 2/3 main fields match
    },
    
    {
        "test_id": "DISCREPANCY_003",
        "description": "Laboratory values with unit mismatch",
        "edc_data": {
            "subject_id": "S003",
            "visit": "V1",
            "laboratory": {
                "glucose": 95,  # mg/dL
                "glucose_unit": "mg/dL",
                "hemoglobin": 12.5,
                "hemoglobin_unit": "g/dL"
            }
        },
        "source_data": {
            "subject_id": "S003",
            "visit": "V1",
            "laboratory": {
                "glucose": 5.3,  # mmol/L (equivalent to 95 mg/dL)
                "glucose_unit": "mmol/L",
                "hemoglobin": 125,  # g/L (equivalent to 12.5 g/dL)
                "hemoglobin_unit": "g/L"
            }
        },
        "expected_discrepancies": [
            {
                "field": "laboratory.glucose",
                "edc_value": 95,
                "source_value": 5.3,
                "difference": "unit_conversion_needed",
                "expected_severity": "minor",
                "expected_confidence_min": 0.8
            },
            {
                "field": "laboratory.hemoglobin",
                "edc_value": 12.5,
                "source_value": 125,
                "difference": "unit_conversion_needed",
                "expected_severity": "minor",
                "expected_confidence_min": 0.8
            }
        ],
        "expected_accuracy": 0.5  # Units differ but values are equivalent
    },
    
    {
        "test_id": "DISCREPANCY_004",
        "description": "Protocol deviation - eligibility violation",
        "edc_data": {
            "subject_id": "S004",
            "visit": "Screening",
            "demographics": {
                "age": 65,
                "weight": 75.5
            },
            "eligibility": {
                "meets_inclusion_criteria": True,
                "inclusion_violations": []
            }
        },
        "source_data": {
            "subject_id": "S004",
            "visit": "Screening", 
            "demographics": {
                "age": 65,
                "weight": 75.5
            },
            "eligibility": {
                "meets_inclusion_criteria": False,
                "inclusion_violations": ["Age > 60 years excluded per protocol amendment"]
            }
        },
        "expected_discrepancies": [
            {
                "field": "eligibility.meets_inclusion_criteria",
                "edc_value": True,
                "source_value": False,
                "difference": "protocol_deviation",
                "expected_severity": "critical",  # Protocol violation
                "expected_confidence_min": 0.95
            }
        ],
        "expected_accuracy": 0.67  # 2/3 main sections match
    },
    
    {
        "test_id": "DISCREPANCY_005",
        "description": "Perfect match - no discrepancies",
        "edc_data": {
            "subject_id": "S005",
            "visit": "V1",
            "vital_signs": {
                "systolic_bp": 118,
                "diastolic_bp": 78,
                "heart_rate": 68
            },
            "concomitant_medications": ["Aspirin 81mg", "Metoprolol 50mg"]
        },
        "source_data": {
            "subject_id": "S005",
            "visit": "V1",
            "vital_signs": {
                "systolic_bp": 118,
                "diastolic_bp": 78,
                "heart_rate": 68
            },
            "concomitant_medications": ["Aspirin 81mg", "Metoprolol 50mg"]
        },
        "expected_discrepancies": [],
        "expected_accuracy": 1.0  # Perfect match
    },
    
    {
        "test_id": "DISCREPANCY_006",
        "description": "Multiple discrepancies across different fields",
        "edc_data": {
            "subject_id": "S006",
            "visit": "V3",
            "vital_signs": {
                "systolic_bp": 140,
                "diastolic_bp": 90,
                "heart_rate": 85,
                "temperature": 99.1
            },
            "laboratory": {
                "glucose": 180,
                "cholesterol": 220
            },
            "adverse_events": [
                {"term": "Headache", "severity": "Mild"}
            ]
        },
        "source_data": {
            "subject_id": "S006",
            "visit": "V3",
            "vital_signs": {
                "systolic_bp": 135,  # 5 point difference
                "diastolic_bp": 92,  # 2 point difference  
                "heart_rate": 85,
                "temperature": 99.2  # 0.1 degree difference
            },
            "laboratory": {
                "glucose": 185,  # 5 point difference
                "cholesterol": 220
            },
            "adverse_events": [
                {"term": "Headache", "severity": "Mild"},
                {"term": "Nausea", "severity": "Mild"}  # Additional AE in source
            ]
        },
        "expected_discrepancies": [
            {
                "field": "vital_signs.systolic_bp",
                "edc_value": 140,
                "source_value": 135,
                "difference": -5,
                "expected_severity": "minor",
                "expected_confidence_min": 0.9
            },
            {
                "field": "vital_signs.diastolic_bp", 
                "edc_value": 90,
                "source_value": 92,
                "difference": 2,
                "expected_severity": "minor",
                "expected_confidence_min": 0.85
            },
            {
                "field": "laboratory.glucose",
                "edc_value": 180,
                "source_value": 185,
                "difference": 5,
                "expected_severity": "minor",
                "expected_confidence_min": 0.9
            },
            {
                "field": "adverse_events",
                "edc_value": [{"term": "Headache"}],
                "source_value": [{"term": "Headache"}, {"term": "Nausea"}],
                "difference": "missing_in_edc",
                "expected_severity": "major",
                "expected_confidence_min": 0.9
            }
        ],
        "expected_accuracy": 0.5  # Multiple discrepancies
    }
]


# Critical data field test cases
CRITICAL_DATA_TEST_CASES = [
    {
        "test_id": "CRITICAL_001",
        "description": "Death event - highest priority",
        "data": {
            "subject_id": "S007",
            "adverse_events": [
                {
                    "term": "Death",
                    "outcome": "Fatal",
                    "cause": "Cardiac arrest",
                    "date": "2025-01-20"
                }
            ]
        },
        "expected_critical_fields": [
            {
                "field_name": "adverse_events.death",
                "expected_risk_level": "critical",
                "expected_immediate_action": True,
                "expected_regulatory_reporting": True
            }
        ],
        "expected_overall_risk_score_min": 0.95
    },
    
    {
        "test_id": "CRITICAL_002", 
        "description": "Protocol deviation affecting eligibility",
        "data": {
            "subject_id": "S008",
            "eligibility": {
                "inclusion_criteria_met": False,
                "exclusion_criteria_violated": ["Pregnancy"],
                "enrollment_date": "2025-01-10"
            },
            "pregnancy_test": {
                "result": "Positive",
                "date": "2025-01-09"
            }
        },
        "expected_critical_fields": [
            {
                "field_name": "eligibility.inclusion_criteria_met",
                "expected_risk_level": "critical",
                "expected_immediate_action": True,
                "expected_regulatory_reporting": True
            }
        ],
        "expected_overall_risk_score_min": 0.85
    },
    
    {
        "test_id": "CRITICAL_003",
        "description": "Normal data - low risk",
        "data": {
            "subject_id": "S009",
            "vital_signs": {
                "systolic_bp": 120,
                "diastolic_bp": 80,
                "heart_rate": 70
            },
            "laboratory": {
                "glucose": 95,
                "cholesterol": 180
            }
        },
        "expected_critical_fields": [],
        "expected_overall_risk_score_min": 0.0,
        "expected_overall_risk_score_max": 0.3
    }
]


# Pattern detection test cases
PATTERN_DETECTION_TEST_CASES = [
    {
        "test_id": "PATTERN_001",
        "description": "Site-specific blood pressure measurement pattern",
        "historical_data": [
            {
                "subject_id": "S010",
                "site_id": "SITE_001",
                "discrepancy": "vital_signs.systolic_bp",
                "edc_value": 120,
                "source_value": 125,
                "difference": 5,
                "timestamp": "2025-01-15"
            },
            {
                "subject_id": "S011", 
                "site_id": "SITE_001",
                "discrepancy": "vital_signs.systolic_bp",
                "edc_value": 130,
                "source_value": 135,
                "difference": 5,
                "timestamp": "2025-01-16"
            },
            {
                "subject_id": "S012",
                "site_id": "SITE_001", 
                "discrepancy": "vital_signs.systolic_bp",
                "edc_value": 125,
                "source_value": 130,
                "difference": 5,
                "timestamp": "2025-01-17"
            },
            {
                "subject_id": "S013",
                "site_id": "SITE_002",
                "discrepancy": "laboratory.glucose",
                "edc_value": 95,
                "source_value": 98,
                "difference": 3,
                "timestamp": "2025-01-18"
            }
        ],
        "expected_patterns": [
            {
                "pattern_type": "site_specific",
                "description_contains": "SITE_001",
                "affected_subjects_count": 3,
                "pattern_strength_min": 0.85
            }
        ]
    }
]


def get_test_dataset(test_id: str) -> Dict[str, Any]:
    """Get a specific test dataset by ID."""
    for dataset in GROUND_TRUTH_DATASETS:
        if dataset["test_id"] == test_id:
            return dataset
    
    for dataset in CRITICAL_DATA_TEST_CASES:
        if dataset["test_id"] == test_id:
            return dataset
            
    for dataset in PATTERN_DETECTION_TEST_CASES:
        if dataset["test_id"] == test_id:
            return dataset
    
    raise ValueError(f"Test dataset {test_id} not found")


def get_all_discrepancy_tests() -> List[Dict[str, Any]]:
    """Get all discrepancy detection test cases."""
    return GROUND_TRUTH_DATASETS


def get_all_critical_data_tests() -> List[Dict[str, Any]]:
    """Get all critical data identification test cases."""
    return CRITICAL_DATA_TEST_CASES


def get_all_pattern_tests() -> List[Dict[str, Any]]:
    """Get all pattern detection test cases."""
    return PATTERN_DETECTION_TEST_CASES


def calculate_accuracy_score(predicted_discrepancies: List[Dict], expected_discrepancies: List[Dict], tolerance: float = 0.1) -> float:
    """Calculate accuracy score comparing predicted vs expected discrepancies.
    
    Args:
        predicted_discrepancies: List of discrepancies found by the agent
        expected_discrepancies: List of ground truth discrepancies
        tolerance: Tolerance for confidence score matching
        
    Returns:
        Accuracy score between 0.0 and 1.0
    """
    if not expected_discrepancies:
        # If no discrepancies expected, score is 1.0 if none found, 0.0 if any found
        return 1.0 if not predicted_discrepancies else 0.0
    
    correct_predictions = 0
    
    for expected in expected_discrepancies:
        # Find matching predicted discrepancy
        for predicted in predicted_discrepancies:
            if (predicted.get("field") == expected["field"] and
                predicted.get("edc_value") == expected["edc_value"] and
                predicted.get("source_value") == expected["source_value"]):
                
                # Check if confidence is within tolerance
                expected_conf_min = expected.get("expected_confidence_min", 0.0)
                predicted_conf = predicted.get("confidence", 0.0)
                
                if predicted_conf >= expected_conf_min - tolerance:
                    correct_predictions += 1
                break
    
    return correct_predictions / len(expected_discrepancies)


def calculate_performance_metrics(predicted_discrepancies: List[Dict], expected_discrepancies: List[Dict]) -> Dict[str, float]:
    """Calculate comprehensive performance metrics.
    
    Returns:
        Dictionary with precision, recall, f1_score, and accuracy
    """
    if not expected_discrepancies and not predicted_discrepancies:
        return {"precision": 1.0, "recall": 1.0, "f1_score": 1.0, "accuracy": 1.0}
    
    if not expected_discrepancies:
        return {"precision": 0.0, "recall": 1.0, "f1_score": 0.0, "accuracy": 0.0}
    
    if not predicted_discrepancies:
        return {"precision": 1.0, "recall": 0.0, "f1_score": 0.0, "accuracy": 0.0}
    
    # True positives: correctly identified discrepancies
    true_positives = 0
    for expected in expected_discrepancies:
        for predicted in predicted_discrepancies:
            if (predicted.get("field") == expected["field"] and
                predicted.get("edc_value") == expected["edc_value"] and
                predicted.get("source_value") == expected["source_value"]):
                true_positives += 1
                break
    
    # False positives: incorrectly identified discrepancies
    false_positives = len(predicted_discrepancies) - true_positives
    
    # False negatives: missed discrepancies
    false_negatives = len(expected_discrepancies) - true_positives
    
    # Calculate metrics
    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0.0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0.0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    accuracy = true_positives / len(expected_discrepancies) if expected_discrepancies else 0.0
    
    return {
        "precision": precision,
        "recall": recall, 
        "f1_score": f1_score,
        "accuracy": accuracy,
        "true_positives": true_positives,
        "false_positives": false_positives,
        "false_negatives": false_negatives
    }