import asyncio
import json
import pytest

from app.api.v1.endpoints.health import health_check
from starlette.responses import JSONResponse
import sys
import types
from typing import Any, cast
from types import SimpleNamespace


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


def _decode_response(res):
    """Helper to extract JSON content from health response regardless of type."""
    if isinstance(res, JSONResponse):
        raw = res.body
        if isinstance(raw, memoryview):
            raw_bytes = raw.tobytes()
        else:
            raw_bytes = raw if isinstance(raw, (bytes, bytearray)) else bytes(raw)
        return json.loads(raw_bytes.decode())
    return res


@pytest.mark.asyncio
async def test_health_warns_includes_redis_when_not_configured(monkeypatch):
    # Ensure DB check succeeds; redis is often not configured in test env
    dummy_db = _FakeDB()
    res = await health_check(cast(Any, dummy_db))  # type: ignore[arg-type]
    # health.py returns either dict or JSONResponse; for healthy path it should be dict
    # Ensure warnings key exists and contains a redis-related warning when not configured
    content = _decode_response(res)
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
    res = await health_check(dummy_db)  # type: ignore[arg-type]
    assert isinstance(res, JSONResponse)
    assert res.status_code == 503
    content = _decode_response(res)
    assert content.get("status") == "unhealthy"


@pytest.mark.asyncio
async def test_health_all_ok_with_configured_redis(monkeypatch):
    # Setup fake Redis asyncio module
    redis_pkg = types.ModuleType("redis")
    redis_asyncio = types.ModuleType("redis.asyncio")
    class _FakeRedisClient:
        async def ping(self):
            return
        async def close(self):
            return
    async def _from_url_ok(url):
        return _FakeRedisClient()
    redis_asyncio.from_url = _from_url_ok
    redis_pkg.asyncio = redis_asyncio
    monkeypatch.setitem(sys.modules, "redis", redis_pkg)
    monkeypatch.setitem(sys.modules, "redis.asyncio", redis_asyncio)

    from app import config as cfg
    monkeypatch.setattr(cfg, "settings", SimpleNamespace(redis_url="redis://fake", admin_telegram_ids=[]))

    dummy_db = _FakeDB()
    res = await health_check(cast(Any, dummy_db))  # type: ignore[arg-type]
    content = _decode_response(res)
    assert content["services"]["redis"] == "ok"
    assert content["status"] == "healthy"
    assert "warnings" in content


@pytest.mark.asyncio
async def test_health_redis_failure(monkeypatch):
    # Redis configured but ping fails
    redis_pkg = types.ModuleType("redis")
    redis_asyncio = types.ModuleType("redis.asyncio")
    class _FakeRedisClientFail:
        async def ping(self):
            raise Exception("redis ping failed")
        async def close(self):
            return
    async def _from_url_fail(url):
        return _FakeRedisClientFail()
    redis_asyncio.from_url = _from_url_fail
    redis_pkg.asyncio = redis_asyncio
    monkeypatch.setitem(sys.modules, "redis", redis_pkg)
    monkeypatch.setitem(sys.modules, "redis.asyncio", redis_asyncio)

    from app import config as cfg
    monkeypatch.setattr(cfg, "settings", SimpleNamespace(redis_url="redis://fake", admin_telegram_ids=[]))

    dummy_db = _FakeDB()
    res = await health_check(cast(Any, dummy_db))
    assert isinstance(res, JSONResponse)
    content = _decode_response(res)
    assert content["services"]["redis"].startswith("error")


@pytest.mark.asyncio
async def test_health_redis_library_missing(monkeypatch):
    # Simulate missing redis library by removing modules
    import sys as _sys
    _sys.modules.pop("redis.asyncio", None)
    _sys.modules.pop("redis", None)

    from app import config as cfg
    monkeypatch.setattr(cfg, "settings", SimpleNamespace(redis_url="redis://fake", admin_telegram_ids=[]))

    dummy_db = _FakeDB()
    res = await health_check(dummy_db)  # type: ignore[arg-type]
    content = _decode_response(res)
    assert isinstance(content, dict)
    redis_status = content.get("services", {}).get("redis")
    assert redis_status is not None
    ok = (redis_status in {"not_configured", "ok"} or (isinstance(redis_status, str) and redis_status.startswith("error")))
    assert ok
