"""Enums for the application."""

from enum import Enum


class UserRole(str, Enum):
    """User roles in the system."""
    CLIENT = "client"
    ADMIN = "admin"
    MANAGER = "manager"
    KITCHEN = "kitchen"
    PACKER = "packer"
    COURIER = "courier"


class OrderStatus(str, Enum):
    """Order statuses in the lifecycle."""
    NEW = "NEW"
    CONFIRMED = "CONFIRMED"
    PAID = "PAID"
    IN_PROGRESS = "IN_PROGRESS"
    READY = "READY"
    PACKED = "PACKED"
    ASSIGNED = "ASSIGNED"
    IN_DELIVERY = "IN_DELIVERY"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


class PaymentMethod(str, Enum):
    """Payment methods available."""
    CASH = "cash"
    CARD_COURIER = "card_courier"
    TRANSFER = "transfer"


class PaymentStatus(str, Enum):
    """Payment statuses."""
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"


class DiscountType(str, Enum):
    """Discount types for promo codes."""
    FIXED = "fixed"
    PERCENT = "percent"
