"""
Import validation tests - Critical for catching deployment failures
These tests ensure all modules can be imported successfully
"""

import sys
from pathlib import Path

import pytest

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
            from app.agents_v2.portfolio_manager import (
                PortfolioManager,
                WorkflowContext,
            )

            assert PortfolioManager is not None
            assert WorkflowContext is not None
        except ImportError as e:
            pytest.fail(f"Failed to import Portfolio Manager components: {e}")

    def test_base_agent_imports(self):
        """Test base agent imports"""
        try:
            from app.agents_v2.data_verifier import DataVerifier
            from app.agents_v2.query_analyzer import QueryAnalyzer

            assert QueryAnalyzer is not None
            assert DataVerifier is not None
        except ImportError as e:
            pytest.fail(f"Failed to import agent components: {e}")

    def test_api_endpoints_import(self):
        """Test API endpoint imports - This catches the specific deployment failure"""
        try:
            from app.api.endpoints.clinical_workflows import router as clinical_router
            from app.api.endpoints.test_data import router as test_data_router

            assert clinical_router is not None
            assert test_data_router is not None
        except ImportError as e:
            pytest.fail(f"Failed to import API endpoints: {e}")

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
            ("app.agents_v2.query_analyzer", "QueryAnalyzer"),
            ("app.agents_v2.data_verifier", "DataVerifier"),
            ("app.agents_v2.query_generator", "QueryGenerator"),
            ("app.agents_v2.query_tracker", "QueryTracker"),
            ("app.agents_v2.deviation_detector", "DeviationDetector"),
            ("app.agents_v2.analytics_agent", "AnalyticsAgent"),
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
            from app.api.models.agent_models import (
                WorkflowExecutionRequest,
                WorkflowStatusRequest,
            )

            assert WorkflowExecutionRequest is not None
            assert WorkflowStatusRequest is not None
        except ImportError as e:
            pytest.fail(f"Failed to import API models: {e}")


class TestInstantiation:
    """Test that classes can be instantiated (deeper validation)"""

    def test_portfolio_manager_instantiation(self):
        """Test Portfolio Manager can be created"""
        try:
            from app.agents_v2.portfolio_manager import PortfolioManager

            pm = PortfolioManager()
            assert pm is not None
        except Exception as e:
            pytest.fail(f"Failed to instantiate Portfolio Manager: {e}")

    def test_workflow_context_validation(self):
        """Test WorkflowContext validation"""
        try:
            from app.agents_v2.portfolio_manager import WorkflowContext

            # Valid context
            context = WorkflowContext()
            assert context is not None
            assert hasattr(context, "active_workflows")
            assert hasattr(context, "completed_workflows")

        except Exception as e:
            pytest.fail(f"WorkflowContext validation failed: {e}")


# Test all imports when file is run directly
if __name__ == "__main__":
    import subprocess

    result = subprocess.run(
        [sys.executable, "-m", "pytest", __file__, "-v"], capture_output=True, text=True
    )
    print("STDOUT:")
    print(result.stdout)
    print("STDERR:")
    print(result.stderr)
    print(f"Return code: {result.returncode}")
