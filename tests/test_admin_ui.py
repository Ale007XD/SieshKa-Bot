"""Tests for minimal admin UI MVP."""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.api.v1.dependencies import get_db_session, get_current_admin
from unittest.mock import AsyncMock
from fastapi import HTTPException, status


@pytest.fixture
def client():
    mock_session = AsyncMock()
    async def override_get_db_session():
        yield mock_session
    app.dependency_overrides[get_db_session] = override_get_db_session
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_admin_dashboard_allows_when_admin(client, monkeypatch):
    async def _admin_ok():
        return {"id": 1, "name": "Admin", "is_admin": True}
    app.dependency_overrides[get_current_admin] = _admin_ok
    resp = client.get("/admin/dashboard")
    assert resp.status_code == 200
    assert "Admin Dashboard" in resp.text or "dashboard" in resp.text.lower()
    app.dependency_overrides.clear()


def test_admin_dashboard_denies_when_not_admin(client):
    async def _admin_forbid():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    app.dependency_overrides[get_current_admin] = _admin_forbid
    resp = client.get("/admin/dashboard")
    assert resp.status_code == status.HTTP_403_FORBIDDEN
    app.dependency_overrides.clear()


def test_admin_orders_renders(client):
    async def _admin_ok():
        return {"id": 1, "name": "Admin", "is_admin": True}
    app.dependency_overrides[get_current_admin] = _admin_ok
    resp = client.get("/admin/orders")
    assert resp.status_code == 200
    assert "Admin Orders" in resp.text or "Orders" in resp.text
    app.dependency_overrides.clear()
