"""Throttling middleware to prevent spam."""

import time
from typing import Callable, Any, Awaitable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery

from app.utils.exceptions import ValidationException


class ThrottlingMiddleware(BaseMiddleware):
    """Middleware to throttle user requests."""
    
    def __init__(self, rate_limit: float = 0.5, max_cache_size: int = 10000):
        """
        Initialize throttling middleware.
        
        Args:
            rate_limit: Minimum seconds between requests from same user
            max_cache_size: Maximum number of entries to keep in memory
        """
        self.rate_limit = rate_limit
        self.max_cache_size = max_cache_size
        self.last_requests: Dict[int, float] = {}
    
    def _cleanup_old_entries(self, current_time: float) -> None:
        """Remove entries older than rate_limit to prevent memory leaks."""
        if len(self.last_requests) > self.max_cache_size:
            # Remove entries older than 5 minutes
            cutoff_time = current_time - 300
            self.last_requests = {
                k: v for k, v in self.last_requests.items() 
                if v > cutoff_time
            }
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any]
    ) -> Any:
        """Check rate limit."""
        user = data.get("user")
        
        if not user:
            return await handler(event, data)
        
        current_time = time.time()
        user_id = user.id
        
        # Cleanup old entries periodically
        if len(self.last_requests) % 100 == 0:
            self._cleanup_old_entries(current_time)
        
        # Check last request time
        if user_id in self.last_requests:
            time_passed = current_time - self.last_requests[user_id]
            if time_passed < self.rate_limit:
                # Rate limit hit
                if isinstance(event, Message):
                    await event.answer(
                        "⏱ Пожалуйста, не так быстро. Подождите немного."
                    )
                elif isinstance(event, CallbackQuery):
                    await event.answer(
                        "⏱ Слишком быстро!", show_alert=True
                    )
                return None
        
        # Update last request time
        self.last_requests[user_id] = current_time
        
        return await handler(event, data)
