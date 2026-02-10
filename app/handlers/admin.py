"""Admin handlers for admin workflow."""

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.utils.admin_guard import is_admin_callback, is_admin_message
from app.config import settings
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
from app.utils.templates import Templates
from app.states.admin import AdminStates

router = Router()

def _require_admin_callback(callback: CallbackQuery) -> bool:
    return is_admin_callback(callback)

def _require_admin_message(message: Message) -> bool:
    return is_admin_message(message)

def _admin_guard(callback_or_message) -> bool:
    if isinstance(callback_or_message, CallbackQuery):
        return _require_admin_callback(callback_or_message)
    if isinstance(callback_or_message, Message):
        return _require_admin_message(callback_or_message)
    return False

# Main admin menu
@router.message(F.text == "👑 Админ-панель")
async def admin_panel(message: Message):
    """Show admin panel."""
    if not _admin_guard(message):
        await message.answer("❌ Access denied (admin only)")
        return
    await message.answer(
        Templates.admin_panel(),
        reply_markup=get_admin_menu_keyboard()
    )

@router.callback_query(F.data == "admin:menu")
async def menu_management(callback: CallbackQuery, session: AsyncSession) -> None:
    if not _admin_guard(callback):
        await callback.answer("❌ Access denied", show_alert=True)
        return
    await callback.answer()
    await callback.message.edit_text(
        "📋 Управление меню",
        reply_markup=get_menu_management_keyboard()
    )

@router.callback_query(F.data == "admin:categories")
async def category_management(callback: CallbackQuery, session: AsyncSession) -> None:
    if not _admin_guard(callback):
        await callback.answer("❌ Access denied", show_alert=True)
        return
    await callback.answer()
    menu_service = MenuService(session)
    categories = await menu_service.get_all_categories(
        include_inactive=True,
        include_archived=False
    )
    await callback.message.edit_text(
        f"📁 Категории ({len(categories)})",
        reply_markup=get_category_management_keyboard(categories)
    )

@router.callback_query(F.data == "admin:products")
async def product_management(callback: CallbackQuery, session: AsyncSession) -> None:
    if not _admin_guard(callback):
        await callback.answer("❌ Access denied", show_alert=True)
        return
    await callback.answer()
    menu_service = MenuService(session)
    categories = await menu_service.get_all_categories()
    await callback.message.edit_text(
        "🍽 Управление товарами",
        reply_markup=get_product_management_keyboard(categories)
    )

@router.callback_query(F.data == "admin:archive")
async def archive_management(callback: CallbackQuery, session: AsyncSession) -> None:
    if not _admin_guard(callback):
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
async def unarchive_category(callback: CallbackQuery, session: AsyncSession, user: User) -> None:
    if not _admin_guard(callback):
        await callback.answer("❌ Access denied", show_alert=True)
        return
    category_id = int(callback.data.split(":")[2])
    archive_service = ArchiveService(session)
    try:
        await archive_service.unarchive_category(category_id=category_id, actor_user_id=user.id, cascade_option="with_descendants")
        await callback.answer("✅ Категория разархивирована")
        await archive_management(callback, session)
    except Exception as e:
        await callback.answer(f"❌ Ошибка: {str(e)}", show_alert=True)

@router.callback_query(F.data.startswith("archive:product:"))
async def unarchive_product(callback: CallbackQuery, session: AsyncSession, user: User) -> None:
    if not _admin_guard(callback):
        await callback.answer("❌ Access denied", show_alert=True)
        return
    product_id = int(callback.data.split(":")[2])
    archive_service = ArchiveService(session)
    try:
        await archive_service.unarchive_product(product_id=product_id, actor_user_id=user.id)
        await callback.answer("✅ Товар разархивирован")
        await archive_management(callback, session)
    except Exception as e:
        await callback.answer(f"❌ Ошибка: {str(e)}", show_alert=True)

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
    if not _admin_guard(callback):
        await callback.answer("❌ Access denied", show_alert=True)
        return
    await callback.answer()
    user_service = UserService(session)
    staff = await user_service.get_staff_users()
    await callback.message.edit_text(
        f"👥 Персонал ({len(staff)})",
        reply_markup=get_staff_management_keyboard(staff)
    )

@router.callback_query(F.data == "staff:add")
async def add_staff_start(callback: CallbackQuery, state) -> None:
    if not _admin_guard(callback):
        await callback.answer("❌ Access denied", show_alert=True)
        return
    await callback.answer()
    await state.set_state(AdminStates.staff_add_user_id)
    await callback.message.edit_text("Введите Telegram ID пользователя:")
