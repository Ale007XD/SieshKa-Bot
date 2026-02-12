"""Order service for order lifecycle management."""

from typing import List, Optional
from datetime import datetime, date

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict
from sqlalchemy.orm import selectinload

from app.models.order import Order, OrderStatusLog
from app.models.order_item import OrderItem
from app.models.product import Product
from app.models.daily_counter import DailyCounter
from app.models.user import User
from app.utils.enums import OrderStatus, PaymentStatus, UserRole
from app.utils.exceptions import (
    NotFoundException,
    ValidationException,
    InvalidStateTransitionException
)
from app.utils.state_machine import OrderStateMachine


class OrderService:
    """Service for order operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.state_machine = OrderStateMachine()
    
    async def get_order_by_id(self, order_id: int) -> Order:
        """Get order by ID with related data."""
        result = await self.session.execute(
            select(Order)
            .options(
                selectinload(Order.items),
                selectinload(Order.user),
                selectinload(Order.courier)
            )
            .where(Order.id == order_id)
        )
        order = result.scalar_one_or_none()
        if not order:
            raise NotFoundException("Order", str(order_id))
        return order
    
    async def get_order_by_number(self, order_number: str) -> Order:
        """Get order by order number."""
        result = await self.session.execute(
            select(Order)
            .options(
                selectinload(Order.items),
                selectinload(Order.user),
                selectinload(Order.courier)
            )
            .where(Order.order_number == order_number)
        )
        order = result.scalar_one_or_none()
        if not order:
            raise NotFoundException("Order", order_number)
        return order
    
    async def get_user_orders(
        self,
        user_id: int,
        limit: int = 20,
        offset: int = 0
    ) -> List[Order]:
        """Get orders for a user."""
        result = await self.session.execute(
            select(Order)
            .where(Order.user_id == user_id)
            .order_by(Order.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all()
    
    async def get_orders_by_status(
        self,
        status: OrderStatus,
        limit: int = 50
    ) -> List[Order]:
        """Get orders by status."""
        result = await self.session.execute(
            select(Order)
            .options(selectinload(Order.user))
            .where(Order.status == status.value)
            .order_by(Order.created_at.asc())
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_orders(
        self,
        skip: int = 0,
        limit: int = 20
    ) -> List[Order]:
        """Get orders with pagination."""
        result = await self.session.execute(
            select(Order)
            .options(selectinload(Order.user))
            .order_by(Order.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def create_order(
        self,
        user_id: int,
        items: List[dict],
        delivery_address: str,
        delivery_phone: str,
        payment_method: str,
        delivery_comment: Optional[str] = None,
        promo_code_id: Optional[int] = None
    ) -> Order:
        """Create a new order."""
        # Generate order number
        order_number = await self._generate_order_number()
        
        # Calculate totals
        subtotal = 0.0
        order_items = []
        
        for item_data in items:
            product_id = item_data["product_id"]
            quantity = item_data.get("quantity", 1)
            modifiers = item_data.get("modifiers", [])
            special_instructions = item_data.get("special_instructions")
            
            # Get product
            product_result = await self.session.execute(
                select(Product).where(Product.id == product_id)
            )
            product = product_result.scalar_one_or_none()
            
            if not product:
                raise NotFoundException("Product", str(product_id))
            
            if not product.is_available:
                raise ValidationException(f"Product '{product.name}' is not available")
            
            # Calculate price with modifiers
            product_price = float(product.price)
            modifiers_price = sum(m.get("price_adjustment", 0) for m in modifiers)
            item_total = (product_price + modifiers_price) * quantity
            
            subtotal += item_total
            
            # Create order item
            order_item = OrderItem(
                product_id=product_id,
                product_name=product.name,
                product_price=product_price,
                quantity=quantity,
                modifiers=modifiers if modifiers else None,
                modifiers_price=modifiers_price,
                item_total=item_total,
                special_instructions=special_instructions
            )
            order_items.append(order_item)
        
        # Calculate total (delivery fee and discount logic would go here)
        delivery_fee = 0.0
        discount_amount = 0.0
        total = subtotal + delivery_fee - discount_amount
        
        # Create order
        order = Order(
            order_number=order_number,
            user_id=user_id,
            status=OrderStatus.NEW.value,
            payment_method=payment_method,
            payment_status=PaymentStatus.PENDING.value,
            subtotal=subtotal,
            delivery_fee=delivery_fee,
            discount_amount=discount_amount,
            total=total,
            delivery_address=delivery_address,
            delivery_phone=delivery_phone,
            delivery_comment=delivery_comment,
            promo_code_id=promo_code_id,
            items=order_items
        )
        
        self.session.add(order)
        await self.session.flush()
        await self.session.commit()
        
        # Log initial status
        await self._log_status_change(order.id, None, OrderStatus.NEW.value, user_id)
        
        return order
    
    async def transition_status(
        self,
        order_id: int,
        new_status: OrderStatus,
        changed_by_id: Optional[int] = None,
        reason: Optional[str] = None
    ) -> Order:
        """Transition order to new status with optimistic locking."""
        # Get current order with version
        order = await self.get_order_by_id(order_id)
        current_status = OrderStatus(order.status)
        
        # Validate transition
        if not self.state_machine.can_transition(current_status, new_status):
            raise InvalidStateTransitionException(
                current_status.value,
                new_status.value
            )
        
        # Update with optimistic locking
        from sqlalchemy import update
        current_version = order.version
        
        from app.utils.time import utc_now
        now = utc_now()
        timestamp_field = self._get_timestamp_field(new_status)
        update_values = {
            "status": new_status.value,
            "version": current_version + 1
        }
        if timestamp_field:
            update_values[timestamp_field] = now
        
        result = await self.session.execute(
            update(Order)
            .where(Order.id == order_id, Order.version == current_version)
            .values(**update_values)
        )
        
        if result.rowcount == 0:
            raise InvalidStateTransitionException(
                current_status.value,
                new_status.value
            )
        
        # Refresh order object with new values
        await self.session.refresh(order)
        
        # Log the change
        await self._log_status_change(
            order.id,
            current_status.value,
            new_status.value,
            changed_by_id,
            reason
        )
        
        return order
    
    async def assign_courier(
        self,
        order_id: int,
        courier_id: int,
        assigned_by_id: int
    ) -> Order:
        """Assign courier to order."""
        order = await self.get_order_by_id(order_id)
        
        # Verify courier exists and has courier role
        courier_result = await self.session.execute(
            select(User).where(
                and_(
                    User.id == courier_id,
                    User.role == UserRole.COURIER.value,
                    User.is_active == True
                )
            )
        )
        courier = courier_result.scalar_one_or_none()
        
        if not courier:
            raise ValidationException("Invalid courier")
        
        from app.utils.time import utc_now
        order.courier_id = courier_id
        order.assigned_at = utc_now()
        
        await self.session.flush()
        await self.session.commit()
        return order
    
    async def cancel_order(
        self,
        order_id: int,
        cancelled_by_id: int,
        reason: str
    ) -> Order:
        """Cancel an order."""
        order = await self.get_order_by_id(order_id)
        
        if not order.can_be_cancelled():
            raise ValidationException("Order cannot be cancelled at this stage")
        
        old_status = order.status
        
        from app.utils.time import utc_now
        order.status = OrderStatus.CANCELLED.value
        order.cancelled_at = utc_now()
        order.cancelled_by_id = cancelled_by_id
        order.cancellation_reason = reason
        
        await self._log_status_change(
            order.id,
            old_status,
            OrderStatus.CANCELLED.value,
            cancelled_by_id,
            reason
        )
        
        await self.session.flush()
        await self.session.commit()
        return order
    
    async def _generate_order_number(self) -> str:
        """Generate unique order number using daily counter."""
        today = date.today()
        
        # Try to increment counter
        counter_result = await self.session.execute(
            select(DailyCounter).where(DailyCounter.counter_date == today)
        )
        counter = counter_result.scalar_one_or_none()
        
        if counter:
            counter.counter += 1
        else:
            counter = DailyCounter(counter_date=today, counter=1)
            self.session.add(counter)
        
        await self.session.flush()
        await self.session.commit()
        
        # Format: YYYYMMDD-XXXX
        return f"{today.strftime('%Y%m%d')}-{counter.counter:04d}"
    
    async def _log_status_change(
        self,
        order_id: int,
        old_status: Optional[str],
        new_status: str,
        changed_by_id: Optional[int] = None,
        reason: Optional[str] = None
    ) -> None:
        """Log order status change."""
        log = OrderStatusLog(
            order_id=order_id,
            old_status=old_status,
            new_status=new_status,
            changed_by_id=changed_by_id,
            reason=reason
        )
        self.session.add(log)
    
    def _get_timestamp_field(self, status: OrderStatus) -> Optional[str]:
        """Get timestamp field name for a status."""
        timestamp_map = {
            OrderStatus.CONFIRMED: "confirmed_at",
            OrderStatus.PAID: "paid_at",
            OrderStatus.IN_PROGRESS: "in_progress_at",
            OrderStatus.READY: "ready_at",
            OrderStatus.PACKED: "packed_at",
            OrderStatus.ASSIGNED: "assigned_at",
            OrderStatus.IN_DELIVERY: "in_delivery_at",
            OrderStatus.DELIVERED: "delivered_at",
            OrderStatus.CANCELLED: "cancelled_at",
        }
        return timestamp_map.get(status)

    async def get_order_counts_by_status(self, statuses: List[OrderStatus]) -> Dict[str, int]:
        """Get order counts for multiple statuses in a single query."""
        status_values = [s.value for s in statuses]
        result = await self.session.execute(
            select(Order.status, func.count(Order.id).label("count"))
            .where(Order.status.in_(status_values))
            .group_by(Order.status)
        )
        return {row.status: row.count for row in result.all()}
