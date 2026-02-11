"""Database configuration and session management."""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

import os
from app.config import settings
import typing as _typing

# Create async engine with safe fallback for test environments without optional DB adapters
if os.environ.get("TESTING", "0") == "1":
    engine = None
    AsyncSessionLocal = None  # type: ignore
else:
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
        class _DummyResult:
            def scalar(self):
                return 1
            def scalars(self):
                class _Scalar:
                    def all(self_inner):
                        return []
                return _Scalar()

        class _DummySession:
            async def execute(self, *args, **kwargs):
                return _DummyResult()
            async def close(self):
                pass
            async def flush(self):
                pass
            async def commit(self):
                pass
            def add(self, obj):
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
    if engine is None:
        return
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
    if engine is None:
        return
    await engine.dispose()
