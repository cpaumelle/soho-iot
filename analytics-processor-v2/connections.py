"""
SenseMy IoT Platform: Database Connections
Version: 20250629
Last Updated: 2025-06-29 14:30:00 UTC
Authors: SenseMy IoT Team

Changelog:
- Migrated to SQLAlchemy engine and session management
- Updated connection string generation
- Added table creation utility function
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from typing import Generator

# Create Base for declarative models
Base = declarative_base()

def get_analytics_engine():
    """Create SQLAlchemy engine for analytics database"""
    analytics_host = os.getenv("ANALYTICS_DB_HOST", "analytics-database")
    analytics_port = os.getenv("ANALYTICS_DB_PORT", "5432")
    analytics_user = os.getenv("ANALYTICS_DB_USER", "analytics_user")
    analytics_password = os.getenv("ANALYTICS_DB_PASSWORD", "analytics_pass")
    analytics_name = os.getenv("ANALYTICS_DB_NAME", "analytics_db")

    analytics_url = f"postgresql://{analytics_user}:{analytics_password}@{analytics_host}:{analytics_port}/{analytics_name}"

    return create_engine(analytics_url, pool_pre_ping=True)

def get_analytics_session() -> Generator[Session, None, None]:
    """Create a database session generator"""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_analytics_engine())
    try:
        session = SessionLocal()
        yield session
    finally:
        session.close()

def create_analytics_tables():
    """Create all tables defined in the models"""
    from app.models.database import Base
    engine = get_analytics_engine()
    Base.metadata.create_all(bind=engine)
