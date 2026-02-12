"""Database middleware for aiogram."""

from typing import Callable, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal


class DBSessionMiddleware(BaseMiddleware):
    """Middleware that provides database session to handlers."""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any]
    ) -> Any:
        """Create and provide database session."""
        async with AsyncSessionLocal() as session:
            data["session"] = session
            return await handler(event, data)
