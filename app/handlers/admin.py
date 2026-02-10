"""Admin handlers for admin workflow (clean, unified guard)."""

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession
import typing as _t

from app.config import settings
from app.models.user import User
from app.utils.admin_guard import is_admin_callback, is_admin_message
from app.utils.permissions import ensure_admin

from app.services.menu_service import MenuService
from app.services.archive_service import ArchiveService
from app.services.order_service import OrderService
from app.services.stats_service import StatsService
from app.services.user_service import UserService
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
from app.keyboards.common import confirm_keyboard
from app.utils.enums import UserRole, OrderStatus
from app.states.admin import AdminStates
from app.templates import Templates

router = Router()

def _guard_admin(callback_or_message: object) -> bool:
    if isinstance(callback_or_message, CallbackQuery):
        return is_admin_callback(callback_or_message)
    if isinstance(callback_or_message, Message):
        return is_admin_message(callback_or_message)
    return False

@router.message(F.text == "👑 Админ-панель")
async def admin_panel(message: Message):
    if not _guard_admin(message):
        await message.answer("❌ Access denied (admin only)")
        return
    await message.answer(Templates.admin_panel(), reply_markup=get_admin_menu_keyboard())

@router.callback_query(F.data == "admin:menu")
async def menu_management(callback: CallbackQuery, session: AsyncSession):
    if not _guard_admin(callback):
        await callback.answer("❌ Access denied", show_alert=True)
        return
    await callback.answer()
    await callback.message.edit_text("📋 Управление меню", reply_markup=get_menu_management_keyboard())

@router.callback_query(F.data == "admin:categories")
async def category_management(callback: CallbackQuery, session: AsyncSession):
    if not _guard_admin(callback):
        await callback.answer("❌ Access denied", show_alert=True)
        return
    await callback.answer()
    menu_service = MenuService(session)
    categories = await menu_service.get_all_categories(include_inactive=True, include_archived=False)
    await callback.message.edit_text(f"📁 Категории ({len(categories)})", reply_markup=get_category_management_keyboard(categories))

@router.callback_query(F.data == "admin:products")
async def product_management(callback: CallbackQuery, session: AsyncSession):
    if not _guard_admin(callback):
        await callback.answer("❌ Access denied", show_alert=True)
        return
    await callback.answer()
    menu_service = MenuService(session)
    categories = await menu_service.get_all_categories()
    await callback.message.edit_text("🍽 Управление товарами", reply_markup=get_product_management_keyboard(categories))

@router.callback_query(F.data == "admin:archive")
async def archive_management(callback: CallbackQuery, session: AsyncSession):
    if not _guard_admin(callback):
        await callback.answer("❌ Access denied", show_alert=True)
        return
    await callback.answer()
    archive_service = ArchiveService(session)
    archived_categories = await archive_service.get_archived_categories()
    archived_products = await archive_service.get_archived_products()
    text = (
        "📦 Управление архивом\n\n"
        f"Архивировано категорий: {len(archived_categories)}\n"
        f"Архивировано товаров: {len(archived_products)}"
    )
    await callback.message.edit_text(text, reply_markup=get_archive_management_keyboard(archived_categories, archived_products))

@router.callback_query(F.data.startswith("archive:category:"))
async def unarchive_category(callback: CallbackQuery, session: AsyncSession, user: User):
    if not _guard_admin(callback):
        await callback.answer("❌ Access denied", show_alert=True)
        return
    category_id = int(callback.data.split(":")[2])
    archive_service = ArchiveService(session)
    await archive_service.unarchive_category(category_id=category_id, actor_user_id=user.id, cascade_option="with_descendants")
    await callback.answer("✅ Категория разархивирована")
    await archive_management(callback, session)

@router.callback_query(F.data.startswith("archive:product:"))
async def unarchive_product(callback: CallbackQuery, session: AsyncSession, user: User):
    if not _guard_admin(callback):
        await callback.answer("❌ Access denied", show_alert=True)
        return
    product_id = int(callback.data.split(":")[2])
    archive_service = ArchiveService(session)
    await archive_service.unarchive_product(product_id=product_id, actor_user_id=user.id)
    await callback.answer("✅ Товар разархивирован")
    await archive_management(callback, session)

@router.callback_query(F.data.startswith("unarchive_cat:"))
async def confirm_unarchive_category(callback: CallbackQuery) -> None:
    category_id = int(callback.data.split(":")[1])
    await callback.answer()
    await callback.message.edit_text(
        "Разархивировать с подкатегориями и товарами?",
        reply_markup=confirm_keyboard(f"confirm_unarchive_cat:{category_id}")
    )

@router.callback_query(F.data == "admin:staff")
async def staff_management(callback: CallbackQuery, session: AsyncSession) -> None:
    if not _guard_admin(callback):
        await callback.answer("❌ Access denied", show_alert=True)
        return
    await callback.answer()
    staff = await UserService(session).get_staff_users()
    await callback.message.edit_text(f"👥 Персонал ({len(staff)})", reply_markup=get_staff_management_keyboard(staff))

@router.callback_query(F.data == "staff:add")
async def add_staff_start(callback: CallbackQuery, state) -> None:
    if not _guard_admin(callback):
        await callback.answer("❌ Access denied", show_alert=True)
        return
    await callback.answer()
    await state.set_state(AdminStates.staff_add_user_id)
    await callback.message.edit_text("Введите Telegram ID пользователя:")

@router.callback_query(F.data == "admin:orders")
async def order_management(callback: CallbackQuery, session: AsyncSession) -> None:
    if not _guard_admin(callback):
        await callback.answer("❌ Access denied", show_alert=True)
        return
    await callback.answer()
    status_counts = await OrderService(session).get_order_counts_by_status([
        OrderStatus.NEW, OrderStatus.CONFIRMED, OrderStatus.IN_PROGRESS
    ])
    text = (
        "📦 Управление заказами\n\n"
        f"🆕 Новые: {status_counts.get(OrderStatus.NEW.value, 0)}\n"
        f"✅ Подтверждены: {status_counts.get(OrderStatus.CONFIRMED.value, 0)}\n"
        f"👨‍🍳 Готовятся: {status_counts.get(OrderStatus.IN_PROGRESS.value, 0)}"
    )
    await callback.message.edit_text(text, reply_markup=get_order_management_keyboard())

@router.callback_query(F.data == "admin:stats")
async def statistics(callback: CallbackQuery, session: AsyncSession) -> None:
    if not _guard_admin(callback):
        await callback.answer("❌ Access denied", show_alert=True)
        return
    await callback.answer()
    daily = await StatsService(session).get_daily_stats()
    text = (
        f"📊 Статистика на {daily['date']}\n\n"
        f"📦 Заказов: {daily['total_orders']}\n"
        f"💰 Выручка: {daily['total_revenue']:.2f} ₽\n"
        f"💵 Средний чек: {daily['average_order_value']:.2f} ₽"
    )
    await callback.message.edit_text(text, reply_markup=get_statistics_keyboard())
