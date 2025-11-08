"""
Database configuration and session management.

This module provides SQLAlchemy database connection handling,
session management, and base model class.
"""

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from .config import get_settings

# Get application settings
settings = get_settings()

# Create SQLAlchemy engine
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=settings.environment == "development",
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Database session dependency for FastAPI.
    
    Yields a database session and ensures it's closed after the request.
    Use this as a dependency in FastAPI route handlers.
    
    Example:
        @app.get("/jobs")
        def get_jobs(db: Session = Depends(get_db)):
            return db.query(Job).all()
    
    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Initialize database by creating all tables.
    
    This function creates all tables defined by models inheriting from Base.
    Should be called on application startup.
    
    Note:
        In production, use Alembic migrations instead of this function.
    """
    from backend.models import Job, Metric  # noqa: F401
    
    Base.metadata.create_all(bind=engine)

