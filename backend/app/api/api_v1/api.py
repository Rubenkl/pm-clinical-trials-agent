"""Main API router for v1 endpoints."""

from fastapi import APIRouter

# Clinical workflow endpoints (using Runner.run() directly)
from app.api.endpoints.clinical_workflows import router as workflows_router

# Test data endpoints for mock data
from app.api.endpoints.test_data import router as test_data_router

# Dashboard metrics
from app.api.endpoints.dashboard import router as dashboard_router


api_router = APIRouter()

# Clinical workflows - main agent functionality
api_router.include_router(
    workflows_router,
    prefix="/clinical",
    tags=["clinical-workflows"]
)

# Test data for frontend development
api_router.include_router(
    test_data_router,
    prefix="/test-data",
    tags=["test-data"]
)

# Dashboard metrics
api_router.include_router(
    dashboard_router,
    prefix="/dashboard",
    tags=["dashboard"]
)