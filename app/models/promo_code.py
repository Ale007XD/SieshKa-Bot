"""PromoCode model for v1.1 (prepared but safe when disabled)."""

from typing import List, Optional
from datetime import datetime, timezone

from sqlalchemy import Boolean, String, Integer, Numeric, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class PromoCode(BaseModel):
    """Promo code model for discounts (v1.1 feature)."""
    
    __tablename__ = "promo_codes"
    
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Discount type
    discount_type: Mapped[str] = mapped_column(String(10), default="fixed", nullable=False)  # fixed or percent
    discount_value: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    
    # Limits
    max_uses: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    current_uses: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    min_order_amount: Mapped[float] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    max_discount_amount: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)
    
    # Validity period
    valid_from: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), nullable=True)
    valid_until: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Relationships
    orders: Mapped[List["Order"]] = relationship("Order", back_populates="promo_code")
    
    def __repr__(self):
        return f"<PromoCode(id={self.id}, code={self.code})>"
    
    def is_valid(self) -> bool:
        """Check if promo code is currently valid."""
        if not self.is_active:
            return False
        
        now = datetime.now(timezone.utc)
        
        if self.valid_from and now < self.valid_from:
            return False
        
        if self.valid_until and now > self.valid_until:
            return False
        
        if self.max_uses is not None and self.current_uses >= self.max_uses:
            return False
        
        return True
    
    def calculate_discount(self, order_total: float) -> float:
        """Calculate discount amount for given order total."""
        if not self.is_valid():
            return 0.0
        
        if order_total < self.min_order_amount:
            return 0.0
        
        if self.discount_type == "percent":
            discount = order_total * (self.discount_value / 100)
        else:
            discount = self.discount_value
        
        if self.max_discount_amount:
            discount = min(discount, self.max_discount_amount)
        
        return float(discount)
