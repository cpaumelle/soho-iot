# version: 0.2.0 — 2025-06-30
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from os import getenv

Base = declarative_base()

ANALYTICS_DB_URL = getenv("ANALYTICS_DB_URL", "postgresql://analytics_user:analytics_secret@analytics-database:5432/analytics_db")
INGEST_DB_URL = getenv("INGEST_DB_URL", "postgresql://iot:secret@ingest-database:5432/soho_iot")

analytics_engine = create_engine(ANALYTICS_DB_URL)
ingest_engine = create_engine(INGEST_DB_URL)

AnalyticsSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=analytics_engine)
IngestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=ingest_engine)

def get_analytics_db():
    db = AnalyticsSessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_ingest_db():
    db = IngestSessionLocal()
    try:
        yield db
    finally:
        db.close()

# alias for backward compatibility
get_analytics_session = get_analytics_db
