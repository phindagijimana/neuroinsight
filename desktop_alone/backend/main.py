"""
Main FastAPI application for NeuroInsight.

This module initializes and configures the FastAPI application,
including middleware, routes, and lifecycle events.
"""

from contextlib import asynccontextmanager

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from backend.api import cleanup_router, jobs_router, metrics_router, upload_router, visualizations_router
from backend.core import get_settings, init_db, setup_logging
from backend.core.logging import get_logger

# Initialize settings and logging
settings = get_settings()
setup_logging(settings.log_level, settings.environment)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager.
    
    Handles startup and shutdown events.
    """
    # Startup
    logger.info(
        "application_starting",
        app_name=settings.app_name,
        version=settings.app_version,
        environment=settings.environment,
    )
    
    # Initialize database
    try:
        init_db()
        logger.info("database_initialized")
    except Exception as e:
        logger.error("database_initialization_failed", error=str(e))
        raise
    
    yield
    
    # Shutdown
    logger.info("application_shutting_down")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Neuroimaging pipeline for hippocampal asymmetry analysis",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure CORS
# If cors_origins_list contains "*", use allow_origin_regex to match all origins
cors_origins = settings.cors_origins_list
if cors_origins == ["*"]:
    # Allow all origins when "*" is specified
    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=r".*",  # Match any origin
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    # Use specific origins
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    """
    Health check endpoint.
    
    Returns application status and version information.
    """
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
    }


# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """
    Root endpoint with API information.
    """
    return {
        "message": "NeuroInsight API",
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health",
    }


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler.
    
    Catches unhandled exceptions and returns a standardized error response.
    """
    logger.error(
        "unhandled_exception",
        path=request.url.path,
        method=request.method,
        error=str(exc),
        exc_info=True,
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc) if settings.environment == "development" else None,
        },
    )


# Include routers
app.include_router(upload_router)
app.include_router(jobs_router)
app.include_router(metrics_router)
app.include_router(visualizations_router)
app.include_router(cleanup_router)  # Admin cleanup endpoints

# Serve frontend static files in desktop mode
if settings.desktop_mode:
    frontend_dir = Path(__file__).parent.parent / "frontend"
    if frontend_dir.exists():
        app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")
        logger.info("frontend_static_files_enabled", path=str(frontend_dir))


if __name__ == "__main__":
    import uvicorn
    import os
    
    # Allow port override via environment
    port = int(os.getenv("PORT", settings.api_port))
    
    # Disable reload for desktop/production - causes "Address in use" with PyInstaller
    should_reload = settings.environment == "development" and not settings.desktop_mode
    
    uvicorn.run(
        "backend.main:app",
        host=settings.api_host,
        port=port,
        reload=should_reload,
        log_level=settings.log_level.lower(),
    )

