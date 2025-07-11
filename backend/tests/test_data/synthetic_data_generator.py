"""Synthetic Clinical Trial Data Generator for Agent Testing."""

import json
import random
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional


@dataclass
class StudyConfiguration:
    """Configuration for generating synthetic study data."""

    protocol_id: str
    phase: str
    therapeutic_area: str
    subject_count: int
    site_count: int
    discrepancy_rate: float = 0.15  # 15% of data points have discrepancies
    critical_event_rate: float = 0.05  # 5% critical safety events


class SyntheticDataGenerator:
    """Generate realistic synthetic clinical trial data for testing."""

    def __init__(self, config: StudyConfiguration):
        self.config = config
        self.therapeutic_templates = {
            "cardiology": {
                "vital_signs": {
                    "systolic_bp": (110, 180),
                    "diastolic_bp": (70, 110),
                    "heart_rate": (60, 100),
                },
                "laboratory": {
                    "troponin": (0.01, 0.15),
                    "bnp": (50, 400),
                    "creatinine": (0.8, 2.0),
                },
                "imaging": {
                    "lvef": (40, 70),
                    "wall_motion": [
                        "normal",
                        "mild_hypokinesis",
                        "moderate_hypokinesis",
                    ],
                },
                "adverse_events": ["chest_pain", "dyspnea", "palpitations", "syncope"],
            },
            "oncology": {
                "vital_signs": {
                    "systolic_bp": (100, 160),
                    "diastolic_bp": (60, 100),
                    "heart_rate": (70, 120),
                },
                "laboratory": {
                    "hemoglobin": (8.0, 15.0),
                    "platelets": (50, 400),
                    "alt": (10, 300),
                },
                "tumor_assessment": {
                    "target_lesions": (1, 5),
                    "sum_diameters": (10, 150),
                },
                "adverse_events": [
                    "fatigue",
                    "nausea",
                    "neutropenia",
                    "thrombocytopenia",
                ],
            },
        }

    def generate_complete_study(self) -> Dict[str, Any]:
        """Generate complete synthetic study with subjects, sites, and data."""

        study = {
            "study_info": {
                "protocol_id": self.config.protocol_id,
                "phase": self.config.phase,
                "therapeutic_area": self.config.therapeutic_area,
                "generation_timestamp": datetime.now().isoformat(),
                "total_subjects": self.config.subject_count,
                "total_sites": self.config.site_count,
            },
            "sites": self._generate_sites(),
            "subjects": self._generate_subjects(),
            "discrepancy_summary": self._calculate_discrepancy_summary(),
        }

        return study

    def _generate_sites(self) -> List[Dict[str, Any]]:
        """Generate synthetic study sites."""
        sites = []
        for i in range(1, self.config.site_count + 1):
            site = {
                "site_id": f"SITE_{i:03d}",
                "site_name": f"Research Center {i}",
                "country": random.choice(["USA", "Canada", "Germany", "UK"]),
                "investigator": f"Dr. {random.choice(['Smith', 'Johnson', 'Brown', 'Davis'])}",
                "enrollment_target": random.randint(10, 30),
                "performance_metrics": {
                    "query_rate": round(random.uniform(0.05, 0.25), 3),
                    "protocol_deviation_rate": round(random.uniform(0.02, 0.10), 3),
                },
            }
            sites.append(site)
        return sites

    def _generate_subjects(self) -> List[Dict[str, Any]]:
        """Generate synthetic subjects with realistic clinical data."""
        subjects = []
        template = self.therapeutic_templates.get(
            self.config.therapeutic_area, self.therapeutic_templates["cardiology"]
        )

        for i in range(1, self.config.subject_count + 1):
            subject_id = f"{self.config.protocol_id[:4]}{i:03d}"
            site_id = f"SITE_{random.randint(1, self.config.site_count):03d}"

            # Generate baseline subject
            subject = {
                "subject_id": subject_id,
                "site_id": site_id,
                "demographics": self._generate_demographics(),
                "visits": self._generate_visits(subject_id, template),
                "overall_status": random.choice(["active", "completed", "withdrawn"]),
                "data_quality": {
                    "total_data_points": 0,
                    "discrepant_data_points": 0,
                    "query_count": 0,
                    "critical_findings": 0,
                },
            }

            # Add data quality metrics
            subject["data_quality"] = self._calculate_subject_data_quality(subject)
            subjects.append(subject)

        return subjects

    def _generate_demographics(self) -> Dict[str, Any]:
        """Generate realistic demographic data."""
        return {
            "age": random.randint(18, 80),
            "gender": random.choice(["M", "F"]),
            "race": random.choice(["White", "Black", "Asian", "Hispanic", "Other"]),
            "weight": round(random.uniform(45.0, 120.0), 1),
            "height": round(random.uniform(150.0, 200.0), 1),
            "enrollment_date": (
                datetime.now() - timedelta(days=random.randint(30, 365))
            ).strftime("%Y-%m-%d"),
        }

    def _generate_visits(self, subject_id: str, template: Dict) -> List[Dict[str, Any]]:
        """Generate visit data with potential discrepancies."""
        visits = []
        visit_schedule = [
            "Screening",
            "Baseline",
            "Week_4",
            "Week_8",
            "Week_12",
            "End_of_Study",
        ]

        for visit_name in visit_schedule:
            visit = {
                "visit_name": visit_name,
                "visit_date": (
                    datetime.now() - timedelta(days=random.randint(0, 180))
                ).strftime("%Y-%m-%d"),
                "edc_data": self._generate_visit_data(template),
                "source_data": None,  # Will be generated with discrepancies
                "discrepancies": [],
                "queries": [],
            }

            # Generate source data with potential discrepancies
            visit["source_data"] = self._generate_source_data_with_discrepancies(
                visit["edc_data"], template
            )

            # Identify discrepancies
            visit["discrepancies"] = self._identify_discrepancies(
                visit["edc_data"], visit["source_data"]
            )

            # Generate queries based on discrepancies
            visit["queries"] = self._generate_queries_for_discrepancies(
                visit["discrepancies"], subject_id, visit_name
            )

            visits.append(visit)

        return visits

    def _generate_visit_data(self, template: Dict) -> Dict[str, Any]:
        """Generate realistic visit data based on therapeutic area template."""
        data = {}

        # Generate vital signs
        if "vital_signs" in template:
            vital_signs = {}
            for param, (min_val, max_val) in template["vital_signs"].items():
                vital_signs[param] = round(random.uniform(min_val, max_val), 1)
            data["vital_signs"] = vital_signs

        # Generate laboratory data
        if "laboratory" in template:
            laboratory = {}
            for param, (min_val, max_val) in template["laboratory"].items():
                laboratory[param] = round(random.uniform(min_val, max_val), 2)
            data["laboratory"] = laboratory

        # Generate therapeutic-specific data
        for key, value in template.items():
            if key not in ["vital_signs", "laboratory", "adverse_events"]:
                if isinstance(value, dict) and all(
                    isinstance(v, tuple) for v in value.values()
                ):
                    # Numeric parameters
                    section = {}
                    for param, (min_val, max_val) in value.items():
                        section[param] = round(random.uniform(min_val, max_val), 1)
                    data[key] = section
                elif isinstance(value, dict) and any(
                    isinstance(v, list) for v in value.values()
                ):
                    # Categorical parameters
                    section = {}
                    for param, options in value.items():
                        if isinstance(options, list):
                            section[param] = random.choice(options)
                        elif isinstance(options, tuple):
                            section[param] = round(
                                random.uniform(options[0], options[1]), 1
                            )
                    data[key] = section

        # Generate adverse events (randomly)
        if random.random() < 0.3:  # 30% chance of AE
            ae_terms = template.get("adverse_events", ["headache", "fatigue", "nausea"])
            data["adverse_events"] = [
                {
                    "term": random.choice(ae_terms),
                    "severity": random.choice(["Mild", "Moderate", "Severe"]),
                    "start_date": (
                        datetime.now() - timedelta(days=random.randint(1, 30))
                    ).strftime("%Y-%m-%d"),
                    "outcome": random.choice(
                        ["Ongoing", "Recovered", "Recovered with sequelae"]
                    ),
                }
            ]
        else:
            data["adverse_events"] = []

        return data

    def _generate_source_data_with_discrepancies(
        self, edc_data: Dict, template: Dict
    ) -> Dict[str, Any]:
        """Generate source data with intentional discrepancies for testing."""
        source_data = json.loads(json.dumps(edc_data))  # Deep copy

        # Introduce discrepancies based on configured rate
        if random.random() < self.config.discrepancy_rate:
            self._introduce_random_discrepancies(source_data)

        return source_data

    def _introduce_random_discrepancies(self, data: Dict) -> None:
        """Introduce realistic discrepancies in source data."""
        discrepancy_types = [
            "transcription_error",
            "unit_conversion",
            "missing_data",
            "additional_data",
            "calculation_error",
        ]

        discrepancy_type = random.choice(discrepancy_types)

        if discrepancy_type == "transcription_error":
            # Small numeric differences
            for section, values in data.items():
                if isinstance(values, dict):
                    for param, value in values.items():
                        if isinstance(value, (int, float)) and random.random() < 0.3:
                            # 5-10% variance
                            variance = value * random.uniform(0.05, 0.10)
                            values[param] = round(
                                value + random.choice([-variance, variance]), 2
                            )

        elif discrepancy_type == "missing_data":
            # Remove some data points
            for section, values in data.items():
                if isinstance(values, dict) and random.random() < 0.5:
                    if values:  # Only if there are values to remove
                        param_to_remove = random.choice(list(values.keys()))
                        del values[param_to_remove]

        elif discrepancy_type == "additional_data":
            # Add extra adverse events or findings
            if "adverse_events" in data and random.random() < 0.4:
                additional_ae = {
                    "term": random.choice(["dizziness", "rash", "constipation"]),
                    "severity": "Mild",
                    "start_date": datetime.now().strftime("%Y-%m-%d"),
                }
                data["adverse_events"].append(additional_ae)

    def _identify_discrepancies(
        self, edc_data: Dict, source_data: Dict
    ) -> List[Dict[str, Any]]:
        """Identify discrepancies between EDC and source data."""
        discrepancies = []

        def compare_nested_dicts(edc_dict, source_dict, prefix=""):
            for key in set(list(edc_dict.keys()) + list(source_dict.keys())):
                current_path = f"{prefix}.{key}" if prefix else key

                if key not in edc_dict:
                    discrepancies.append(
                        {
                            "field": current_path,
                            "discrepancy_type": "missing_in_edc",
                            "edc_value": None,
                            "source_value": source_dict[key],
                            "severity": (
                                "major" if "adverse_events" in current_path else "minor"
                            ),
                        }
                    )
                elif key not in source_data:
                    discrepancies.append(
                        {
                            "field": current_path,
                            "discrepancy_type": "missing_in_source",
                            "edc_value": edc_dict[key],
                            "source_value": None,
                            "severity": "minor",
                        }
                    )
                elif isinstance(edc_dict[key], dict) and isinstance(
                    source_dict[key], dict
                ):
                    compare_nested_dicts(edc_dict[key], source_dict[key], current_path)
                elif edc_dict[key] != source_dict[key]:
                    discrepancies.append(
                        {
                            "field": current_path,
                            "discrepancy_type": "value_difference",
                            "edc_value": edc_dict[key],
                            "source_value": source_dict[key],
                            "severity": self._assess_discrepancy_severity(
                                current_path, edc_dict[key], source_dict[key]
                            ),
                        }
                    )

        compare_nested_dicts(edc_data, source_data)
        return discrepancies

    def _assess_discrepancy_severity(
        self, field: str, edc_value: Any, source_value: Any
    ) -> str:
        """Assess severity of discrepancy based on field type and magnitude."""
        if "adverse_events" in field or "eligibility" in field:
            return "critical"

        if isinstance(edc_value, (int, float)) and isinstance(
            source_value, (int, float)
        ):
            percent_diff = abs(edc_value - source_value) / max(abs(edc_value), 1) * 100
            if percent_diff > 20:
                return "major"
            elif percent_diff > 10:
                return "minor"
            else:
                return "trivial"

        return "minor"

    def _generate_queries_for_discrepancies(
        self, discrepancies: List[Dict], subject_id: str, visit: str
    ) -> List[Dict[str, Any]]:
        """Generate clinical queries based on identified discrepancies."""
        queries = []

        for i, discrepancy in enumerate(discrepancies):
            query = {
                "query_id": f"Q_{subject_id}_{visit}_{i+1:03d}",
                "subject_id": subject_id,
                "visit": visit,
                "field": discrepancy["field"],
                "query_text": self._generate_query_text(discrepancy),
                "severity": discrepancy["severity"],
                "status": random.choice(["Open", "Answered", "Closed"]),
                "created_date": datetime.now().strftime("%Y-%m-%d"),
                "response_required_by": (datetime.now() + timedelta(days=7)).strftime(
                    "%Y-%m-%d"
                ),
            }
            queries.append(query)

        return queries

    def _generate_query_text(self, discrepancy: Dict) -> str:
        """Generate realistic query text based on discrepancy type."""
        field = discrepancy["field"]
        discrepancy_type = discrepancy["discrepancy_type"]
        edc_value = discrepancy["edc_value"]
        source_value = discrepancy["source_value"]

        templates = {
            "value_difference": f"Please verify {field}. EDC shows {edc_value} but source document shows {source_value}. Please confirm correct value.",
            "missing_in_edc": f"Source document shows {field} = {source_value} but this is not recorded in EDC. Please enter if applicable.",
            "missing_in_source": f"EDC shows {field} = {edc_value} but this is not documented in source. Please provide source documentation.",
        }

        return templates.get(discrepancy_type, f"Please verify data for {field}.")

    def _calculate_subject_data_quality(self, subject: Dict) -> Dict[str, int]:
        """Calculate data quality metrics for a subject."""
        total_points = 0
        discrepant_points = 0
        query_count = 0
        critical_findings = 0

        for visit in subject["visits"]:
            # Count data points
            for section_data in visit["edc_data"].values():
                if isinstance(section_data, dict):
                    total_points += len(section_data)
                elif isinstance(section_data, list):
                    total_points += len(section_data)
                else:
                    total_points += 1

            # Count discrepancies and queries
            discrepant_points += len(visit["discrepancies"])
            query_count += len(visit["queries"])
            critical_findings += len(
                [d for d in visit["discrepancies"] if d["severity"] == "critical"]
            )

        return {
            "total_data_points": total_points,
            "discrepant_data_points": discrepant_points,
            "query_count": query_count,
            "critical_findings": critical_findings,
        }

    def _calculate_discrepancy_summary(self) -> Dict[str, Any]:
        """Calculate overall study discrepancy statistics."""
        return {
            "expected_discrepancy_rate": self.config.discrepancy_rate,
            "expected_critical_event_rate": self.config.critical_event_rate,
            "generation_parameters": {
                "subject_count": self.config.subject_count,
                "site_count": self.config.site_count,
                "therapeutic_area": self.config.therapeutic_area,
            },
        }


# Example usage and presets
STUDY_PRESETS = {
    "cardiology_phase2": StudyConfiguration(
        protocol_id="CARD-2025-001",
        phase="Phase II",
        therapeutic_area="cardiology",
        subject_count=50,
        site_count=3,
        discrepancy_rate=0.12,
        critical_event_rate=0.04,
    ),
    "oncology_phase1": StudyConfiguration(
        protocol_id="ONCO-2025-001",
        phase="Phase I",
        therapeutic_area="oncology",
        subject_count=30,
        site_count=2,
        discrepancy_rate=0.20,  # Higher discrepancy rate for Phase I
        critical_event_rate=0.08,  # Higher critical event rate
    ),
}


def generate_test_study(preset_name: str = "cardiology_phase2") -> Dict[str, Any]:
    """Generate a complete test study using preset configuration."""
    config = STUDY_PRESETS.get(preset_name)
    if not config:
        raise ValueError(f"Unknown preset: {preset_name}")

    generator = SyntheticDataGenerator(config)
    return generator.generate_complete_study()


if __name__ == "__main__":
    # Generate sample data
    study_data = generate_test_study("cardiology_phase2")

    # Save to file for inspection
    with open("sample_study_data.json", "w") as f:
        json.dump(study_data, f, indent=2)

    print(f"Generated study with {len(study_data['subjects'])} subjects")
    print(f"Total sites: {len(study_data['sites'])}")
    print(
        f"Expected discrepancy rate: {study_data['discrepancy_summary']['expected_discrepancy_rate']}"
    )
