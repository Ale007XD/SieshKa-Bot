"""Staff keyboards."""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_staff_menu_keyboard(role: str) -> InlineKeyboardMarkup:
    """Get staff menu keyboard based on role."""
    keyboards = {
        "manager": InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📋 Меню", callback_data="menu")],
            [InlineKeyboardButton(text="🆕 Новые заказы", callback_data="manager:new_orders")],
            [InlineKeyboardButton(text="📦 Все заказы", callback_data="manager:orders")]
        ]),
        "kitchen": InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📋 Меню", callback_data="menu")],
            [InlineKeyboardButton(text="💳 Заказы к приготовлению", callback_data="kitchen:paid_orders")],
            [InlineKeyboardButton(text="🔥 Готовятся", callback_data="kitchen:in_progress")]
        ]),
        "packer": InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📋 Меню", callback_data="menu")],
            [InlineKeyboardButton(text="🔥 Готовые к упаковке", callback_data="packer:ready_orders")]
        ]),
        "courier": InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📋 Меню", callback_data="menu")],
            [InlineKeyboardButton(text="📦 Доступные заказы", callback_data="courier:available")],
            [InlineKeyboardButton(text="👤 Мои заказы", callback_data="courier:my_orders")]
        ]),
    }
    
    return keyboards.get(role, InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Меню", callback_data="menu")]
    ]))
