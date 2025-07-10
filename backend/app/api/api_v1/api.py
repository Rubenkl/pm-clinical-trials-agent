"""Main API router for v1 endpoints."""

from fastapi import APIRouter

from app.api.endpoints.agents import agents_router
from app.api.endpoints.test_data import router as test_data_router
from app.api.endpoints.queries import router as queries_router
from app.api.endpoints.sdv import router as sdv_router
from app.api.endpoints.deviations import router as deviations_router
from app.api.endpoints.dashboard import router as dashboard_router


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

# Include query management endpoints
api_router.include_router(
    queries_router,
    prefix="/queries",
    tags=["queries"]
)

# Include SDV endpoints
api_router.include_router(
    sdv_router,
    prefix="/sdv",
    tags=["sdv"]
)

# Include deviation detection endpoints
api_router.include_router(
    deviations_router,
    prefix="/deviations",
    tags=["deviations"]
)

# Include dashboard metrics endpoints
api_router.include_router(
    dashboard_router,
    prefix="/dashboard",
    tags=["dashboard"]
)