"""Main API router for v1 endpoints."""

from fastapi import APIRouter

from app.api.endpoints.agents import agents_router
from app.api.endpoints.test_data import router as test_data_router


api_router = APIRouter()

# Include agent endpoints
api_router.include_router(
    agents_router,
    prefix="/agents",
    tags=["agents"]
)

# Include test data endpoints
api_router.include_router(
    test_data_router,
    prefix="/test-data",
    tags=["test-data"]
)