"""
Deployment readiness tests - Simulate deployment environment
These tests catch issues that only show up in production/Railway
"""

import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))


class TestDeploymentReadiness:
    """Test deployment-specific issues"""

    def test_uvicorn_app_loading(self):
        """Test that uvicorn can load the app (simulates Railway startup)"""
        try:
            # Import the app as uvicorn would
            from app.main import app

            # Check it's a FastAPI app
            assert hasattr(app, "routes")
            assert hasattr(app, "openapi")

        except ImportError as e:
            pytest.fail(f"uvicorn cannot load app: {e}")

    def test_environment_variables(self):
        """Test required environment variables"""
        # Simulate Railway environment
        test_env = {
            "OPENAI_API_KEY": "test-key",
            "PORT": "8000",
            "USE_TEST_DATA": "true",
        }

        # Test config loading with environment
        original_env = {}
        try:
            # Backup original environment
            for key in test_env:
                original_env[key] = os.environ.get(key)
                os.environ[key] = test_env[key]

            # Import and test config
            from app.core.config import settings

            assert settings.openai_api_key == "test-key"

        finally:
            # Restore environment
            for key, value in original_env.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value

    def test_health_endpoint_accessibility(self):
        """Test health endpoint can be accessed"""
        try:
            from app.api.endpoints.health import health_check
            from app.core.config import settings

            # Call health check
            result = health_check()
            assert result is not None
            assert isinstance(result, dict)

        except Exception as e:
            pytest.fail(f"Health endpoint not accessible: {e}")

    def test_api_router_registration(self):
        """Test all API routers are properly registered"""
        try:
            from app.main import app

            # Check routes are registered
            routes = [route.path for route in app.routes]

            # Key endpoints that should exist
            expected_paths = ["/health", "/api/v1/agents/chat", "/api/v1/agents/status"]

            for path in expected_paths:
                assert any(path in route for route in routes), f"Missing route: {path}"

        except Exception as e:
            pytest.fail(f"API router registration failed: {e}")

    def test_dependency_injection(self):
        """Test FastAPI dependency injection works"""
        try:
            from app.api.dependencies import get_portfolio_manager

            # Test dependency can be resolved
            pm = get_portfolio_manager()
            assert pm is not None

        except Exception as e:
            pytest.fail(f"Dependency injection failed: {e}")

    def test_openai_sdk_import(self):
        """Test OpenAI SDK imports (critical for agents)"""
        try:
            # Test the specific import that agents use
            from agents import Agent, Runner, function_tool

            assert Agent is not None
            assert function_tool is not None
            assert Runner is not None

        except ImportError as e:
            pytest.fail(f"OpenAI SDK import failed: {e}")

    def test_synthetic_data_availability(self):
        """Test synthetic data can be generated"""
        try:
            from app.services.test_data_service import TestDataService

            service = TestDataService()
            status = service.get_status()
            assert status["available"] is True

        except Exception as e:
            pytest.fail(f"Test data service failed: {e}")


class TestProductionSimulation:
    """Simulate production environment conditions"""

    def test_concurrent_agent_access(self):
        """Test multiple agents can be accessed simultaneously"""
        try:
            from app.agents.data_verifier import DataVerifier
            from app.agents.portfolio_manager import PortfolioManager
            from app.agents.query_analyzer import QueryAnalyzer

            # Create multiple agents (simulates concurrent requests)
            pm1 = PortfolioManager()
            pm2 = PortfolioManager()
            qa = QueryAnalyzer()
            dv = DataVerifier()

            assert all([pm1, pm2, qa, dv])

        except Exception as e:
            pytest.fail(f"Concurrent agent access failed: {e}")

    def test_memory_usage_reasonable(self):
        """Test app doesn't use excessive memory on import"""
        import tracemalloc

        tracemalloc.start()

        try:
            # Import the full application
            from app.agents.portfolio_manager import PortfolioManager
            from app.main import app

            # Create some agents
            pm = PortfolioManager()

            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()

            # Memory should be reasonable (less than 100MB)
            assert (
                current < 100 * 1024 * 1024
            ), f"Memory usage too high: {current / 1024 / 1024:.2f} MB"

        except Exception as e:
            pytest.fail(f"Memory usage test failed: {e}")


# Test runner for direct execution
if __name__ == "__main__":
    # Run tests and report results
    import subprocess

    print("🚀 Running Deployment Readiness Tests...")
    result = subprocess.run(
        [sys.executable, "-m", "pytest", __file__, "-v", "--tb=short"],
        capture_output=True,
        text=True,
    )

    print("RESULTS:")
    print(result.stdout)
    if result.stderr:
        print("ERRORS:")
        print(result.stderr)

    if result.returncode == 0:
        print("✅ All deployment readiness tests PASSED")
    else:
        print("❌ Deployment readiness tests FAILED")
        sys.exit(1)
