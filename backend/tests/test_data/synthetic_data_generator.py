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
    protocol_deviation_rate: float = 0.25  # 25% of subjects have protocol deviations
    clean_subjects_rate: float = 0.30  # 30% of subjects are completely clean (no discrepancies or deviations)


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
                "protocol_requirements": {
                    "inclusion_criteria": {
                        "age_min": 18,
                        "age_max": 80,
                        "lvef_min": 40,
                        "systolic_bp_max": 180,
                        "creatinine_max": 2.5,
                    },
                    "visit_windows": {
                        "Baseline": {"days_before": 0, "days_after": 0},
                        "Week_4": {"days_before": 3, "days_after": 3},
                        "Week_8": {"days_before": 5, "days_after": 5},
                        "Week_12": {"days_before": 7, "days_after": 7},
                        "End_of_Study": {"days_before": 14, "days_after": 14},
                    },
                    "required_assessments": {
                        "vital_signs": ["systolic_bp", "diastolic_bp", "heart_rate"],
                        "laboratory": ["troponin", "bnp", "creatinine"],
                        "imaging": ["lvef"],
                    },
                },
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

            # Determine subject data quality profile for balanced demo data
            quality_roll = random.random()
            if quality_roll < self.config.clean_subjects_rate:
                # Clean subjects: no discrepancies, no protocol deviations
                subject_has_discrepancies = False
                subject_has_protocol_deviations = False
                subject_quality_profile = "clean"
            elif quality_roll < self.config.clean_subjects_rate + (1 - self.config.clean_subjects_rate) * 0.5:
                # Discrepancy-only subjects: have discrepancies but compliant with protocol
                subject_has_discrepancies = True
                subject_has_protocol_deviations = False
                subject_quality_profile = "discrepancy_only"
            else:
                # Complex subjects: may have both discrepancies and protocol deviations
                subject_has_discrepancies = random.random() < 0.8  # 80% chance
                subject_has_protocol_deviations = random.random() < self.config.protocol_deviation_rate
                subject_quality_profile = "complex"

            # Generate baseline subject with quality profile metadata
            subject = {
                "subject_id": subject_id,
                "site_id": site_id,
                "demographics": self._generate_demographics(template, subject_has_protocol_deviations),
                "visits": self._generate_visits(subject_id, template, subject_has_discrepancies, subject_has_protocol_deviations),
                "overall_status": random.choice(["active", "completed", "withdrawn"]),
                "data_quality": {
                    "total_data_points": 0,
                    "discrepant_data_points": 0,
                    "query_count": 0,
                    "critical_findings": 0,
                },
                # Metadata for agent evaluation and supervised learning
                "_generation_metadata": {
                    "quality_profile": subject_quality_profile,
                    "has_discrepancies": subject_has_discrepancies,
                    "has_protocol_deviations": subject_has_protocol_deviations,
                    "is_ground_truth": True,  # Flag for supervised learning
                    "generation_timestamp": datetime.now().isoformat(),
                },
            }

            # Add data quality metrics
            subject["data_quality"] = self._calculate_subject_data_quality(subject)
            subjects.append(subject)

        return subjects

    def _generate_demographics(self, template: Dict, has_protocol_deviations: bool = False) -> Dict[str, Any]:
        """Generate realistic demographic data with optional protocol deviations."""
        protocol_reqs = template.get("protocol_requirements", {}).get("inclusion_criteria", {})
        
        if has_protocol_deviations and random.random() < 0.5:
            # Introduce age-related protocol deviation
            if random.random() < 0.5:
                age = random.choice([17, 81, 82, 85])  # Outside 18-80 range
            else:
                age = random.randint(protocol_reqs.get("age_min", 18), protocol_reqs.get("age_max", 80))
        else:
            # Compliant age
            age = random.randint(protocol_reqs.get("age_min", 18), protocol_reqs.get("age_max", 80))
        
        return {
            "age": age,
            "gender": random.choice(["M", "F"]),
            "race": random.choice(["White", "Black", "Asian", "Hispanic", "Other"]),
            "weight": round(random.uniform(45.0, 120.0), 1),
            "height": round(random.uniform(150.0, 200.0), 1),
            "enrollment_date": (
                datetime.now() - timedelta(days=random.randint(30, 365))
            ).strftime("%Y-%m-%d"),
        }

    def _generate_visits(self, subject_id: str, template: Dict, has_discrepancies: bool = True, has_protocol_deviations: bool = False) -> List[Dict[str, Any]]:
        """Generate visit data with potential discrepancies and protocol deviations."""
        visits = []
        visit_schedule = [
            "Screening",
            "Baseline",
            "Week_4",
            "Week_8",
            "Week_12",
            "End_of_Study",
        ]

        protocol_windows = template.get("protocol_requirements", {}).get("visit_windows", {})
        baseline_date = datetime.now() - timedelta(days=random.randint(30, 180))
        
        for i, visit_name in enumerate(visit_schedule):
            # Calculate intended visit date based on baseline
            weeks_from_baseline = {
                "Screening": -1,
                "Baseline": 0,
                "Week_4": 4,
                "Week_8": 8, 
                "Week_12": 12,
                "End_of_Study": 16
            }.get(visit_name, 0)
            
            intended_visit_date = baseline_date + timedelta(weeks=weeks_from_baseline)
            
            if visit_name == "Baseline":
                actual_visit_date = intended_visit_date
            else:
                
                # Introduce visit window deviations if flagged
                if has_protocol_deviations and visit_name in protocol_windows and random.random() < 0.3:
                    # Create visit outside allowed window
                    window = protocol_windows[visit_name]
                    max_deviation = max(window.get("days_before", 0), window.get("days_after", 0))
                    deviation_days = random.randint(max_deviation + 1, max_deviation + 10)
                    actual_visit_date = intended_visit_date + timedelta(days=random.choice([-deviation_days, deviation_days]))
                else:
                    # Visit within allowed window or slightly early/late
                    window_days = random.randint(-2, 2) if visit_name != "Baseline" else 0
                    actual_visit_date = intended_visit_date + timedelta(days=window_days)
            
            visit = {
                "visit_name": visit_name,
                "visit_date": actual_visit_date.strftime("%Y-%m-%d"),
                "intended_visit_date": intended_visit_date.strftime("%Y-%m-%d"),
                "edc_data": self._generate_visit_data(template, has_protocol_deviations),
                "source_data": None,  # Will be generated with discrepancies
                "discrepancies": [],
                "queries": [],
                "protocol_deviations": [],
            }

            # Generate source data with potential discrepancies
            visit["source_data"] = self._generate_source_data_with_discrepancies(
                visit["edc_data"], template, has_discrepancies
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

    def _generate_visit_data(self, template: Dict, has_protocol_deviations: bool = False) -> Dict[str, Any]:
        """Generate realistic visit data based on therapeutic area template with optional protocol deviations."""
        data = {}

        # Generate vital signs with potential protocol deviations
        if "vital_signs" in template:
            vital_signs = {}
            protocol_reqs = template.get("protocol_requirements", {}).get("inclusion_criteria", {})
            
            for param, (min_val, max_val) in template["vital_signs"].items():
                if has_protocol_deviations and param == "systolic_bp" and random.random() < 0.3:
                    # Introduce BP protocol deviation
                    max_allowed = protocol_reqs.get("systolic_bp_max", 180)
                    if random.random() < 0.5:
                        vital_signs[param] = round(random.uniform(max_allowed + 5, max_allowed + 30), 1)
                    else:
                        vital_signs[param] = round(random.uniform(min_val, max_val), 1)
                else:
                    vital_signs[param] = round(random.uniform(min_val, max_val), 1)
            data["vital_signs"] = vital_signs

        # Generate laboratory data with potential protocol deviations
        if "laboratory" in template:
            laboratory = {}
            protocol_reqs = template.get("protocol_requirements", {}).get("inclusion_criteria", {})
            
            for param, (min_val, max_val) in template["laboratory"].items():
                if has_protocol_deviations and param == "creatinine" and random.random() < 0.3:
                    # Introduce creatinine protocol deviation
                    max_allowed = protocol_reqs.get("creatinine_max", 2.5)
                    if random.random() < 0.5:
                        laboratory[param] = round(random.uniform(max_allowed + 0.2, max_allowed + 1.0), 2)
                    else:
                        laboratory[param] = round(random.uniform(min_val, max_val), 2)
                else:
                    laboratory[param] = round(random.uniform(min_val, max_val), 2)
            data["laboratory"] = laboratory

        # Generate therapeutic-specific data with potential protocol deviations
        for key, value in template.items():
            if key not in ["vital_signs", "laboratory", "adverse_events", "protocol_requirements"]:
                if isinstance(value, dict) and all(
                    isinstance(v, tuple) for v in value.values()
                ):
                    # Numeric parameters
                    section = {}
                    protocol_reqs = template.get("protocol_requirements", {}).get("inclusion_criteria", {})
                    
                    for param, (min_val, max_val) in value.items():
                        if has_protocol_deviations and param == "lvef" and random.random() < 0.3:
                            # Introduce LVEF protocol deviation (below minimum)
                            min_allowed = protocol_reqs.get("lvef_min", 40)
                            if random.random() < 0.5:
                                section[param] = round(random.uniform(min_allowed - 15, min_allowed - 1), 1)
                            else:
                                section[param] = round(random.uniform(min_val, max_val), 1)
                        else:
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
        self, edc_data: Dict, template: Dict, has_discrepancies: bool = True
    ) -> Dict[str, Any]:
        """Generate source data with intentional discrepancies for testing."""
        source_data = json.loads(json.dumps(edc_data))  # Deep copy

        # Only introduce discrepancies if this subject is flagged to have them
        if has_discrepancies:
            # Introduce discrepancies at individual data point level (not visit level)
            # This ensures balanced mix of normal and discrepant data for realistic demos
            self._introduce_selective_discrepancies(source_data)
        # When has_discrepancies=False, source_data should be identical to edc_data

        return source_data

    def _introduce_selective_discrepancies(self, data: Dict) -> None:
        """Introduce balanced discrepancies - a few per visit for realistic demos."""
        # Instead of applying rate to every data point, select a few random points per visit
        # This creates realistic discrepancy counts (2-5 per visit)
        
        # Count total data points in this visit
        all_data_points = []
        for section_name, section_data in data.items():
            if isinstance(section_data, dict):
                for param_name, param_value in section_data.items():
                    all_data_points.append((section_name, param_name, param_value))
        
        # Select a small number of data points to modify (1-4 per visit)
        num_discrepancies = random.randint(1, 4) if all_data_points else 0
        points_to_modify = random.sample(all_data_points, min(num_discrepancies, len(all_data_points)))
        
        for section_name, param_name, param_value in points_to_modify:
            section_data = data[section_name]
            
            if isinstance(param_value, (int, float)):
                # Small transcription errors (5-15% variance)
                variance_factor = random.uniform(0.05, 0.15)
                variance = param_value * variance_factor
                section_data[param_name] = round(
                    param_value + random.choice([-variance, variance]), 2
                )
            elif isinstance(param_value, str) and random.random() < 0.3:
                # Occasional missing data (remove parameter)
                del section_data[param_name]
        
        # Handle adverse events separately
        if "adverse_events" in data and isinstance(data["adverse_events"], list):
            # 20% chance to add an extra AE or modify existing one
            if random.random() < 0.2:
                if data["adverse_events"] and random.random() < 0.5:
                    # Modify existing AE severity
                    ae_to_modify = random.choice(data["adverse_events"])
                    ae_to_modify["severity"] = random.choice(["Mild", "Moderate", "Severe"])
                else:
                    # Add additional AE not in EDC
                    additional_ae = {
                        "term": random.choice(["dizziness", "headache", "fatigue", "nausea"]),
                        "severity": random.choice(["Mild", "Moderate"]),
                        "start_date": (datetime.now() - timedelta(days=random.randint(1, 14))).strftime("%Y-%m-%d"),
                        "outcome": "Ongoing"
                    }
                    data["adverse_events"].append(additional_ae)

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
                elif key not in source_dict:
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
        discrepancy_rate=0.02,  # Very low rate for individual data points to create realistic discrepancy counts
        critical_event_rate=0.04,
        protocol_deviation_rate=0.20,  # 20% of subjects have protocol deviations
        clean_subjects_rate=0.30,  # 30% of subjects are completely clean
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
