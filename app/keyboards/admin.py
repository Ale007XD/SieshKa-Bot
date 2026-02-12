"""Admin keyboards."""

from typing import List

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from app.models.category import Category
from app.models.product import Product
from app.models.user import User
from app.utils.enums import UserRole
from sqlalchemy import select


def get_admin_menu_keyboard() -> InlineKeyboardMarkup:
    """Get admin main menu keyboard."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Управление меню", callback_data="admin:menu")],
        [InlineKeyboardButton(text="📦 Управление заказами", callback_data="admin:orders")],
        [InlineKeyboardButton(text="👥 Управление персоналом", callback_data="admin:staff")],
        [InlineKeyboardButton(text="📦 Архив", callback_data="admin:archive")],
        [InlineKeyboardButton(text="📊 Статистика", callback_data="admin:stats")],
        [InlineKeyboardButton(text="⚙️ Настройки", callback_data="admin:settings")],
    ])


def get_menu_management_keyboard() -> InlineKeyboardMarkup:
    """Get menu management keyboard."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📁 Категории", callback_data="admin:categories")],
        [InlineKeyboardButton(text="🍽 Товары", callback_data="admin:products")],
        [InlineKeyboardButton(text="🔧 Модификаторы", callback_data="admin:modifiers")],
        [InlineKeyboardButton(text="📥 Импорт/Экспорт", callback_data="admin:import_export")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back")]
    ])


def get_category_management_keyboard(categories: List[Category]) -> InlineKeyboardMarkup:
    """Get category management keyboard."""
    buttons = []
    
    for category in categories:
        status = "🟢" if category.is_active else "🔴"
        buttons.append([InlineKeyboardButton(
            text=f"{status} {category.name}",
            callback_data=f"edit_category:{category.id}"
        )])
    
    buttons.append([InlineKeyboardButton(
        text="➕ Добавить категорию",
        callback_data="add_category"
    )])
    
    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="admin:menu")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_product_management_keyboard(categories: List[Category]) -> InlineKeyboardMarkup:
    """Get product management keyboard."""
    buttons = []
    
    for category in categories:
        buttons.append([InlineKeyboardButton(
            text=f"📁 {category.name}",
            callback_data=f"manage_category_products:{category.id}"
        )])
    
    buttons.append([InlineKeyboardButton(
        text="➕ Добавить товар",
        callback_data="add_product"
    )])
    
    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="admin:menu")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_archive_management_keyboard(
    categories: List[Category],
    products: List[Product]
) -> InlineKeyboardMarkup:
    """Get archive management keyboard."""
    buttons = []
    
    buttons.append([InlineKeyboardButton(
        text=f"📁 Архивированные категории ({len(categories)})",
        callback_data="archive:view_categories"
    )])
    
    buttons.append([InlineKeyboardButton(
        text=f"🍽 Архивированные товары ({len(products)})",
        callback_data="archive:view_products"
    )])
    
    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="back")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_staff_management_keyboard(staff: List[User]) -> InlineKeyboardMarkup:
    """Get staff management keyboard."""
    buttons = []
    
    for member in staff:
        role_emoji = {
            UserRole.ADMIN.value: "👑",
            UserRole.MANAGER.value: "📋",
            UserRole.KITCHEN.value: "👨‍🍳",
            UserRole.PACKER.value: "📦",
            UserRole.COURIER.value: "🚚"
        }.get(member.role, "👤")
        
        buttons.append([InlineKeyboardButton(
            text=f"{role_emoji} {member.full_name} ({member.role})",
            callback_data=f"edit_staff:{member.id}"
        )])
    
    buttons.append([InlineKeyboardButton(
        text="➕ Добавить сотрудника",
        callback_data="staff:add"
    )])
    
    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="back")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


 # edit_category handler moved to app/handlers/admin.py; removed from keyboard module to avoid routing conflicts


def get_order_management_keyboard() -> InlineKeyboardMarkup:
    """Get order management keyboard."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🆕 Новые", callback_data="admin:orders:new")],
        [InlineKeyboardButton(text="✅ Подтвержденные", callback_data="admin:orders:confirmed")],
        [InlineKeyboardButton(text="👨‍🍳 Готовятся", callback_data="admin:orders:in_progress")],
        [InlineKeyboardButton(text="🚚 В доставке", callback_data="admin:orders:in_delivery")],
        [InlineKeyboardButton(text="📊 Все заказы", callback_data="admin:orders:all")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back")]
    ])


def get_statistics_keyboard() -> InlineKeyboardMarkup:
    """Get statistics keyboard."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📅 За сегодня", callback_data="stats:today")],
        [InlineKeyboardButton(text="📆 За неделю", callback_data="stats:week")],
        [InlineKeyboardButton(text="📈 За месяц", callback_data="stats:month")],
        [InlineKeyboardButton(text="🏆 Топ товаров", callback_data="stats:top_products")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back")]
    ])
