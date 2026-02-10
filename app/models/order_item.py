"""OrderItem model for order line items."""

from typing import List, Optional

from sqlalchemy import Boolean, String, Integer, ForeignKey, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSON

from app.models.base import BaseModel


class OrderItem(BaseModel):
    """Order item representing a product in an order."""
    
    __tablename__ = "order_items"
    
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    
    # Snapshot of product data at order time
    product_name: Mapped[str] = mapped_column(String(255), nullable=False)
    product_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    
    # Quantity
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    
    # Modifiers (stored as JSON for flexibility)
    modifiers: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    modifiers_price: Mapped[float] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    
    # Item total
    item_total: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    
    # Special instructions
    special_instructions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationships
    order: Mapped["Order"] = relationship("Order", back_populates="items")
    product: Mapped["Product"] = relationship("Product", back_populates="order_items")
    
    def __repr__(self):
        return f"<OrderItem(id={self.id}, order_id={self.order_id}, product={self.product_name})>"
    
    def calculate_total(self) -> float:
        """Calculate item total including modifiers."""
        base = float(self.product_price) * self.quantity
        modifiers = float(self.modifiers_price) * self.quantity
        return base + modifiers
