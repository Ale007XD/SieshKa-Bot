"""Smoke tests for basic functionality."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint():
    """Test health check endpoint."""
    response = client.get("/api/v1/health")
    # Note: This will fail without a database, which is expected in smoke tests
    # The important thing is that the endpoint exists and returns a response
    assert response.status_code in [200, 503]  # 200 = healthy, 503 = unhealthy
    
    data = response.json()
    assert "status" in data
    assert "version" in data
    assert "services" in data


def test_api_version():
    """Test that API version is present."""
    response = client.get("/api/v1/health")
    data = response.json()
    assert data.get("version") == "1.0.0"


@pytest.mark.asyncio
async def test_models_import():
    """Test that all models can be imported."""
    try:
        from app.models import (
            User, Category, Product, Modifier, ModifierOption,
            ProductModifier, Order, OrderStatusLog, OrderItem,
            AppSettings, PromoCode, DeliveryZone, Review,
            DailyCounter, AdminAuditLog
        )
        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import models: {e}")


@pytest.mark.asyncio
async def test_enums_import():
    """Test that enums can be imported."""
    try:
        from app.utils.enums import UserRole, OrderStatus, PaymentMethod, PaymentStatus
        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import enums: {e}")


@pytest.mark.asyncio
async def test_exceptions_import():
    """Test that exceptions can be imported."""
    try:
        from app.utils.exceptions import AppException, NotFoundException, ValidationException
        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import exceptions: {e}")
