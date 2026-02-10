"""Tests for services."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.state_machine import OrderStateMachine
from app.utils.enums import OrderStatus


class TestOrderStateMachine:
    """Test order state machine."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.state_machine = OrderStateMachine()
    
    def test_new_to_confirmed(self):
        """Test transition from NEW to CONFIRMED."""
        assert self.state_machine.can_transition(
            OrderStatus.NEW, OrderStatus.CONFIRMED
        ) is True
    
    def test_new_to_cancelled(self):
        """Test transition from NEW to CANCELLED."""
        assert self.state_machine.can_transition(
            OrderStatus.NEW, OrderStatus.CANCELLED
        ) is True
    
    def test_new_to_delivered_invalid(self):
        """Test that NEW to DELIVERED is invalid."""
        assert self.state_machine.can_transition(
            OrderStatus.NEW, OrderStatus.DELIVERED
        ) is False
    
    def test_delivered_is_terminal(self):
        """Test that DELIVERED is terminal state."""
        assert self.state_machine.is_terminal(OrderStatus.DELIVERED) is True
        assert len(self.state_machine.get_allowed_transitions(OrderStatus.DELIVERED)) == 0
    
    def test_cancelled_is_terminal(self):
        """Test that CANCELLED is terminal state."""
        assert self.state_machine.is_terminal(OrderStatus.CANCELLED) is True
    
    def test_full_pipeline_transitions(self):
        """Test full order pipeline transitions."""
        pipeline = [
            (OrderStatus.NEW, OrderStatus.CONFIRMED),
            (OrderStatus.CONFIRMED, OrderStatus.PAID),
            (OrderStatus.PAID, OrderStatus.IN_PROGRESS),
            (OrderStatus.IN_PROGRESS, OrderStatus.READY),
            (OrderStatus.READY, OrderStatus.PACKED),
            (OrderStatus.PACKED, OrderStatus.ASSIGNED),
            (OrderStatus.ASSIGNED, OrderStatus.IN_DELIVERY),
            (OrderStatus.IN_DELIVERY, OrderStatus.DELIVERED),
        ]
        
        for from_status, to_status in pipeline:
            assert self.state_machine.can_transition(from_status, to_status) is True


class TestValidators:
    """Test validators."""
    
    def test_phone_validation(self):
        """Test phone number validation."""
        from app.utils.validators import Validators
        
        # Valid phones
        assert Validators.validate_phone("+79123456789") == "+79123456789"
        assert Validators.validate_phone("89123456789") == "+79123456789"
        assert Validators.validate_phone("+7 (912) 345-67-89") == "+79123456789"
        
        # Invalid phones
        with pytest.raises(Exception):
            Validators.validate_phone("123")  # Too short
    
    def test_price_validation(self):
        """Test price validation."""
        from app.utils.validators import Validators
        
        assert Validators.validate_price(100.50) == 100.50
        assert Validators.validate_price(0) == 0.0
        
        with pytest.raises(Exception):
            Validators.validate_price(-10)  # Negative


class TestFormatters:
    """Test formatters."""
    
    def test_price_formatting(self):
        """Test price formatting."""
        from app.utils.formatters import Formatters
        
        assert Formatters.format_price(100.50) == "100.50 ₽"
        assert Formatters.format_price(0) == "0.00 ₽"
    
    def test_order_number_formatting(self):
        """Test order number formatting."""
        from app.utils.formatters import Formatters
        
        assert Formatters.format_order_number("20260205-0001") == "#20260205-0001"
    
    def test_status_formatting(self):
        """Test status formatting."""
        from app.utils.formatters import Formatters
        
        assert "Новый" in Formatters.format_order_status("NEW")
        assert "Доставлен" in Formatters.format_order_status("DELIVERED")
