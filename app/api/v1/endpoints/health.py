"""Health check endpoint."""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db

router = APIRouter()


@router.get("")
async def health_check(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """Health check endpoint verifying database and service status."""
    health_status = {
        "status": "healthy",
        "version": "1.0.0",
        "services": {
            "api": "ok",
            "database": "unknown",
            "redis": "unknown"
        }
    }
    
    # Check database
    try:
        result = await db.execute(text("SELECT 1"))
        if result.scalar() == 1:
            health_status["services"]["database"] = "ok"
    except Exception as e:
        health_status["services"]["database"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # Check Redis (optional)
    try:
        from app.config import settings
        import redis.asyncio as aioredis

        if settings.redis_url:
            redis_client = await aioredis.from_url(settings.redis_url)
            await redis_client.ping()
            await redis_client.close()
            health_status["services"]["redis"] = "ok"
        else:
            health_status["services"]["redis"] = "not_configured"
    except Exception as e:
        health_status["services"]["redis"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"
    
    if health_status["status"] == "unhealthy":
        raise HTTPException(status_code=503, detail=health_status)
    
    return health_status
