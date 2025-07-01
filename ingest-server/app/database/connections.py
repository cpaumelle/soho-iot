# version: 0.2.1 — 2025-06-30
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from os import getenv

Base = declarative_base()

DB_URL = getenv("DATABASE_URL")
if not DB_URL:
    raise RuntimeError("❌ DATABASE_URL is not set")

engine = create_engine(DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
