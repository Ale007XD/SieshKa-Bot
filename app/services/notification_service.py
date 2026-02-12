"""Notification service for sending notifications."""

from typing import Optional, List
import logging

from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from app.models.order import Order
from app.models.user import User
from app.utils.enums import UserRole
from app.utils.enums import OrderStatus

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for sending notifications."""
    
    def __init__(self, bot: Optional[Bot] = None):
        self.bot = bot
    
    async def notify_order_created(self, order: Order) -> None:
        """Notify about new order."""
        if not self.bot:
            return
        
        try:
            message = (
                f"📦 <b>Новый заказ #{order.order_number}</b>\n\n"
                f"👤 Клиент: {order.user.full_name}\n"
                f"📞 Телефон: {order.delivery_phone}\n"
                f"💰 Сумма: {order.total:.2f} ₽\n"
                f"💳 Оплата: {self._format_payment_method(order.payment_method)}\n\n"
                f"📍 Адрес: {order.delivery_address}"
            )
            
            # Notify managers
            await self._notify_staff(UserRole.MANAGER.value, message)
            
        except Exception as e:
            logger.error(f"Failed to notify order created: {e}")
    
    async def notify_order_status_changed(
        self,
        order: Order,
        old_status: str,
        new_status: str
    ) -> None:
        """Notify about order status change."""
        if not self.bot:
            return
        
        try:
            # Notify customer
            status_messages = {
                OrderStatus.CONFIRMED.value: f"✅ Заказ #{order.order_number} подтвержден!",
                OrderStatus.IN_PROGRESS.value: f"👨‍🍳 Заказ #{order.order_number} готовится",
                OrderStatus.READY.value: f"🔥 Заказ #{order.order_number} готов к упаковке",
                OrderStatus.PACKED.value: f"📦 Заказ #{order.order_number} упакован",
                OrderStatus.IN_DELIVERY.value: f"🚚 Заказ #{order.order_number} в пути",
                OrderStatus.DELIVERED.value: f"🎉 Заказ #{order.order_number} доставлен!",
                OrderStatus.CANCELLED.value: f"❌ Заказ #{order.order_number} отменен",
            }
            
            message = status_messages.get(
                new_status,
                f"Статус заказа #{order.order_number} изменен: {new_status}"
            )
            
            await self.bot.send_message(order.user.telegram_id, message)
            
        except Exception as e:
            logger.error(f"Failed to notify status change: {e}")
    
    async def notify_courier_assigned(
        self,
        order: Order,
        courier: User
    ) -> None:
        """Notify courier about assignment."""
        if not self.bot:
            return
        
        try:
            message = (
                f"🚚 <b>Новый заказ для доставки</b>\n\n"
                f"📦 Заказ: #{order.order_number}\n"
                f"💰 Сумма: {order.total:.2f} ₽\n"
                f"📞 Телефон: {order.delivery_phone}\n\n"
                f"📍 Адрес: {order.delivery_address}"
            )
            
            if order.delivery_comment:
                message += f"\n💬 Комментарий: {order.delivery_comment}"
            
            await self.bot.send_message(courier.telegram_id, message)
            
        except Exception as e:
            logger.error(f"Failed to notify courier: {e}")
    
    async def notify_backup_completed(
        self,
        chat_id: int,
        filename: str,
        size_mb: float,
        success: bool = True
    ) -> None:
        """Notify about backup completion."""
        if not self.bot:
            return
        
        try:
            if success:
                message = (
                    f"📁 <b>Бэкап завершен</b>\n\n"
                    f"Файл: <code>{filename}</code>\n"
                    f"Размер: {size_mb:.2f} MB"
                )
            else:
                message = (
                    f"⚠️ <b>Бэкап завершен с предупреждением</b>\n\n"
                    f"Файл: <code>{filename}</code>\n"
                    f"Размер: {size_mb:.2f} MB\n\n"
                    f"Файл слишком большой для отправки в Telegram. "
                    f"Хранится локально."
                )
            
            await self.bot.send_message(chat_id, message)
            
        except Exception as e:
            logger.error(f"Failed to notify backup: {e}")
    
    async def _notify_staff(self, role: str, message: str) -> None:
        """Notify staff members with specific role."""
        # This would query the database for staff members
        # For now, we'll skip the actual implementation
        pass
    
    def _format_payment_method(self, method: str) -> str:
        """Format payment method for display."""
        methods = {
            "cash": "Наличные",
            "card_courier": "Картой курьеру",
            "transfer": "Перевод",
        }
        return methods.get(method, method)
