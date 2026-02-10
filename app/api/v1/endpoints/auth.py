"""Auth API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.schemas import Token, UserLogin
from app.api.v1.dependencies import get_db_session, get_current_user
from app.services.user_service import UserService
from app.utils.security import create_jwt_token, verify_password

router = APIRouter()


@router.post("/login", response_model=Token)
async def login(
    credentials: UserLogin,
    session: AsyncSession = Depends(get_db_session)
):
    """Login and get access token."""
    # Note: This is a simplified auth. In production, use proper password hashing
    user_service = UserService(session)
    
    # For API access, we would typically check username/password
    # For now, we'll return a dummy implementation
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="API authentication not yet implemented"
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    current_user: dict = Depends(get_current_user)
):
    """Refresh access token."""
    # Implementation would go here
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Token refresh not yet implemented"
    )
