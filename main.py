from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import os
import logging
from utils.routes import router
from schemas.database import create_tables

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)


# Modern lifespan event handler (replaces @app.on_event)
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    Code before yield runs at startup, code after yield runs at shutdown.
    """
    # Startup
    logger.info("AI Tutor Orchestrator starting up...")
    create_tables()
    logger.info("Database tables initialized")
    
    yield  # Application runs here
    
    # Shutdown
    logger.info("AI Tutor Orchestrator shutting down...")
    logger.info("Cleanup completed")


# Initialize FastAPI app with lifespan
app = FastAPI(
    title="AI Tutor Orchestrator",
    description="Hackathon Project - Hybrid Agent System with Intelligent Query Routing",
    version="1.0.0",
    lifespan=lifespan  # Modern approach - no more deprecation warnings!
)


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include API routes
app.include_router(router, prefix="/api/v1", tags=["AI Tutor"])


@app.get("/", tags=["Health"])
def read_root():
    """
    Root endpoint - API status and configuration check
    """
    return {
        "message": "AI Tutor Orchestrator API is running",
        "version": "1.0.0",
        "groq_configured": bool(os.getenv("GROQ_API_KEY")),
        "openrouter_configured": bool(os.getenv("OPENROUTER_API_KEY")),
        "groq_model": "llama-3.3-70b-versatile",
        "openrouter_model": os.getenv("OPENROUTER_MODEL", "Not configured"),
        "status": "healthy",
        "docs": "/docs",
        "api_prefix": "/api/v1"
    }


@app.get("/health", tags=["Health"])
def health_check():
    """
    Health check endpoint for monitoring
    """
    return {
        "status": "healthy",
        "database": "sqlite",
        "api_version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
