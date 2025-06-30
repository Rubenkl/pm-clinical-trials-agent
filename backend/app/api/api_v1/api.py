"""Main API router for v1 endpoints."""

from fastapi import APIRouter

from app.api.endpoints.agents import agents_router


api_router = APIRouter()

# Include agent endpoints
api_router.include_router(
    agents_router,
    prefix="/agents",
    tags=["agents"]
)