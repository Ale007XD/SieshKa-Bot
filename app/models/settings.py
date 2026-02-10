"""Settings model for application configuration."""

from typing import Optional

from sqlalchemy import Boolean, String, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class AppSettings(BaseModel):
    """Application settings stored in database."""
    
    __tablename__ = "app_settings"
    
    # Company info
    company_name: Mapped[str] = mapped_column(String(255), default="Food Delivery", nullable=False)
    company_phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    company_address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Working hours
    working_hours_start: Mapped[str] = mapped_column(String(5), default="09:00", nullable=False)
    working_hours_end: Mapped[str] = mapped_column(String(5), default="22:00", nullable=False)
    
    # Delivery settings
    delivery_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    delivery_fee: Mapped[float] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    free_delivery_threshold: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)
    min_order_amount: Mapped[float] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    
    # Order settings
    auto_confirm_orders: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    estimated_delivery_time: Mapped[int] = mapped_column(default=60, nullable=False)  # minutes
    
    # Notification settings
    notification_channel_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    manager_notification_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Payment settings
    cash_payment_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    card_courier_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    transfer_payment_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    transfer_details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    def __repr__(self):
        return f"<AppSettings(id={self.id}, company={self.company_name})>"
