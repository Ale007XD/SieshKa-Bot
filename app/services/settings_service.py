"""Settings service for application configuration."""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.settings import AppSettings
from app.utils.exceptions import NotFoundException


class SettingsService:
    """Service for application settings management."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self._cache = None
    
    async def get_settings(self) -> AppSettings:
        """Get application settings (creates default if none exists)."""
        result = await self.session.execute(
            select(AppSettings).limit(1)
        )
        settings = result.scalar_one_or_none()
        
        if not settings:
            # Create default settings
            settings = AppSettings()
            self.session.add(settings)
            await self.session.flush()
            await self.session.commit()
        
        return settings
    
    async def update_settings(
        self,
        company_name: Optional[str] = None,
        company_phone: Optional[str] = None,
        company_address: Optional[str] = None,
        working_hours_start: Optional[str] = None,
        working_hours_end: Optional[str] = None,
        delivery_enabled: Optional[bool] = None,
        delivery_fee: Optional[float] = None,
        free_delivery_threshold: Optional[float] = None,
        min_order_amount: Optional[float] = None,
        auto_confirm_orders: Optional[bool] = None,
        estimated_delivery_time: Optional[int] = None,
        notification_channel_id: Optional[str] = None,
        manager_notification_enabled: Optional[bool] = None,
        cash_payment_enabled: Optional[bool] = None,
        card_courier_enabled: Optional[bool] = None,
        transfer_payment_enabled: Optional[bool] = None,
        transfer_details: Optional[str] = None
    ) -> AppSettings:
        """Update application settings."""
        settings = await self.get_settings()
        
        if company_name is not None:
            settings.company_name = company_name
        if company_phone is not None:
            settings.company_phone = company_phone
        if company_address is not None:
            settings.company_address = company_address
        if working_hours_start is not None:
            settings.working_hours_start = working_hours_start
        if working_hours_end is not None:
            settings.working_hours_end = working_hours_end
        if delivery_enabled is not None:
            settings.delivery_enabled = delivery_enabled
        if delivery_fee is not None:
            settings.delivery_fee = delivery_fee
        if free_delivery_threshold is not None:
            settings.free_delivery_threshold = free_delivery_threshold
        if min_order_amount is not None:
            settings.min_order_amount = min_order_amount
        if auto_confirm_orders is not None:
            settings.auto_confirm_orders = auto_confirm_orders
        if estimated_delivery_time is not None:
            settings.estimated_delivery_time = estimated_delivery_time
        if notification_channel_id is not None:
            settings.notification_channel_id = notification_channel_id
        if manager_notification_enabled is not None:
            settings.manager_notification_enabled = manager_notification_enabled
        if cash_payment_enabled is not None:
            settings.cash_payment_enabled = cash_payment_enabled
        if card_courier_enabled is not None:
            settings.card_courier_enabled = card_courier_enabled
        if transfer_payment_enabled is not None:
            settings.transfer_payment_enabled = transfer_payment_enabled
        if transfer_details is not None:
            settings.transfer_details = transfer_details
        
        await self.session.flush()
        await self.session.commit()
        self._cache = None  # Invalidate cache
        
        return settings
    
    async def is_payment_method_enabled(self, method: str) -> bool:
        """Check if a payment method is enabled."""
        settings = await self.get_settings()
        
        method_map = {
            "cash": settings.cash_payment_enabled,
            "card_courier": settings.card_courier_enabled,
            "transfer": settings.transfer_payment_enabled
        }
        
        return method_map.get(method, False)
    
    async def get_available_payment_methods(self) -> list:
        """Get list of enabled payment methods."""
        settings = await self.get_settings()
        
        methods = []
        if settings.cash_payment_enabled:
            methods.append(("cash", "Наличные"))
        if settings.card_courier_enabled:
            methods.append(("card_courier", "Картой курьеру"))
        if settings.transfer_payment_enabled:
            methods.append(("transfer", "Перевод"))
        
        return methods
