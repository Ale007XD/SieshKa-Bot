"""Formatters for displaying data."""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional


class Formatters:
    """Data formatting utilities."""
    
    @staticmethod
    def format_price(price: float) -> str:
        """Format price with currency."""
        return f"{price:.2f} ₽"
    
    @staticmethod
    def format_order_number(order_number: str) -> str:
        """Format order number for display."""
        return f"#{order_number}"
    
    @staticmethod
    def format_phone(phone: str) -> str:
        """Format phone number for display."""
        if not phone:
            return ""
        
        # Remove + for formatting
        digits = phone.replace('+', '').replace('-', '').replace(' ', '')
        
        if len(digits) == 11 and digits.startswith('7'):
            # Russian format: +7 (XXX) XXX-XX-XX
            return f"+7 ({digits[1:4]}) {digits[4:7]}-{digits[7:9]}-{digits[9:11]}"
        
        return phone
    
    @staticmethod
    def format_datetime(dt: Optional[datetime]) -> str:
        """Format datetime for display."""
        if not dt:
            return "—"
        
        return dt.strftime("%d.%m.%Y %H:%M")
    
    @staticmethod
    def format_date(d: Optional[date]) -> str:
        """Format date for display."""
        if not d:
            return "—"
        
        return d.strftime("%d.%m.%Y")
    
    @staticmethod
    def format_order_status(status: str) -> str:
        """Format order status for display."""
        status_map = {
            "NEW": "🆕 Новый",
            "CONFIRMED": "✅ Подтвержден",
            "PAID": "💳 Оплачен",
            "IN_PROGRESS": "👨‍🍳 Готовится",
            "READY": "🔥 Готов",
            "PACKED": "📦 Упакован",
            "ASSIGNED": "👤 Назначен",
            "IN_DELIVERY": "🚚 В пути",
            "DELIVERED": "🎉 Доставлен",
            "CANCELLED": "❌ Отменен",
        }
        return status_map.get(status, status)
    
    @staticmethod
    def format_payment_method(method: str) -> str:
        """Format payment method for display."""
        method_map = {
            "cash": "💵 Наличные",
            "card_courier": "💳 Картой курьеру",
            "transfer": "🏦 Перевод",
        }
        return method_map.get(method, method)
    
    @staticmethod
    def format_user_role(role: str) -> str:
        """Format user role for display."""
        role_map = {
            "client": "👤 Клиент",
            "admin": "👑 Администратор",
            "manager": "📋 Менеджер",
            "kitchen": "👨‍🍳 Кухня",
            "packer": "📦 Упаковщик",
            "courier": "🚚 Курьер",
        }
        return role_map.get(role, role)
    
    @staticmethod
    def truncate_text(text: str, max_length: int = 100) -> str:
        """Truncate text to max length with ellipsis."""
        if not text:
            return ""
        
        if len(text) <= max_length:
            return text
        
        return text[:max_length - 3] + "..."
