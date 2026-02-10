"""PromoCode service for v1.1 (safe no-op when disabled)."""

from typing import Optional, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.promo_code import PromoCode


class PromoCodeService:
    """Service for promo code operations (v1.1 feature)."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.enabled = settings.feature_promo_codes
    
    async def validate_and_apply(
        self,
        code: str,
        order_total: float
    ) -> Dict[str, Any]:
        """Validate and apply promo code. Returns safe no-op when disabled."""
        if not self.enabled:
            # Safe no-op behavior
            return {
                "applied": False,
                "discount": 0.0,
                "message": "Промокоды временно недоступны"
            }
        
        # Implementation would go here when enabled
        # For now, return safe no-op
        return {
            "applied": False,
            "discount": 0.0,
            "message": "Промокод не найден"
        }
    
    async def get_promo_code_by_code(self, code: str) -> Optional[PromoCode]:
        """Get promo code by code string."""
        if not self.enabled:
            return None
        
        # Implementation would go here
        return None
    
    async def increment_usage(self, promo_code_id: int) -> None:
        """Increment promo code usage counter."""
        if not self.enabled:
            return
        
        # Implementation would go here
        pass
    
    async def create_promo_code(self, **kwargs) -> Optional[PromoCode]:
        """Create a new promo code."""
        if not self.enabled:
            return None
        
        # Implementation would go here
        return None
    
    async def deactivate_promo_code(self, promo_code_id: int) -> bool:
        """Deactivate a promo code."""
        if not self.enabled:
            return False
        
        # Implementation would go here
        return False
