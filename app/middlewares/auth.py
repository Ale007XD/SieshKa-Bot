"""Authentication and authorization middleware."""

from typing import Callable, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery

from app.services.user_service import UserService
from app.models.user import User


class AuthMiddleware(BaseMiddleware):
    """Middleware for user authentication."""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any]
    ) -> Any:
        """Authenticate user from Telegram data."""
        session = data.get("session")
        
        if not session:
            return await handler(event, data)
        
        # Get Telegram user info
        telegram_user = None
        if isinstance(event, Message):
            telegram_user = event.from_user
        elif isinstance(event, CallbackQuery):
            telegram_user = event.from_user
        
        if telegram_user:
            user_service = UserService(session)
            user = await user_service.get_or_create_user(
                telegram_id=telegram_user.id,
                username=telegram_user.username,
                first_name=telegram_user.first_name,
                last_name=telegram_user.last_name
            )
            data["user"] = user
            data["is_admin"] = user.is_admin()
            data["is_staff"] = user.is_staff()
        
        return await handler(event, data)


class AdminMiddleware(BaseMiddleware):
    """Middleware to restrict access to admins only."""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any]
    ) -> Any:
        """Check if user is admin."""
        user = data.get("user")
        
        if not user or not user.is_admin():
            if isinstance(event, Message):
                await event.answer("⛔ У вас нет доступа к этой функции.")
            elif isinstance(event, CallbackQuery):
                await event.answer("⛔ Нет доступа", show_alert=True)
            return None
        
        return await handler(event, data)


class StaffMiddleware(BaseMiddleware):
    """Middleware to restrict access to staff only."""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any]
    ) -> Any:
        """Check if user is staff."""
        user = data.get("user")
        
        if not user or not user.is_staff():
            if isinstance(event, Message):
                await event.answer("⛔ У вас нет доступа к этой функции.")
            elif isinstance(event, CallbackQuery):
                await event.answer("⛔ Нет доступа", show_alert=True)
            return None
        
        return await handler(event, data)
