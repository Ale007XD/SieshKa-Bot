"""Staff keyboards."""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.utils.enums import UserRole


def get_staff_menu_keyboard(role: str) -> InlineKeyboardMarkup:
    """Get staff menu keyboard based on role."""
    keyboards = {
        UserRole.MANAGER.value: InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📋 Меню", callback_data="menu")],
            [InlineKeyboardButton(text="🆕 Новые заказы", callback_data="manager:new_orders")],
            [InlineKeyboardButton(text="📦 Все заказы", callback_data="manager:orders")]
        ]),
        UserRole.KITCHEN.value: InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📋 Меню", callback_data="menu")],
            [InlineKeyboardButton(text="💳 Заказы к приготовлению", callback_data="kitchen:paid_orders")],
            [InlineKeyboardButton(text="🔥 Готовятся", callback_data="kitchen:in_progress")]
        ]),
        UserRole.PACKER.value: InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📋 Меню", callback_data="menu")],
            [InlineKeyboardButton(text="🔥 Готовые к упаковке", callback_data="packer:ready_orders")]
        ]),
        UserRole.COURIER.value: InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📋 Меню", callback_data="menu")],
            [InlineKeyboardButton(text="📦 Доступные заказы", callback_data="courier:available")],
            [InlineKeyboardButton(text="👤 Мои заказы", callback_data="courier:my_orders")]
        ]),
    }
    
    return keyboards.get(role, InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Меню", callback_data="menu")]
    ]))
