"""
Pytest configuration and fixtures for FastAPI tests
"""
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Set test environment variables before importing app
os.environ['APP_KEY'] = 'test-secret-key-for-testing-only'
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
os.environ['APP_DEBUG'] = 'True'

from main import app
from src.database import Base, get_db


@pytest.fixture(scope="session")
def test_db():
    """Create test database"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()


@pytest.fixture(scope="function")
def client(test_db):
    """FastAPI test client with dependency override for database"""
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def reset_db(test_db):
    """Reset database before each test"""
    # Clean up after each test
    yield
    for table in reversed(Base.metadata.sorted_tables):
        test_db.execute(table.delete())
    test_db.commit()

