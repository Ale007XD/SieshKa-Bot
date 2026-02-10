"""Keyboards package."""

from app.keyboards.common import get_main_menu_keyboard, confirm_keyboard, back_keyboard
from app.keyboards.client import (
    get_client_menu_keyboard,
    get_categories_keyboard,
    get_products_keyboard,
    get_product_detail_keyboard,
    get_cart_keyboard,
    get_payment_methods_keyboard,
    get_orders_keyboard
)
from app.keyboards.admin import (
    get_admin_menu_keyboard,
    get_menu_management_keyboard,
    get_category_management_keyboard,
    get_product_management_keyboard,
    get_archive_management_keyboard,
    get_staff_management_keyboard,
    get_order_management_keyboard,
    get_statistics_keyboard
)
from app.keyboards.staff import get_staff_menu_keyboard

__all__ = [
    "get_main_menu_keyboard",
    "confirm_keyboard",
    "back_keyboard",
    "get_client_menu_keyboard",
    "get_categories_keyboard",
    "get_products_keyboard",
    "get_product_detail_keyboard",
    "get_cart_keyboard",
    "get_payment_methods_keyboard",
    "get_orders_keyboard",
    "get_admin_menu_keyboard",
    "get_menu_management_keyboard",
    "get_category_management_keyboard",
    "get_product_management_keyboard",
    "get_archive_management_keyboard",
    "get_staff_management_keyboard",
    "get_order_management_keyboard",
    "get_statistics_keyboard",
    "get_staff_menu_keyboard",
]
