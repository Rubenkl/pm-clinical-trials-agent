"""FastAPI application main entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import time
import uuid

from app.core.config import get_settings
from app.api.api_v1.api import api_router
from app.api.endpoints.health import health_router


def create_application() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()
    
    app = FastAPI(
        title="Clinical Trials Agent API",
        description="AI-powered clinical trials management system with multi-agent orchestration",
        version="0.1.0",
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        openapi_url="/openapi.json" if settings.debug else None,
    )

    # Add CORS middleware (always add in debug mode, conditionally in production)
    if settings.debug or settings.cors_origins:
        cors_origins = settings.get_cors_origins_list() if settings.cors_origins else ["*"]
        app.add_middleware(
            CORSMiddleware,
            allow_origins=cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Add trusted host middleware in production
    if not settings.debug:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["*"]  # Configure appropriately for production
        )

    # Add request ID middleware
    @app.middleware("http")
    async def add_request_id(request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        response.headers["X-API-Version"] = "v1"
        
        return response

    # Add request timing middleware
    @app.middleware("http")
    async def add_process_time(request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response

    # Exception handlers
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request, exc):
        return JSONResponse(
            status_code=422,
            content={
                "error": "Validation Error",
                "message": "The request data is invalid",
                "details": exc.errors(),
                "request_id": getattr(request.state, "request_id", None)
            }
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request, exc):
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "message": "An unexpected error occurred",
                "details": str(exc) if settings.debug else "Contact system administrator",
                "request_id": getattr(request.state, "request_id", None)
            }
        )

    # Include routers
    app.include_router(health_router, tags=["health"])
    app.include_router(api_router, prefix=settings.api_v1_str)

    return app


# Create the application instance
app = create_application()


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    settings = get_settings()
    
    # Initialize agent system
    from app.api.dependencies import initialize_agent_system
    await initialize_agent_system()
    
    print(f"🚀 {settings.app_name} started successfully")
    print(f"📊 Debug mode: {settings.debug}")
    print(f"🔑 OpenAI API configured: {'Yes' if settings.openai_api_key else 'No'}")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on application shutdown."""
    print("🔄 Shutting down Clinical Trials Agent API...")
    
    # Clean up agent resources
    from app.api.dependencies import cleanup_agent_system
    await cleanup_agent_system()
    
    print("✅ Shutdown complete")


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with basic API information."""
    settings = get_settings()
    return {
        "message": "Clinical Trials Agent API",
        "version": "0.1.0",
        "status": "operational",
        "docs_url": "/docs" if settings.debug else None,
        "health_check": "/health"
    }