"""Admin UI endpoints (minimal MVP) for server-rendered pages."""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from typing import Any

router = APIRouter()
_templates = None
_templates_available = False
try:
    from fastapi.templating import Jinja2Templates
    _templates = Jinja2Templates(directory="templates")
    _templates_available = True
except Exception:
    _templates = None
    _templates_available = False

from app.api.v1.dependencies import get_db_session, get_current_admin


@router.get("/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request, session=Depends(get_db_session), current_user: dict = Depends(get_current_admin)):
    if _templates_available and _templates is not None and hasattr(_templates, "TemplateResponse"):
        return _templates.TemplateResponse("admin/dashboard.html", {"request": request, "user": current_user})
    name = getattr(current_user, "name", getattr(current_user, "id", "Admin")) if isinstance(current_user, dict) else "Admin"
    html = f"<html><body><h1>Admin Dashboard</h1><p>Welcome, {name}.</p><a href='/admin/orders'>Orders</a> | <a href='/admin/settings'>Settings</a></body></html>"
    return HTMLResponse(content=html)


@router.get("/orders", response_class=HTMLResponse)
async def admin_orders(request: Request, session=Depends(get_db_session), current_user: dict = Depends(get_current_admin)):
    orders = []  # Placeholder data for MVP
    if _templates_available and _templates is not None and hasattr(_templates, "TemplateResponse"):
        return _templates.TemplateResponse("admin/orders.html", {"request": request, "orders": orders, "user": current_user})
    html = "<html><body><h1>Admin Orders</h1><ul></ul></body></html>"
    return HTMLResponse(content=html)


@router.get("/settings", response_class=HTMLResponse)
async def admin_settings(request: Request, session=Depends(get_db_session), current_user: dict = Depends(get_current_admin)):
    if _templates_available and _templates is not None and hasattr(_templates, "TemplateResponse"):
        return _templates.TemplateResponse("admin/settings.html", {"request": request, "user": current_user})
    html = "<html><body><h1>Admin Settings</h1></body></html>"
    return HTMLResponse(content=html)
