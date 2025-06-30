"""API dependencies for dependency injection."""

from functools import lru_cache
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.config import Settings, get_settings
from app.agents.portfolio_manager import PortfolioManager
from app.agents.query_analyzer import QueryAnalyzer
from app.agents.data_verifier import DataVerifier


# Security
security = HTTPBearer(auto_error=False)


# Global agent instances
_portfolio_manager: Optional[PortfolioManager] = None
_query_analyzer: Optional[QueryAnalyzer] = None
_data_verifier: Optional[DataVerifier] = None


async def get_current_settings() -> Settings:
    """Get current application settings."""
    return get_settings()


def validate_openai_key(settings: Settings = Depends(get_current_settings)) -> bool:
    """Validate that OpenAI API key is configured."""
    if not settings.openai_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OpenAI API key not configured. Please set OPENAI_API_KEY environment variable."
        )
    return True


@lru_cache()
def get_portfolio_manager() -> PortfolioManager:
    """Get or create portfolio manager instance."""
    global _portfolio_manager
    
    if _portfolio_manager is None:
        _portfolio_manager = PortfolioManager()
    
    return _portfolio_manager


@lru_cache()
def get_query_analyzer() -> QueryAnalyzer:
    """Get or create query analyzer instance."""
    global _query_analyzer
    
    if _query_analyzer is None:
        _query_analyzer = QueryAnalyzer()
    
    return _query_analyzer


@lru_cache()
def get_data_verifier() -> DataVerifier:
    """Get or create data verifier instance."""
    global _data_verifier
    
    if _data_verifier is None:
        _data_verifier = DataVerifier()
    
    return _data_verifier


async def initialize_agent_system() -> None:
    """Initialize the agent system with all agents."""
    portfolio_manager = get_portfolio_manager()
    query_analyzer = get_query_analyzer()
    data_verifier = get_data_verifier()
    
    # Register agents with portfolio manager
    portfolio_manager.register_agent("query_analyzer", query_analyzer, ["data_analysis", "query_generation"])
    portfolio_manager.register_agent("data_verifier", data_verifier, ["data_verification", "quality_checks"])
    
    print("✅ Agent system initialized successfully")
    print(f"📊 Portfolio Manager: {portfolio_manager.agent_id}")
    print(f"🔍 Query Analyzer: {query_analyzer.agent_id}")
    print(f"✅ Data Verifier: {data_verifier.agent_id}")
    print(f"🤝 Registered agents: {portfolio_manager.get_available_agents()}")


async def cleanup_agent_system() -> None:
    """Clean up agent system resources."""
    global _portfolio_manager, _query_analyzer, _data_verifier
    
    if _portfolio_manager:
        # Clean up portfolio manager resources
        _portfolio_manager = None
    
    if _query_analyzer:
        # Clean up query analyzer resources
        _query_analyzer = None
    
    if _data_verifier:
        # Clean up data verifier resources
        _data_verifier = None
    
    print("🧹 Agent system cleaned up")


def get_agent_by_type(agent_type: str) -> object:
    """Get agent instance by type."""
    agent_map = {
        "portfolio-manager": get_portfolio_manager,
        "query-analyzer": get_query_analyzer,
        "data-verifier": get_data_verifier,
    }
    
    agent_factory = agent_map.get(agent_type)
    if not agent_factory:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown agent type: {agent_type}. Available types: {list(agent_map.keys())}"
        )
    
    return agent_factory()


def validate_workflow_permissions(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    settings: Settings = Depends(get_current_settings)
) -> bool:
    """Validate permissions for workflow execution."""
    # In debug mode, allow all workflows
    if settings.debug:
        return True
    
    # TODO: Implement actual authentication and authorization
    # For now, just check if we have credentials for non-debug mode
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required for workflow execution",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return True


def get_request_context(request) -> dict:
    """Extract context information from request."""
    return {
        "request_id": getattr(request.state, "request_id", None),
        "user_agent": request.headers.get("user-agent"),
        "client_ip": request.client.host if request.client else None,
        "path": request.url.path,
        "method": request.method,
    }


async def validate_rate_limits(
    request,
    settings: Settings = Depends(get_current_settings)
) -> bool:
    """Validate rate limits for API requests."""
    # TODO: Implement actual rate limiting
    # For now, just return True
    # In production, integrate with Redis for distributed rate limiting
    
    if settings.debug:
        return True
    
    # Basic rate limiting could check:
    # - Requests per minute/hour per IP
    # - Requests per minute/hour per API key
    # - Total system load
    
    return True


def get_agent_health_checker():
    """Get agent health checker dependency."""
    async def check_agent_health(agent_id: str) -> dict:
        """Check health of a specific agent."""
        try:
            agent = get_agent_by_type(agent_id)
            
            # Basic health check
            if hasattr(agent, 'is_active'):
                is_active = agent.is_active
            else:
                is_active = True  # Assume active if no health check method
            
            # Get agent statistics if available
            stats = {}
            if hasattr(agent, 'get_stats'):
                stats = agent.get_stats()
            
            return {
                "agent_id": agent_id,
                "status": "healthy" if is_active else "unhealthy",
                "is_active": is_active,
                "statistics": stats,
                "last_checked": None  # Could add actual timestamp tracking
            }
            
        except Exception as e:
            return {
                "agent_id": agent_id,
                "status": "error",
                "is_active": False,
                "error": str(e),
                "last_checked": None
            }
    
    return check_agent_health


def get_system_health_checker():
    """Get system health checker dependency."""
    async def check_system_health() -> dict:
        """Check overall system health."""
        from app.api.endpoints.health import check_database_health, check_redis_health, check_agents_health
        
        # Check individual services
        database_health = await check_database_health()
        redis_health = await check_redis_health() 
        agents_health = await check_agents_health()
        
        health_data = {
            "database": database_health,
            "redis": redis_health,
            "agents": agents_health,
        }
        
        # Determine overall status
        all_healthy = all(
            service.get("status") == "healthy" 
            for service in health_data.values()
        )
        
        return {
            "status": "healthy" if all_healthy else "unhealthy",
            "services": health_data
        }
    
    return check_system_health