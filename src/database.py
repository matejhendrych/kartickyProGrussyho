"""
Database configuration for FastAPI with PostgreSQL support
"""
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from src.config import settings


def _build_engine():
    db_url = str(settings.DATABASE_URL)
    sqlite_connect_args = {"check_same_thread": False} if db_url.startswith("sqlite") else {}
    return create_engine(
        db_url,
        pool_pre_ping=True,
        echo=settings.DEBUG,
        connect_args=sqlite_connect_args
    )


engine = _build_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Database session dependency for FastAPI
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
