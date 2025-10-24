import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
from app.main import app


@pytest.fixture
def client():
    """Create test client for FastAPI app"""
    return TestClient(app)


class TestAPIEndpoints:
    """Test cases for API endpoints"""
    
    def test_root_endpoint(self, client):
        """Test root endpoint returns HTML"""
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
    
    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
    
    def test_cities_endpoint(self, client):
        """Test cities endpoint"""
        response = client.get("/cities")
        assert response.status_code == 200
        data = response.json()
        assert "cities" in data
        assert isinstance(data["cities"], list)
    
    def test_weather_endpoint_no_cities(self, client):
        """Test weather endpoint with no cities"""
        response = client.get("/weather")
        assert response.status_code == 200
        data = response.json()
        assert "error" in data
        assert data["error"] == "Weather service not initialized"
    
    def test_weather_endpoint_with_cities(self, client):
        """Test weather endpoint with cities"""
        response = client.get("/weather?cities=Moscow,Saint Petersburg")
        assert response.status_code == 200
        data = response.json()
        assert "error" in data
        assert data["error"] == "Weather service not initialized"


if __name__ == "__main__":
    pytest.main([__file__])
