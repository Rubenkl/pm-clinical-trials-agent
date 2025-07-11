"""Tests for discrepancy identification algorithms and systems."""

import json
from datetime import datetime, timedelta
from typing import Any, Dict, List

import pytest

from app.agents.data_verifier import (
    DataDiscrepancy,
    DataVerifier,
    DiscrepancySeverity,
    DiscrepancyType,
    VerificationResult,
)


class TestDiscrepancyIdentification:
    """Test suite for discrepancy identification algorithms."""

    def setup_method(self):
        """Set up test fixtures."""
        self.verifier = DataVerifier()

    def test_value_mismatch_identification(self):
        """Test identification of value mismatches between systems."""
        edc_data = {"systolic_bp": 120, "subject_id": "S001"}
        source_data = {"systolic_bp": 125, "subject_id": "S001"}

        discrepancy = self.verifier._identify_value_mismatch(
            field_name="systolic_bp", edc_value=120, source_value=125
        )

        assert discrepancy is not None
        assert discrepancy.discrepancy_type == DiscrepancyType.VALUE_MISMATCH
        assert discrepancy.field_name == "systolic_bp"
        assert discrepancy.edc_value == 120
        assert discrepancy.source_value == 125
        assert discrepancy.difference == 5

    def test_missing_data_identification(self):
        """Test identification of missing data in either system."""
        # Missing in EDC
        missing_edc = self.verifier._identify_missing_data(
            field_name="adverse_events",
            edc_value=None,
            source_value=[{"term": "Headache"}],
        )

        assert missing_edc is not None
        assert missing_edc.discrepancy_type == DiscrepancyType.MISSING_IN_EDC
        assert (
            missing_edc.severity == DiscrepancySeverity.CRITICAL
        )  # Adverse events are critical

        # Missing in source
        missing_source = self.verifier._identify_missing_data(
            field_name="laboratory.glucose", edc_value=95, source_value=None
        )

        assert missing_source is not None
        assert missing_source.discrepancy_type == DiscrepancyType.MISSING_IN_SOURCE

    def test_format_difference_identification(self):
        """Test identification of format differences."""
        discrepancy = self.verifier._identify_format_difference(
            field_name="birth_date", edc_value="01/15/1985", source_value="1985-01-15"
        )

        assert discrepancy is not None
        assert discrepancy.discrepancy_type == DiscrepancyType.FORMAT_DIFFERENCE
        assert discrepancy.severity == DiscrepancySeverity.MINOR

    def test_unit_mismatch_identification(self):
        """Test identification of unit mismatches."""
        discrepancy = self.verifier._identify_unit_mismatch(
            field_name="laboratory.glucose",
            edc_value=95,
            edc_unit="mg/dL",
            source_value=5.3,
            source_unit="mmol/L",
        )

        assert discrepancy is not None
        assert discrepancy.discrepancy_type == DiscrepancyType.UNIT_MISMATCH
        assert discrepancy.severity == DiscrepancySeverity.MINOR
        # Values are equivalent, so should note unit conversion needed
        assert "conversion" in discrepancy.description.lower()

    def test_protocol_deviation_identification(self):
        """Test identification of protocol deviations."""
        discrepancy = self.verifier._identify_protocol_deviation(
            field_name="eligibility.meets_criteria",
            edc_value=True,
            source_value=False,
            protocol_rules={"age_limit": 60},
        )

        assert discrepancy is not None
        assert discrepancy.discrepancy_type == DiscrepancyType.PROTOCOL_DEVIATION
        assert discrepancy.severity == DiscrepancySeverity.CRITICAL
        assert discrepancy.requires_query is True

    def test_range_violation_identification(self):
        """Test identification of range violations."""
        # Blood pressure critically high (outside critical range)
        discrepancy = self.verifier._identify_range_violation(
            field_name="vital_signs.systolic_bp",
            value=350,  # Outside critical range (200, 300)
            normal_range=(90, 180),
            critical_range=(200, 300),
        )

        assert discrepancy is not None
        assert discrepancy.discrepancy_type == DiscrepancyType.RANGE_VIOLATION
        assert discrepancy.severity == DiscrepancySeverity.CRITICAL

    def test_calculation_error_identification(self):
        """Test identification of calculation errors."""
        # BMI calculation error
        height_cm = 170
        weight_kg = 70
        reported_bmi = 25.5  # Should be ~24.2
        expected_bmi = weight_kg / ((height_cm / 100) ** 2)

        discrepancy = self.verifier._identify_calculation_error(
            field_name="demographics.bmi",
            reported_value=reported_bmi,
            calculated_value=expected_bmi,
            tolerance=0.5,
        )

        assert discrepancy is not None
        assert discrepancy.discrepancy_type == DiscrepancyType.CALCULATION_ERROR
        assert abs(discrepancy.difference - (reported_bmi - expected_bmi)) < 0.01

    def test_severity_assessment_algorithm(self):
        """Test severity assessment algorithm for different discrepancy types."""
        # Critical: Safety-related field
        critical_severity = self.verifier._assess_discrepancy_severity(
            field_name="adverse_events.serious",
            discrepancy_type=DiscrepancyType.MISSING_IN_EDC,
            field_criticality="safety",
        )
        assert critical_severity == DiscrepancySeverity.CRITICAL

        # Major: Important clinical field
        major_severity = self.verifier._assess_discrepancy_severity(
            field_name="laboratory.glucose",
            discrepancy_type=DiscrepancyType.VALUE_MISMATCH,
            difference_magnitude=50,
        )
        assert major_severity == DiscrepancySeverity.MAJOR

        # Minor: Small numerical difference
        minor_severity = self.verifier._assess_discrepancy_severity(
            field_name="vital_signs.systolic_bp",
            discrepancy_type=DiscrepancyType.VALUE_MISMATCH,
            difference_magnitude=3,
        )
        assert minor_severity == DiscrepancySeverity.MINOR

    def test_confidence_scoring_algorithm(self):
        """Test confidence scoring algorithm."""
        # High confidence for exact matches with clear difference
        high_confidence = self.verifier._calculate_confidence_score(
            field_name="subject_id",
            edc_value="S001",
            source_value="S002",
            difference_type="exact_mismatch",
        )
        assert high_confidence >= 0.95

        # Medium confidence for numerical differences
        medium_confidence = self.verifier._calculate_confidence_score(
            field_name="vital_signs.systolic_bp",
            edc_value=120,
            source_value=125,
            difference_type="numerical_difference",
        )
        assert 0.7 <= medium_confidence <= 0.9

        # Lower confidence for ambiguous cases
        low_confidence = self.verifier._calculate_confidence_score(
            field_name="comments",
            edc_value="Patient feeling well",
            source_value="Pt. feels good",
            difference_type="semantic_difference",
        )
        assert 0.5 <= low_confidence <= 0.8

    def test_batch_discrepancy_identification(self):
        """Test batch processing of multiple discrepancies."""
        edc_data = {
            "subject_id": "S001",
            "vital_signs": {"systolic_bp": 120, "diastolic_bp": 80},
            "laboratory": {"glucose": 95},
            "adverse_events": [],
        }

        source_data = {
            "subject_id": "S001",
            "vital_signs": {"systolic_bp": 125, "diastolic_bp": 80},  # 5 point diff
            "laboratory": {"glucose": 98},  # 3 point diff
            "adverse_events": [{"term": "Headache"}],  # Missing in EDC
        }

        discrepancies = self.verifier._identify_all_discrepancies(edc_data, source_data)

        assert len(discrepancies) == 3

        # Check systolic BP discrepancy
        bp_discrepancy = next(
            (d for d in discrepancies if "systolic_bp" in d.field_name), None
        )
        assert bp_discrepancy is not None
        assert bp_discrepancy.difference == 5
        assert bp_discrepancy.severity == DiscrepancySeverity.MINOR

        # Check glucose discrepancy
        glucose_discrepancy = next(
            (d for d in discrepancies if "glucose" in d.field_name), None
        )
        assert glucose_discrepancy is not None
        assert glucose_discrepancy.difference == 3

        # Check adverse events discrepancy
        ae_discrepancy = next(
            (d for d in discrepancies if "adverse_events" in d.field_name), None
        )
        assert ae_discrepancy is not None
        assert ae_discrepancy.discrepancy_type == DiscrepancyType.MISSING_IN_EDC
        assert (
            ae_discrepancy.severity == DiscrepancySeverity.CRITICAL
        )  # Adverse events are critical

    def test_temporal_pattern_detection(self):
        """Test detection of temporal patterns in discrepancies."""
        historical_discrepancies = [
            {
                "field": "vital_signs.systolic_bp",
                "timestamp": datetime.now() - timedelta(days=3),
                "site_id": "SITE_001",
                "difference": 5,
            },
            {
                "field": "vital_signs.systolic_bp",
                "timestamp": datetime.now() - timedelta(days=2),
                "site_id": "SITE_001",
                "difference": 5,
            },
            {
                "field": "vital_signs.systolic_bp",
                "timestamp": datetime.now() - timedelta(days=1),
                "site_id": "SITE_001",
                "difference": 5,
            },
        ]

        patterns = self.verifier._detect_temporal_patterns(historical_discrepancies)

        assert len(patterns) >= 1
        pattern = patterns[0]
        assert pattern["pattern_type"] == "consistent_bias"
        assert pattern["field"] == "vital_signs.systolic_bp"
        assert pattern["site_id"] == "SITE_001"
        assert pattern["pattern_strength"] > 0.8

    def test_site_specific_pattern_detection(self):
        """Test detection of site-specific discrepancy patterns."""
        site_discrepancies = [
            {"site_id": "SITE_001", "field": "laboratory.glucose", "difference": 5},
            {"site_id": "SITE_001", "field": "laboratory.glucose", "difference": 6},
            {"site_id": "SITE_001", "field": "laboratory.glucose", "difference": 4},
            {"site_id": "SITE_002", "field": "laboratory.glucose", "difference": 1},
        ]

        patterns = self.verifier._detect_site_patterns(site_discrepancies)

        site_001_pattern = next(p for p in patterns if p["site_id"] == "SITE_001")
        assert site_001_pattern["average_difference"] > 4.5
        assert site_001_pattern["consistency_score"] > 0.7

    def test_field_specific_pattern_detection(self):
        """Test detection of field-specific discrepancy patterns."""
        field_discrepancies = [
            {"field": "vital_signs.systolic_bp", "difference": 5, "subject_id": "S001"},
            {"field": "vital_signs.systolic_bp", "difference": 4, "subject_id": "S002"},
            {"field": "vital_signs.systolic_bp", "difference": 6, "subject_id": "S003"},
            {
                "field": "vital_signs.diastolic_bp",
                "difference": 1,
                "subject_id": "S001",
            },
        ]

        patterns = self.verifier._detect_field_patterns(field_discrepancies)

        bp_pattern = next(p for p in patterns if "systolic_bp" in p["field"])
        assert bp_pattern["occurrence_rate"] > 0.5
        assert bp_pattern["average_magnitude"] > 4.5

    def test_discrepancy_clustering(self):
        """Test clustering of similar discrepancies."""
        discrepancies = [
            DataDiscrepancy(
                discrepancy_id="D001",
                field_name="vital_signs.systolic_bp",
                edc_value=120,
                source_value=125,
                discrepancy_type=DiscrepancyType.VALUE_MISMATCH,
                severity=DiscrepancySeverity.MINOR,
                confidence=0.9,
                description="BP measurement difference",
                difference=5,
            ),
            DataDiscrepancy(
                discrepancy_id="D002",
                field_name="vital_signs.systolic_bp",
                edc_value=130,
                source_value=134,
                discrepancy_type=DiscrepancyType.VALUE_MISMATCH,
                severity=DiscrepancySeverity.MINOR,
                confidence=0.9,
                description="BP measurement difference",
                difference=4,
            ),
            DataDiscrepancy(
                discrepancy_id="D003",
                field_name="laboratory.glucose",
                edc_value=95,
                source_value=100,
                discrepancy_type=DiscrepancyType.VALUE_MISMATCH,
                severity=DiscrepancySeverity.MINOR,
                confidence=0.8,
                description="Lab value difference",
                difference=5,
            ),
        ]

        clusters = self.verifier._cluster_discrepancies(discrepancies)

        assert len(clusters) == 2  # BP cluster and lab cluster
        bp_cluster = next(
            (c for c in clusters if "vital_signs" in c["field_pattern"]), None
        )
        assert bp_cluster is not None
        assert len(bp_cluster["discrepancies"]) == 2

    def test_discrepancy_prioritization(self):
        """Test prioritization of discrepancies for review."""
        discrepancies = [
            DataDiscrepancy(
                discrepancy_id="D001",
                field_name="adverse_events",
                edc_value=[],
                source_value=[{"term": "Death"}],
                discrepancy_type=DiscrepancyType.MISSING_IN_EDC,
                severity=DiscrepancySeverity.CRITICAL,
                confidence=0.95,
                description="Missing death event",
            ),
            DataDiscrepancy(
                discrepancy_id="D002",
                field_name="vital_signs.systolic_bp",
                edc_value=120,
                source_value=125,
                discrepancy_type=DiscrepancyType.VALUE_MISMATCH,
                severity=DiscrepancySeverity.MINOR,
                confidence=0.9,
                description="Minor BP difference",
            ),
        ]

        prioritized = self.verifier._prioritize_discrepancies(discrepancies)

        # Critical discrepancy should be first
        assert prioritized[0].severity == DiscrepancySeverity.CRITICAL
        assert prioritized[0].field_name == "adverse_events"
        assert prioritized[1].severity == DiscrepancySeverity.MINOR

    def test_false_positive_filtering(self):
        """Test filtering of potential false positive discrepancies."""
        potential_discrepancies = [
            {
                "field": "comments",
                "edc_value": "Patient feeling well",
                "source_value": "Pt. feels good",
                "similarity_score": 0.85,
            },
            {
                "field": "subject_id",
                "edc_value": "S001",
                "source_value": "S002",
                "similarity_score": 0.1,
            },
        ]

        filtered = self.verifier._filter_false_positives(potential_discrepancies)

        # Only the subject_id discrepancy should remain (low similarity = real discrepancy)
        assert len(filtered) == 1
        assert filtered[0]["field"] == "subject_id"

    def test_discrepancy_resolution_tracking(self):
        """Test tracking of discrepancy resolution status."""
        discrepancy = DataDiscrepancy(
            discrepancy_id="D001",
            field_name="vital_signs.systolic_bp",
            edc_value=120,
            source_value=125,
            discrepancy_type=DiscrepancyType.VALUE_MISMATCH,
            severity=DiscrepancySeverity.MINOR,
            confidence=0.9,
            description="BP measurement difference",
        )

        # Track resolution
        resolution_data = {
            "resolution_status": "resolved",
            "resolution_method": "data_clarification_form",
            "resolved_value": 125,
            "resolver": "clinical_monitor",
            "resolution_date": datetime.now().isoformat(),
        }

        updated_discrepancy = self.verifier._update_discrepancy_resolution(
            discrepancy, resolution_data
        )

        assert updated_discrepancy.metadata["resolution_status"] == "resolved"
        assert updated_discrepancy.metadata["resolved_value"] == 125

    def test_regulatory_impact_assessment(self):
        """Test assessment of regulatory impact for discrepancies."""
        # Critical safety discrepancy
        safety_impact = self.verifier._assess_regulatory_impact(
            field_name="adverse_events.serious",
            discrepancy_type=DiscrepancyType.MISSING_IN_EDC,
            severity=DiscrepancySeverity.CRITICAL,
        )

        assert safety_impact["reporting_required"] is True
        assert safety_impact["urgency"] == "immediate"
        assert "FDA" in safety_impact["applicable_regulations"]

        # Minor discrepancy
        minor_impact = self.verifier._assess_regulatory_impact(
            field_name="demographics.height",
            discrepancy_type=DiscrepancyType.VALUE_MISMATCH,
            severity=DiscrepancySeverity.MINOR,
        )

        assert minor_impact["reporting_required"] is False
        assert minor_impact["urgency"] == "routine"
