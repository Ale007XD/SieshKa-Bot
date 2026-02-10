from app.utils.exceptions import AppException

def ensure_admin(user) -> None:
    """Raise if user is not admin."""
    if user is None or not getattr(user, "is_admin", lambda: False)():
        raise AppException("Access denied", "Admin privileges required")
