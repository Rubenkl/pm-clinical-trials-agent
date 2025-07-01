#!/usr/bin/env python3
"""Verify that the Clinical Trials Agent system is properly set up."""

import sys
import os
from pathlib import Path

def check_environment():
    """Check environment configuration."""
    print("🔍 Checking Environment Configuration...")
    
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_example.exists():
        print("❌ .env.example file missing")
        return False
    else:
        print("✅ .env.example file exists")
    
    if not env_file.exists():
        print("⚠️  .env file not found - you need to copy .env.example to .env and configure your API key")
        return False
    else:
        print("✅ .env file exists")
        
        # Check for API key
        try:
            from app.core.config import get_settings
            settings = get_settings()
            if not settings.openai_api_key or settings.openai_api_key == "sk-your-openai-api-key-here":
                print("⚠️  OPENAI_API_KEY not configured in .env file")
                return False
            else:
                print("✅ OpenAI API key is configured")
        except Exception as e:
            print(f"❌ Error loading configuration: {e}")
            return False
    
    return True

def check_dependencies():
    """Check that all required dependencies are installed."""
    print("\n🔍 Checking Dependencies...")
    
    try:
        from agents import Agent, function_tool, Runner
        print("✅ OpenAI Agents SDK installed correctly")
    except ImportError as e:
        print(f"❌ OpenAI Agents SDK not installed: {e}")
        print("   Run: pip install openai-agents")
        return False
    
    try:
        import fastapi
        import uvicorn
        import pydantic
        print("✅ FastAPI and dependencies installed")
    except ImportError as e:
        print(f"❌ FastAPI dependencies missing: {e}")
        print("   Run: pip install -r requirements.txt")
        return False
    
    return True

def check_agents():
    """Check that all agents are working."""
    print("\n🔍 Checking Agents...")
    
    try:
        from app.agents.portfolio_manager import PortfolioManager
        from app.agents.query_analyzer import QueryAnalyzer
        from app.agents.data_verifier import DataVerifier
        from app.agents.query_generator import QueryGenerator
        from app.agents.query_tracker import QueryTracker
        
        agents = [
            ("Portfolio Manager", PortfolioManager(), 5),
            ("Query Analyzer", QueryAnalyzer(), 5),
            ("Data Verifier", DataVerifier(), 6),
            ("Query Generator", QueryGenerator(), 3),
            ("Query Tracker", QueryTracker(), 4)
        ]
        
        total_tools = 0
        for name, agent, expected_tools in agents:
            actual_tools = len(agent.agent.tools)
            total_tools += actual_tools
            if actual_tools == expected_tools:
                print(f"✅ {name}: {actual_tools} tools")
            else:
                print(f"❌ {name}: {actual_tools} tools (expected {expected_tools})")
                return False
        
        print(f"✅ Total system: {total_tools} function tools")
        return True
        
    except Exception as e:
        print(f"❌ Error loading agents: {e}")
        return False

def check_tests():
    """Check that key tests can run."""
    print("\n🔍 Checking Tests...")
    
    try:
        from tests.test_sdk_integration import TestSDKIntegration
        test_instance = TestSDKIntegration()
        
        from app.agents.portfolio_manager import PortfolioManager
        from app.agents.query_analyzer import QueryAnalyzer
        from app.agents.data_verifier import DataVerifier
        from app.agents.query_generator import QueryGenerator
        from app.agents.query_tracker import QueryTracker
        
        pm = PortfolioManager()
        qa = QueryAnalyzer()
        dv = DataVerifier()
        qg = QueryGenerator()
        qt = QueryTracker()
        
        # Run key tests
        test_instance.test_all_agents_initialized(pm, qa, dv, qg, qt)
        test_instance.test_openai_agents_sdk_function_tools(pm, qa, dv, qg, qt)
        
        print("✅ Key integration tests pass")
        return True
        
    except Exception as e:
        print(f"❌ Test errors: {e}")
        return False

def main():
    """Run all verification checks."""
    print("🚀 Clinical Trials Agent - System Verification")
    print("=" * 55)
    
    checks = [
        ("Environment Configuration", check_environment),
        ("Dependencies", check_dependencies),
        ("Agents", check_agents),
        ("Tests", check_tests)
    ]
    
    all_passed = True
    for check_name, check_func in checks:
        if not check_func():
            all_passed = False
    
    print("\n" + "=" * 55)
    if all_passed:
        print("🎉 ALL CHECKS PASSED!")
        print("✅ Your Clinical Trials Agent system is ready!")
        print("\n📋 Next Steps:")
        print("   1. Configure your OpenAI API key in .env file")
        print("   2. Run: uvicorn app.main:app --reload")
        print("   3. Visit: http://localhost:8000/docs")
    else:
        print("❌ SOME CHECKS FAILED")
        print("📋 Please address the issues above before proceeding")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())