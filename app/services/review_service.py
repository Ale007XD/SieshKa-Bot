"""Review service for v1.1 (safe no-op when disabled)."""

from typing import Optional, List, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.review import Review


class ReviewService:
    """Service for review operations (v1.1 feature)."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.enabled = settings.feature_reviews
    
    async def can_leave_review(
        self,
        user_id: int,
        order_id: int
    ) -> Dict[str, Any]:
        """Check if user can leave a review. Returns safe no-op when disabled."""
        if not self.enabled:
            # Safe no-op behavior
            return {
                "can_review": False,
                "message": "Отзывы временно недоступны"
            }
        
        # Implementation would go here when enabled
        return {
            "can_review": False,
            "message": "Отзывы временно недоступны"
        }
    
    async def create_review(
        self,
        user_id: int,
        order_id: int,
        **kwargs
    ) -> Optional[Review]:
        """Create a new review."""
        if not self.enabled:
            return None
        
        # Implementation would go here
        return None
    
    async def get_reviews(
        self,
        approved_only: bool = True,
        limit: int = 20
    ) -> List[Review]:
        """Get reviews."""
        if not self.enabled:
            return []
        
        # Implementation would go here
        return []
    
    async def approve_review(
        self,
        review_id: int,
        moderator_id: int
    ) -> bool:
        """Approve a review."""
        if not self.enabled:
            return False
        
        # Implementation would go here
        return False
    
    async def respond_to_review(
        self,
        review_id: int,
        response: str,
        responder_id: int
    ) -> bool:
        """Respond to a review."""
        if not self.enabled:
            return False
        
        # Implementation would go here
        return False
