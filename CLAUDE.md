# Behavior
- Always use Test-driven development. Which means you need to plan first and check best practices online, create tests, make sure all tests fail, then write functionality, and keep iterating until the tests pass (but do not change the tests). Then, you can consider the task done
- After updating the functionality, check if you can update each CLAUDE.md file so you are better informed later on.
- Feel free to make use of a scratchpad if you feel so.
- **For Reveal.js Presentations**: Apply TDD by writing tests for content accuracy, interactive elements, performance, and accessibility BEFORE creating the presentation. See `/product-management/roadmaps/presentation-delivery-plan.md` for detailed TDD approach.

## IMPORTANT: Before Starting Any Work
1. **Check Project Plans First**: Always review the following documents in `/product-management/roadmaps/` before beginning any task:
   - `master-implementation-plan-2025.md` - Overall project timeline and phases
   - `backend-development-tasks.md` - Detailed backend task breakdown
   - `sprint-execution-plan.md` - Current sprint goals and priorities
   - `presentation-delivery-plan.md` - Presentation schedule and requirements

2. **Follow Sprint Goals**: Work should align with the current sprint's objectives as defined in the sprint execution plan

3. **Task Prioritization**: Use the priority matrix in backend-development-tasks.md to determine what to work on first

4. **Track Progress**: Update task completion status in the relevant sprint tracking 


# PM Clinical Trials Agent

## Project Overview

This project is a comprehensive clinical trials management system that combines product management workflows with AI-powered backend services and a modern frontend interface.

## Architecture

### Tech Stack
- **Backend**: FastAPI + OpenAI Agents SDK (handles multi-agent orchestration, state management, handoffs)
- **Frontend**: React + Vite + Tailwind (initially prototyped in Lovable)
- **AI Orchestration**: OpenAI Agents SDK with Portfolio Manager pattern
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
2. **Backend**: Lightweight FastAPI wrapper around OpenAI Agents SDK
3. **AI Agents**: Portfolio Manager + specialist agents using SDK's built-in orchestration
4. **Deployment**: Deploy both services separately on Railway

### Deployment Strategy
- **Frontend**: Deployed as React app with Caddy server on Railway
- **Backend**: Deployed as FastAPI with Hypercorn server on Railway
- **State Management**: SDK Context objects (in-memory + optional PostgreSQL for persistence)
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
- `OPENAI_API_KEY`: OpenAI API key for agents (required)
- `PORT`: Railway-provided port
- `DEBUG`: Enable debug mode (optional)
- `CORS_ORIGINS`: Allowed CORS origins (optional)

### Frontend
- `VITE_API_BASE_URL`: Backend API URL
- `PORT`: Railway-provided port

## Notes
- This is a single product with multiple features
- All presentations use Reveal.js format
- External research separate from PM documentation
- Railway deployment with separate frontend/backend services
- **OpenAI Agents SDK handles**: Multi-agent coordination, state management, handoffs, tracing
- **FastAPI provides**: Lightweight HTTP interface to the agent system
- **No complex database models**: State managed via SDK Context objects