"""Product model for menu items."""

from typing import List, Optional

from sqlalchemy import Boolean, String, Integer, ForeignKey, Numeric, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class Product(BaseModel):
    """Product model representing menu items."""
    
    __tablename__ = "products"
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    
    # Category reference
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)
    
    # Availability
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Archiving
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    archived_at: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), nullable=True)
    archived_by_user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id"),
        nullable=True
    )
    
    # Stock management
    stock_quantity: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    track_stock: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Image
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Sorting
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Relationships
    category: Mapped["Category"] = relationship("Category", back_populates="products")
    modifiers: Mapped[List["ProductModifier"]] = relationship("ProductModifier", back_populates="product", lazy="dynamic")
    order_items: Mapped[List["OrderItem"]] = relationship("OrderItem", back_populates="product")
    archived_by_user: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[archived_by_user_id],
        back_populates="archived_products"
    )
    
    def __repr__(self):
        return f"<Product(id={self.id}, name={self.name}, price={self.price})>"
    
    @property
    def is_available(self) -> bool:
        """Check if product is available for ordering."""
        if not self.is_active or self.is_archived:
            return False
        if self.track_stock and self.stock_quantity is not None:
            return self.stock_quantity > 0
        return True
