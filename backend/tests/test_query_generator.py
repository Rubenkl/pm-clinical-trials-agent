"""Tests for Query Generator Agent using OpenAI Agents SDK."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import json
from typing import Dict, Any

from app.agents.query_generator import QueryGenerator, QueryTemplate


class TestQueryGenerator:
    """Test suite for Query Generator agent."""
    
    @pytest.fixture
    def mock_openai_client(self):
        """Mock OpenAI client for testing."""
        with patch('app.agents.query_generator.OpenAI') as mock_client:
            # Mock assistant
            mock_assistant = Mock()
            mock_assistant.id = "asst_test123"
            mock_assistant.name = "Clinical Query Generator"
            
            # Mock thread
            mock_thread = Mock()
            mock_thread.id = "thread_test123"
            
            # Mock message
            mock_message = Mock()
            mock_message.content = [Mock(text=Mock(value=json.dumps({
                "query_text": "Dear Site Test,\n\nWe identified a discrepancy...",
                "category": "data_discrepancy",
                "priority": "major",
                "supporting_docs": ["Source document", "Lab report"],
                "regulatory_refs": ["ICH-GCP 4.9"],
                "suggested_response_time": "5 business days"
            })))]
            
            # Mock run
            mock_run = Mock()
            mock_run.status = "completed"
            mock_run.id = "run_test123"
            
            # Set up client methods
            mock_client.return_value.beta.assistants.create.return_value = mock_assistant
            mock_client.return_value.beta.threads.create.return_value = mock_thread
            mock_client.return_value.beta.threads.messages.create.return_value = Mock()
            mock_client.return_value.beta.threads.runs.create.return_value = mock_run
            mock_client.return_value.beta.threads.runs.retrieve.return_value = mock_run
            mock_client.return_value.beta.threads.messages.list.return_value = Mock(data=[mock_message])
            
            yield mock_client
    
    @pytest.fixture
    def query_generator(self, mock_openai_client):
        """Create QueryGenerator instance with mocked client."""
        return QueryGenerator()
    
    @pytest.fixture
    def sample_analysis(self) -> Dict[str, Any]:
        """Sample analysis data for testing."""
        return {
            "query_id": "AUTO_SUBJ001_hemoglobin_20250129_143022",
            "category": "data_discrepancy",
            "severity": "major",
            "confidence": 0.95,
            "subject_id": "SUBJ001",
            "visit": "Week 4",
            "field_name": "Hemoglobin",
            "description": "Hemoglobin value in EDC (12.5 g/dL) differs from source (11.2 g/dL)",
            "suggested_actions": [
                "Verify correct lab value from source document",
                "Update EDC with correct value",
                "Document reason for discrepancy"
            ],
            "medical_context": "Hemoglobin below normal range indicates anemia",
            "regulatory_impact": "Critical lab value requiring immediate verification"
        }
    
    def test_query_generator_initialization(self, query_generator):
        """Test QueryGenerator initialization."""
        assert query_generator.assistant is not None
        assert query_generator.instructions is not None
        assert len(query_generator.templates) >= 3
        assert "missing_data" in query_generator.templates
        assert "data_discrepancy" in query_generator.templates
        assert "adverse_event" in query_generator.templates
    
    def test_template_initialization(self, query_generator):
        """Test query templates are properly initialized."""
        missing_data_template = query_generator.get_template("missing_data")
        assert missing_data_template is not None
        assert missing_data_template.category == "missing_data"
        assert missing_data_template.severity == "major"
        assert "Dear Site" in missing_data_template.template
        assert "ICH-GCP 4.9" in missing_data_template.regulatory_requirements
    
    @pytest.mark.asyncio
    async def test_generate_query_basic(self, query_generator, sample_analysis):
        """Test basic query generation."""
        result = await query_generator.generate_query(sample_analysis)
        
        assert result is not None
        assert "query_text" in result
        assert "category" in result
        assert "priority" in result
        assert result["category"] == "data_discrepancy"
        assert result["priority"] == "major"
        assert len(result["query_text"]) > 50
    
    @pytest.mark.asyncio
    async def test_generate_query_with_site_preferences(self, query_generator, sample_analysis):
        """Test query generation with site preferences."""
        site_prefs = {
            "language": "en-US",
            "formal_tone": True,
            "include_protocol_section": True,
            "max_length": 500
        }
        
        result = await query_generator.generate_query(sample_analysis, site_prefs)
        
        assert result is not None
        assert result["language"] == "en"
        assert "thread_id" in result
    
    @pytest.mark.asyncio
    async def test_generate_query_different_categories(self, query_generator):
        """Test query generation for different categories."""
        categories = ["missing_data", "adverse_event", "protocol_deviation"]
        
        for category in categories:
            analysis = {
                "category": category,
                "severity": "major",
                "subject_id": "TEST001",
                "visit": "Baseline",
                "field_name": "Test Field",
                "description": f"Test {category} issue"
            }
            
            result = await query_generator.generate_query(analysis)
            assert result["category"] == category
    
    @pytest.mark.asyncio
    async def test_batch_query_generation(self, query_generator):
        """Test batch query generation."""
        analyses = [
            {
                "category": "missing_data",
                "subject_id": "SUBJ001",
                "visit": "Week 2",
                "field_name": "Blood Pressure"
            },
            {
                "category": "data_discrepancy",
                "subject_id": "SUBJ002",
                "visit": "Week 4",
                "field_name": "Weight"
            }
        ]
        
        results = await query_generator.generate_batch_queries(analyses)
        
        assert len(results) == 2
        assert all("query_text" in r for r in results)
        assert results[0]["category"] == "missing_data"
        assert results[1]["category"] == "data_discrepancy"
    
    def test_preview_query_with_template(self, query_generator):
        """Test query preview using templates."""
        analysis = {
            "category": "missing_data",
            "site_name": "Test Hospital",
            "field_name": "Blood Pressure",
            "subject_id": "SUBJ001",
            "visit": "Week 4",
            "visit_date": "2025-01-29",
            "reason": "primary endpoint assessment"
        }
        
        preview = query_generator.preview_query(analysis)
        
        assert "Test Hospital" in preview
        assert "SUBJ001" in preview
        assert "Blood Pressure" in preview
        assert "Week 4" in preview
    
    def test_preview_query_missing_fields(self, query_generator):
        """Test query preview with missing required fields."""
        analysis = {
            "category": "missing_data",
            "subject_id": "SUBJ001"
            # Missing other required fields
        }
        
        preview = query_generator.preview_query(analysis)
        
        assert "Template requires fields" in preview
    
    def test_validate_query_valid(self, query_generator):
        """Test query validation for valid query."""
        valid_query = """Dear Site Memorial Hospital,

We have identified a discrepancy in the Hemoglobin value for Subject SUBJ001 at Week 4 visit:

- EDC Value: 12.5 g/dL
- Source Document Value: 11.2 g/dL

Please verify the correct value and update the EDC accordingly, or provide clarification for the discrepancy.

This is required per protocol section 7.2 and ICH-GCP guidelines.

Thank you for your cooperation."""
        
        validation = query_generator.validate_query(valid_query)
        
        assert validation["valid"] is True
        assert len(validation["issues"]) == 0
        assert validation["word_count"] > 50
    
    def test_validate_query_too_short(self, query_generator):
        """Test query validation for too short query."""
        short_query = "Please fix the data."
        
        validation = query_generator.validate_query(short_query)
        
        assert validation["valid"] is False
        assert "too short" in validation["issues"][0]
    
    def test_validate_query_missing_elements(self, query_generator):
        """Test query validation for missing required elements."""
        incomplete_query = """Hello,

There is a problem with the data for patient 001.

Thanks."""
        
        validation = query_generator.validate_query(incomplete_query)
        
        assert validation["valid"] is False
        assert any("Missing standard phrases" in issue for issue in validation["issues"])
        assert any("regulatory" in issue for issue in validation["issues"])
    
    def test_get_template_exists(self, query_generator):
        """Test retrieving existing template."""
        template = query_generator.get_template("data_discrepancy")
        
        assert template is not None
        assert isinstance(template, QueryTemplate)
        assert template.category == "data_discrepancy"
    
    def test_get_template_not_exists(self, query_generator):
        """Test retrieving non-existent template."""
        template = query_generator.get_template("non_existent")
        
        assert template is None
    
    @pytest.mark.asyncio
    async def test_generate_query_critical_severity(self, query_generator):
        """Test query generation for critical severity issues."""
        critical_analysis = {
            "category": "adverse_event",
            "severity": "critical",
            "subject_id": "SUBJ001",
            "visit": "Week 8",
            "field_name": "SAE",
            "description": "Serious adverse event reported",
            "event_type": "Myocardial Infarction",
            "event_date": "2025-01-28"
        }
        
        result = await query_generator.generate_query(critical_analysis)
        
        assert result["priority"] == "critical"
        assert "24 hours" in result.get("suggested_response_time", "")
    
    @pytest.mark.asyncio
    async def test_multi_language_support(self, query_generator):
        """Test multi-language query generation."""
        languages = ["en", "es", "fr"]
        
        for lang in languages:
            result = await query_generator.generate_query(
                {"category": "missing_data", "subject_id": "TEST001"},
                language=lang
            )
            assert result["language"] == lang