"""Tests for handlers."""

import pytest
from aiogram import Dispatcher

from app.handlers import get_all_routers


class TestHandlers:
    """Test handlers module."""
    
    def test_get_all_routers(self):
        """Test that all routers are returned."""
        routers = get_all_routers()
        assert len(routers) == 7  # common, client, admin, manager, kitchen, packer, courier
    
    def test_routers_are_valid(self):
        """Test that all items are Router instances."""
        from aiogram import Router
        
        routers = get_all_routers()
        for router in routers:
            assert isinstance(router, Router)
