"""Settings API endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.schemas import SettingsResponse, SettingsUpdate
from app.api.v1.dependencies import get_db_session, get_current_admin
from app.services.settings_service import SettingsService

router = APIRouter()


@router.get("", response_model=SettingsResponse)
async def get_settings(
    session: AsyncSession = Depends(get_db_session)
):
    """Get application settings."""
    settings_service = SettingsService(session)
    settings = await settings_service.get_settings()
    return settings


@router.patch("", response_model=SettingsResponse)
async def update_settings(
    settings_update: SettingsUpdate,
    session: AsyncSession = Depends(get_db_session),
    current_user: dict = Depends(get_current_admin)
):
    """Update application settings (admin only)."""
    settings_service = SettingsService(session)
    
    try:
        updated_settings = await settings_service.update_settings(
            company_name=settings_update.company_name,
            company_phone=settings_update.company_phone,
            company_address=settings_update.company_address,
            delivery_fee=settings_update.delivery_fee,
            min_order_amount=settings_update.min_order_amount
        )
        return updated_settings
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/payment-methods")
async def get_payment_methods(
    session: AsyncSession = Depends(get_db_session)
):
    """Get available payment methods."""
    settings_service = SettingsService(session)
    methods = await settings_service.get_available_payment_methods()
    
    return {
        "methods": [
            {"code": code, "name": name}
            for code, name in methods
        ]
    }
