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

# Convenience role groupings for quick role checks across modules
STAFF_ROLES = {
    UserRole.ADMIN.value,
    UserRole.MANAGER.value,
    UserRole.KITCHEN.value,
    UserRole.PACKER.value,
    UserRole.COURIER.value,
}
CLIENT_ROLES = {UserRole.CLIENT.value}
ADMIN_ROLES = {UserRole.ADMIN.value}
MANAGER_ROLES = {UserRole.MANAGER.value}

# SAVED: 2026-02-12 09:56:25
