"""Category model for 3-level menu structure."""

from typing import List, Optional

from sqlalchemy import Boolean, String, Integer, ForeignKey, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class Category(BaseModel):
    """Category model supporting 3-level hierarchy."""
    
    __tablename__ = "categories"
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Hierarchy (max 3 levels)
    parent_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("categories.id"),
        nullable=True
    )
    level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)  # 1, 2, or 3
    
    # Archiving
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    archived_at: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), nullable=True)
    archived_by_user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id"),
        nullable=True
    )
    
    # Image
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Relationships
    parent: Mapped[Optional["Category"]] = relationship(
        "Category",
        remote_side="Category.id",
        back_populates="children"
    )
    children: Mapped[List["Category"]] = relationship(
        "Category",
        back_populates="parent",
        lazy="dynamic"
    )
    products: Mapped[List["Product"]] = relationship("Product", back_populates="category", lazy="dynamic")
    archived_by_user: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[archived_by_user_id],
        back_populates="archived_categories"
    )
    
    def __repr__(self):
        return f"<Category(id={self.id}, name={self.name}, level={self.level})>"
    
    def get_full_path(self) -> str:
        """Get full category path."""
        if self.parent:
            return f"{self.parent.get_full_path()} > {self.name}"
        return self.name
