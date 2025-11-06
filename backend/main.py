"""
Investment Research Assistant - FastAPI Backend
Main application entry point
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from api.routes import router as api_router
from core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle management for the application.
    Initialize resources on startup, cleanup on shutdown.
    """
    logger.info("🚀 Starting Investment Research Assistant API")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    
    # Startup: Initialize services
    # We'll add Pinecone initialization here later
    
    yield
    
    # Shutdown: Cleanup resources
    logger.info("👋 Shutting down Investment Research Assistant API")


# Create FastAPI application
app = FastAPI(
    title="Investment Research Assistant API",
    description="RAG-based financial document analysis and research system",
    version="1.0.0",
    lifespan=lifespan,
)

# Add rate limiter to app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS with specific methods and headers
cors_origins = settings.CORS_ORIGINS
logger.info(f"🌐 CORS origins configured: {cors_origins}")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],  # Specific methods only
    allow_headers=["Content-Type", "Authorization", "X-API-Key"],  # Specific headers only
)

# API Key Authentication Middleware
@app.middleware("http")
async def verify_api_key(request: Request, call_next):
    """Verify API key for protected endpoints"""
    # Skip auth for health check endpoints and OPTIONS (preflight) requests
    if request.url.path in ["/", "/health", "/docs", "/openapi.json", "/redoc"] or request.method == "OPTIONS":
        return await call_next(request)
    
    # Check if API keys are configured
    valid_keys = settings.VALID_API_KEYS
    if valid_keys:
        # Get API key from header
        api_key = request.headers.get("X-API-Key") or request.headers.get("Authorization", "").replace("Bearer ", "")
        
        if not api_key or api_key not in valid_keys:
            logger.warning(f"Invalid API key attempt from {request.client.host if request.client else 'unknown'}")
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid or missing API key. Please provide a valid X-API-Key header."}
            )
        
        # Store API key in request state for rate limiting/tracking
        request.state.api_key = api_key
    
    return await call_next(request)

# Request size limit middleware
@app.middleware("http")
async def limit_request_size(request: Request, call_next):
    """Limit request body size to prevent DoS attacks"""
    max_size = 1024 * 1024  # 1MB
    
    if request.headers.get("content-length"):
        content_length = int(request.headers["content-length"])
        if content_length > max_size:
            return JSONResponse(
                status_code=413,
                content={"detail": "Request body too large. Maximum size: 1MB"}
            )
    
    response = await call_next(request)
    return response

# Include API routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Investment Research Assistant API",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "checks": {
            "api": "ok",
            "pinecone": "ok",  # We'll add real checks later
            "openai": "ok"
        },
        "cors_origins": settings.CORS_ORIGINS,
        "cors_origins_count": len(settings.CORS_ORIGINS)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True
    )
