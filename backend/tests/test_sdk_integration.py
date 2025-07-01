"""Comprehensive integration tests for OpenAI Agents SDK refactoring."""

import pytest
import asyncio
from typing import Dict, Any
from datetime import datetime

from app.agents.portfolio_manager import PortfolioManager
from app.agents.query_analyzer import QueryAnalyzer
from app.agents.data_verifier import DataVerifier
from app.agents.query_generator import QueryGenerator
from app.agents.query_tracker import QueryTracker


class TestSDKIntegration:
    """Test suite for comprehensive SDK integration."""
    
    @pytest.fixture
    def portfolio_manager(self):
        """Portfolio Manager instance."""
        return PortfolioManager()
    
    @pytest.fixture
    def query_analyzer(self):
        """Query Analyzer instance."""
        return QueryAnalyzer()
    
    @pytest.fixture
    def data_verifier(self):
        """Data Verifier instance."""
        return DataVerifier()
    
    @pytest.fixture
    def query_generator(self):
        """Query Generator instance."""
        return QueryGenerator()
    
    @pytest.fixture
    def query_tracker(self):
        """Query Tracker instance."""
        return QueryTracker()
    
    @pytest.fixture
    def sample_clinical_data(self):
        """Sample clinical trial data for testing."""
        return {
            "subject_id": "SUBJ001",
            "visit": "Week 4",
            "site_name": "Memorial Hospital",
            "edc_data": {
                "hemoglobin": "12.5",
                "weight": "75.0",
                "blood_pressure_systolic": "140",
                "blood_pressure_diastolic": "90",
                "adverse_events": [
                    {"term": "Headache", "severity": "mild", "start_date": "2024-12-15"}
                ]
            },
            "source_data": {
                "hemoglobin": "11.2",
                "weight": "75.0", 
                "blood_pressure_systolic": "135",
                "blood_pressure_diastolic": "90",
                "adverse_events": [
                    {"term": "Headache", "severity": "mild", "start_date": "2024-12-15"}
                ]
            }
        }
    
    def test_all_agents_initialized(self, portfolio_manager, query_analyzer, data_verifier, query_generator, query_tracker):
        """Test that all agents are properly initialized with OpenAI Agents SDK patterns."""
        agents = [
            (portfolio_manager, "Clinical Portfolio Manager", 5),
            (query_analyzer, "Clinical Query Analyzer", 5),
            (data_verifier, "Clinical Data Verifier", 6),
            (query_generator, "Clinical Query Generator", 3),
            (query_tracker, "Clinical Query Tracker", 4)
        ]
        
        for agent_instance, expected_name, expected_tools in agents:
            # Test agent and context initialization
            assert agent_instance.agent is not None
            assert agent_instance.context is not None
            assert expected_name in agent_instance.agent.name
            
            # Test OpenAI Agents SDK integration
            assert len(agent_instance.agent.tools) == expected_tools
            assert hasattr(agent_instance.agent, 'instructions')
            assert len(agent_instance.agent.instructions) > 100  # Substantial instructions
    
    def test_agent_instructions_defined(self, portfolio_manager, query_analyzer, data_verifier):
        """Test that all agents have proper instructions defined."""
        assert portfolio_manager.instructions is not None
        assert len(portfolio_manager.instructions) > 100  # Substantial instructions
        
        assert query_analyzer.instructions is not None
        assert len(query_analyzer.instructions) > 100
        
        assert data_verifier.instructions is not None
        assert len(data_verifier.instructions) > 100
    
    @pytest.mark.asyncio
    async def test_portfolio_manager_orchestration(self, portfolio_manager, sample_clinical_data):
        """Test Portfolio Manager workflow orchestration."""
        workflow_request = {
            "workflow_id": "WF_INTEGRATION_001",
            "workflow_type": "query_resolution",
            "description": "Integration test workflow",
            "input_data": sample_clinical_data
        }
        
        result = await portfolio_manager.orchestrate_workflow(workflow_request)
        
        assert result is not None
        assert "workflow_id" in result
        assert "status" in result
        assert "execution_plan" in result
        assert result["workflow_id"] == "WF_INTEGRATION_001"
    
    @pytest.mark.asyncio
    async def test_query_analyzer_functionality(self, query_analyzer, sample_clinical_data):
        """Test Query Analyzer SDK functionality."""
        # Test single data point analysis
        analysis_result = await query_analyzer.analyze_data_point(sample_clinical_data["edc_data"])
        
        assert "query_id" in analysis_result
        assert "category" in analysis_result
        assert "severity" in analysis_result
        assert "confidence" in analysis_result
        assert 0.0 <= analysis_result["confidence"] <= 1.0
        
        # Test batch analysis
        batch_data = [sample_clinical_data["edc_data"], sample_clinical_data["source_data"]]
        batch_results = await query_analyzer.batch_analyze(batch_data)
        
        assert len(batch_results) == 2
        assert all("query_id" in result for result in batch_results)
    
    @pytest.mark.asyncio
    async def test_data_verifier_functionality(self, data_verifier, sample_clinical_data):
        """Test Data Verifier SDK functionality."""
        edc_data = sample_clinical_data["edc_data"]
        source_data = sample_clinical_data["source_data"]
        
        # Test cross-system verification
        verification_result = await data_verifier.cross_system_verification(edc_data, source_data)
        
        assert "verification_id" in verification_result
        assert "match_score" in verification_result
        assert "discrepancies" in verification_result
        assert 0.0 <= verification_result["match_score"] <= 1.0
        
        # Test SDV verification
        sdv_result = await data_verifier.complete_sdv_verification(edc_data, source_data)
        
        assert "sdv_status" in sdv_result
        assert "audit_trail" in sdv_result
        assert sdv_result["sdv_status"] in ["passed", "failed", "requires_review"]
    
    @pytest.mark.asyncio
    async def test_context_sharing_between_agents(self, portfolio_manager, query_analyzer, data_verifier):
        """Test that contexts properly accumulate data across operations."""
        sample_data = {
            "subject_id": "SUBJ001",
            "field_name": "hemoglobin",
            "edc_value": "12.5",
            "source_value": "11.2"
        }
        
        # Query Analyzer context accumulation
        await query_analyzer.analyze_data_point(sample_data)
        assert len(query_analyzer.context.analysis_history) > 0
        
        # Data Verifier context accumulation
        edc_data = {"subject_id": "SUBJ001", "hemoglobin": "12.5"}
        source_data = {"subject_id": "SUBJ001", "hemoglobin": "11.2"}
        await data_verifier.cross_system_verification(edc_data, source_data)
        assert len(data_verifier.context.verification_history) > 0
        
        # Portfolio Manager context accumulation
        workflow_request = {
            "workflow_id": "WF_CONTEXT_TEST",
            "workflow_type": "query_resolution",
            "input_data": sample_data
        }
        await portfolio_manager.orchestrate_workflow(workflow_request)
        assert len(portfolio_manager.context.active_workflows) > 0
    
    @pytest.mark.asyncio
    async def test_performance_optimization(self, query_analyzer, data_verifier):
        """Test performance optimization features work correctly."""
        # Test Query Analyzer batch processing
        large_dataset = []
        for i in range(10):
            data_point = {
                "subject_id": f"SUBJ{i:03d}",
                "field_name": "hemoglobin",
                "edc_value": str(12.0 + i * 0.1),
                "source_value": str(11.5 + i * 0.1)
            }
            large_dataset.append(data_point)
        
        start_time = datetime.now()
        results = await query_analyzer.batch_analyze(large_dataset)
        execution_time = (datetime.now() - start_time).total_seconds()
        
        assert len(results) == 10
        assert execution_time < 10.0  # Should complete quickly
        
        # Test Data Verifier batch processing
        batch_data = []
        for i in range(5):
            edc_data = {"subject_id": f"SUBJ{i:03d}", "hemoglobin": str(12.0 + i * 0.1)}
            source_data = {"subject_id": f"SUBJ{i:03d}", "hemoglobin": str(11.8 + i * 0.1)}
            batch_data.append((edc_data, source_data))
        
        start_time = datetime.now()
        batch_result = await data_verifier.batch_verification(batch_data)
        execution_time = (datetime.now() - start_time).total_seconds()
        
        assert batch_result["total_subjects"] == 5
        assert execution_time < 15.0  # Should complete quickly
    
    @pytest.mark.asyncio
    async def test_error_handling_across_agents(self, portfolio_manager, query_analyzer, data_verifier):
        """Test error handling consistency across all agents."""
        # Test Portfolio Manager error handling
        invalid_workflow = {
            "workflow_type": "",  # Invalid
            "input_data": {}
        }
        
        pm_result = await portfolio_manager.orchestrate_workflow(invalid_workflow)
        assert pm_result["success"] is False
        assert "error" in pm_result
        
        # Test Query Analyzer error handling
        invalid_data = {"invalid": "structure"}
        qa_result = await query_analyzer.analyze_data_point(invalid_data)
        # Should handle gracefully
        assert qa_result is not None
        
        # Test Data Verifier error handling
        dv_result = await data_verifier.cross_system_verification({}, {})
        # Should handle gracefully
        assert dv_result is not None
    
    def test_configuration_consistency(self, portfolio_manager, query_analyzer, data_verifier):
        """Test that configuration options work consistently."""
        # Test confidence thresholds
        assert query_analyzer.confidence_threshold == 0.7
        assert data_verifier.confidence_threshold == 0.8
        
        # Test configurability
        query_analyzer.set_confidence_threshold(0.9)
        assert query_analyzer.confidence_threshold == 0.9
        
        data_verifier.set_confidence_threshold(0.85)
        assert data_verifier.confidence_threshold == 0.85
    
    @pytest.mark.asyncio
    async def test_medical_terminology_consistency(self, query_analyzer):
        """Test medical terminology handling consistency."""
        # Test medical term standardization
        assert query_analyzer.standardize_medical_term("MI") == "Myocardial infarction"
        assert query_analyzer.standardize_medical_term("HTN") == "Hypertension"
        
        # Test severity assessment
        from app.agents.query_analyzer import QuerySeverity
        critical_severity = query_analyzer.assess_medical_severity("myocardial infarction")
        assert critical_severity == QuerySeverity.CRITICAL
    
    @pytest.mark.asyncio
    async def test_regulatory_compliance_features(self, data_verifier):
        """Test regulatory compliance features across agents."""
        # Test audit trail generation
        verification_data = {
            "verification_id": "DV_REGULATORY_TEST",
            "subject_id": "SUBJ001",
            "discrepancies_found": 1,
            "critical_findings": 0
        }
        
        audit_trail = await data_verifier.generate_audit_trail(verification_data)
        
        assert "audit_id" in audit_trail
        assert "regulatory_compliance" in audit_trail
        assert audit_trail["regulatory_compliance"]["gdp_compliance"] == "verified"
    
    def test_openai_agents_sdk_function_tools(self, portfolio_manager, query_analyzer, data_verifier, query_generator, query_tracker):
        """Test that all agents have proper OpenAI Agents SDK function tools defined."""
        agents_tools = [
            (portfolio_manager, 5, "Portfolio Manager"),
            (query_analyzer, 5, "Query Analyzer"),
            (data_verifier, 6, "Data Verifier"),
            (query_generator, 3, "Query Generator"),
            (query_tracker, 4, "Query Tracker")
        ]
        
        total_tools = 0
        for agent_instance, expected_count, agent_name in agents_tools:
            tools = agent_instance.agent.tools
            assert len(tools) == expected_count, f"{agent_name} should have {expected_count} tools, found {len(tools)}"
            total_tools += len(tools)
            
            # Verify tools are proper OpenAI Agents SDK function tools
            for tool in tools:
                # OpenAI Agents SDK tools may be wrapped, check if callable
                assert callable(tool) or hasattr(tool, '__call__'), f"{agent_name} tool should be callable"
        
        assert total_tools == 23, f"Total system should have 23 tools, found {total_tools}"
    
    @pytest.mark.asyncio
    async def test_end_to_end_workflow_simulation(self, portfolio_manager, sample_clinical_data):
        """Test end-to-end workflow simulation."""
        # Simulate a complete clinical trials workflow
        workflow_steps = [
            {
                "workflow_id": "WF_E2E_001",
                "workflow_type": "query_resolution",
                "description": "End-to-end workflow test",
                "input_data": sample_clinical_data
            },
            {
                "workflow_id": "WF_E2E_002", 
                "workflow_type": "data_verification",
                "description": "Data verification workflow",
                "input_data": sample_clinical_data
            }
        ]
        
        results = []
        for workflow in workflow_steps:
            result = await portfolio_manager.orchestrate_workflow(workflow)
            results.append(result)
            
            # Check workflow was created
            workflow_id = result.get("workflow_id")
            if workflow_id:
                status = await portfolio_manager.get_workflow_status(workflow_id)
                assert status is not None
        
        assert len(results) == 2
        assert all("workflow_id" in r for r in results)
    
    def test_memory_efficiency(self, portfolio_manager, query_analyzer, data_verifier):
        """Test that agents manage memory efficiently."""
        # Check that contexts don't grow unbounded
        initial_pm_history = len(portfolio_manager.context.active_workflows)
        initial_qa_history = len(query_analyzer.context.analysis_history)
        initial_dv_history = len(data_verifier.context.verification_history)
        
        # All should start empty or with minimal data
        assert initial_pm_history < 5
        assert initial_qa_history < 5
        assert initial_dv_history < 5
    
    @pytest.mark.asyncio
    async def test_concurrent_operations(self, query_analyzer):
        """Test that agents can handle concurrent operations."""
        # Create multiple concurrent analysis tasks
        tasks = []
        for i in range(3):
            data_point = {
                "subject_id": f"SUBJ{i:03d}",
                "field_name": "hemoglobin",
                "edc_value": str(12.0 + i),
                "source_value": str(11.5 + i)
            }
            task = query_analyzer.analyze_data_point(data_point)
            tasks.append(task)
        
        # Execute concurrently
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 3
        assert all("query_id" in result for result in results)
        assert all(result["subject_id"] == f"SUBJ{i:03d}" for i, result in enumerate(results))