# PM Clinical Trials Agent

A comprehensive clinical trials management system combining product management workflows with AI-powered backend services and modern frontend interface.

## 🏗️ Project Structure

```
pm-clinical-trials-agent/
├── product-management/     # Product management documentation
├── research/              # External research and analysis  
├── backend/               # FastAPI + OpenAI agents
├── frontend/              # React + Vite + Tailwind
├── shared/                # Common types and documentation
└── deployment/            # Railway deployment configs
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Railway CLI
- OpenAI API key

### Development Setup

1. **Clone and setup**
   ```bash
   git clone <repository-url>
   cd pm-clinical-trials-agent
   ```

2. **Backend setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   cp .env.example .env  # Configure your environment variables
   uvicorn app.main:app --reload
   ```

3. **Frontend setup**
   ```bash
   cd frontend
   npm install
   cp .env.example .env.local  # Configure your environment variables
   npm run dev
   ```

## 🛠️ Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **OpenAI Agents**: Multi-agent orchestrator system
- **PostgreSQL**: Database (Railway managed)
- **Hypercorn**: ASGI server for production

### Frontend  
- **React 18**: UI framework
- **Vite**: Build tool and development server
- **Tailwind CSS**: Utility-first CSS framework
- **Lovable.dev**: Rapid prototyping platform

### Deployment
- **Railway.app**: Cloud deployment platform
- **Docker**: Containerization
- **Caddy**: Web server for frontend

## 📋 Product Management Workflow

The project includes comprehensive product management documentation:

- **PRDs**: Product Requirements Documents
- **Roadmaps**: Product timelines and milestones  
- **User Stories**: Feature specifications and acceptance criteria
- **Presentations**: Reveal.js presentations for stakeholders
- **Research**: Market analysis and external sources

## 🤖 AI Agent System

The backend implements a multi-agent orchestrator with specialized agents:

- **Clinical Agent**: Clinical trials protocols and regulations
- **Data Agent**: Data analysis and reporting
- **Workflow Agent**: Project management and task coordination

## 🚢 Deployment

Deploy to Railway.app with separate services:

```bash
# Deploy backend
cd backend && railway up

# Deploy frontend  
cd frontend && railway up
```

See `deployment/CLAUDE.md` for detailed deployment instructions.

## 📚 Documentation

Each major component has detailed documentation:

- [`CLAUDE.md`](./CLAUDE.md) - Project overview and setup
- [`product-management/CLAUDE.md`](./product-management/CLAUDE.md) - PM workflows and templates
- [`backend/CLAUDE.md`](./backend/CLAUDE.md) - API and agent architecture  
- [`frontend/CLAUDE.md`](./frontend/CLAUDE.md) - UI components and Lovable integration
- [`deployment/CLAUDE.md`](./deployment/CLAUDE.md) - Railway deployment guide

## 🧪 Development Commands

### Backend
```bash
cd backend
uvicorn app.main:app --reload    # Start development server
pytest                          # Run tests
python -m pytest --cov=app     # Run tests with coverage
```

### Frontend  
```bash
cd frontend
npm run dev        # Start development server
npm run build      # Build for production
npm run test       # Run tests
npm run lint       # Lint code
```

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📞 Support

For questions or support, please check the documentation in each component's `CLAUDE.md` file or create an issue in the repository.