"""Common handlers for all users."""
from typing import Optional

from aiogram import Router, F
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext

from app.services.user_service import UserService
from app.utils.templates import Templates
from app.keyboards.common import get_main_menu_keyboard
from app.keyboards.client import get_client_menu_keyboard
from app.keyboards.admin import get_admin_menu_keyboard
from app.keyboards.staff import get_staff_menu_keyboard

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, session: AsyncSession, user: Optional[User] = None):
    """Handle /start command."""
    # If user is not injected by middleware, fetch or create from Telegram data
    if user is None:
        telegram_user = getattr(message, "from_user", None)
        if telegram_user:
            user_service = UserService(session)
            user = await user_service.get_or_create_user(
                telegram_id=telegram_user.id,
                username=telegram_user.username,
                first_name=telegram_user.first_name,
                last_name=telegram_user.last_name
            )
        else:
            class Guest:
                first_name = None
                def is_admin(self):
                    return False
                def is_staff(self):
                    return False
            user = Guest()
            user.first_name = None
    await message.answer(
        Templates.welcome_message(user.first_name or "Друг"),
        reply_markup=get_main_menu_keyboard(user)
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Handle /help command."""
    await message.answer(Templates.help_message())


@router.message(F.text == "◀️ Назад")
async def back_handler(message: Message, state: FSMContext, user: Optional[User] = None) -> None:
    """Handle back button."""
    await state.clear()
    
    if user is None:
        class Guest:
            def is_admin(self): return False
            def is_staff(self): return False
            role = None
        user = Guest()
    
    if user.is_admin():
        await message.answer(
            "👑 Панель администратора",
            reply_markup=get_admin_menu_keyboard()
        )
    elif user.is_staff():
        await message.answer(
            f"🔧 Панель {user.role}",
            reply_markup=get_staff_menu_keyboard(user.role)
        )
    else:
        await message.answer(
            "👋 Главное меню",
            reply_markup=get_client_menu_keyboard()
        )


@router.callback_query(F.data == "back")
async def back_callback(callback: CallbackQuery, state: FSMContext, user: Optional[User] = None) -> None:
    """Handle back callback."""
    await callback.answer()
    await state.clear()
    
    # If user is not injected by middleware, create a lightweight guest user
    if user is None:
        class Guest:
            def is_admin(self):
                return False
            def is_staff(self):
                return False
            role = None
        user = Guest()
    
    if user.is_admin():
        await callback.message.edit_text(
            "👑 Панель администратора",
            reply_markup=get_admin_menu_keyboard()
        )
    elif user.is_staff():
        await callback.message.edit_text(
            f"🔧 Панель {user.role}",
            reply_markup=get_staff_menu_keyboard(user.role)
        )
    else:
        await callback.message.edit_text(
            "👋 Главное меню",
            reply_markup=get_client_menu_keyboard()
        )


@router.message(Command("cancel"))
@router.message(F.text == "❌ Отмена")
async def cmd_cancel(message: Message, state: FSMContext):
    """Cancel current operation."""
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("Нет активных операций для отмены.")
        return
    
    await state.clear()
    await message.answer("✅ Операция отменена.")
