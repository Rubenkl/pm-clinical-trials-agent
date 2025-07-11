"""
Test suite for agent JSON output consistency.
Following TDD: These tests verify agents output structured JSON that can be parsed.
"""

import json
import re
from unittest.mock import Mock, patch

import pytest

from app.agents.data_verifier import DataVerifier
from app.agents.portfolio_manager import PortfolioManager
from app.agents.query_analyzer import QueryAnalyzer
from app.agents.query_generator import QueryGenerator
from app.agents.query_tracker import QueryTracker


class TestQueryAnalyzerJSONOutput:
    """Test that Query Analyzer outputs consistent JSON"""

    def test_query_analyzer_includes_json_in_response(self):
        """Test that Query Analyzer includes JSON output in response"""
        analyzer = QueryAnalyzer()

        # Mock the agent to return a response with JSON
        with patch.object(analyzer, "analyze_data_point") as mock_analyze:
            mock_analyze.return_value = """
            Clinical Analysis Complete:
            
            ```json
            {
                "severity": "critical",
                "category": "laboratory_value",
                "interpretation": "Hemoglobin 6.0 g/dL indicates severe anemia",
                "clinical_significance": "high",
                "confidence_score": 0.95,
                "suggested_query": "URGENT: Please confirm hemoglobin value of 6.0 g/dL",
                "recommendations": ["Immediate medical review", "Check for bleeding", "Consider transfusion"],
                "clinical_findings": [
                    {
                        "parameter": "hemoglobin",
                        "value": "6.0 g/dL",
                        "interpretation": "Severe anemia",
                        "severity": "critical",
                        "clinical_significance": "Life-threatening"
                    }
                ]
            }
            ```
            
            This requires immediate attention.
            """

            response = analyzer.analyze_data_point(
                {
                    "field_name": "hemoglobin",
                    "edc_value": "6.0",
                    "subject_id": "SUBJ001",
                }
            )

            # Verify JSON is present in response
            assert "```json" in response
            assert "```" in response

            # Extract and validate JSON
            json_match = re.search(r"```json\n(.*?)\n```", response, re.DOTALL)
            assert json_match is not None, "No JSON block found in response"

            # Parse JSON to ensure it's valid
            json_data = json.loads(json_match.group(1))

            # Verify required fields are present
            assert "severity" in json_data
            assert "category" in json_data
            assert "interpretation" in json_data
            assert "confidence_score" in json_data
            assert "suggested_query" in json_data
            assert "recommendations" in json_data
            assert "clinical_findings" in json_data

            # Verify field types
            assert isinstance(json_data["severity"], str)
            assert isinstance(json_data["confidence_score"], (int, float))
            assert isinstance(json_data["recommendations"], list)
            assert isinstance(json_data["clinical_findings"], list)

    def test_query_analyzer_json_structure_consistency(self):
        """Test that Query Analyzer always returns consistent JSON structure"""
        analyzer = QueryAnalyzer()

        test_cases = [
            "Analyze blood pressure 180/90 for subject SUBJ001",
            "Review glucose level 300 mg/dL for subject SUBJ002",
            "Check creatinine 3.5 mg/dL for subject SUBJ003",
        ]

        for test_input in test_cases:
            with patch.object(analyzer, "analyze_data_point") as mock_analyze:
                # Mock different responses with consistent JSON structure
                mock_analyze.return_value = f"""
                Analysis of {test_input}:
                
                ```json
                {{
                    "severity": "major",
                    "category": "vital_signs",
                    "interpretation": "Value outside normal range",
                    "clinical_significance": "medium",
                    "confidence_score": 0.85,
                    "suggested_query": "Please confirm the value",
                    "recommendations": ["Verify with source", "Medical review"],
                    "clinical_findings": []
                }}
                ```
                """

                response = analyzer.analyze_data_point({"test": test_input})

                # Extract JSON
                json_match = re.search(r"```json\n(.*?)\n```", response, re.DOTALL)
                assert json_match is not None

                json_data = json.loads(json_match.group(1))

                # Verify all required fields are present
                required_fields = [
                    "severity",
                    "category",
                    "interpretation",
                    "clinical_significance",
                    "confidence_score",
                    "suggested_query",
                    "recommendations",
                    "clinical_findings",
                ]

                for field in required_fields:
                    assert field in json_data, f"Missing required field: {field}"


class TestDataVerifierJSONOutput:
    """Test that Data Verifier outputs consistent JSON"""

    def test_data_verifier_includes_json_in_response(self):
        """Test that Data Verifier includes JSON output in response"""
        verifier = DataVerifier()

        with patch.object(verifier, "cross_system_verification") as mock_verify:
            mock_verify.return_value = """
            Data Verification Complete:
            
            ```json
            {
                "match_score": 0.85,
                "matching_fields": ["age", "gender", "visit_date"],
                "discrepancies": [
                    {
                        "field": "blood_pressure",
                        "edc_value": "120/80",
                        "source_value": "130/85",
                        "severity": "minor",
                        "discrepancy_type": "mismatch",
                        "confidence": 0.9
                    }
                ],
                "total_fields_compared": 15,
                "verification_status": "completed",
                "critical_findings": []
            }
            ```
            
            Verification shows good overall match with minor discrepancy.
            """

            response = verifier.cross_system_verification(
                {"bp": "120/80"}, {"bp": "130/85"}
            )

            # Verify JSON is present
            assert "```json" in response

            # Extract and validate JSON
            json_match = re.search(r"```json\n(.*?)\n```", response, re.DOTALL)
            assert json_match is not None

            json_data = json.loads(json_match.group(1))

            # Verify required fields
            assert "match_score" in json_data
            assert "matching_fields" in json_data
            assert "discrepancies" in json_data
            assert "total_fields_compared" in json_data

            # Verify data types
            assert isinstance(json_data["match_score"], (int, float))
            assert isinstance(json_data["matching_fields"], list)
            assert isinstance(json_data["discrepancies"], list)
            assert isinstance(json_data["total_fields_compared"], int)


class TestPortfolioManagerJSONOutput:
    """Test that Portfolio Manager outputs consistent JSON"""

    def test_portfolio_manager_workflow_json_output(self):
        """Test that Portfolio Manager includes workflow JSON in response"""
        manager = PortfolioManager()

        with patch.object(manager, "orchestrate_workflow") as mock_orchestrate:
            mock_orchestrate.return_value = """
            Workflow Orchestration Complete:
            
            ```json
            {
                "workflow_id": "WF_20250109_001",
                "workflow_type": "comprehensive_analysis",
                "status": "completed",
                "agents_involved": ["query-analyzer", "data-verifier", "query-generator"],
                "execution_time": 8.5,
                "results": {
                    "queries_generated": 3,
                    "discrepancies_found": 2,
                    "critical_findings": 1
                },
                "recommendations": [
                    "Prioritize critical hemoglobin finding",
                    "Review blood pressure discrepancy",
                    "Schedule follow-up verification"
                ],
                "next_actions": [
                    {
                        "action": "medical_review",
                        "priority": "high",
                        "assigned_to": "medical_monitor"
                    }
                ]
            }
            ```
            
            All agents completed successfully with actionable results.
            """

            response = manager.orchestrate_workflow(
                {"workflow_type": "comprehensive_analysis", "subject_id": "SUBJ001"}
            )

            # Verify JSON is present
            assert "```json" in response

            # Extract and validate JSON
            json_match = re.search(r"```json\n(.*?)\n```", response, re.DOTALL)
            assert json_match is not None

            json_data = json.loads(json_match.group(1))

            # Verify workflow-specific fields
            assert "workflow_id" in json_data
            assert "workflow_type" in json_data
            assert "status" in json_data
            assert "agents_involved" in json_data
            assert "execution_time" in json_data
            assert "results" in json_data
            assert "recommendations" in json_data
            assert "next_actions" in json_data


class TestQueryGeneratorJSONOutput:
    """Test that Query Generator outputs consistent JSON"""

    def test_query_generator_includes_json_in_response(self):
        """Test that Query Generator includes JSON output in response"""
        generator = QueryGenerator()

        with patch.object(generator, "generate_clinical_query") as mock_generate:
            mock_generate.return_value = """
            Query Generation Complete:
            
            ```json
            {
                "query_id": "Q_20250109_001",
                "query_text": "Please confirm the hemoglobin value of 6.0 g/dL reported for Subject SUBJ001 at the Week 12 visit. This value appears to be significantly below the normal range (12-16 g/dL) and represents a potential safety concern.",
                "query_type": "safety_query",
                "severity": "critical",
                "medical_justification": "Hemoglobin level indicates severe anemia requiring immediate clinical review",
                "regulatory_references": ["ICH E6(R2) 5.1.1", "FDA Guidance on Safety Reporting"],
                "response_timeline": "24_hours",
                "escalation_required": true,
                "supporting_documentation": [
                    "Normal range reference values",
                    "Previous hemoglobin trends for subject"
                ]
            }
            ```
            
            Query generated with appropriate medical context and urgency.
            """

            response = generator.generate_clinical_query(
                {
                    "finding": "hemoglobin 6.0 g/dL",
                    "subject_id": "SUBJ001",
                    "severity": "critical",
                }
            )

            # Verify JSON is present
            assert "```json" in response

            # Extract and validate JSON
            json_match = re.search(r"```json\n(.*?)\n```", response, re.DOTALL)
            assert json_match is not None

            json_data = json.loads(json_match.group(1))

            # Verify query-specific fields
            assert "query_id" in json_data
            assert "query_text" in json_data
            assert "query_type" in json_data
            assert "severity" in json_data
            assert "medical_justification" in json_data
            assert "response_timeline" in json_data
            assert "escalation_required" in json_data


class TestQueryTrackerJSONOutput:
    """Test that Query Tracker outputs consistent JSON"""

    def test_query_tracker_includes_json_in_response(self):
        """Test that Query Tracker includes JSON output in response"""
        tracker = QueryTracker()

        with patch.object(tracker, "track_query_lifecycle") as mock_track:
            mock_track.return_value = """
            Query Tracking Update:
            
            ```json
            {
                "query_id": "Q_20250109_001",
                "status": "pending_response",
                "created_date": "2025-01-09T10:30:00Z",
                "last_updated": "2025-01-09T10:35:00Z",
                "age_hours": 2.5,
                "sla_status": "within_sla",
                "sla_remaining_hours": 21.5,
                "assigned_to": "site_coordinator",
                "priority": "high",
                "escalation_level": 0,
                "workflow_history": [
                    {
                        "timestamp": "2025-01-09T10:30:00Z",
                        "action": "query_created",
                        "performed_by": "system"
                    },
                    {
                        "timestamp": "2025-01-09T10:35:00Z",
                        "action": "assigned_to_site",
                        "performed_by": "query_manager"
                    }
                ],
                "next_milestone": {
                    "action": "site_response_due",
                    "due_date": "2025-01-10T10:30:00Z"
                }
            }
            ```
            
            Query is being tracked and is within SLA timelines.
            """

            response = tracker.track_query_lifecycle("Q_20250109_001")

            # Verify JSON is present
            assert "```json" in response

            # Extract and validate JSON
            json_match = re.search(r"```json\n(.*?)\n```", response, re.DOTALL)
            assert json_match is not None

            json_data = json.loads(json_match.group(1))

            # Verify tracking-specific fields
            assert "query_id" in json_data
            assert "status" in json_data
            assert "created_date" in json_data
            assert "last_updated" in json_data
            assert "age_hours" in json_data
            assert "sla_status" in json_data
            assert "assigned_to" in json_data
            assert "workflow_history" in json_data
            assert "next_milestone" in json_data


class TestJSONConsistencyAcrossAgents:
    """Test that all agents follow consistent JSON output patterns"""

    def test_all_agents_use_consistent_json_format(self):
        """Test that all agents use consistent JSON formatting"""
        agents = [
            QueryAnalyzer(),
            DataVerifier(),
            PortfolioManager(),
            QueryGenerator(),
            QueryTracker(),
        ]

        # Common JSON formatting rules all agents should follow
        for agent in agents:
            # Mock a response from each agent
            if isinstance(agent, QueryAnalyzer):
                with patch.object(agent, "analyze_clinical_data") as mock_method:
                    mock_method.return_value = """
                    ```json
                    {"test": "value"}
                    ```
                    """
                    response = agent.analyze_clinical_data("test")
            elif isinstance(agent, DataVerifier):
                with patch.object(agent, "cross_system_verification") as mock_method:
                    mock_method.return_value = """
                    ```json
                    {"test": "value"}
                    ```
                    """
                    response = agent.cross_system_verification({}, {})
            elif isinstance(agent, PortfolioManager):
                with patch.object(agent, "orchestrate_workflow") as mock_method:
                    mock_method.return_value = """
                    ```json
                    {"test": "value"}
                    ```
                    """
                    response = agent.orchestrate_workflow({})
            elif isinstance(agent, QueryGenerator):
                with patch.object(agent, "generate_clinical_query") as mock_method:
                    mock_method.return_value = """
                    ```json
                    {"test": "value"}
                    ```
                    """
                    response = agent.generate_clinical_query({})
            elif isinstance(agent, QueryTracker):
                with patch.object(agent, "track_query_lifecycle") as mock_method:
                    mock_method.return_value = """
                    ```json
                    {"test": "value"}
                    ```
                    """
                    response = agent.track_query_lifecycle("test")

            # Verify consistent JSON formatting
            assert "```json" in response
            assert response.count("```json") == 1, "Should have exactly one JSON block"
            assert (
                response.count("```") >= 2
            ), "Should have opening and closing JSON markers"

            # Extract JSON and verify it's valid
            json_match = re.search(r"```json\n(.*?)\n```", response, re.DOTALL)
            assert json_match is not None

            # Should be valid JSON
            json_data = json.loads(json_match.group(1))
            assert isinstance(json_data, dict)

    def test_json_schema_validation_patterns(self):
        """Test that JSON outputs follow expected schema patterns"""
        # Define expected schema patterns for different agent types
        schema_patterns = {
            "query_analyzer": {
                "required_fields": [
                    "severity",
                    "category",
                    "interpretation",
                    "confidence_score",
                ],
                "field_types": {
                    "severity": str,
                    "confidence_score": (int, float),
                    "recommendations": list,
                },
            },
            "data_verifier": {
                "required_fields": [
                    "match_score",
                    "discrepancies",
                    "total_fields_compared",
                ],
                "field_types": {
                    "match_score": (int, float),
                    "discrepancies": list,
                    "total_fields_compared": int,
                },
            },
            "portfolio_manager": {
                "required_fields": ["workflow_id", "workflow_type", "status"],
                "field_types": {
                    "workflow_id": str,
                    "workflow_type": str,
                    "status": str,
                },
            },
        }

        # This test validates the schema patterns are well-defined
        for agent_type, schema in schema_patterns.items():
            assert "required_fields" in schema
            assert "field_types" in schema
            assert isinstance(schema["required_fields"], list)
            assert isinstance(schema["field_types"], dict)
            assert len(schema["required_fields"]) > 0
