"""Admin handlers for admin workflow."""

from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.category import Category

router = Router()


@router.callback_query(F.data.startswith("edit_category:"))
async def edit_category(callback: CallbackQuery, session: AsyncSession) -> None:
    """Handle editing a category selected from admin menu."""
    # Extract category id from callback data
    try:
        category_id = int(callback.data.split(":", 1)[1])
    except Exception:
        await callback.answer("Неверный идентификатор категории", show_alert=True)
        return

    # Fetch category from DB
    result = await session.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    if not category:
        await callback.answer("Категория не найдена", show_alert=True)
        return

    text = (
        f"Категория: {category.name}\n"
        f"Описание: {category.description or '-'}\n"
        f"Активна: {'Да' if category.is_active else 'Нет'}\n"
        f"ID: {category.id}"
    )

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="◀️ Назад", callback_data="admin:menu")
    ]])
    await callback.message.edit_text(text, reply_markup=kb)
