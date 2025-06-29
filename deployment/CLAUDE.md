# Deployment Guide - Railway.app

## Overview
This project deploys as separate services on Railway.app: a FastAPI backend and a React frontend. This guide covers the complete deployment process from development to production.

## Railway Architecture

### Service Structure
- **Backend Service**: FastAPI with OpenAI agents
- **Frontend Service**: React app served with Caddy
- **Database Service**: PostgreSQL (optional, if needed)

### Domain Configuration
- **Frontend**: `yourdomain.com`
- **Backend**: `api.yourdomain.com`
- **Database**: Internal Railway network only

## Prerequisites

### 1. Railway Account Setup
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login
```

### 2. Environment Variables
Create `.env` files for local development and configure Railway variables:

#### Backend Environment Variables
```bash
# Required
OPENAI_API_KEY=sk-...
DATABASE_URL=postgresql://user:pass@host:port/dbname
PORT=8000

# Optional
DEBUG=false
CORS_ORIGINS=https://yourdomain.com
MAX_WORKERS=4
```

#### Frontend Environment Variables
```bash
# Required
VITE_API_BASE_URL=https://api.yourdomain.com

# Optional
VITE_APP_TITLE="Clinical Trials Agent"
VITE_ENABLE_DEBUG=false
```

## Deployment Process

### 1. Backend Deployment

#### Step 1: Create Backend Service
```bash
cd backend
railway init
railway add
# Select "Empty Service"
# Name: "clinical-trials-backend"
```

#### Step 2: Configure Backend Service
```bash
# Set environment variables
railway variables set OPENAI_API_KEY=your_key_here
railway variables set PORT=8000

# Deploy
railway up
```

#### Step 3: Configure Domain
1. Go to Railway dashboard
2. Select backend service
3. Go to Settings > Networking
4. Generate domain or add custom domain
5. Set as `api.yourdomain.com`

### 2. Frontend Deployment

#### Step 1: Create Frontend Service
```bash
cd frontend
railway init
railway add
# Select "Empty Service"
# Name: "clinical-trials-frontend"
```

#### Step 2: Configure Frontend Service
```bash
# Set environment variables
railway variables set VITE_API_BASE_URL=https://api.yourdomain.com

# Deploy
railway up
```

#### Step 3: Configure Domain
1. Go to Railway dashboard
2. Select frontend service
3. Go to Settings > Networking
4. Generate domain or add custom domain
5. Set as `yourdomain.com`

### 3. Database Setup (if needed)

#### Step 1: Add PostgreSQL Service
```bash
railway add
# Select "PostgreSQL"
```

#### Step 2: Connect Database
```bash
# Get database URL from Railway dashboard
# Add to backend environment variables
railway variables set DATABASE_URL=postgresql://...
```

## Configuration Files

### Backend Configuration

#### `backend/railway.toml`
```toml
[build]
builder = "DOCKERFILE"

[deploy]
startCommand = "hypercorn app.main:app --bind 0.0.0.0:$PORT"
healthcheckPath = "/health"
healthcheckTimeout = 100
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10

[env]
PORT = "8000"
```

#### `backend/Dockerfile`
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE $PORT

# Start application
CMD ["hypercorn", "app.main:app", "--bind", "0.0.0.0:$PORT"]
```

### Frontend Configuration

#### `frontend/railway.toml`
```toml
[build]
builder = "DOCKERFILE"

[deploy]
startCommand = "caddy run --config /etc/caddy/Caddyfile"
healthcheckPath = "/"
healthcheckTimeout = 100
```

#### `frontend/Dockerfile`
```dockerfile
# Build stage
FROM node:18-alpine as builder

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci --only=production

# Copy source code
COPY . .

# Build application
RUN npm run build

# Production stage
FROM caddy:alpine

# Copy built application
COPY --from=builder /app/dist /srv

# Copy Caddy configuration
COPY Caddyfile /etc/caddy/Caddyfile

# Expose port
EXPOSE 80

# Start Caddy
CMD ["caddy", "run", "--config", "/etc/caddy/Caddyfile"]
```

#### `frontend/Caddyfile`
```
:80 {
    root * /srv
    
    # Handle client-side routing
    try_files {path} /index.html
    
    # Enable file server
    file_server
    
    # Enable gzip compression
    encode gzip
    
    # Security headers
    header {
        X-Content-Type-Options nosniff
        X-Frame-Options DENY
        X-XSS-Protection "1; mode=block"
    }
}
```

## Deployment Scripts

### `deployment/scripts/deploy-backend.sh`
```bash
#!/bin/bash
set -e

echo "Deploying backend to Railway..."

cd backend

# Install dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/ -v

# Deploy to Railway
railway up

echo "Backend deployment complete!"
```

### `deployment/scripts/deploy-frontend.sh`
```bash
#!/bin/bash
set -e

echo "Deploying frontend to Railway..."

cd frontend

# Install dependencies
npm ci

# Run tests
npm run test

# Build application
npm run build

# Deploy to Railway
railway up

echo "Frontend deployment complete!"
```

### `deployment/scripts/deploy-all.sh`
```bash
#!/bin/bash
set -e

echo "Deploying full application to Railway..."

# Deploy backend
./deployment/scripts/deploy-backend.sh

# Deploy frontend
./deployment/scripts/deploy-frontend.sh

echo "Full deployment complete!"
echo "Frontend: https://yourdomain.com"
echo "Backend: https://api.yourdomain.com"
```

## Environment Management

### Development
```bash
# Start backend
cd backend && uvicorn app.main:app --reload

# Start frontend
cd frontend && npm run dev
```

### Staging/Production
```bash
# Deploy to Railway
railway up

# Check deployment status
railway status

# View logs
railway logs
```

## Monitoring and Troubleshooting

### Health Checks
- Backend: `https://api.yourdomain.com/health`
- Frontend: `https://yourdomain.com` (returns 200 for index.html)

### Log Access
```bash
# View backend logs
railway logs --service clinical-trials-backend

# View frontend logs
railway logs --service clinical-trials-frontend

# Follow logs in real-time
railway logs --follow
```

### Common Issues

#### CORS Errors
- Ensure `CORS_ORIGINS` includes frontend domain
- Check that domains are properly configured

#### API Connection Issues
- Verify `VITE_API_BASE_URL` points to correct backend domain
- Check network connectivity between services

#### Build Failures
- Check that all environment variables are set
- Verify Docker builds work locally
- Review Railway build logs

## Security Considerations

### Environment Variables
- Never commit secrets to repository
- Use Railway's secure variable storage
- Rotate API keys regularly

### Network Security
- Backend only accepts requests from frontend domain
- Database only accessible from Railway internal network
- Use HTTPS for all external communications

### Access Control
- Limit Railway project access to necessary team members
- Use principle of least privilege for service permissions
- Regular security audits of deployed services