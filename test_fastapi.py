"""
Simple test to verify FastAPI application structure
"""
import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set environment variables before importing app
os.environ['APP_KEY'] = 'test-secret-key-for-testing-only'
os.environ['DATABASE_URL'] = 'sqlite:///test.db'

from main import app

client = TestClient(app)


def test_read_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
    assert "version" in response.json()


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_services_health():
    """Test services health endpoint"""
    response = client.get("/services/health")
    assert response.status_code == 200
    assert "status" in response.json()


def test_api_docs():
    """Test that API documentation is available"""
    response = client.get("/docs")
    assert response.status_code == 200


def test_openapi_schema():
    """Test that OpenAPI schema is available"""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert "openapi" in response.json()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
