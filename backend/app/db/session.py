"""
Database Session Manager
Handles PostgreSQL connections with graceful fallback
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator, Optional
import os
import logging

logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://impactai:impactai123@localhost:5432/impactai_db")

# Create engine with connection pooling
try:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,  # Verify connections before using
        pool_size=10,
        max_overflow=20,
        echo=os.getenv("SQL_ECHO", "false").lower() == "true"
    )
    
    # Test connection
    with engine.connect() as conn:
        conn.execute("SELECT 1")
    
    db_enabled = True
    logger.info("✅ PostgreSQL connected successfully")
    
except Exception as e:
    logger.warning(f"⚠️  PostgreSQL not available: {e}")
    logger.warning("   Database features disabled - using cache/JSON only")
    db_enabled = False
    engine = None

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) if engine else None

# Base class for models
Base = declarative_base()


def get_db() -> Generator[Optional[Session], None, None]:
    """
    Get database session with graceful fallback
    Returns None if database is not available
    """
    if not db_enabled or not SessionLocal:
        yield None
        return
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def is_db_available() -> bool:
    """Check if database is available"""
    return db_enabled
