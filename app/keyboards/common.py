"""Common keyboards."""

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from app.models.user import User


def get_main_menu_keyboard(user: User) -> ReplyKeyboardMarkup:
    """Get main menu keyboard based on user role."""
    if user.is_admin():
        buttons = [
            [KeyboardButton(text="📋 Меню"), KeyboardButton(text="🛒 Корзина")],
            [KeyboardButton(text="👑 Админ-панель")]
        ]
    elif user.is_staff():
        role_buttons = {
            "manager": [KeyboardButton(text="📋 Панель менеджера")],
            "kitchen": [KeyboardButton(text="👨‍🍳 Панель кухни")],
            "packer": [KeyboardButton(text="📦 Панель упаковщика")],
            "courier": [KeyboardButton(text="🚚 Панель курьера")],
        }
        buttons = [
            [KeyboardButton(text="📋 Меню"), KeyboardButton(text="🛒 Корзина")],
            role_buttons.get(user.role, [])
        ]
    else:
        buttons = [
            [KeyboardButton(text="📋 Меню"), KeyboardButton(text="🛒 Корзина")],
            [KeyboardButton(text="📦 Мои заказы")]
        ]
    
    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True
    )


def confirm_keyboard(confirm_callback: str, cancel_callback: str = "back") -> InlineKeyboardMarkup:
    """Get confirmation keyboard."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Да", callback_data=confirm_callback),
            InlineKeyboardButton(text="❌ Нет", callback_data=cancel_callback)
        ]
    ])


def back_keyboard(back_callback: str = "back") -> InlineKeyboardMarkup:
    """Get back button keyboard."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data=back_callback)]
    ])
