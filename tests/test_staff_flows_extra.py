import pytest
from types import SimpleNamespace

from app.config import settings
from app.utils.admin_guard import is_admin_callback


def _cb(uid):
    return SimpleNamespace(from_user=SimpleNamespace(id=uid), data="admin:menu")

def test_staff_guard_allows_when_admin_in_settings():
    settings.admin_telegram_ids = [1234]
    assert is_admin_callback(_cb(1234)) is True

def test_staff_guard_denies_when_not_admin():
    settings.admin_telegram_ids = [1234]
    assert is_admin_callback(_cb(9999)) is False
