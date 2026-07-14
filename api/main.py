from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from ..configs.settings import settings
from ..utils.logger import setup_logging, get_logger
from ..state.manager import state_manager
from ..memory.manager import memory_manager
from ..utils.observability import observability
from .routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    setup_logging(
        log_level="INFO" if settings.environment == "production" else "DEBUG",
        log_to_file=True,
        log_to_console=True
    )
    logger = get_logger("api")
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    
    observability.initialize(app)
    # Initialize state manager
    await state_manager.initialize()
    
    # Initialize memory manager
    await memory_manager.initialize()
    
    logger.info("Application startup complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")
    await state_manager.close()
    await memory_manager.close()
    logger.info("Application shutdown complete")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Production-grade Multi-Agent AI Platform",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.debug else ["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def observe_api_request(request, call_next):
    """Record API request duration and failures without exposing request content."""
    with observability.span("api.request", method=request.method, path=request.url.path):
        return await call_next(request)

# Include routes
app.include_router(router, prefix=settings.api_prefix)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Multi-Agent AI System API",
        "version": settings.app_version,
        "docs": "/api/docs"
    }
