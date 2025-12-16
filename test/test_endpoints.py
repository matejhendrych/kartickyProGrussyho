"""
FastAPI endpoint tests
"""
from fastapi.testclient import TestClient


def test_root(client):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_services_health(client):
    """Test services health endpoint"""
    response = client.get("/services/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data


def test_api_docs(client):
    """Test that API documentation is available"""
    response = client.get("/docs")
    assert response.status_code == 200


def test_openapi_schema(client):
    """Test that OpenAPI schema is available"""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert "openapi" in schema
    assert "info" in schema
