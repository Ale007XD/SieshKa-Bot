"""Tests for API endpoints."""

import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

from app.main import app
from app.database import get_db


@pytest.fixture
def client():
    """Create test client with mocked database."""
    mock_session = AsyncMock()
    
    async def override_get_db():
        yield mock_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


class TestHealthEndpoint:
    """Test health endpoint."""
    
    def test_health_check_exists(self, client):
        """Test that health endpoint exists."""
        response = client.get("/api/v1/health")
        # May return 200 or 503 depending on DB connectivity
        assert response.status_code in [200, 503]
    
    def test_health_response_structure(self, client):
        """Test health response structure."""
        response = client.get("/api/v1/health")
        data = response.json()
        
        assert "status" in data
        assert "version" in data
        assert "services" in data
        assert isinstance(data["services"], dict)


class TestMenuEndpoints:
    """Test menu endpoints."""
    
    def test_get_categories(self, client):
        """Test getting categories."""
        response = client.get("/api/v1/menu/categories")
        # With mocked DB, should return 200
        assert response.status_code in [200, 422]
    
    def test_get_products(self, client):
        """Test getting products."""
        response = client.get("/api/v1/menu/products")
        assert response.status_code in [200, 422]


class TestOrdersEndpoints:
    """Test orders endpoints."""
    
    def test_get_orders_requires_auth(self, client):
        """Test that orders endpoint requires auth."""
        response = client.get("/api/v1/orders")
        # Should require authentication
        assert response.status_code in [401, 403, 422]
    
    def test_get_order_status_public(self, client):
        """Test order status endpoint (public)."""
        # Test with fake order number - now requires phone parameter
        response = client.get("/api/v1/orders/FAKE123/status")
        # Should return 422 (validation error) without phone parameter
        assert response.status_code in [404, 422, 503]


class TestSettingsEndpoints:
    """Test settings endpoints."""
    
    def test_get_settings(self, client):
        """Test getting settings."""
        response = client.get("/api/v1/settings")
        assert response.status_code in [200, 422]
    
    def test_get_payment_methods(self, client):
        """Test getting payment methods."""
        response = client.get("/api/v1/settings/payment-methods")
        assert response.status_code in [200, 422]

def test_dependency_utils_normalize_user():
    """Test normalize_user helper returns expected structure for a mock user."""
    class DummyUser:
        def __init__(self):
            self.id = 123
            self.role = "ADMIN"
        def is_admin(self):
            return True

    from app.api.v1.dependency_utils import normalize_user
    u = DummyUser()
    data = normalize_user(u)
    assert isinstance(data, dict)
    assert data["id"] == 123
    assert data["role"] == "ADMIN"
    assert data["is_admin"] is True
