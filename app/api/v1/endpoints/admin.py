"""Admin UI endpoints (minimal MVP) for server-rendered pages."""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from app.api.v1.dependencies import get_db_session, get_current_admin

router = APIRouter()


@router.get("/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request, session=Depends(get_db_session), current_user: dict = Depends(get_current_admin)):
    name = getattr(current_user, "name", getattr(current_user, "id", "Admin")) if isinstance(current_user, dict) else "Admin"
    html = f"<html><body><h1>Admin Dashboard</h1><p>Welcome, {name}.</p><a href='/admin/orders'>Orders</a> | <a href='/admin/settings'>Settings</a></body></html>"
    return HTMLResponse(content=html)


@router.get("/orders", response_class=HTMLResponse)
async def admin_orders(request: Request, session=Depends(get_db_session), current_user: dict = Depends(get_current_admin)):
    orders = []  # Placeholder data for MVP
    html = "<html><body><h1>Admin Orders</h1><ul></ul></body></html>"
    return HTMLResponse(content=html)


@router.get("/settings", response_class=HTMLResponse)
async def admin_settings(request: Request, session=Depends(get_db_session), current_user: dict = Depends(get_current_admin)):
    html = "<html><body><h1>Admin Settings</h1></body></html>"
    return HTMLResponse(content=html)
