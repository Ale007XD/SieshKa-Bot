"""DeliveryZone service for v1.1 (safe no-op when disabled)."""

from typing import Optional, List, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.delivery_zone import DeliveryZone


class DeliveryZoneService:
    """Service for delivery zone operations (v1.1 feature)."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.enabled = settings.feature_delivery_zones
    
    async def check_address_in_zone(
        self,
        address: str
    ) -> Dict[str, Any]:
        """Check if address is in a delivery zone. Returns safe no-op when disabled."""
        if not self.enabled:
            # Safe no-op behavior - allow all addresses
            return {
                "in_zone": True,
                "zone_id": None,
                "zone_name": None,
                "delivery_fee": 0.0
            }
        
        # Implementation would go here when enabled
        return {
            "in_zone": True,
            "zone_id": None,
            "zone_name": None,
            "delivery_fee": 0.0
        }
    
    async def get_zones(self) -> List[DeliveryZone]:
        """Get all delivery zones."""
        if not self.enabled:
            return []
        
        # Implementation would go here
        return []
    
    async def get_zone_by_id(self, zone_id: int) -> Optional[DeliveryZone]:
        """Get zone by ID."""
        if not self.enabled:
            return None
        
        # Implementation would go here
        return None
    
    async def create_zone(self, **kwargs) -> Optional[DeliveryZone]:
        """Create a new delivery zone."""
        if not self.enabled:
            return None
        
        # Implementation would go here
        return None
    
    async def update_zone(self, zone_id: int, **kwargs) -> bool:
        """Update a delivery zone."""
        if not self.enabled:
            return False
        
        # Implementation would go here
        return False
