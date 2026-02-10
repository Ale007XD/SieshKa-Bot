"""Order and OrderStatusLog models."""

from decimal import Decimal
from typing import List, Optional

from sqlalchemy import Boolean, String, Integer, ForeignKey, Numeric, DateTime, Text, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.utils.enums import OrderStatus, PaymentMethod, PaymentStatus


class Order(BaseModel):
    """Order model representing customer orders."""
    
    __tablename__ = "orders"
    
    # Order number (YYYYMMDD-XXXX format)
    order_number: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    
    # User reference
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    
    # Status
    status: Mapped[str] = mapped_column(
        String(20),
        default=OrderStatus.NEW.value,
        nullable=False
    )
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)  # For optimistic locking
    
    # Payment
    payment_method: Mapped[str] = mapped_column(String(20), nullable=False)
    payment_status: Mapped[str] = mapped_column(
        String(20),
        default=PaymentStatus.PENDING.value,
        nullable=False
    )
    
    # Pricing
    subtotal: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    delivery_fee: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    discount_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    total: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    
    # Delivery information
    delivery_address: Mapped[str] = mapped_column(Text, nullable=False)
    delivery_phone: Mapped[str] = mapped_column(String(20), nullable=False)
    delivery_comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Assigned staff
    courier_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    
    # Timestamps for status tracking
    confirmed_at: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), nullable=True)
    paid_at: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), nullable=True)
    in_progress_at: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), nullable=True)
    ready_at: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), nullable=True)
    packed_at: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), nullable=True)
    assigned_at: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), nullable=True)
    in_delivery_at: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), nullable=True)
    delivered_at: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), nullable=True)
    cancelled_at: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Cancellation reason
    cancellation_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    cancelled_by_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    
    # Promo code (v1.1)
    promo_code_id: Mapped[Optional[int]] = mapped_column(ForeignKey("promo_codes.id"), nullable=True)
    
    # Relationships
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id], back_populates="orders")
    items: Mapped[List["OrderItem"]] = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    status_logs: Mapped[List["OrderStatusLog"]] = relationship("OrderStatusLog", back_populates="order", cascade="all, delete-orphan")
    courier: Mapped[Optional["User"]] = relationship("User", foreign_keys=[courier_id])
    cancelled_by: Mapped[Optional["User"]] = relationship("User", foreign_keys=[cancelled_by_id])
    promo_code: Mapped[Optional["PromoCode"]] = relationship("PromoCode", back_populates="orders")
    
    def __repr__(self):
        return f"<Order(id={self.id}, number={self.order_number}, status={self.status})>"
    
    def is_cancelled(self) -> bool:
        """Check if order is cancelled."""
        return self.status == OrderStatus.CANCELLED.value
    
    def is_delivered(self) -> bool:
        """Check if order is delivered."""
        return self.status == OrderStatus.DELIVERED.value
    
    def can_be_cancelled(self) -> bool:
        """Check if order can be cancelled."""
        return self.status not in [
            OrderStatus.DELIVERED.value,
            OrderStatus.CANCELLED.value,
            OrderStatus.IN_DELIVERY.value
        ]


class OrderStatusLog(BaseModel):
    """Audit log for order status changes."""
    
    __tablename__ = "order_status_logs"
    
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False)
    old_status: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    new_status: Mapped[str] = mapped_column(String(20), nullable=False)
    changed_by_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationships
    order: Mapped["Order"] = relationship("Order", back_populates="status_logs")
    changed_by: Mapped[Optional["User"]] = relationship("User")
    
    def __repr__(self):
        return f"<OrderStatusLog(order_id={self.order_id}, {self.old_status} -> {self.new_status})>"
