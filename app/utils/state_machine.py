"""State machine for order status transitions."""

from typing import Set, Dict, List

from app.utils.enums import OrderStatus


class OrderStateMachine:
    """State machine defining valid order status transitions."""
    
    def __init__(self):
        # Define valid transitions
        self.transitions: Dict[OrderStatus, Set[OrderStatus]] = {
            OrderStatus.NEW: {
                OrderStatus.CONFIRMED,
                OrderStatus.CANCELLED
            },
            OrderStatus.CONFIRMED: {
                OrderStatus.PAID,
                OrderStatus.CANCELLED
            },
            OrderStatus.PAID: {
                OrderStatus.IN_PROGRESS,
                OrderStatus.CANCELLED
            },
            OrderStatus.IN_PROGRESS: {
                OrderStatus.READY,
                OrderStatus.CANCELLED
            },
            OrderStatus.READY: {
                OrderStatus.PACKED,
                OrderStatus.CANCELLED
            },
            OrderStatus.PACKED: {
                OrderStatus.ASSIGNED,
                OrderStatus.CANCELLED
            },
            OrderStatus.ASSIGNED: {
                OrderStatus.IN_DELIVERY,
                OrderStatus.CANCELLED
            },
            OrderStatus.IN_DELIVERY: {
                OrderStatus.DELIVERED,
                OrderStatus.CANCELLED
            },
            OrderStatus.DELIVERED: set(),  # Terminal state
            OrderStatus.CANCELLED: set()    # Terminal state
        }
    
    def can_transition(
        self,
        from_status: OrderStatus,
        to_status: OrderStatus
    ) -> bool:
        """Check if transition from from_status to to_status is valid."""
        if from_status not in self.transitions:
            return False
        
        return to_status in self.transitions[from_status]
    
    def get_allowed_transitions(self, status: OrderStatus) -> List[OrderStatus]:
        """Get list of allowed next statuses."""
        if status not in self.transitions:
            return []
        
        return list(self.transitions[status])
    
    def get_all_statuses(self) -> List[OrderStatus]:
        """Get all order statuses."""
        return list(OrderStatus)
    
    def is_terminal(self, status: OrderStatus) -> bool:
        """Check if status is terminal (no further transitions)."""
        if status not in self.transitions:
            return True
        
        return len(self.transitions[status]) == 0
