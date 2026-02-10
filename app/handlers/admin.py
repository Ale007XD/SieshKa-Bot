"""Admin handlers for admin workflow."""

from aiogram import Router, F
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types import Message, CallbackQuery
# Removed unused imports: Command, FSMContext
from app.models.user import User

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


# Main admin menu
@router.message(F.text == "👑 Админ-панель")
async def admin_panel(message: Message):
    """Show admin panel."""
    await message.answer(
        Templates.admin_panel(),
        reply_markup=get_admin_menu_keyboard()
    )


# Menu management
@router.callback_query(F.data == "admin:menu")
async def menu_management(callback: CallbackQuery, session: AsyncSession):
    """Show menu management."""
    await callback.answer()
    await callback.message.edit_text(
        "📋 Управление меню",
        reply_markup=get_menu_management_keyboard()
    )


@router.callback_query(F.data == "admin:categories")
async def category_management(callback: CallbackQuery, session: AsyncSession):
    """Show category management."""
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
async def product_management(callback: CallbackQuery, session: AsyncSession):
    """Show product management."""
    await callback.answer()
    menu_service = MenuService(session)
    categories = await menu_service.get_all_categories()
    
    await callback.message.edit_text(
        "🍽 Управление товарами",
        reply_markup=get_product_management_keyboard(categories)
    )


# Archive management
@router.callback_query(F.data == "admin:archive")
async def archive_management(callback: CallbackQuery, session: AsyncSession):
    """Show archive management."""
    await callback.answer()
    archive_service = ArchiveService(session)
    
    archived_categories = await archive_service.get_archived_categories()
    archived_products = await archive_service.get_archived_products()
    
    text = (
        "📦 Управление архивом\n\n"
        f"Архивировано категорий: {len(archived_categories)}\n"
        f"Архивировано товаров: {len(archived_products)}"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=get_archive_management_keyboard(
            archived_categories,
            archived_products
        )
    )


@router.callback_query(F.data.startswith("archive:category:"))
async def unarchive_category(callback: CallbackQuery, session: AsyncSession, user: User):
    """Unarchive category."""
    category_id = int(callback.data.split(":")[2])
    archive_service = ArchiveService(session)
    
    try:
        await archive_service.unarchive_category(
            category_id=category_id,
            actor_user_id=user.id,
            cascade_option="with_descendants"
        )
        await callback.answer("✅ Категория разархивирована")
        
        # Refresh view
        await archive_management(callback, session)
    except Exception as e:
        await callback.answer(f"❌ Ошибка: {str(e)}", show_alert=True)


@router.callback_query(F.data.startswith("archive:product:"))
async def unarchive_product(callback: CallbackQuery, session: AsyncSession, user: User):
    """Unarchive product."""
    product_id = int(callback.data.split(":")[2])
    archive_service = ArchiveService(session)
    
    try:
        await archive_service.unarchive_product(
            product_id=product_id,
            actor_user_id=user.id
        )
        await callback.answer("✅ Товар разархивирован")
        
        # Refresh view
        await archive_management(callback, session)
    except Exception as e:
        await callback.answer(f"❌ Ошибка: {str(e)}", show_alert=True)


@router.callback_query(F.data.startswith("unarchive_cat:"))
async def confirm_unarchive_category(callback: CallbackQuery):
    """Confirm unarchive category."""
    category_id = int(callback.data.split(":")[1])
    await callback.answer()
    await callback.message.edit_text(
        "Разархивировать с подкатегориями и товарами?",
        reply_markup=confirm_keyboard(f"confirm_unarchive_cat:{category_id}")
    )


# Staff management
@router.callback_query(F.data == "admin:staff")
async def staff_management(callback: CallbackQuery, session: AsyncSession):
    """Show staff management."""
    await callback.answer()
    user_service = UserService(session)
    staff = await user_service.get_staff_users()
    
    await callback.message.edit_text(
        f"👥 Персонал ({len(staff)})",
        reply_markup=get_staff_management_keyboard(staff)
    )


@router.callback_query(F.data == "staff:add")
async def add_staff_start(callback: CallbackQuery, state: FSMContext):
    """Start adding staff."""
    await callback.answer()
    await state.set_state(AdminStates.staff_add_user_id)
    await callback.message.edit_text(
        "Введите Telegram ID пользователя:"
    )


@router.message(AdminStates.staff_add_user_id)
async def process_staff_id(message: Message, state: FSMContext):
    """Process staff Telegram ID."""
    try:
        telegram_id = int(message.text.strip())
        await state.update_data(telegram_id=telegram_id)
        await state.set_state(AdminStates.staff_select_role)
        
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📋 Менеджер", callback_data="role:manager")],
            [InlineKeyboardButton(text="👨‍🍳 Кухня", callback_data="role:kitchen")],
            [InlineKeyboardButton(text="📦 Упаковщик", callback_data="role:packer")],
            [InlineKeyboardButton(text="🚚 Курьер", callback_data="role:courier")],
            [InlineKeyboardButton(text="◀️ Отмена", callback_data="cancel")]
        ])
        
        await message.answer("Выберите роль:", reply_markup=keyboard)
    except ValueError:
        await message.answer("❌ Неверный ID. Введите число:")


# Order management
@router.callback_query(F.data == "admin:orders")
async def order_management(callback: CallbackQuery, session: AsyncSession):
    """Show order management."""
    await callback.answer()
    order_service = OrderService(session)
    
    # Get counts by status (single query)
    status_counts = await order_service.get_order_counts_by_status([
        OrderStatus.NEW, OrderStatus.CONFIRMED, OrderStatus.IN_PROGRESS
    ])
    
    text = (
        "📦 Управление заказами\n\n"
        f"🆕 Новые: {status_counts.get(OrderStatus.NEW.value, 0)}\n"
        f"✅ Подтверждены: {status_counts.get(OrderStatus.CONFIRMED.value, 0)}\n"
        f"👨‍🍳 Готовятся: {status_counts.get(OrderStatus.IN_PROGRESS.value, 0)}"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=get_order_management_keyboard()
    )


# Statistics
@router.callback_query(F.data == "admin:stats")
async def statistics(callback: CallbackQuery, session: AsyncSession):
    """Show statistics menu."""
    await callback.answer()
    stats_service = StatsService(session)
    daily = await stats_service.get_daily_stats()
    
    text = (
        f"📊 Статистика на {daily['date']}\n\n"
        f"📦 Заказов: {daily['total_orders']}\n"
        f"💰 Выручка: {daily['total_revenue']:.2f} ₽\n"
        f"💵 Средний чек: {daily['average_order_value']:.2f} ₽"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=get_statistics_keyboard()
    )
