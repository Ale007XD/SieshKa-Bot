import pytest
from fastapi import HTTPException

from app.api.v1.dependencies import get_current_admin


@pytest.mark.asyncio
async def test_get_current_admin_allows_when_admin():
    current_user = {"is_admin": True}
    result = await get_current_admin(current_user)
    assert result == current_user


@pytest.mark.asyncio
async def test_get_current_admin_denies_when_not_admin():
    current_user = {"is_admin": False}
    with pytest.raises(HTTPException) as excinfo:
        await get_current_admin(current_user)
    assert excinfo.value.status_code == 403
    assert "Admin access required" in excinfo.value.detail
