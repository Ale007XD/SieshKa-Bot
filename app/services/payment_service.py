"""Payment service for v1.1 (safe no-op when disabled)."""

from typing import Optional, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings


class PaymentService:
    """Service for online payment operations (v1.1 feature)."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.enabled = settings.feature_online_payments
    
    async def create_payment(
        self,
        order_id: int,
        amount: float,
        payment_method: str
    ) -> Dict[str, Any]:
        """Create online payment. Returns safe no-op when disabled."""
        if not self.enabled:
            # Safe no-op behavior
            return {
                "success": False,
                "payment_url": None,
                "payment_id": None,
                "message": "Онлайн-оплата временно недоступна"
            }
        
        # Implementation would go here when enabled
        return {
            "success": False,
            "payment_url": None,
            "payment_id": None,
            "message": "Онлайн-оплата временно недоступна"
        }
    
    async def verify_payment(self, payment_id: str) -> Dict[str, Any]:
        """Verify payment status."""
        if not self.enabled:
            return {
                "verified": False,
                "status": "unknown",
                "message": "Онлайн-оплата временно недоступна"
            }
        
        # Implementation would go here
        return {
            "verified": False,
            "status": "unknown",
            "message": "Онлайн-оплата временно недоступна"
        }
    
    async def process_callback(self, callback_data: Dict[str, Any]) -> bool:
        """Process payment provider callback."""
        if not self.enabled:
            return False
        
        # Implementation would go here
        return False
    
    async def refund_payment(
        self,
        payment_id: str,
        amount: Optional[float] = None
    ) -> Dict[str, Any]:
        """Refund a payment."""
        if not self.enabled:
            return {
                "success": False,
                "message": "Онлайн-оплата временно недоступна"
            }
        
        # Implementation would go here
        return {
            "success": False,
            "message": "Онлайн-оплата временно недоступна"
        }
