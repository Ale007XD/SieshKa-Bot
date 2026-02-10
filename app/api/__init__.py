"""API package."""

try:
    from app.api.main import app  # type: ignore
except Exception:
    app = None

__all__ = ["app"]
