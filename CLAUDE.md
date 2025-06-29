# Behavior
- Always use Test-driven development. Which means you need to plan first and check best practices online, create tests, make sure all tests fail, then write functionality, and keep iterating until the tests pass (but do not change the tests). Then, you can consider the task done
- After updating the functionality, check if you can update each CLAUDE.md file so you are better informed later on.
- Feel free to make use of a scratchpad if you feel so. 


# PM Clinical Trials Agent

## Project Overview

This project is a comprehensive clinical trials management system that combines product management workflows with AI-powered backend services and a modern frontend interface.

## Architecture

### Tech Stack
- **Backend**: FastAPI with OpenAI multi-agent orchestrator
- **Frontend**: React + Vite + Tailwind (initially prototyped in Lovable)
- **Deployment**: Railway.app for both frontend and backend
- **Presentations**: Reveal.js for all stakeholder presentations

### Project Structure

```
pm-clinical-trials-agent/
├── product-management/     # Product management documentation
│   ├── prds/              # Product Requirements Documents
│   ├── roadmaps/          # Product roadmaps and timelines
│   ├── user-stories/      # User stories and acceptance criteria
│   ├── metrics/           # KPIs and success metrics
│   ├── status-updates/    # Progress tracking and scratchpads
│   └── presentations/     # Reveal.js presentations
├── research/              # External research and analysis
├── backend/               # FastAPI + OpenAI agents
├── frontend/              # React application (from Lovable)
├── shared/                # Common types and documentation
└── deployment/            # Railway deployment configs
```

## Development Workflow

### Product Management
1. Research goes in `/research/` folder
2. PRDs and documentation in `/product-management/`
3. All presentations built with Reveal.js
4. Status updates and scratchpads in `/product-management/status-updates/`

### Development Process
1. **Frontend**: Prototype in Lovable.dev, then export to `/frontend/`
2. **Backend**: Build FastAPI with multi-agent orchestrator in `/backend/`
3. **Deployment**: Deploy both services separately on Railway

### Deployment Strategy
- **Frontend**: Deployed as React app with Caddy server on Railway
- **Backend**: Deployed as FastAPI with Hypercorn server on Railway
- **Database**: PostgreSQL on Railway (if needed)
- **Environment**: Separate services with proper domain configuration

## Key Commands

### Backend Development
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

### Deployment
```bash
# Deploy via Railway CLI
railway login
railway init
railway up
```

## Environment Variables

### Backend
- `PORT`: Railway-provided port
- `DATABASE_URL`: PostgreSQL connection string
- `OPENAI_API_KEY`: OpenAI API key for agents

### Frontend
- `VITE_API_BASE_URL`: Backend API URL
- `PORT`: Railway-provided port

## Notes
- This is a single product with multiple features
- All presentations use Reveal.js format
- External research separate from PM documentation
- Railway deployment with separate frontend/backend services