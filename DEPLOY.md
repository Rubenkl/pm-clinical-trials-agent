# Railway Deployment Guide

## 🚀 Deploy to Railway (3 steps, 3 minutes)

### **Step 1: Push to GitHub**
```bash
git add .
git commit -m "Deploy to Railway"
git push origin main
```

### **Step 2: Deploy via Railway Dashboard**
1. Go to [railway.app](https://railway.app)
2. Click "Deploy Now" → "Deploy from GitHub repo"
3. Select repository: `pm-clinical-trials-agent`
4. Add environment variable: `OPENAI_API_KEY=sk-your-key-here`
5. Click "Deploy"

### **Step 3: Test Your System**
Railway gives you a URL like: `https://your-app.up.railway.app`

```bash
# Test immediately
curl https://your-app.up.railway.app/health
curl https://your-app.up.railway.app/api/v1/test-data/status

# Chat with agents
curl -X POST https://your-app.up.railway.app/api/v1/agents/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Show me subjects with critical discrepancies"}'

# View API docs
open https://your-app.up.railway.app/docs
```

## ✅ **What You Get**
- 5 AI agents with real OpenAI SDK
- 50 synthetic subjects with clinical data
- Complete API for testing
- No real clinical data needed
- Instant testing capability

**That's it! Your clinical trials AI system is live on Railway.**