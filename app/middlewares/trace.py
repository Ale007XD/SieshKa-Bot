"""Trace middleware for request tracing."""

import uuid
import logging
from typing import Callable, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

logger = logging.getLogger(__name__)


class TraceMiddleware(BaseMiddleware):
    """Middleware for request tracing with unique IDs."""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any]
    ) -> Any:
        """Add trace ID to context."""
        trace_id = str(uuid.uuid4())[:8]
        data["trace_id"] = trace_id
        
        # Log with trace ID
        logger.debug(f"[{trace_id}] Processing update")
        
        try:
            result = await handler(event, data)
            logger.debug(f"[{trace_id}] Update processed successfully")
            return result
        except Exception as e:
            logger.error(f"[{trace_id}] Error processing update: {e}")
            raise
