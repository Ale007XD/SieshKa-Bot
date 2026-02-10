"""Review model for v1.1 (prepared but safe when disabled)."""

from typing import Optional

from sqlalchemy import Boolean, String, Integer, ForeignKey, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class Review(BaseModel):
    """Review model for customer feedback (v1.1 feature)."""
    
    __tablename__ = "reviews"
    
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False)
    
    # Ratings (1-5)
    food_rating: Mapped[int] = mapped_column(Integer, nullable=False)
    delivery_rating: Mapped[int] = mapped_column(Integer, nullable=False)
    service_rating: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Overall rating (calculated)
    overall_rating: Mapped[float] = mapped_column(Numeric(3, 2), nullable=False)
    
    # Comment
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Moderation
    is_approved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_visible: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    moderated_by_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    
    # Response from admin/manager
    response: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    responded_by_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    
    def __repr__(self):
        return f"<Review(id={self.id}, order_id={self.order_id}, rating={self.overall_rating})>"
    
    def calculate_overall(self) -> float:
        """Calculate overall rating from individual ratings."""
        return round((self.food_rating + self.delivery_rating + self.service_rating) / 3, 2)
