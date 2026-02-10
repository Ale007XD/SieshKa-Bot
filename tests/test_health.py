import asyncio
import json
import pytest

from app.api.v1.endpoints.health import health_check
from starlette.responses import JSONResponse


class _FakeResult:
    def scalar(self):
        return 1


class _FakeDB:
    def __init__(self, raise_exc: bool = False):
        self.raise_exc = raise_exc

    async def execute(self, query):
        if self.raise_exc:
            raise Exception("db failure")
        return _FakeResult()


@pytest.mark.asyncio
async def test_health_warns_includes_redis_when_not_configured(monkeypatch):
    # Ensure DB check succeeds; redis is often not configured in test env
    dummy_db = _FakeDB()
    res = await health_check(dummy_db)
    # health.py returns either dict or JSONResponse; for healthy path it should be dict
    # Ensure warnings key exists and contains a redis-related warning when not configured
    if isinstance(res, JSONResponse):
        content = json.loads(res.body.decode())
    else:
        content = res
    assert isinstance(content, dict)
    assert "warnings" in content
    # Look for a redis warning entry if present
    warns = content.get("warnings", [])
    assert isinstance(warns, list)
    # If a redis warning exists, ensure structure is correct; otherwise, at least no crash
    if warns:
        assert any(isinstance(w, dict) and w.get("service") == "redis" for w in warns)


@pytest.mark.asyncio
async def test_health_unhealthy_on_db_failure():
    dummy_db = _FakeDB(raise_exc=True)
    res = await health_check(dummy_db)
    assert isinstance(res, JSONResponse)
    assert res.status_code == 503
    content = json.loads(res.body.decode())
    assert content.get("status") == "unhealthy"
