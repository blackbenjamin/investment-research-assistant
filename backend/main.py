"""
Investment Research Assistant - FastAPI Backend
Main application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from api.routes import router as api_router
from core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


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

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True
    )
