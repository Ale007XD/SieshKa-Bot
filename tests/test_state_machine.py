"""Tests for state machine."""

import pytest

from app.utils.state_machine import OrderStateMachine
from app.utils.enums import OrderStatus


@pytest.fixture
def state_machine():
    """Create state machine fixture."""
    return OrderStateMachine()


class TestStateMachineBasics:
    """Test basic state machine functionality."""
    
    def test_state_machine_creation(self, state_machine):
        """Test state machine can be created."""
        assert state_machine is not None
        assert isinstance(state_machine.transitions, dict)
    
    def test_get_all_statuses(self, state_machine):
        """Test getting all statuses."""
        statuses = state_machine.get_all_statuses()
        assert len(statuses) == 10
        assert OrderStatus.NEW in statuses
        assert OrderStatus.DELIVERED in statuses
    
    def test_terminal_states(self, state_machine):
        """Test terminal states detection."""
        assert state_machine.is_terminal(OrderStatus.DELIVERED) is True
        assert state_machine.is_terminal(OrderStatus.CANCELLED) is True
        assert state_machine.is_terminal(OrderStatus.NEW) is False
        assert state_machine.is_terminal(OrderStatus.IN_PROGRESS) is False


class TestValidTransitions:
    """Test valid state transitions."""
    
    def test_new_transitions(self, state_machine):
        """Test NEW state transitions."""
        assert state_machine.can_transition(OrderStatus.NEW, OrderStatus.CONFIRMED) is True
        assert state_machine.can_transition(OrderStatus.NEW, OrderStatus.CANCELLED) is True
        
        # Invalid transitions
        assert state_machine.can_transition(OrderStatus.NEW, OrderStatus.DELIVERED) is False
        assert state_machine.can_transition(OrderStatus.NEW, OrderStatus.PAID) is False
    
    def test_confirmed_transitions(self, state_machine):
        """Test CONFIRMED state transitions."""
        assert state_machine.can_transition(OrderStatus.CONFIRMED, OrderStatus.PAID) is True
        assert state_machine.can_transition(OrderStatus.CONFIRMED, OrderStatus.CANCELLED) is True
        
        assert state_machine.can_transition(OrderStatus.CONFIRMED, OrderStatus.NEW) is False
    
    def test_paid_transitions(self, state_machine):
        """Test PAID state transitions."""
        assert state_machine.can_transition(OrderStatus.PAID, OrderStatus.IN_PROGRESS) is True
        assert state_machine.can_transition(OrderStatus.PAID, OrderStatus.CANCELLED) is True
    
    def test_pipeline_transitions(self, state_machine):
        """Test standard order pipeline."""
        pipeline = [
            OrderStatus.NEW,
            OrderStatus.CONFIRMED,
            OrderStatus.PAID,
            OrderStatus.IN_PROGRESS,
            OrderStatus.READY,
            OrderStatus.PACKED,
            OrderStatus.ASSIGNED,
            OrderStatus.IN_DELIVERY,
            OrderStatus.DELIVERED
        ]
        
        for i in range(len(pipeline) - 1):
            current = pipeline[i]
            next_status = pipeline[i + 1]
            assert state_machine.can_transition(current, next_status) is True, \
                f"Should be able to transition from {current} to {next_status}"


class TestInvalidTransitions:
    """Test invalid state transitions."""
    
    def test_no_backward_transitions(self, state_machine):
        """Test that backward transitions are not allowed."""
        # Can't go back in pipeline
        assert state_machine.can_transition(OrderStatus.PAID, OrderStatus.CONFIRMED) is False
        assert state_machine.can_transition(OrderStatus.IN_PROGRESS, OrderStatus.PAID) is False
        assert state_machine.can_transition(OrderStatus.DELIVERED, OrderStatus.IN_DELIVERY) is False
    
    def test_terminal_no_transitions(self, state_machine):
        """Test that terminal states have no outgoing transitions."""
        delivered_transitions = state_machine.get_allowed_transitions(OrderStatus.DELIVERED)
        cancelled_transitions = state_machine.get_allowed_transitions(OrderStatus.CANCELLED)
        
        assert len(delivered_transitions) == 0
        assert len(cancelled_transitions) == 0
    
    def test_skip_transitions_invalid(self, state_machine):
        """Test that skipping steps is not allowed."""
        assert state_machine.can_transition(OrderStatus.NEW, OrderStatus.IN_PROGRESS) is False
        assert state_machine.can_transition(OrderStatus.CONFIRMED, OrderStatus.READY) is False
        assert state_machine.can_transition(OrderStatus.PAID, OrderStatus.DELIVERED) is False
