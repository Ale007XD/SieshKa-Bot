"""Modifier models for product customizations."""

from typing import List

from sqlalchemy import Boolean, String, Integer, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class Modifier(BaseModel):
    """Modifier definition (e.g., 'Size', 'Toppings')."""
    
    __tablename__ = "modifiers"
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=True)
    is_required: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_multiple: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # Allow multiple selections
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Relationships
    options: Mapped[List["ModifierOption"]] = relationship("ModifierOption", back_populates="modifier", lazy="dynamic")
    product_links: Mapped[List["ProductModifier"]] = relationship("ProductModifier", back_populates="modifier")
    
    def __repr__(self):
        return f"<Modifier(id={self.id}, name={self.name})>"


class ModifierOption(BaseModel):
    """Individual modifier options (e.g., 'Large', 'Extra Cheese')."""
    
    __tablename__ = "modifier_options"
    
    modifier_id: Mapped[int] = mapped_column(ForeignKey("modifiers.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    price_adjustment: Mapped[float] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Relationships
    modifier: Mapped["Modifier"] = relationship("Modifier", back_populates="options")
    
    def __repr__(self):
        return f"<ModifierOption(id={self.id}, name={self.name}, adjustment={self.price_adjustment})>"


class ProductModifier(BaseModel):
    """Link table: which modifiers apply to which products."""
    
    __tablename__ = "product_modifiers"
    
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    modifier_id: Mapped[int] = mapped_column(ForeignKey("modifiers.id"), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Relationships
    product: Mapped["Product"] = relationship("Product", back_populates="modifiers")
    modifier: Mapped["Modifier"] = relationship("Modifier", back_populates="product_links")
    
    def __repr__(self):
        return f"<ProductModifier(product_id={self.product_id}, modifier_id={self.modifier_id})>"
