from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Index, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from datetime import datetime, timezone
import os
import logging
from typing import Generator
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Database configuration with fallback
DATABASE_URL = os.getenv("DATABASE_URL")
SQLITE_FALLBACK = "sqlite:///./data/hackathon.db"

# Environment validation with fallback logic
def get_database_url() -> str:
    """Get database URL with fallback to SQLite"""
    if not DATABASE_URL or not DATABASE_URL.strip():
        logger.warning("DATABASE_URL not set, using SQLite fallback")
        return SQLITE_FALLBACK
    
    # Validate PostgreSQL URL format
    if DATABASE_URL.startswith("postgresql"):
        try:
            # Test connection format
            if "://" not in DATABASE_URL:
                raise ValueError("Invalid PostgreSQL URL format")
            logger.info("Using PostgreSQL database")
            return DATABASE_URL
        except Exception as e:
            logger.error(f"PostgreSQL URL validation failed: {e}, falling back to SQLite")
            return SQLITE_FALLBACK
    
    # For SQLite URLs
    elif DATABASE_URL.startswith("sqlite"):
        logger.info("Using SQLite database")
        return DATABASE_URL
    
    else:
        logger.warning(f"Unknown database type in URL: {DATABASE_URL}, using SQLite fallback")
        return SQLITE_FALLBACK

# Get final database URL
FINAL_DATABASE_URL = get_database_url()

# Engine configuration based on database type
def create_database_engine():
    """Create database engine with appropriate configuration"""
    try:
        if FINAL_DATABASE_URL.startswith("postgresql"):
            # PostgreSQL configuration
            engine = create_engine(
                FINAL_DATABASE_URL,
                pool_pre_ping=True,  # Validate connections before use
                pool_recycle=3600,   # Recycle connections every hour
                pool_size=5,         # Connection pool size
                max_overflow=10,     # Maximum overflow connections
                connect_args={"sslmode": "require"}
            )
        else:
            # SQLite configuration
            engine = create_engine(
                FINAL_DATABASE_URL,
                pool_pre_ping=True,
                connect_args={"check_same_thread": False, "timeout": 20}
            )
        
        # Test connection with proper SQLAlchemy 2.0 syntax
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))  # Fixed: Using text() wrapper
        
        logger.info(f"Database engine created successfully: {FINAL_DATABASE_URL.split('@')[0] if '@' in FINAL_DATABASE_URL else FINAL_DATABASE_URL}")
        return engine
        
    except Exception as e:
        logger.error(f"Failed to create engine for {FINAL_DATABASE_URL}: {e}")
        # Final fallback to SQLite
        if FINAL_DATABASE_URL != SQLITE_FALLBACK:
            logger.info("Attempting final SQLite fallback")
            try:
                engine = create_engine(
                    SQLITE_FALLBACK,
                    pool_pre_ping=True,
                    connect_args={"check_same_thread": False, "timeout": 20}
                )
                with engine.connect() as conn:
                    conn.execute(text("SELECT 1"))  # Fixed: Using text() wrapper
                logger.info("SQLite fallback engine created successfully")
                return engine
            except Exception as fallback_error:
                logger.critical(f"SQLite fallback also failed: {fallback_error}")
                raise RuntimeError("Could not establish database connection")
        raise

# Create engine
engine = create_database_engine()

# Session configuration
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False  # Keep objects usable after commit
)

# Base model
Base = declarative_base()

class AgentInteraction(Base):
    """Model for storing agent-user interactions"""
    __tablename__ = "agent_interactions"
    
    id = Column(Integer, primary_key=True, index=True)
    agent_type = Column(String(50), nullable=False, index=True)
    user_query = Column(Text, nullable=False)
    agent_response = Column(Text, nullable=False)
    model_used = Column(String(100), nullable=True, index=True)  # Track which model was used
    classification = Column(String(50), nullable=True, index=True)  # Query classification
    confidence = Column(String(20), nullable=True)  # Confidence level
    processing_time = Column(Integer, nullable=True)  # Processing time in milliseconds
    created_at = Column(
        DateTime, 
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )
    
    # Composite index for common queries
    __table_args__ = (
        Index('idx_agent_created', 'agent_type', 'created_at'),
        Index('idx_model_classification', 'model_used', 'classification'),
    )

    def __repr__(self):
        return f"<AgentInteraction(id={self.id}, agent='{self.agent_type}', created='{self.created_at}')>"

# Database dependency with error handling
def get_db() -> Generator[Session, None, None]:
    """Database session dependency with error handling"""
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    except Exception as e:
        logger.error(f"Unexpected database error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

# Table creation with error handling
def create_tables():
    """Create all tables with error handling"""
    try:
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
        # Verify table creation with proper SQLAlchemy 2.0 syntax
        with engine.connect() as conn:
            if FINAL_DATABASE_URL.startswith("sqlite"):
                result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))  # Fixed: Using text()
            else:
                result = conn.execute(text("SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname='public'"))  # Fixed: Using text()
            
            tables = [row[0] for row in result]
            logger.info(f"Available tables: {tables}")
            
    except Exception as e:
        logger.error(f"Failed to create tables: {e}")
        raise RuntimeError(f"Database initialization failed: {e}")

# Database health check
def check_database_health() -> dict:
    """Check database connection health"""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))  # Fixed: Using text()
        
        # Get basic stats
        with SessionLocal() as db:
            total_interactions = db.query(AgentInteraction).count()
            
        return {
            "status": "healthy",
            "database_url": FINAL_DATABASE_URL.split('@')[0] if '@' in FINAL_DATABASE_URL else FINAL_DATABASE_URL,
            "total_interactions": total_interactions,
            "connection_pool_size": engine.pool.size() if hasattr(engine.pool, 'size') else "unknown"
        }
        
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "database_url": FINAL_DATABASE_URL.split('@')[0] if '@' in FINAL_DATABASE_URL else FINAL_DATABASE_URL
        }
