"""Client keyboards."""

from typing import List

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from app.models.category import Category
from app.models.product import Product
from app.services.cart_service import CartItem


def get_client_menu_keyboard() -> InlineKeyboardMarkup:
    """Get client main menu keyboard."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Просмотреть меню", callback_data="view_menu")],
        [InlineKeyboardButton(text="🛒 Корзина", callback_data="view_cart")],
        [InlineKeyboardButton(text="📦 Мои заказы", callback_data="view_orders")],
    ])


def get_categories_keyboard(
    categories: List[Category],
    parent_id: int = None
) -> InlineKeyboardMarkup:
    """Get categories keyboard."""
    buttons = []
    
    for category in categories:
        buttons.append([InlineKeyboardButton(
            text=f"📁 {category.name}",
            callback_data=f"category:{category.id}"
        )])
    
    if parent_id:
        buttons.append([InlineKeyboardButton(
            text="◀️ Назад",
            callback_data="back"
        )])
    else:
        buttons.append([InlineKeyboardButton(
            text="🔄 Обновить меню",
            callback_data="refresh_menu"
        )])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_products_keyboard(
    products: List[Product],
    category_id: int
) -> InlineKeyboardMarkup:
    """Get products keyboard."""
    buttons = []
    
    for product in products:
        price_text = f"{float(product.price):.0f} ₽"
        buttons.append([InlineKeyboardButton(
            text=f"{product.name} — {price_text}",
            callback_data=f"product:{product.id}"
        )])
    
    buttons.append([InlineKeyboardButton(
        text="◀️ Назад к категориям",
        callback_data=f"back_to_category:{category_id}"
    )])
    
    buttons.append([InlineKeyboardButton(
        text="🛒 Корзина",
        callback_data="view_cart"
    )])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_product_detail_keyboard(product: Product) -> InlineKeyboardMarkup:
    """Get product detail keyboard."""
    buttons = [
        [InlineKeyboardButton(
            text="➕ Добавить в корзину",
            callback_data=f"add_to_cart:{product.id}"
        )],
        [InlineKeyboardButton(
            text="◀️ Назад",
            callback_data=f"back_to_category:{product.category_id}"
        )],
        [InlineKeyboardButton(
            text="🛒 Корзина",
            callback_data="view_cart"
        )]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_cart_keyboard(items: List[CartItem]) -> InlineKeyboardMarkup:
    """Get cart keyboard."""
    buttons = []
    
    for idx, item in enumerate(items):
        buttons.append([InlineKeyboardButton(
            text=f"❌ {item.product_name} (x{item.quantity})",
            callback_data=f"remove_from_cart:{idx}"
        )])
    
    buttons.append([
        InlineKeyboardButton(text="🗑 Очистить", callback_data="clear_cart"),
        InlineKeyboardButton(text="💳 Оформить", callback_data="checkout")
    ])
    
    buttons.append([InlineKeyboardButton(
        text="◀️ Продолжить покупки",
        callback_data="view_menu"
    )])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_checkout_keyboard() -> InlineKeyboardMarkup:
    """Get checkout keyboard for client flow."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Оформить заказ", callback_data="checkout")],
        [InlineKeyboardButton(text="◀️ Продолжить покупки", callback_data="view_menu")]
    ])

def get_payment_methods_keyboard(methods: List[tuple]) -> InlineKeyboardMarkup:
    """Get payment methods keyboard."""
    buttons = []
    
    for method_code, method_name in methods:
        buttons.append([InlineKeyboardButton(
            text=method_name,
            callback_data=f"payment:{method_code}"
        )])
    
    buttons.append([InlineKeyboardButton(
        text="◀️ Назад в корзину",
        callback_data="view_cart"
    )])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_orders_keyboard(orders, show_detail: bool = False) -> InlineKeyboardMarkup:
    """Get orders list keyboard."""
    buttons = []
    
    if not show_detail:
        for order in orders:
            from app.utils.formatters import Formatters
            status_emoji = {
                "NEW": "🆕",
                "CONFIRMED": "✅",
                "PAID": "💳",
                "IN_PROGRESS": "👨‍🍳",
                "READY": "🔥",
                "PACKED": "📦",
                "ASSIGNED": "👤",
                "IN_DELIVERY": "🚚",
                "DELIVERED": "🎉",
                "CANCELLED": "❌"
            }.get(order.status, "📦")
            
            buttons.append([InlineKeyboardButton(
                text=f"{status_emoji} #{order.order_number} — {Formatters.format_price(order.total)}",
                callback_data=f"order:{order.id}"
            )])
    
    buttons.append([InlineKeyboardButton(
        text="◀️ Назад",
        callback_data="back"
    )])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)
