"""Handlers package."""

from aiogram import Router
from typing import List

from app.handlers.common import router as common_router
from app.handlers.client import router as client_router
from app.handlers.admin import router as admin_router
from app.handlers.manager import router as manager_router
from app.handlers.kitchen import router as kitchen_router
from app.handlers.packer import router as packer_router
from app.handlers.courier import router as courier_router


def get_all_routers() -> List[Router]:
    """Get all routers for registration."""
    return [
        common_router,
        client_router,
        admin_router,
        manager_router,
        kitchen_router,
        packer_router,
        courier_router,
    ]


__all__ = [
    "get_all_routers",
    "common_router",
    "client_router",
    "admin_router",
    "manager_router",
    "kitchen_router",
    "packer_router",
    "courier_router",
]
