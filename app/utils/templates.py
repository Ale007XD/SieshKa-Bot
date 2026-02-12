"""Message templates for Telegram bot."""

from typing import List

from app.models.order import Order
from app.utils.enums import UserRole
from app.utils.formatters import Formatters


class Templates:
    """Message templates for the bot."""
    
    @staticmethod
    def welcome_message(first_name: str) -> str:
        """Welcome message for new users."""
        return (
            f"👋 Привет, {first_name}!\n\n"
            f"Добро пожаловать в наш бот доставки еды! 🍕\n\n"
            f"Здесь вы можете:\n"
            f"• 📋 Просмотреть меню\n"
            f"• 🛒 Сделать заказ\n"
            f"• 📦 Отследить статус доставки\n\n"
            f"Используйте меню ниже для навигации 👇"
        )
    
    @staticmethod
    def menu_header() -> str:
        """Menu header message."""
        return "📋 <b>Наше меню</b>\n\nВыберите категорию:"
    
    @staticmethod
    def category_empty() -> str:
        """Empty category message."""
        return "😔 В этой категории пока нет товаров"
    
    @staticmethod
    def product_details(
        name: str,
        price: float,
        description: str = None
    ) -> str:
        """Product details message."""
        text = f"<b>{name}</b>\n"
        text += f"💰 {Formatters.format_price(price)}\n"
        
        if description:
            text += f"\n{description}"
        
        return text
    
    @staticmethod
    def cart_header() -> str:
        """Cart header message."""
        return "🛒 <b>Ваша корзина</b>\n\n"
    
    @staticmethod
    def cart_item(
        index: int,
        name: str,
        quantity: int,
        price: float
    ) -> str:
        """Single cart item line."""
        total = price * quantity
        return f"{index}. {name} x{quantity} = {Formatters.format_price(total)}\n"
    
    @staticmethod
    def cart_footer(subtotal: float) -> str:
        """Cart footer with total."""
        return f"\n<b>Итого:</b> {Formatters.format_price(subtotal)}"
    
    @staticmethod
    def empty_cart() -> str:
        """Empty cart message."""
        return "🛒 <b>Ваша корзина пуста</b>\n\nДобавьте товары из меню"
    
    @staticmethod
    def order_confirmation(order: Order) -> str:
        """Order confirmation message."""
        text = f"📦 <b>Заказ подтвержден!</b>\n\n"
        text += f"Номер заказа: {Formatters.format_order_number(order.order_number)}\n"
        text += f"Сумма: {Formatters.format_price(order.total)}\n"
        text += f"Оплата: {Formatters.format_payment_method(order.payment_method)}\n\n"
        text += f"📍 Адрес: {order.delivery_address}\n"
        text += f"📞 Телефон: {Formatters.format_phone(order.delivery_phone)}\n\n"
        text += "Спасибо за заказ! Мы скоро свяжемся с вами."
        
        return text
    
    @staticmethod
    def order_details(order: Order) -> str:
        """Order details message."""
        text = f"📦 <b>Заказ {Formatters.format_order_number(order.order_number)}</b>\n\n"
        
        # Status
        text += f"Статус: {Formatters.format_order_status(order.status)}\n"
        text += f"Дата: {Formatters.format_datetime(order.created_at)}\n\n"
        
        # Items
        text += "<b>Состав заказа:</b>\n"
        for item in order.items:
            text += f"• {item.product_name} x{item.quantity}\n"
        
        # Totals
        text += f"\n<b>Сумма:</b> {Formatters.format_price(order.subtotal)}\n"
        if order.delivery_fee:
            text += f"<b>Доставка:</b> {Formatters.format_price(order.delivery_fee)}\n"
        if order.discount_amount:
            text += f"<b>Скидка:</b> -{Formatters.format_price(order.discount_amount)}\n"
        text += f"<b>Итого:</b> {Formatters.format_price(order.total)}\n\n"
        
        # Delivery info
        text += f"📍 Адрес: {order.delivery_address}\n"
        text += f"📞 Телефон: {Formatters.format_phone(order.delivery_phone)}\n"
        text += f"💳 Оплата: {Formatters.format_payment_method(order.payment_method)}"
        
        if order.delivery_comment:
            text += f"\n💬 Комментарий: {order.delivery_comment}"
        
        return text
    
    @staticmethod
    def help_message() -> str:
        """Help message."""
        return (
            "📋 <b>Справка по использованию бота</b>\n\n"
            "<b>Основные команды:</b>\n"
            "• /start — Начать работу с ботом\n"
            "• /menu — Открыть меню\n"
            "• /cart — Показать корзину\n"
            "• /orders — История заказов\n"
            "• /help — Показать эту справку\n\n"
            "<b>Как сделать заказ:</b>\n"
            "1. Выберите категорию в меню\n"
            "2. Выберите товар и добавьте в корзину\n"
            "3. Перейдите в корзину и нажмите 'Оформить заказ'\n"
            "4. Укажите адрес доставки и телефон\n"
            "5. Подтвердите заказ\n\n"
            "Если у вас есть вопросы, свяжитесь с нами!"
        )
    
    @staticmethod
    def admin_panel() -> str:
        """Admin panel message."""
        return (
            "👑 <b>Панель администратора</b>\n\n"
            "Выберите действие:\n"
            "• 📋 Управление меню\n"
            "• 📦 Управление заказами\n"
            "• 👥 Управление персоналом\n"
            "• 📊 Статистика\n"
            "• ⚙️ Настройки"
        )
    
    @staticmethod
    def staff_panel(role: str) -> str:
        """Staff panel message based on role."""
        panels = {
            UserRole.MANAGER.value: (
                "📋 <b>Панель менеджера</b>\n\n"
                "• 📦 Новые заказы\n"
                "• ✅ Подтверждение заказов\n"
                "• 💳 Управление оплатами"
            ),
            UserRole.KITCHEN.value: (
                "👨‍🍳 <b>Панель кухни</b>\n\n"
                "• 📋 Заказы в работе\n"
                "• 🔥 Отметить готовым"
            ),
            UserRole.PACKER.value: (
                "📦 <b>Панель упаковщика</b>\n\n"
                "• 🔥 Готовые блюда\n"
                "• 📦 Отметить упакованным"
            ),
            UserRole.COURIER.value: (
                "🚚 <b>Панель курьера</b>\n\n"
                "• 📦 Заказы на доставку\n"
                "• 🚚 Взять в доставку\n"
                "• 🎉 Отметить доставленным"
            ),
        }
        return panels.get(role, "🔧 <b>Панель сотрудника</b>")
