import pytest
from fastapi import HTTPException

from app.api.v1.dependencies_jwt import get_current_user_jwt


class DummyCreds:
    def __init__(self, token):
        self.credentials = token


async def test_get_current_user_jwt_valid(monkeypatch):
    payload = {"sub": 1, "role": "ADMIN"}

    def fake_decode(token):
        if token == "valid-token":
            return payload
        return None

    monkeypatch.setattr("app.api.v1.dependencies_jwt.decode_jwt_token", fake_decode, raising=False)
    # also ensure the token path used inside function returns payload
    creds = DummyCreds("valid-token")
    result = await get_current_user_jwt(creds)
    assert result == payload


async def test_get_current_user_jwt_invalid(monkeypatch):
    monkeypatch.setattr("app.api.v1.dependencies_jwt.decode_jwt_token", lambda t: None, raising=False)
    creds = DummyCreds("invalid-token")
    with pytest.raises(HTTPException):
        await get_current_user_jwt(creds)
