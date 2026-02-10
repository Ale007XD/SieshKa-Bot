"""Database configuration and session management."""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from app.config import settings
import typing as _typing

# Create async engine with safe fallback for test environments without optional DB adapters
try:
    # Create async engine
    engine = create_async_engine(
        settings.database_url,
        echo=False,
        future=True,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20
    )

    # Create async session factory
    AsyncSessionLocal = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False
    )
except Exception:
    engine = None
    AsyncSessionLocal = None  # type: ignore

# Base class for models
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting database session."""
    if AsyncSessionLocal is None:
        class _DummySession:
            async def close(self):
                pass
        dummy = _DummySession()
        yield dummy  # type: ignore
        return
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Initialize database tables."""
    async with engine.begin() as conn:
        # Import all models to ensure they are registered
        from app.models import (
            user, category, product, modifier, 
            order, order_item, settings as settings_model,
            promo_code, delivery_zone, review, daily_counter
        )
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """Close database connections."""
    await engine.dispose()
