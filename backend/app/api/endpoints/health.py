"""Health check endpoints."""

from fastapi import APIRouter, Depends, status
from datetime import datetime
from typing import Dict, Any

from app.api.models.agent_models import HealthCheckResponse
from app.api.dependencies import get_system_health_checker, get_current_settings
from app.core.config import Settings


health_router = APIRouter()


@health_router.get("/health", response_model=Dict[str, Any])
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "0.1.0",
        "message": "Clinical Trials Agent API is operational"
    }


@health_router.get(
    "/health/detailed",
    response_model=HealthCheckResponse,
    responses={
        200: {"description": "System is healthy"},
        503: {"description": "System is unhealthy"}
    }
)
async def detailed_health_check(
    settings: Settings = Depends(get_current_settings),
    health_checker = Depends(get_system_health_checker)
):
    """Detailed health check with service status."""
    from fastapi import Response
    
    health_data = await health_checker()
    
    response_data = HealthCheckResponse(
        status=health_data["status"],
        timestamp=datetime.now(),
        version="0.1.0",
        services=health_data["services"]
    )
    
    # Return appropriate status code based on health
    if health_data["status"] == "unhealthy":
        return Response(
            content=response_data.model_dump_json(),
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            media_type="application/json"
        )
    
    return response_data


async def check_database_health() -> Dict[str, Any]:
    """Check database health."""
    # TODO: Implement actual database health check
    # For now, return healthy status
    return {
        "status": "healthy",
        "response_time": 0.05,
        "connection_pool": "active"
    }


async def check_redis_health() -> Dict[str, Any]:
    """Check Redis health."""
    # TODO: Implement actual Redis health check
    # For now, return healthy status
    return {
        "status": "healthy",
        "response_time": 0.02,
        "memory_usage": "45MB"
    }


async def check_agents_health() -> Dict[str, Any]:
    """Check agents health."""
    # TODO: Implement actual agents health check
    # For now, return healthy status
    return {
        "status": "healthy",
        "active_agents": 2,
        "total_agents": 2
    }