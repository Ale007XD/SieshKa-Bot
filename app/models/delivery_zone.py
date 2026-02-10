"""DeliveryZone model for v1.1 (prepared but safe when disabled)."""

from typing import Optional, List

from sqlalchemy import Boolean, String, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSON

from app.models.base import BaseModel


class DeliveryZone(BaseModel):
    """Delivery zone model for geographic restrictions (v1.1 feature)."""
    
    __tablename__ = "delivery_zones"
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Zone boundary (GeoJSON polygon or list of coordinates)
    boundary: Mapped[dict] = mapped_column(JSON, nullable=False)
    
    # Delivery settings for this zone
    delivery_fee: Mapped[float] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    free_delivery_threshold: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)
    min_order_amount: Mapped[float] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    estimated_delivery_time: Mapped[int] = mapped_column(default=60, nullable=False)  # minutes
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    def __repr__(self):
        return f"<DeliveryZone(id={self.id}, name={self.name})>"
