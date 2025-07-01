"""
Import validation tests - Critical for catching deployment failures
These tests ensure all modules can be imported successfully
"""
import pytest
import sys
from pathlib import Path

# Add backend to path for testing
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

class TestImports:
    """Test all critical imports that could break deployment"""
    
    def test_core_config_import(self):
        """Test core configuration imports"""
        try:
            from app.core.config import settings
            assert settings is not None
        except ImportError as e:
            pytest.fail(f"Failed to import core config: {e}")
    
    def test_portfolio_manager_imports(self):
        """Test Portfolio Manager and related imports"""
        try:
            from app.agents.portfolio_manager import PortfolioManager, WorkflowRequest, WorkflowContext
            assert PortfolioManager is not None
            assert WorkflowRequest is not None
            assert WorkflowContext is not None
        except ImportError as e:
            pytest.fail(f"Failed to import Portfolio Manager components: {e}")
    
    def test_base_agent_imports(self):
        """Test base agent imports"""
        try:
            from app.agents.base_agent import BaseAgent, AgentResponse
            assert BaseAgent is not None
            assert AgentResponse is not None
        except ImportError as e:
            pytest.fail(f"Failed to import base agent components: {e}")
    
    def test_api_endpoints_import(self):
        """Test API endpoint imports - This catches the specific deployment failure"""
        try:
            from app.api.endpoints.agents import agents_router
            assert agents_router is not None
        except ImportError as e:
            pytest.fail(f"Failed to import agents endpoint: {e}")
    
    def test_health_endpoint_import(self):
        """Test health endpoint imports"""
        try:
            from app.api.endpoints.health import health_router
            assert health_router is not None
        except ImportError as e:
            pytest.fail(f"Failed to import health endpoint: {e}")
    
    def test_main_app_import(self):
        """Test main FastAPI app import - Critical for uvicorn startup"""
        try:
            from app.main import app
            assert app is not None
        except ImportError as e:
            pytest.fail(f"Failed to import main app: {e}")
    
    def test_all_agent_imports(self):
        """Test all agent imports to catch missing dependencies"""
        agents = [
            ("app.agents.query_analyzer", "QueryAnalyzer"),
            ("app.agents.data_verifier", "DataVerifier"), 
            ("app.agents.query_generator", "QueryGenerator"),
            ("app.agents.query_tracker", "QueryTracker"),
        ]
        
        for module_name, class_name in agents:
            try:
                module = __import__(module_name, fromlist=[class_name])
                agent_class = getattr(module, class_name)
                assert agent_class is not None
            except (ImportError, AttributeError) as e:
                pytest.fail(f"Failed to import {class_name} from {module_name}: {e}")
    
    def test_pydantic_models_import(self):
        """Test Pydantic model imports"""
        try:
            from app.api.models.agent_models import ChatRequest, ChatResponse
            assert ChatRequest is not None
            assert ChatResponse is not None
        except ImportError as e:
            pytest.fail(f"Failed to import API models: {e}")

class TestInstantiation:
    """Test that classes can be instantiated (deeper validation)"""
    
    def test_portfolio_manager_instantiation(self):
        """Test Portfolio Manager can be created"""
        try:
            from app.agents.portfolio_manager import PortfolioManager
            pm = PortfolioManager()
            assert pm is not None
        except Exception as e:
            pytest.fail(f"Failed to instantiate Portfolio Manager: {e}")
    
    def test_workflow_request_validation(self):
        """Test WorkflowRequest validation"""
        try:
            from app.agents.portfolio_manager import WorkflowRequest
            
            # Valid request
            request = WorkflowRequest(
                workflow_id="test_001",
                workflow_type="query_resolution",
                description="Test workflow",
                input_data={"test": "data"}
            )
            assert request.workflow_id == "test_001"
            
            # Invalid request should raise validation error
            with pytest.raises(Exception):
                WorkflowRequest()  # Missing required fields
                
        except Exception as e:
            pytest.fail(f"WorkflowRequest validation failed: {e}")

# Test all imports when file is run directly
if __name__ == "__main__":
    import subprocess
    result = subprocess.run([sys.executable, "-m", "pytest", __file__, "-v"], 
                          capture_output=True, text=True)
    print("STDOUT:")
    print(result.stdout)
    print("STDERR:")
    print(result.stderr)
    print(f"Return code: {result.returncode}")