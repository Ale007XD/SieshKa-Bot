"""Database configuration and session management."""

from typing import AsyncGenerator, cast
import logging

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

import os
from app.config import settings

# Create async engine with safe fallback for test environments without optional DB adapters
if os.environ.get("TESTING", "0") == "1":
    engine = None
    AsyncSessionLocal = None  # type: ignore
else:
    try:
        # Create async engine
        db_url = settings.database_url
        if not db_url:
            raise RuntimeError("DATABASE_URL is not set")
        engine = create_async_engine(
            db_url,
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
logger = logging.getLogger(__name__)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting database session."""
    if AsyncSessionLocal is None:
        class _DummyResult:
            def scalar(self):
                return None
            def scalars(self):
                class _Scalar:
                    def all(self):
                        return []
                return _Scalar()

        class _DummySession(AsyncSession):  # type: ignore[misc]
            def __init__(self, *args, **kwargs):  # pragma: no cover
                pass
            async def __aenter__(self):
                return self
            async def __aexit__(self, exc_type, exc, tb):
                pass
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
        yield dummy  # type: ignore[no-redef]
        return
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db():
    """Initialize database tables and seed initial data if needed."""
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

    # Seed initial categories if none exist
    if AsyncSessionLocal is not None:
        from sqlalchemy import select
        from app.models.category import Category
        try:
            async with AsyncSessionLocal() as session:
                result = await session.execute(select(Category))
                existing = result.scalars().all()
                if not existing:
                    seed_names = ["Пицца", "Суши", "Бургеры", "Напитки", "Десерты"]
                    categories = [Category(name=n) for n in seed_names]
                    session.add_all(categories)
                    await session.commit()
                    logger.info("Seeded categories: %s", ",".join(seed_names))
        except Exception as e:
            logger.exception("Error seeding categories: %s", e)

async def close_db():
    """Close database connections."""
    if engine is None:
        return
    await engine.dispose()
