"""Health check endpoint."""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
import asyncio
from typing import Dict, Any
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db

router = APIRouter()


@router.get("")
async def health_check(db: AsyncSession = Depends(get_db)) -> Any:
    """Health check endpoint verifying database and service status."""
    health_status = {
        "status": "healthy",
        "version": "1.0.0",
        "services": {
            "api": "ok",
            "database": "unknown",
            "redis": "unknown"
        },
        # Collect non-blocking warnings to aid debugging without failing health checks
        "warnings": []
    }
    
    # Check database
    try:
        result = await db.execute(text("SELECT 1"))
        scalar = result.scalar()
        if asyncio.iscoroutine(scalar):
            scalar = await scalar
        if scalar == 1:
            health_status["services"]["database"] = "ok"
    except Exception as e:
        health_status["services"]["database"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"
        health_status["warnings"].append({
            "service": "database",
            "level": "warning",
            "message": str(e)
        })
    
    # Check Redis (optional)
    try:
        from app.config import settings
        try:
            import redis.asyncio as aioredis  # type: ignore
        except Exception:
            aioredis = None  # type: ignore

        if settings.redis_url and aioredis is not None:
            redis_client = await aioredis.from_url(settings.redis_url)
            await redis_client.ping()
            await redis_client.close()
            health_status["services"]["redis"] = "ok"
        else:
            health_status["services"]["redis"] = "not_configured"
    except ModuleNotFoundError:
        # Redis library not installed; treat as not configured
        health_status["services"]["redis"] = "not_configured"
        health_status["warnings"].append({
            "service": "redis",
            "level": "warning",
            "message": "Redis library not installed"
        })
    except Exception as e:
        health_status["services"]["redis"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"
        health_status["warnings"].append({
            "service": "redis",
            "level": "warning",
            "message": str(e)
        })
    
    if health_status["status"] == "unhealthy":
        # Return health payload with 503 status but as a normal JSON body
        return JSONResponse(status_code=503, content=health_status)
    
    return health_status
