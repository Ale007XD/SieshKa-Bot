"""Shared helpers for API dependencies."""

from typing import Dict


def normalize_user(user) -> Dict[str, object]:
    """Normalize a User ORM object into a simple dict used by API responses.

    Exposes a consistent shape: {"id": int, "role": str, "is_admin": bool}.
    """
    # Guard against None just in case
    if user is None:
        return {"id": None, "role": None, "is_admin": False}
    # Some models implement methods; rely on them to determine admin status
    is_admin = False
    try:
        is_admin = getattr(user, "is_admin", lambda: False)()
    except Exception:
        is_admin = False
    return {
        "id": int(getattr(user, "id", 0)),
        "role": getattr(user, "role", None),
        "is_admin": bool(is_admin),
    }
