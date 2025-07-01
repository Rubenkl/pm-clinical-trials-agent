# 🚀 Clinical Trials Agent - Setup Guide

## ✅ Current System Status

You have a **fully functional multi-agent system** using the real OpenAI Agents SDK with:
- **5 specialized agents** (Portfolio Manager, Query Analyzer, Data Verifier, Query Generator, Query Tracker)
- **23 function tools** with proper string-based signatures
- **Pydantic context classes** for modern data validation
- **Complete test coverage** and documentation

## 📋 Required Setup Steps

### 1. **Set Up OpenAI API Key** (REQUIRED)

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your OpenAI API key
# Replace "sk-your-openai-api-key-here" with your actual key
OPENAI_API_KEY="sk-proj-xxxxxxxxxxxxx"
```

**Get your API key from**: https://platform.openai.com/api-keys

### 2. **Install Dependencies**

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install all dependencies including OpenAI Agents SDK
pip install -r requirements.txt
```

### 3. **Verify Installation**

```bash
# Test that OpenAI Agents SDK is installed correctly
python3 -c "from agents import Agent, function_tool, Runner; print('✅ OpenAI Agents SDK installed')"

# Test all agents are working
python3 -c "
from app.agents.portfolio_manager import PortfolioManager
from app.agents.query_analyzer import QueryAnalyzer
print('✅ All agents loading correctly')
"
```

### 4. **Run the Application**

```bash
# Start the FastAPI server
uvicorn app.main:app --reload --port 8000

# The API will be available at:
# - http://localhost:8000
# - API docs: http://localhost:8000/docs
```

## 🧹 Cleanup Tasks (Already Completed)

✅ **Old files removed**:
- `portfolio_manager_backup.py`
- `portfolio_manager_fixed.py`
- `portfolio_manager_simple.py`

✅ **Tests to keep** (already updated for SDK):
- `test_data_verifier_sdk.py`
- `test_portfolio_manager_sdk.py`
- `test_query_analyzer_sdk.py`
- `test_sdk_integration.py`

## 🔥 Quick Test After Setup

Once you have your API key configured, test the complete system:

```python
import asyncio
from app.agents.portfolio_manager import PortfolioManager

async def test_with_api():
    pm = PortfolioManager()
    
    # This will use the real OpenAI API
    workflow_request = {
        "workflow_id": "TEST_001",
        "workflow_type": "query_resolution",
        "description": "Test clinical data analysis",
        "input_data": {
            "subject_id": "SUBJ001",
            "hemoglobin": "12.5"
        }
    }
    
    result = await pm.orchestrate_workflow(workflow_request)
    print(f"Result: {result}")

# Run the test
asyncio.run(test_with_api())
```

## ⚠️ Important Notes

1. **API Costs**: Each agent call uses the OpenAI API. Monitor your usage at https://platform.openai.com/usage

2. **Model Selection**: Currently configured to use `gpt-4`. You can change this in `.env`:
   ```
   OPENAI_MODEL="gpt-4"  # or "gpt-3.5-turbo" for lower cost
   ```

3. **Rate Limits**: The system includes rate limiting (100 requests/minute by default)

4. **Mock Fallbacks**: The code includes mock fallbacks if the SDK isn't available, but with the SDK installed, these won't be used

## 🎯 Next Steps

1. **Test with Real Data**: Try the API endpoints with actual clinical trial data
2. **Monitor Performance**: Use the `/api/v1/agents/status` endpoint to monitor agent performance
3. **Deploy to Production**: Use Railway.app deployment as documented

## 📚 Resources

- **API Documentation**: `/backend/API_DOCUMENTATION.md`
- **Agent Details**: `/backend/CLAUDE.md`
- **OpenAI Agents SDK Docs**: https://platform.openai.com/docs/guides/agents-sdk

## ✨ You're Ready!

With your OpenAI API key configured, you have a production-ready clinical trials multi-agent system powered by the OpenAI Agents SDK!