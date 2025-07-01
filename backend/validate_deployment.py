#!/usr/bin/env python3
"""
Deployment Validation Script
Run this before deploying to catch import/configuration issues
"""
import sys
import os
import traceback
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

def test_critical_imports():
    """Test all critical imports that broke deployment"""
    print("🔍 Testing Critical Imports...")
    
    tests = [
        ("Core Config", "from app.core.config import settings"),
        ("Portfolio Manager", "from app.agents.portfolio_manager import PortfolioManager, WorkflowRequest"),
        ("Base Agent", "from app.agents.base_agent import BaseAgent, AgentResponse"),
        ("Agents Endpoint", "from app.api.endpoints.agents import agents_router"),
        ("Health Endpoint", "from app.api.endpoints.health import health_router"),
        ("Main App", "from app.main import app"),
        ("OpenAI SDK", "from agents import Agent, function_tool"),
    ]
    
    failed = []
    for name, import_stmt in tests:
        try:
            exec(import_stmt)
            print(f"  ✅ {name}")
        except Exception as e:
            print(f"  ❌ {name}: {e}")
            failed.append((name, str(e)))
    
    return failed

def test_app_instantiation():
    """Test app and agents can be created"""
    print("\n🏗️ Testing App Instantiation...")
    
    try:
        from app.main import app
        print("  ✅ FastAPI app created")
        
        from app.agents.portfolio_manager import PortfolioManager
        pm = PortfolioManager()
        print("  ✅ Portfolio Manager created")
        
        from app.agents.portfolio_manager import WorkflowRequest
        request = WorkflowRequest(
            workflow_id="test",
            workflow_type="test",
            description="test",
            input_data={}
        )
        print("  ✅ WorkflowRequest validation works")
        
        return []
        
    except Exception as e:
        print(f"  ❌ Instantiation failed: {e}")
        return [("Instantiation", str(e))]

def test_environment_config():
    """Test environment configuration"""
    print("\n⚙️ Testing Environment Config...")
    
    try:
        from app.core.config import settings
        
        # Check critical settings
        if not hasattr(settings, 'openai_api_key'):
            print("  ⚠️ OPENAI_API_KEY not configured")
        else:
            print("  ✅ OPENAI_API_KEY configured")
        
        print(f"  ✅ Debug mode: {getattr(settings, 'debug', 'Not set')}")
        print(f"  ✅ Use test data: {getattr(settings, 'use_test_data', 'Not set')}")
        
        return []
        
    except Exception as e:
        print(f"  ❌ Config failed: {e}")
        return [("Config", str(e))]

def test_routes():
    """Test API routes are registered"""
    print("\n🛣️ Testing API Routes...")
    
    try:
        from app.main import app
        
        routes = [route.path for route in app.routes]
        expected_routes = ['/health', '/api/v1/agents/chat', '/api/v1/agents/status']
        
        missing = []
        for route in expected_routes:
            if any(route in r for r in routes):
                print(f"  ✅ {route}")
            else:
                print(f"  ❌ Missing: {route}")
                missing.append(route)
        
        return [("Missing Routes", str(missing))] if missing else []
        
    except Exception as e:
        print(f"  ❌ Route testing failed: {e}")
        return [("Routes", str(e))]

def main():
    """Run all validation tests"""
    print("🚀 Railway Deployment Validation")
    print("=" * 50)
    
    all_failures = []
    
    # Run all tests
    all_failures.extend(test_critical_imports())
    all_failures.extend(test_app_instantiation())
    all_failures.extend(test_environment_config())
    all_failures.extend(test_routes())
    
    print("\n" + "=" * 50)
    
    if not all_failures:
        print("✅ ALL TESTS PASSED - Ready for deployment!")
        return 0
    else:
        print("❌ VALIDATION FAILED - Fix these issues before deploying:")
        for name, error in all_failures:
            print(f"  • {name}: {error}")
        return 1

if __name__ == "__main__":
    sys.exit(main())