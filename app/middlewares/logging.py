"""Logging middleware."""

import logging
from typing import Callable, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseMiddleware):
    """Middleware for logging updates."""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any]
    ) -> Any:
        """Log the update."""
        user = data.get("user")
        user_info = f"User {user.id} ({user.full_name})" if user else "Unknown user"
        
        if isinstance(event, Message):
            logger.info(f"{user_info}: Message - {event.text or '[non-text]'}")
        elif isinstance(event, CallbackQuery):
            logger.info(f"{user_info}: Callback - {event.data}")
        
        try:
            result = await handler(event, data)
            return result
        except Exception as e:
            logger.error(f"Error handling update from {user_info}: {e}", exc_info=True)
            raise
