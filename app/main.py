"""Main FastAPI application entry point."""

import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.endpoints import health, auth, menu, orders, settings, guest_orders, admin
from app.config import settings
from app.database import close_db, init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    await init_db()
    yield
    # Shutdown
    await close_db()


app = FastAPI(
    title="Food Delivery API",
    description="REST API for Food Delivery Telegram Bot",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve simple mobile shop frontend (guest orders)
try:
    app.mount("/shop", StaticFiles(directory="shop"), name="shop")
except Exception:
    pass

# Include routers
app.include_router(health.router, prefix="/api/v1/health", tags=["health"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(menu.router, prefix="/api/v1/menu", tags=["menu"])
app.include_router(orders.router, prefix="/api/v1/orders", tags=["orders"])
app.include_router(settings.router, prefix="/api/v1/settings", tags=["settings"])
app.include_router(guest_orders.router, prefix="/api/v1/orders", tags=["guest_orders"])
# Safe include for admin router (may be absent in some environments)
_admin_router = getattr(admin, "router", None)
if _admin_router is not None:
    app.include_router(_admin_router, prefix="/admin", tags=["admin"])  # type: ignore[arg-type]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
