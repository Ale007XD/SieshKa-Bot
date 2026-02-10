import pytest

from app.utils.permissions import ensure_admin
from app.utils.exceptions import AppException


def test_admin_guard_raises_for_non_admin():
    class DummyUser:
        def is_admin(self):
            return False
    with pytest.raises(AppException):
        ensure_admin(DummyUser())


def test_admin_guard_passes_for_admin():
    class DummyUser:
        def is_admin(self):
            return True
    # Should not raise
    ensure_admin(DummyUser())
