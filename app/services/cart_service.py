"""Cart service for managing user shopping carts."""

import json
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, asdict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product
from app.models.modifier import ModifierOption
from app.services.menu_service import MenuService
from app.utils.exceptions import NotFoundException, ValidationException


@dataclass
class CartItem:
    """Cart item data class."""
    product_id: int
    product_name: str
    product_price: float
    quantity: int
    modifiers: List[Dict[str, Any]]
    modifiers_price: float
    item_total: float
    special_instructions: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> "CartItem":
        """Create from dictionary."""
        return cls(**data)


class CartService:
    """Service for shopping cart operations."""
    
    def __init__(self, session: AsyncSession, redis_client=None):
        self.session = session
        self.redis = redis_client
        self.menu_service = MenuService(session)
    
    def _get_cart_key(self, user_id: int) -> str:
        """Get Redis key for user cart."""
        return f"cart:{user_id}"
    
    def _get_lock_key(self, user_id: int) -> str:
        """Get Redis lock key for cart checkout."""
        return f"lock:cart:{user_id}"
    
    async def get_cart(self, user_id: int) -> List[CartItem]:
        """Get user's cart."""
        if self.redis:
            cart_key = self._get_cart_key(user_id)
            cart_data = await self.redis.get(cart_key)
            if cart_data:
                items = json.loads(cart_data)
                return [CartItem.from_dict(item) for item in items]
        return []
    
    async def save_cart(self, user_id: int, items: List[CartItem]) -> None:
        """Save user's cart."""
        if self.redis:
            cart_key = self._get_cart_key(user_id)
            cart_data = json.dumps([item.to_dict() for item in items])
            await self.redis.set(cart_key, cart_data, ex=86400)  # 24 hours
    
    async def clear_cart(self, user_id: int) -> None:
        """Clear user's cart."""
        if self.redis:
            cart_key = self._get_cart_key(user_id)
            await self.redis.delete(cart_key)
    
    async def add_item(
        self,
        user_id: int,
        product_id: int,
        quantity: int = 1,
        modifier_option_ids: Optional[List[int]] = None,
        special_instructions: Optional[str] = None
    ) -> CartItem:
        """Add item to cart."""
        # Get product
        product = await self.menu_service.get_product_by_id(product_id)
        
        if not product.is_available:
            raise ValidationException("Product is not available")
        
        # Calculate modifiers
        modifiers = []
        modifiers_price = 0.0
        
        if modifier_option_ids:
            for option_id in modifier_option_ids:
                option_result = await self.session.execute(
                    select(ModifierOption).where(ModifierOption.id == option_id)
                )
                option = option_result.scalar_one_or_none()
                if option:
                    modifiers.append({
                        "id": option.id,
                        "name": option.name,
                        "price_adjustment": float(option.price_adjustment)
                    })
                    modifiers_price += float(option.price_adjustment)
        
        # Calculate item total
        item_total = (float(product.price) + modifiers_price) * quantity
        
        # Create cart item
        cart_item = CartItem(
            product_id=product_id,
            product_name=product.name,
            product_price=float(product.price),
            quantity=quantity,
            modifiers=modifiers,
            modifiers_price=modifiers_price,
            item_total=item_total,
            special_instructions=special_instructions
        )
        
        # Add to cart
        cart = await self.get_cart(user_id)
        cart.append(cart_item)
        await self.save_cart(user_id, cart)
        
        return cart_item
    
    async def remove_item(self, user_id: int, item_index: int) -> None:
        """Remove item from cart by index."""
        cart = await self.get_cart(user_id)
        
        if item_index < 0 or item_index >= len(cart):
            raise ValidationException("Invalid item index")
        
        cart.pop(item_index)
        await self.save_cart(user_id, cart)
    
    async def update_quantity(
        self,
        user_id: int,
        item_index: int,
        quantity: int
    ) -> CartItem:
        """Update item quantity."""
        if quantity < 1:
            raise ValidationException("Quantity must be at least 1")
        
        cart = await self.get_cart(user_id)
        
        if item_index < 0 or item_index >= len(cart):
            raise ValidationException("Invalid item index")
        
        item = cart[item_index]
        item.quantity = quantity
        item.item_total = (item.product_price + item.modifiers_price) * quantity
        
        await self.save_cart(user_id, cart)
        return item
    
    async def get_cart_summary(self, user_id: int) -> dict:
        """Get cart summary."""
        cart = await self.get_cart(user_id)
        
        total_items = sum(item.quantity for item in cart)
        subtotal = sum(item.item_total for item in cart)
        
        return {
            "items": cart,
            "total_items": total_items,
            "subtotal": subtotal,
            "item_count": len(cart)
        }
    
    async def acquire_checkout_lock(self, user_id: int, ttl_seconds: int = 30) -> bool:
        """Acquire lock for cart checkout."""
        if not self.redis:
            return True
        
        lock_key = self._get_lock_key(user_id)
        # Use Redis SET NX EX for atomic lock acquisition
        acquired = await self.redis.set(lock_key, "1", nx=True, ex=ttl_seconds)
        return acquired
    
    async def release_checkout_lock(self, user_id: int) -> None:
        """Release cart checkout lock."""
        if self.redis:
            lock_key = self._get_lock_key(user_id)
            await self.redis.delete(lock_key)
