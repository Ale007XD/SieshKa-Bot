"""Telegram Bot entry point."""

import asyncio
import logging
import signal
import sys

from aiogram import Bot, Dispatcher

from app.config import settings
from app.database import close_db, init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global flag for graceful shutdown
shutdown_event = asyncio.Event()


def signal_handler(sig, frame):
    """Handle shutdown signals gracefully."""
    logger.info(f"Received signal {sig}, initiating graceful shutdown...")
    shutdown_event.set()


async def main():
    """Main bot entry point."""
    # Initialize database
    await init_db()
    logger.info("Database initialized")
    
    # Register signal handlers using asyncio (cross-platform)
    loop = asyncio.get_event_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        try:
            loop.add_signal_handler(sig, shutdown_event.set)
        except NotImplementedError:
            # Windows doesn't support add_signal_handler, use signal.signal in main thread
            pass
    
    # Initialize bot and dispatcher
    if not settings.bot_token:
        raise RuntimeError("BOT_TOKEN is not set in environment")
    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()
    
    # Register all handlers
    from app.handlers import get_all_routers
    from app.middlewares.db import DBSessionMiddleware
    from app.middlewares.auth import AuthMiddleware
    
    # Register middlewares
    dp.update.middleware(DBSessionMiddleware())
    dp.update.middleware(AuthMiddleware())
    
    # Register all routers
    for router in get_all_routers():
        dp.include_router(router)
    
    logger.info("Registered %d routers", len(get_all_routers()))
    
    logger.info("Bot starting polling...")
    
    try:
        # Start polling
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Bot error: {e}")
    finally:
        # Cleanup
        await bot.session.close()
        await close_db()
        logger.info("Bot shutdown complete")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
        sys.exit(0)
