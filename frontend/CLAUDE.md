# Frontend - React + Vite + Tailwind (from Lovable)

## Overview
The frontend is a React application built with Vite and Tailwind CSS, initially prototyped in Lovable.dev and then exported for production deployment on Railway.

## Architecture

### Tech Stack
- **Framework**: React 18
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **Deployment**: Railway with Caddy server
- **Prototyping**: Lovable.dev for rapid development

### Directory Structure

```
frontend/
├── src/
│   ├── components/      # Reusable UI components
│   │   ├── ui/         # Base UI components (buttons, inputs, etc.)
│   │   ├── layout/     # Layout components (header, sidebar, etc.)
│   │   └── features/   # Feature-specific components
│   ├── pages/          # Route-based page components
│   │   ├── Dashboard.tsx
│   │   ├── Trials.tsx
│   │   ├── Analytics.tsx
│   │   └── Settings.tsx
│   ├── hooks/          # Custom React hooks
│   │   ├── useAgent.ts
│   │   ├── useTrials.ts
│   │   └── useAuth.ts
│   ├── services/       # API service functions
│   │   ├── api.ts      # Base API configuration
│   │   ├── agents.ts   # Agent-related API calls
│   │   └── trials.ts   # Trial management API calls
│   ├── utils/          # Utility functions
│   │   ├── constants.ts
│   │   ├── helpers.ts
│   │   └── types.ts
│   ├── styles/         # Global styles and Tailwind config
│   │   ├── globals.css
│   │   └── tailwind.css
│   ├── App.tsx         # Main application component
│   ├── main.tsx        # Application entry point
│   └── vite-env.d.ts   # Vite type definitions
├── public/             # Static assets
│   ├── index.html
│   ├── favicon.ico
│   └── assets/
├── tests/              # Frontend tests
│   ├── components/
│   ├── pages/
│   └── utils/
├── package.json        # Node dependencies and scripts
├── vite.config.ts      # Vite configuration
├── tailwind.config.js  # Tailwind configuration
├── tsconfig.json       # TypeScript configuration
├── Dockerfile          # Railway deployment
└── railway.toml        # Railway configuration
```

## Lovable Integration Workflow

### 1. Prototype in Lovable
- Use Lovable.dev to rapidly prototype features
- Describe functionality in natural language
- Iterate on UI/UX with visual editing
- Test core functionality and user flows

### 2. Export from Lovable
```bash
# Download project from Lovable
# Extract to temporary directory
# Copy relevant files to frontend/ directory
```

### 3. Production Setup
```bash
cd frontend
npm install
npm run dev
```

## Development Setup

### Local Development
```bash
cd frontend
npm install
npm run dev
```

### Environment Variables
```bash
# .env.local
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_TITLE="Clinical Trials Agent"
VITE_ENABLE_DEBUG=true
```

### Available Scripts
```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run preview      # Preview production build
npm run test         # Run tests
npm run lint         # Lint code
npm run type-check   # TypeScript type checking
```

## Key Components

### Layout Components
- `Header`: Navigation and user menu
- `Sidebar`: Main navigation menu
- `Layout`: Main application layout wrapper

### Feature Components
- `AgentChat`: AI agent interaction interface
-`TrialManager`: Clinical trial management interface
- `Dashboard`: Main dashboard with KPIs and summaries
- `Analytics`: Data visualization and reporting

### UI Components (Tailwind-based)
- `Button`: Standardized button components
- `Input`: Form input components
- `Modal`: Modal dialog components
- `Table`: Data table components
- `Card`: Content card components

## API Integration

### Service Layer Pattern
```typescript
// services/api.ts
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

export const apiClient = {
  get: (endpoint: string) => fetch(`${API_BASE_URL}${endpoint}`),
  post: (endpoint: string, data: any) => 
    fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    })
};
```

### Custom Hooks
```typescript
// hooks/useAgent.ts
export const useAgent = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [response, setResponse] = useState(null);
  
  const sendMessage = async (message: string) => {
    setIsLoading(true);
    try {
      const result = await agentService.chat(message);
      setResponse(result);
    } finally {
      setIsLoading(false);
    }
  };
  
  return { sendMessage, response, isLoading };
};
```

## Railway Deployment

### Dockerfile Configuration
```dockerfile
FROM node:18-alpine as builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM caddy:alpine
COPY --from=builder /app/dist /srv
COPY Caddyfile /etc/caddy/Caddyfile
EXPOSE 80
```

### Caddyfile
```
:80 {
    root * /srv
    try_files {path} /index.html
    file_server
}
```

### Railway Configuration (railway.toml)
```toml
[build]
builder = "DOCKERFILE"

[deploy]
startCommand = "caddy run --config /etc/caddy/Caddyfile"
healthcheckPath = "/"
healthcheckTimeout = 100
```

## Dependencies (package.json)
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.8.0",
    "@tanstack/react-query": "^4.24.0",
    "axios": "^1.3.0",
    "clsx": "^1.2.1",
    "tailwind-merge": "^1.10.0"
  },
  "devDependencies": {
    "@types/react": "^18.0.27",
    "@types/react-dom": "^18.0.10",
    "@vitejs/plugin-react": "^3.1.0",
    "vite": "^4.1.0",
    "typescript": "^4.9.4",
    "tailwindcss": "^3.2.6",
    "autoprefixer": "^10.4.13",
    "postcss": "^8.4.21"
  }
}
```

## Styling with Tailwind

### Configuration
- Custom color palette for clinical trials theme
- Responsive design patterns
- Component-specific utility classes
- Dark mode support (if needed)

### Best Practices
- Use Tailwind utility classes for styling
- Create component variants using clsx/tailwind-merge
- Maintain consistent spacing and typography
- Follow accessibility guidelines

## Testing Strategy
- Unit tests for components using React Testing Library
- Integration tests for API interactions
- E2E tests for critical user flows
- Visual regression testing for UI consistency